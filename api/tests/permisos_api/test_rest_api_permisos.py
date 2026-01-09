"""
Tests TDD para API REST del sistema de permisos granular.

Cobertura:
- Funciones API (CRUD)
- Capacidades API (CRUD)
- Grupos de Permisos API (CRUD)
- Permisos Excepcionales API (grant/revoke)
- Auditoría API (readonly)
- Verificación API (custom endpoints)

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from callcentersite.apps.users.models_permisos_granular import (
    Funcion,
    Capacidad,
    GrupoPermiso,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)

User = get_user_model()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def api_client():
    """Cliente API REST."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Usuario administrador para tests."""
    return User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='test1234',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def regular_user(db):
    """Usuario regular para tests."""
    return User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='test1234',
    )


@pytest.fixture
def funcion_sample(db):
    """Función de ejemplo."""
    return Funcion.objects.create(
        nombre='dashboards',
        nombre_completo='sistema.vistas.dashboards',
        dominio='vistas',
        categoria='visualizacion',
        descripcion='Dashboards del sistema',
        activa=True,
    )


@pytest.fixture
def capacidad_sample(db):
    """Capacidad de ejemplo."""
    return Capacidad.objects.create(
        codigo='sistema.vistas.dashboards.ver',
        nombre='Ver Dashboards',
        descripcion='Permite ver dashboards',
        nivel_riesgo='bajo',
        activa=True,
    )


@pytest.fixture
def grupo_sample(db, capacidad_sample):
    """Grupo de permisos de ejemplo."""
    grupo = GrupoPermiso.objects.create(
        codigo='operadores',
        nombre='Operadores',
        descripcion='Grupo de operadores',
        categoria='operativo',
        nivel_riesgo='bajo',
        activo=True,
    )
    GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad_sample)
    return grupo


# =============================================================================
# TESTS: FUNCION API
# =============================================================================

@pytest.mark.django_db
class TestFuncionAPI:
    """Tests para endpoints de Funciones."""

    def test_list_funciones(self, api_client, admin_user, funcion_sample):
        """Test: GET /api/permisos/funciones/ - Lista funciones."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/funciones/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['nombre'] == 'dashboards'

    def test_list_funciones_con_filtro_activa(self, api_client, admin_user, funcion_sample):
        """Test: GET /api/permisos/funciones/?activa=true - Filtrar por activa."""
        # Crear función inactiva
        Funcion.objects.create(
            nombre='inactiva',
            nombre_completo='sistema.test.inactiva',
            dominio='test',
            categoria='test',
            activa=False,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/funciones/?activa=true')

        assert response.status_code == status.HTTP_200_OK
        assert all(f['activa'] is True for f in response.data)

    def test_create_funcion(self, api_client, admin_user):
        """Test: POST /api/permisos/funciones/ - Crear función."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'nombre': 'usuarios',
            'nombre_completo': 'sistema.administracion.usuarios',
            'dominio': 'administracion',
            'categoria': 'gestion',
            'descripcion': 'Gestión de usuarios',
            'activa': True,
        }

        response = api_client.post('/api/permisos/funciones/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nombre'] == 'usuarios'
        assert Funcion.objects.filter(nombre_completo='sistema.administracion.usuarios').exists()

    def test_create_funcion_nombre_duplicado(self, api_client, admin_user, funcion_sample):
        """Test: POST /api/permisos/funciones/ - Error nombre duplicado."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'nombre': 'dashboards',
            'nombre_completo': 'sistema.vistas.dashboards',  # Ya existe
            'dominio': 'vistas',
            'categoria': 'visualizacion',
            'activa': True,
        }

        response = api_client.post('/api/permisos/funciones/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_funcion(self, api_client, admin_user, funcion_sample):
        """Test: GET /api/permisos/funciones/:id/ - Obtener detalle."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/funciones/{funcion_sample.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'dashboards'
        assert 'capacidades' in response.data

    def test_update_funcion(self, api_client, admin_user, funcion_sample):
        """Test: PUT /api/permisos/funciones/:id/ - Actualizar función."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'nombre': 'dashboards_v2',
            'nombre_completo': 'sistema.vistas.dashboards',
            'dominio': 'vistas',
            'categoria': 'visualizacion_avanzada',
            'activa': True,
        }

        response = api_client.put(f'/api/permisos/funciones/{funcion_sample.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'dashboards_v2'

        funcion_sample.refresh_from_db()
        assert funcion_sample.nombre == 'dashboards_v2'

    def test_delete_funcion(self, api_client, admin_user, funcion_sample):
        """Test: DELETE /api/permisos/funciones/:id/ - Desactivar función."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f'/api/permisos/funciones/{funcion_sample.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        funcion_sample.refresh_from_db()
        assert funcion_sample.activa is False


# =============================================================================
# TESTS: CAPACIDAD API
# =============================================================================

@pytest.mark.django_db
class TestCapacidadAPI:
    """Tests para endpoints de Capacidades."""

    def test_list_capacidades(self, api_client, admin_user, capacidad_sample):
        """Test: GET /api/permisos/capacidades/ - Lista capacidades."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/capacidades/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['codigo'] == 'sistema.vistas.dashboards.ver'

    def test_list_capacidades_con_filtro_nivel_riesgo(self, api_client, admin_user):
        """Test: GET /api/permisos/capacidades/?nivel_riesgo=critico - Filtrar."""
        # Crear capacidad crítica
        Capacidad.objects.create(
            codigo='sistema.admin.delete_all',
            nombre='Eliminar Todo',
            nivel_riesgo='critico',
            activa=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/capacidades/?nivel_riesgo=critico')

        assert response.status_code == status.HTTP_200_OK
        assert all(c['nivel_riesgo'] == 'critico' for c in response.data)

    def test_create_capacidad(self, api_client, admin_user):
        """Test: POST /api/permisos/capacidades/ - Crear capacidad."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'sistema.administracion.usuarios.crear',
            'nombre': 'Crear Usuarios',
            'descripcion': 'Permite crear usuarios',
            'nivel_riesgo': 'medio',
            'requiere_aprobacion': True,
            'activa': True,
        }

        response = api_client.post('/api/permisos/capacidades/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'sistema.administracion.usuarios.crear'
        assert Capacidad.objects.filter(codigo='sistema.administracion.usuarios.crear').exists()

    def test_create_capacidad_codigo_duplicado(self, api_client, admin_user, capacidad_sample):
        """Test: POST /api/permisos/capacidades/ - Error código duplicado."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'sistema.vistas.dashboards.ver',  # Ya existe
            'nombre': 'Ver Dashboards Duplicado',
            'nivel_riesgo': 'bajo',
            'activa': True,
        }

        response = api_client.post('/api/permisos/capacidades/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_capacidad(self, api_client, admin_user, capacidad_sample):
        """Test: GET /api/permisos/capacidades/:id/ - Obtener detalle."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/capacidades/{capacidad_sample.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'sistema.vistas.dashboards.ver'
        assert 'funciones' in response.data

    def test_update_capacidad(self, api_client, admin_user, capacidad_sample):
        """Test: PUT /api/permisos/capacidades/:id/ - Actualizar capacidad."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'sistema.vistas.dashboards.ver',
            'nombre': 'Ver Dashboards Mejorado',
            'descripcion': 'Descripción actualizada',
            'nivel_riesgo': 'medio',
            'requiere_aprobacion': True,
            'activa': True,
        }

        response = api_client.put(f'/api/permisos/capacidades/{capacidad_sample.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['nivel_riesgo'] == 'medio'

        capacidad_sample.refresh_from_db()
        assert capacidad_sample.nivel_riesgo == 'medio'

    def test_delete_capacidad(self, api_client, admin_user, capacidad_sample):
        """Test: DELETE /api/permisos/capacidades/:id/ - Desactivar capacidad."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f'/api/permisos/capacidades/{capacidad_sample.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        capacidad_sample.refresh_from_db()
        assert capacidad_sample.activa is False


# =============================================================================
# TESTS: GRUPO PERMISO API
# =============================================================================

@pytest.mark.django_db
class TestGrupoPermisoAPI:
    """Tests para endpoints de Grupos de Permisos."""

    def test_list_grupos(self, api_client, admin_user, grupo_sample):
        """Test: GET /api/permisos/grupos/ - Lista grupos."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/grupos/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['codigo'] == 'operadores'

    def test_create_grupo(self, api_client, admin_user, capacidad_sample):
        """Test: POST /api/permisos/grupos/ - Crear grupo."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'supervisores',
            'nombre': 'Supervisores',
            'descripcion': 'Grupo de supervisores',
            'categoria': 'gestion',
            'nivel_riesgo': 'medio',
            'activo': True,
            'capacidades_codigos': [capacidad_sample.codigo],
        }

        response = api_client.post('/api/permisos/grupos/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'supervisores'

        grupo = GrupoPermiso.objects.get(codigo='supervisores')
        assert grupo.capacidades.count() == 1

    def test_create_grupo_codigo_duplicado(self, api_client, admin_user, grupo_sample):
        """Test: POST /api/permisos/grupos/ - Error código duplicado."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'operadores',  # Ya existe
            'nombre': 'Operadores Duplicado',
            'categoria': 'operativo',
            'nivel_riesgo': 'bajo',
            'activo': True,
        }

        response = api_client.post('/api/permisos/grupos/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_grupo(self, api_client, admin_user, grupo_sample):
        """Test: GET /api/permisos/grupos/:id/ - Obtener detalle."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/grupos/{grupo_sample.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'operadores'
        assert 'capacidades' in response.data
        assert len(response.data['capacidades']) == 1

    def test_update_grupo_capacidades(self, api_client, admin_user, grupo_sample):
        """Test: PUT /api/permisos/grupos/:id/ - Actualizar capacidades."""
        # Crear nueva capacidad
        nueva_cap = Capacidad.objects.create(
            codigo='sistema.vistas.metricas.ver',
            nombre='Ver Métricas',
            nivel_riesgo='bajo',
            activa=True,
        )

        api_client.force_authenticate(user=admin_user)

        data = {
            'codigo': 'operadores',
            'nombre': 'Operadores Actualizado',
            'categoria': 'operativo',
            'nivel_riesgo': 'bajo',
            'activo': True,
            'capacidades_codigos': [nueva_cap.codigo],
        }

        response = api_client.put(f'/api/permisos/grupos/{grupo_sample.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK

        grupo_sample.refresh_from_db()
        assert grupo_sample.capacidades.count() == 1
        assert grupo_sample.capacidades.first().codigo == nueva_cap.codigo

    def test_delete_grupo(self, api_client, admin_user, grupo_sample):
        """Test: DELETE /api/permisos/grupos/:id/ - Desactivar grupo."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f'/api/permisos/grupos/{grupo_sample.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        grupo_sample.refresh_from_db()
        assert grupo_sample.activo is False


# =============================================================================
# TESTS: PERMISO EXCEPCIONAL API
# =============================================================================

@pytest.mark.django_db
class TestPermisoExcepcionalAPI:
    """Tests para endpoints de Permisos Excepcionales."""

    def test_list_permisos_excepcionales(self, api_client, admin_user, regular_user, capacidad_sample):
        """Test: GET /api/permisos/excepcionales/ - Lista permisos."""
        # Crear permiso excepcional
        PermisoExcepcional.objects.create(
            usuario=regular_user,
            capacidad=capacidad_sample,
            tipo='temporal',
            otorgado_por=admin_user,
            motivo='Test permiso',
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/excepcionales/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_permiso_excepcional(self, api_client, admin_user, regular_user, capacidad_sample):
        """Test: POST /api/permisos/excepcionales/ - Otorgar permiso."""
        api_client.force_authenticate(user=admin_user)

        data = {
            'usuario_id': regular_user.id,
            'capacidad_codigo': capacidad_sample.codigo,
            'tipo': 'temporal',
            'fecha_expiracion': '2025-12-31T23:59:59Z',
            'motivo': 'Permiso temporal de prueba',
        }

        response = api_client.post('/api/permisos/excepcionales/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert PermisoExcepcional.objects.filter(usuario=regular_user).exists()

    def test_delete_permiso_excepcional(self, api_client, admin_user, regular_user, capacidad_sample):
        """Test: DELETE /api/permisos/excepcionales/:id/ - Revocar permiso."""
        permiso = PermisoExcepcional.objects.create(
            usuario=regular_user,
            capacidad=capacidad_sample,
            tipo='temporal',
            otorgado_por=admin_user,
            motivo='Test permiso',
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f'/api/permisos/excepcionales/{permiso.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        permiso.refresh_from_db()
        assert permiso.activo is False


# =============================================================================
# TESTS: AUDITORIA API
# =============================================================================

@pytest.mark.django_db
class TestAuditoriaAPI:
    """Tests para endpoints de Auditoría."""

    def test_list_auditoria(self, api_client, admin_user, capacidad_sample):
        """Test: GET /api/permisos/auditoria/ - Lista logs."""
        # Crear log de auditoría
        AuditoriaPermiso.objects.create(
            usuario=admin_user,
            capacidad_codigo=capacidad_sample.codigo,
            accion='acceso_permitido',
            resultado='exito',
            ip_address='127.0.0.1',
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/auditoria/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_auditoria_con_filtros(self, api_client, admin_user, capacidad_sample):
        """Test: GET /api/permisos/auditoria/?usuario_id=X - Filtrar logs."""
        AuditoriaPermiso.objects.create(
            usuario=admin_user,
            capacidad_codigo=capacidad_sample.codigo,
            accion='acceso_denegado',
            resultado='fallo',
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/auditoria/?usuario_id={admin_user.id}')

        assert response.status_code == status.HTTP_200_OK
        assert all(log['usuario_email'] == admin_user.email for log in response.data)


# =============================================================================
# TESTS: VERIFICACION API
# =============================================================================

@pytest.mark.django_db
class TestVerificacionAPI:
    """Tests para endpoints de verificación de permisos."""

    def test_obtener_capacidades_usuario(self, api_client, admin_user, regular_user, grupo_sample):
        """Test: GET /api/permisos/verificar/:id/capacidades/ - Obtener capacidades."""
        # Asignar grupo al usuario
        UsuarioGrupo.objects.create(
            usuario=regular_user,
            grupo=grupo_sample,
            asignado_por=admin_user,
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/verificar/{regular_user.id}/capacidades/')

        assert response.status_code == status.HTTP_200_OK
        assert 'capacidades' in response.data
        assert len(response.data['capacidades']) >= 1

    def test_verificar_tiene_permiso(self, api_client, admin_user, regular_user, grupo_sample, capacidad_sample):
        """Test: GET /api/permisos/verificar/:id/tiene-permiso/?capacidad=X"""
        # Asignar grupo al usuario
        UsuarioGrupo.objects.create(
            usuario=regular_user,
            grupo=grupo_sample,
            asignado_por=admin_user,
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            f'/api/permisos/verificar/{regular_user.id}/tiene-permiso/?capacidad={capacidad_sample.codigo}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'tiene_permiso' in response.data
        assert response.data['tiene_permiso'] is True

    def test_obtener_menu_usuario(self, api_client, admin_user, regular_user, grupo_sample):
        """Test: GET /api/permisos/verificar/:id/menu/ - Obtener menú dinámico."""
        # Asignar grupo al usuario
        UsuarioGrupo.objects.create(
            usuario=regular_user,
            grupo=grupo_sample,
            asignado_por=admin_user,
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/verificar/{regular_user.id}/menu/')

        assert response.status_code == status.HTTP_200_OK
        assert 'menu' in response.data

    def test_obtener_grupos_usuario(self, api_client, admin_user, regular_user, grupo_sample):
        """Test: GET /api/permisos/verificar/:id/grupos/ - Obtener grupos."""
        # Asignar grupo al usuario
        UsuarioGrupo.objects.create(
            usuario=regular_user,
            grupo=grupo_sample,
            asignado_por=admin_user,
            activo=True,
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/verificar/{regular_user.id}/grupos/')

        assert response.status_code == status.HTTP_200_OK
        assert 'grupos' in response.data
        assert len(response.data['grupos']) >= 1

    def test_verificar_tiene_permiso_sin_capacidad_param(self, api_client, admin_user, regular_user):
        """Test: GET /api/permisos/verificar/:id/tiene-permiso/ - Error sin query param."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/permisos/verificar/{regular_user.id}/tiene-permiso/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_verificar_usuario_no_existe(self, api_client, admin_user):
        """Test: GET /api/permisos/verificar/99999/capacidades/ - Usuario no existe."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/permisos/verificar/99999/capacidades/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# TESTS: AUTHENTICATION
# =============================================================================

@pytest.mark.django_db
class TestAuthentication:
    """Tests de autenticación en endpoints."""

    def test_endpoint_requiere_autenticacion(self, api_client):
        """Test: Endpoints requieren autenticación."""
        response = api_client.get('/api/permisos/funciones/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_usuario_autenticado_puede_acceder(self, api_client, regular_user):
        """Test: Usuario autenticado puede acceder."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/permisos/funciones/')
        assert response.status_code == status.HTTP_200_OK
