# Guía Rápida: Validación de api/callcentersite

## Estado General
✅ **APROBADO CON OBSERVACIONES MENORES**

---

## Resumen en 30 Segundos

El backend Django `api/callcentersite` está **correctamente estructurado** y **cumple todas las restricciones arquitectónicas críticas**:

- ✅ RNF-002: Sesiones en base de datos PostgreSQL (NO Redis)
- ✅ Sin dependencias prohibidas
- ✅ 23 aplicaciones Django organizadas por dominio
- ✅ Seguridad robusta (JWT + session protection + database routing)
- ✅ Herramientas de calidad configuradas (Ruff, MyPy, Bandit)
- ✅ Testing comprehensivo con cobertura ≥80%

---

## Comandos de Validación Rápida

```bash
cd /home/runner/work/IACT---project/IACT---project/api/callcentersite

# Verificación de calidad
make lint           # Linting con Ruff
make type-check     # Type checking con MyPy
make security       # Análisis de seguridad con Bandit

# Testing
make test-coverage  # Tests con cobertura ≥80%

# Django checks
python manage.py check --deploy

# Todo en uno
make quality        # Lint + Format-check + Type-check + Security
make ci            # Quality + Test-coverage
```

---

## Observaciones Menores (No Bloquean)

### 1. Duplicación de Apps ⚠️
**Ubicación**: `callcentersite/settings/base.py`
```python
"callcentersite.apps.configuration",  # línea 46
"callcentersite.apps.configuracion",  # línea 47
```
**Acción**: Consolidar en una sola app cuando haya ventana de refactorización.

### 2. URL Duplicada ⚠️
**Ubicación**: `callcentersite/urls.py`
```python
path("api/v1/", include("callcentersite.apps.users.urls")),  # línea 23
# ... otras rutas ...
path("api/v1/", include("callcentersite.apps.users.urls")),  # línea 35 - DUPLICADA
```
**Acción**: Eliminar línea 35.

---

## Arquitectura Destacada

### Database Router ✅
**Archivo**: `callcentersite/database_router.py`

Protege la base de datos IVR legacy:
- ✅ Lecturas permitidas desde `ivr_readonly`
- ✅ Escrituras **bloqueadas con excepción**
- ✅ Migraciones deshabilitadas

```python
def db_for_write(self, model, **hints):
    if app_label.startswith("ivr_legacy"):
        raise ValueError(
            "CRITICAL RESTRICTION VIOLATED: IVR database is READ-ONLY"
        )
```

### Session Security Middleware ✅
**Archivo**: `callcentersite/middleware/session_security.py`

Protección contra session hijacking:
- ✅ Valida IP por sesión
- ✅ Valida User-Agent por sesión
- ✅ Logout automático ante cambios sospechosos

---

## Estructura de Apps (23)

### Core (4)
- `common`, `users`, `authentication`, `permissions`

### Negocio (4)
- `llamadas`, `clientes`, `equipos`, `horarios`

### Operaciones (4)
- `notifications`, `alertas`, `tickets`, `audit`

### Análisis (4)
- `analytics`, `metricas`, `dashboard`, `reportes`

### Integración (2)
- `ivr_legacy`, `etl`

### Configuración (5)
- `configuration`, `configuracion`, `presupuestos`, `politicas`, `excepciones`

---

## Endpoints Principales

```
/admin/                           - Django Admin
/api/schema/                      - OpenAPI Schema
/api/docs/                        - Swagger UI
/api/v1/*                        - APIs REST
/api/dora/                       - Métricas DORA
/health/                         - Health Check
```

---

## Bases de Datos

### PostgreSQL (Principal)
- **Host**: 127.0.0.1:15432
- **Database**: iact_analytics
- **Uso**: Analytics, sesiones, métricas

### MariaDB (IVR Legacy - Read-Only)
- **Host**: 127.0.0.1:13306
- **Database**: ivr_legacy
- **Uso**: Solo lectura de datos IVR

---

## Checklist Pre-Deployment

```bash
# 1. Calidad
make lint              # ✅
make format-check      # ✅
make type-check        # ⚠️ (warnings ok)
make security          # ✅

# 2. Tests
make test-coverage     # ✅ (≥80%)

# 3. Django
python manage.py check --deploy  # ✅
python manage.py showmigrations  # ✅

# 4. Configuración
# ✅ SECRET_KEY único
# ✅ DEBUG=False en producción
# ✅ ALLOWED_HOSTS configurado
# ✅ Bases de datos configuradas
```

---

## Documentación Completa

Ver: `VALIDACION_API_CALLCENTERSITE.md` para el reporte detallado de 19KB.

---

## Recomendación

**El proyecto está listo para continuar desarrollo y despliegue.** Las 2 observaciones menores pueden abordarse en sprints futuros sin bloquear el avance.

---

**Validado**: 2025-11-16  
**Por**: ApiAgent
