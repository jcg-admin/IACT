"""Tests de integración para la API REST de dashboards."""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.dashboard.models import DashboardConfiguracion

User = get_user_model()


@pytest.mark.django_db
class TestDashboardAPIREST:
    """Tests de integración para /api/v1/dashboard/."""

    def setup_method(self):
        """Configura un cliente autenticado y stubs de permisos por prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test.user',
            password='TestP@ss123',
            email='test@test.com',
        )
        self.client.force_authenticate(user=self.user)

        # Parchear verificaciones de permisos para aislar lógica del dashboard
        self.perm_patch = patch(
            'callcentersite.apps.users.services_permisos_granular.'
            'UserManagementService.usuario_tiene_permiso',
            side_effect=lambda usuario_id, *args, **kwargs: bool(usuario_id),
        )
        self.verificar_patch = patch(
            'callcentersite.apps.users.service_helpers.verificar_permiso_y_auditar',
            return_value=None,
        )
        self.auditar_patch = patch(
            'callcentersite.apps.users.service_helpers.auditar_accion_exitosa',
            return_value=None,
        )

        self.perm_patch.start()
        self.verificar_patch.start()
        self.auditar_patch.start()

    def teardown_method(self):
        """Detiene los parches aplicados durante cada prueba."""
        self.perm_patch.stop()
        self.verificar_patch.stop()
        self.auditar_patch.stop()

    def test_api_ver_dashboard_overview(self):
        """GET /api/v1/dashboard/overview/ devuelve widgets y metadatos."""
        response = self.client.get('/api/v1/dashboard/overview/')

        assert response.status_code == status.HTTP_200_OK
        assert 'widgets' in response.data
        assert 'last_update' in response.data
        assert isinstance(response.data['widgets'], list)

    def test_api_personalizar_dashboard(self):
        """PUT /api/v1/dashboard/personalizar/ guarda la configuración."""
        payload = {
            'configuracion': {
                'widgets': [
                    {'type': 'total_calls', 'position': {'x': 0, 'y': 0}},
                    {'type': 'avg_duration', 'position': {'x': 1, 'y': 0}},
                ]
            }
        }

        response = self.client.put('/api/v1/dashboard/personalizar/', payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['configuracion'] == payload['configuracion']

        config = DashboardConfiguracion.objects.get(usuario=self.user)
        assert config.configuracion == payload['configuracion']

    def test_api_personalizar_con_configuracion_invalida(self):
        """PUT /api/v1/dashboard/personalizar/ con configuración inválida retorna 400."""
        payload = {'configuracion': ['widget_invalido']}

        response = self.client.put('/api/v1/dashboard/personalizar/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'configuracion' in response.data

    def test_api_exportar_dashboard(self):
        """POST /api/v1/dashboard/exportar/ responde con metadatos de exportación."""
        payload = {'formato': 'pdf'}

        response = self.client.post('/api/v1/dashboard/exportar/', payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['formato'] == 'pdf'
        assert 'archivo' in response.data
        assert 'timestamp' in response.data

    def test_api_compartir_dashboard(self):
        """POST /api/v1/dashboard/compartir/ devuelve destinatario y tipo."""
        destino = User.objects.create_user(
            username='destino.user',
            password='TestP@ss123',
            email='destino@test.com',
        )

        response = self.client.post(
            '/api/v1/dashboard/compartir/',
            {'compartir_con_usuario_id': destino.id},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['tipo'] == 'usuario'
        assert response.data['compartido_con'] == destino.email

    def test_api_compartir_usuario_inexistente(self):
        """POST /api/v1/dashboard/compartir/ con usuario inválido retorna 400."""
        response = self.client.post(
            '/api/v1/dashboard/compartir/',
            {'compartir_con_usuario_id': 99999},
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Usuario receptor no encontrado' in response.data['error']

    def test_api_autenticacion_requerida(self):
        """GET /api/v1/dashboard/overview/ sin autenticación responde 401/403."""
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/v1/dashboard/overview/')

        assert response.status_code in {
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        }
