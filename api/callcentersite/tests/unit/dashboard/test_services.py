"""
Tests unitarios para DashboardService siguiendo TDD.

Referencia: TDD Best Practices
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.exceptions import PermissionDenied, ValidationError

from callcentersite.apps.dashboard.services import DashboardService


@pytest.mark.unit
class TestDashboardServiceExportar:
    """Tests unitarios para exportar()."""

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied) as exc_info:
            DashboardService.exportar(
                usuario_id=999,
                formato='pdf'
            )

        assert 'No tiene permiso para exportar dashboards' in str(exc_info.value)

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_formato_invalido_lanza_validation_error(self, mock_ums):
        """RED: Formato inválido debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DashboardService.exportar(
                usuario_id=1,
                formato='invalid'
            )

        assert 'invalido' in str(exc_info.value).lower()

    @patch('callcentersite.apps.dashboard.services.AuditoriaPermiso')
    @patch('callcentersite.apps.dashboard.services.timezone')
    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_exportacion_pdf_retorna_datos_correctos(self, mock_ums, mock_timezone, mock_auditoria):
        """RED: Exportación PDF debe retornar formato, archivo y timestamp."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_now = MagicMock()
        mock_now.timestamp.return_value = 1234567890
        mock_now.isoformat.return_value = '2025-11-08T10:00:00Z'
        mock_timezone.now.return_value = mock_now

        # Act
        resultado = DashboardService.exportar(
            usuario_id=1,
            formato='pdf'
        )

        # Assert
        assert resultado['formato'] == 'pdf'
        assert 'archivo' in resultado
        assert resultado['timestamp'] == '2025-11-08T10:00:00Z'

    @patch('callcentersite.apps.dashboard.services.AuditoriaPermiso')
    @patch('callcentersite.apps.dashboard.services.timezone')
    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_exportacion_excel_retorna_datos_correctos(self, mock_ums, mock_timezone, mock_auditoria):
        """RED: Exportación Excel debe retornar formato correcto."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_now = MagicMock()
        mock_now.timestamp.return_value = 1234567890
        mock_now.isoformat.return_value = '2025-11-08T10:00:00Z'
        mock_timezone.now.return_value = mock_now

        # Act
        resultado = DashboardService.exportar(
            usuario_id=1,
            formato='excel'
        )

        # Assert
        assert resultado['formato'] == 'excel'


@pytest.mark.unit
class TestDashboardServicePersonalizar:
    """Tests unitarios para personalizar()."""

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            DashboardService.personalizar(
                usuario_id=999,
                configuracion={'widgets': []}
            )

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_configuracion_no_dict_lanza_validation_error(self, mock_ums):
        """RED: Configuración que no es dict debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DashboardService.personalizar(
                usuario_id=1,
                configuracion='no es un dict'
            )

        assert 'objeto JSON' in str(exc_info.value)

    @patch('callcentersite.apps.dashboard.services.AuditoriaPermiso')
    @patch('callcentersite.apps.dashboard.services.DashboardConfiguracion')
    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_personalizacion_exitosa_retorna_config(self, mock_ums, mock_config_model, mock_auditoria):
        """RED: Personalización exitosa debe retornar objeto DashboardConfiguracion."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_config = MagicMock()
        mock_config.id = 123
        mock_config.configuracion = {'widgets': []}
        mock_config_model.objects.update_or_create.return_value = (mock_config, True)

        # Act
        resultado = DashboardService.personalizar(
            usuario_id=1,
            configuracion={'widgets': []}
        )

        # Assert
        assert resultado.id == 123
        assert resultado.configuracion == {'widgets': []}


@pytest.mark.unit
class TestDashboardServiceCompartir:
    """Tests unitarios para compartir()."""

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_sin_permiso_lanza_permission_denied(self, mock_ums):
        """RED: Usuario sin permiso debe lanzar PermissionDenied."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = False

        # Act & Assert
        with pytest.raises(PermissionDenied):
            DashboardService.compartir(
                usuario_id=999,
                compartir_con_usuario_id=1
            )

    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_sin_receptor_lanza_validation_error(self, mock_ums):
        """RED: Sin especificar receptor debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DashboardService.compartir(
                usuario_id=1,
                compartir_con_usuario_id=None,
                compartir_con_grupo_codigo=None
            )

        assert 'debe especificar' in str(exc_info.value).lower()

    @patch('callcentersite.apps.dashboard.services.AuditoriaPermiso')
    @patch('callcentersite.apps.dashboard.services.User')
    @patch('callcentersite.apps.dashboard.services.timezone')
    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_compartir_con_usuario_retorna_datos_correctos(
        self, mock_ums, mock_timezone, mock_user, mock_auditoria
    ):
        """RED: Compartir con usuario debe retornar email y tipo 'usuario'."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_usuario_receptor = MagicMock()
        mock_usuario_receptor.email = 'receptor@test.com'
        mock_user.objects.get.return_value = mock_usuario_receptor
        mock_now = MagicMock()
        mock_now.isoformat.return_value = '2025-11-08T10:00:00Z'
        mock_timezone.now.return_value = mock_now

        # Act
        resultado = DashboardService.compartir(
            usuario_id=1,
            compartir_con_usuario_id=2
        )

        # Assert
        assert resultado['compartido_con'] == 'receptor@test.com'
        assert resultado['tipo'] == 'usuario'
        assert resultado['timestamp'] == '2025-11-08T10:00:00Z'

    @patch('callcentersite.apps.dashboard.services.User')
    @patch('callcentersite.apps.dashboard.services.UserManagementService')
    def test_usuario_receptor_no_existe_lanza_validation_error(self, mock_ums, mock_user):
        """RED: Usuario receptor no existente debe lanzar ValidationError."""
        # Arrange
        mock_ums.usuario_tiene_permiso.return_value = True
        mock_user.DoesNotExist = Exception  # Simular excepción
        mock_user.objects.get.side_effect = Exception()

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DashboardService.compartir(
                usuario_id=1,
                compartir_con_usuario_id=999
            )

        assert 'no encontrado' in str(exc_info.value).lower()
