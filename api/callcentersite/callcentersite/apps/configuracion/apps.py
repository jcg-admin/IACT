"""Configuración de la app configuracion."""

from django.apps import AppConfig


class ConfiguracionConfig(AppConfig):
    """Configuración de la app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.configuracion'
    verbose_name = 'Configuración del Sistema'
