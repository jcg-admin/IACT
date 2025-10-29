"""Tests para el sistema de permisos de tres niveles."""

import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestPermissionPrecedence:
    """Validación de precedencia de permisos según especificación."""

    def test_permiso_directo_tiene_maxima_prioridad(self, django_assert_num_queries):
        User = get_user_model()
        user = User.objects.create_user(username="alice", password="segura123", email="alice@example.com")

        from callcentersite.apps.users import models as user_models
        permission = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Puede ver analítica",
            resource="analytics",
            action="view",
            description="Permite ver reportes de analítica",
        )

        role = user_models.Role.objects.create(name="Analista", description="Rol analista")
        role.permissions.add(permission)

        segment = user_models.Segment.objects.create(
            name="Segmento activo",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )
        segment.permissions.add(permission)

        user_models.UserPermission.objects.create(user=user, permission=permission, granted_by=user)

        from callcentersite.apps.users.services import PermissionService

        with django_assert_num_queries(1):
            assert PermissionService.has_permission(user, "analytics.view") is True

    def test_permiso_por_segmento_sin_coincidencia_no_habilita(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
            is_active=False,
        )

        from callcentersite.apps.users import models as user_models
        permission = user_models.Permission.objects.create(
            codename="reports.generate",
            name="Generar reportes",
            resource="reports",
            action="create",
            description="Puede generar reportes",
        )

        segment = user_models.Segment.objects.create(
            name="Activos",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )
        segment.permissions.add(permission)

        from callcentersite.apps.users.services import PermissionService

        assert PermissionService.has_permission(user, "reports.generate") is False

    def test_permiso_por_rol_sin_permiso_directo(self):
        User = get_user_model()
        user = User.objects.create_user(username="carol", password="segura123", email="carol@example.com")

        from callcentersite.apps.users import models as user_models
        permission = user_models.Permission.objects.create(
            codename="audit.view",
            name="Ver auditoría",
            resource="audit",
            action="view",
            description="Puede consultar registros de auditoría",
        )

        role = user_models.Role.objects.create(name="Auditor", description="Rol auditor")
        role.permissions.add(permission)
        user_models.RoleAssignment.objects.create(user=user, role=role, granted_by=user)

        from callcentersite.apps.users.services import PermissionService

        assert PermissionService.has_permission(user, "audit.view") is True
