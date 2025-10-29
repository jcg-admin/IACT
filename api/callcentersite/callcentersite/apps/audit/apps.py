"""Configuración de auditoría."""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Configura la app de auditoría."""

    name = "callcentersite.apps.audit"
    verbose_name = "Auditoría"
