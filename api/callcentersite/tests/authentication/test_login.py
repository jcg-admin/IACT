"""
Tests TDD para RF-005: Login con Credenciales Locales

Este módulo contiene los tests para validar el comportamiento del login
con credenciales locales, basado en los requisitos funcionales RF-005 y
las reglas de negocio RN-C01-01 y RN-C01-02.

Casos de prueba:
- TEST-005-001: Login exitoso con credenciales válidas
- TEST-005-002: Login fallido con credenciales inválidas
- TEST-005-003: Login fallido con usuario inexistente
- TEST-005-004: Login fallido con cuenta bloqueada
- TEST-005-005: Login fallido con usuario inactivo
- TEST-005-006: Desbloqueo automático tras 15 minutos
- TEST-005-007: Bloqueo automático al tercer intento fallido
- TEST-005-008: Cierre de sesión anterior (sesión única)
- TEST-005-009: Reset de contador de intentos en login exitoso
- TEST-005-010: No revelar existencia de username
- TEST-005-011: Performance de login menor a 500ms

Documentación: docs/implementacion/backend/requisitos/funcionales/rf005_login_credenciales_locales.md
"""

import pytest
import time
from datetime import timedelta
from django.utils.timezone import now
from django.test import RequestFactory
from rest_framework.test import APIClient

# Nota: Estas importaciones fallarán hasta que implementemos los módulos
# Esto es esperado en TDD - primero escribimos los tests, luego el código
try:
    from callcentersite.apps.authentication.services import AuthenticationService
    from callcentersite.apps.users.models import User, UserSession
    from callcentersite.apps.audit.models import AuditLog
    from callcentersite.apps.notifications.models import InternalMessage
except ImportError:
    # Los módulos aún no existen - esto es esperado en TDD
    AuthenticationService = None
    User = None
    UserSession = None
    AuditLog = None
    InternalMessage = None


@pytest.mark.django_db
class TestRF005LoginCredencialesLocales:
    """
    Tests para RF-005: Login con Credenciales Locales

    Escenario principal: Usuario se autentica con username/password
    almacenados en PostgreSQL y recibe tokens JWT.
    """

    def setup_method(self):
        """Configuración antes de cada test"""
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_005_001_login_exitoso_con_credenciales_validas(self):
        """
        TEST-005-001: Login exitoso con credenciales válidas

        Given: un usuario registrado "juan.perez" con contraseña "SecureP@ss123"
          And: el usuario tiene status='ACTIVO'
          And: el usuario NO está bloqueado (is_locked=False)
          And: la contraseña coincide con el hash bcrypt almacenado
        When: el usuario envía POST /api/v1/auth/login
        Then: el sistema retorna HTTP 200 OK
          And: el sistema retorna access_token (válido 15 minutos)
          And: el sistema retorna refresh_token (válido 7 días)
          And: el sistema retorna token_type: "Bearer"
          And: el sistema retorna expires_in: 900 (segundos)
          And: el sistema resetea failed_login_attempts a 0
          And: el sistema actualiza last_login_at
          And: el sistema audita evento LOGIN_SUCCESS
        """
        # Arrange
        user = User.objects.create_user(
            username='juan.perez',
            password='SecureP@ss123',
            email='juan.perez@company.com',
            status='ACTIVO',
            is_locked=False,
            segment='GE'
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act
        result = AuthenticationService.login(
            username='juan.perez',
            password='SecureP@ss123',
            request=request
        )

        # Assert
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 900  # 15 minutos en segundos

        # Verificar que el usuario fue actualizado
        user.refresh_from_db()
        assert user.failed_login_attempts == 0
        assert user.last_login_at is not None

        # Verificar auditoría
        audit = AuditLog.objects.filter(
            event_type='LOGIN_SUCCESS',
            user_id=user.id
        ).first()
        assert audit is not None
        assert audit.result == 'SUCCESS'

    def test_005_002_login_fallido_credenciales_invalidas(self):
        """
        TEST-005-002: Login fallido con credenciales inválidas

        Given: un usuario registrado "juan.perez"
          And: el usuario tiene password_hash válido
        When: el usuario envía POST /api/v1/auth/login con password incorrecta
        Then: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna error "Credenciales inválidas"
          And: el sistema retorna attempts_remaining: 2
          And: el sistema incrementa failed_login_attempts de 0 a 1
          And: el sistema NO revela si el username existe
          And: el sistema audita evento LOGIN_FAILURE
        """
        # Arrange
        user = User.objects.create_user(
            username='juan.perez',
            password='CorrectP@ss123',
            email='juan.perez@company.com',
            status='ACTIVO'
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            AuthenticationService.login(
                username='juan.perez',
                password='WrongPassword',
                request=request
            )

        assert 'Credenciales inválidas' in str(exc_info.value)

        # Verificar que el contador se incrementó
        user.refresh_from_db()
        assert user.failed_login_attempts == 1
        assert user.last_failed_login_at is not None

        # Verificar auditoría
        audit = AuditLog.objects.filter(
            event_type='LOGIN_FAILURE'
        ).first()
        assert audit is not None

    def test_005_003_login_fallido_usuario_inexistente(self):
        """
        TEST-005-003: Login fallido con usuario inexistente

        Given: un username "usuario.inexistente" que NO existe en la BD
        When: el usuario envía POST /api/v1/auth/login con ese username
        Then: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna "Credenciales inválidas" (mismo mensaje)
          And: el sistema NO revela que el usuario no existe
          And: el sistema NO incrementa contador (usuario no existe)
          And: el sistema audita evento LOGIN_FAILURE con username (NO user_id)
        """
        # Arrange
        request = self.factory.post('/api/v1/auth/login')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            AuthenticationService.login(
                username='usuario.inexistente',
                password='AnyPassword123!',
                request=request
            )

        # Verificar que el mensaje NO revela que el usuario no existe
        assert 'Credenciales inválidas' in str(exc_info.value)
        assert 'no existe' not in str(exc_info.value).lower()

        # Verificar auditoría (con username, no user_id)
        audit = AuditLog.objects.filter(
            event_type='LOGIN_FAILURE'
        ).first()
        assert audit is not None
        assert audit.user_id is None  # No hay user_id porque no existe

    def test_005_004_login_fallido_cuenta_bloqueada(self):
        """
        TEST-005-004: Login fallido con cuenta bloqueada

        Given: un usuario "bob" con failed_login_attempts=3
          And: el usuario tiene is_locked=True
          And: el usuario tiene locked_until=<timestamp futuro>
        When: el usuario envía POST /api/v1/auth/login con credenciales válidas
        Then: el sistema retorna HTTP 403 Forbidden
          And: el sistema retorna error "Cuenta bloqueada"
          And: el sistema retorna locked_until y minutes_remaining
          And: el sistema NO permite login hasta que pase locked_until
          And: el sistema NO resetea el contador de intentos
        """
        # Arrange
        locked_until = now() + timedelta(minutes=10)
        user = User.objects.create_user(
            username='bob',
            password='ValidP@ss123',
            email='bob@company.com',
            status='ACTIVO',
            is_locked=True,
            locked_until=locked_until,
            failed_login_attempts=3
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            AuthenticationService.login(
                username='bob',
                password='ValidP@ss123',
                request=request
            )

        assert 'Cuenta bloqueada' in str(exc_info.value) or 'bloqueado' in str(exc_info.value).lower()

        # Verificar que el contador NO se reseteó
        user.refresh_from_db()
        assert user.failed_login_attempts == 3
        assert user.is_locked is True

    def test_005_005_login_fallido_usuario_inactivo(self):
        """
        TEST-005-005: Login fallido con usuario inactivo

        Given: un usuario "alice" con status='INACTIVO'
          And: el usuario tiene credenciales válidas
        When: el usuario envía POST /api/v1/auth/login
        Then: el sistema retorna HTTP 403 Forbidden
          And: el sistema retorna error "Usuario inactivo"
          And: el sistema NO genera tokens
        """
        # Arrange
        user = User.objects.create_user(
            username='alice',
            password='ValidP@ss123',
            email='alice@company.com',
            status='INACTIVO'  # Usuario inactivo
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            AuthenticationService.login(
                username='alice',
                password='ValidP@ss123',
                request=request
            )

        assert 'inactivo' in str(exc_info.value).lower()

    def test_005_006_desbloqueo_automatico_tras_15_minutos(self):
        """
        TEST-005-006: Desbloqueo automático tras 15 minutos

        Given: un usuario "carol" con is_locked=True
          And: el usuario tiene locked_until=<timestamp pasado>
        When: el usuario envía POST /api/v1/auth/login con credenciales válidas
        Then: el sistema desbloquea automáticamente la cuenta
          And: el sistema establece is_locked=False
          And: el sistema resetea failed_login_attempts a 0
          And: el sistema establece locked_until=NULL
          And: el sistema permite el login exitoso
          And: el sistema audita evento USER_UNLOCKED con reason='automatic_timeout'
          And: el sistema retorna tokens JWT normalmente
        """
        # Arrange
        locked_until = now() - timedelta(minutes=1)  # Ya pasó el tiempo
        user = User.objects.create_user(
            username='carol',
            password='ValidP@ss123',
            email='carol@company.com',
            status='ACTIVO',
            is_locked=True,
            locked_until=locked_until,
            failed_login_attempts=3
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act
        result = AuthenticationService.login(
            username='carol',
            password='ValidP@ss123',
            request=request
        )

        # Assert - login exitoso
        assert 'access_token' in result

        # Verificar desbloqueo automático
        user.refresh_from_db()
        assert user.is_locked is False
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

        # Verificar auditoría de desbloqueo
        audit = AuditLog.objects.filter(
            event_type='USER_UNLOCKED',
            user_id=user.id
        ).first()
        assert audit is not None
        assert audit.details.get('reason') == 'automatic_timeout'

    def test_005_007_bloqueo_automatico_tercer_intento(self):
        """
        TEST-005-007: Bloqueo automático al tercer intento fallido

        Given: un usuario "dave" con failed_login_attempts=2
          And: el usuario NO está bloqueado aún
        When: el usuario envía POST /api/v1/auth/login con password incorrecta (3er intento)
        Then: el sistema incrementa failed_login_attempts a 3
          And: el sistema establece is_locked=True
          And: el sistema establece locked_until=<now + 15 minutos>
          And: el sistema establece lock_reason='MAX_FAILED_ATTEMPTS'
          And: el sistema retorna HTTP 403 Forbidden
          And: el sistema audita evento USER_LOCKED
          And: el sistema envía notificación a buzón interno (NO email)
        """
        # Arrange
        user = User.objects.create_user(
            username='dave',
            password='ValidP@ss123',
            email='dave@company.com',
            status='ACTIVO',
            failed_login_attempts=2  # Ya tiene 2 intentos fallidos
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act & Assert - tercer intento fallido
        with pytest.raises(Exception) as exc_info:
            AuthenticationService.login(
                username='dave',
                password='WrongPassword',  # Password incorrecta
                request=request
            )

        # Verificar bloqueo
        user.refresh_from_db()
        assert user.failed_login_attempts == 3
        assert user.is_locked is True
        assert user.locked_until is not None
        assert user.lock_reason == 'MAX_FAILED_ATTEMPTS'

        # Verificar que locked_until es aproximadamente 15 minutos en el futuro
        time_diff = (user.locked_until - now()).total_seconds()
        assert 890 < time_diff < 910  # ~15 minutos (con margen de error)

        # Verificar auditoría
        audit = AuditLog.objects.filter(
            event_type='USER_LOCKED',
            user_id=user.id
        ).first()
        assert audit is not None
        assert audit.details.get('reason') == 'max_failed_attempts'

        # Verificar notificación por buzón interno (NO email)
        notification = InternalMessage.objects.filter(
            user_id=user.id,
            subject__icontains='bloqueada'
        ).first()
        assert notification is not None
        assert notification.created_by_system is True

    def test_005_008_cierre_sesion_anterior_sesion_unica(self):
        """
        TEST-005-008: Cierre de sesión anterior (sesión única)

        Given: un usuario "eve" con sesión activa en dispositivo A
          And: la sesión tiene session_key="abc123" y is_active=True
        When: el usuario hace login desde dispositivo B
        Then: el sistema cierra la sesión anterior (dispositivo A)
          And: el sistema establece session(abc123).is_active=False
          And: el sistema establece session(abc123).logged_out_at=<now>
          And: el sistema establece session(abc123).logout_reason='NEW_SESSION'
          And: el sistema audita evento SESSION_CLOSED
          And: el sistema envía notificación a buzón interno
          And: el sistema crea nueva sesión para dispositivo B
        """
        # Arrange
        user = User.objects.create_user(
            username='eve',
            password='ValidP@ss123',
            email='eve@company.com',
            status='ACTIVO'
        )

        # Crear sesión activa previa
        old_session = UserSession.objects.create(
            user=user,
            session_key='abc123',
            is_active=True,
            user_agent='Chrome/DeviceA'
        )

        request = self.factory.post('/api/v1/auth/login')
        request.session = {'session_key': 'xyz789'}  # Nueva sesión

        # Act
        result = AuthenticationService.login(
            username='eve',
            password='ValidP@ss123',
            request=request
        )

        # Assert
        assert 'access_token' in result

        # Verificar que la sesión anterior fue cerrada
        old_session.refresh_from_db()
        assert old_session.is_active is False
        assert old_session.logged_out_at is not None
        assert old_session.logout_reason == 'NEW_SESSION'

        # Verificar auditoría de cierre
        audit = AuditLog.objects.filter(
            event_type='SESSION_CLOSED',
            user_id=user.id
        ).first()
        assert audit is not None

        # Verificar notificación
        notification = InternalMessage.objects.filter(
            user_id=user.id,
            subject__icontains='nueva sesión'
        ).first()
        assert notification is not None

    def test_005_009_resetea_contador_intentos_en_login_exitoso(self):
        """
        TEST-005-009: Reset de contador de intentos en login exitoso

        Given: un usuario "frank" con failed_login_attempts=2
          And: el usuario NO está bloqueado
        When: el usuario hace login exitoso con credenciales válidas
        Then: el sistema resetea failed_login_attempts a 0
          And: el sistema establece last_failed_login_at=NULL
          And: el usuario puede hacer login normalmente
        """
        # Arrange
        user = User.objects.create_user(
            username='frank',
            password='ValidP@ss123',
            email='frank@company.com',
            status='ACTIVO',
            failed_login_attempts=2  # Tiene 2 intentos fallidos previos
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act
        result = AuthenticationService.login(
            username='frank',
            password='ValidP@ss123',
            request=request
        )

        # Assert
        assert 'access_token' in result

        # Verificar reset del contador
        user.refresh_from_db()
        assert user.failed_login_attempts == 0
        assert user.last_failed_login_at is None

    def test_005_010_no_revela_existencia_username(self):
        """
        TEST-005-010: No revelar existencia de username

        Given: sistema de login configurado
        When: se intenta login con username inexistente
        Then: el mensaje de error es idéntico al de password incorrecta
          And: el sistema NO revela si el username existe o no
          And: ambos casos retornan "Credenciales inválidas"
        """
        # Arrange - crear usuario existente
        user = User.objects.create_user(
            username='existente',
            password='ValidP@ss123',
            email='existente@company.com',
            status='ACTIVO'
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act - intentar con usuario inexistente
        error_msg_1 = None
        try:
            AuthenticationService.login(
                username='inexistente',
                password='AnyPassword123!',
                request=request
            )
        except Exception as e:
            error_msg_1 = str(e)

        # Act - intentar con usuario existente pero password incorrecta
        error_msg_2 = None
        try:
            AuthenticationService.login(
                username='existente',
                password='WrongPassword123!',
                request=request
            )
        except Exception as e:
            error_msg_2 = str(e)

        # Assert - ambos mensajes deben ser idénticos
        assert error_msg_1 is not None
        assert error_msg_2 is not None
        assert 'Credenciales inválidas' in error_msg_1
        assert 'Credenciales inválidas' in error_msg_2
        # Verificar que NO se menciona "no existe" o similar
        assert 'no existe' not in error_msg_1.lower()

    def test_005_011_performance_login_menor_500ms(self):
        """
        TEST-005-011: Performance de login menor a 500ms

        Given: un usuario con credenciales válidas
        When: el usuario hace login
        Then: el tiempo total de procesamiento es menor a 500ms

        Nota: bcrypt con cost factor 12 toma ~300-400ms,
        más ~10-50ms de query a PostgreSQL = ~350-450ms total
        """
        # Arrange
        user = User.objects.create_user(
            username='perf_test',
            password='ValidP@ss123',
            email='perf@company.com',
            status='ACTIVO'
        )

        request = self.factory.post('/api/v1/auth/login')

        # Act - medir tiempo
        start_time = time.time()
        result = AuthenticationService.login(
            username='perf_test',
            password='ValidP@ss123',
            request=request
        )
        end_time = time.time()

        # Assert
        elapsed_time = (end_time - start_time) * 1000  # en milisegundos
        assert elapsed_time < 500, f"Login tomó {elapsed_time}ms, esperado < 500ms"
        assert 'access_token' in result


# Tests de integración
@pytest.mark.django_db
class TestRF005LoginIntegration:
    """Tests de integración para RF-005"""

    def test_005_int_001_flujo_completo_login_con_auditoria(self):
        """
        TEST-005-INT-001: Flujo completo de login con auditoría

        Verifica el flujo end-to-end desde login hasta tokens,
        incluyendo auditoría y actualización de usuario.
        """
        # TODO: Implementar test de integración completo
        pytest.skip("Test de integración - implementar después")

    def test_005_int_002_login_con_cierre_sesion_previa_y_notificacion(self):
        """
        TEST-005-INT-002: Login con cierre de sesión previa y notificación

        Verifica el flujo completo de sesión única con notificación.
        """
        # TODO: Implementar test de integración completo
        pytest.skip("Test de integración - implementar después")
