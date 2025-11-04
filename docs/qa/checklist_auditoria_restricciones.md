---
id: CHECK-AUDIT-REST
tipo: checklist
categoria: qa-auditoria
version: 1.0.0
fecha_creacion: 2025-11-04
propietario: equipo-qa
relacionados: ["PROC-QA", "restricciones_completas.md"]
---
# Checklist de Auditoría de Restricciones - IACT

## Propósito

Este checklist permite auditar el cumplimiento de las restricciones críticas del proyecto IACT. Se basa en los hallazgos de la auditoría real del código en `api/`.

**Última auditoría**: 2025-11-04
**Estado del código**: En desarrollo

---

## 📋 CÓMO USAR ESTE CHECKLIST

### Frecuencia de Auditoría

- **Pre-Deploy a Producción**: OBLIGATORIO
- **Cada Sprint/Release**: RECOMENDADO
- **Después de cambios mayores**: RECOMENDADO
- **Auditoría de seguridad**: TRIMESTRAL

### Niveles de Severidad

- 🔴 **CRÍTICO**: Incumplimiento bloquea deploy a producción
- 🟡 **ALTA**: Debe corregirse antes de release
- 🟢 **MEDIA**: Debe corregirse en próximo sprint
- ⚪ **BAJA**: Mejora recomendada

### Scoring

- ✅ Cumple totalmente (1 punto)
- ⚠️ Cumple parcialmente (0.5 puntos)
- ❌ No cumple (0 puntos)
- N/A No aplica (no cuenta)

**Aprobación mínima**: 90% en ítems CRÍTICOS, 80% en ALTA

---

## 🔴 SECCIÓN 1: RESTRICCIONES CRÍTICAS (NO NEGOCIABLES)

### 1.1 Comunicaciones [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.1.1 | ❌ NO hay imports de `send_mail`, `EmailMessage`, `SMTPConnection` | `grep -r "send_mail\|EmailMessage\|smtp" api/` | ✅ | Sin hallazgos |
| 1.1.2 | ❌ NO hay configuración de EMAIL_* en settings | `grep "EMAIL_BACKEND\|EMAIL_HOST" api/callcentersite/callcentersite/settings/` | ✅ | Sin hallazgos |
| 1.1.3 | ✅ Existe modelo InternalMessage | `api/callcentersite/callcentersite/apps/notifications/models.py` | ✅ | Líneas 10-65 |
| 1.1.4 | ✅ Notificaciones usan InternalMessage | Revisar servicios de notificación | ⚠️ | Pendiente implementar |
| 1.1.5 | ✅ Recuperación de contraseña NO usa email | Revisar views de auth | ⚠️ | Pendiente implementar |

**Score 1.1**: 3/5 (60%) - ⚠️ REQUIERE ATENCIÓN

**Acciones pendientes**:
- [ ] Implementar recuperación de contraseña con preguntas de seguridad
- [ ] Implementar servicio de notificaciones que use InternalMessage

---

### 1.2 Gestión de Sesiones [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.2.1 | ✅ SESSION_ENGINE = 'django.contrib.sessions.backends.db' | `api/callcentersite/callcentersite/settings/base.py` | ⚠️ | Usa default (DB) pero NO explícito |
| 1.2.2 | ❌ NO hay Redis/Memcached en requirements | `api/callcentersite/requirements/base.txt` | ✅ | Sin Redis/Memcached |
| 1.2.3 | ✅ SESSION_COOKIE_AGE = 900 (15 minutos) | `grep SESSION_COOKIE_AGE api/callcentersite/callcentersite/settings/` | ❌ | NO configurado |
| 1.2.4 | ✅ Middleware SessionSecurityMiddleware activo | `api/callcentersite/callcentersite/settings/base.py:52` | ✅ | Verifica IP + User-Agent |
| 1.2.5 | ✅ Sesiones verifican IP y User-Agent | `api/callcentersite/callcentersite/middleware/session_security.py:45-48` | ✅ | Implementado |
| 1.2.6 | ✅ Una sesión por usuario (cierra previas) | Revisar lógica de login | ⚠️ | Pendiente verificar |

**Score 1.2**: 3.5/6 (58%) - ⚠️ REQUIERE ATENCIÓN

**Acciones pendientes**:
- [ ] Agregar `SESSION_ENGINE = 'django.contrib.sessions.backends.db'` explícitamente en base.py
- [ ] Agregar `SESSION_COOKIE_AGE = 900` en base.py
- [ ] Implementar cierre de sesiones previas en login

---

### 1.3 Base de Datos Dual [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.3.1 | ✅ BD 'default' configurada (PostgreSQL) | `api/callcentersite/callcentersite/settings/base.py:80-92` | ✅ | PostgreSQL |
| 1.3.2 | ✅ BD 'ivr_readonly' configurada (MySQL) | `api/callcentersite/callcentersite/settings/base.py:93-106` | ✅ | MySQL |
| 1.3.3 | ✅ DATABASE_ROUTERS incluye IVRReadOnlyRouter | `api/callcentersite/callcentersite/settings/base.py:108` | ✅ | Configurado |
| 1.3.4 | ✅ Router protege BD IVR (raise error en write) | `api/callcentersite/callcentersite/database_router.py:23-27` | ✅ | ValueError en write |
| 1.3.5 | ✅ Router permite migraciones solo en 'default' | `api/callcentersite/callcentersite/database_router.py:39-43` | ✅ | Implementado |
| 1.3.6 | ✅ Usuario BD IVR es readonly | Verificar con DBA | ⚠️ | Pendiente validar en producción |

**Score 1.3**: 5.5/6 (92%) - ✅ APROBADO

**Acciones pendientes**:
- [ ] Validar con DBA que usuario de BD IVR solo tiene permisos SELECT

---

### 1.4 Actualización de Datos [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.4.1 | ❌ NO hay WebSockets | `grep -r "websocket\|channels" api/` | ✅ | Sin hallazgos |
| 1.4.2 | ❌ NO hay SSE (Server-Sent Events) | `grep -r "text/event-stream\|EventSource" api/` | ✅ | Sin hallazgos |
| 1.4.3 | ✅ ETL configurado con APScheduler | `api/callcentersite/requirements/base.txt:44` | ✅ | APScheduler>=3.10.4 |
| 1.4.4 | ✅ ETL_FREQUENCY_HOURS configurable (6-12h) | `api/callcentersite/callcentersite/settings/base.py:143` | ✅ | Default 6 horas |
| 1.4.5 | ✅ Dashboard NO tiene auto-refresh | Revisar frontend/dashboard views | ⚠️ | Pendiente verificar frontend |

**Score 1.4**: 4.5/5 (90%) - ✅ APROBADO

---

### 1.5 Sentry [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.5.1 | ❌ NO hay sentry-sdk en requirements | `grep -i sentry api/callcentersite/requirements/` | ✅ | Sin Sentry |
| 1.5.2 | ❌ NO hay imports de sentry_sdk | `grep -r "sentry" api/` | ✅ | Sin hallazgos |
| 1.5.3 | ❌ NO hay SENTRY_DSN en settings | `grep SENTRY api/callcentersite/callcentersite/settings/` | ✅ | Sin configuración |

**Score 1.5**: 3/3 (100%) - ✅ APROBADO

---

## 🔐 SECCIÓN 2: SEGURIDAD DJANGO/DRF

### 2.1 Configuración Base [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.1.1 | ✅ DEBUG = False en producción | `api/callcentersite/callcentersite/settings/production.py:5` | ✅ | Configurado |
| 2.1.2 | ✅ SECRET_KEY desde env variable | `api/callcentersite/callcentersite/settings/base.py:13` | ✅ | os.getenv("DJANGO_SECRET_KEY") |
| 2.1.3 | ✅ ALLOWED_HOSTS desde env | `api/callcentersite/callcentersite/settings/base.py:16-20` | ✅ | Configurable |
| 2.1.4 | ✅ SECURE_SSL_REDIRECT = True | `grep SECURE_SSL_REDIRECT api/callcentersite/callcentersite/settings/production.py` | ❌ | NO configurado |
| 2.1.5 | ✅ SESSION_COOKIE_SECURE = True | `api/callcentersite/callcentersite/settings/production.py:36` | ✅ | Configurado |
| 2.1.6 | ✅ CSRF_COOKIE_SECURE = True | `api/callcentersite/callcentersite/settings/production.py:37` | ✅ | Configurado |
| 2.1.7 | ✅ SECURE_HSTS_SECONDS = 31536000 | `api/callcentersite/callcentersite/settings/production.py:33` | ✅ | Configurado |

**Score 2.1**: 6/7 (86%) - ✅ APROBADO

**Acciones pendientes**:
- [ ] Agregar `SECURE_SSL_REDIRECT = True` en production.py

---

### 2.2 Headers de Seguridad [ALTA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.2.1 | ✅ X-Content-Type-Options: nosniff | `grep X_CONTENT_TYPE_OPTIONS api/callcentersite/callcentersite/settings/` | ❌ | NO configurado |
| 2.2.2 | ✅ X-Frame-Options: DENY | `grep X_FRAME_OPTIONS api/callcentersite/callcentersite/settings/` | ❌ | NO configurado |
| 2.2.3 | ✅ X-XSS-Protection | `grep X_XSS_PROTECTION api/callcentersite/callcentersite/settings/` | ❌ | NO configurado |
| 2.2.4 | ✅ Strict-Transport-Security | SECURE_HSTS_SECONDS configurado | ✅ | Via HSTS settings |

**Score 2.2**: 1/4 (25%) - ❌ REQUIERE CORRECCIÓN

**Acciones pendientes**:
- [ ] Agregar `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] Agregar `X_FRAME_OPTIONS = 'DENY'`
- [ ] Agregar `SECURE_BROWSER_XSS_FILTER = True`

---

### 2.3 Autenticación JWT [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.3.1 | ✅ ACCESS_TOKEN_LIFETIME = 15 min | `api/callcentersite/callcentersite/settings/base.py:132` | ✅ | timedelta(minutes=15) |
| 2.3.2 | ✅ REFRESH_TOKEN_LIFETIME = 7 días | `api/callcentersite/callcentersite/settings/base.py:133` | ✅ | timedelta(days=7) |
| 2.3.3 | ✅ ROTATE_REFRESH_TOKENS = True | `api/callcentersite/callcentersite/settings/base.py:134` | ✅ | Configurado |
| 2.3.4 | ✅ BLACKLIST_AFTER_ROTATION = True | `api/callcentersite/callcentersite/settings/base.py:135` | ✅ | Configurado |
| 2.3.5 | ✅ rest_framework_simplejwt.token_blacklist en INSTALLED_APPS | `api/callcentersite/callcentersite/settings/base.py:31` | ✅ | Instalado |

**Score 2.3**: 5/5 (100%) - ✅ APROBADO

---

### 2.4 Permisos y Throttling [ALTA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.4.1 | ✅ DEFAULT_PERMISSION_CLASSES = [IsAuthenticated] | `api/callcentersite/callcentersite/settings/base.py:121` | ✅ | Configurado |
| 2.4.2 | ✅ DEFAULT_THROTTLE_CLASSES configurado | `grep DEFAULT_THROTTLE_CLASSES api/callcentersite/callcentersite/settings/base.py` | ❌ | NO configurado |
| 2.4.3 | ✅ DEFAULT_THROTTLE_RATES configurado | `grep DEFAULT_THROTTLE_RATES api/callcentersite/callcentersite/settings/base.py` | ❌ | NO configurado |
| 2.4.4 | ❌ NO hay AllowAny en endpoints sensibles | Revisar views (excepto login/public) | ⚠️ | Solo en testing.py |
| 2.4.5 | ✅ Permisos personalizados por endpoint | Revisar views | ⚠️ | Pendiente verificar |

**Score 2.4**: 2.5/5 (50%) - ⚠️ REQUIERE ATENCIÓN

**Acciones pendientes**:
- [ ] Agregar throttling en REST_FRAMEWORK settings:
  ```python
  'DEFAULT_THROTTLE_CLASSES': [
      'rest_framework.throttling.AnonRateThrottle',
      'rest_framework.throttling.UserRateThrottle'
  ],
  'DEFAULT_THROTTLE_RATES': {
      'anon': '100/hour',
      'user': '10000/day'
  }
  ```

---

### 2.5 Paginación [ALTA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.5.1 | ✅ DEFAULT_PAGINATION_CLASS configurado | `api/callcentersite/callcentersite/settings/base.py:125` | ✅ | PageNumberPagination |
| 2.5.2 | ✅ PAGE_SIZE = 50 | `api/callcentersite/callcentersite/settings/base.py:126` | ✅ | Configurado |
| 2.5.3 | ✅ MAX_PAGE_SIZE configurado | `grep MAX_PAGE_SIZE api/callcentersite/callcentersite/settings/base.py` | ❌ | NO configurado |

**Score 2.5**: 2/3 (67%) - ⚠️ REQUIERE ATENCIÓN

**Acciones pendientes**:
- [ ] Agregar paginación personalizada con MAX_PAGE_SIZE = 1000

---

### 2.6 Prevención de Vulnerabilidades [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.6.1 | ❌ NO hay eval() | `grep -r "eval(" api/callcentersite` | ✅ | Sin hallazgos |
| 2.6.2 | ❌ NO hay exec() | `grep -r "exec(" api/callcentersite` | ✅ | Sin hallazgos |
| 2.6.3 | ❌ NO hay pickle.load() sin validación | `grep -r "pickle.load" api/callcentersite` | ✅ | Sin hallazgos |
| 2.6.4 | ❌ NO hay yaml.load() (usar safe_load) | `grep -r "yaml.load(" api/callcentersite` | ✅ | Sin hallazgos |
| 2.6.5 | ❌ NO hay SQL raw con concatenación | Revisar queries | ⚠️ | Pendiente auditoría manual |
| 2.6.6 | ❌ NO hay extra() con input de usuario | `grep -r "\.extra(" api/callcentersite` | ⚠️ | Pendiente verificar |

**Score 2.6**: 4/6 (67%) - ⚠️ REQUIERE AUDITORÍA MANUAL

---

### 2.7 CORS [MEDIA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 2.7.1 | ✅ django-cors-headers en requirements | `api/callcentersite/requirements/base.txt:37` | ✅ | Instalado |
| 2.7.2 | ✅ corsheaders en INSTALLED_APPS | `grep cors api/callcentersite/callcentersite/settings/base.py` | ❌ | NO agregado |
| 2.7.3 | ✅ CorsMiddleware en MIDDLEWARE | `grep -i cors api/callcentersite/callcentersite/settings/base.py` | ❌ | NO agregado |
| 2.7.4 | ✅ CORS_ALLOWED_ORIGINS configurado | `grep CORS_ api/callcentersite/callcentersite/settings/` | ❌ | NO configurado |

**Score 2.7**: 1/4 (25%) - ❌ REQUIERE CORRECCIÓN

**Acciones pendientes**:
- [ ] Agregar 'corsheaders' a INSTALLED_APPS
- [ ] Agregar 'corsheaders.middleware.CorsMiddleware' a MIDDLEWARE (después de SecurityMiddleware)
- [ ] Configurar CORS_ALLOWED_ORIGINS con dominios específicos

---

## 💾 SECCIÓN 3: BASE DE DATOS Y MODELOS

### 3.1 Eliminación Lógica [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 3.1.1 | ✅ User tiene is_deleted | `api/callcentersite/callcentersite/apps/users/models.py:188` | ✅ | Campo booleano |
| 3.1.2 | ✅ User tiene deleted_at | `api/callcentersite/callcentersite/apps/users/models.py:189` | ✅ | Campo datetime |
| 3.1.3 | ✅ User tiene método mark_deleted() | `api/callcentersite/callcentersite/apps/users/models.py:210-214` | ✅ | Implementado |
| 3.1.4 | ❌ NO hay .delete() en modelos principales | Revisar código | ⚠️ | Pendiente auditoría manual |

**Score 3.1**: 3/4 (75%) - ⚠️ REQUIERE AUDITORÍA

---

### 3.2 Auditoría [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 3.2.1 | ✅ Modelo AuditLog existe | `api/callcentersite/callcentersite/apps/audit/models.py:9` | ✅ | Implementado |
| 3.2.2 | ✅ AuditLog es inmutable | `api/callcentersite/callcentersite/apps/audit/models.py:34-37` | ✅ | raise RuntimeError |
| 3.2.3 | ✅ AuditLog registra usuario | `api/callcentersite/callcentersite/apps/audit/models.py:12-14` | ✅ | ForeignKey |
| 3.2.4 | ✅ AuditLog registra IP | `api/callcentersite/callcentersite/apps/audit/models.py:18` | ✅ | GenericIPAddressField |
| 3.2.5 | ✅ AuditLog registra User-Agent | `api/callcentersite/callcentersite/apps/audit/models.py:19` | ✅ | TextField |
| 3.2.6 | ✅ AuditLog registra valores antes/después | `api/callcentersite/callcentersite/apps/audit/models.py:21-22` | ✅ | JSONField |

**Score 3.2**: 6/6 (100%) - ✅ APROBADO

---

## 🏗️ SECCIÓN 4: ARQUITECTURA Y ANTIPATRONES

### 4.1 Antipatrones Prohibidos [ALTA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 4.1.1 | ❌ NO hay Lava Flow (métodos pass sin implementar) | `grep -r "def.*:.*pass$" api/callcentersite` | ✅ | Sin hallazgos |
| 4.1.2 | ❌ NO hay God Objects (clases >500 líneas) | Revisar tamaño de clases | ⚠️ | Pendiente análisis |
| 4.1.3 | ❌ NO hay Magic Numbers/Strings | Buscar literales hardcodeados | ⚠️ | Pendiente análisis |
| 4.1.4 | ❌ NO hay Circular Dependencies | `python -m pydeps api/callcentersite` | ⚠️ | Pendiente verificar |

**Score 4.1**: 1/4 (25%) - ⚠️ REQUIERE ANÁLISIS

---

## 📦 SECCIÓN 5: DEPENDENCIAS Y SEGURIDAD

### 5.1 Dependencias [ALTA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 5.1.1 | ✅ requirements.txt con versiones exactas | `api/callcentersite/requirements/base.txt` | ❌ | Usa rangos (>=) |
| 5.1.2 | ✅ Dependencias con hashes (--hash) | Verificar formato | ❌ | Sin hashes |
| 5.1.3 | ❌ NO hay Sentry | `grep sentry api/callcentersite/requirements/` | ✅ | Sin Sentry |
| 5.1.4 | ✅ SBOM generado | Buscar archivos .json/.xml | ❌ | Pendiente generar |

**Score 5.1**: 1.5/4 (38%) - ❌ REQUIERE CORRECCIÓN

**Acciones pendientes**:
- [ ] Generar requirements.txt con versiones exactas: `pip freeze > requirements-lock.txt`
- [ ] Agregar hashes: `pip-compile --generate-hashes`
- [ ] Generar SBOM: `cyclonedx-py requirements -o sbom.json`

---

### 5.2 Escaneo de Seguridad [CRÍTICO]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 5.2.1 | ✅ Bandit configurado | `api/callcentersite/pyproject.toml:179-188` | ✅ | Configurado |
| 5.2.2 | ✅ Ruff con reglas de seguridad (S) | `api/callcentersite/pyproject.toml:46` | ✅ | Activado |
| 5.2.3 | ✅ MyPy configurado | `api/callcentersite/pyproject.toml:140-166` | ✅ | Configurado |
| 5.2.4 | ✅ safety check ejecutado | Ejecutar `safety check` | ⚠️ | Pendiente ejecutar |
| 5.2.5 | ✅ Sin CVE High/Critical | Resultados de safety | ⚠️ | Pendiente verificar |

**Score 5.2**: 3/5 (60%) - ⚠️ REQUIERE EJECUCIÓN

---

## 📊 SECCIÓN 6: CALIDAD DE CÓDIGO

### 6.1 Herramientas [MEDIA]

| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 6.1.1 | ✅ Black configurado | `api/callcentersite/pyproject.toml:114-131` | ✅ | Configurado |
| 6.1.2 | ✅ Ruff configurado | `api/callcentersite/pyproject.toml:21-112` | ✅ | Configurado |
| 6.1.3 | ✅ isort configurado | `api/callcentersite/pyproject.toml:133-138` | ✅ | Configurado |
| 6.1.4 | ✅ Pytest configurado | `api/callcentersite/pyproject.toml:200-204` | ✅ | Configurado |
| 6.1.5 | ✅ Coverage configurado | `api/callcentersite/pyproject.toml:206-229` | ✅ | Configurado |

**Score 6.1**: 5/5 (100%) - ✅ APROBADO

---

## 📝 RESUMEN EJECUTIVO

### Scores por Sección

| Sección | Score | Estado | Prioridad |
|---------|-------|--------|-----------|
| 1. Restricciones Críticas | 70% | ⚠️ ATENCIÓN | 🔴 CRÍTICO |
| 2. Seguridad Django/DRF | 65% | ⚠️ ATENCIÓN | 🔴 CRÍTICO |
| 3. Base de Datos y Modelos | 88% | ✅ APROBADO | 🔴 CRÍTICO |
| 4. Arquitectura y Antipatrones | 25% | ❌ REQUIERE ANÁLISIS | 🟡 ALTA |
| 5. Dependencias y Seguridad | 49% | ❌ REQUIERE CORRECCIÓN | 🟡 ALTA |
| 6. Calidad de Código | 100% | ✅ APROBADO | 🟢 MEDIA |

### Score Global: **66%** - ⚠️ REQUIERE MEJORAS ANTES DE PRODUCCIÓN

---

## 🚨 BLOQUEADORES PARA PRODUCCIÓN

Los siguientes ítems DEBEN corregirse antes de deploy a producción:

### Críticos (Bloquean Deploy)

1. **SESSION_ENGINE no explícito** - Agregar configuración explícita
2. **SESSION_COOKIE_AGE no configurado** - Agregar timeout de 15 minutos
3. **Throttling no configurado** - Agregar rate limiting
4. **Headers de seguridad faltantes** - Agregar X-Content-Type-Options, X-Frame-Options
5. **CORS no configurado** - Configurar CORS correctamente
6. **Dependencias sin versiones exactas** - Generar lock file

### Altos (Deben corregirse en Sprint)

7. **SECURE_SSL_REDIRECT no configurado** - Forzar HTTPS
8. **MAX_PAGE_SIZE no limitado** - Prevenir queries masivas
9. **SBOM no generado** - Requerido para auditoría
10. **Recuperación de contraseña pendiente** - Implementar con preguntas de seguridad

---

## 📋 PLAN DE ACCIÓN SUGERIDO

### Sprint 1 (Bloqueadores Críticos)

**Semana 1:**
- [ ] Agregar configuración explícita de sesiones en base.py
- [ ] Configurar throttling en REST_FRAMEWORK
- [ ] Agregar headers de seguridad faltantes
- [ ] Configurar CORS correctamente

**Semana 2:**
- [ ] Generar requirements con versiones exactas y hashes
- [ ] Ejecutar safety check y corregir CVEs
- [ ] Generar SBOM con CycloneDX
- [ ] Agregar SECURE_SSL_REDIRECT

### Sprint 2 (Implementaciones Pendientes)

**Semana 3:**
- [ ] Implementar recuperación de contraseña con preguntas de seguridad
- [ ] Implementar servicio de notificaciones con InternalMessage
- [ ] Implementar cierre de sesiones previas en login

**Semana 4:**
- [ ] Auditoría manual de queries SQL
- [ ] Análisis de antipatrones con herramientas
- [ ] Revisión de eliminación lógica en todos los modelos

---

## 🔧 SCRIPTS DE VALIDACIÓN AUTOMATIZADOS

### Script 1: Verificar Restricciones Críticas

```bash
#!/bin/bash
# scripts/validate_critical_restrictions.sh

echo "🔍 Validando restricciones críticas..."

# 1. Verificar NO email
echo "1. Verificando NO email..."
if grep -r "send_mail\|EmailMessage\|smtp" api/ --include="*.py" | grep -v "test"; then
    echo "❌ FALLO: Se encontró uso de email"
    exit 1
fi
echo "✅ OK: Sin email"

# 2. Verificar NO Sentry
echo "2. Verificando NO Sentry..."
if grep -ri "sentry" api/callcentersite/requirements/; then
    echo "❌ FALLO: Sentry encontrado en requirements"
    exit 1
fi
echo "✅ OK: Sin Sentry"

# 3. Verificar NO Redis para sesiones
echo "3. Verificando NO Redis..."
if grep -ri "redis\|memcached" api/callcentersite/requirements/; then
    echo "❌ FALLO: Redis/Memcached encontrado"
    exit 1
fi
echo "✅ OK: Sin Redis/Memcached"

# 4. Verificar NO eval/exec/pickle
echo "4. Verificando NO eval/exec/pickle..."
if grep -r "eval(\|exec(\|pickle.load" api/callcentersite --include="*.py" | grep -v "test"; then
    echo "❌ FALLO: Código peligroso encontrado"
    exit 1
fi
echo "✅ OK: Sin código peligroso"

echo ""
echo "✅ TODAS LAS RESTRICCIONES CRÍTICAS PASARON"
```

### Script 2: Verificar Configuración de Seguridad

```bash
#!/bin/bash
# scripts/validate_security_config.sh

echo "🔒 Validando configuración de seguridad..."

cd api/callcentersite

# 1. Django check --deploy
echo "1. Ejecutando Django check --deploy..."
python manage.py check --deploy --settings=callcentersite.settings.production
if [ $? -ne 0 ]; then
    echo "❌ FALLO: Django check --deploy"
    exit 1
fi
echo "✅ OK: Django check passed"

# 2. Bandit
echo "2. Ejecutando Bandit..."
bandit -r callcentersite/ -f json -o bandit-report.json
if [ $? -ne 0 ]; then
    echo "❌ FALLO: Bandit encontró problemas"
    exit 1
fi
echo "✅ OK: Bandit passed"

# 3. Safety
echo "3. Ejecutando Safety check..."
safety check --json --output safety-report.json
if [ $? -ne 0 ]; then
    echo "⚠️  WARNING: Safety encontró vulnerabilidades"
fi

# 4. Ruff
echo "4. Ejecutando Ruff..."
ruff check .
if [ $? -ne 0 ]; then
    echo "❌ FALLO: Ruff encontró problemas"
    exit 1
fi
echo "✅ OK: Ruff passed"

echo ""
echo "✅ VALIDACIÓN DE SEGURIDAD COMPLETADA"
```

### Script 3: Verificar Database Router

```bash
#!/bin/bash
# scripts/validate_database_router.sh

echo "💾 Validando protección de BD IVR..."

cd api/callcentersite

# Test que intenta escribir a BD IVR
python -c "
from django.conf import settings
import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'callcentersite.settings.development'
django.setup()

from callcentersite.database_router import IVRReadOnlyRouter

router = IVRReadOnlyRouter()

# Mock model
class MockMeta:
    app_label = 'ivr_legacy'
    label = 'ivr_legacy.TestModel'

class MockModel:
    _meta = MockMeta()

try:
    result = router.db_for_write(MockModel())
    print('❌ FALLO: Router permitió escritura a BD IVR')
    exit(1)
except ValueError as e:
    if 'READ-ONLY' in str(e):
        print('✅ OK: Router bloquea escritura a BD IVR')
        exit(0)
    else:
        print(f'❌ FALLO: Error inesperado: {e}')
        exit(1)
"
```

---

## 📚 RECURSOS Y REFERENCIAS

### Documentos Relacionados

- [Restricciones Completas](../requisitos/restricciones_completas.md)
- [Procedimiento QA](../gobernanza/procesos/procedimiento_qa.md)
- [DRF Secure Code Checklist](https://github.com/Tauseef-Hilal/DRF-Secure-Code-Checklist)

### Herramientas Recomendadas

- **Bandit**: https://bandit.readthedocs.io/
- **Safety**: https://pyup.io/safety/
- **Ruff**: https://docs.astral.sh/ruff/
- **CycloneDX**: https://cyclonedx.org/
- **Django Check**: https://docs.djangoproject.com/en/stable/ref/django-admin/#check

---

## 📝 HISTORIAL DE AUDITORÍAS

| Fecha | Auditor | Score Global | Estado | Notas |
|-------|---------|--------------|--------|-------|
| 2025-11-04 | Claude Agent | 66% | ⚠️ Requiere mejoras | Primera auditoría completa |

---

## ✅ FIRMA DE APROBACIÓN

**Para producción, este checklist requiere**:

- [ ] Score global >= 90%
- [ ] Todos los ítems CRÍTICOS al 100%
- [ ] Todos los ítems ALTA >= 80%
- [ ] Firma de QA Lead
- [ ] Firma de Security Lead
- [ ] Firma de Tech Lead

**Aprobado por**:

- QA Lead: _________________ Fecha: _______
- Security Lead: _________________ Fecha: _______
- Tech Lead: _________________ Fecha: _______

---

**Última actualización**: 2025-11-04
**Próxima auditoría**: Antes de deploy a producción
