"""Modelos para configuración de dashboards."""

from django.conf import settings
from django.db import models


class DashboardConfiguration(models.Model):
    """
    Configuración personalizada de dashboard por usuario.

    Permite a cada usuario personalizar qué widgets ve y en qué orden.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_config',
        help_text='Usuario dueño de esta configuración'
    )

    widgets = models.JSONField(
        default=list,
        help_text='Lista ordenada de tipos de widgets a mostrar'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación de la configuración'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última actualización'
    )

    class Meta:
        db_table = 'dashboard_configurations'
        verbose_name = 'Configuración de Dashboard'
        verbose_name_plural = 'Configuraciones de Dashboard'

    def __str__(self):
        return f'Dashboard config for {self.user.username}'
