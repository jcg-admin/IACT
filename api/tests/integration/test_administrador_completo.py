"""
Test E2E: Flujo completo de administrador tecnico.

Flujo completo:
1. Admin crea 3 usuarios
2. Asigna diferentes grupos
3. Verifica permisos efectivos
4. Exporta usuarios
5. Audita todas las acciones

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 84)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.users.models_permisos_granular import (
    AuditoriaPermiso,
    UsuarioGrupo,
)
from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestAdministradorCompletoE2E:
    """Tests end-to-end para flujo completo de administrador."""

    @pytest.fixture
    def admin_user(self, db):
        """Usuario administrador con permisos completos."""
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Master',
            is_staff=True,
            is_superuser=True,
        )
        # Asignar grupo de administracion
        UserManagementService.asignar_grupo_a_usuario(
            usuario_id=admin.id,
            grupo_codigo='administracion_usuarios',
            asignado_por_id=admin.id,
        )
        return admin

    @pytest.fixture
    def api_client(self):
        """Cliente API."""
        return APIClient()

    def test_flujo_administrador_completo(self, admin_user, api_client):
        """
        Test del flujo completo de un administrador creando
        y gestionando multiples usuarios.
        """
        api_client.force_authenticate(user=admin_user)

        # 1. Crear 3 usuarios
        usuarios_data = [
            {
                'email': 'operador1@test.com',
                'first_name': 'Operador',
                'last_name': 'Uno',
                'password': 'password123',
            },
            {
                'email': 'supervisor1@test.com',
                'first_name': 'Supervisor',
                'last_name': 'Uno',
                'password': 'password123',
            },
            {
                'email': 'analista1@test.com',
                'first_name': 'Analista',
                'last_name': 'Uno',
                'password': 'password123',
            },
        ]

        usuarios_creados = []
        for user_data in usuarios_data:
            response = api_client.post('/api/v1/usuarios/', user_data)
            assert response.status_code == status.HTTP_201_CREATED
            usuarios_creados.append(response.data)

        assert len(usuarios_creados) == 3

        # 2. Asignar diferentes grupos a cada usuario
        grupos_asignacion = [
            ('operador1@test.com', ['visualizacion_basica']),
            ('supervisor1@test.com', ['visualizacion_basica', 'gestion_operaciones']),
            ('analista1@test.com', ['visualizacion_basica', 'reportes_analitica']),
        ]

        for email, grupos in grupos_asignacion:
            usuario = next(u for u in usuarios_creados if u['email'] == email)
            response = api_client.post(
                f'/api/v1/usuarios/{usuario["id"]}/asignar_grupos/',
                {
                    'grupos_codigos': grupos,
                }
            )
            assert response.status_code == status.HTTP_200_OK

        # 3. Verificar permisos efectivos de cada usuario
        # Operador (solo visualizacion_basica)
        operador = User.objects.get(email='operador1@test.com')
        assert UserManagementService.usuario_tiene_permiso(
            usuario_id=operador.id,
            capacidad_codigo='sistema.vistas.dashboards.ver',
        ) is True
        assert UserManagementService.usuario_tiene_permiso(
            usuario_id=operador.id,
            capacidad_codigo='sistema.administracion.usuarios.crear',
        ) is False

        # Supervisor (visualizacion + gestion)
        supervisor = User.objects.get(email='supervisor1@test.com')
        assert UserManagementService.usuario_tiene_permiso(
            usuario_id=supervisor.id,
            capacidad_codigo='sistema.vistas.dashboards.ver',
        ) is True
        # Verificar que tiene permisos de gestion_operaciones si existen

        # Analista (visualizacion + reportes)
        analista = User.objects.get(email='analista1@test.com')
        assert UserManagementService.usuario_tiene_permiso(
            usuario_id=analista.id,
            capacidad_codigo='sistema.vistas.dashboards.ver',
        ) is True

        # 4. Listar usuarios con filtros (simula exportacion)
        response = api_client.get('/api/v1/usuarios/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] >= 3

        # Filtrar por activo
        response = api_client.get('/api/v1/usuarios/', {'activo': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert all(u['is_active'] for u in response.data['resultados'])

        # Filtrar por email
        response = api_client.get(
            '/api/v1/usuarios/',
            {'email_contains': 'operador'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['resultados']) >= 1

        # 5. Auditar todas las acciones realizadas
        # Verificar que se registraron las creaciones
        auditorias_creacion = AuditoriaPermiso.objects.filter(
            usuario=admin_user,
            capacidad_codigo='sistema.administracion.usuarios.crear',
            accion='crear',
            resultado='permitido',
        )
        assert auditorias_creacion.count() == 3

        # Verificar que se registraron las asignaciones de grupos
        auditorias_asignacion = AuditoriaPermiso.objects.filter(
            usuario=admin_user,
            capacidad_codigo='sistema.administracion.usuarios.asignar_grupos',
            accion='asignar_grupos',
            resultado='permitido',
        )
        assert auditorias_asignacion.count() == 3

        # Verificar que se registraron los listados
        auditorias_ver = AuditoriaPermiso.objects.filter(
            usuario=admin_user,
            capacidad_codigo='sistema.administracion.usuarios.ver',
            accion='listar',
            resultado='permitido',
        )
        assert auditorias_ver.count() >= 1

    def test_admin_puede_modificar_multiples_usuarios(self, admin_user, api_client):
        """Admin puede modificar varios usuarios en secuencia."""
        api_client.force_authenticate(user=admin_user)

        # Crear usuarios
        usuarios = []
        for i in range(5):
            response = api_client.post('/api/v1/usuarios/', {
                'email': f'user{i}@test.com',
                'first_name': 'User',
                'last_name': f'Number{i}',
                'password': 'password123',
            })
            usuarios.append(response.data['id'])

        # Modificar todos
        for usuario_id in usuarios:
            response = api_client.patch(
                f'/api/v1/usuarios/{usuario_id}/',
                {
                    'is_staff': True,
                }
            )
            assert response.status_code == status.HTTP_200_OK

        # Verificar que todos fueron modificados
        for usuario_id in usuarios:
            usuario = User.objects.get(id=usuario_id)
            assert usuario.is_staff is True

    def test_admin_puede_suspender_y_reactivar_batch(self, admin_user, api_client):
        """Admin puede suspender y reactivar multiples usuarios."""
        api_client.force_authenticate(user=admin_user)

        # Crear usuarios
        usuarios = []
        for i in range(3):
            response = api_client.post('/api/v1/usuarios/', {
                'email': f'batch{i}@test.com',
                'first_name': 'Batch',
                'last_name': f'User{i}',
                'password': 'password123',
            })
            usuarios.append(response.data['id'])

        # Suspender todos
        for usuario_id in usuarios:
            response = api_client.post(
                f'/api/v1/usuarios/{usuario_id}/suspender/',
                {
                    'motivo': 'Suspension masiva de prueba',
                }
            )
            assert response.status_code == status.HTTP_200_OK

        # Verificar que todos estan suspendidos
        for usuario_id in usuarios:
            usuario = User.objects.get(id=usuario_id)
            assert usuario.is_active is False

        # Reactivar todos
        for usuario_id in usuarios:
            response = api_client.post(
                f'/api/v1/usuarios/{usuario_id}/reactivar/'
            )
            assert response.status_code == status.HTTP_200_OK

        # Verificar que todos estan activos
        for usuario_id in usuarios:
            usuario = User.objects.get(id=usuario_id)
            assert usuario.is_active is True

    def test_auditoria_completa_de_flujo(self, admin_user, api_client):
        """Verificar que toda la actividad del admin se audita correctamente."""
        api_client.force_authenticate(user=admin_user)

        # Limpiar auditoria previa
        AuditoriaPermiso.objects.filter(usuario=admin_user).delete()

        # Realizar varias acciones
        # 1. Crear usuario
        response = api_client.post('/api/v1/usuarios/', {
            'email': 'auditoria@test.com',
            'first_name': 'Auditoria',
            'last_name': 'Test',
            'password': 'password123',
        })
        usuario_id = response.data['id']

        # 2. Asignar grupos
        api_client.post(
            f'/api/v1/usuarios/{usuario_id}/asignar_grupos/',
            {
                'grupos_codigos': ['visualizacion_basica'],
            }
        )

        # 3. Modificar usuario
        api_client.patch(
            f'/api/v1/usuarios/{usuario_id}/',
            {
                'first_name': 'Auditoria Modificada',
            }
        )

        # 4. Suspender usuario
        api_client.post(
            f'/api/v1/usuarios/{usuario_id}/suspender/',
            {
                'motivo': 'Test de auditoria',
            }
        )

        # 5. Reactivar usuario
        api_client.post(f'/api/v1/usuarios/{usuario_id}/reactivar/')

        # 6. Eliminar usuario
        api_client.delete(f'/api/v1/usuarios/{usuario_id}/')

        # Verificar que todas las acciones fueron auditadas
        auditorias = AuditoriaPermiso.objects.filter(
            usuario=admin_user,
            resultado='permitido',
        ).order_by('timestamp')

        # Debe haber al menos 6 registros (una por cada accion)
        assert auditorias.count() >= 6

        # Verificar que cada tipo de accion esta presente
        acciones_esperadas = ['crear', 'asignar_grupos', 'editar', 'suspender', 'reactivar', 'eliminar']
        acciones_auditadas = set(auditorias.values_list('accion', flat=True))

        for accion in acciones_esperadas:
            assert accion in acciones_auditadas, f"Falta auditoria de accion: {accion}"
