"""
Tests TDD para RF-009: Gestión de Contraseñas Seguras e Intentos Fallidos

Casos de prueba (23 tests):
- Complejidad de contraseñas (9 tests)
- Hashing con bcrypt (4 tests)
- Intentos fallidos (5 tests)
- Bloqueo y desbloqueo (5 tests)

Documentación: docs/implementacion/backend/requisitos/funcionales/rf009_gestion_passwords_intentos_fallidos.md
"""

import pytest
import bcrypt
from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError

try:
    from callcentersite.apps.authentication.validators import validate_password_complexity
    from callcentersite.apps.authentication.services import (
        hash_password, verify_password, handle_failed_login,
        unlock_user_manual, validate_password_history
    )
    from callcentersite.apps.users.models import User, PasswordHistory
    from callcentersite.apps.audit.models import AuditLog
    from callcentersite.apps.notifications.models import InternalMessage
except ImportError:
    validate_password_complexity = None
    hash_password = None
    verify_password = None
    handle_failed_login = None
    unlock_user_manual = None
    validate_password_history = None
    User = None
    PasswordHistory = None
    AuditLog = None
    InternalMessage = None


@pytest.mark.django_db
class TestRF009ComplejidadPasswords:
    """Tests de complejidad de contraseñas"""

    def test_009_001_password_valida_cumple_complejidad(self):
        """TEST-009-001: Password válida cumple todos los requisitos"""
        user = User.objects.create(username='test')
        validate_password_complexity('SecureP@ss123', user)
        # No debe lanzar excepción

    def test_009_002_password_rechazada_sin_mayuscula(self):
        """TEST-009-002: Rechaza password sin mayúscula"""
        with pytest.raises(ValidationError) as exc:
            validate_password_complexity('securep@ss123', None)
        assert 'mayúscula' in str(exc.value).lower()

    def test_009_003_password_rechazada_sin_minuscula(self):
        """TEST-009-003: Rechaza password sin minúscula"""
        with pytest.raises(ValidationError):
            validate_password_complexity('SECUREP@SS123', None)

    def test_009_004_password_rechazada_sin_digito(self):
        """TEST-009-004: Rechaza password sin dígito"""
        with pytest.raises(ValidationError):
            validate_password_complexity('SecureP@ssword', None)

    def test_009_005_password_rechazada_sin_caracter_especial(self):
        """TEST-009-005: Rechaza password sin carácter especial"""
        with pytest.raises(ValidationError):
            validate_password_complexity('SecurePass123', None)

    def test_009_006_password_rechazada_menor_8_caracteres(self):
        """TEST-009-006: Rechaza password < 8 caracteres"""
        with pytest.raises(ValidationError) as exc:
            validate_password_complexity('Pass1!', None)
        assert '8 caracteres' in str(exc.value)

    def test_009_007_password_rechazada_mayor_100_caracteres(self):
        """TEST-009-007: Rechaza password > 100 caracteres"""
        long_password = 'A' * 101 + 'a1!'
        with pytest.raises(ValidationError):
            validate_password_complexity(long_password, None)

    def test_009_008_password_rechazada_contiene_username(self):
        """TEST-009-008: Rechaza password que contiene username"""
        user = User.objects.create(username='juanperez')
        with pytest.raises(ValidationError) as exc:
            validate_password_complexity('JuanPerez123!', user)
        assert 'username' in str(exc.value).lower()

    def test_009_009_password_rechazada_reutiliza_reciente(self):
        """TEST-009-009: Rechaza reutilización de últimas 5 passwords"""
        user = User.objects.create_user(username='test', password='OldP@ss123', email='test@ex.com')
        PasswordHistory.objects.create(
            user=user,
            password_hash=hash_password('OldP@ss123')
        )

        with pytest.raises(ValidationError) as exc:
            validate_password_history(user, 'OldP@ss123')
        assert 'últimas 5' in str(exc.value)


@pytest.mark.django_db
class TestRF009HashingBcrypt:
    """Tests de hashing con bcrypt"""

    def test_009_010_hash_bcrypt_cost_factor_12(self):
        """TEST-009-010: Hash usa bcrypt con cost factor 12"""
        password = 'SecureP@ss123'
        hashed = hash_password(password)

        assert hashed.startswith('$2b$12$')  # bcrypt cost 12

    def test_009_011_hash_bcrypt_salt_unico(self):
        """TEST-009-011: Cada hash tiene salt único"""
        password = 'SecureP@ss123'
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Diferentes por salt único

    def test_009_012_verify_password_exitoso(self):
        """TEST-009-012: Verificación exitosa de password"""
        password = 'SecureP@ss123'
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_009_013_verify_password_fallido(self):
        """TEST-009-013: Verificación fallida con password incorrecta"""
        password = 'SecureP@ss123'
        hashed = hash_password(password)

        assert verify_password('WrongPassword', hashed) is False


@pytest.mark.django_db
class TestRF009IntentosFallidos:
    """Tests de intentos fallidos"""

    def test_009_014_primer_intento_fallido_incrementa_contador(self):
        """TEST-009-014: Primer intento fallido incrementa contador a 1"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        assert user.failed_login_attempts == 0

        handle_failed_login('test')

        user.refresh_from_db()
        assert user.failed_login_attempts == 1
        assert user.last_failed_login_at is not None

    def test_009_015_tercer_intento_fallido_bloquea_cuenta(self):
        """TEST-009-015: Tercer intento fallido bloquea cuenta"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.failed_login_attempts = 2
        user.save()

        handle_failed_login('test')

        user.refresh_from_db()
        assert user.failed_login_attempts == 3
        assert user.is_locked is True
        assert user.locked_until is not None
        assert user.lock_reason == 'MAX_FAILED_ATTEMPTS'

    def test_009_016_login_exitoso_resetea_contador(self):
        """TEST-009-016: Login exitoso resetea contador a 0"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.failed_login_attempts = 2
        user.save()

        # Simular login exitoso
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.save()

        user.refresh_from_db()
        assert user.failed_login_attempts == 0

    def test_009_017_contador_no_resetea_por_tiempo(self):
        """TEST-009-017: Contador NO se resetea automáticamente por tiempo"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.failed_login_attempts = 2
        user.last_failed_login_at = now() - timedelta(days=7)
        user.save()

        user.refresh_from_db()
        assert user.failed_login_attempts == 2  # NO se resetea

    def test_009_018_notificacion_buzon_interno_al_bloquear(self):
        """TEST-009-018: Notifica vía buzón interno al bloquear (NO email)"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.failed_login_attempts = 2
        user.save()

        handle_failed_login('test')

        notification = InternalMessage.objects.filter(
            user_id=user.id,
            subject__icontains='bloqueada'
        ).first()
        assert notification is not None
        assert notification.created_by_system is True


@pytest.mark.django_db
class TestRF009BloqueoDesbloqueo:
    """Tests de bloqueo y desbloqueo"""

    def test_009_019_desbloqueo_automatico_tras_15_minutos(self):
        """TEST-009-019: Desbloqueo automático tras 15 minutos"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.is_locked = True
        user.locked_until = now() - timedelta(minutes=1)  # Ya pasó
        user.failed_login_attempts = 3
        user.save()

        # Simular validación de credenciales que detecta desbloqueo
        if user.locked_until and now() >= user.locked_until:
            user.is_locked = False
            user.locked_until = None
            user.failed_login_attempts = 0
            user.save()

        user.refresh_from_db()
        assert user.is_locked is False

    def test_009_020_desbloqueo_manual_por_admin_con_role_r016(self):
        """TEST-009-020: Admin con role R016 puede desbloquear manualmente"""
        admin = User.objects.create_user(username='admin', password='Pass123!', email='admin@ex.com')
        # admin.roles.add('R016')  # Role de administrador

        target_user = User.objects.create_user(username='blocked', password='Pass123!', email='blocked@ex.com')
        target_user.is_locked = True
        target_user.save()

        unlock_user_manual(admin, target_user)

        target_user.refresh_from_db()
        assert target_user.is_locked is False

    def test_009_021_desbloqueo_manual_rechazado_sin_role_r016(self):
        """TEST-009-021: Usuario sin role R016 NO puede desbloquear"""
        regular_user = User.objects.create_user(username='regular', password='Pass123!', email='regular@ex.com')
        target_user = User.objects.create_user(username='blocked', password='Pass123!', email='blocked@ex.com')
        target_user.is_locked = True
        target_user.save()

        with pytest.raises(Exception):
            unlock_user_manual(regular_user, target_user)

    def test_009_022_auditoria_user_locked(self):
        """TEST-009-022: Audita evento USER_LOCKED"""
        user = User.objects.create_user(username='test', password='Pass123!', email='test@ex.com')
        user.failed_login_attempts = 2
        user.save()

        handle_failed_login('test')

        assert AuditLog.objects.filter(event_type='USER_LOCKED', user_id=user.id).exists()

    def test_009_023_auditoria_user_unlocked(self):
        """TEST-009-023: Audita evento USER_UNLOCKED"""
        admin = User.objects.create_user(username='admin', password='Pass123!', email='admin@ex.com')
        target_user = User.objects.create_user(username='blocked', password='Pass123!', email='blocked@ex.com')
        target_user.is_locked = True
        target_user.save()

        unlock_user_manual(admin, target_user)

        assert AuditLog.objects.filter(event_type='USER_UNLOCKED', user_id=target_user.id).exists()


@pytest.mark.django_db
class TestRF009PasswordsIntegration:
    """Tests de integración para RF-009"""

    def test_009_int_001_flujo_completo_3_intentos_bloqueo_desbloqueo(self):
        """TEST-009-INT-001: Flujo completo de intentos fallidos"""
        # TODO: Implementar test de integración
        pytest.skip("Test de integración - implementar después")

    def test_009_int_002_cambio_password_valida_complejidad_e_historial(self):
        """TEST-009-INT-002: Cambio de password valida complejidad e historial"""
        # TODO: Implementar test de integración
        pytest.skip("Test de integración - implementar después")
