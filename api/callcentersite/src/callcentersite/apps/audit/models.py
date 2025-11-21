"""Modelo de auditoría inmutable."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Registro de acciones relevantes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    # Campos principales
    action = models.CharField(max_length=100, default='', blank=True)  # Legacy
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        default='',
        blank=True,
        help_text='Tipo de evento (LOGIN_SUCCESS, USER_LOCKED, etc.)'
    )
    resource = models.CharField(max_length=100, default='', blank=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True)

    # Información de contexto
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Valores de cambio
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)

    # Resultado
    result = models.CharField(max_length=20, default='', blank=True)
    error_message = models.TextField(null=True, blank=True)

    # Metadatos adicionales
    metadata = models.JSONField(default=dict, blank=True)
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Detalles adicionales del evento'
    )

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ("-timestamp",)
        default_permissions = ()
        permissions = [("view_auditlog", "Puede ver los registros de auditoría")]

    @property
    def user_id(self) -> int | None:
        """Retorna el ID del usuario para compatibilidad con tests."""
        return self.user.id if self.user else None

    def save(self, *args, **kwargs):  # type: ignore[override]
        if self.pk:
            raise RuntimeError("Los registros de auditoría son inmutables")
        # Sincronizar event_type y action si solo uno está definido
        if self.event_type and not self.action:
            self.action = self.event_type
        elif self.action and not self.event_type:
            self.event_type = self.action
        super().save(*args, **kwargs)
