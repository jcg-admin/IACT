"""Configuración de la app presupuestos."""

from django.apps import AppConfig


class PresupuestosConfig(AppConfig):
    """Configuración de la app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'callcentersite.apps.presupuestos'
    verbose_name = 'Gestión de Presupuestos'
