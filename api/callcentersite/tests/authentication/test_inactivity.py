"""
Tests TDD para RF-008: Cierre Automático de Sesiones por Inactividad

Casos de prueba (10 tests):
- TEST-008-001 a TEST-008-010

Documentación: docs/implementacion/backend/requisitos/funcionales/rf008_cierre_inactividad.md
"""

import pytest
from datetime import timedelta
from django.utils.timezone import now
from django.test import RequestFactory

try:
    from callcentersite.apps.authentication.services import update_session_activity
    from callcentersite.apps.authentication.jobs import close_inactive_sessions
    from callcentersite.apps.users.models import User, UserSession
    from callcentersite.apps.audit.models import AuditLog
    from callcentersite.apps.notifications.models import InternalMessage
except ImportError:
    update_session_activity = None
    close_inactive_sessions = None
    User = None
    UserSession = None
    AuditLog = None
    InternalMessage = None


@pytest.mark.django_db
class TestRF008CierreInactividad:
    """Tests para RF-008: Cierre Automático por Inactividad"""

    def setup_method(self):
        self.factory = RequestFactory()

    def test_008_001_update_session_activity_actualiza_last_activity_at(self):
        """TEST-008-001: Actualiza last_activity_at en cada request"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=5)
        )
        old_activity = session.last_activity_at
        request = self.factory.get('/api/v1/endpoint')

        update_session_activity(user, request)

        session.refresh_from_db()
        assert session.last_activity_at > old_activity

    def test_008_002_sesion_inactiva_30_minutos_es_cerrada(self):
        """TEST-008-002: Sesión inactiva por 30+ minutos es cerrada"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=35)
        )

        result = close_inactive_sessions()

        session.refresh_from_db()
        assert session.is_active is False
        assert session.logout_reason == 'INACTIVITY_TIMEOUT'
        assert result['closed_sessions'] == 1

    def test_008_003_sesion_activa_menor_30_minutos_no_es_cerrada(self):
        """TEST-008-003: Sesión activa < 30 min NO es cerrada"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=10)
        )

        close_inactive_sessions()

        session.refresh_from_db()
        assert session.is_active is True

    def test_008_004_job_cierra_multiples_sesiones_en_lote(self):
        """TEST-008-004: Job cierra múltiples sesiones inactivas"""
        for i in range(5):
            user = User.objects.create_user(username=f'user{i}', password='Pass123!', email=f'u{i}@ex.com')
            UserSession.objects.create(
                user=user, session_key=f'key{i}', is_active=True,
                last_activity_at=now() - timedelta(minutes=35)
            )

        result = close_inactive_sessions()

        assert result['closed_sessions'] == 5

    def test_008_005_job_audita_evento_session_timeout(self):
        """TEST-008-005: Job audita evento SESSION_TIMEOUT"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=35)
        )

        close_inactive_sessions()

        assert AuditLog.objects.filter(event_type='SESSION_TIMEOUT', user_id=user.id).exists()

    def test_008_006_job_notifica_usuario_via_buzon_interno(self):
        """TEST-008-006: Job notifica vía buzón interno (NO email)"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=35)
        )

        close_inactive_sessions()

        notification = InternalMessage.objects.filter(
            user_id=user.id,
            subject__icontains='inactividad'
        ).first()
        assert notification is not None
        assert notification.created_by_system is True

    def test_008_007_job_elimina_django_session(self):
        """TEST-008-007: Job elimina django_session"""
        # TODO: Implementar con django_session
        pytest.skip("Implementar con django_session")

    def test_008_008_usuario_reactiva_sesion_antes_cierre(self):
        """TEST-008-008: Usuario reactiva sesión antes del cierre"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        session = UserSession.objects.create(
            user=user, session_key='abc', is_active=True,
            last_activity_at=now() - timedelta(minutes=29)
        )
        request = self.factory.get('/api/v1/endpoint')

        update_session_activity(user, request)
        close_inactive_sessions()

        session.refresh_from_db()
        assert session.is_active is True  # No se cierra porque se actualizó

    def test_008_009_access_token_valido_despues_cierre_inactividad(self):
        """TEST-008-009: Access token sigue válido después de cierre por inactividad"""
        # Nota: JWT es stateless, sigue válido hasta expirar
        pytest.skip("Test conceptual - JWT stateless")

    def test_008_010_job_programado_cada_5_minutos(self):
        """TEST-008-010: Job configurado para ejecutarse cada 5 minutos"""
        # TODO: Verificar configuración de APScheduler
        pytest.skip("Verificar configuración de scheduler")
