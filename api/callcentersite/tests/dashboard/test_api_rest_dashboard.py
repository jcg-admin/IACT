"""
Tests de integración para API REST de dashboards.

Verifica que los endpoints HTTP funcionan correctamente.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestDashboardAPIREST:
    """Tests de integración para API REST /api/v1/dashboard/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        # Crear usuario autenticado
        self.user = User.objects.create_user(
            username='test.user',
            password='TestP@ss123',
            email='test@test.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_api_ver_dashboard_personal(self):
        """
        API: GET /api/v1/dashboard/ - Ver dashboard personal.

        Given usuario autenticado
        When GET a /api/v1/dashboard/
        Then retorna 200 OK
          And retorna widgets por defecto
        """
        # Act
        response = self.client.get('/api/v1/dashboard/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'widgets' in response.data
        assert 'last_update' in response.data
        assert isinstance(response.data['widgets'], list)

    def test_api_personalizar_dashboard(self):
        """
        API: POST /api/v1/dashboard/personalizar/ - Personalizar widgets.

        Given usuario autenticado
        When POST con lista de widgets
        Then retorna 200 OK
          And dashboard es personalizado
        """
        # Arrange
        datos = {
            'widgets': ['total_calls', 'avg_duration']
        }

        # Act
        response = self.client.post('/api/v1/dashboard/personalizar/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'Dashboard personalizado exitosamente' in response.data['message']

        # Verificar que se aplicó
        dashboard = self.client.get('/api/v1/dashboard/')
        widget_types = [w['type'] for w in dashboard.data['widgets']]
        assert 'total_calls' in widget_types
        assert 'avg_duration' in widget_types

    def test_api_personalizar_con_widget_invalido(self):
        """
        API: POST /api/v1/dashboard/personalizar/ - Error con widget inválido.

        Given usuario autenticado
        When POST con widget inexistente
        Then retorna 400 BAD REQUEST
        """
        # Arrange
        datos = {
            'widgets': ['widget_inexistente']
        }

        # Act
        response = self.client.post('/api/v1/dashboard/personalizar/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_api_exportar_dashboard_csv(self):
        """
        API: POST /api/v1/dashboard/exportar/ - Exportar a CSV.

        Given usuario autenticado
        When POST a /exportar/ con formato CSV
        Then retorna archivo CSV
        """
        # Arrange
        datos = {
            'formato': 'csv'
        }

        # Act
        response = self.client.post('/api/v1/dashboard/exportar/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'dashboard.csv' in response['Content-Disposition']

    def test_api_exportar_dashboard_pdf(self):
        """
        API: POST /api/v1/dashboard/exportar/ - Exportar a PDF.

        Given usuario autenticado
        When POST a /exportar/ con formato PDF
        Then retorna archivo PDF
        """
        # Arrange
        datos = {
            'formato': 'pdf'
        }

        # Act
        response = self.client.post('/api/v1/dashboard/exportar/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert 'dashboard.pdf' in response['Content-Disposition']

    def test_api_compartir_dashboard(self):
        """
        API: POST /api/v1/dashboard/compartir/ - Compartir configuración.

        Given usuario autenticado con configuración
        When POST a /compartir/ con usuario destino
        Then retorna 200 OK
          And configuración es copiada
        """
        # Arrange
        usuario_destino = User.objects.create_user(
            username='destino.user',
            password='TestP@ss123',
            email='destino@test.com'
        )

        # Personalizar dashboard origen
        self.client.post('/api/v1/dashboard/personalizar/', {
            'widgets': ['total_calls']
        }, format='json')

        # Act - Compartir
        response = self.client.post('/api/v1/dashboard/compartir/', {
            'usuario_destino_id': usuario_destino.id
        }, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'compartido exitosamente' in response.data['message'].lower()

    def test_api_compartir_a_usuario_inexistente(self):
        """
        API: POST /api/v1/dashboard/compartir/ - Error con usuario inexistente.

        Given usuario autenticado
        When POST a /compartir/ con ID inexistente
        Then retorna 404 NOT FOUND
        """
        # Act
        response = self.client.post('/api/v1/dashboard/compartir/', {
            'usuario_destino_id': 99999
        }, format='json')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_api_autenticacion_requerida(self):
        """
        API: Todos los endpoints requieren autenticación.

        Given usuario no autenticado
        When GET a /api/v1/dashboard/
        Then retorna 401 UNAUTHORIZED o 403 FORBIDDEN
        """
        # Arrange - Desautenticar
        self.client.force_authenticate(user=None)

        # Act
        response = self.client.get('/api/v1/dashboard/')

        # Assert
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ]
