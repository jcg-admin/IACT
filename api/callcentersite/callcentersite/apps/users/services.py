"""Servicios de negocio para la app de usuarios."""

from __future__ import annotations

from typing import Iterable

from django.contrib.auth import get_user_model
from . import models

User = get_user_model()


class PermissionService:
    """Evalúa permisos según precedencia definida."""

    @staticmethod
    def has_permission(user: User, permission_codename: str) -> bool:
        """Evalúa si el usuario tiene el permiso solicitado."""

        if not user.is_authenticated:
            return False

        if PermissionService._has_direct_permission(user, permission_codename):
            return True

        if PermissionService._has_role_permission(user, permission_codename):
            return True

        return PermissionService._has_segment_permission(user, permission_codename)

    @staticmethod
    def _has_direct_permission(user: User, permission_codename: str) -> bool:
        return models.UserPermission.objects.filter(
            user=user, permission__codename=permission_codename
        ).exists()

    @staticmethod
    def _has_role_permission(user: User, permission_codename: str) -> bool:
        return models.Permission.objects.filter(
            codename=permission_codename,
            roles__assignments__user=user,
        ).exists()

    @staticmethod
    def _has_segment_permission(user: User, permission_codename: str) -> bool:
        segments = models.Segment.objects.filter(
            is_active=True,
            permissions__codename=permission_codename,
        ).distinct()

        for segment in segments:
            if segment.matches(user):
                return True
        return False

    @staticmethod
    def permissions_for_user(user: User) -> Iterable[str]:
        """Retorna todos los permisos efectivos del usuario."""

        direct = set(
            models.UserPermission.objects.filter(user=user).values_list(
                "permission__codename", flat=True
            )
        )
        role_based = set(
            models.Permission.objects.filter(roles__assignments__user=user).values_list(
                "codename", flat=True
            )
        )

        segment_permissions: set[str] = set()
        segments = models.Segment.objects.filter(is_active=True).prefetch_related("permissions")
        for segment in segments:
            if segment.matches(user):
                segment_permissions.update(
                    segment.permissions.values_list("codename", flat=True)
                )

        return direct.union(role_based).union(segment_permissions)
