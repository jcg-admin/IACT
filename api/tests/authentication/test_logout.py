"""
Tests TDD para RF-007: Logout Manual y Cierre de Sesión

Casos de prueba (11 tests):
- TEST-007-001 a TEST-007-011

Documentación: docs/implementacion/backend/requisitos/funcionales/rf007_logout_manual.md
"""

import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient

try:
    from callcentersite.apps.authentication.services import AuthenticationService
    from callcentersite.apps.users.models import User, UserSession
    from callcentersite.apps.audit.models import AuditLog
    from rest_framework_simplejwt.tokens import RefreshToken
except ImportError:
    AuthenticationService = None
    User = None
    UserSession = None
    AuditLog = None
    RefreshToken = None


@pytest.mark.django_db
class TestRF007LogoutManual:
    """Tests para RF-007: Logout Manual"""

    def setup_method(self):
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_007_001_logout_exitoso_con_sesion_activa(self):
        """TEST-007-001: Logout exitoso blacklistea refresh token y cierra sesión"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(user=user, session_key='abc123', is_active=True)
        refresh = RefreshToken.for_user(user)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, str(refresh), request)

        session.refresh_from_db()
        assert session.is_active is False
        assert session.logout_reason == 'MANUAL'
        assert AuditLog.objects.filter(event_type='LOGOUT_SUCCESS', user_id=user.id).exists()

    def test_007_002_logout_blacklistea_refresh_token(self):
        """TEST-007-002: Logout agrega refresh token a blacklist"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        refresh = RefreshToken.for_user(user)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, str(refresh), request)

        # Intentar reutilizar debe fallar
        with pytest.raises(Exception):
            RefreshToken(str(refresh))

    def test_007_003_logout_cierra_sesion_en_user_sessions(self):
        """TEST-007-003: Logout marca is_active=False en user_sessions"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(user=user, session_key='abc', is_active=True)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, None, request)

        session.refresh_from_db()
        assert session.is_active is False

    def test_007_004_logout_elimina_django_session(self):
        """TEST-007-004: Logout elimina registro de django_session"""
        # TODO: Implementar cuando esté disponible django_session
        pytest.skip("Implementar con django_session")

    def test_007_005_logout_audita_evento_logout_success(self):
        """TEST-007-005: Logout audita evento LOGOUT_SUCCESS"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, None, request)

        assert AuditLog.objects.filter(event_type='LOGOUT_SUCCESS', user_id=user.id).exists()

    def test_007_006_logout_idempotente_token_ya_blacklisted(self):
        """TEST-007-006: Logout es idempotente si token ya está blacklisted"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        refresh = RefreshToken.for_user(user)
        request = self.factory.post('/api/v1/auth/logout')

        # Primer logout
        AuthenticationService.logout(user, str(refresh), request)
        # Segundo logout (debe ser idempotente)
        AuthenticationService.logout(user, str(refresh), request)

        # No debe fallar

    def test_007_007_logout_sin_refresh_token(self):
        """TEST-007-007: Logout funciona sin proporcionar refresh_token"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='abc', is_active=True)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, None, request)

        assert UserSession.objects.filter(user=user, is_active=False).exists()

    def test_007_008_logout_cierra_multiples_sesiones_activas(self):
        """TEST-007-008: Logout cierra todas las sesiones activas del usuario"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='abc', is_active=True)
        UserSession.objects.create(user=user, session_key='xyz', is_active=True)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, None, request)

        assert UserSession.objects.filter(user=user, is_active=True).count() == 0

    def test_007_009_logout_sin_autenticacion_rechazado(self):
        """TEST-007-009: Logout sin autenticación retorna 401"""
        # TODO: Implementar con view real
        pytest.skip("Implementar con view real")

    def test_007_010_access_token_sigue_valido_despues_logout(self):
        """TEST-007-010: Access token sigue válido después de logout (stateless)"""
        # Nota: Por diseño JWT stateless, access token sigue válido hasta expirar
        pytest.skip("Test conceptual - access token es stateless")

    def test_007_011_no_puede_refrescar_token_despues_logout(self):
        """TEST-007-011: No puede refrescar token después de logout"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        tokens = AuthenticationService.generate_jwt_tokens(user)
        request = self.factory.post('/api/v1/auth/logout')

        AuthenticationService.logout(user, tokens['refresh'], request)

        # Intentar refrescar debe fallar
        with pytest.raises(Exception):
            AuthenticationService.refresh_access_token(tokens['refresh'])
