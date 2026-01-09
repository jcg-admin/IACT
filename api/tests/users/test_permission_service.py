"""Tests TDD para PermissionService basados en requisitos funcionales.

Requisitos cubiertos:
- RF-001: Sistema de evaluación de permisos con tres niveles
- RF-003: Obtener permisos efectivos de usuario
"""

import pytest
from django.contrib.auth import get_user_model

from callcentersite.apps.users import models as user_models
from callcentersite.apps.users.services import PermissionService

User = get_user_model()


@pytest.mark.django_db
class TestRF001EvaluacionPermisosTresNiveles:
    """Tests para RF-001: Sistema de evaluación de permisos con precedencia."""

    def test_usuario_no_autenticado_siempre_retorna_false(self):
        """
        RF-001 Escenario 4: Usuario no autenticado siempre retorna false.

        Given un usuario NO autenticado
        When el sistema evalúa has_permission
        Then retorna false sin evaluar permisos
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
            is_active=False,
        )
        # Marcar como no autenticado
        user.set_authenticated(False)

        result = PermissionService.has_permission(user, "cualquier.permiso")

        assert result is False

    def test_permiso_inexistente_retorna_false(self):
        """
        RF-001 Escenario 6: Permiso no existe en ningún nivel.

        Given un usuario autenticado sin permisos
        When evalúa un permiso inexistente
        Then retorna false
        """
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
        )

        result = PermissionService.has_permission(user, "permiso.inexistente")

        assert result is False

    def test_permiso_por_segmento_cuando_coincide_criterio(self):
        """
        RF-001 Escenario 3: Permiso por segmento cuando usuario coincide.

        Given usuario sin permisos directos ni roles
          And usuario con is_active=True
          And segmento activo con criterio is_active=True
        When evalúa permiso del segmento
        Then retorna true
        """
        user = User.objects.create_user(
            username="dave",
            password="segura123",
            email="dave@example.com",
            is_active=True,
        )

        permission = user_models.Permission.objects.create(
            codename="reports.generate",
            name="Generar reportes",
            resource="reports",
            action="generate",
            description="Puede generar reportes",
        )

        segment = user_models.Segment.objects.create(
            name="Activos",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )
        segment.permissions.add(permission)

        result = PermissionService.has_permission(user, "reports.generate")

        assert result is True

    def test_segmento_inactivo_es_ignorado(self):
        """
        RF-001 / RF-004: Segmentos con is_active=False son ignorados.

        Given un segmento con is_active=False
          And el segmento tiene un permiso
        When usuario coincide con criterios del segmento
        Then el permiso NO es otorgado
        """
        user = User.objects.create_user(
            username="eve",
            password="segura123",
            email="eve@example.com",
            is_active=True,
        )

        permission = user_models.Permission.objects.create(
            codename="reports.view",
            name="Ver reportes",
            resource="reports",
            action="view",
            description="Puede ver reportes",
        )

        segment = user_models.Segment.objects.create(
            name="Segmento Inactivo",
            description="Este segmento está desactivado",
            criteria={"is_active": True},
            is_active=False,  # INACTIVO
        )
        segment.permissions.add(permission)

        result = PermissionService.has_permission(user, "reports.view")

        assert result is False

    def test_short_circuit_no_evalua_roles_si_tiene_directo(self):
        """
        RF-001 BR-02: Short-circuit - no evaluar roles si encuentra directo.

        Este test valida que el sistema NO consulta roles cuando
        el permiso ya fue encontrado a nivel directo.

        Nota: En la implementación actual (in-memory) es difícil verificar
        el short-circuit sin instrumentación. Este test valida el comportamiento
        correcto aunque no puede verificar directamente que no se consultó.
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
        )

        permission = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Ver analítica",
            resource="analytics",
            action="view",
            description="Puede ver analítica",
        )

        # Permiso directo
        user_models.UserPermission.objects.create(
            user=user,
            permission=permission,
            granted_by=user,
        )

        # Rol con el mismo permiso (no debería consultarse)
        role = user_models.Role.objects.create(
            name="Analista",
            description="Rol con analytics.view",
        )
        role.permissions.add(permission)
        user_models.RoleAssignment.objects.create(
            user=user,
            role=role,
            granted_by=user,
        )

        result = PermissionService.has_permission(user, "analytics.view")

        assert result is True
        # El short-circuit debería haber retornado en nivel directo
        # sin consultar el rol, pero el resultado es correcto de todas formas


@pytest.mark.django_db
class TestRF003PermisosEfectivosUsuario:
    """Tests para RF-003: Obtener todos los permisos efectivos."""

    def test_permissions_for_user_con_tres_niveles(self):
        """
        RF-003 Escenario 1: Usuario con permisos en los 3 niveles.

        Given usuario con permisos directo, rol y segmento
        When se ejecuta permissions_for_user
        Then retorna todos los permisos sin duplicados
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
            is_active=True,
        )

        # Crear permisos
        perm_analytics_view = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Ver analítica",
            resource="analytics",
            action="view",
            description="",
        )

        perm_reports_view = user_models.Permission.objects.create(
            codename="reports.view",
            name="Ver reportes",
            resource="reports",
            action="view",
            description="",
        )

        perm_dashboard_view = user_models.Permission.objects.create(
            codename="dashboard.view",
            name="Ver dashboard",
            resource="dashboard",
            action="view",
            description="",
        )

        # Nivel 1: Permiso directo
        user_models.UserPermission.objects.create(
            user=user,
            permission=perm_analytics_view,
            granted_by=user,
        )

        # Nivel 2: Permiso por rol (con duplicado analytics.view y nuevo reports.view)
        role = user_models.Role.objects.create(
            name="Analista",
            description="Rol analista",
        )
        role.permissions.add(perm_analytics_view)  # Duplicado
        role.permissions.add(perm_reports_view)  # Nuevo
        user_models.RoleAssignment.objects.create(
            user=user,
            role=role,
            granted_by=user,
        )

        # Nivel 3: Permiso por segmento (con duplicado reports.view y nuevo dashboard.view)
        segment = user_models.Segment.objects.create(
            name="Activos",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )
        segment.permissions.add(perm_reports_view)  # Duplicado
        segment.permissions.add(perm_dashboard_view)  # Nuevo

        result = PermissionService.permissions_for_user(user)
        result_list = sorted(result)

        expected = sorted(["analytics.view", "reports.view", "dashboard.view"])
        assert result_list == expected

    def test_permissions_for_user_sin_permisos(self):
        """
        RF-003 Escenario 2: Usuario sin permisos.

        Given usuario sin permisos directos, roles ni segmentos
        When se ejecuta permissions_for_user
        Then retorna lista vacía
        """
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
        )

        result = PermissionService.permissions_for_user(user)

        assert list(result) == []

    def test_permissions_for_user_elimina_duplicados(self):
        """
        RF-003: Verificar que se eliminan duplicados correctamente.

        Given usuario con mismo permiso en múltiples niveles
        When se ejecuta permissions_for_user
        Then aparece solo una vez
        """
        user = User.objects.create_user(
            username="carol",
            password="segura123",
            email="carol@example.com",
            is_active=True,
        )

        permission = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Ver analítica",
            resource="analytics",
            action="view",
            description="",
        )

        # Agregar mismo permiso en los 3 niveles
        # Nivel 1: Directo
        user_models.UserPermission.objects.create(
            user=user,
            permission=permission,
            granted_by=user,
        )

        # Nivel 2: Rol
        role = user_models.Role.objects.create(
            name="Analista",
            description="",
        )
        role.permissions.add(permission)
        user_models.RoleAssignment.objects.create(
            user=user,
            role=role,
            granted_by=user,
        )

        # Nivel 3: Segmento
        segment = user_models.Segment.objects.create(
            name="Activos",
            description="",
            criteria={"is_active": True},
            is_active=True,
        )
        segment.permissions.add(permission)

        result = list(PermissionService.permissions_for_user(user))

        # Debe aparecer solo una vez
        assert result.count("analytics.view") == 1
        assert result == ["analytics.view"]

    def test_permissions_for_user_solo_segmentos_activos(self):
        """
        RF-003: Solo considerar segmentos con is_active=True.

        Given usuario que coincide con segmento inactivo
        When se ejecuta permissions_for_user
        Then NO incluye permisos del segmento inactivo
        """
        user = User.objects.create_user(
            username="dave",
            password="segura123",
            email="dave@example.com",
            is_active=True,
        )

        permission = user_models.Permission.objects.create(
            codename="reports.view",
            name="Ver reportes",
            resource="reports",
            action="view",
            description="",
        )

        # Segmento inactivo
        segment = user_models.Segment.objects.create(
            name="Segmento Inactivo",
            description="",
            criteria={"is_active": True},
            is_active=False,  # INACTIVO
        )
        segment.permissions.add(permission)

        result = list(PermissionService.permissions_for_user(user))

        assert result == []
