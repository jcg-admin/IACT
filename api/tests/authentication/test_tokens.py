"""
Tests TDD para RF-006: Generación y Validación de Tokens JWT

Este módulo contiene los tests para validar la generación, validación y
refresh de tokens JWT, basado en el requisito funcional RF-006 y las
reglas de negocio RN-C01-03, RN-C01-04 y RN-C01-11.

Casos de prueba:
- TEST-006-001: Generación de tokens con claims personalizados
- TEST-006-002: Access token expira exactamente en 15 minutos
- TEST-006-003: Refresh token expira exactamente en 7 días
- TEST-006-004: Validación exitosa de access token
- TEST-006-005: Validación falla con token expirado
- TEST-006-006: Validación falla con firma inválida
- TEST-006-007: Validación falla con tipo de token incorrecto
- TEST-006-008: Validación falla con usuario inactivo
- TEST-006-009: Validación falla con usuario bloqueado
- TEST-006-010: Refresh token genera nuevo par de tokens
- TEST-006-011: Refresh token blacklistea el token viejo
- TEST-006-012: Refresh token falla con token blacklisted
- TEST-006-013: Refresh token falla con token expirado
- TEST-006-014: Algoritmo de firma es HS256
- TEST-006-015: SECRET_KEY tiene longitud mínima de 256 bits

Documentación: docs/implementacion/backend/requisitos/funcionales/rf006_tokens_jwt.md
"""

import pytest
import jwt
from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient

# Nota: Estas importaciones fallarán hasta que implementemos los módulos
try:
    from callcentersite.apps.authentication.services import TokenService
    from callcentersite.apps.users.models import User
    from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
    from rest_framework_simplejwt.exceptions import TokenError
except ImportError:
    TokenService = None
    User = None
    RefreshToken = None
    AccessToken = None
    TokenError = None


@pytest.mark.django_db
class TestRF006TokensJWT:
    """
    Tests para RF-006: Generación y Validación de Tokens JWT

    Escenario principal: Sistema genera y valida tokens JWT con
    configuración específica (15min access, 7 días refresh).
    """

    def setup_method(self):
        """Configuración antes de cada test"""
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_006_001_generacion_tokens_con_claims_personalizados(self):
        """
        TEST-006-001: Generación de tokens con claims personalizados

        Given: un usuario "juan.perez" autenticado exitosamente
          And: el usuario tiene segment="GE"
          And: el usuario tiene roles=["ANALISTA_DATOS", "VIEWER_BASICO"]
        When: el sistema genera tokens JWT
        Then: el access_token contiene todos los claims personalizados
          And: el refresh_token contiene los mismos claims
          And: ambos tokens están firmados con SECRET_KEY usando HS256
        """
        # Arrange
        user = User.objects.create_user(
            username='juan.perez',
            password='SecureP@ss123',
            email='juan.perez@company.com',
            segment='GE'
        )
        # Agregar roles
        # user.roles.add('ANALISTA_DATOS', 'VIEWER_BASICO')

        # Act
        tokens = TokenService.generate_jwt_tokens(user)

        # Assert - estructura básica
        assert 'access' in tokens
        assert 'refresh' in tokens

        # Decodificar access token (sin verificar para inspección)
        access_payload = jwt.decode(
            tokens['access'],
            options={"verify_signature": False}
        )

        # Verificar claims personalizados en access token
        assert access_payload['user_id'] == user.id
        assert access_payload['username'] == 'juan.perez'
        assert access_payload['email'] == 'juan.perez@company.com'
        assert access_payload['segment'] == 'GE'
        assert 'roles' in access_payload
        assert access_payload['token_type'] == 'access'

        # Verificar claims estándar
        assert 'iat' in access_payload  # issued at
        assert 'exp' in access_payload  # expiration
        assert 'jti' in access_payload  # JWT ID

        # Decodificar refresh token
        refresh_payload = jwt.decode(
            tokens['refresh'],
            options={"verify_signature": False}
        )

        # Verificar que refresh token tiene los mismos claims personalizados
        assert refresh_payload['username'] == 'juan.perez'
        assert refresh_payload['email'] == 'juan.perez@company.com'
        assert refresh_payload['token_type'] == 'refresh'

    def test_006_002_access_token_expira_exactamente_15_minutos(self):
        """
        TEST-006-002: Access token expira exactamente en 15 minutos

        Given: un usuario autenticado
        When: el sistema genera access token
        Then: el token expira exactamente 15 minutos después de emisión
          And: exp - iat = 900 segundos (15 minutos)
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        # Act
        tokens = TokenService.generate_jwt_tokens(user)

        # Assert
        access_payload = jwt.decode(
            tokens['access'],
            options={"verify_signature": False}
        )

        # Calcular duración
        iat = access_payload['iat']
        exp = access_payload['exp']
        duration_seconds = exp - iat

        # Verificar que es exactamente 15 minutos (900 segundos)
        assert duration_seconds == 900, f"Access token expira en {duration_seconds}s, esperado 900s (15min)"

    def test_006_003_refresh_token_expira_exactamente_7_dias(self):
        """
        TEST-006-003: Refresh token expira exactamente en 7 días

        Given: un usuario autenticado
        When: el sistema genera refresh token
        Then: el token expira exactamente 7 días después de emisión
          And: exp - iat = 604800 segundos (7 días)
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        # Act
        tokens = TokenService.generate_jwt_tokens(user)

        # Assert
        refresh_payload = jwt.decode(
            tokens['refresh'],
            options={"verify_signature": False}
        )

        # Calcular duración
        iat = refresh_payload['iat']
        exp = refresh_payload['exp']
        duration_seconds = exp - iat

        # Verificar que es exactamente 7 días (604800 segundos)
        expected_seconds = 7 * 24 * 60 * 60  # 604800
        assert duration_seconds == expected_seconds, \
            f"Refresh token expira en {duration_seconds}s, esperado {expected_seconds}s (7 días)"

    def test_006_004_validacion_exitosa_access_token(self):
        """
        TEST-006-004: Validación exitosa de access token

        Given: un usuario con access_token válido
          And: el token NO ha expirado (< 15 minutos)
          And: el token tiene firma válida
          And: el usuario está activo (is_active=True)
          And: el usuario NO está bloqueado (is_locked=False)
        When: el usuario envía request con header Authorization
        Then: el sistema valida el token exitosamente
          And: el sistema extrae user_id del claim
          And: el sistema permite acceso al endpoint protegido
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com',
            status='ACTIVO',
            is_locked=False
        )

        tokens = TokenService.generate_jwt_tokens(user)
        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'

        # Act
        validated_user = TokenService.validate_access_token(request)

        # Assert
        assert validated_user is not None
        assert validated_user.id == user.id
        assert validated_user.username == 'test_user'

    def test_006_005_validacion_falla_token_expirado(self):
        """
        TEST-006-005: Validación falla con token expirado

        Given: un usuario con access_token emitido hace 16 minutos
          And: el token tiene firma válida
        When: el usuario envía request con ese token
        Then: el sistema rechaza el token
          And: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna error "Token expirado"
        """
        # Arrange - crear token expirado manualmente
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        # Crear token que ya expiró
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Manipular exp para que esté en el pasado
        access.set_exp(lifetime=timedelta(seconds=-60))  # Expiró hace 1 minuto
        expired_token = str(access)

        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {expired_token}'

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.validate_access_token(request)

        assert 'expirado' in str(exc_info.value).lower() or 'expired' in str(exc_info.value).lower()

    def test_006_006_validacion_falla_firma_invalida(self):
        """
        TEST-006-006: Validación falla con firma inválida

        Given: un token JWT manipulado o firmado con otra SECRET_KEY
        When: el usuario envía request con ese token
        Then: el sistema rechaza el token
          And: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna error "Token inválido"
        """
        # Arrange - crear token con SECRET_KEY diferente
        fake_secret = "fake_secret_key_12345"
        payload = {
            'user_id': 999,
            'username': 'hacker',
            'token_type': 'access',
            'exp': (now() + timedelta(minutes=15)).timestamp(),
            'iat': now().timestamp()
        }
        fake_token = jwt.encode(payload, fake_secret, algorithm='HS256')

        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {fake_token}'

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.validate_access_token(request)

        assert 'inválido' in str(exc_info.value).lower() or 'invalid' in str(exc_info.value).lower()

    def test_006_007_validacion_falla_tipo_token_incorrecto(self):
        """
        TEST-006-007: Validación falla con tipo de token incorrecto

        Given: un usuario con refresh_token (NO access_token)
        When: el usuario intenta usar el refresh_token para acceder a endpoint protegido
        Then: el sistema rechaza el token
          And: el sistema retorna error "Debe usar access token"
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        tokens = TokenService.generate_jwt_tokens(user)
        refresh_token = tokens['refresh']  # Usar refresh en lugar de access

        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {refresh_token}'

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.validate_access_token(request)

        error_msg = str(exc_info.value).lower()
        assert 'access token' in error_msg or 'tipo' in error_msg

    def test_006_008_validacion_falla_usuario_inactivo(self):
        """
        TEST-006-008: Validación falla con usuario inactivo

        Given: un access_token válido (firma y expiración correctos)
          And: el usuario asociado tiene is_active=False
        When: el usuario envía request con ese token
        Then: el sistema rechaza el request
          And: el sistema retorna HTTP 403 Forbidden
          And: el sistema retorna error "Usuario inactivo"
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com',
            status='ACTIVO'
        )

        tokens = TokenService.generate_jwt_tokens(user)

        # Desactivar usuario después de generar token
        user.status = 'INACTIVO'
        user.save()

        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.validate_access_token(request)

        assert 'inactivo' in str(exc_info.value).lower()

    def test_006_009_validacion_falla_usuario_bloqueado(self):
        """
        TEST-006-009: Validación falla con usuario bloqueado

        Given: un access_token válido
          And: el usuario asociado tiene is_locked=True
        When: el usuario envía request con ese token
        Then: el sistema rechaza el request
          And: el sistema retorna HTTP 403 Forbidden
          And: el sistema retorna error "Usuario bloqueado"
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com',
            is_locked=False
        )

        tokens = TokenService.generate_jwt_tokens(user)

        # Bloquear usuario después de generar token
        user.is_locked = True
        user.save()

        request = self.factory.get('/api/v1/protected')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.validate_access_token(request)

        assert 'bloqueado' in str(exc_info.value).lower() or 'locked' in str(exc_info.value).lower()

    def test_006_010_refresh_token_genera_nuevo_par(self):
        """
        TEST-006-010: Refresh token genera nuevo par de tokens

        Given: un usuario con refresh_token válido
          And: el refresh_token NO ha expirado (< 7 días)
          And: el refresh_token NO está en blacklist
        When: el usuario envía POST /api/v1/auth/refresh
        Then: el sistema genera nuevo access_token (válido 15min)
          And: el sistema genera nuevo refresh_token (válido 7 días)
          And: el sistema retorna HTTP 200 OK con ambos tokens
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        original_tokens = TokenService.generate_jwt_tokens(user)
        refresh_token_str = original_tokens['refresh']

        # Act
        new_tokens = TokenService.refresh_access_token(refresh_token_str)

        # Assert
        assert 'access' in new_tokens
        assert 'refresh' in new_tokens

        # Verificar que los tokens son diferentes a los originales
        assert new_tokens['access'] != original_tokens['access']
        assert new_tokens['refresh'] != original_tokens['refresh']

        # Verificar que el nuevo access token es válido
        access_payload = jwt.decode(
            new_tokens['access'],
            options={"verify_signature": False}
        )
        assert access_payload['user_id'] == user.id

    def test_006_011_refresh_token_blacklistea_viejo(self):
        """
        TEST-006-011: Refresh token blacklistea el token viejo

        Given: un usuario con refresh_token válido
        When: el usuario usa el refresh_token para obtener nuevos tokens
        Then: el sistema blacklistea el refresh_token viejo
          And: el sistema NO permite reutilizar el refresh_token viejo
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        tokens = TokenService.generate_jwt_tokens(user)
        old_refresh = tokens['refresh']

        # Act - usar el refresh token por primera vez
        new_tokens = TokenService.refresh_access_token(old_refresh)

        # Assert - intentar usar el refresh token viejo nuevamente
        with pytest.raises(TokenError):
            TokenService.refresh_access_token(old_refresh)

    def test_006_012_refresh_token_falla_token_blacklisted(self):
        """
        TEST-006-012: Refresh token falla con token blacklisted

        Given: un refresh_token que ya fue usado previamente
          And: el token fue blacklisted al usarse (rotación)
        When: el usuario intenta usar ese refresh_token nuevamente
        Then: el sistema rechaza el token
          And: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna error "Token inválido o ya usado"
        """
        # Arrange
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        tokens = TokenService.generate_jwt_tokens(user)
        refresh_token = tokens['refresh']

        # Usar el refresh token (lo blacklistea)
        TokenService.refresh_access_token(refresh_token)

        # Act & Assert - intentar reutilizar
        with pytest.raises(Exception) as exc_info:
            TokenService.refresh_access_token(refresh_token)

        error_msg = str(exc_info.value).lower()
        assert 'blacklist' in error_msg or 'usado' in error_msg or 'invalid' in error_msg

    def test_006_013_refresh_token_falla_token_expirado(self):
        """
        TEST-006-013: Refresh token falla con token expirado

        Given: un refresh_token emitido hace 8 días (> 7 días)
        When: el usuario intenta refrescar el access_token
        Then: el sistema rechaza el refresh_token
          And: el sistema retorna HTTP 401 Unauthorized
          And: el sistema retorna error "Refresh token expirado"
        """
        # Arrange - crear refresh token expirado
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        refresh = RefreshToken.for_user(user)
        # Manipular para que expire
        refresh.set_exp(lifetime=timedelta(days=-1))  # Expiró hace 1 día
        expired_refresh = str(refresh)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            TokenService.refresh_access_token(expired_refresh)

        error_msg = str(exc_info.value).lower()
        assert 'expirado' in error_msg or 'expired' in error_msg

    def test_006_014_algoritmo_firma_es_hs256(self):
        """
        TEST-006-014: Algoritmo de firma es HS256

        Given: configuración de JWT
        Then: el algoritmo configurado es HS256
          And: NO se permite algoritmo "None"
          And: NO se permite algoritmo inseguro
        """
        # Assert - verificar configuración
        assert settings.SIMPLE_JWT['ALGORITHM'] == 'HS256'

        # Verificar que un token generado usa HS256
        user = User.objects.create_user(
            username='test_user',
            password='SecureP@ss123',
            email='test@company.com'
        )

        tokens = TokenService.generate_jwt_tokens(user)

        # Decodificar header del token
        header = jwt.get_unverified_header(tokens['access'])
        assert header['alg'] == 'HS256'
        assert header['typ'] == 'JWT'

    def test_006_015_secret_key_longitud_minima_256_bits(self):
        """
        TEST-006-015: SECRET_KEY tiene longitud mínima de 256 bits

        Given: configuración de Django
        Then: SECRET_KEY tiene al menos 32 caracteres (256 bits)
          And: SECRET_KEY NO es el valor por defecto de Django
        """
        # Assert
        secret_key = settings.SECRET_KEY

        # Verificar longitud mínima (32 caracteres = 256 bits)
        assert len(secret_key) >= 32, \
            f"SECRET_KEY tiene {len(secret_key)} caracteres, mínimo requerido: 32"

        # Verificar que NO es el default de Django
        assert secret_key != 'django-insecure-*', \
            "SECRET_KEY no debe ser el valor por defecto de Django"


# Tests de integración
@pytest.mark.django_db
class TestRF006TokensIntegration:
    """Tests de integración para RF-006"""

    def test_006_int_001_flujo_completo_login_validacion_refresh(self):
        """
        TEST-006-INT-001: Flujo completo login → validación → refresh

        Verifica el flujo end-to-end completo de tokens JWT.
        """
        # TODO: Implementar test de integración completo
        pytest.skip("Test de integración - implementar después")

    def test_006_int_002_rotacion_refresh_tokens_en_multiple_refresh(self):
        """
        TEST-006-INT-002: Rotación de refresh tokens en múltiples refresh

        Verifica que la rotación funciona correctamente en múltiples
        operaciones de refresh consecutivas.
        """
        # TODO: Implementar test de integración completo
        pytest.skip("Test de integración - implementar después")


# Tests de seguridad
@pytest.mark.django_db
class TestRF006TokensSecurity:
    """Tests de seguridad para RF-006"""

    def test_006_sec_001_no_acepta_algoritmo_none(self):
        """
        TEST-006-SEC-001: No acepta algoritmo "None"

        Verifica que el sistema rechaza tokens con algoritmo "None"
        (vulnerabilidad conocida).
        """
        # TODO: Implementar test de seguridad
        pytest.skip("Test de seguridad - implementar después")

    def test_006_sec_002_no_acepta_firma_con_otro_secret(self):
        """
        TEST-006-SEC-002: No acepta firma con otro SECRET_KEY

        Verifica que tokens firmados con diferente SECRET_KEY son rechazados.
        """
        # TODO: Implementar test de seguridad
        pytest.skip("Test de seguridad - implementar después")

    def test_006_sec_003_claims_no_contienen_password(self):
        """
        TEST-006-SEC-003: Claims no contienen password

        Verifica que los tokens JWT NO incluyen información sensible
        como passwords.
        """
        # TODO: Implementar test de seguridad
        pytest.skip("Test de seguridad - implementar después")
