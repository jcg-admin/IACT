"""Modelos para la gestión de usuarios y permisos."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from callcentersite.apps.common.models import BaseModel, TimeStampedModel


class User(AbstractUser, BaseModel):
    """Usuario principal del sistema con campos adicionales."""

    email = models.EmailField("correo", unique=True)
    last_login_ip = models.GenericIPAddressField("última IP de acceso", null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(
        "intentos de inicio de sesión fallidos",
        default=0,
        validators=[MinValueValidator(0)],
    )

    REQUIRED_FIELDS = ["email"]

    class Meta(AbstractUser.Meta):
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def mark_deleted(self) -> None:
        """Realiza soft delete del usuario."""

        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "is_deleted", "deleted_at"])


class Permission(TimeStampedModel):
    """Permiso granular definido por recurso y acción."""

    codename = models.CharField("codigo", max_length=100, unique=True)
    name = models.CharField("nombre", max_length=255)
    resource = models.CharField("recurso", max_length=100)
    action = models.CharField("acción", max_length=50)
    description = models.TextField("descripción")

    class Meta:
        verbose_name = "permiso"
        verbose_name_plural = "permisos"
        ordering = ("codename",)

    def __str__(self) -> str:  # pragma: no cover - representación
        return self.codename


class Role(TimeStampedModel):
    """Rol que agrupa permisos para asignación indirecta."""

    name = models.CharField("nombre", max_length=100, unique=True)
    description = models.TextField("descripción")
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    is_system_role = models.BooleanField("rol del sistema", default=False)

    class Meta:
        verbose_name = "rol"
        verbose_name_plural = "roles"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - representación
        return self.name


class RoleAssignment(TimeStampedModel):
    """Relación entre usuarios y roles."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    granted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="granted_roles", help_text="Usuario que asignó el rol"
    )

    class Meta:
        verbose_name = "asignación de rol"
        verbose_name_plural = "asignaciones de roles"
        unique_together = ("user", "role")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} -> {self.role}"


class UserPermission(TimeStampedModel):
    """Permisos directos asignados a un usuario."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="direct_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="direct_assignments")
    granted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="granted_permissions",
        help_text="Usuario que concedió el permiso",
    )
    granted_at = models.DateTimeField("fecha de concesión", auto_now_add=True)

    class Meta:
        verbose_name = "permiso directo"
        verbose_name_plural = "permisos directos"
        unique_together = ("user", "permission")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} -> {self.permission}"


class Segment(TimeStampedModel):
    """Segmentación de usuarios con criterios dinámicos."""

    name = models.CharField("nombre", max_length=150)
    description = models.TextField("descripción")
    criteria = models.JSONField("criterios", default=dict)
    permissions = models.ManyToManyField(Permission, related_name="segments", blank=True)
    is_active = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "segmento"
        verbose_name_plural = "segmentos"
        ordering = ("name",)

    def matches(self, user: User) -> bool:
        """Evalúa si el usuario cumple con los criterios del segmento."""

        for field, expected in self.criteria.items():
            value: Any = getattr(user, field, None)
            if value != expected:
                return False
        return True

    def __str__(self) -> str:  # pragma: no cover
        return self.name
