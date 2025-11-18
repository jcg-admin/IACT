"""
Tests de integración para API REST de configuración.

Verifica que los endpoints HTTP funcionan correctamente.
"""

import json
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from callcentersite.apps.configuracion.models import ConfiguracionSistema
from callcentersite.apps.configuration.models import Configuracion

User = get_user_model()


@pytest.mark.django_db
class TestConfiguracionAPIREST:
    """Tests de integración para API REST /api/v1/configuracion/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        # Crear usuario autenticado
        self.user = User.objects.create_user(
            username='admin.test',
            password='AdminP@ss123',
            email='admin@test.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        # Crear configuraciones de prueba
        ConfiguracionSistema.objects.create(
            clave='max_intentos_login',
            valor='3',
            tipo='integer',
            descripcion='Máximo de intentos de login',
            valor_default='3'
        )
        ConfiguracionSistema.objects.create(
            clave='timeout_session',
            valor='30',
            tipo='integer',
            descripcion='Timeout de sesión en minutos',
            valor_default='30'
        )

    def test_api_listar_configuraciones(self):
        """
        API: GET /api/v1/configuracion/ - Listar todas las configuraciones.

        Given configuraciones existentes
        When GET a /api/v1/configuracion/
        Then retorna 200 OK
          And retorna lista de configuraciones
        """
        # Act
        response = self.client.get('/api/v1/configuracion/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 2

    def test_api_listar_configuraciones_ignora_modelo_legacy(self):
        """El endpoint debe usar ConfiguracionSistema y no el modelo legacy."""

        Configuracion.objects.create(
            categoria='general',
            clave='legacy_param',
            valor='1',
            tipo_dato='integer',
            valor_default='1',
            descripcion='Legacy config',
        )

        response = self.client.get('/api/v1/configuracion/')

        claves = {item['clave'] for item in response.data}

        assert {'max_intentos_login', 'timeout_session'} <= claves
        assert 'legacy_param' not in claves

    def test_api_ver_configuracion_especifica(self):
        """
        API: GET /api/v1/configuracion/{clave}/ - Ver configuración específica.

        Given configuración existente
        When GET a /api/v1/configuracion/{clave}/
        Then retorna 200 OK
          And retorna datos de la configuración
        """
        # Act
        response = self.client.get('/api/v1/configuracion/max_intentos_login/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['clave'] == 'max_intentos_login'
        assert response.data['valor'] == '3'
        assert response.data['tipo'] == 'integer'

    def test_api_modificar_configuracion(self):
        """
        API: PATCH /api/v1/configuracion/{clave}/modificar/ - Modificar configuración.

        Given configuración existente
        When PATCH con nuevo valor
        Then retorna 200 OK
          And configuración es actualizada
        """
        # Arrange
        datos = {
            'nuevo_valor': '60',
            'motivo': 'Aumentar tiempo de sesión'
        }

        # Act
        response = self.client.patch(
            '/api/v1/configuracion/timeout_session/modificar/',
            datos,
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'actualizada exitosamente' in response.data['message'].lower()

        # Verificar cambio
        config = ConfiguracionSistema.objects.get(clave='timeout_session')
        assert config.valor == '60'

    def test_api_modificar_con_valor_invalido(self):
        """
        API: PATCH /api/v1/configuracion/{clave}/modificar/ - Error con valor inválido.

        Given configuración tipo integer
        When PATCH con valor no numérico
        Then retorna 400 BAD REQUEST
        """
        # Arrange
        datos = {
            'nuevo_valor': 'not_a_number'
        }

        # Act
        response = self.client.patch(
            '/api/v1/configuracion/max_intentos_login/modificar/',
            datos,
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_api_exportar_configuracion(self):
        """
        API: POST /api/v1/configuracion/exportar/ - Exportar configuraciones.

        Given configuraciones existentes
        When POST a /exportar/
        Then retorna archivo JSON
        """
        # Act
        response = self.client.post('/api/v1/configuracion/exportar/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/json'
        assert 'configuracion.json' in response['Content-Disposition']

        # Verificar que es JSON válido
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_api_importar_configuracion(self):
        """
        API: POST /api/v1/configuracion/importar/ - Importar configuraciones.

        Given JSON válido con configuraciones
        When POST a /importar/
        Then retorna 200 OK
          And configuraciones son creadas/actualizadas
        """
        # Arrange
        json_data = json.dumps([
            {
                'clave': 'new_param',
                'valor': 'new_value',
                'tipo': 'string',
                'descripcion': 'Nuevo parámetro',
                'valor_default': 'default'
            }
        ])
        datos = {'json_data': json_data}

        # Act
        response = self.client.post('/api/v1/configuracion/importar/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'importadas exitosamente' in response.data['message'].lower()
        assert response.data['resultado']['creadas'] >= 1

        # Verificar que se creó
        assert ConfiguracionSistema.objects.filter(clave='new_param').exists()

    def test_api_ver_historial_configuracion(self):
        """
        API: GET /api/v1/configuracion/{clave}/historial/ - Ver historial.

        Given configuración con cambios
        When GET a /{clave}/historial/
        Then retorna 200 OK
          And retorna historial de cambios
        """
        # Arrange - Hacer un cambio primero
        self.client.patch(
            '/api/v1/configuracion/timeout_session/modificar/',
            {'nuevo_valor': '45'},
            format='json'
        )

        # Act
        response = self.client.get('/api/v1/configuracion/timeout_session/historial/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1

    def test_api_auditar_historial_completo(self):
        """
        API: GET /api/v1/configuracion/auditar/ - Ver historial completo.

        Given múltiples configuraciones con cambios
        When GET a /auditar/
        Then retorna 200 OK
          And retorna historial completo
        """
        # Arrange - Hacer cambios
        self.client.patch(
            '/api/v1/configuracion/timeout_session/modificar/',
            {'nuevo_valor': '45'},
            format='json'
        )
        self.client.patch(
            '/api/v1/configuracion/max_intentos_login/modificar/',
            {'nuevo_valor': '5'},
            format='json'
        )

        # Act
        response = self.client.get('/api/v1/configuracion/auditar/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 2

    def test_api_autenticacion_requerida(self):
        """
        API: Todos los endpoints requieren autenticación.

        Given usuario no autenticado
        When GET a /api/v1/configuracion/
        Then retorna 401 UNAUTHORIZED o 403 FORBIDDEN
        """
        # Arrange - Desautenticar
        self.client.force_authenticate(user=None)

        # Act
        response = self.client.get('/api/v1/configuracion/')

        # Assert
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ]
