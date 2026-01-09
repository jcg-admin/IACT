"""
Middleware para auditoría automática de permisos.

Configuración en settings.py:

    MIDDLEWARE = [
        # ... otros middleware
        'callcentersite.apps.users.middleware_permisos.PermissionAuditMiddleware',
        # ... otros middleware
    ]

    # Opcional: Configuración personalizada
    PERMISSION_AUDIT_CONFIG = {
        'enabled': True,  # Habilitar/deshabilitar auditoría
        'audit_all_requests': False,  # Auditar TODOS los requests (cuidado con volumen)
        'audit_only_authenticated': True,  # Solo auditar usuarios autenticados
        'exclude_paths': [  # Excluir estos paths de auditoría
            '/api/health/',
            '/api/metrics/',
            '/static/',
            '/media/',
        ],
        'include_query_params': True,  # Incluir query params en auditoría
        'async_audit': True,  # Usar Celery para auditoría asíncrona (recomendado)
    }

Performance:
    - Con async_audit=True: 0-1ms overhead (Celery task)
    - Con async_audit=False: 5-10ms overhead (INSERT directo a DB)

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

import time
import logging
from typing import Optional, List
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    'enabled': True,
    'audit_all_requests': False,
    'audit_only_authenticated': True,
    'exclude_paths': [
        '/api/health/',
        '/api/metrics/',
        '/static/',
        '/media/',
        '/admin/jsi18n/',
    ],
    'include_query_params': True,
    'async_audit': False,  # Por defecto False (requiere Celery configurado)
}


def get_audit_config():
    """Obtiene la configuración de auditoría desde settings."""
    return getattr(settings, 'PERMISSION_AUDIT_CONFIG', DEFAULT_CONFIG)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _should_audit_request(request: HttpRequest, config: dict) -> bool:
    """
    Determina si un request debe ser auditado.

    Args:
        request: HttpRequest
        config: Configuración de auditoría

    Returns:
        True si debe auditarse, False si no
    """
    # 1. Si está deshabilitado, no auditar
    if not config.get('enabled', True):
        return False

    # 2. Si solo auditar autenticados, verificar
    if config.get('audit_only_authenticated', True):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False

    # 3. Excluir paths específicos
    exclude_paths = config.get('exclude_paths', [])
    request_path = request.path
    for exclude_path in exclude_paths:
        if request_path.startswith(exclude_path):
            return False

    # 4. Si audit_all_requests=False, solo auditar si hay header específico
    if not config.get('audit_all_requests', False):
        # Solo auditar si viene de un endpoint que usa decoradores de permisos
        # El decorador puede setear un atributo en el request
        if not getattr(request, '_permission_checked', False):
            return False

    return True


def _get_client_ip(request: HttpRequest) -> Optional[str]:
    """Extrae la IP del cliente (soporta proxies)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _get_user_agent(request: HttpRequest) -> Optional[str]:
    """Extrae el User-Agent del cliente."""
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def _build_audit_metadata(request: HttpRequest, config: dict) -> dict:
    """
    Construye metadata adicional para auditoría.

    Args:
        request: HttpRequest
        config: Configuración de auditoría

    Returns:
        Dict con metadata (method, path, query_params, etc)
    """
    metadata = {
        'method': request.method,
        'path': request.path,
        'ip_address': _get_client_ip(request),
        'user_agent': _get_user_agent(request),
    }

    # Incluir query params si está configurado
    if config.get('include_query_params', True):
        metadata['query_params'] = dict(request.GET)

    return metadata


def _audit_request_sync(
    usuario_id: int,
    capacidad_codigo: str,
    resultado: bool,
    ip_address: Optional[str],
    user_agent: Optional[str],
):
    """
    Audita un request de manera SÍNCRONA (bloquea el request).

    Performance: 5-10ms

    Args:
        usuario_id: ID del usuario
        capacidad_codigo: Código de la capacidad o path verificado
        resultado: True si se concedió acceso, False si se denegó
        ip_address: IP del cliente
        user_agent: User-Agent del cliente
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT verificar_permiso_y_auditar(%s, %s, %s, %s)",
                [usuario_id, capacidad_codigo, ip_address, user_agent]
            )
    except Exception as e:
        logger.error(f"Error en auditoría síncrona: {e}", exc_info=True)


def _audit_request_async(
    usuario_id: int,
    capacidad_codigo: str,
    resultado: bool,
    ip_address: Optional[str],
    user_agent: Optional[str],
    metadata: dict,
):
    """
    Audita un request de manera ASÍNCRONA usando Celery.

    Performance: < 1ms (solo encola task)

    Args:
        usuario_id: ID del usuario
        capacidad_codigo: Código de la capacidad o path verificado
        resultado: True si se concedió acceso, False si se denegó
        ip_address: IP del cliente
        user_agent: User-Agent del cliente
        metadata: Metadata adicional del request
    """
    try:
        # Importar task de Celery (solo si está configurado)
        from .tasks import audit_permission_check

        audit_permission_check.delay(
            usuario_id=usuario_id,
            capacidad_codigo=capacidad_codigo,
            resultado=resultado,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )
    except ImportError:
        # Celery no configurado, fallback a auditoría síncrona
        logger.warning(
            "Celery no configurado, usando auditoría síncrona. "
            "Configura Celery para mejor performance."
        )
        _audit_request_sync(
            usuario_id, capacidad_codigo, resultado, ip_address, user_agent
        )
    except Exception as e:
        logger.error(f"Error en auditoría asíncrona: {e}", exc_info=True)


# =============================================================================
# MIDDLEWARE
# =============================================================================

class PermissionAuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditoría automática de permisos.

    Funcionalidad:
    1. Audita todos los requests de usuarios autenticados
    2. Registra IP, User-Agent, timestamp, path
    3. Soporta auditoría síncrona o asíncrona (Celery)
    4. Configurable mediante settings.PERMISSION_AUDIT_CONFIG

    Performance:
    - Async (Celery): < 1ms overhead
    - Sync (sin Celery): 5-10ms overhead

    Configuración:
        MIDDLEWARE = [
            # ...
            'callcentersite.apps.users.middleware_permisos.PermissionAuditMiddleware',
        ]

        PERMISSION_AUDIT_CONFIG = {
            'enabled': True,
            'audit_all_requests': False,  # Solo auditar requests con permisos verificados
            'async_audit': True,  # Usar Celery
        }
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.config = get_audit_config()
        self.enabled = self.config.get('enabled', True)

    def process_request(self, request: HttpRequest):
        """
        Se ejecuta ANTES de la vista.

        Registra el timestamp de inicio para medir latencia.
        """
        if self.enabled:
            request._permission_audit_start_time = time.time()

        return None

    def process_response(self, request: HttpRequest, response: HttpResponse):
        """
        Se ejecuta DESPUÉS de la vista.

        Si el request debe ser auditado, registra la verificación.
        """
        if not self.enabled:
            return response

        # 1. Verificar si debe auditarse
        if not _should_audit_request(request, self.config):
            return response

        # 2. Obtener información del usuario
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return response

        # 3. Determinar capacidad verificada
        capacidad_codigo = getattr(request, '_permission_required', None)
        if not capacidad_codigo:
            # Si no hay capacidad específica, usar el path como referencia
            capacidad_codigo = f"access:{request.method}:{request.path}"

        # 4. Determinar resultado (basado en status code)
        resultado = 200 <= response.status_code < 400

        # 5. Obtener metadata
        metadata = _build_audit_metadata(request, self.config)

        # 6. Calcular latencia
        start_time = getattr(request, '_permission_audit_start_time', None)
        if start_time:
            latency_ms = (time.time() - start_time) * 1000
            metadata['latency_ms'] = round(latency_ms, 2)

        # 7. Auditar (async o sync)
        ip_address = _get_client_ip(request)
        user_agent = _get_user_agent(request)

        if self.config.get('async_audit', False):
            _audit_request_async(
                usuario_id=user.id,
                capacidad_codigo=capacidad_codigo,
                resultado=resultado,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata,
            )
        else:
            _audit_request_sync(
                usuario_id=user.id,
                capacidad_codigo=capacidad_codigo,
                resultado=resultado,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        """
        Se ejecuta cuando hay una excepción en la vista.

        Audita el error si es PermissionDenied.
        """
        if not self.enabled:
            return None

        # Solo auditar si es un error de permisos
        from django.core.exceptions import PermissionDenied
        if not isinstance(exception, PermissionDenied):
            return None

        # Obtener usuario
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        # Auditar el acceso denegado
        capacidad_codigo = getattr(request, '_permission_required', None) or \
                          f"denied:{request.method}:{request.path}"

        metadata = _build_audit_metadata(request, self.config)
        ip_address = _get_client_ip(request)
        user_agent = _get_user_agent(request)

        if self.config.get('async_audit', False):
            _audit_request_async(
                usuario_id=user.id,
                capacidad_codigo=capacidad_codigo,
                resultado=False,  # Acceso denegado
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata,
            )
        else:
            _audit_request_sync(
                usuario_id=user.id,
                capacidad_codigo=capacidad_codigo,
                resultado=False,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return None  # Dejar que Django maneje el exception normalmente


# =============================================================================
# INTEGRATION WITH DECORATORS
# =============================================================================

def mark_permission_checked(request: HttpRequest, capacidad_codigo: str):
    """
    Helper function para marcar que un request tiene verificación de permisos.

    Debe ser llamada por los decoradores de permisos para que el middleware
    sepa que debe auditar este request.

    Args:
        request: HttpRequest
        capacidad_codigo: Código de la capacidad verificada
    """
    request._permission_checked = True
    request._permission_required = capacidad_codigo
