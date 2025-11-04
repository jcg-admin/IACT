---
id: DOC-RESTRICCIONES-MAESTRO
tipo: restricciones
titulo: Documento Maestro de Restricciones y Lineamientos
version: 1.0.0
fecha_creacion: 2025-10-21
ultima_actualizacion: 2025-11-04
dominio: global
owner: equipo-arquitectura
estado: definitivo
---

## Documento Maestro de Restricciones y Lineamientos

---

## 📋 INFORMACIÓN DEL DOCUMENTO

|Atributo|Valor|
|---|---|
|**Versión**|1.0.0 - DEFINITIVA|
|**Fecha**|21 Octubre 2025|
|**Proyecto**|Sistema IACT - IVR Analytics & Customer Tracking|
|**Propósito**|Consolidar TODAS las restricciones del proyecto|
|**Audiencia**|Equipo técnico, arquitectos, desarrolladores|

---

## 🎯 CATEGORÍAS DE RESTRICCIONES

1. **Restricciones Técnicas Críticas** (No negociables)
2. **Restricciones de Seguridad** (DRF Secure Code)
3. **Restricciones de Arquitectura** (Patrones y antipatrones)
4. **Restricciones de Base de Datos** (Dual BD)
5. **Restricciones Funcionales** (SRS v2.0)
6. **Restricciones de Performance** (SLA)
7. **Restricciones de Infraestructura** (Deployment)
8. **Restricciones de Desarrollo** (Coding standards)

---

## 🔴 1. RESTRICCIONES TÉCNICAS CRÍTICAS (NO NEGOCIABLES)

### 1.1 Comunicaciones

```yaml
❌ PROHIBIDO ABSOLUTO:
  - Envío de correos electrónicos
  - SMTP/SendGrid/Mailgun/cualquier servicio de email
  - Templates de email
  - Recuperación de contraseña por email
  - Notificaciones por email
  - Alertas por email

✅ OBLIGATORIO:
  - Todas las notificaciones vía buzón interno
  - Modelo InternalMessage
  - UC-037: Sistema de mensajería interno completo
  - Recuperación de contraseña solo con 3 preguntas de seguridad
```

**Justificación:** Restricción de negocio del cliente

**Aplicable a:**

- UC-003: Recuperar Contraseña
- UC-037: Recibir Notificación
- UC-036 a UC-040: Sistema de Alertas
- Todos los módulos que requieran notificar usuarios

---

### 1.2 Gestión de Sesiones

```yaml
❌ PROHIBIDO:
  - Redis para sesiones
  - Memcached para sesiones
  - Sesiones en memoria sin respaldo
  - Cualquier backend volátil

✅ OBLIGATORIO:
  - Sesiones en base de datos MySQL
  - Tabla: user_sessions
  - SESSION_ENGINE = 'django.contrib.sessions.backends.db'
  - Timeout: 15 minutos exactos
  - Sesión única por usuario (cerrar previas automáticamente)

⚠️ VALIDACIONES:
  - Verificar IP + User-Agent en cada request
  - Cerrar sesión automática por inactividad
  - Bloquear si cambio de IP sospechoso
```

**Justificación:** Infraestructura del cliente no tiene Redis

**Aplicable a:**

- UC-001: Iniciar Sesión
- UC-002: Cerrar Sesión
- UC-005: Gestión de Sesiones
- Middleware de autenticación

---

### 1.3 Base de Datos Dual

```yaml
❌ PROHIBIDO EN BD IVR:
  - Permisos INSERT
  - Permisos UPDATE
  - Permisos DELETE
  - Permisos CREATE TABLE
  - Permisos ALTER TABLE
  - Cualquier operación de escritura
  - Conexión con usuario con privilegios

✅ OBLIGATORIO:
  - Usuario con permisos SELECT únicamente
  - Conexión 'ivr_readonly' en settings
  - ETL solo lectura de datos
  - Zero impacto en operación IVR 24/7

✅ BD ANALYTICS (Write):
  - Permisos completos
  - Modelos Django
  - Migraciones permitidas
  - Conexión 'default'

⚠️ CRÍTICO:
  - Protección absoluta de BD IVR
  - Cualquier escritura accidental = incidente mayor
```

**Justificación:** BD IVR en producción 24/7, no se puede afectar

**Aplicable a:**

- ETL Service completo
- Adaptadores de BD Legacy
- Queries de reportes
- Todo acceso a datos del IVR

---

### 1.4 Actualización de Datos

```yaml
❌ PROHIBIDO:
  - Real-time updates
  - WebSockets
  - Server-Sent Events (SSE)
  - Polling automático
  - Push notifications
  - Auto-refresh de dashboard

✅ OBLIGATORIO:
  - Dashboard actualizado según frecuencia ETL (6-12 horas)
  - Usuario debe refrescar manualmente (F5)
  - Mostrar "Última actualización: timestamp"
  - Mostrar "Próxima actualización: timestamp"

📊 FRECUENCIA ETL:
  - Configurable: 6-12 horas
  - No menor a 6 horas
  - Ejecutado por APScheduler
```

**Justificación:** Arquitectura simplificada sin real-time

**Aplicable a:**

- UC-025: Dashboard Principal
- Todos los widgets
- Gráficos y visualizaciones
- Métricas en tiempo real (no existen)

---

## 🔐 2. RESTRICCIONES DE SEGURIDAD (DRF SECURE CODE)

### 2.1 Configuración Django/DRF

```yaml
✅ OBLIGATORIO EN PRODUCCIÓN:
  DEBUG = False
  SECRET_KEY desde variables de entorno
  ALLOWED_HOSTS explícitamente definidos
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_HSTS_SECONDS = 31536000  # 1 año

✅ MIDDLEWARE REQUERIDO:
  - SecurityMiddleware (primero)
  - SessionMiddleware
  - CsrfViewMiddleware
  - AuthenticationMiddleware
  - django-cors-headers.CorsMiddleware

✅ HEADERS DE SEGURIDAD:
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000
```

**Checklist:** Sección 1 - Configuración y Seguridad del Framework

---

### 2.2 Autenticación y Autorización

```yaml
❌ PROHIBIDO:
  - AllowAny en endpoints sensibles
  - Autenticación básica (Basic Auth)
  - Contraseñas en plain text
  - Tokens sin expiración

✅ OBLIGATORIO:
  - JWT con djangorestframework-simplejwt
  - Access token: 15 minutos
  - Refresh token: 7 días
  - Rotate refresh tokens: True
  - Blacklist after rotation: True

✅ PERMISOS:
  - DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]
  - Permisos personalizados por endpoint
  - check_object_permissions() siempre que aplique
  - Precedencia: Directo > Rol > Segmento

✅ THROTTLING OBLIGATORIO:
  - AnonRateThrottle: 100/hour
  - UserRateThrottle: 10000/day
  - ScopedRateThrottle por endpoint crítico
  - Login: 5 intentos/5 minutos por IP
```

**Checklist:** Sección 2 - Autenticación, Autorización y Throttling

---

### 2.3 Serializers y Exposición de Datos

```yaml
❌ PROHIBIDO:
  - fields = '__all__'
  - exclude = [...]
  - Exponer contraseñas/tokens
  - Exponer PII sin justificación
  - Serializers sin validación

✅ OBLIGATORIO:
  - fields explícitos y mínimos
  - read_only_fields para campos sensibles
  - write_only_fields para contraseñas
  - Métodos validate_field() para validaciones
  - Enmascarar PII cuando sea necesario

✅ PAGINACIÓN:
  - DEFAULT_PAGINATION_CLASS obligatorio
  - PAGE_SIZE = 50 (default)
  - MAX_PAGE_SIZE = 1000
  - Cursor pagination para datasets grandes
```

**Checklist:** Sección 3 - Serializers y Exposición de Datos

---

### 2.4 Prevención de Vulnerabilidades

```yaml
❌ PROHIBIDO ABSOLUTAMENTE:
  - eval()
  - exec()
  - pickle.load() sin validación
  - yaml.load() (usar yaml.safe_load())
  - raw SQL con concatenación
  - extra() con input del usuario
  - cursor.execute() con f-strings

✅ OBLIGATORIO:
  - Queries parametrizadas siempre
  - Django ORM para consultas
  - URLValidator para URLs externas
  - Allowlist para dominios permitidos
  - Validación de tipos MIME en uploads
  - Content-Type verification en uploads

⚠️ VALIDACIONES UPLOAD:
  - MAX_UPLOAD_SIZE configurado
  - Extensiones permitidas (allowlist)
  - Verificar magic bytes del archivo
  - Escaneo antivirus si aplica
```

**Checklist:** Sección 4 - Entrada de Datos y Prevención de Vulnerabilidades

---

### 2.5 Dependencias y SBOM

```yaml
✅ OBLIGATORIO:
  - SBOM generado en cada release (CycloneDX/SPDX)
  - Escaneo con safety check / pip-audit
  - Sin CVE High/Critical en producción
  - Dependencias bloqueadas con hashes
  - requirements.txt con versiones exactas

✅ CI/CD:
  - safety check en cada PR
  - Bandit (SAST) en cada PR
  - Semgrep con reglas DRF
  - python manage.py check --deploy

❌ PROHIBIDO:
  - Dependency confusion
  - Instalar desde PyPI público sin validación
  - Versiones con rangos (~=, >=)
```

**Checklist:** Sección 5 - Dependencias y Cadena de Suministro

---

## 🏗️ 3. RESTRICCIONES DE ARQUITECTURA

### 3.1 Antipatrones Prohibidos

```yaml
❌ 1. LAVA FLOW:
  - No métodos pass sin implementación
  - No código muerto en producción
  - Eliminar o implementar completamente

❌ 2. GOD OBJECT:
  - Clases con máximo 5 responsabilidades
  - Separar lógica de negocio de infraestructura
  - Single Responsibility Principle

❌ 3. SEQUENTIAL COUPLING:
  - APIs sin orden obligatorio de llamadas
  - Fail fast en constructores
  - Validaciones en entrada

❌ 4. POLTERGEIST:
  - Clases deben agregar valor, no solo delegar
  - Eliminar capas innecesarias

❌ 5. SHOTGUN SURGERY:
  - Cambios deben ser locales
  - Configuración centralizada
  - Open/Closed Principle

❌ 6. CIRCULAR DEPENDENCY:
  - Sin ciclos en imports
  - Dependency Injection
  - Django Signals para desacoplar

❌ 7. MAGIC NUMBERS/STRINGS:
  - Constantes en constants.py
  - Enums para estados
  - Configuración en settings

❌ 8. PRIMITIVE OBSESSION:
  - Objetos de valor para resultados
  - DTOs para transferencia
  - No tuplas/dicts primitivos

❌ 9. INAPPROPRIATE INTIMACY:
  - Encapsulación
  - Law of Demeter
  - Interfaces públicas claras

❌ 10. REINVENTING THE WHEEL:
  - Usar Django/DRF built-ins
  - No reimplementar lo que existe
  - Aprovechar el framework
```

---

### 3.2 Patrones Permitidos

```yaml
✅ USAR CUANDO APLIQUE:

Singleton:
  - Scheduler (única instancia necesaria)
  - Thread-safe con Lock

Adapter:
  - BD Legacy IVR
  - Servicios externos legacy

Strategy (simplificado):
  - Funciones, no clases complejas
  - Diccionario de estrategias

Observer:
  - Django Signals (built-in)
  - No implementación custom

Middleware:
  - Auth, permisos, throttling
  - Logging, auditoría
  - CORS, seguridad

Managers/QuerySets:
  - Django ORM extensiones
  - No Repository Pattern custom
```

---

### 3.3 Principios SOLID

```yaml
✅ OBLIGATORIO:

S - Single Responsibility:
  - Una clase = una razón para cambiar
  - Servicios cohesivos pequeños

O - Open/Closed:
  - Abierto a extensión
  - Cerrado a modificación
  - Configuración > código hardcoded

L - Liskov Substitution:
  - Subclases intercambiables
  - Sin cambio de comportamiento

I - Interface Segregation:
  - Interfaces pequeñas y cohesivas
  - No forzar dependencias innecesarias

D - Dependency Inversion:
  - Depender de abstracciones
  - Inyección de dependencias
```

---

## 💾 4. RESTRICCIONES DE BASE DE DATOS

### 4.1 Estructura de BD IVR (Readonly)

```yaml
✅ ACCESO:
  - Solo SELECT
  - Usuario: ivr_readonly_user
  - Conexión: 'ivr_readonly'

📋 TABLAS:
  - tbl_historico_t1_YYYY (Trimestre 1)
  - tbl_historico_t2_YYYY (Trimestre 2)
  - tbl_historico_t3_YYYY (Trimestre 3)
  - Trimestre 4: ??? (pendiente clarificar)

⚠️ CAMPOS (Pendiente definición exacta):
  - dFecha
  - centro_transferencia (o variantes legacy)
  - servicio_800
  - total_llamadas (o variantes)
  - tiempo_espera
  - tiempo_atencion
  - estado
  - menu_seleccion
  - opcion_menu
  - transferido_a
  - comentarios

🔴 CRÍTICO:
  - Estructura NO documentada completamente
  - Requiere diccionario de datos del cliente
  - Adapter debe manejar variaciones de nombres
```

---

### 4.2 BD Analytics (Write)

```yaml
✅ MODELOS DJANGO:
  - User (extendido)
  - Role, UserRole
  - DirectPermission
  - DataSegment
  - SecurityQuestion
  - UserSession
  - Alert, AlertHistory
  - InternalMessage
  - ReporteTrimestral (espejo de IVR)
  - DataAvailability
  - ExportHistory
  - AuditLog

✅ MIGRACIONES:
  - Django migrations estándar
  - Versionadas en git
  - Squash periódicamente

⚠️ RETENCIÓN:
  - Datos reportes: 3 años online
  - Sesiones: eliminar expiradas diariamente
  - Notificaciones: 30 días después de leídas
  - Alertas: 6 meses activo + 2 años archivado
  - Exports: 7 días
  - Auditoría: según política (2+ años)
```

---

### 4.3 ETL

```yaml
✅ PROCESO:
  1. Extraer de BD IVR (readonly)
  2. Transformar (limpiar, normalizar)
  3. Cargar en BD Analytics
  4. Actualizar DataAvailability

⏰ FRECUENCIA:
  - Configurable: 6-12 horas
  - Scheduler: APScheduler
  - Job: ETLJob.run()

✅ TRANSACCIONALIDAD:
  - @transaction.atomic en todo el proceso
  - Rollback completo si falla cualquier paso
  - DataAvailability solo si count > 0

⚠️ VALIDACIONES:
  - Manejo de NULL
  - Duplicados (consolidar)
  - Inconsistencias (loguear)
  - Rango de fechas máximo: 2 años por ejecución
```

---

## 🎯 5. RESTRICCIONES FUNCIONALES (SRS v2.0)

### 5.1 Autenticación y Usuarios

```yaml
UC-001: Login
  - Usuario/contraseña
  - Bloqueo tras 3 intentos (15 min)
  - Sesión única (cerrar previas)
  - JWT tokens
  - Timeout: 15 minutos inactividad

UC-003: Recuperación de contraseña
  - SOLO 3 preguntas de seguridad
  - NO email
  - Contraseña temporal vía buzón interno
  - Forzar cambio en próximo login

UC-004: Cambio de contraseña
  - Políticas: 8-100 chars, complejidad
  - No repetir últimas 5
  - No contener username/nombre
  - Historial de contraseñas (hashes)

UC-006: Crear usuario
  - Username autogenerado: nombre.apellido###
  - Estado inicial: PENDIENTE_CONFIGURACION
  - Contraseña temporal
  - Notificación vía buzón interno

UC-008: Eliminar usuario
  - Baja LÓGICA únicamente
  - No eliminación física
  - deleted_at, deleted_by
  - Conservar datos por auditoría
```

---

### 5.2 Roles y Permisos (RBAC)

```yaml
✅ MODELO:
  - Flat RBAC (NIST)
  - 18 roles funcionales (R001-R018)
  - Sin jerarquía automática
  - Usuarios pueden tener múltiples roles
  - Permisos se acumulan (unión)

✅ PRECEDENCIA (UC-042):
  1. Permisos Directos (mayor)
  2. Permisos de Roles
  3. Permisos de Segmento (menor)

✅ SEPARACIÓN DE FUNCIONES (SoD):
  - R016 (SYSTEM_ADMIN) ⚔️ R017 (AUDIT_VIEWER)
  - R001 (USERS_FULL_MANAGER) ⚔️ R017 (AUDIT_VIEWER)
  - Validar antes de asignar

✅ PERMISOS DIRECTOS:
  - Justificación obligatoria (min 20 chars)
  - Vencimiento obligatorio (max 6 meses)
  - Auditar todas las asignaciones
```

---

### 5.3 Reportes

```yaml
UC-017: Reporte Trimestral
  - Tiempo respuesta: < 5 segundos
  - Filtros: fecha, centro, servicio
  - Aplicar segmento automáticamente
  - Caché de queries frecuentes

UC-020: Filtros de Fecha
  - 15+ presets rápidos
  - Rango personalizado
  - Comparación entre períodos
  - Validar disponibilidad de datos
  - Rango máximo: 2 años

UC-022/023/024: Exportaciones
  CSV:
    - Max: 100,000 registros
    - Timeout: 60 segundos
    - UTF-8, delimitador coma

  Excel:
    - Max: 100,000 registros
    - Timeout: 90 segundos
    - Formato .xlsx con estilos

  PDF:
    - Max: 10,000 registros
    - Timeout: 120 segundos
    - Logo, encabezados, paginación

✅ LÍMITES DIARIOS:
  - BÁSICO: 5 exportaciones
  - ANALISTA: sin límite
  - COORDINACIÓN: 20 exportaciones
  - ADMINISTRADOR: sin límite
```

---

### 5.4 Dashboard y Visualización

```yaml
UC-025: Dashboard Principal
  - 10 widgets priorizados
  - Actualización según ETL (6-12h)
  - Timestamp visible: última actualización
  - NO real-time updates
  - Usuario debe refrescar manualmente

✅ WIDGETS:
  1. Llamadas Último Período (CRÍTICO)
  2. Distribución por Servicio (CRÍTICO)
  3. Top 5 Centros (ALTA)
  4. Estado de Datos (ALTA)
  5. Alertas Activas (ALTA)
  6-10. Otros según prioridad

UC-030: Personalizar Dashboard
  - Solo rol R009 (DASHBOARD_CUSTOMIZER)
  - Máximo 5 vistas guardadas
  - Máximo 10 widgets por vista
  - Layout configurable (grid 12x8)
```

---

### 5.5 Alertas

```yaml
UC-036 a UC-040: Sistema de Alertas

✅ TIPOS:
  - THRESHOLD: Valor vs umbral
  - ANOMALY: ±2σ (desviación estándar)
  - PATTERN: Tendencias sostenidas
  - TREND: Variación porcentual

✅ SEVERIDADES:
  - INFO (azul)
  - WARNING (amarillo)
  - CRITICAL (rojo)

✅ FRECUENCIAS:
  - IMMEDIATE: al instante
  - HOURLY: cada hora
  - DAILY: diaria
  - ONCE: una sola vez

✅ SNOOZE:
  - 1 hora
  - 8 horas
  - 24 horas
  - Personalizado

⚠️ LÍMITES:
  - Máximo 50 destinatarios por alerta
  - Evaluación cada 5 minutos
  - Consolidar alertas repetitivas
  - Retención: 6 meses + 2 años archivado

🔴 CRÍTICO:
  - SOLO notificación vía buzón interno
  - NO email bajo ninguna circunstancia
```

---

## ⚡ 6. RESTRICCIONES DE PERFORMANCE (SLA)

### 6.1 Tiempos de Respuesta

```yaml
✅ REPORTES:
  - Principales: < 5 segundos
  - Complejos: < 10 segundos
  - Análisis exploratorio: < 300 segundos (5 min)

✅ EXPORTACIONES:
  - CSV: 60 segundos máximo
  - Excel: 90 segundos máximo
  - PDF: 120 segundos máximo

✅ DASHBOARD:
  - Carga inicial: < 3 segundos
  - Carga de widget: < 2 segundos

✅ APIs:
  - GET simples: < 500ms
  - POST/PUT: < 1 segundo
  - Búsquedas: < 2 segundos

⚠️ OPTIMIZACIONES:
  - Índices en campos de filtro
  - Caché de queries frecuentes
  - Paginación obligatoria
  - Select/prefetch related
```

---

### 6.2 Límites de Datos

```yaml
✅ RESULTADOS EN PANTALLA:
  - Máximo: 50,000 registros
  - Paginación: 50 items default
  - Cursor pagination para grandes datasets

✅ EXPORTACIONES:
  - CSV: 100,000 registros
  - Excel: 100,000 registros
  - PDF: 10,000 registros
  - División automática si excede

✅ QUERIES:
  - Rango fechas: máximo 2 años
  - Timeout análisis: 5 minutos
```

---

## 🚀 7. RESTRICCIONES DE INFRAESTRUCTURA

### 7.1 Contenedores

```yaml
✅ DOCKERFILE:
  - Multi-stage build obligatorio
  - Imagen base: python:3.11-slim
  - Usuario non-root
  - No secrets en imagen
  - Layer caching optimizado

✅ ESCANEO:
  - Trivy en cada build
  - Sin vulnerabilidades High/Critical
  - SBOM de imagen generado

✅ HEALTHCHECKS:
  - /health (liveness)
  - /health/ready (readiness)
  - Timeout: 5 segundos
```

---

### 7.2 Deployment

```yaml
✅ KUBERNETES:
  - Recursos limitados (requests/limits)
  - HPA configurado
  - PodDisruptionBudget
  - NetworkPolicies

✅ STRATEGY:
  - RollingUpdate para cambios menores
  - Blue-Green para cambios mayores
  - Canary para features críticos
  - Rollback automatizado si falla

✅ SECRETS:
  - Kubernetes Secrets
  - Vault/KMS para producción
  - Rotación periódica
  - No secrets en código/logs
```

---

## 💻 8. RESTRICCIONES DE DESARROLLO

### 8.1 Coding Standards

```yaml
✅ PYTHON:
  - PEP 8 obligatorio
  - Black para formateo
  - Flake8 para linting
  - isort para imports
  - Type hints (Python 3.10+)

✅ DJANGO/DRF:
  - Serializers explícitos (no __all__)
  - Permisos en cada endpoint
  - Throttling configurado
  - Paginación siempre
  - Validaciones exhaustivas

✅ TESTING:
  - Cobertura: mínimo 80%
  - Tests unitarios + integración
  - Factory Boy para fixtures
  - Pytest como runner
  - Tests de seguridad (Bandit)

✅ DOCUMENTACIÓN:
  - Docstrings en funciones/clases
  - OpenAPI/Swagger actualizado
  - README con setup
  - Diagramas actualizados
```

---

### 8.2 Git y CI/CD

```yaml
✅ COMMITS:
  - Conventional Commits
  - Formato: type(scope): description
  - Firmar commits (GPG)

✅ BRANCHES:
  - main: producción
  - develop: integración
  - feature/*: features
  - hotfix/*: urgentes

✅ CI/CD PIPELINE:
  1. Linting (Black, Flake8)
  2. Tests (pytest)
  3. SAST (Bandit, Semgrep)
  4. Dependency check (safety)
  5. Build Docker
  6. Scan imagen (Trivy)
  7. Deploy
  8. Smoke tests

✅ GATES:
  - Sin tests failing
  - Cobertura >= 80%
  - Sin CVE High/Critical
  - Bandit score >= B
  - check --deploy passing
```

---

## 📊 9. RESTRICCIONES DE LOGGING Y AUDITORÍA

### 9.1 Logging

```yaml
❌ PROHIBIDO EN LOGS:
  - Contraseñas
  - Tokens
  - API Keys
  - PII sin enmascarar
  - Números de tarjeta
  - SSN/CURP/RFC

✅ OBLIGATORIO:
  - Request ID único
  - User ID si autenticado
  - Timestamp ISO 8601
  - Level correcto
  - Masking de PII

✅ FORMATO:
  - JSON estructurado
  - Campos estándar
  - Trazabilidad end-to-end

✅ RETENCIÓN:
  - Aplicación: 30 días
  - Acceso: 90 días
  - Auditoría: 2+ años
  - Rotación automática
```

---

### 9.2 Auditoría

```yaml
✅ EVENTOS A AUDITAR:
  - Login/Logout
  - Cambios de permisos
  - Creación/modificación usuarios
  - Acceso a datos sensibles
  - Exportaciones
  - Cambios de configuración
  - Fallos de autenticación

✅ INFORMACIÓN:
  - Usuario (quién)
  - Acción (qué)
  - Recurso (sobre qué)
  - Timestamp (cuándo)
  - IP (desde dónde)
  - User Agent
  - Resultado (éxito/fallo)
  - Valores antes/después

✅ IMMUTABILIDAD:
  - Logs de auditoría inmutables
  - Solo append
  - No eliminación
  - Separación de funciones (SoD)
```

---

## 🔒 10. RESTRICCIONES DE PRIVACIDAD Y DATOS

### 10.1 Clasificación de Datos

```yaml
PÚBLICOS:
  - Catálogos (centros, servicios)
  - Documentación pública

INTERNOS:
  - Reportes agregados
  - Estadísticas sin PII

CONFIDENCIALES:
  - Información de usuarios
  - Registros de acceso
  - Configuración del sistema

RESTRINGIDOS:
  - Contraseñas (hashes)
  - Tokens
  - Preguntas de seguridad
  - Datos de auditoría
```

---

### 10.2 Minimización de Datos

```yaml
✅ PRINCIPIOS:
  - Recolectar solo lo necesario
  - Retener solo el tiempo necesario
  - Compartir solo con quien necesita
  - Eliminar cuando ya no se requiere

✅ PII:
  - Enmascarar en logs
  - Cifrar en tránsito
  - Cifrar en reposo si necesario
  - No exponer en URLs
  - Minimizar en serializers
```

---

## 📋 11. CHECKLIST DE CUMPLIMIENTO

### 11.1 Pre-Deploy

```yaml
☑️ Configuración:
  - DEBUG=False en prod
  - SECRET_KEY desde env
  - ALLOWED_HOSTS correcto
  - SECURE_* flags activos

☑️ Seguridad:
  - Permisos configurados
  - Throttling activo
  - CORS correcto
  - HTTPS forzado

☑️ Base de Datos:
  - Migraciones aplicadas
  - Usuario BD correcto
  - Backups configurados

☑️ Dependencias:
  - SBOM generado
  - Sin CVE críticos
  - Versiones bloqueadas

☑️ Tests:
  - Cobertura >= 80%
  - Todos passing
  - SAST passing
  - check --deploy passing

☑️ Infraestructura:
  - Healthchecks funcionando
  - Recursos limitados
  - Secrets configurados
  - Monitoring activo
```

---

### 11.2 Post-Deploy

```yaml
☑️ Validaciones:
  - Smoke tests passing
  - Dashboard carga correctamente
  - Login funciona
  - APIs responden

☑️ Monitoring:
  - Logs fluyendo
  - Métricas reportando
  - Alertas configuradas
  - Trazabilidad activa

☑️ Rollback Plan:
  - Procedimiento documentado
  - Backups verificados
  - Contactos disponibles
```

---

## 🎓 12. GLOSARIO DE RESTRICCIONES

```yaml
Términos Clave:

CRÍTICO / NO NEGOCIABLE:
  - Debe cumplirse sin excepción
  - Violación = rechazo automático

OBLIGATORIO:
  - Debe implementarse
  - Excepciones requieren aprobación formal

PROHIBIDO:
  - No debe usarse bajo ninguna circunstancia
  - Violación = incidente de seguridad

RECOMENDADO:
  - Buena práctica
  - Excepciones permitidas con justificación

EVITAR:
  - No preferido
  - Alternativas deben considerarse primero
```

---

## ✅ RESUMEN EJECUTIVO

### Restricciones Críticas (Top 10)

1. 🚫 **NO EMAIL** - Solo buzón interno
2. 🔒 **BD IVR READONLY** - Zero escritura
3. 💾 **SESIONES EN BD** - No Redis
4. 🔄 **NO REAL-TIME** - Actualización por ETL
5. 🔐 **DEBUG=FALSE** - Siempre en producción
6. 🎫 **JWT + PERMISOS** - Autenticación robusta
7. 📊 **PAGINACIÓN** - Siempre activa
8. 🔍 **AUDITORÍA** - Eventos críticos logged
9. 🛡️ **SIN CVE HIGH** - Dependencias seguras
10. 📝 **BAJA LÓGICA** - No eliminación física

### Cumplimiento Requerido

- ✅ **100%** restricciones críticas
- ✅ **95%** restricciones obligatorias
- ✅ **80%** restricciones recomendadas

### Consecuencias de Incumplimiento

- **Críticas:** Rechazo en code review + rollback
- **Obligatorias:** Plan de corrección inmediato (72h)
- **Recomendadas:** Deuda técnica documentada

---

**Documento controlado** - Cambios requieren aprobación de arquitectura
