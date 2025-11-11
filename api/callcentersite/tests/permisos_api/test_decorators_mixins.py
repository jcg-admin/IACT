"""
Tests para decoradores, middleware y mixins de permisos granulares.

Cobertura:
- Decoradores: @require_permission, @require_any_permission, @require_all_permissions
- Middleware: PermissionAuditMiddleware
- Mixins: GranularPermissionMixin
- Permission Classes: GranularPermission

Ejecutar:
    pytest api/callcentersite/tests/permisos_api/test_decorators_mixins.py -v
"""

import pytest
from django.test import RequestFactory
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from callcentersite.apps.users.decorators_permisos import (
    require_permission,
    require_any_permission,
    require_all_permissions,
)
from callcentersite.apps.users.mixins_permisos import (
    GranularPermission,
    GranularPermissionMixin,
)
from callcentersite.apps.users.middleware_permisos import (
    PermissionAuditMiddleware,
)
from callcentersite.apps.users.models_permisos_granular import (
    Capacidad,
    GrupoPermiso,
    UsuarioGrupo,
)

User = get_user_model()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def request_factory():
    """Factory para crear requests de Django."""
    return RequestFactory()


@pytest.fixture
def api_request_factory():
    """Factory para crear requests de DRF."""
    return APIRequestFactory()


@pytest.fixture
def user_with_permissions(db, admin_user):
    """
    Usuario con capacidades específicas para testing.

    Capacidades:
    - sistema.vistas.dashboards.ver
    - sistema.vistas.reportes.ver
    - sistema.vistas.reportes.editar
    """
    # Crear capacidades
    cap_dashboard = Capacidad.objects.create(
        codigo='sistema.vistas.dashboards.ver',
        nombre='Ver Dashboards',
        descripcion='Permite ver dashboards del sistema',
        activa=True,
    )
    cap_reportes_ver = Capacidad.objects.create(
        codigo='sistema.vistas.reportes.ver',
        nombre='Ver Reportes',
        descripcion='Permite ver reportes',
        activa=True,
    )
    cap_reportes_editar = Capacidad.objects.create(
        codigo='sistema.vistas.reportes.editar',
        nombre='Editar Reportes',
        descripcion='Permite editar reportes',
        activa=True,
    )

    # Crear grupo con estas capacidades
    grupo = GrupoPermiso.objects.create(
        codigo='test_grupo',
        nombre='Grupo de Test',
        descripcion='Grupo para testing',
        activo=True,
    )
    grupo.capacidades.add(cap_dashboard, cap_reportes_ver, cap_reportes_editar)

    # Crear usuario y asignarlo al grupo
    user = User.objects.create_user(
        username='test_user_perms',
        email='test@example.com',
        password='test123',
    )

    UsuarioGrupo.objects.create(
        usuario=user,
        grupo=grupo,
        asignado_por=admin_user,
        activo=True,
    )

    return user


@pytest.fixture
def user_without_permissions(db):
    """Usuario sin ninguna capacidad."""
    return User.objects.create_user(
        username='test_user_no_perms',
        email='test_no_perms@example.com',
        password='test123',
    )


# =============================================================================
# TESTS: DECORADOR @require_permission
# =============================================================================

@pytest.mark.django_db
class TestRequirePermissionDecorator:
    """Tests para el decorador @require_permission."""

    def test_usuario_con_permiso_accede_exitosamente(
        self, request_factory, user_with_permissions
    ):
        """Usuario con permiso debe poder acceder a la vista."""

        @require_permission('sistema.vistas.dashboards.ver')
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        request = request_factory.get('/dashboard/')
        request.user = user_with_permissions

        response = dashboard_view(request)

        assert response.status_code == 200
        assert response.content == b"Dashboard content"

    def test_usuario_sin_permiso_es_denegado_con_exception(
        self, request_factory, user_without_permissions
    ):
        """Usuario sin permiso debe recibir PermissionDenied."""

        @require_permission('sistema.vistas.dashboards.ver')
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        request = request_factory.get('/dashboard/')
        request.user = user_without_permissions

        with pytest.raises(PermissionDenied) as excinfo:
            dashboard_view(request)

        assert 'sistema.vistas.dashboards.ver' in str(excinfo.value)

    def test_usuario_sin_permiso_retorna_json_si_raise_exception_false(
        self, request_factory, user_without_permissions
    ):
        """Con raise_exception=False, debe retornar JSON en vez de exception."""

        @require_permission('sistema.vistas.dashboards.ver', raise_exception=False)
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        request = request_factory.get('/dashboard/')
        request.user = user_without_permissions

        response = dashboard_view(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == 403
        data = response.json()
        assert data['error'] == 'Permiso denegado'
        assert data['required_permission'] == 'sistema.vistas.dashboards.ver'

    def test_usuario_no_autenticado_es_denegado(self, request_factory):
        """Usuario no autenticado debe ser denegado."""

        @require_permission('sistema.vistas.dashboards.ver')
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        # Request sin usuario
        request = request_factory.get('/dashboard/')
        request.user = None

        with pytest.raises(PermissionDenied) as excinfo:
            dashboard_view(request)

        assert 'no autenticado' in str(excinfo.value).lower()

    def test_auditoria_es_registrada(
        self, request_factory, user_with_permissions, django_assert_num_queries
    ):
        """La verificación debe ser auditada."""

        @require_permission('sistema.vistas.dashboards.ver', audit=True)
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        request = request_factory.get('/dashboard/')
        request.user = user_with_permissions

        # Debe hacer:
        # - 1 query para verificar permiso (SQL function)
        # - 1 query para auditar (SQL function)
        with django_assert_num_queries(2):
            response = dashboard_view(request)

        assert response.status_code == 200

    def test_sin_auditoria_si_audit_false(
        self, request_factory, user_with_permissions, django_assert_num_queries
    ):
        """Con audit=False no debe auditar."""

        @require_permission('sistema.vistas.dashboards.ver', audit=False)
        def dashboard_view(request):
            return HttpResponse("Dashboard content")

        request = request_factory.get('/dashboard/')
        request.user = user_with_permissions

        # Solo 1 query para verificar permiso
        with django_assert_num_queries(1):
            response = dashboard_view(request)

        assert response.status_code == 200


# =============================================================================
# TESTS: DECORADOR @require_any_permission
# =============================================================================

@pytest.mark.django_db
class TestRequireAnyPermissionDecorator:
    """Tests para el decorador @require_any_permission."""

    def test_usuario_con_una_de_varias_capacidades_accede(
        self, request_factory, user_with_permissions
    ):
        """Usuario con al menos una capacidad debe poder acceder."""

        @require_any_permission([
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.usuarios.ver',  # No tiene esta
        ])
        def analytics_view(request):
            return HttpResponse("Analytics content")

        request = request_factory.get('/analytics/')
        request.user = user_with_permissions

        response = analytics_view(request)

        assert response.status_code == 200

    def test_usuario_sin_ninguna_capacidad_es_denegado(
        self, request_factory, user_without_permissions
    ):
        """Usuario sin ninguna capacidad debe ser denegado."""

        @require_any_permission([
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.reportes.ver',
        ])
        def analytics_view(request):
            return HttpResponse("Analytics content")

        request = request_factory.get('/analytics/')
        request.user = user_without_permissions

        with pytest.raises(PermissionDenied):
            analytics_view(request)

    def test_retorna_json_con_raise_exception_false(
        self, request_factory, user_without_permissions
    ):
        """Con raise_exception=False debe retornar JSON."""

        @require_any_permission(
            ['sistema.vistas.dashboards.ver', 'sistema.vistas.reportes.ver'],
            raise_exception=False
        )
        def analytics_view(request):
            return HttpResponse("Analytics content")

        request = request_factory.get('/analytics/')
        request.user = user_without_permissions

        response = analytics_view(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == 403
        data = response.json()
        assert 'required_permissions_any' in data


# =============================================================================
# TESTS: DECORADOR @require_all_permissions
# =============================================================================

@pytest.mark.django_db
class TestRequireAllPermissionsDecorator:
    """Tests para el decorador @require_all_permissions."""

    def test_usuario_con_todas_las_capacidades_accede(
        self, request_factory, user_with_permissions
    ):
        """Usuario con todas las capacidades debe acceder."""

        @require_all_permissions([
            'sistema.vistas.reportes.ver',
            'sistema.vistas.reportes.editar',
        ])
        def edit_report_view(request):
            return HttpResponse("Edit report")

        request = request_factory.get('/reports/edit/')
        request.user = user_with_permissions

        response = edit_report_view(request)

        assert response.status_code == 200

    def test_usuario_sin_todas_las_capacidades_es_denegado(
        self, request_factory, user_with_permissions
    ):
        """Usuario que le falta alguna capacidad debe ser denegado."""

        @require_all_permissions([
            'sistema.vistas.reportes.ver',  # Tiene esta
            'sistema.vistas.reportes.eliminar',  # NO tiene esta
        ])
        def delete_report_view(request):
            return HttpResponse("Delete report")

        request = request_factory.get('/reports/delete/')
        request.user = user_with_permissions

        with pytest.raises(PermissionDenied):
            delete_report_view(request)

    def test_json_response_incluye_capacidades_faltantes(
        self, request_factory, user_with_permissions
    ):
        """JSON response debe listar las capacidades que faltan."""

        @require_all_permissions(
            [
                'sistema.vistas.reportes.ver',  # Tiene
                'sistema.vistas.reportes.eliminar',  # NO tiene
                'sistema.vistas.admin.ver',  # NO tiene
            ],
            raise_exception=False
        )
        def admin_view(request):
            return HttpResponse("Admin")

        request = request_factory.get('/admin/')
        request.user = user_with_permissions

        response = admin_view(request)

        assert response.status_code == 403
        data = response.json()
        assert 'missing_permissions' in data
        assert 'sistema.vistas.reportes.eliminar' in data['missing_permissions']
        assert 'sistema.vistas.admin.ver' in data['missing_permissions']


# =============================================================================
# TESTS: GRANULAR PERMISSION CLASS (DRF)
# =============================================================================

@pytest.mark.django_db
class TestGranularPermissionClass:
    """Tests para GranularPermission class de DRF."""

    def test_viewset_con_permiso_simple_permite_acceso(
        self, api_request_factory, user_with_permissions
    ):
        """ViewSet con permission_map simple debe verificar correctamente."""

        class TestViewSet(viewsets.ViewSet):
            permission_classes = [GranularPermission]
            permission_map = {
                'list': 'sistema.vistas.dashboards.ver',
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200
        assert response.data == {'data': 'OK'}

    def test_viewset_sin_permiso_deniega_acceso(
        self, api_request_factory, user_without_permissions
    ):
        """ViewSet debe denegar acceso si el usuario no tiene permiso."""

        class TestViewSet(viewsets.ViewSet):
            permission_classes = [GranularPermission]
            permission_map = {
                'list': 'sistema.vistas.dashboards.ver',
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_without_permissions)

        response = view(request)

        assert response.status_code == 403

    def test_permission_map_con_lista_verifica_any(
        self, api_request_factory, user_with_permissions
    ):
        """Lista en permission_map debe verificar ANY (al menos una)."""

        class TestViewSet(viewsets.ViewSet):
            permission_classes = [GranularPermission]
            permission_map = {
                'list': [
                    'sistema.vistas.dashboards.ver',  # Tiene
                    'sistema.vistas.usuarios.ver',  # NO tiene
                ],
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200

    def test_permission_map_con_dict_all_verifica_todas(
        self, api_request_factory, user_with_permissions
    ):
        """Dict con 'all' debe verificar que tenga TODAS las capacidades."""

        class TestViewSet(viewsets.ViewSet):
            permission_classes = [GranularPermission]
            permission_map = {
                'list': {
                    'all': [
                        'sistema.vistas.reportes.ver',  # Tiene
                        'sistema.vistas.reportes.editar',  # Tiene
                    ]
                },
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200

    def test_permission_map_dict_all_deniega_si_falta_alguna(
        self, api_request_factory, user_with_permissions
    ):
        """Dict con 'all' debe denegar si falta alguna capacidad."""

        class TestViewSet(viewsets.ViewSet):
            permission_classes = [GranularPermission]
            permission_map = {
                'list': {
                    'all': [
                        'sistema.vistas.reportes.ver',  # Tiene
                        'sistema.vistas.admin.ver',  # NO tiene
                    ]
                },
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 403


# =============================================================================
# TESTS: GRANULAR PERMISSION MIXIN
# =============================================================================

@pytest.mark.django_db
class TestGranularPermissionMixin:
    """Tests para GranularPermissionMixin."""

    def test_mixin_configura_permission_class_automaticamente(
        self, api_request_factory, user_with_permissions
    ):
        """El mixin debe configurar GranularPermission automáticamente."""

        class TestViewSet(GranularPermissionMixin, viewsets.ViewSet):
            permission_map = {
                'list': 'sistema.vistas.dashboards.ver',
            }

            def list(self, request):
                return Response({'data': 'OK'})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200

    def test_check_permission_method_verifica_correctamente(
        self, api_request_factory, user_with_permissions
    ):
        """El método check_permission() debe funcionar correctamente."""

        class TestViewSet(GranularPermissionMixin, viewsets.ViewSet):
            permission_map = {'list': 'sistema.vistas.dashboards.ver'}

            def list(self, request):
                # Verificar permiso adicional dentro del método
                if self.check_permission('sistema.vistas.reportes.ver'):
                    return Response({'can_see_reports': True})
                return Response({'can_see_reports': False})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200
        assert response.data['can_see_reports'] is True

    def test_get_user_capacidades_retorna_lista_completa(
        self, api_request_factory, user_with_permissions
    ):
        """El método get_user_capacidades() debe retornar todas las capacidades."""

        class TestViewSet(GranularPermissionMixin, viewsets.ViewSet):
            permission_map = {'list': 'sistema.vistas.dashboards.ver'}

            def list(self, request):
                capacidades = self.get_user_capacidades()
                return Response({'capacidades': capacidades})

        view = TestViewSet.as_view({'get': 'list'})
        request = api_request_factory.get('/test/')
        force_authenticate(request, user=user_with_permissions)

        response = view(request)

        assert response.status_code == 200
        capacidades = response.data['capacidades']
        assert 'sistema.vistas.dashboards.ver' in capacidades
        assert 'sistema.vistas.reportes.ver' in capacidades
        assert 'sistema.vistas.reportes.editar' in capacidades


# =============================================================================
# TESTS: MIDDLEWARE
# =============================================================================

@pytest.mark.django_db
class TestPermissionAuditMiddleware:
    """Tests para PermissionAuditMiddleware."""

    def test_middleware_marca_timestamp_en_process_request(
        self, request_factory, user_with_permissions
    ):
        """El middleware debe marcar timestamp en process_request."""

        def get_response(request):
            return HttpResponse("OK")

        middleware = PermissionAuditMiddleware(get_response)
        request = request_factory.get('/test/')
        request.user = user_with_permissions

        middleware.process_request(request)

        assert hasattr(request, '_permission_audit_start_time')
        assert isinstance(request._permission_audit_start_time, float)

    def test_middleware_audita_requests_con_permission_checked(
        self, request_factory, user_with_permissions
    ):
        """El middleware debe auditar requests marcados con _permission_checked."""

        def get_response(request):
            # Marcar que se verificó permiso
            request._permission_checked = True
            request._permission_required = 'sistema.vistas.test.ver'
            return HttpResponse("OK")

        middleware = PermissionAuditMiddleware(get_response)
        request = request_factory.get('/test/')
        request.user = user_with_permissions

        response = middleware(request)

        assert response.status_code == 200
        # La auditoría debe haberse ejecutado (verificar en logs o DB)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.django_db
class TestIntegrationDecoratorConMiddleware:
    """Tests de integración entre decoradores y middleware."""

    def test_decorador_marca_request_para_middleware(
        self, request_factory, user_with_permissions
    ):
        """El decorador debe marcar el request para que el middleware lo audite."""

        @require_permission('sistema.vistas.dashboards.ver')
        def dashboard_view(request):
            return HttpResponse("Dashboard")

        request = request_factory.get('/dashboard/')
        request.user = user_with_permissions

        response = dashboard_view(request)

        # El decorador debe haber marcado el request
        assert hasattr(request, '_permission_checked')
        assert request._permission_checked is True
        assert hasattr(request, '_permission_required')
        assert request._permission_required == 'sistema.vistas.dashboards.ver'
