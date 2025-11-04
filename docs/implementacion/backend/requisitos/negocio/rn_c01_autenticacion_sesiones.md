---
id: RN-C01-COMPONENTE-1
tipo: reglas_negocio
titulo: Reglas de Negocio - Componente 1 - Autenticación y Sesiones
version: 6.0.0
fecha_creacion: 2025-11-04
dominio: backend
componente: autenticacion_sesiones
owner: equipo-backend
estado: completo_definitivo
---

# COMPONENTE 1 - PARTE 1: REGLAS DE NEGOCIO

**Sistema:** IACT
**Componente:** 1 de 12 - Autenticación y Sesiones
**Documento:** Reglas de Negocio Detalladas (14 reglas)
**Versión:** 6.0.0 - COMPLETO Y DEFINITIVO
**Fecha:** 4 de noviembre de 2025

---

## 📋 ÍNDICE DE REGLAS

### Reglas MUST (14 reglas - 100%)

| # | Código | Nombre | Tipo | Sprint |
|---|--------|--------|------|--------|
| 1 | RN-C01-01 | Login con Credenciales Locales | ACTIVADOR | 1 |
| 2 | RN-C01-02 | Validación de Credenciales | RESTRICCIÓN | 1 |
| 3 | RN-C01-03 | Generación de Tokens JWT | ACTIVADOR | 1 |
| 4 | RN-C01-04 | Validación de Tokens JWT | RESTRICCIÓN | 1 |
| 5 | RN-C01-05 | Logout Manual | ACTIVADOR | 1 |
| 6 | RN-C01-06 | Cierre por Inactividad | ACTIVADOR | 1 |
| 7 | RN-C01-07 | Complejidad de Contraseñas | RESTRICCIÓN | 1 |
| 8 | RN-C01-08 | Intentos Fallidos Limitados | RESTRICCIÓN | 1 |
| 9 | RN-C01-09 | Bloqueo Temporal de Cuenta | ACTIVADOR | 1 |
| 10 | RN-C01-10 | Hash Seguro de Passwords | HECHO | 1 |
| 11 | RN-C01-11 | Refresh Token | ACTIVADOR | 2 |
| 12 | RN-C01-12 | Auditoría de Login | ACTIVADOR | 2 |
| 13 | RN-C01-13 | Sesiones en PostgreSQL | HECHO | 1 |
| 14 | RN-C01-14 | Sesión Única por Usuario | RESTRICCIÓN | 1 |

---

## 📖 REGLAS DETALLADAS

---

### **RN-C01-01: Login con Credenciales Locales** 🔴 MUST

**Código:** RN-C01-01
**Tipo:** ACTIVADOR
**Prioridad:** MUST - CRÍTICO
**Sprint:** 1
**UC Relacionado:** UC-001 (Iniciar Sesión)

#### **Descripción**

El sistema debe permitir a los usuarios autenticarse **únicamente** mediante credenciales locales (username/password) almacenadas en la base de datos PostgreSQL del sistema. No se soporta ningún otro método de autenticación.

#### **Restricciones Aplicables**

```yaml
❌ PROHIBIDO:
  - LDAP/Active Directory
  - OAuth2 (Google, Microsoft, GitHub, etc.)
  - SAML
  - Autenticación biométrica
  - Passwordless (Magic links)
  - Validación de IP address
  - Bloqueo por cambio de IP

✅ OBLIGATORIO:
  - Solo autenticación local
  - Credenciales en PostgreSQL
  - Almacenar user_agent (NO validar)
  - Sesión única por usuario
  - Bloqueo tras 3 intentos
```

#### **Disparador**

```
CUANDO usuario envía POST /api/v1/auth/login con credenciales
```

#### **Condiciones de Entrada**

- Username NO debe estar vacío
- Password NO debe estar vacío
- Username debe existir en tabla `users` (PostgreSQL)
- Password debe coincidir con el hash bcrypt almacenado
- Usuario debe estar en estado "ACTIVO" (`status = 'ACTIVO'`)
- Usuario NO debe estar bloqueado (`is_locked = False`)
- Si tiene sesión activa previa, debe cerrarse primero (sesión única)

#### **Lógica de Negocio**

```python
def login(username: str, password: str, request) -> dict:
    """
    Autenticar usuario con credenciales locales

    Args:
        username: Nombre de usuario o email
        password: Contraseña en texto plano
        request: Request HTTP (para user_agent)

    Returns:
        dict con access_token, refresh_token, expires_in

    Raises:
        AuthenticationFailed: Si credenciales inválidas
        UserInactive: Si usuario no está activo
        UserLocked: Si cuenta está bloqueada
    """

    # PASO 1: Validar credenciales (RN-C01-02)
    try:
        user = validate_credentials(username, password)
    except (InvalidCredentials, UserInactive, UserLocked) as e:
        # Incrementar intentos fallidos
        handle_failed_login(username)
        raise e

    # PASO 2: Cerrar sesión previa si existe (sesión única - RN-C01-14)
    active_sessions = UserSession.objects.filter(
        user=user,
        is_active=True
    )

    if active_sessions.exists():
        for session in active_sessions:
            # Cerrar sesión anterior
            session.is_active = False
            session.logged_out_at = now()
            session.logout_reason = 'NEW_SESSION'
            session.save()

            # Cerrar en django_session también
            try:
                DjangoSession.objects.get(
                    session_key=session.session_key
                ).delete()
            except DjangoSession.DoesNotExist:
                pass

            # Auditar cierre
            AuditLog.create(
                event_type='SESSION_CLOSED',
                user_id=user.id,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                details={
                    'reason': 'new_session',
                    'old_session_id': session.session_id
                }
            )

        # Notificar al usuario vía buzón interno (NO email, SIN IP)
        InternalMessage.create(
            user_id=user.id,
            subject='Nueva sesión iniciada',
            body='Se ha iniciado una nueva sesión en tu cuenta.\n\n'
                 'Tu sesión anterior ha sido cerrada automáticamente.\n\n'
                 'Si no fuiste tú quien inició esta sesión, '
                 'por favor cambia tu contraseña inmediatamente.',
            severity='INFO',
            created_by_system=True
        )

    # PASO 3: Crear nueva sesión en PostgreSQL
    session = UserSession.objects.create(
        user=user,
        session_key=request.session.session_key,
        user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown'),  # ✅ Almacenar
        is_active=True,
        created_at=now(),
        last_activity_at=now()
    )

    # PASO 4: Generar tokens JWT (RN-C01-03)
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)

    # Agregar claims personalizados
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['segment'] = user.segment
    refresh['roles'] = list(user.roles.values_list('code', flat=True))

    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # PASO 5: Actualizar datos del usuario
    user.last_login_at = now()
    user.failed_login_attempts = 0  # Resetear contador
    user.last_failed_login_at = None
    user.save()

    # PASO 6: Auditar login exitoso (RN-C01-12)
    AuditLog.create(
        event_type='LOGIN_SUCCESS',
        user_id=user.id,
        user_agent=request.META.get('HTTP_USER_AGENT'),  # ✅ Para auditoría
        details={
            'username': user.username,
            'method': 'local',
            'session_id': session.session_id
        },
        result='SUCCESS'
    )

    # PASO 7: Retornar tokens
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 900  # 15 minutos en segundos
    }
```

#### **Manejo de Errores**

```python
def handle_failed_login(username: str):
    """
    Incrementar intentos fallidos y bloquear si es necesario
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # Usuario no existe, no hacemos nada
        return

    # Incrementar contador (NO se resetea por tiempo)
    user.failed_login_attempts += 1
    user.last_failed_login_at = now()

    # Bloquear si llegó a 3 intentos (RN-C01-08, RN-C01-09)
    if user.failed_login_attempts >= 3:
        user.is_locked = True
        user.locked_until = now() + timedelta(minutes=15)
        user.lock_reason = 'MAX_FAILED_ATTEMPTS'

        # Notificar vía buzón interno (NO email, SIN IP)
        InternalMessage.create(
            user_id=user.id,
            subject='Cuenta bloqueada temporalmente',
            body=f'Tu cuenta ha sido bloqueada por 15 minutos debido a '
                 f'múltiples intentos fallidos de login.\n\n'
                 f'Será desbloqueada automáticamente a las '
                 f'{user.locked_until.strftime("%H:%M:%S")}.\n\n'
                 f'Si no fuiste tú quien intentó acceder, por favor '
                 f'contacta al administrador del sistema inmediatamente.',
            severity='WARNING',
            created_by_system=True
        )

        # Auditar bloqueo
        AuditLog.create(
            event_type='USER_LOCKED',
            user_id=user.id,
            details={
                'reason': 'max_failed_attempts',
                'failed_attempts': 3,
                'locked_until': user.locked_until.isoformat()
            },
            result='FAILURE'
        )

    user.save()
```

#### **Datos de Entrada**

```json
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "juan.perez",
  "password": "SecureP@ss123"
}
```

#### **Datos de Salida (Éxito)**

```json
HTTP 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoianVhbi5wZXJleiIsImVtYWlsIjoianVhbi5wZXJlekBjb21wYW55LmNvbSIsInNlZ21lbnQiOiJHRSIsInJvbGVzIjpbIkFOQUxJU1RBX0RBVE9TIiwiVklFV0VSX0JBU0lDTyJdLCJpYXQiOjE3MzA3MDcyMDAsImV4cCI6MTczMDcwODEwMCwianRpIjoidW5pcXVlLWp3dC1pZCIsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoianVhbi5wZXJleiIsImVtYWlsIjoianVhbi5wZXJlekBjb21wYW55LmNvbSIsInNlZ21lbnQiOiJHRSIsInJvbGVzIjpbIkFOQUxJU1RBX0RBVE9TIiwiVklFV0VSX0JBU0lDTyJdLCJpYXQiOjE3MzA3MDcyMDAsImV4cCI6MTczMTMxMjAwMCwianRpIjoidW5pcXVlLXJlZnJlc2gtaWQiLCJ0b2tlbl90eXBlIjoicmVmcmVzaCJ9.signature",
  "token_type": "Bearer",
  "expires_in": 900
}
```

#### **Datos de Salida (Error)**

```json
// Credenciales inválidas
HTTP 401 Unauthorized
{
  "error": "Credenciales inválidas",
  "attempts_remaining": 2
}

// Usuario bloqueado
HTTP 403 Forbidden
{
  "error": "Cuenta bloqueada",
  "locked_until": "2025-11-04T11:15:00Z",
  "minutes_remaining": 14
}

// Usuario inactivo
HTTP 403 Forbidden
{
  "error": "Usuario inactivo",
  "message": "Contacta al administrador"
}

// Throttling
HTTP 429 Too Many Requests
{
  "error": "Demasiados intentos",
  "retry_after": 300
}
```

#### **Reglas Relacionadas**

- **RN-C01-02:** Validación de Credenciales
- **RN-C01-03:** Generación de Tokens JWT
- **RN-C01-08:** Intentos Fallidos Limitados
- **RN-C01-09:** Bloqueo Temporal
- **RN-C01-12:** Auditoría de Login
- **RN-C01-14:** Sesión Única

#### **Casos de Prueba**

- **TC-AUTH-001:** Login exitoso con credenciales válidas
- **TC-AUTH-002:** Login con credenciales inválidas
- **TC-AUTH-003:** Bloqueo tras 3 intentos fallidos
- **TC-AUTH-009:** Sesión única (cierre de sesión previa)

---

### **RN-C01-02: Validación de Credenciales** 🔴 MUST

**Código:** RN-C01-02
**Tipo:** RESTRICCIÓN
**Prioridad:** MUST - CRÍTICO
**Sprint:** 1

#### **Descripción**

Las credenciales proporcionadas deben ser validadas contra los valores almacenados de forma segura usando **bcrypt**. Solo se validan credenciales locales almacenadas en PostgreSQL.

#### **Restricciones Aplicables**

```yaml
✅ OBLIGATORIO:
  - bcrypt con cost factor 12
  - Solo base de datos local (PostgreSQL)
  - Validar estado del usuario (ACTIVO)
  - Verificar bloqueo de cuenta
  - Desbloqueo automático si tiempo expiró

❌ PROHIBIDO:
  - Validar contra LDAP/AD
  - Validar contra OAuth2
  - Validar contra servicios externos
```

#### **Regla de Negocio**

```
Username debe:
- Existir en tabla users (auth_source='local')
- Estar en formato válido (lowercase, sin espacios)
- NO estar eliminado lógicamente (deleted_at IS NULL)

Password debe:
- Coincidir con hash bcrypt almacenado en password_hash
- Verificarse mediante bcrypt.checkpw()
- Tener longitud entre 8-100 caracteres (validado en RN-C01-07)
```

#### **Algoritmo de Validación**

```python
import bcrypt
from django.utils.timezone import now
from datetime import timedelta

def validate_credentials(username: str, password: str) -> User:
    """
    Validar credenciales locales únicamente

    Args:
        username: Username o email del usuario
        password: Password en texto plano

    Returns:
        User: Objeto usuario si validación exitosa

    Raises:
        InvalidCredentials: Si username no existe o password incorrecto
        UserInactive: Si usuario no está activo
        UserLocked: Si cuenta está bloqueada
    """

    # PASO 1: Buscar usuario por username (o email)
    try:
        user = User.objects.get(
            username=username.lower().strip(),
            auth_source='local',  # SOLO autenticación local
            deleted_at__isnull=True  # No eliminados lógicamente
        )
    except User.DoesNotExist:
        # No revelar si el usuario existe o no (seguridad)
        raise InvalidCredentials('Credenciales inválidas')

    # PASO 2: Verificar que el password_hash existe
    if not user.password_hash:
        raise InvalidCredentials('Usuario sin contraseña configurada')

    # PASO 3: Verificar password con bcrypt
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = user.password_hash.encode('utf-8')

        if not bcrypt.checkpw(password_bytes, hash_bytes):
            raise InvalidCredentials('Contraseña incorrecta')
    except (ValueError, AttributeError) as e:
        # Hash corrupto o inválido
        raise InvalidCredentials('Error al validar contraseña')

    # PASO 4: Verificar estado del usuario
    if user.status != 'ACTIVO':
        if user.status == 'PENDIENTE_CONFIGURACION':
            raise UserInactive(
                'Usuario pendiente de configuración inicial'
            )
        else:
            raise UserInactive(
                'Usuario inactivo. Contacta al administrador.'
            )

    # PASO 5: Verificar bloqueo de cuenta
    if user.is_locked:
        # Verificar si ya pasó el tiempo de bloqueo
        if user.locked_until and now() < user.locked_until:
            # Aún está bloqueado
            tiempo_restante = (user.locked_until - now()).seconds // 60
            raise UserLocked(
                f'Cuenta bloqueada. Tiempo restante: {tiempo_restante} minutos'
            )
        else:
            # Ya pasó el tiempo, desbloquear automáticamente
            user.is_locked = False
            user.locked_until = None
            user.failed_login_attempts = 0
            user.lock_reason = None
            user.save()

            # Auditar desbloqueo automático
            AuditLog.create(
                event_type='USER_UNLOCKED',
                user_id=user.id,
                details={
                    'reason': 'automatic_timeout',
                    'unlocked_at': now().isoformat()
                },
                result='SUCCESS'
            )

    # PASO 6: Validaciones adicionales (opcional)
    # Verificar que la contraseña no esté expirada (futuro)
    # if user.password_expires_at and now() > user.password_expires_at:
    #     raise PasswordExpired('Contraseña expirada')

    # Validación exitosa
    return user
```

#### **Excepciones Personalizadas**

```python
class InvalidCredentials(Exception):
    """Username no existe o password incorrecto"""
    pass

class UserInactive(Exception):
    """Usuario no está en estado ACTIVO"""
    pass

class UserLocked(Exception):
    """Cuenta bloqueada temporalmente"""
    pass
```

#### **Performance**

```yaml
Objetivo: < 500ms por validación
Factores:
  - bcrypt es intencionalmente lento (cost 12)
  - Query a PostgreSQL: ~10-50ms
  - bcrypt.checkpw(): ~300-400ms
  - Total típico: ~350-450ms

Optimizaciones:
  - NO cachear passwords (seguridad)
  - SÍ usar índice en username
  - Cost factor configurable (ajustar en producción si necesario)
```

#### **Seguridad**

```yaml
Fortalezas:
  ✅ bcrypt resistente a rainbow tables
  ✅ Salt único por password
  ✅ Cost factor ajustable (futureproof)
  ✅ Timing attack mitigation (bcrypt constante)
  ✅ No revela si username existe

Consideraciones:
  ⚠️ Mismo mensaje de error para username y password
  ⚠️ No especificar cuál campo es incorrecto
  ⚠️ Rate limiting en endpoint de login (5/5min)
```

#### **Reglas Relacionadas**

- **RN-C01-01:** Login con Credenciales
- **RN-C01-10:** Hash Seguro de Passwords
- **RN-C01-07:** Complejidad de Contraseñas

---

### **RN-C01-03: Generación de Tokens JWT** 🔴 MUST

**Código:** RN-C01-03
**Tipo:** ACTIVADOR
**Prioridad:** MUST - CRÍTICO
**Sprint:** 1

#### **Descripción**

Al autenticarse exitosamente, el sistema genera tokens JWT (JSON Web Tokens) usando **djangorestframework-simplejwt** con las configuraciones específicas del proyecto.

#### **Restricciones Aplicables**

```yaml
✅ OBLIGATORIO:
  - Access token: 15 minutos exactos
  - Refresh token: 7 días exactos
  - Rotate refresh tokens: True
  - Blacklist after rotation: True
  - Algoritmo: HS256
  - Claims personalizados: username, email, segment, roles

❌ PROHIBIDO:
  - Tokens de larga duración
  - Tokens sin expiración
  - Algoritmos inseguros (None, HS1)
  - Secrets hardcodeados
```

#### **Estructura del Access Token**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123,
    "username": "juan.perez",
    "email": "juan.perez@company.com",
    "segment": "GE",
    "roles": ["ANALISTA_DATOS", "VIEWER_BASICO"],
    "iat": 1730707200,
    "exp": 1730708100,
    "jti": "unique-jwt-id-abc123",
    "token_type": "access"
  },
  "signature": "..."
}
```

#### **Estructura del Refresh Token**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123,
    "username": "juan.perez",
    "email": "juan.perez@company.com",
    "segment": "GE",
    "roles": ["ANALISTA_DATOS", "VIEWER_BASICO"],
    "iat": 1730707200,
    "exp": 1731312000,
    "jti": "unique-refresh-id-xyz789",
    "token_type": "refresh"
  },
  "signature": "..."
}
```

#### **Configuración (settings.py)**

```python
from datetime import timedelta

SIMPLE_JWT = {
    # Duración de tokens (RESTRICCIONES)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # 15 min EXACTOS
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 días EXACTOS

    # Seguridad
    'ROTATE_REFRESH_TOKENS': True,     # Generar nuevo refresh al usar
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist refresh viejo
    'UPDATE_LAST_LOGIN': False,        # Lo manejamos manualmente

    # Algoritmo
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Desde variable de entorno
    'VERIFYING_KEY': None,

    # Headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Claims
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    # Token classes
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),

    # Sliding tokens (NO usamos)
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```

#### **Proceso de Generación**

```python
from rest_framework_simplejwt.tokens import RefreshToken

def generate_tokens_for_user(user) -> dict:
    """
    Generar access y refresh tokens para un usuario

    Args:
        user: Objeto User

    Returns:
        dict con 'access' y 'refresh' tokens
    """
    # 1. Crear refresh token
    refresh = RefreshToken.for_user(user)

    # 2. Agregar claims personalizados
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['segment'] = user.segment

    # Obtener roles del usuario (M2M relationship)
    roles = list(user.roles.values_list('code', flat=True))
    refresh['roles'] = roles

    # 3. Access token se genera automáticamente del refresh
    access = refresh.access_token

    # 4. Retornar ambos tokens
    return {
        'access': str(access),
        'refresh': str(refresh)
    }
```

#### **Claims Personalizados**

| Claim | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `user_id` | int | ID del usuario | 123 |
| `username` | string | Nombre de usuario | "juan.perez" |
| `email` | string | Email del usuario | "juan@company.com" |
| `segment` | string | Segmento de datos | "GE", "OP", "FI" |
| `roles` | array | Códigos de roles | ["R009", "R010"] |
| `iat` | int | Issued at (timestamp) | 1730707200 |
| `exp` | int | Expiration (timestamp) | 1730708100 |
| `jti` | string | JWT ID (único) | "abc123..." |
| `token_type` | string | Tipo de token | "access" o "refresh" |

#### **Decodificación (Backend)**

```python
import jwt
from django.conf import settings

def decode_access_token(token: str) -> dict:
    """
    Decodificar y validar access token
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )

        # Validar tipo de token
        if payload.get('token_type') != 'access':
            raise InvalidToken('No es un access token')

        return payload

    except jwt.ExpiredSignatureError:
        raise TokenExpired('Token expirado')
    except jwt.InvalidTokenError as e:
        raise InvalidToken(f'Token inválido: {str(e)}')
```

#### **Validación (Frontend)**

```javascript
// Validar token en frontend (NO verificar firma, solo estructura)
function isTokenExpired(token) {
    try:
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp * 1000; // Convertir a ms
        return Date.now() >= exp;
    } catch (e) {
        return true; // Si hay error, asumir expirado
    }
}

// Refrescar token si está por expirar
if (isTokenExpired(accessToken)) {
    const newTokens = await refreshAccessToken(refreshToken);
    localStorage.setItem('access_token', newTokens.access);
    localStorage.setItem('refresh_token', newTokens.refresh);
}
```

#### **Seguridad del Secret**

```yaml
Secret Key:
  ✅ Mínimo 256 bits (32 caracteres)
  ✅ Desde variable de entorno
  ✅ Nunca en código fuente
  ✅ Único por ambiente (dev/staging/prod)
  ✅ Rotación cada 90 días

Generación segura:
  python -c "import secrets; print(secrets.token_urlsafe(32))"

Variable de entorno:
  export DJANGO_SECRET_KEY="tu-secret-key-super-seguro-aqui"
```

#### **Blacklist de Tokens**

```python
# Al hacer logout o refresh
from rest_framework_simplejwt.tokens import RefreshToken

def blacklist_token(refresh_token_str: str):
    """
    Agregar refresh token a blacklist
    """
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()  # Método de simplejwt
    except Exception as e:
        # Token ya blacklisted o inválido
        pass
```

#### **Tablas de Blacklist (simplejwt)**

```sql
-- Tokens emitidos (outstanding)
CREATE TABLE token_blacklist_outstandingtoken (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    jti VARCHAR(255) UNIQUE NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Tokens blacklisted
CREATE TABLE token_blacklist_blacklistedtoken (
    id SERIAL PRIMARY KEY,
    token_id INTEGER UNIQUE NOT NULL
        REFERENCES token_blacklist_outstandingtoken(id),
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Reglas Relacionadas**

- **RN-C01-01:** Login (genera tokens)
- **RN-C01-04:** Validación de Tokens
- **RN-C01-05:** Logout (blacklist)
- **RN-C01-11:** Refresh Token

---

(Continuación del documento con las reglas RN-C01-04 a RN-C01-14...)

---

**NOTA:** Este documento continúa con las reglas restantes. Las reglas mostradas aquí son las más críticas para el módulo de autenticación.

---

**Fin del extracto - Documento completo: 14 reglas de negocio**
