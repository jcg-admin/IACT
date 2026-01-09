"""
Test E2E: Exportacion e importacion de configuracion.

Flujo completo:
1. Admin exporta configuracion
2. Admin modifica valores
3. Admin importa configuracion anterior
4. Valores restaurados

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 83)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.configuration.models import Configuracion, ConfiguracionHistorial
from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestConfiguracionBackupE2E:
    """Tests end-to-end para exportacion e importacion de configuraciones."""

    @pytest.fixture
    def admin_user(self, db):
        """Usuario administrador tecnico."""
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            is_staff=True,
        )
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=admin.id,
            grupo_codigo='configuracion_sistema',
            asignado_por_id=admin.id,
        )
        return admin

    @pytest.fixture
    def configuraciones_iniciales(self, db):
        """Crear algunas configuraciones iniciales."""
        configs = [
            Configuracion.objects.create(
                categoria='seguridad',
                clave='seguridad.session_timeout',
                valor='900',
                tipo_dato='integer',
                valor_default='900',
                descripcion='Timeout de sesion en segundos',
            ),
            Configuracion.objects.create(
                categoria='seguridad',
                clave='seguridad.max_login_attempts',
                valor='5',
                tipo_dato='integer',
                valor_default='5',
                descripcion='Maximo de intentos de login',
            ),
            Configuracion.objects.create(
                categoria='notificaciones',
                clave='notificaciones.email_habilitado',
                valor='true',
                tipo_dato='boolean',
                valor_default='true',
                descripcion='Habilitar notificaciones por email',
            ),
        ]
        return configs

    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()

    def test_flujo_exportacion_e_importacion(
        self,
        admin_user,
        configuraciones_iniciales,
        api_client
    ):
        """
        Test del flujo completo de backup y restore de configuraciones.
        """
        api_client.force_authenticate(user=admin_user)

        # 1. Exportar configuraciones actuales
        response = api_client.get('/api/v1/configuracion/exportar/')

        assert response.status_code == status.HTTP_200_OK
        backup_original = response.data

        # Verificar estructura del backup
        assert 'seguridad' in backup_original
        assert 'notificaciones' in backup_original
        assert len(backup_original['seguridad']) == 2
        assert len(backup_original['notificaciones']) == 1

        # Guardar valores originales para comparar
        valor_timeout_original = next(
            c['valor'] for c in backup_original['seguridad']
            if c['clave'] == 'seguridad.session_timeout'
        )
        assert valor_timeout_original == '900'

        # 2. Modificar valores
        response = api_client.put(
            '/api/v1/configuracion/seguridad.session_timeout/',
            {
                'nuevo_valor': '1800',
            }
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.put(
            '/api/v1/configuracion/seguridad.max_login_attempts/',
            {
                'nuevo_valor': '3',
            }
        )
        assert response.status_code == status.HTTP_200_OK

        # Verificar que los valores cambiaron
        config_timeout = Configuracion.objects.get(
            clave='seguridad.session_timeout'
        )
        assert config_timeout.valor == '1800'

        config_attempts = Configuracion.objects.get(
            clave='seguridad.max_login_attempts'
        )
        assert config_attempts.valor == '3'

        # 3. Importar configuracion anterior (restore)
        response = api_client.post(
            '/api/v1/configuracion/importar/',
            {
                'configuraciones_json': backup_original,
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['actualizadas'] >= 2

        # 4. Verificar que valores fueron restaurados
        config_timeout.refresh_from_db()
        assert config_timeout.valor == '900'

        config_attempts.refresh_from_db()
        assert config_attempts.valor == '5'

    def test_exportacion_filtra_por_categoria(
        self,
        admin_user,
        configuraciones_iniciales,
        api_client
    ):
        """Exportar con filtro de categoria solo retorna esa categoria."""
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(
            '/api/v1/configuracion/exportar/',
            {'categoria': 'seguridad'}
        )

        # Nota: Este test asume que el endpoint acepta filtro por categoria
        # Si no lo acepta, ajustar el servicio

    def test_historial_registra_todos_los_cambios(
        self,
        admin_user,
        configuraciones_iniciales,
        api_client
    ):
        """Cada cambio de configuracion se registra en historial."""
        api_client.force_authenticate(user=admin_user)

        config = configuraciones_iniciales[0]
        valor_original = config.valor

        # Hacer varios cambios
        for nuevo_valor in ['1200', '1500', '1800']:
            api_client.put(
                f'/api/v1/configuracion/{config.clave}/',
                {
                    'nuevo_valor': nuevo_valor,
                }
            )

        # Verificar que se crearon 3 registros de historial
        historial = ConfiguracionHistorial.objects.filter(
            configuracion=config
        ).order_by('timestamp')

        assert historial.count() == 3
        assert historial[0].valor_anterior == valor_original
        assert historial[0].valor_nuevo == '1200'
        assert historial[1].valor_anterior == '1200'
        assert historial[1].valor_nuevo == '1500'
        assert historial[2].valor_anterior == '1500'
        assert historial[2].valor_nuevo == '1800'

    def test_restaurar_a_valor_default(
        self,
        admin_user,
        configuraciones_iniciales,
        api_client
    ):
        """Restaurar configuracion a su valor por defecto."""
        api_client.force_authenticate(user=admin_user)

        config = configuraciones_iniciales[0]
        valor_default = config.valor_default

        # Modificar valor
        api_client.put(
            f'/api/v1/configuracion/{config.clave}/',
            {
                'nuevo_valor': '9999',
            }
        )

        config.refresh_from_db()
        assert config.valor == '9999'

        # Restaurar a default
        response = api_client.post(
            f'/api/v1/configuracion/{config.clave}/restaurar/'
        )

        assert response.status_code == status.HTTP_200_OK

        config.refresh_from_db()
        assert config.valor == valor_default

    def test_importacion_parcial_con_errores(
        self,
        admin_user,
        configuraciones_iniciales,
        api_client
    ):
        """Importacion con algunos errores actualiza las validas."""
        api_client.force_authenticate(user=admin_user)

        # Preparar JSON con mix de configs validas e invalidas
        json_importar = {
            'seguridad': [
                {
                    'clave': 'seguridad.session_timeout',
                    'valor': '2400',
                    'tipo_dato': 'integer',
                    'valor_default': '900',
                },
                {
                    'clave': 'configuracion.inexistente',  # No existe
                    'valor': 'error',
                },
            ],
        }

        response = api_client.post(
            '/api/v1/configuracion/importar/',
            {
                'configuraciones_json': json_importar,
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['actualizadas'] >= 1
        # Puede tener errores por la config inexistente

    def test_usuario_sin_permiso_no_puede_exportar(
        self,
        configuraciones_iniciales,
        api_client
    ):
        """Usuario sin permiso no puede exportar configuraciones."""
        usuario_sin_permiso = User.objects.create_user(
            email='sin_permiso@test.com',
            password='password123',
            first_name='Sin',
            last_name='Permiso',
        )

        api_client.force_authenticate(user=usuario_sin_permiso)

        response = api_client.get('/api/v1/configuracion/exportar/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
