"""Modelo de auditoría inmutable."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Registro de acciones relevantes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    result = models.CharField(max_length=20)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ("-timestamp",)
        default_permissions = ()
        permissions = [("view_auditlog", "Puede ver los registros de auditoría")]

    def save(self, *args, **kwargs):  # type: ignore[override]
        if self.pk:
            raise RuntimeError("Los registros de auditoría son inmutables")
        super().save(*args, **kwargs)
