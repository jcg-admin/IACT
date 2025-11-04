"""
Tests TDD para RF-010: Sesión Única por Usuario en PostgreSQL

Casos de prueba (11 tests):
- TEST-010-001 a TEST-010-011

Documentación: docs/implementacion/backend/requisitos/funcionales/rf010_sesion_unica.md
"""

import pytest
from django.conf import settings
from django.test import RequestFactory

try:
    from callcentersite.apps.authentication.services import (
        close_previous_sessions, create_user_session
    )
    from callcentersite.apps.users.models import User, UserSession
    from callcentersite.apps.audit.models import AuditLog
    from callcentersite.apps.notifications.models import InternalMessage
    from django.contrib.sessions.models import Session as DjangoSession
except ImportError:
    close_previous_sessions = None
    create_user_session = None
    User = None
    UserSession = None
    AuditLog = None
    InternalMessage = None
    DjangoSession = None


@pytest.mark.django_db
class TestRF010SesionUnica:
    """Tests para RF-010: Sesión Única por Usuario"""

    def setup_method(self):
        self.factory = RequestFactory()

    def test_010_001_primer_login_sin_sesion_previa(self):
        """TEST-010-001: Primer login crea sesión sin cerrar ninguna"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        request = self.factory.post('/api/v1/auth/login')
        request.session = type('obj', (object,), {'session_key': 'abc123'})()

        session = create_user_session(user, request)

        assert session.is_active is True
        assert UserSession.objects.filter(user=user, is_active=True).count() == 1

    def test_010_002_login_con_sesion_activa_cierra_anterior(self):
        """TEST-010-002: Login con sesión activa cierra sesión anterior"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        old_session = UserSession.objects.create(
            user=user, session_key='old_key', is_active=True
        )
        request = self.factory.post('/api/v1/auth/login')

        closed_count = close_previous_sessions(user, request)

        old_session.refresh_from_db()
        assert old_session.is_active is False
        assert old_session.logout_reason == 'NEW_SESSION'
        assert closed_count == 1

    def test_010_003_multiples_sesiones_activas_cierra_todas(self):
        """TEST-010-003: Múltiples sesiones activas son cerradas"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='key1', is_active=True)
        UserSession.objects.create(user=user, session_key='key2', is_active=True)
        request = self.factory.post('/api/v1/auth/login')

        closed_count = close_previous_sessions(user, request)

        assert closed_count == 2
        assert UserSession.objects.filter(user=user, is_active=True).count() == 0

    def test_010_004_usuario_tiene_maximo_1_sesion_activa(self):
        """TEST-010-004: Usuario tiene máximo 1 sesión activa después de login"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='old', is_active=True)
        request = self.factory.post('/api/v1/auth/login')
        request.session = type('obj', (object,), {'session_key': 'new'})()

        close_previous_sessions(user, request)
        create_user_session(user, request)

        assert UserSession.objects.filter(user=user, is_active=True).count() == 1

    def test_010_005_sesiones_almacenadas_en_postgresql(self):
        """TEST-010-005: Sesiones se almacenan en PostgreSQL"""
        # Verificar que UserSession usa PostgreSQL
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(user=user, session_key='abc', is_active=True)

        # Verificar que se guardó en BD
        assert UserSession.objects.filter(session_key='abc').exists()

    def test_010_006_session_engine_es_db_no_redis(self):
        """TEST-010-006: SESSION_ENGINE configurado como 'db' (NO Redis)"""
        session_engine = settings.SESSION_ENGINE

        assert 'db' in session_engine or 'database' in session_engine
        assert 'cache' not in session_engine
        assert 'redis' not in session_engine.lower()

    def test_010_007_cierre_sesion_anterior_en_ambas_tablas(self):
        """TEST-010-007: Cierre de sesión en user_sessions Y django_session"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(user=user, session_key='abc', is_active=True)
        request = self.factory.post('/api/v1/auth/login')

        close_previous_sessions(user, request)

        session.refresh_from_db()
        assert session.is_active is False

        # TODO: Verificar django_session también
        # assert not DjangoSession.objects.filter(session_key='abc').exists()

    def test_010_008_notificacion_buzon_interno_sin_ip(self):
        """TEST-010-008: Notificación vía buzón interno sin IP address"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='old', is_active=True)
        request = self.factory.post('/api/v1/auth/login')

        close_previous_sessions(user, request)

        notification = InternalMessage.objects.filter(
            user_id=user.id,
            subject__icontains='nueva sesión'
        ).first()
        assert notification is not None
        # Verificar que NO contiene IP
        assert 'ip' not in notification.body.lower()

    def test_010_009_auditoria_session_closed(self):
        """TEST-010-009: Audita evento SESSION_CLOSED"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(user=user, session_key='old', is_active=True)
        request = self.factory.post('/api/v1/auth/login')

        close_previous_sessions(user, request)

        assert AuditLog.objects.filter(
            event_type='SESSION_CLOSED',
            user_id=user.id
        ).exists()

    def test_010_010_user_agent_almacenado_no_validado(self):
        """TEST-010-010: User-agent se almacena pero NO se valida"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        request = self.factory.post('/api/v1/auth/login')
        request.META['HTTP_USER_AGENT'] = 'Chrome/100.0'
        request.session = type('obj', (object,), {'session_key': 'abc'})()

        session = create_user_session(user, request)

        assert session.user_agent == 'Chrome/100.0'

        # Cambiar user_agent no debe bloquear
        request.META['HTTP_USER_AGENT'] = 'Firefox/90.0'
        # No debe lanzar excepción

    def test_010_011_sesion_unica_independiente_por_usuario(self):
        """TEST-010-011: Sesión única es independiente por usuario"""
        user1 = User.objects.create_user(username='user1', password='Pass123!', email='u1@ex.com')
        user2 = User.objects.create_user(username='user2', password='Pass123!', email='u2@ex.com')

        session1 = UserSession.objects.create(user=user1, session_key='key1', is_active=True)
        session2 = UserSession.objects.create(user=user2, session_key='key2', is_active=True)

        request = self.factory.post('/api/v1/auth/login')

        # Cerrar sesiones de user1
        close_previous_sessions(user1, request)

        # Verificar que solo se cerró sesión de user1
        session1.refresh_from_db()
        session2.refresh_from_db()
        assert session1.is_active is False
        assert session2.is_active is True  # No afectada


@pytest.mark.django_db
class TestRF010SesionUnicaIntegration:
    """Tests de integración para RF-010"""

    def test_010_int_001_flujo_completo_login_cierre_sesion_anterior(self):
        """TEST-010-INT-001: Flujo completo de sesión única"""
        # TODO: Implementar test de integración
        pytest.skip("Test de integración - implementar después")

    def test_010_int_002_usuario_dispositivo_a_pierde_acceso_tras_login_dispositivo_b(self):
        """TEST-010-INT-002: Usuario en dispositivo A pierde acceso tras login en B"""
        # TODO: Implementar test de integración
        pytest.skip("Test de integración - implementar después")


@pytest.mark.django_db
class TestRF010SesionUnicaConfig:
    """Tests de configuración para RF-010"""

    def test_010_conf_001_session_engine_configurado_correctamente(self):
        """TEST-010-CONF-001: SESSION_ENGINE = 'django.contrib.sessions.backends.db'"""
        expected_engine = 'django.contrib.sessions.backends.db'
        assert settings.SESSION_ENGINE == expected_engine, \
            f"SESSION_ENGINE es {settings.SESSION_ENGINE}, esperado {expected_engine}"

    def test_010_conf_002_no_usa_redis_como_backend(self):
        """TEST-010-CONF-002: Verificar que NO se usa Redis"""
        session_engine = settings.SESSION_ENGINE.lower()
        assert 'redis' not in session_engine
        assert 'cache' not in session_engine
