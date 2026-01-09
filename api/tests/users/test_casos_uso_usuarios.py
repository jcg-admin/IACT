"""
Tests TDD para Casos de Uso del módulo de Usuarios.

Sistema de gestión de usuarios/agentes del call center.
Casos de uso implementados siguiendo TDD.
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestUC014_CrearUsuario:
    """
    UC-014: Crear Usuario/Agente.

    Actor: Administrador
    Precondición: Usuario autenticado con permiso "sistema.admin.usuarios.crear"

    Flujo principal:
    1. Sistema recibe datos del nuevo usuario
    2. Sistema valida que username y email son únicos
    3. Sistema hashea la contraseña con bcrypt
    4. Sistema crea usuario con status='ACTIVO'
    5. Sistema audita creación
    """

    def test_crear_usuario_exitoso(self):
        """
        UC-014 Escenario 1: Creación exitosa de usuario.

        Given datos válidos de usuario
        When se crea el usuario
        Then usuario es creado con contraseña hasheada
          And status es ACTIVO por defecto
          And is_locked es False
        """
        # Arrange
        from callcentersite.apps.users.services import UserService

        # Act
        usuario = UserService.crear_usuario(
            username='nuevo.agente',
            email='nuevo.agente@company.com',
            password='SecureP@ss123',
            segment='GE'
        )

        # Assert
        assert usuario is not None
        assert usuario.username == 'nuevo.agente'
        assert usuario.email == 'nuevo.agente@company.com'
        assert usuario.status == 'ACTIVO'
        assert usuario.is_locked is False
        assert usuario.failed_login_attempts == 0
        # Verificar que password está hasheada (Django usa diferentes algoritmos)
        assert usuario.password != 'SecureP@ss123'
        # Password hasheada tiene formato: algorithm$salt$hash
        assert '$' in usuario.password

    def test_crear_usuario_con_username_duplicado(self):
        """
        UC-014 Escenario 2: Intento de crear usuario con username existente.

        Given un usuario existente con username 'agent1'
        When se intenta crear otro usuario con mismo username
        Then sistema lanza ValidationError
        """
        # Arrange
        User.objects.create_user(
            username='agent1',
            password='pass',
            email='agent1@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserService.crear_usuario(
                username='agent1',  # Username duplicado
                email='different@test.com',
                password='SecureP@ss123'
            )

        assert 'username' in str(exc_info.value).lower()

    def test_crear_usuario_con_email_duplicado(self):
        """
        UC-014 Escenario 3: Intento de crear usuario con email existente.

        Given un usuario existente con email
        When se intenta crear otro usuario con mismo email
        Then sistema lanza ValidationError
        """
        # Arrange
        User.objects.create_user(
            username='agent1',
            password='pass',
            email='unique@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserService.crear_usuario(
                username='agent2',
                email='unique@test.com',  # Email duplicado
                password='SecureP@ss123'
            )

        assert 'email' in str(exc_info.value).lower()


@pytest.mark.django_db
class TestUC015_ActualizarUsuario:
    """
    UC-015: Actualizar Perfil de Usuario.

    Actor: Administrador/Usuario
    Precondición: Usuario existe

    Flujo principal:
    1. Sistema recibe ID de usuario y campos a actualizar
    2. Sistema valida que usuario existe
    3. Sistema actualiza campos permitidos
    4. Sistema audita cambios
    """

    def test_actualizar_email_usuario(self):
        """
        UC-015 Escenario 1: Actualizar email de usuario.

        Given un usuario existente
        When se actualiza el email
        Then email es actualizado correctamente
        """
        # Arrange
        usuario = User.objects.create_user(
            username='test.user',
            password='pass',
            email='old@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        usuario_actualizado = UserService.actualizar_usuario(
            usuario_id=usuario.id,
            email='new@test.com'
        )

        # Assert
        assert usuario_actualizado.email == 'new@test.com'

    def test_actualizar_segment_usuario(self):
        """
        UC-015 Escenario 2: Actualizar segmento de usuario.

        Given un usuario con segment='GE'
        When se actualiza a segment='VIP'
        Then segmento es actualizado
        """
        # Arrange
        usuario = User.objects.create_user(
            username='agent.segment',
            password='pass',
            email='agent@test.com',
            segment='GE'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        usuario_actualizado = UserService.actualizar_usuario(
            usuario_id=usuario.id,
            segment='VIP'
        )

        # Assert
        assert usuario_actualizado.segment == 'VIP'


@pytest.mark.django_db
class TestUC016_BloquearDesbloquearUsuario:
    """
    UC-016: Bloquear/Desbloquear Usuario Manualmente.

    Actor: Administrador
    Precondición: Usuario existe y tiene permiso de administración

    Flujo principal:
    1. Sistema recibe ID de usuario y acción (bloquear/desbloquear)
    2. Sistema valida permisos del administrador
    3. Sistema actualiza is_locked y locked_until
    4. Sistema audita la acción
    5. Sistema envía notificación al usuario
    """

    def test_bloquear_usuario_manualmente(self):
        """
        UC-016 Escenario 1: Bloquear usuario manualmente.

        Given un usuario activo no bloqueado
        When administrador bloquea el usuario
        Then usuario es bloqueado con razón 'ADMIN_LOCK'
          And locked_until es NULL (indefinido)
        """
        # Arrange
        usuario = User.objects.create_user(
            username='problem.user',
            password='pass',
            email='problem@test.com',
            is_locked=False
        )

        from callcentersite.apps.users.services import UserService

        # Act
        UserService.bloquear_usuario(
            usuario_id=usuario.id,
            razon='Violación de políticas de uso'
        )

        # Assert
        usuario.refresh_from_db()
        assert usuario.is_locked is True
        assert usuario.lock_reason == 'ADMIN_LOCK'
        assert usuario.locked_until is None  # Indefinido

    def test_desbloquear_usuario_manualmente(self):
        """
        UC-016 Escenario 2: Desbloquear usuario previamente bloqueado.

        Given un usuario bloqueado
        When administrador desbloquea el usuario
        Then is_locked es False
          And locked_until es NULL
          And failed_login_attempts se resetea a 0
        """
        # Arrange
        usuario = User.objects.create_user(
            username='locked.user',
            password='pass',
            email='locked@test.com',
            is_locked=True,
            locked_until=timezone.now() + timedelta(hours=1),
            failed_login_attempts=3,
            lock_reason='MAX_FAILED_ATTEMPTS'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        UserService.desbloquear_usuario(usuario_id=usuario.id)

        # Assert
        usuario.refresh_from_db()
        assert usuario.is_locked is False
        assert usuario.locked_until is None
        assert usuario.failed_login_attempts == 0
        assert usuario.lock_reason == ''


@pytest.mark.django_db
class TestUC017_EliminarUsuario:
    """
    UC-017: Eliminar Usuario (Soft Delete).

    Actor: Administrador
    Precondición: Usuario existe y tiene permiso de eliminación

    Flujo principal:
    1. Sistema recibe ID de usuario a eliminar
    2. Sistema valida que usuario existe
    3. Sistema realiza soft delete (is_deleted=True)
    4. Sistema establece is_active=False
    5. Sistema registra deleted_at
    6. Sistema audita eliminación
    """

    def test_eliminar_usuario_soft_delete(self):
        """
        UC-017 Escenario 1: Eliminación lógica de usuario.

        Given un usuario activo
        When se elimina el usuario
        Then is_deleted es True
          And is_active es False
          And deleted_at es timestamp actual
          And usuario NO es eliminado de la BD
        """
        # Arrange
        usuario = User.objects.create_user(
            username='to.delete',
            password='pass',
            email='delete@test.com',
            is_active=True
        )

        from callcentersite.apps.users.services import UserService

        # Act
        UserService.eliminar_usuario(usuario_id=usuario.id)

        # Assert
        usuario.refresh_from_db()
        assert usuario.is_deleted is True
        assert usuario.is_active is False
        assert usuario.deleted_at is not None
        # Verificar que sigue en BD
        assert User.objects.filter(id=usuario.id).exists()

    def test_usuario_eliminado_no_puede_autenticarse(self):
        """
        UC-017 Escenario 2: Usuario eliminado no puede hacer login.

        Given un usuario eliminado (soft delete)
        When intenta autenticarse
        Then is_authenticated property retorna False
        """
        # Arrange
        usuario = User.objects.create_user(
            username='deleted.user',
            password='pass',
            email='deleted@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        UserService.eliminar_usuario(usuario_id=usuario.id)

        # Assert
        usuario.refresh_from_db()
        assert usuario.is_authenticated is False


@pytest.mark.django_db
class TestUC018_ConsultarUsuarios:
    """
    UC-018: Consultar/Listar Usuarios.

    Actor: Administrador/Supervisor
    Precondición: Usuario autenticado con permiso de consulta

    Flujo principal:
    1. Sistema recibe filtros de búsqueda
    2. Sistema aplica filtros
    3. Sistema excluye usuarios eliminados por defecto
    4. Sistema retorna lista paginada
    """

    def test_listar_usuarios_activos(self):
        """
        UC-018 Escenario 1: Listar solo usuarios activos.

        Given 3 usuarios activos y 2 eliminados
        When se listan usuarios sin filtros
        Then retorna solo usuarios activos
        """
        # Arrange
        from callcentersite.apps.users.services import UserService

        # Usuarios activos
        for i in range(3):
            User.objects.create_user(
                username=f'active{i}',
                password='pass',
                email=f'active{i}@test.com'
            )

        # Usuarios eliminados
        for i in range(2):
            user = User.objects.create_user(
                username=f'deleted{i}',
                password='pass',
                email=f'deleted{i}@test.com'
            )
            user.mark_deleted()

        # Act
        usuarios = UserService.listar_usuarios()

        # Assert
        assert len(usuarios) == 3
        assert all(not u.is_deleted for u in usuarios)

    def test_filtrar_usuarios_por_segment(self):
        """
        UC-018 Escenario 2: Filtrar usuarios por segmento.

        Given usuarios con diferentes segmentos
        When se filtra por segment='VIP'
        Then retorna solo usuarios VIP
        """
        # Arrange
        User.objects.create_user(
            username='vip1', password='pass', email='vip1@test.com', segment='VIP'
        )
        User.objects.create_user(
            username='vip2', password='pass', email='vip2@test.com', segment='VIP'
        )
        User.objects.create_user(
            username='ge1', password='pass', email='ge1@test.com', segment='GE'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        usuarios_vip = UserService.listar_usuarios(segment='VIP')

        # Assert
        assert len(usuarios_vip) == 2
        assert all(u.segment == 'VIP' for u in usuarios_vip)

    def test_filtrar_usuarios_bloqueados(self):
        """
        UC-018 Escenario 3: Listar usuarios bloqueados.

        Given usuarios bloqueados y no bloqueados
        When se filtra por is_locked=True
        Then retorna solo usuarios bloqueados
        """
        # Arrange
        User.objects.create_user(
            username='locked1', password='pass', email='l1@test.com', is_locked=True
        )
        User.objects.create_user(
            username='locked2', password='pass', email='l2@test.com', is_locked=True
        )
        User.objects.create_user(
            username='active1', password='pass', email='a1@test.com', is_locked=False
        )

        from callcentersite.apps.users.services import UserService

        # Act
        usuarios_bloqueados = UserService.listar_usuarios(is_locked=True)

        # Assert
        assert len(usuarios_bloqueados) == 2
        assert all(u.is_locked for u in usuarios_bloqueados)


@pytest.mark.django_db
class TestUC019_CambiarContrasena:
    """
    UC-019: Cambiar Contraseña de Usuario.

    Actor: Usuario/Administrador
    Precondición: Usuario autenticado

    Flujo principal:
    1. Sistema recibe contraseña actual y nueva contraseña
    2. Sistema valida contraseña actual
    3. Sistema valida fortaleza de nueva contraseña
    4. Sistema hashea y guarda nueva contraseña
    5. Sistema audita cambio
    """

    def test_cambiar_contrasena_exitoso(self):
        """
        UC-019 Escenario 1: Cambio exitoso de contraseña.

        Given un usuario con contraseña válida
        When cambia su contraseña proporcionando la actual
        Then contraseña es actualizada y hasheada
        """
        # Arrange
        usuario = User.objects.create_user(
            username='change.pass',
            password='OldP@ss123',
            email='change@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act
        UserService.cambiar_contrasena(
            usuario_id=usuario.id,
            contrasena_actual='OldP@ss123',
            contrasena_nueva='NewP@ss456'
        )

        # Assert
        usuario.refresh_from_db()
        # Verificar que la nueva contraseña funciona
        from django.contrib.auth.hashers import check_password
        assert check_password('NewP@ss456', usuario.password)
        assert not check_password('OldP@ss123', usuario.password)

    def test_cambiar_contrasena_con_actual_incorrecta(self):
        """
        UC-019 Escenario 2: Intento con contraseña actual incorrecta.

        Given un usuario
        When intenta cambiar contraseña con contraseña actual incorrecta
        Then sistema lanza PermissionDenied
        """
        # Arrange
        usuario = User.objects.create_user(
            username='secure.user',
            password='CorrectP@ss123',
            email='secure@test.com'
        )

        from callcentersite.apps.users.services import UserService

        # Act & Assert
        with pytest.raises(PermissionDenied) as exc_info:
            UserService.cambiar_contrasena(
                usuario_id=usuario.id,
                contrasena_actual='WrongP@ss123',  # Incorrecta
                contrasena_nueva='NewP@ss456'
            )

        assert 'actual' in str(exc_info.value).lower() or 'incorrecta' in str(exc_info.value).lower()
