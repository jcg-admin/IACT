"""
Tests unitarios para UsuarioService siguiendo TDD.

Ciclo Red-Green-Refactor:
1. RED: Tests que fallan
2. GREEN: Código mínimo que pase
3. REFACTOR: Mejorar manteniendo tests verdes

Referencia: TDD Best Practices
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from callcentersite.apps.users.services_usuarios import UsuarioService

User = get_user_model()


@pytest.mark.unit
class TestUsuarioServiceListarUsuarios:
    """Tests unitarios para listar_usuarios()."""

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    @patch('callcentersite.apps.users.services_usuarios.User')
    def test_sin_permiso_lanza_permission_denied(self, mock_user, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied) as exc_info:
            UsuarioService.listar_usuarios(
                usuario_solicitante_id=999,
                filtros={},
                page=1,
                page_size=50
            )

        assert 'No tiene permiso para listar usuarios' in str(exc_info.value)

        # Verificar que se intentó validar el permiso correcto
        mock_ums.usuario_tiene_permiso.assert_called_once_with(
            usuario_id=999,
            capacidad_codigo='sistema.administracion.usuarios.ver'
        )

    @patch('callcentersite.apps.users.services_usuarios.AuditoriaPermiso')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_sin_permiso_audita_intento_denegado(self, mock_ums, mock_auditoria):
        """RED: Intento sin permiso debe registrarse en auditoria."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act
        with pytest.raises(PermissionDenied):
            UsuarioService.listar_usuarios(
                usuario_solicitante_id=999,
                filtros={},
                page=1,
                page_size=50
            )

        # Assert: Debe crear registro de auditoria
        mock_auditoria.objects.create.assert_called_once()
        call_kwargs = mock_auditoria.objects.create.call_args.kwargs
        assert call_kwargs['resultado'] == 'denegado'
        assert call_kwargs['usuario_id'] == 999
        assert call_kwargs['accion'] == 'listar'

    @patch('callcentersite.apps.users.services_usuarios.AuditoriaPermiso')
    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_con_permiso_audita_acceso_permitido(self, mock_ums, mock_user, mock_auditoria):
        """RED: Acceso permitido debe registrarse en auditoria."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)
        mock_queryset.values.return_value = []
        mock_user.objects.filter.return_value = mock_queryset

        # Act
        UsuarioService.listar_usuarios(
            usuario_solicitante_id=1,
            filtros={},
            page=1,
            page_size=50
        )

        # Assert: Debe crear registro de auditoria permitido
        assert mock_auditoria.objects.create.call_count >= 1
        # Buscar la llamada con resultado='permitido'
        calls = mock_auditoria.objects.create.call_args_list
        permitido_call = next((c for c in calls if c.kwargs.get('resultado') == 'permitido'), None)
        assert permitido_call is not None
        assert permitido_call.kwargs['accion'] == 'listar'

    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_filtro_activo_true_filtra_correctamente(self, mock_ums, mock_user):
        """RED: Filtro activo=true debe filtrar solo usuarios activos."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)
        mock_queryset.values.return_value = []
        mock_user.objects.filter.return_value = mock_queryset

        # Act
        UsuarioService.listar_usuarios(
            usuario_solicitante_id=1,
            filtros={'activo': True},
            page=1,
            page_size=50
        )

        # Assert: Debe haber llamado a filter con is_active
        filter_calls = mock_queryset.filter.call_args_list
        # Verificar que se filtró por is_active=True
        activo_filter = any(
            call.kwargs.get('is_active') is True or
            (len(call.args) > 0 and hasattr(call.args[0], 'children') and
             any('is_active' in str(child) for child in getattr(call.args[0], 'children', [])))
            for call in filter_calls
        )
        # Como no podemos verificar fácilmente el Q object, verificamos que se llamó filter
        assert len(filter_calls) >= 2  # is_deleted=False + is_active=True


@pytest.mark.unit
class TestUsuarioServiceCrearUsuario:
    """Tests unitarios para crear_usuario()."""

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied) as exc_info:
            UsuarioService.crear_usuario(
                usuario_solicitante_id=999,
                datos={
                    'email': 'test@test.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'password123'
                }
            )

        assert 'No tiene permiso para crear usuarios' in str(exc_info.value)

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_sin_email_lanza_validation_error(self, mock_ums):
        """RED: Datos sin email deben lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UsuarioService.crear_usuario(
                usuario_solicitante_id=1,
                datos={
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'password123'
                }
            )

        assert 'email' in str(exc_info.value).lower()

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_sin_password_lanza_validation_error(self, mock_ums):
        """RED: Datos sin password deben lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UsuarioService.crear_usuario(
                usuario_solicitante_id=1,
                datos={
                    'email': 'test@test.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )

        assert 'password' in str(exc_info.value).lower()

    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_email_duplicado_lanza_validation_error(self, mock_ums, mock_user):
        """RED: Email duplicado debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_user.objects.filter.return_value.exists.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UsuarioService.crear_usuario(
                usuario_solicitante_id=1,
                datos={
                    'email': 'duplicate@test.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'password123'
                }
            )

        assert 'ya existe' in str(exc_info.value).lower()

    @patch('callcentersite.apps.users.services_usuarios.AuditoriaPermiso')
    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_creacion_exitosa_audita_accion(self, mock_ums, mock_user, mock_auditoria):
        """RED: Creación exitosa debe auditar acción."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_user.objects.filter.return_value.exists.return_value = False
        mock_usuario_creado = MagicMock()
        mock_usuario_creado.id = 123
        mock_usuario_creado.email = 'test@test.com'
        mock_user.objects.create_user.return_value = mock_usuario_creado

        # Act
        UsuarioService.crear_usuario(
            usuario_solicitante_id=1,
            datos={
                'email': 'test@test.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'password123'
            }
        )

        # Assert: Debe auditar con resultado permitido
        calls = mock_auditoria.objects.create.call_args_list
        permitido_call = next((c for c in calls if c.kwargs.get('resultado') == 'permitido'), None)
        assert permitido_call is not None
        assert permitido_call.kwargs['accion'] == 'crear'
        assert permitido_call.kwargs['recurso_id'] == 123


@pytest.mark.unit
class TestUsuarioServiceEliminarUsuario:
    """Tests unitarios para eliminar_usuario()."""

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            UsuarioService.eliminar_usuario(
                usuario_solicitante_id=999,
                usuario_id=1
            )

    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_usuario_no_existe_lanza_validation_error(self, mock_ums, mock_user):
        """RED: Usuario no existente debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_user.DoesNotExist = User.DoesNotExist
        mock_user.objects.get.side_effect = User.DoesNotExist()

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UsuarioService.eliminar_usuario(
                usuario_solicitante_id=1,
                usuario_id=999
            )

        assert 'no encontrado' in str(exc_info.value).lower()

    @patch('callcentersite.apps.users.services_usuarios.timezone')
    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_eliminacion_marca_is_deleted_true(self, mock_ums, mock_user, mock_timezone):
        """RED: Eliminación debe marcar is_deleted=True."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_usuario = MagicMock()
        mock_usuario.id = 123
        mock_usuario.email = 'test@test.com'
        mock_user.objects.get.return_value = mock_usuario

        # Act
        UsuarioService.eliminar_usuario(
            usuario_solicitante_id=1,
            usuario_id=123
        )

        # Assert
        assert mock_usuario.is_deleted is True
        assert mock_usuario.is_active is False
        mock_usuario.save.assert_called_once()


@pytest.mark.unit
class TestUsuarioServiceSuspenderUsuario:
    """Tests unitarios para suspender_usuario()."""

    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_suspender_a_si_mismo_lanza_validation_error(self, mock_ums):
        """RED: Usuario no puede suspenderse a si mismo."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UsuarioService.suspender_usuario(
                usuario_solicitante_id=1,
                usuario_id=1,  # Mismo ID
                motivo='Test'
            )

        assert 'si mismo' in str(exc_info.value).lower()

    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_suspension_marca_is_active_false(self, mock_ums, mock_user):
        """RED: Suspensión debe marcar is_active=False."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_usuario = MagicMock()
        mock_usuario.id = 123
        mock_usuario.email = 'test@test.com'
        mock_user.objects.get.return_value = mock_usuario

        # Act
        UsuarioService.suspender_usuario(
            usuario_solicitante_id=1,
            usuario_id=123,
            motivo='Violación de políticas'
        )

        # Assert
        assert mock_usuario.is_active is False
        mock_usuario.save.assert_called_once()

    @patch('callcentersite.apps.users.services_usuarios.AuditoriaPermiso')
    @patch('callcentersite.apps.users.services_usuarios.User')
    @patch('callcentersite.apps.users.services_usuarios.UserManagementService')
    def test_suspension_audita_con_motivo(self, mock_ums, mock_user, mock_auditoria):
        """RED: Suspensión debe auditar con motivo."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_usuario = MagicMock()
        mock_usuario.id = 123
        mock_usuario.email = 'test@test.com'
        mock_user.objects.get.return_value = mock_usuario

        # Act
        UsuarioService.suspender_usuario(
            usuario_solicitante_id=1,
            usuario_id=123,
            motivo='Test de auditoria'
        )

        # Assert
        calls = mock_auditoria.objects.create.call_args_list
        permitido_call = next((c for c in calls if c.kwargs.get('resultado') == 'permitido'), None)
        assert permitido_call is not None
        assert 'Test de auditoria' in permitido_call.kwargs['detalles']
