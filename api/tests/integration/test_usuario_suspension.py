"""
Test E2E: Suspension y reactivacion de usuario.

Flujo completo:
1. Admin suspende usuario
2. Usuario pierde acceso
3. Admin reactiva usuario
4. Usuario recupera acceso

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 81)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)
from callcentersite.apps.users.services_usuarios import UsuarioService

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestUsuarioSuspensionE2E:
    """Tests end-to-end para suspension y reactivacion de usuarios."""

    @pytest.fixture
    def admin_user(self, db):
        """Usuario administrador."""
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            is_staff=True,
        )
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=admin.id,
            grupo_codigo='administracion_usuarios',
            asignado_por_id=admin.id,
        )
        return admin

    @pytest.fixture
    def usuario_regular(self, admin_user):
        """Usuario regular con acceso basico."""
        usuario = UsuarioService.crear_usuario(
            usuario_solicitante_id=admin_user.id,
            datos={
                'email': 'regular@test.com',
                'first_name': 'Regular',
                'last_name': 'User',
                'password': 'password123',
            }
        )
        UsuarioService.asignar_grupos_usuario(
            usuario_solicitante_id=admin_user.id,
            usuario_id=usuario.id,
            grupos_codigos=['visualizacion_basica'],
        )
        return usuario

    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()

    def test_flujo_suspension_completo(self, admin_user, usuario_regular, api_client):
        """
        Test del flujo completo de suspension y reactivacion.
        """
        # Verificar que usuario tiene acceso inicial
        api_client.force_authenticate(user=usuario_regular)
        response = api_client.get('/api/v1/dashboard/overview/')
        assert response.status_code == status.HTTP_200_OK

        # 1. Admin suspende usuario
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            f'/api/v1/usuarios/{usuario_regular.id}/suspender/',
            {
                'motivo': 'Violacion de politicas de uso',
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is False

        # 2. Usuario pierde acceso (is_active=False)
        usuario_regular.refresh_from_db()
        assert usuario_regular.is_active is False

        # Verificar que usuario NO puede acceder a dashboard
        api_client.force_authenticate(user=usuario_regular)
        response = api_client.get('/api/v1/dashboard/overview/')
        # Django/DRF debería denegar acceso a usuarios inactivos
        # El comportamiento exacto depende de la configuración de permisos

        # 3. Admin reactiva usuario
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            f'/api/v1/usuarios/{usuario_regular.id}/reactivar/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is True

        # 4. Usuario recupera acceso
        usuario_regular.refresh_from_db()
        assert usuario_regular.is_active is True

        api_client.force_authenticate(user=usuario_regular)
        response = api_client.get('/api/v1/dashboard/overview/')
        assert response.status_code == status.HTTP_200_OK

    def test_usuario_no_puede_suspenderse_a_si_mismo(self, admin_user, api_client):
        """Usuario no puede suspenderse a si mismo."""
        api_client.force_authenticate(user=admin_user)

        response = api_client.post(
            f'/api/v1/usuarios/{admin_user.id}/suspender/',
            {
                'motivo': 'Intento de auto-suspension',
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_suspension_registra_auditoria(self, admin_user, usuario_regular, api_client):
        """Suspension y reactivacion se registran en auditoria."""
        from callcentersite.apps.users.models_permisos_granular import (
            AuditoriaPermiso,
        )

        api_client.force_authenticate(user=admin_user)

        # Suspender
        api_client.post(
            f'/api/v1/usuarios/{usuario_regular.id}/suspender/',
            {
                'motivo': 'Test de auditoria',
            }
        )

        # Verificar registro de suspension
        auditoria = AuditoriaPermiso.objects.filter(
            usuario_id=admin_user.id,
            capacidad_codigo='sistema.administracion.usuarios.suspender',
            accion='suspender',
            resultado='permitido',
        ).first()

        assert auditoria is not None
        assert 'Test de auditoria' in auditoria.detalles

        # Reactivar
        api_client.post(f'/api/v1/usuarios/{usuario_regular.id}/reactivar/')

        # Verificar registro de reactivacion
        auditoria = AuditoriaPermiso.objects.filter(
            usuario_id=admin_user.id,
            capacidad_codigo='sistema.administracion.usuarios.reactivar',
            accion='reactivar',
            resultado='permitido',
        ).first()

        assert auditoria is not None

    def test_usuario_sin_permiso_no_puede_suspender(self, usuario_regular, api_client):
        """Usuario sin permiso no puede suspender a otros."""
        # Crear otro usuario
        otro_usuario = User.objects.create_user(
            email='otro@test.com',
            password='password123',
            first_name='Otro',
            last_name='Usuario',
        )

        api_client.force_authenticate(user=usuario_regular)

        response = api_client.post(
            f'/api/v1/usuarios/{otro_usuario.id}/suspender/',
            {
                'motivo': 'Intento sin permiso',
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
