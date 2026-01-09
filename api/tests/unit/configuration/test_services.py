"""
Tests unitarios para ConfiguracionService siguiendo TDD.

Referencia: TDD Best Practices
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.exceptions import PermissionDenied, ValidationError

from callcentersite.apps.configuration.services import ConfiguracionService


@pytest.mark.unit
class TestConfiguracionServiceObtener:
    """Tests unitarios para obtener_configuracion()."""

    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied) as exc_info:
            ConfiguracionService.obtener_configuracion(
                usuario_id=999,
                categoria=None
            )

        assert 'No tiene permiso para ver configuraciones' in str(exc_info.value)

    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_categoria_retorna_todas(self, mock_ums, mock_config):
        """RED: Sin filtro de categoría debe retornar todas las configs."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.values.return_value = [
            {'id': 1, 'categoria': 'seguridad', 'clave': 'test'},
            {'id': 2, 'categoria': 'notificaciones', 'clave': 'test2'},
        ]
        mock_config.objects.filter.return_value = mock_queryset

        # Act
        resultado = ConfiguracionService.obtener_configuracion(
            usuario_id=1,
            categoria=None
        )

        # Assert
        assert len(resultado) == 2
        # No debe haber segundo filtro por categoria
        assert mock_queryset.filter.call_count == 1

    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_con_categoria_filtra_correctamente(self, mock_ums, mock_config):
        """RED: Con categoría debe filtrar solo esa categoría."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.values.return_value = [
            {'id': 1, 'categoria': 'seguridad', 'clave': 'test'},
        ]
        mock_config.objects.filter.return_value = mock_queryset

        # Act
        resultado = ConfiguracionService.obtener_configuracion(
            usuario_id=1,
            categoria='seguridad'
        )

        # Assert
        # Debe haber dos filtros: activa=True y categoria=seguridad
        assert mock_queryset.filter.call_count == 2


@pytest.mark.unit
class TestConfiguracionServiceEditar:
    """Tests unitarios para editar_configuracion()."""

    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            ConfiguracionService.editar_configuracion(
                usuario_id=999,
                clave='test.config',
                nuevo_valor='nuevo'
            )

    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_configuracion_no_existe_lanza_validation_error(self, mock_ums, mock_config):
        """RED: Configuración no existente debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_config.DoesNotExist = Exception
        mock_config.objects.get.side_effect = Exception()

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracionService.editar_configuracion(
                usuario_id=1,
                clave='inexistente',
                nuevo_valor='valor'
            )

        assert 'no encontrada' in str(exc_info.value).lower()

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.ConfiguracionHistorial')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_edicion_crea_registro_historial(
        self, mock_ums, mock_config, mock_historial, mock_transaction
    ):
        """RED: Edición debe crear registro en historial."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_configuracion = MagicMock()
        mock_configuracion.clave = 'test.config'
        mock_configuracion.valor = 'valor_antiguo'
        mock_config.objects.get.return_value = mock_configuracion
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        # Act
        ConfiguracionService.editar_configuracion(
            usuario_id=1,
            clave='test.config',
            nuevo_valor='valor_nuevo',
            ip_address='127.0.0.1',
            user_agent='Test'
        )

        # Assert
        mock_historial.objects.create.assert_called_once()
        call_kwargs = mock_historial.objects.create.call_args.kwargs
        assert call_kwargs['valor_anterior'] == 'valor_antiguo'
        assert call_kwargs['valor_nuevo'] == 'valor_nuevo'

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.ConfiguracionHistorial')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_edicion_actualiza_updated_by(
        self, mock_ums, mock_config, mock_historial, mock_transaction
    ):
        """RED: Edición debe actualizar updated_by_id."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_configuracion = MagicMock()
        mock_configuracion.valor = 'antiguo'
        mock_config.objects.get.return_value = mock_configuracion
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        # Act
        ConfiguracionService.editar_configuracion(
            usuario_id=123,
            clave='test.config',
            nuevo_valor='nuevo'
        )

        # Assert
        assert mock_configuracion.updated_by_id == 123
        mock_configuracion.save.assert_called_once()


@pytest.mark.unit
class TestConfiguracionServiceExportar:
    """Tests unitarios para exportar_configuracion()."""

    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            ConfiguracionService.exportar_configuracion(
                usuario_id=999,
                formato='json'
            )

    @patch('callcentersite.apps.configuration.services.AuditoriaPermiso')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_exportacion_retorna_dict_por_categoria(
        self, mock_ums, mock_config, mock_auditoria
    ):
        """RED: Exportación debe retornar dict organizado por categoría."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.values.return_value = [
            {'categoria': 'seguridad', 'clave': 'seg.1'},
            {'categoria': 'seguridad', 'clave': 'seg.2'},
            {'categoria': 'notificaciones', 'clave': 'not.1'},
        ]
        mock_config.objects.filter.return_value = mock_queryset

        # Act
        resultado = ConfiguracionService.exportar_configuracion(
            usuario_id=1,
            formato='json'
        )

        # Assert
        assert 'seguridad' in resultado
        assert 'notificaciones' in resultado
        assert len(resultado['seguridad']) == 2
        assert len(resultado['notificaciones']) == 1


@pytest.mark.unit
class TestConfiguracionServiceImportar:
    """Tests unitarios para importar_configuracion()."""

    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            ConfiguracionService.importar_configuracion(
                usuario_id=999,
                configuraciones_json={}
            )

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.ConfiguracionHistorial')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_importacion_actualiza_configs_existentes(
        self, mock_ums, mock_config, mock_historial, mock_transaction
    ):
        """RED: Importación debe actualizar configs existentes."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_configuracion = MagicMock()
        mock_configuracion.valor = 'antiguo'
        mock_config.objects.get.return_value = mock_configuracion
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        json_importar = {
            'seguridad': [
                {
                    'clave': 'seg.timeout',
                    'valor': '1800',
                    'tipo_dato': 'integer',
                    'valor_default': '900'
                }
            ]
        }

        # Act
        resultado = ConfiguracionService.importar_configuracion(
            usuario_id=1,
            configuraciones_json=json_importar
        )

        # Assert
        assert resultado['actualizadas'] == 1
        assert resultado['importadas'] == 0

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_importacion_crea_configs_nuevas(
        self, mock_ums, mock_config, mock_transaction
    ):
        """RED: Importación debe crear configs que no existen."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_config.DoesNotExist = Exception
        mock_config.objects.get.side_effect = Exception()
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        json_importar = {
            'nueva_categoria': [
                {
                    'clave': 'nueva.config',
                    'valor': 'valor',
                    'tipo_dato': 'string',
                    'valor_default': 'default'
                }
            ]
        }

        # Act
        resultado = ConfiguracionService.importar_configuracion(
            usuario_id=1,
            configuraciones_json=json_importar
        )

        # Assert
        assert resultado['importadas'] == 1
        assert resultado['actualizadas'] == 0
        mock_config.objects.create.assert_called_once()


@pytest.mark.unit
class TestConfiguracionServiceRestaurar:
    """Tests unitarios para restaurar_configuracion()."""

    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            ConfiguracionService.restaurar_configuracion(
                usuario_id=999,
                clave='test.config'
            )

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.ConfiguracionHistorial')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_restaurar_asigna_valor_default(
        self, mock_ums, mock_config, mock_historial, mock_transaction
    ):
        """RED: Restaurar debe asignar valor_default al valor."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_configuracion = MagicMock()
        mock_configuracion.valor = 'modificado'
        mock_configuracion.valor_default = 'original'
        mock_config.objects.get.return_value = mock_configuracion
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        # Act
        ConfiguracionService.restaurar_configuracion(
            usuario_id=1,
            clave='test.config'
        )

        # Assert
        assert mock_configuracion.valor == 'original'
        mock_configuracion.save.assert_called_once()

    @patch('callcentersite.apps.configuration.services.transaction')
    @patch('callcentersite.apps.configuration.services.ConfiguracionHistorial')
    @patch('callcentersite.apps.configuration.services.Configuracion')
    @patch('callcentersite.apps.configuration.services.UserManagementService')
    def test_restaurar_crea_registro_historial(
        self, mock_ums, mock_config, mock_historial, mock_transaction
    ):
        """RED: Restaurar debe crear registro en historial."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_configuracion = MagicMock()
        mock_configuracion.clave = 'test.config'
        mock_configuracion.valor = 'modificado'
        mock_configuracion.valor_default = 'original'
        mock_config.objects.get.return_value = mock_configuracion
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        # Act
        ConfiguracionService.restaurar_configuracion(
            usuario_id=1,
            clave='test.config'
        )

        # Assert
        mock_historial.objects.create.assert_called_once()
        call_kwargs = mock_historial.objects.create.call_args.kwargs
        assert call_kwargs['valor_anterior'] == 'modificado'
        assert call_kwargs['valor_nuevo'] == 'original'
