"""
Configuración de Sentry para monitoreo en producción.
Incluye integración con Django, logging y performance monitoring.
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


def init_sentry():
    """
    Inicializa Sentry para monitoreo de errores y performance.

    Variables de entorno requeridas:
    - SENTRY_DSN: DSN de Sentry para el proyecto
    - SENTRY_ENVIRONMENT: Entorno (development, staging, production)
    - SENTRY_TRACES_SAMPLE_RATE: Tasa de muestreo para traces (0.0 a 1.0)
    """
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        # No inicializar Sentry si no hay DSN configurado
        return

    environment = os.getenv("SENTRY_ENVIRONMENT", "development")
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))

    # Configuración de logging integration
    logging_integration = LoggingIntegration(
        level=None,  # Captura todos los niveles
        event_level="ERROR",  # Solo envía eventos para ERROR y superior
    )

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[
            DjangoIntegration(
                transaction_style="url",  # Usar URL como nombre de transacción
                middleware_spans=True,  # Crear spans para middleware
                signals_spans=True,  # Crear spans para signals
                cache_spans=True,  # Crear spans para cache
            ),
            logging_integration,
            RedisIntegration(),
            CeleryIntegration(
                monitor_beat_tasks=True,
                exclude_beat_tasks=[],
            ),
        ],
        # Tasa de muestreo para performance monitoring
        traces_sample_rate=traces_sample_rate,
        # Tasa de muestreo para profiling
        profiles_sample_rate=profiles_sample_rate,
        # Enviar versión de la aplicación
        release=os.getenv("SENTRY_RELEASE", "0.1.0"),
        # Configuración de tags
        before_send=before_send,
        # Ignorar ciertos errores
        ignore_errors=[
            KeyboardInterrupt,
            BrokenPipeError,
        ],
        # Maximum number of breadcrumbs
        max_breadcrumbs=50,
        # Attach stack trace to messages
        attach_stacktrace=True,
        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,
        # Request bodies configuration
        request_bodies="medium",  # never, small, medium, always
        # In-app include paths
        in_app_include=["callcentersite"],
        # Debug mode
        debug=os.getenv("SENTRY_DEBUG", "false").lower() == "true",
    )


def before_send(event, hint):
    """
    Hook llamado antes de enviar un evento a Sentry.
    Permite filtrar o modificar eventos antes de enviarlos.

    Args:
        event: El evento a enviar
        hint: Información adicional sobre el evento

    Returns:
        El evento modificado o None para no enviarlo
    """
    # Agregar información adicional del usuario si está disponible
    if "request" in hint:
        request = hint["request"]
        if hasattr(request, "user") and request.user.is_authenticated:
            event.setdefault("user", {}).update({
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            })

    # Filtrar ciertos errores en desarrollo
    if os.getenv("SENTRY_ENVIRONMENT") == "development":
        # No enviar errores de desarrollo a Sentry
        if event.get("level") in ["debug", "info"]:
            return None

    # Agregar tags personalizados
    event.setdefault("tags", {}).update({
        "server_name": os.getenv("HOSTNAME", "unknown"),
        "django_version": os.getenv("DJANGO_VERSION", "5.2"),
    })

    return event


def configure_sentry_scope():
    """
    Configura el scope global de Sentry con información del contexto.
    """
    from sentry_sdk import configure_scope

    with configure_scope() as scope:
        scope.set_tag("application", "callcentersite")
        scope.set_tag("component", "api")

        # Agregar información del entorno
        scope.set_context("environment", {
            "python_version": os.getenv("PYTHON_VERSION", "3.12"),
            "django_version": os.getenv("DJANGO_VERSION", "5.2"),
        })
