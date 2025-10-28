# Arquitectura GitHub Codespaces - CallCenter Django

## 📋 Índice
1. [Visión General](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Gestión de Dependencias](#gestión-de-dependencias)
6. [Optimización de Costos](#optimización-de-costos)
7. [Comandos y Automatización](#comandos-y-automatización)

---

## Visión General

### Objetivo
Entorno de desarrollo basado en GitHub Codespaces con prebuild nativo, optimizado para costos y tiempo de inicio, usando Docker Compose con perfiles para gestión inteligente de servicios.

### Stack Tecnológico
- **Framework:** Django 4.2+
- **Bases de Datos:** PostgreSQL 15 (siempre activo) + MariaDB 11 (bajo demanda)
- **Contenedores:** Docker Compose con Alpine Linux
- **CI/CD:** GitHub Codespaces Prebuild nativo
- **Gestión:** Makefile para automatización de tareas

### Principios de Diseño
1. **Costo-efectivo:** Solo servicios necesarios activos por defecto
2. **Inicio rápido:** Prebuild reduce tiempo de ~3 min a ~30 seg
3. **Idempotente:** Scripts detectan estado y actúan en consecuencia
4. **Sin fricción:** Configuración automática, mínima intervención manual

### Decisión de Arquitectura: Ubicación de Requirements

**Estructura adoptada:** Requirements dentro del proyecto Django (`callcentersite/requirements/`)

**Razones:**
1. **Coherencia:** Todo el código Django junto, incluyendo sus dependencias
2. **workspaceFolder:** El directorio de trabajo de Codespaces apunta a `callcentersite/`
3. **Claridad:** Separa claramente la configuración del entorno (.devcontainer/) del código de la aplicación
4. **Escalabilidad:** Si en el futuro se agrega otro proyecto al monorepo, cada uno tiene sus propios requirements

**Alternativas consideradas:**
- Requirements en root del repo: Más común en proyectos Python simples, pero menos coherente cuando el workspace es una subcarpeta
- Requirements en .devcontainer/: Mezcla configuración de infraestructura con dependencias de aplicación

---

## Estructura del Proyecto

```
proyecto/
├── .devcontainer/
│   ├── devcontainer.json       # Configuración de Codespaces
│   ├── docker-compose.yml      # Orquestación de servicios
│   └── Dockerfile              # Imagen Alpine con deps core
├── .github/
│   └── workflows/
│       └── (opcional)          # Actions personalizados
└── callcentersite/             # Proyecto Django
    ├── requirements/
    │   ├── base.txt            # Dependencias de producción
    │   ├── dev.txt             # Herramientas de desarrollo
    │   └── test.txt            # Framework de testing
    ├── manage.py
    ├── Makefile                # Automatización de tareas
    ├── .env.example           # Variables de entorno template
    ├── README-CODESPACES.md   # Documentación de uso
    └── callcentersite/
        ├── settings.py
        ├── wsgi.py
        └── urls.py
```

---

## Componentes del Sistema

### 1. Contenedor Principal (app)

**Imagen Base:** `python:3.12-alpine3.19`

**Responsabilidades:**
- Ejecutar aplicación Django
- Proporcionar herramientas de desarrollo
- Gestionar migraciones de base de datos

**Optimizaciones:**
- Usuario no-root (`django:1000`)
- Dependencies pre-instaladas en layer
- Volumen cached para código fuente
- Volumen adicional para cache de pip
- Red personalizada para aislamiento

**Build Arguments:**
```dockerfile
ARG PYTHON_VERSION=3.12
ARG USER_UID=1000
ARG USER_GID=1000
```

**Labels de Metadata:**
```yaml
labels:
  com.callcenter.service: "django-app"
  com.callcenter.environment: "development"
  com.callcenter.description: "Django application container"
```

**Volúmenes:**
- `..:/workspace:cached` - Código fuente con caché optimizado
- `pip_cache:/home/django/.cache/pip` - Cache de pip persistente

**Restart Policy:** `unless-stopped` - Reinicio automático excepto si se detiene manualmente

### 2. PostgreSQL (db_postgres)

**Imagen:** `postgres:15-alpine`

**Características:**
- Activo por defecto (sin profile)
- Healthcheck cada 5 segundos con start_period de 10s
- Volumen persistente `pg_data` con nombre explícito
- Puerto 5432 expuesto solo internamente (expose, no ports)
- Configuración UTF8 y locale en_US.UTF-8
- Timezone configurado a UTC

**Variables de Entorno Completas:**
```yaml
POSTGRES_DB: callcenterdb
POSTGRES_USER: django_user
POSTGRES_PASSWORD: django_pass
POSTGRES_INITDB_ARGS: "--encoding=UTF8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8"
TZ: UTC
PGTZ: UTC
```

**Uso:**
- Base de datos principal
- Datos transaccionales
- Modelos Django por defecto

**Healthcheck Mejorado:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U django_user -d callcenterdb"]
  interval: 5s
  timeout: 5s
  retries: 10
  start_period: 10s  # Tiempo adicional para inicialización
```

### 3. MariaDB (db_mariadb)

**Imagen:** `mariadb:11-jammy`

**Características:**
- Inactivo por defecto (profile: `mariadb`)
- Healthcheck cada 5 segundos con start_period de 30s
- Volumen persistente `maria_data` con nombre explícito
- Puerto 3306 expuesto solo internamente
- Character set utf8mb4 y collation utf8mb4_unicode_ci
- Timezone configurado a UTC

**Variables de Entorno Completas:**
```yaml
MARIADB_DATABASE: callcenterdb_maria
MARIADB_USER: django_user
MARIADB_PASSWORD: django_pass
MARIADB_ROOT_PASSWORD: root_pass
MARIADB_CHARSET: utf8mb4
MARIADB_COLLATION: utf8mb4_unicode_ci
TZ: UTC
```

**Uso:**
- Sistema legacy o datos específicos
- Activación bajo demanda
- Requiere router de base de datos Django

**Profile:** Solo se activa con `--profile mariadb`

### 4. Red Personalizada

**Nombre:** `callcenter_dev_network`
**Driver:** bridge

**Beneficios:**
- Aislamiento de otros contenedores
- DNS interno automático entre servicios
- Mejor control de red

### 5. Volúmenes Nombrados

Todos los volúmenes tienen nombres explícitos para mejor gestión:
- `callcenter_pg_data` - Datos PostgreSQL
- `callcenter_maria_data` - Datos MariaDB
- `callcenter_pip_cache` - Cache de pip compartido

---

## Flujo de Trabajo

### Fase 1: Prebuild (GitHub)

```
Push a main
    │
    ▼
GitHub detecta cambios
    │
    ├─── requirements/*.txt? ──→ Trigger Prebuild
    ├─── .devcontainer/*? ────→ Trigger Prebuild
    └─── Otros archivos ──────→ Skip Prebuild
    │
    ▼
Build Dockerfile
    │
    ▼
Instalar requirements/base.txt
    │
    ▼
Cachear imagen
    │
    ▼
Prebuild disponible
```

**Tiempo:** ~5-10 minutos (una sola vez)
**Costo:** $0 (incluido en GitHub)

### Fase 2: Creación de Codespace

```
Click: Create Codespace
    │
    ▼
Descargar prebuild
    │
    ▼
Iniciar contenedor app
    │
    ▼
Iniciar PostgreSQL
    │
    ▼
¿PostgreSQL healthy? ──No──┐
    │                       │
   Sí                       │
    │                       │
    ▼                       │
onCreateCommand             │
    │                       │
    ▼                       │
Instalar requirements/dev.txt
    │
    ▼
Instalar requirements/test.txt
    │
    ▼
postStartCommand
    │
    ▼
Ejecutar migraciones
    │
    ▼
Codespace listo
```

**Tiempo:** ~30-60 segundos
**Costo:** ~$0.0015 (30 seg × $0.18/hora)

### Fase 3: Uso Diario

```
Reabrir Codespace
    │
    ▼
Resume desde suspensión
    │
    ▼
postStartCommand
    │
    ▼
Verificar DB health
    │
    ▼
Ejecutar migraciones
    │
    ▼
Codespace activo
    │
    ▼
¿Necesitas MariaDB?
    │
    ├─── Sí ───→ docker compose --profile mariadb up
    │                │
    │                ▼
    │            Migrar MariaDB
    │                │
    └─── No ────┐    │
                │    │
                ▼    ▼
         Desarrollo normal
```

**Tiempo:** ~10-15 segundos
**Costo:** ~$0.0008 (15 seg × $0.18/hora)

---

## Gestión de Dependencias

### Estrategia de 3 Capas

#### Layer 1: Base (callcentersite/requirements/base.txt)
**Instalado:** En Dockerfile durante prebuild
**Contenido:**
- Django core
- Drivers de bases de datos (psycopg2-binary, mysqlclient)
- Utilidades esenciales (python-dotenv, whitenoise)

**Rebuild trigger:** Cambios en este archivo reconstruyen prebuild

#### Layer 2: Development (callcentersite/requirements/dev.txt)
**Instalado:** onCreateCommand (primera creación)
**Contenido:**
- Formateadores (black, ruff)
- Linters (mypy)
- Debugging tools (django-debug-toolbar, ipython)
- Django extensions

**Rebuild trigger:** Solo se reinstala al recrear Codespace

#### Layer 3: Testing (callcentersite/requirements/test.txt)
**Instalado:** onCreateCommand (primera creación)
**Contenido:**
- pytest y plugins
- Coverage tools
- Factories (factory-boy, faker)
- Mocking utilities

**Rebuild trigger:** Solo se reinstala al recrear Codespace

### Flujo de Actualización

```bash
# Desarrollador actualiza dependencia
echo "django-cors-headers>=4.3" >> api/requirements/base.txt

# Commit y push
git add api/requirements/base.txt
git commit -m "feat: agregar django-cors-headers"
git push origin main

# GitHub automáticamente:
# 1. Detecta cambio en api/requirements/base.txt
# 2. Trigger rebuild de prebuild
# 3. Nuevos Codespaces usan versión actualizada

# Codespaces existentes:
make install-base  # Actualizar manualmente
```

---

## Optimización de Costos

### Estrategia de Profiles

**Servicios sin profile (siempre activos):**
- `app`: Aplicación Django
- `db_postgres`: Base de datos principal

**Servicios con profile (bajo demanda):**
- `db_mariadb` (profile: `mariadb`)

### Cálculo de Costos

#### Configuración Base (app + postgres)
```
CPU: 2 cores
RAM: ~1.5 GB usada / 4 GB disponibles
Costo: $0.18/hora
```

#### Con MariaDB Activado (app + postgres + mariadb)
```
CPU: 2 cores
RAM: ~2.2 GB usada / 4 GB disponibles
Costo: $0.18/hora (mismo precio, hay capacidad)
```

#### Por Desarrollador (mes, 40h/semana)
```
Tiempo activo: 160 horas/mes
Costo compute: 160 × $0.18 = $28.80

Con timeout 30 min (uso real ~80h):
Costo compute: 80 × $0.18 = $14.40

Storage (10GB): $0.70/mes

Total optimizado: $15.10/mes por dev
```

#### Ahorro vs Sin Prebuild
```
Sin prebuild:
- Tiempo instalación: 3 min por inicio
- 20 días × 3 min = 60 min/mes desperdiciados
- Costo desperdicio: 60 min × ($0.18/60) = $0.18/mes

Con prebuild:
- Tiempo instalación: 30 seg por inicio
- 20 días × 30 seg = 10 min/mes
- Costo: 10 min × ($0.18/60) = $0.03/mes

Ahorro: $0.15/mes por dev (83% reducción)
```

### Configuración de Timeouts

**Recomendado en Settings → Codespaces:**
```
Idle timeout: 30 minutos
Default retention: 1 día
Max retention: 7 días
```

---

## Comandos y Automatización

### Makefile: Interfaz Unificada

**Principios:**
1. **Idempotencia:** Detectar estado antes de actuar
2. **Feedback claro:** Sin emojis, mensajes profesionales
3. **Robustez:** Manejo de errores silencioso cuando apropiado
4. **Simplicidad:** Una tarea = un comando

### Lifecycle Hooks de Devcontainer

El devcontainer.json implementa múltiples hooks para automatización completa:

#### 1. updateContentCommand
**Cuándo:** Después de actualizar contenido del repositorio (git pull)
**Propósito:** Sincronizar cambios del repo
**Ejemplo:**
```json
"updateContentCommand": {
  "info": "echo 'Repositorio actualizado'"
}
```

#### 2. onCreateCommand
**Cuándo:** Una sola vez al crear el Codespace
**Propósito:** Instalaciones pesadas que no cambian frecuentemente
**Ejemplo:**
```json
"onCreateCommand": {
  "install-dev": "pip install -r requirements/dev.txt",
  "install-test": "pip install -r requirements/test.txt",
  "verify": "python -c 'import django; import pytest'"
}
```

#### 3. postCreateCommand
**Cuándo:** Después de onCreateCommand
**Propósito:** Configuraciones que requieren dependencias instaladas
**Ejemplo:**
```json
"postCreateCommand": {
  "setup-git": "git config --global --add safe.directory /workspace",
  "copy-env": "[ ! -f .env ] && cp .env.example .env || true"
}
```

#### 4. postStartCommand
**Cuándo:** Cada vez que el Codespace inicia o resume
**Propósito:** Verificaciones de estado y migraciones
**Ejemplo:**
```json
"postStartCommand": {
  "wait-db": "until pg_isready -h db_postgres -U django_user; do sleep 1; done",
  "migrate-postgres": "python manage.py migrate",
  "collect-static": "python manage.py collectstatic --noinput --clear || true"
}
```

#### 5. postAttachCommand
**Cuándo:** Después de que el editor se conecta
**Propósito:** Información de bienvenida
**Ejemplo:**
```json
"postAttachCommand": {
  "welcome": "cat README-CODESPACES.md",
  "status": "make ps"
}
```

### Categorías de Comandos

#### 1. Gestión de Dependencias
```makefile
make install-base    # Instalar/actualizar requirements/base.txt
make install-dev     # Instalar/actualizar requirements/dev.txt
make install-test    # Instalar/actualizar requirements/test.txt
make install-all     # Instalar/actualizar todas las dependencias
```

#### 2. Base de Datos
```makefile
make migrate         # Migrar PostgreSQL
make migrate-mariadb # Migrar MariaDB (si está activo)
make migrate-all     # Migrar ambas bases de datos
make db-shell        # Consola PostgreSQL
make db-reset        # Reiniciar base de datos (pide confirmación)
```

#### 3. Desarrollo
```makefile
make run             # Iniciar servidor Django
make shell           # Django shell
make superuser       # Crear superusuario
make mariadb-up      # Activar MariaDB
make mariadb-down    # Desactivar MariaDB
```

#### 4. Testing y Calidad
```makefile
make test            # Ejecutar tests
make test-cov        # Tests con coverage HTML
make test-fast       # Tests paralelos
make format          # Formatear código (black + ruff)
make lint            # Verificar calidad
make check           # Django system checks
```

#### 5. Mantenimiento
```makefile
make clean           # Limpiar archivos temporales
make logs            # Ver logs de todos los servicios
make ps              # Estado de contenedores
make restart         # Reiniciar servicios
```

### Detección Inteligente de Estado

**Ejemplo: make migrate**
```bash
# El comando detecta:
# 1. ¿PostgreSQL está corriendo?
# 2. ¿Hay migraciones pendientes?
# 3. ¿La base de datos está lista?

# Solo ejecuta si hay trabajo por hacer
# Salida limpia: solo muestra cambios aplicados
```

**Ejemplo: make install-dev**
```bash
# El comando detecta:
# 1. ¿requirements/dev.txt cambió?
# 2. ¿Paquetes ya instalados?
# 3. ¿Versiones coinciden?

# Reinstala solo si es necesario
# Sin --force manual: la lógica es automática
```

---

## Herramientas y Extensiones

### Extensiones de VSCode Instaladas

#### Python Core
- **ms-python.python** - Soporte completo de Python
- **ms-python.vscode-pylance** - Language server de alto rendimiento
- **ms-python.debugpy** - Debugging avanzado

#### Django
- **batisteo.vscode-django** - Snippets y sintaxis para Django templates

#### Linting y Formateo
- **charliermarsh.ruff** - Linter ultra rápido
- **ms-python.black-formatter** - Formateador de código Python

#### Testing
- **littlefoxteam.vscode-python-test-adapter** - Interfaz visual para tests

#### Base de Datos
- **mtxr.sqltools** - Cliente SQL integrado
- **mtxr.sqltools-driver-pg** - Driver PostgreSQL
- **mtxr.sqltools-driver-mysql** - Driver MariaDB/MySQL

#### Docker
- **ms-azuretools.vscode-docker** - Gestión de contenedores

#### Git
- **eamodio.gitlens** - Git supercharged

#### Utilidades
- **usernamehw.errorlens** - Errores inline
- **streetsidesoftware.code-spell-checker** - Corrector ortográfico
- **editorconfig.editorconfig** - Consistencia de código

### Configuraciones Clave de VSCode

#### Python
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.testing.pytestEnabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

#### Django Templates
```json
{
  "emmet.includeLanguages": {
    "django-html": "html"
  },
  "files.associations": {
    "**/templates/**/*.html": "django-html"
  }
}
```

#### SQLTools Pre-configurado
```json
{
  "sqltools.connections": [
    {
      "name": "PostgreSQL",
      "driver": "PostgreSQL",
      "server": "db_postgres",
      "port": 5432,
      "database": "callcenterdb",
      "username": "django_user",
      "password": "django_pass"
    }
  ]
}
```

#### Exclusiones Optimizadas
```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  },
  "search.exclude": {
    "**/__pycache__": true,
    "**/htmlcov": true
  }
}
```

---

## Diagramas de Arquitectura

### Arquitectura de Contenedores

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Codespaces VM (2 cores, 4GB RAM)                │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ Docker Compose Network                          │   │
│  │                                                 │   │
│  │  ┌──────────────┐      ┌─────────────────┐    │   │
│  │  │    app       │──────│  db_postgres    │    │   │
│  │  │  (Django)    │      │  (PostgreSQL)   │    │   │
│  │  │  Alpine 3.19 │      │  Alpine 15      │    │   │
│  │  │  Port: 8000  │      │  Port: 5432     │    │   │
│  │  └──────────────┘      └─────────────────┘    │   │
│  │         │                                      │   │
│  │         │ (optional)                           │   │
│  │         ▼                                      │   │
│  │  ┌──────────────┐                             │   │
│  │  │ db_mariadb   │                             │   │
│  │  │  (MariaDB)   │  profile: mariadb           │   │
│  │  │  Jammy 11    │                             │   │
│  │  │  Port: 3306  │                             │   │
│  │  └──────────────┘                             │   │
│  │                                                 │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  Volumes:                                              │
│  - pg_data    (PostgreSQL persistent data)             │
│  - maria_data (MariaDB persistent data)                │
│  - workspace  (código fuente, cached mount)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Ciclo de Vida de Dependencias

```
┌─────────────────────────────────────────────────────────┐
│                    BUILD TIME                           │
│                                                         │
│  Dockerfile                                             │
│  └─> COPY callcentersite/requirements/base.txt         │
│      └─> pip install -r base.txt                       │
│          ├─> Django                                    │
│          ├─> psycopg2-binary                           │
│          ├─> mysqlclient                               │
│          └─> python-dotenv, whitenoise                 │
│                                                         │
│  Result: Prebuild image cached by GitHub               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  CREATION TIME                          │
│                                                         │
│  onCreateCommand (dentro de callcentersite/)           │
│  ├─> pip install -r requirements/dev.txt               │
│  │   ├─> black, ruff, mypy                            │
│  │   ├─> django-debug-toolbar                         │
│  │   └─> ipython, ipdb                                │
│  │                                                     │
│  └─> pip install -r requirements/test.txt              │
│      ├─> pytest, pytest-django                         │
│      ├─> pytest-cov, coverage                          │
│      └─> factory-boy, faker                            │
│                                                         │
│  Ejecuta una sola vez por Codespace                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   RUNTIME                               │
│                                                         │
│  postStartCommand (cada inicio)                         │
│  ├─> Esperar PostgreSQL healthy                        │
│  ├─> python manage.py migrate                          │
│  └─> Mostrar instrucciones                             │
│                                                         │
│  Usuario ejecuta:                                       │
│  └─> make run  (python manage.py runserver)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Activación de MariaDB

```
Estado Inicial:
┌──────────┐     ┌─────────────┐
│   app    │────▶│ db_postgres │  (activo)
└──────────┘     └─────────────┘

         db_mariadb (inactivo, profile)


Usuario ejecuta: make mariadb-up
                      │
                      ▼
         docker compose --profile mariadb up -d
                      │
                      ▼
┌──────────┐     ┌─────────────┐
│   app    │────▶│ db_postgres │  (activo)
└──────────┘     └─────────────┘
     │
     └──────────▶ ┌─────────────┐
                  │ db_mariadb  │  (activo)
                  └─────────────┘
                      │
                      ▼
         make migrate-mariadb
                      │
                      ▼
         MariaDB listo para uso


Usuario ejecuta: make mariadb-down
                      │
                      ▼
         docker compose stop db_mariadb
                      │
                      ▼
┌──────────┐     ┌─────────────┐
│   app    │────▶│ db_postgres │  (activo)
└──────────┘     └─────────────┘

         db_mariadb (detenido, libera RAM)
```

---

## Matriz de Decisiones

### ¿Cuándo usar cada comando?

| Escenario | Comando | Razón |
|-----------|---------|-------|
| Inicio del día | `make run` | Inicia servidor Django |
| Actualizar deps base | `make install-base` | Sincroniza con requirements/base.txt |
| Antes de commit | `make format lint` | Asegura calidad de código |
| PR review | `make test-cov` | Verifica cobertura de tests |
| Debugging DB | `make db-shell` | Acceso directo a PostgreSQL |
| Trabajo con legacy | `make mariadb-up` | Activa MariaDB temporalmente |
| Liberar RAM | `make mariadb-down` | Detiene MariaDB |
| Limpiar proyecto | `make clean` | Elimina caché y temporales |
| Problemas de migración | `make migrate-all` | Sincroniza ambas DBs |
| Nueva feature | `make test` | Ejecuta suite completa |

---

## Checklist de Optimización

### Al crear el proyecto
- [ ] Crear estructura callcentersite/requirements/ con base/dev/test
- [ ] Configurar prebuild en GitHub Settings
- [ ] Definir timeouts (30 min idle, 1 día retention)
- [ ] Documentar profiles en README

### Por desarrollador
- [ ] Usar `make` en lugar de comandos manuales
- [ ] Cerrar Codespace al terminar el día
- [ ] Activar MariaDB solo cuando sea necesario
- [ ] Eliminar Codespaces antiguos semanalmente

### Por equipo
- [ ] Revisar costos mensualmente en GitHub Billing
- [ ] Actualizar prebuild cuando cambien deps base
- [ ] Mantener callcentersite/requirements/*.txt actualizados
- [ ] Compartir buenas prácticas de uso

---

## Troubleshooting

### Problema: Prebuild no se activa

**Síntomas:**
- Codespace tarda 3+ minutos en iniciar
- Se están instalando dependencias en onCreateCommand

**Diagnóstico:**
```bash
# Verificar si hay prebuild disponible
# En GitHub: Settings → Codespaces → Prebuilds
# Debe aparecer estado "Ready"
```

**Solución:**
1. Verificar que prebuild esté habilitado en Settings
2. Hacer push a rama main para trigger manual
3. Esperar 5-10 min a que complete
4. Recrear Codespace

### Problema: MariaDB no inicia

**Síntomas:**
- Error al ejecutar `make mariadb-up`
- Contenedor db_mariadb no aparece en `docker compose ps`

**Diagnóstico:**
```bash
# Ver logs del contenedor
docker compose logs db_mariadb

# Verificar perfil
docker compose config --profiles
```

**Solución:**
```bash
# Reiniciar con perfil explícito
docker compose --profile mariadb up -d db_mariadb

# Si persiste, recrear volumen
docker compose down -v
docker compose --profile mariadb up -d
```

### Problema: Migraciones fallan

**Síntomas:**
- Error en `make migrate` o `make migrate-mariadb`
- Base de datos no responde

**Diagnóstico:**
```bash
# Verificar que PostgreSQL esté saludable
docker compose ps db_postgres

# Probar conexión directa
pg_isready -h db_postgres -U django_user
```

**Solución:**
```bash
# Esperar a que DB esté ready
until pg_isready -h db_postgres -U django_user; do sleep 1; done

# Ejecutar migraciones manualmente
python manage.py migrate --verbosity 2

# Si hay conflictos, verificar migraciones
python manage.py showmigrations
```

### Problema: Dependencias desactualizadas

**Síntomas:**
- Imports fallan después de actualizar requirements
- Versiones incorrectas de paquetes

**Diagnóstico:**
```bash
# Ver versiones instaladas
pip list | grep django

# Verificar requirements
cat api/requirements/base.txt
```

**Solución:**
```bash
# Reinstalar todas las dependencias
make install-all

# Si persiste, forzar reinstalación
pip install --force-reinstall -r api/requirements/base.txt
```

---

## Glosario

**Prebuild:** Imagen Docker pre-construida por GitHub que contiene dependencias base instaladas, reduciendo tiempo de inicio de Codespaces.

**Profile (Docker Compose):** Etiqueta que agrupa servicios para activación selectiva, permitiendo ejecutar solo subconjuntos de servicios según necesidad.

**onCreateCommand:** Hook que se ejecuta una sola vez cuando se crea un Codespace nuevo, ideal para instalaciones que no cambian frecuentemente.

**postStartCommand:** Hook que se ejecuta cada vez que se inicia o resume un Codespace, ideal para verificaciones y preparación del entorno.

**Healthcheck:** Comando que Docker ejecuta periódicamente para verificar que un servicio esté funcionando correctamente.

**Idempotencia:** Propiedad de una operación que produce el mismo resultado sin importar cuántas veces se ejecute.

**Cached mount:** Tipo de volumen optimizado para código fuente que reduce latencia de I/O entre host y contenedor.

---

## Referencias

### Documentación Oficial
- [GitHub Codespaces Docs](https://docs.github.com/codespaces)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [Django Database Routers](https://docs.djangoproject.com/en/4.2/topics/db/multi-db/)
- [Alpine Linux](https://alpinelinux.org/)

### Herramientas
- [GitHub Pricing Calculator](https://github.com/pricing/calculator)
- [Docker Hub - Python Alpine](https://hub.docker.com/_/python)
- [Docker Hub - PostgreSQL Alpine](https://hub.docker.com/_/postgres)
- [Docker Hub - MariaDB](https://hub.docker.com/_/mariadb)

### Buenas Prácticas
- [12 Factor App](https://12factor.net/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

Esta arquitectura proporciona un balance óptimo entre velocidad de desarrollo, costo de operación y mantenibilidad del sistema.

---

## Mejores Prácticas Implementadas

### Seguridad

#### 1. Usuario No-Root
```dockerfile
# Dockerfile
USER django

# docker-compose.yml
user: django
```
**Beneficio:** Reduce superficie de ataque, previene modificaciones accidentales del sistema

#### 2. Puertos No Publicados
```yaml
# Usar expose en lugar de ports
expose: ["5432"]
# NO usar:
# ports: ["5432:5432"]
```
**Beneficio:** Servicios solo accesibles dentro de la red Docker, no desde el host

#### 3. Secrets Seguros
```yaml
# .env.example - nunca .env
DJANGO_SECRET_KEY=change-me-in-production
```
**Beneficio:** Secrets no versionados en git

#### 4. Configuración Git Segura
```json
"postCreateCommand": {
  "setup-git": "git config --global --add safe.directory /workspace/api"
}
```
**Beneficio:** Previene ataques de directorio no confiable

### Rendimiento

#### 1. Cache de Pip Persistente
```yaml
volumes:
  - pip_cache:/home/django/.cache/pip
```
**Beneficio:** Reinstalaciones 10x más rápidas

#### 2. Volumen Cached para Código
```yaml
volumes:
  - ..:/workspace:cached
```
**Beneficio:** Mejor rendimiento I/O en macOS/Windows

#### 3. Limpieza de Capas Docker
```dockerfile
RUN apk add --no-cache ... \
    && rm -rf /var/cache/apk/*
```
**Beneficio:** Imagen 30-40% más pequeña

#### 4. Healthcheck con Start Period
```yaml
healthcheck:
  start_period: 10s
```
**Beneficio:** Evita falsos negativos durante inicialización

### Mantenibilidad

#### 1. Metadata y Labels
```yaml
labels:
  com.callcenter.service: "django-app"
  com.callcenter.environment: "development"
```
**Beneficio:** Fácil identificación y filtrado de contenedores

#### 2. Comentarios Exhaustivos
Todos los archivos tienen comentarios explicando decisiones técnicas
**Beneficio:** Onboarding más rápido de nuevos desarrolladores

#### 3. Comandos Named en Lifecycle Hooks
```json
"onCreateCommand": {
  "install-dev": "pip install -r requirements/dev.txt",
  "verify": "python -c 'import django'"
}
```
**Beneficio:** Debugging más fácil, logs más claros

#### 4. Nombres Explícitos de Volúmenes
```yaml
volumes:
  pg_data:
    name: callcenter_pg_data
```
**Beneficio:** No hay conflictos entre proyectos

### Costo-Efectividad

#### 1. Profiles para Servicios Opcionales
```yaml
profiles: ["mariadb"]
```
**Beneficio:** Solo pagas por lo que usas

#### 2. Shutdown Action Configurado
```json
"shutdownAction": "stopContainer"
```
**Beneficio:** No cobra cuando cierras VSCode

#### 3. Imagen Alpine
```dockerfile
FROM python:3.12-alpine3.19
```
**Beneficio:** 80% más pequeña que Debian

#### 4. Prebuild Nativo
GitHub construye la imagen automáticamente
**Beneficio:** $0 costo en Actions, incluido en plan

### Desarrollo

#### 1. Restart Policy
```yaml
restart: unless-stopped
```
**Beneficio:** Servicios se recuperan automáticamente de crashes

#### 2. Init Process
```yaml
init: true
```
**Beneficio:** Manejo correcto de señales (SIGTERM, SIGKILL)

#### 3. File Associations Automáticas
```json
"files.associations": {
  "**/templates/**/*.html": "django-html"
}
```
**Beneficio:** Syntax highlighting y autocompletado correctos

#### 4. Extensiones Pre-instaladas
16 extensiones seleccionadas cuidadosamente
**Beneficio:** Entorno listo sin configuración manual

---

## Consideraciones de Producción

### NO usar este setup directamente en producción

Este entorno está optimizado para **desarrollo**. Para producción considera:

#### Cambios Necesarios:
1. **Servidor de aplicación:**
   ```
   Apache + mod_wsgi (según tu estándar de ops)
   NO: python manage.py runserver
   ```

2. **Secrets management:**
   ```
   Usar secrets manager (AWS Secrets, Azure Key Vault, etc.)
   NO: .env files
   ```

3. **Bases de datos:**
   ```
   Instancias gestionadas (RDS, CloudSQL, etc.)
   NO: Contenedores Docker
   ```

4. **Volúmenes:**
   ```
   Storage persistente real
   NO: Docker volumes
   ```

5. **Networking:**
   ```
   Load balancers, SSL/TLS
   NO: Expose directo de puertos
   ```

6. **Monitoring:**
   ```
   (Según restricciones: NO Prometheus/Grafana)
   Logs estructurados + parsing externo
   ```

7. **Usuario:**
   ```
   Usuario específico de app con permisos mínimos
   NO: Usuario genérico 'django'
   ```

### Compatibilidad con Restricciones de Ops

Este setup respeta tus restricciones:
- ✅ NO incluye Redis
- ✅ NO incluye Celery
- ✅ NO incluye Email/SMTP
- ✅ NO incluye Elasticsearch
- ✅ NO incluye Prometheus/Grafana
- ✅ NO incluye WebSockets

Para producción usarás:
- ✅ Apache + mod_wsgi (estándar del equipo)
- ✅ PostgreSQL (gestionado por ops)
- ✅ MariaDB (si disponible en infraestructura)

---

Esta arquitectura proporciona un balance óptimo entre velocidad de desarrollo, costo de operación y mantenibilidad del sistema.