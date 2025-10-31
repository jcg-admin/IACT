"""Servicios de negocio para la app de usuarios."""

from __future__ import annotations

from typing import Iterable, Set

from . import models

User = models.User


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
        return models.UserPermission.objects.has_permission(user, permission_codename)

    @staticmethod
    def _has_role_permission(user: User, permission_codename: str) -> bool:
        for role in models.RoleAssignment.objects.roles_for_user(user):
            if role.permissions.has_codename(permission_codename):
                return True
        return False

    @staticmethod
    def _has_segment_permission(user: User, permission_codename: str) -> bool:
        for segment in models.Segment.objects.with_permission(permission_codename):
            if segment.matches(user):
                return True
        return False

    @staticmethod
    def permissions_for_user(user: User) -> Iterable[str]:
        """Retorna todos los permisos efectivos del usuario."""

        direct: Set[str] = {
            permission.codename
            for permission in models.UserPermission.objects.permissions_for_user(user)
        }

        role_based: Set[str] = set()
        for role in models.RoleAssignment.objects.roles_for_user(user):
            role_based.update(role.permissions.values_list("codename", flat=True))

        segment_permissions: Set[str] = set()
        for segment in models.Segment.objects.active_segments():
            if segment.matches(user):
                segment_permissions.update(
                    segment.permissions.values_list("codename", flat=True)
                )

        return direct.union(role_based).union(segment_permissions)
