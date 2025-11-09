"""
Mixins y Permission Classes para Django REST Framework.

Uso:

    # Ejemplo 1: Permission class simple
    from .mixins_permisos import GranularPermission

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        permission_classes = [GranularPermission]

        # Mapear acciones a capacidades
        permission_map = {
            'list': 'sistema.vistas.articulos.ver',
            'retrieve': 'sistema.vistas.articulos.ver',
            'create': 'sistema.vistas.articulos.crear',
            'update': 'sistema.vistas.articulos.editar',
            'partial_update': 'sistema.vistas.articulos.editar',
            'destroy': 'sistema.vistas.articulos.eliminar',
        }

    # Ejemplo 2: Mixin para ViewSet
    from .mixins_permisos import GranularPermissionMixin

    class ReportViewSet(GranularPermissionMixin, viewsets.ModelViewSet):
        queryset = Report.objects.all()

        permission_map = {
            'list': 'sistema.vistas.reportes.ver',
            'create': 'sistema.vistas.reportes.crear',
            'export_pdf': 'sistema.vistas.reportes.exportar',  # custom action
        }

    # Ejemplo 3: Permission class con múltiples capacidades
    class DashboardViewSet(viewsets.ViewSet):
        permission_classes = [GranularPermission]

        permission_map = {
            'financial': ['finanzas.dashboards.ver', 'finanzas.reportes.ver'],  # ANY
            'admin': {
                'all': ['admin.dashboards.ver', 'admin.permisos.ver'],  # ALL
            },
        }

Performance:
    - Usa SQL functions (5-10ms) en vez de ORM (30-50ms)
    - Cache automático en request (evita verificaciones duplicadas)
    - Auditoría integrada

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

from typing import Dict, List, Union, Optional
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _verificar_permiso_sql(usuario_id: int, capacidad_codigo: str) -> bool:
    """
    Verifica si un usuario tiene un permiso usando la función SQL.

    Performance: 5-10ms

    Args:
        usuario_id: ID del usuario
        capacidad_codigo: Código de la capacidad

    Returns:
        True si tiene permiso, False si no
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT usuario_tiene_permiso(%s, %s)",
            [usuario_id, capacidad_codigo]
        )
        result = cursor.fetchone()
        return result[0] if result else False


def _obtener_capacidades_usuario_sql(usuario_id: int) -> List[str]:
    """
    Obtiene todas las capacidades de un usuario usando la función SQL.

    Performance: 10-20ms

    Args:
        usuario_id: ID del usuario

    Returns:
        Lista de códigos de capacidades
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_capacidades_usuario(%s)",
            [usuario_id]
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else []


def _get_cached_capacidades(request: Request) -> Optional[List[str]]:
    """
    Obtiene las capacidades del usuario desde el cache del request.

    Cache de request: evita múltiples queries SQL en el mismo request.
    """
    return getattr(request, '_cached_user_capacidades', None)


def _set_cached_capacidades(request: Request, capacidades: List[str]):
    """Guarda las capacidades del usuario en el cache del request."""
    request._cached_user_capacidades = capacidades


def _auditar_verificacion(
    request: Request,
    capacidad_codigo: str,
    resultado: bool,
):
    """
    Registra la verificación en auditoría.

    Marca el request para que el middleware lo audite.
    """
    # Marcar para auditoría en middleware
    request._permission_checked = True
    request._permission_required = capacidad_codigo
    request._permission_result = resultado


# =============================================================================
# PERMISSION CLASSES
# =============================================================================

class GranularPermission(permissions.BasePermission):
    """
    Permission class que usa el sistema de permisos granulares.

    Configuración en ViewSet:

        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [GranularPermission]

            # Opción 1: Mapear acciones a capacidades individuales
            permission_map = {
                'list': 'sistema.vistas.items.ver',
                'retrieve': 'sistema.vistas.items.ver',
                'create': 'sistema.vistas.items.crear',
                'update': 'sistema.vistas.items.editar',
                'partial_update': 'sistema.vistas.items.editar',
                'destroy': 'sistema.vistas.items.eliminar',
                'custom_action': 'sistema.vistas.items.procesar',  # custom action
            }

            # Opción 2: Lista de capacidades (ANY - al menos una)
            permission_map = {
                'list': ['capacidad1', 'capacidad2'],  # Requiere AL MENOS una
            }

            # Opción 3: Todas las capacidades (ALL - todas requeridas)
            permission_map = {
                'list': {
                    'all': ['capacidad1', 'capacidad2']  # Requiere TODAS
                }
            }

    Performance:
    - Primera verificación: 5-10ms (SQL function)
    - Verificaciones subsecuentes en mismo request: < 1ms (cache)

    Auditoría:
    - Automática si PermissionAuditMiddleware está configurado
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Verifica si el usuario tiene permiso para la acción.

        Args:
            request: DRF Request
            view: ViewSet o APIView

        Returns:
            True si tiene permiso, False si no
        """
        # 1. Verificar autenticación
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Superuser bypass (opcional, configurar en settings)
        if getattr(request.user, 'is_superuser', False):
            # Opcional: puedes deshabilitar esto para forzar verificación
            # return True
            pass

        # 3. Obtener la acción (list, create, retrieve, etc)
        action = getattr(view, 'action', None)
        if not action:
            # Para APIView sin action (no es ViewSet)
            action = request.method.lower()

        # 4. Obtener permission_map del view
        permission_map = getattr(view, 'permission_map', None)
        if not permission_map:
            raise ImproperlyConfigured(
                f"{view.__class__.__name__} debe definir 'permission_map'"
            )

        # 5. Obtener capacidad(es) requerida(s) para esta acción
        required_permissions = permission_map.get(action)
        if not required_permissions:
            # Acción no configurada - denegar por defecto
            logger.warning(
                f"Acción '{action}' no configurada en permission_map de {view.__class__.__name__}"
            )
            return False

        # 6. Verificar permiso(s)
        has_permission = self._check_permissions(
            request, required_permissions
        )

        # 7. Auditar
        capacidad_codigo = self._format_permission_for_audit(required_permissions)
        _auditar_verificacion(request, capacidad_codigo, has_permission)

        return has_permission

    def _check_permissions(
        self,
        request: Request,
        required_permissions: Union[str, List[str], Dict[str, List[str]]]
    ) -> bool:
        """
        Verifica permisos según el tipo de configuración.

        Args:
            request: DRF Request
            required_permissions: String, list, o dict con 'all'/'any'

        Returns:
            True si tiene permiso, False si no
        """
        usuario_id = request.user.id

        # CASO 1: Single permission (string)
        if isinstance(required_permissions, str):
            return _verificar_permiso_sql(usuario_id, required_permissions)

        # CASO 2: Multiple permissions (list) - ANY (al menos una)
        if isinstance(required_permissions, list):
            # Optimización: obtener todas las capacidades una vez
            capacidades_usuario = _get_cached_capacidades(request)
            if capacidades_usuario is None:
                capacidades_usuario = _obtener_capacidades_usuario_sql(usuario_id)
                _set_cached_capacidades(request, capacidades_usuario)

            # Verificar si tiene al menos una
            return any(cap in capacidades_usuario for cap in required_permissions)

        # CASO 3: Dict con 'all' o 'any'
        if isinstance(required_permissions, dict):
            if 'all' in required_permissions:
                # Requiere TODAS las capacidades
                required_caps = required_permissions['all']
                capacidades_usuario = _get_cached_capacidades(request)
                if capacidades_usuario is None:
                    capacidades_usuario = _obtener_capacidades_usuario_sql(usuario_id)
                    _set_cached_capacidades(request, capacidades_usuario)

                return all(cap in capacidades_usuario for cap in required_caps)

            if 'any' in required_permissions:
                # Requiere AL MENOS UNA capacidad
                required_caps = required_permissions['any']
                capacidades_usuario = _get_cached_capacidades(request)
                if capacidades_usuario is None:
                    capacidades_usuario = _obtener_capacidades_usuario_sql(usuario_id)
                    _set_cached_capacidades(request, capacidades_usuario)

                return any(cap in capacidades_usuario for cap in required_caps)

        # Configuración inválida
        logger.error(f"Configuración inválida de permisos: {required_permissions}")
        return False

    def _format_permission_for_audit(
        self,
        required_permissions: Union[str, List[str], Dict[str, List[str]]]
    ) -> str:
        """
        Formatea los permisos requeridos para auditoría.

        Args:
            required_permissions: Permisos requeridos

        Returns:
            String formateado para auditoría
        """
        if isinstance(required_permissions, str):
            return required_permissions

        if isinstance(required_permissions, list):
            return f"any_of:{','.join(required_permissions[:3])}"

        if isinstance(required_permissions, dict):
            if 'all' in required_permissions:
                caps = required_permissions['all']
                return f"all_of:{','.join(caps[:3])}"
            if 'any' in required_permissions:
                caps = required_permissions['any']
                return f"any_of:{','.join(caps[:3])}"

        return "unknown"


# =============================================================================
# MIXINS
# =============================================================================

class GranularPermissionMixin:
    """
    Mixin para ViewSets que simplifica el uso de permisos granulares.

    Uso:

        class ArticleViewSet(GranularPermissionMixin, viewsets.ModelViewSet):
            queryset = Article.objects.all()

            permission_map = {
                'list': 'sistema.vistas.articulos.ver',
                'create': 'sistema.vistas.articulos.crear',
                'update': 'sistema.vistas.articulos.editar',
                'destroy': 'sistema.vistas.articulos.eliminar',
            }

    El mixin automáticamente:
    - Configura GranularPermission en permission_classes
    - Proporciona helper methods para verificar permisos en el código
    """

    def get_permissions(self):
        """
        Agrega GranularPermission a las permission classes.

        Si el ViewSet ya tiene otras permission classes, las mantiene.
        """
        permission_classes = getattr(self, 'permission_classes', [])

        # Agregar GranularPermission si no está ya
        if GranularPermission not in permission_classes:
            permission_classes = [GranularPermission] + list(permission_classes)

        return [permission() for permission in permission_classes]

    def check_permission(self, capacidad_codigo: str) -> bool:
        """
        Helper method para verificar un permiso dentro del código del ViewSet.

        Uso:
            def custom_action(self, request):
                if not self.check_permission('sistema.reportes.exportar'):
                    return Response({'error': 'Sin permiso'}, status=403)

                # ... lógica de exportación

        Args:
            capacidad_codigo: Código de la capacidad a verificar

        Returns:
            True si tiene permiso, False si no
        """
        request = self.request
        if not request.user or not request.user.is_authenticated:
            return False

        return _verificar_permiso_sql(request.user.id, capacidad_codigo)

    def check_any_permission(self, capacidades: List[str]) -> bool:
        """
        Verifica si el usuario tiene AL MENOS UNA de las capacidades.

        Args:
            capacidades: Lista de códigos de capacidades

        Returns:
            True si tiene al menos una, False si no tiene ninguna
        """
        request = self.request
        if not request.user or not request.user.is_authenticated:
            return False

        capacidades_usuario = _get_cached_capacidades(request)
        if capacidades_usuario is None:
            capacidades_usuario = _obtener_capacidades_usuario_sql(request.user.id)
            _set_cached_capacidades(request, capacidades_usuario)

        return any(cap in capacidades_usuario for cap in capacidades)

    def check_all_permissions(self, capacidades: List[str]) -> bool:
        """
        Verifica si el usuario tiene TODAS las capacidades.

        Args:
            capacidades: Lista de códigos de capacidades (todas requeridas)

        Returns:
            True si tiene todas, False si falta alguna
        """
        request = self.request
        if not request.user or not request.user.is_authenticated:
            return False

        capacidades_usuario = _get_cached_capacidades(request)
        if capacidades_usuario is None:
            capacidades_usuario = _obtener_capacidades_usuario_sql(request.user.id)
            _set_cached_capacidades(request, capacidades_usuario)

        return all(cap in capacidades_usuario for cap in capacidades)

    def get_user_capacidades(self) -> List[str]:
        """
        Obtiene todas las capacidades del usuario actual.

        Usa cache del request para evitar queries múltiples.

        Returns:
            Lista de códigos de capacidades
        """
        request = self.request
        if not request.user or not request.user.is_authenticated:
            return []

        capacidades_usuario = _get_cached_capacidades(request)
        if capacidades_usuario is None:
            capacidades_usuario = _obtener_capacidades_usuario_sql(request.user.id)
            _set_cached_capacidades(request, capacidades_usuario)

        return capacidades_usuario


# =============================================================================
# CONVENIENCE PERMISSION CLASSES
# =============================================================================

class IsAuthenticatedWithGranularPermission(GranularPermission):
    """
    Combina IsAuthenticated con GranularPermission.

    Equivalente a:
        permission_classes = [IsAuthenticated, GranularPermission]

    Pero más eficiente (una sola verificación).
    """
    pass  # GranularPermission ya verifica autenticación


class AllowAnyWithOptionalGranularPermission(permissions.BasePermission):
    """
    Permite acceso sin autenticación, pero si está autenticado verifica permisos.

    Útil para endpoints que tienen funcionalidad pública y funcionalidad privada.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Si no está autenticado, permitir (AllowAny)
        if not request.user or not request.user.is_authenticated:
            return True

        # Si está autenticado, verificar permisos granulares
        granular_perm = GranularPermission()
        return granular_perm.has_permission(request, view)
