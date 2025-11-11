"""
Test E2E: Creacion de usuario + asignacion de grupos.

Flujo completo:
1. Admin crea usuario
2. Asigna grupos
3. Usuario puede acceder a dashboards
4. Usuario NO puede crear otros usuarios

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 80)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.users.models_permisos_granular import (
    GrupoPermiso,
    UsuarioGrupo,
)
from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)
from callcentersite.apps.users.services_usuarios import UsuarioService

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestUsuarioCompletoE2E:
    """Tests end-to-end para flujo completo de usuario."""

    @pytest.fixture
    def admin_user(self, db):
        """Usuario administrador con todos los permisos."""
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            is_staff=True,
        )
        # Asignar grupo administracion_usuarios
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=admin.id,
            grupo_codigo='administracion_usuarios',
            asignado_por_id=admin.id,
        )
        return admin

    @pytest.fixture
    def api_client(self):
        """Cliente API para requests."""
        return APIClient()

    def test_flujo_completo_creacion_usuario(self, admin_user, api_client):
        """
        Test del flujo completo:
        1. Admin crea usuario
        2. Asigna grupo visualizacion_basica
        3. Usuario puede ver dashboards
        4. Usuario NO puede crear otros usuarios
        """
        # Autenticar como admin
        api_client.force_authenticate(user=admin_user)

        # 1. Admin crea usuario
        response = api_client.post('/api/v1/usuarios/', {
            'email': 'nuevo@test.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password': 'password123',
            'is_staff': False,
        })

        assert response.status_code == status.HTTP_201_CREATED
        nuevo_usuario_id = response.data['id']
        assert response.data['email'] == 'nuevo@test.com'

        # 2. Asignar grupo visualizacion_basica
        response = api_client.post(
            f'/api/v1/usuarios/{nuevo_usuario_id}/asignar_grupos/',
            {
                'grupos_codigos': ['visualizacion_basica'],
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Verificar que el grupo fue asignado
        usuario_grupo = UsuarioGrupo.objects.filter(
            usuario_id=nuevo_usuario_id,
            grupo__codigo='visualizacion_basica',
            activo=True,
        ).first()
        assert usuario_grupo is not None

        # 3. Cambiar a nuevo usuario y verificar que puede ver dashboards
        nuevo_usuario = User.objects.get(id=nuevo_usuario_id)
        api_client.force_authenticate(user=nuevo_usuario)

        response = api_client.get('/api/v1/dashboard/overview/')
        assert response.status_code == status.HTTP_200_OK
        assert 'widgets' in response.data

        # 4. Verificar que NO puede crear otros usuarios
        response = api_client.post('/api/v1/usuarios/', {
            'email': 'otro@test.com',
            'first_name': 'Otro',
            'last_name': 'Usuario',
            'password': 'password123',
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data

    def test_usuario_sin_grupos_no_tiene_acceso(self, admin_user, api_client):
        """Usuario sin grupos no puede acceder a ningun endpoint."""
        # Crear usuario sin grupos
        usuario = User.objects.create_user(
            email='sin_grupos@test.com',
            password='password123',
            first_name='Sin',
            last_name='Grupos',
        )

        api_client.force_authenticate(user=usuario)

        # Intentar ver dashboards
        response = api_client.get('/api/v1/dashboard/overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Intentar listar usuarios
        response = api_client.get('/api/v1/usuarios/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cambio_de_grupos_cambia_permisos(self, admin_user, api_client):
        """Cambiar grupos de un usuario cambia sus permisos efectivos."""
        # Crear usuario con grupo visualizacion_basica
        usuario = UsuarioService.crear_usuario(
            usuario_solicitante_id=admin_user.id,
            datos={
                'email': 'cambio@test.com',
                'first_name': 'Cambio',
                'last_name': 'Grupos',
                'password': 'password123',
            }
        )

        UsuarioService.asignar_grupos_usuario(
            usuario_solicitante_id=admin_user.id,
            usuario_id=usuario.id,
            grupos_codigos=['visualizacion_basica'],
        )

        # Verificar que puede ver dashboards
        api_client.force_authenticate(user=usuario)
        response = api_client.get('/api/v1/dashboard/overview/')
        assert response.status_code == status.HTTP_200_OK

        # Cambiar a grupo administracion_usuarios (como admin)
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            f'/api/v1/usuarios/{usuario.id}/asignar_grupos/',
            {
                'grupos_codigos': ['administracion_usuarios'],
            }
        )
        assert response.status_code == status.HTTP_200_OK

        # Ahora puede crear usuarios
        api_client.force_authenticate(user=usuario)
        response = api_client.post('/api/v1/usuarios/', {
            'email': 'creado_por_cambio@test.com',
            'first_name': 'Creado',
            'last_name': 'PorCambio',
            'password': 'password123',
        })
        assert response.status_code == status.HTTP_201_CREATED
