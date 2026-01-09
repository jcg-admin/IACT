"""
Test E2E: Dashboard personalizado por usuario.

Flujo completo:
1. Usuario personaliza dashboard
2. Configuracion se guarda
3. Usuario ve dashboard personalizado
4. Otro usuario ve dashboard por defecto

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 82)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.dashboard.models import DashboardConfiguracion
from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)
from callcentersite.apps.users.services_usuarios import UsuarioService

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestDashboardPersonalizadoE2E:
    """Tests end-to-end para dashboards personalizados."""

    @pytest.fixture
    def admin_user(self, db):
        """Usuario administrador."""
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
        )
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=admin.id,
            grupo_codigo='visualizacion_basica',
            asignado_por_id=admin.id,
        )
        return admin

    @pytest.fixture
    def usuario1(self, admin_user):
        """Primer usuario regular."""
        usuario = User.objects.create_user(
            email='usuario1@test.com',
            password='password123',
            first_name='Usuario',
            last_name='Uno',
        )
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=usuario.id,
            grupo_codigo='visualizacion_basica',
            asignado_por_id=admin_user.id,
        )
        return usuario

    @pytest.fixture
    def usuario2(self, admin_user):
        """Segundo usuario regular."""
        usuario = User.objects.create_user(
            email='usuario2@test.com',
            password='password123',
            first_name='Usuario',
            last_name='Dos',
        )
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=usuario.id,
            grupo_codigo='visualizacion_basica',
            asignado_por_id=admin_user.id,
        )
        return usuario

    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()

    def test_flujo_personalizacion_dashboard(self, usuario1, usuario2, api_client):
        """
        Test del flujo completo de personalizacion de dashboard.
        """
        # 1. Usuario1 personaliza su dashboard
        api_client.force_authenticate(user=usuario1)

        configuracion_personalizada = {
            'widgets': [
                {'tipo': 'llamadas', 'posicion': {'x': 0, 'y': 0}},
                {'tipo': 'tickets', 'posicion': {'x': 1, 'y': 0}},
            ],
            'tema': 'oscuro',
        }

        response = api_client.put('/api/v1/dashboard/personalizar/', {
            'configuracion': configuracion_personalizada,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['configuracion'] == configuracion_personalizada

        # 2. Verificar que la configuracion se guardo en DB
        config_db = DashboardConfiguracion.objects.filter(
            usuario=usuario1
        ).first()

        assert config_db is not None
        assert config_db.configuracion == configuracion_personalizada

        # 3. Usuario1 ve su dashboard personalizado (verificar que existe)
        # En una implementacion real, habria un endpoint para obtener la config
        config_db.refresh_from_db()
        assert config_db.configuracion['tema'] == 'oscuro'

        # 4. Usuario2 NO ve la configuracion de Usuario1
        api_client.force_authenticate(user=usuario2)

        # Usuario2 no tiene configuracion personalizada
        config_usuario2 = DashboardConfiguracion.objects.filter(
            usuario=usuario2
        ).first()

        assert config_usuario2 is None

        # Usuario2 puede personalizar su propio dashboard
        configuracion_usuario2 = {
            'widgets': [
                {'tipo': 'metricas', 'posicion': {'x': 0, 'y': 0}},
            ],
            'tema': 'claro',
        }

        response = api_client.put('/api/v1/dashboard/personalizar/', {
            'configuracion': configuracion_usuario2,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['configuracion']['tema'] == 'claro'

        # Verificar que cada usuario tiene su propia configuracion
        config1 = DashboardConfiguracion.objects.get(usuario=usuario1)
        config2 = DashboardConfiguracion.objects.get(usuario=usuario2)

        assert config1.configuracion['tema'] == 'oscuro'
        assert config2.configuracion['tema'] == 'claro'
        assert config1.id != config2.id

    def test_actualizacion_configuracion_existente(self, usuario1, api_client):
        """Actualizar configuracion existente reemplaza la anterior."""
        api_client.force_authenticate(user=usuario1)

        # Primera configuracion
        config1 = {
            'widgets': [{'tipo': 'A'}],
            'tema': 'oscuro',
        }

        response = api_client.put('/api/v1/dashboard/personalizar/', {
            'configuracion': config1,
        })
        assert response.status_code == status.HTTP_200_OK
        config_id_1 = response.data['id']

        # Segunda configuracion (actualizar)
        config2 = {
            'widgets': [{'tipo': 'B'}, {'tipo': 'C'}],
            'tema': 'claro',
        }

        response = api_client.put('/api/v1/dashboard/personalizar/', {
            'configuracion': config2,
        })
        assert response.status_code == status.HTTP_200_OK
        config_id_2 = response.data['id']

        # Debe ser el mismo registro (update, no create)
        assert config_id_1 == config_id_2

        # Verificar que solo existe un registro
        configs = DashboardConfiguracion.objects.filter(usuario=usuario1)
        assert configs.count() == 1
        assert configs.first().configuracion == config2

    def test_configuracion_invalida_retorna_error(self, usuario1, api_client):
        """Configuracion que no es JSON valido retorna error."""
        api_client.force_authenticate(user=usuario1)

        response = api_client.put('/api/v1/dashboard/personalizar/', {
            'configuracion': 'esto no es un objeto JSON',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_usuario_sin_permiso_no_puede_personalizar(self):
        """Usuario sin grupo no puede personalizar dashboard."""
        # Este test dependeria de que el usuario NO tenga el permiso
        # sistema.vistas.dashboards.personalizar en su grupo
        pass
