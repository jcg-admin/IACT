"""Tests TDD para models de users basados en requisitos funcionales.

Requisitos cubiertos:
- RF-002: Gestión de permisos granulares
- RF-004: Segmentación con criterios dinámicos
- RF-005: Gestión de roles
- RF-006: Borrado lógico de usuarios
"""

import pytest
from datetime import datetime, timezone
from django.contrib.auth import get_user_model

from callcentersite.apps.users import models as user_models

User = get_user_model()


@pytest.mark.django_db
class TestRF002GestionPermisosGranulares:
    """Tests para RF-002: Gestión de permisos granulares."""

    def test_crear_permiso_valido(self):
        """
        RF-002 Escenario 1: Crear permiso válido.

        Given datos válidos de permiso
        When se crea el permiso
        Then se crea exitosamente con ID único
        """
        permission = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Puede ver analítica",
            resource="analytics",
            action="view",
            description="Permite ver reportes de analítica",
        )

        assert permission.id > 0
        assert permission.codename == "analytics.view"
        assert permission.name == "Puede ver analítica"
        assert permission.resource == "analytics"
        assert permission.action == "view"
        assert permission.description == "Permite ver reportes de analítica"

    def test_codename_es_unico_en_hash(self):
        """
        RF-002: Codename debe ser único (verificado por hash).

        Given dos permisos con mismo codename
        When se almacenan en set
        Then se reconocen como el mismo objeto
        """
        perm1 = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Permiso 1",
            resource="analytics",
            action="view",
            description="Desc 1",
        )

        perm2 = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Permiso 2 (mismo codename)",
            resource="analytics",
            action="view",
            description="Desc 2",
        )

        # Hash debe ser igual para mismo codename
        assert hash(perm1) == hash(perm2)

        # En un set, ambos deberían reducirse a uno
        perms_set = {perm1, perm2}
        assert len(perms_set) == 1

    def test_permission_manager_create(self):
        """
        RF-002: PermissionManager.create genera ID incremental.

        Given múltiples permisos creados
        When se usan create
        Then cada uno tiene ID único incremental
        """
        perm1 = user_models.Permission.objects.create(
            codename="p1",
            name="P1",
            resource="r1",
            action="a1",
            description="",
        )

        perm2 = user_models.Permission.objects.create(
            codename="p2",
            name="P2",
            resource="r2",
            action="a2",
            description="",
        )

        assert perm1.id > 0
        assert perm2.id > 0
        assert perm2.id > perm1.id  # IDs incrementales

    def test_permission_manager_all(self):
        """
        RF-002: PermissionManager.all() retorna todos los permisos.

        Given varios permisos creados
        When se llama all()
        Then retorna lista con todos
        """
        perm1 = user_models.Permission.objects.create(
            codename="p1",
            name="P1",
            resource="r1",
            action="a1",
            description="",
        )

        perm2 = user_models.Permission.objects.create(
            codename="p2",
            name="P2",
            resource="r2",
            action="a2",
            description="",
        )

        all_perms = user_models.Permission.objects.all()

        assert len(all_perms) >= 2
        assert perm1 in all_perms
        assert perm2 in all_perms


@pytest.mark.django_db
class TestRF004SegmentacionCriteriosDinamicos:
    """Tests para RF-004: Segmentación con criterios dinámicos."""

    def test_segment_matches_con_criterio_simple(self):
        """
        RF-004 Escenario 1: Usuario coincide con criterio simple.

        Given segmento con criterio is_active=True
          And usuario con is_active=True
        When se evalúa matches()
        Then retorna True
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
            is_active=True,
        )

        segment = user_models.Segment.objects.create(
            name="Activos",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )

        assert segment.matches(user) is True

    def test_segment_no_matches_cuando_criterio_difiere(self):
        """
        RF-004 Escenario 2: Usuario NO coincide con criterio.

        Given segmento con criterio is_active=True
          And usuario con is_active=False
        When se evalúa matches()
        Then retorna False
        """
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
            is_active=False,
        )

        segment = user_models.Segment.objects.create(
            name="Activos",
            description="Usuarios activos",
            criteria={"is_active": True},
            is_active=True,
        )

        assert segment.matches(user) is False

    def test_segment_matches_criterios_multiples_and(self):
        """
        RF-004 Escenario 3: Criterios múltiples (AND lógico).

        Given segmento con múltiples criterios
          And usuario que cumple TODOS
        When se evalúa matches()
        Then retorna True
        """
        user = User.objects.create_user(
            username="carol",
            password="segura123",
            email="carol@example.com",
            is_active=True,
        )
        # Agregar atributo custom para test
        user.department = "sales"

        segment = user_models.Segment.objects.create(
            name="Ventas Activos",
            description="",
            criteria={"is_active": True, "department": "sales"},
            is_active=True,
        )

        assert segment.matches(user) is True

    def test_segment_no_matches_cuando_uno_difiere(self):
        """
        RF-004 Escenario 4: Criterios múltiples - uno NO coincide.

        Given segmento con múltiples criterios
          And usuario que cumple solo algunos
        When se evalúa matches()
        Then retorna False
        """
        user = User.objects.create_user(
            username="dave",
            password="segura123",
            email="dave@example.com",
            is_active=True,
        )
        user.department = "engineering"  # Diferente

        segment = user_models.Segment.objects.create(
            name="Ventas Activos",
            description="",
            criteria={"is_active": True, "department": "sales"},
            is_active=True,
        )

        assert segment.matches(user) is False

    def test_segment_matches_campo_inexistente_retorna_false(self):
        """
        RF-004 Escenario 6: Campo no existe en usuario.

        Given segmento con criterio sobre campo inexistente
          And usuario sin ese atributo
        When se evalúa matches()
        Then retorna False
        """
        user = User.objects.create_user(
            username="eve",
            password="segura123",
            email="eve@example.com",
        )

        segment = user_models.Segment.objects.create(
            name="Segmento",
            description="",
            criteria={"campo_inexistente": "valor"},
            is_active=True,
        )

        assert segment.matches(user) is False

    def test_active_segments_filtra_inactivos(self):
        """
        RF-004 Escenario 5: Segmentos inactivos no se evalúan.

        Given un segmento con is_active=False
        When se llama active_segments()
        Then NO aparece en la lista
        """
        active_segment = user_models.Segment.objects.create(
            name="Activo",
            description="",
            criteria={"is_active": True},
            is_active=True,
        )

        inactive_segment = user_models.Segment.objects.create(
            name="Inactivo",
            description="",
            criteria={"is_active": True},
            is_active=False,  # INACTIVO
        )

        active_list = list(user_models.Segment.objects.active_segments())

        assert active_segment in active_list
        assert inactive_segment not in active_list

    def test_with_permission_retorna_solo_segmentos_con_codename(self):
        """
        RF-004: SegmentManager.with_permission() filtra por permiso.

        Given varios segmentos activos
          And solo uno tiene el permiso solicitado
        When se llama with_permission(codename)
        Then retorna solo el segmento que lo tiene
        """
        permission_view = user_models.Permission.objects.create(
            codename="analytics.view",
            name="Ver analítica",
            resource="analytics",
            action="view",
            description="",
        )

        permission_create = user_models.Permission.objects.create(
            codename="analytics.create",
            name="Crear analítica",
            resource="analytics",
            action="create",
            description="",
        )

        segment_with_view = user_models.Segment.objects.create(
            name="Con View",
            description="",
            criteria={"is_active": True},
            is_active=True,
        )
        segment_with_view.permissions.add(permission_view)

        segment_with_create = user_models.Segment.objects.create(
            name="Con Create",
            description="",
            criteria={"is_active": True},
            is_active=True,
        )
        segment_with_create.permissions.add(permission_create)

        segments_with_view = list(
            user_models.Segment.objects.with_permission("analytics.view")
        )

        assert segment_with_view in segments_with_view
        assert segment_with_create not in segments_with_view


@pytest.mark.django_db
class TestPermissionCollection:
    """Tests para PermissionCollection."""

    def test_add_permission_sin_duplicados(self):
        """
        PermissionCollection.add() no agrega duplicados.

        Given una colección
        When se agrega mismo permiso dos veces
        Then solo aparece una vez
        """
        permission = user_models.Permission.objects.create(
            codename="test.perm",
            name="Test",
            resource="test",
            action="perm",
            description="",
        )

        collection = user_models.PermissionCollection()
        collection.add(permission)
        collection.add(permission)  # Duplicado

        assert len(collection) == 1

    def test_has_codename(self):
        """
        PermissionCollection.has_codename() verifica existencia.

        Given una colección con permisos
        When se busca por codename
        Then retorna True si existe
        """
        permission = user_models.Permission.objects.create(
            codename="test.perm",
            name="Test",
            resource="test",
            action="perm",
            description="",
        )

        collection = user_models.PermissionCollection()
        collection.add(permission)

        assert collection.has_codename("test.perm") is True
        assert collection.has_codename("otro.perm") is False

    def test_values_list_flat(self):
        """
        PermissionCollection.values_list() extrae campo.

        Given una colección con permisos
        When se llama values_list(field, flat=True)
        Then retorna lista de valores de ese campo
        """
        perm1 = user_models.Permission.objects.create(
            codename="perm1",
            name="P1",
            resource="r1",
            action="a1",
            description="",
        )

        perm2 = user_models.Permission.objects.create(
            codename="perm2",
            name="P2",
            resource="r2",
            action="a2",
            description="",
        )

        collection = user_models.PermissionCollection()
        collection.add(perm1)
        collection.add(perm2)

        codenames = collection.values_list("codename", flat=True)

        assert sorted(codenames) == sorted(["perm1", "perm2"])

    def test_values_list_sin_flat_lanza_error(self):
        """
        PermissionCollection.values_list() sin flat=True lanza ValueError.
        """
        collection = user_models.PermissionCollection()

        with pytest.raises(ValueError, match="Solo se soporta flat=True"):
            collection.values_list("codename", flat=False)


@pytest.mark.django_db
class TestUserModel:
    """Tests para el modelo User."""

    def test_user_mark_deleted(self):
        """
        User.mark_deleted() realiza borrado lógico.

        Given un usuario activo
        When se llama mark_deleted()
        Then is_active=False, is_deleted=True, deleted_at se establece
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
            is_active=True,
        )

        assert user.is_deleted is False
        assert user.deleted_at is None

        user.mark_deleted()

        assert user.is_active is False
        assert user.is_deleted is True
        assert user.deleted_at is not None
        assert isinstance(user.deleted_at, datetime)

    def test_user_is_authenticated_cuando_activo(self):
        """
        User.is_authenticated retorna True cuando está activo.

        Given usuario activo y no eliminado
        When se consulta is_authenticated
        Then retorna True
        """
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
            is_active=True,
        )
        user.set_authenticated(True)

        assert user.is_authenticated is True

    def test_user_is_authenticated_false_cuando_deleted(self):
        """
        User.is_authenticated retorna False cuando está eliminado.

        Given usuario eliminado lógicamente
        When se consulta is_authenticated
        Then retorna False
        """
        user = User.objects.create_user(
            username="carol",
            password="segura123",
            email="carol@example.com",
        )
        user.mark_deleted()

        assert user.is_authenticated is False

    def test_user_timestamps_autogenerados(self):
        """
        User tiene created_at y updated_at autogenerados.

        Given un usuario creado
        When se consulta created_at y updated_at
        Then están establecidos
        """
        user = User.objects.create_user(
            username="dave",
            password="segura123",
            email="dave@example.com",
        )

        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


@pytest.mark.django_db
class TestRoleAssignmentManager:
    """Tests para RoleAssignmentManager."""

    def test_roles_for_user(self):
        """
        RoleAssignmentManager.roles_for_user() retorna roles del usuario.

        Given un usuario con múltiples roles asignados
        When se llama roles_for_user(user)
        Then retorna lista de roles asignados
        """
        user = User.objects.create_user(
            username="alice",
            password="segura123",
            email="alice@example.com",
        )

        role1 = user_models.Role.objects.create(
            name="Analista",
            description="",
        )

        role2 = user_models.Role.objects.create(
            name="Auditor",
            description="",
        )

        user_models.RoleAssignment.objects.create(
            user=user,
            role=role1,
            granted_by=user,
        )

        user_models.RoleAssignment.objects.create(
            user=user,
            role=role2,
            granted_by=user,
        )

        roles = user_models.RoleAssignment.objects.roles_for_user(user)

        assert len(roles) == 2
        assert role1 in roles
        assert role2 in roles


@pytest.mark.django_db
class TestUserPermissionManager:
    """Tests para UserPermissionManager."""

    def test_has_permission(self):
        """
        UserPermissionManager.has_permission() verifica permiso directo.

        Given usuario con permiso directo
        When se llama has_permission(user, codename)
        Then retorna True
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
            description="",
        )

        user_models.UserPermission.objects.create(
            user=user,
            permission=permission,
            granted_by=user,
        )

        assert (
            user_models.UserPermission.objects.has_permission(user, "analytics.view")
            is True
        )
        assert (
            user_models.UserPermission.objects.has_permission(user, "otro.permiso")
            is False
        )

    def test_permissions_for_user(self):
        """
        UserPermissionManager.permissions_for_user() retorna permisos directos.

        Given usuario con múltiples permisos directos
        When se llama permissions_for_user(user)
        Then retorna lista de Permission
        """
        user = User.objects.create_user(
            username="bob",
            password="segura123",
            email="bob@example.com",
        )

        perm1 = user_models.Permission.objects.create(
            codename="perm1",
            name="P1",
            resource="r1",
            action="a1",
            description="",
        )

        perm2 = user_models.Permission.objects.create(
            codename="perm2",
            name="P2",
            resource="r2",
            action="a2",
            description="",
        )

        user_models.UserPermission.objects.create(
            user=user,
            permission=perm1,
            granted_by=user,
        )

        user_models.UserPermission.objects.create(
            user=user,
            permission=perm2,
            granted_by=user,
        )

        perms = user_models.UserPermission.objects.permissions_for_user(user)

        assert len(perms) == 2
        assert perm1 in perms
        assert perm2 in perms
