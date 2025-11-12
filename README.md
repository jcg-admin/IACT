# Call Center Analytics

Repositorio monolítico para la plataforma de analítica de centros de contacto (IACT) con Django 5, PostgreSQL y MariaDB.

> **Nota sobre el estado del proyecto**: Actualmente en fase de consolidación documental y alineación de código con documentación. Algunas funcionalidades descritas están planificadas pero no implementadas. Consulta las secciones marcadas como "✅ Implementado" vs "📋 Planificado" para distinguir entre lo actual y lo futuro.

## Estado actual del repositorio

### ✅ Implementado
- **Documentación activa**: centralizada en [`docs/index.md`](docs/index.md)
- **Scripts utilitarios**: en [`scripts/`](scripts/README.md) - validaciones, gates de CI y herramientas de soporte
- **Infraestructura CPython**: builder completo en [`infrastructure/cpython/`](infrastructure/cpython/README.md)
- **Registros temporales**: almacenados manualmente en [`logs_data/`](logs_data/README.md)
- **Histórico**: contenido legado preservado en [`respaldo/docs_legacy/`](respaldo/docs_legacy/README.md)

### 📋 Planificado
- Sistema automatizado de métricas DORA
- Scripts de gestión de requisitos
- Pipeline completo de SDLC con agentes IA
- Automatización de deployment con GitHub Actions

## Inicio rápido

### Requisitos locales
- Python 3.11+
- [Vagrant](https://developer.hashicorp.com/vagrant/install) (para bases de datos)
- VirtualBox 7+
- Cliente PostgreSQL (`postgresql-client`)
- Cliente MariaDB (`mariadb-client`)

### Setup de entorno

1. **Clonar repositorio**:
   ```bash
   git clone https://github.com/2-Coatl/IACT---project.git
   cd IACT---project
   ```

2. **Crear entorno virtual Python**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **⚠️ Levantar bases de datos** (requerido):
   ```bash
   vagrant up  # Levanta PostgreSQL:15432 y MariaDB:13306
   ```

4. **Verificar servicios** (✅ Runbook disponible, 📋 script automatizado pendiente):
   - Guía manual: [`docs/operaciones/verificar_servicios.md`](docs/operaciones/verificar_servicios.md)
   - Script automatizado: `./scripts/verificar_servicios.sh` (📋 Pendiente de implementar)

## Flujo de desarrollo

### 1. Configurar variables de entorno

Crea un archivo `.env` en la raíz con las credenciales de bases de datos:

```bash
# PostgreSQL (analytics)
DB_ANALYTICS_HOST=127.0.0.1
DB_ANALYTICS_PORT=15432
DB_ANALYTICS_NAME=iact_analytics
DB_ANALYTICS_USER=django_user
DB_ANALYTICS_PASSWORD=django_pass

# MariaDB (IVR read-only)
DB_IVR_HOST=127.0.0.1
DB_IVR_PORT=13306
DB_IVR_NAME=ivr_data
DB_IVR_USER=django_user
DB_IVR_PASSWORD=django_pass
```

### 2. Ejecutar migraciones

```bash
python manage.py migrate
```

### 3. Crear superusuario

```bash
python manage.py createsuperuser
```

### 4. Ejecutar tests

✅ **Implementado**:
```bash
# Tests completos
./scripts/run_all_tests.sh

# Solo backend
pytest

# Solo validaciones
./scripts/validate_critical_restrictions.sh
```

📋 **Planificado**: Suite completa con cobertura DORA metrics

### 5. Desarrollo local

📋 **Pendiente**: El servidor de desarrollo Django aún no está configurado en este proyecto.

**Alternativa temporal**: Consulta [`docs/gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md`](docs/gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md)

## Infraestructura CPython
Los scripts disponibles dentro de `infrastructure/cpython/scripts/` son:

| Script | Descripción | Ejemplo |
| --- | --- | --- |
| `build_cpython.sh` | Compila CPython dentro de la VM o desde el host. | `./infrastructure/cpython/scripts/build_cpython.sh 3.12.6` |
| `validate_build.sh` | Verifica la integridad del artefacto generado (`.tgz` + `.sha256`). | `./infrastructure/cpython/scripts/validate_build.sh cpython-3.12.6-ubuntu20.04-build1.tgz` |
| `install_prebuilt_cpython.sh` | Instala un artefacto precompilado existente en un destino (`INSTALLPREFIX`). | `VERSION=3.12.6 INSTALLPREFIX=/opt/python ./infrastructure/cpython/scripts/install_prebuilt_cpython.sh` |

Consulta [`docs/infrastructure/README.md`](docs/infrastructure/README.md) y [`docs/infrastructure/CHANGELOG-cpython.md`](docs/infrastructure/CHANGELOG-cpython.md) para conocer más detalles sobre estos flujos.

## Calidad y contribución

### Tests y validación (✅ Parcialmente implementado)

Ejecuta validaciones antes de abrir un PR:

```bash
# ✅ Tests unitarios disponibles
pytest -c docs/pytest.ini docs/testing

# ✅ Validaciones de shell y gates en cascada
./scripts/run_all_tests.sh --skip-frontend --skip-security

# ✅ Validaciones de restricciones críticas (RNF-002: NO Redis)
./scripts/validate_critical_restrictions.sh
```

### Métricas de calidad (📋 Automatización pendiente)

**Targets del proyecto**:
- Cobertura de código: >= 80%
- Test Pyramid: 60% unit / 30% integration / 10% E2E
- Complejidad ciclomática: <= 10
- MTTR para bugs críticos: <= 2 días

**Estado actual**: Las métricas se calculan manualmente. Ver [`logs_data/SCHEMA.md`](logs_data/SCHEMA.md)

### Workflow de commits

1. **Sigue TDD**: Red → Green → Refactor
2. **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
3. **Evita `--no-verify`**: Si un hook falla, corrígelo en lugar de saltearlo
4. **Coverage mínimo**: 80% en módulos Python modificados

### Guías y estándares (✅ Documentadas)

- **[Guía de Estilo](docs/gobernanza/GUIA_ESTILO.md)** - Convenciones obligatorias (NO emojis, Conventional Commits)
- **[Procedimiento de Desarrollo Local](docs/gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md)** - Setup detallado
- **[Guía Completa de Desarrollo de Features](docs/gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)** - Proceso end-to-end
- **[Estrategia de QA](docs/gobernanza/procesos/qa/ESTRATEGIA_QA.md)** - Testing strategy

## Arquitectura y Stack

### Stack técnico (✅ Implementado)
- **Backend**: Django 5.1, Python 3.11+
- **Bases de datos**: 
  - PostgreSQL 16 (analytics, sessions, metrics)
  - MariaDB 10.11 (IVR read-only)
  - 📋 Cassandra (logs - planificado)
- **Frontend**: 📋 React + Redux Toolkit (planificado)
- **Infrastructure**: Vagrant, VirtualBox, CPython builder

### Restricciones arquitectónicas críticas (✅ Validadas)

⚠️ **RNF-002**: Sesiones DEBEN estar en base de datos
```python
# PROHIBIDO
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Redis/Memcached

# OBLIGATORIO  
SESSION_ENGINE = 'django.contrib.sessions.backends.db'     # PostgreSQL
```

Otras restricciones:
- ❌ NO Redis, Memcached, RabbitMQ, Celery
- ❌ NO MongoDB, Elasticsearch  
- ❌ NO Emojis en código/docs
- ✅ Scripts primero, CI/CD después

Ver: [`docs/gobernanza/estilos/GUIA_ESTILO.md`](docs/gobernanza/estilos/GUIA_ESTILO.md)

### Documentación de arquitectura (✅ Disponible)
- ADRs: [`docs/adr/`](docs/adr/)
- Lineamientos: [`docs/arquitectura/`](docs/arquitectura/)
- Patrones: [`docs/backend/arquitectura/`](docs/backend/arquitectura/)

## Navegación por rol

### Desarrollador Backend
- [`docs/backend/`](docs/backend/) - Arquitectura y diseño
- [`docs/backend/requisitos/`](docs/backend/requisitos/) - Requisitos de negocio
- [Guía de desarrollo](docs/gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)

### Desarrollador Frontend  
- [`docs/frontend/`](docs/frontend/) - Arquitectura y componentes
- 📋 UI en `ui/` (React) - En construcción

### QA / Testing
- [`docs/qa/`](docs/qa/) - Estrategia y checklists
- [`scripts/run_all_tests.sh`](scripts/run_all_tests.sh) - Test runner
- [`docs/testing/`](docs/testing/) - Casos de prueba

### DevOps / SRE
- [`docs/operaciones/`](docs/operaciones/) - Runbooks operacionales
- [`infrastructure/cpython/`](infrastructure/cpython/) - Builder CPython
- [`scripts/`](scripts/) - Scripts de automatización
- 📋 [`docs/dora/`](docs/dora/) - DORA metrics (planificado)

### Arquitecto
- [`docs/adr/`](docs/adr/) - Architecture Decision Records
- [`docs/arquitectura/`](docs/arquitectura/) - Lineamientos generales
- [`docs/gobernanza/`](docs/gobernanza/) - Procesos y estándares

### Product Owner / BA
- [`docs/requisitos/`](docs/requisitos/) - Análisis de negocio
- [`docs/backend/requisitos/`](docs/backend/requisitos/) - Requirements tracking
- 📋 Matriz de trazabilidad (planificada)

## Proyecto y planificación

### Tracking activo (📋 En consolidación)
- **Roadmap**: [`docs/proyecto/ROADMAP.md`](docs/proyecto/ROADMAP.md) - Visión Q4 2025 - Q2 2026
- **Tareas activas**: [`docs/proyecto/TAREAS_ACTIVAS.md`](docs/proyecto/TAREAS_ACTIVAS.md) - Sprint actual
- **Changelog**: [`docs/proyecto/CHANGELOG.md`](docs/proyecto/CHANGELOG.md) - Historial completo

### Revisión actual
- Plan de remediación: [`docs/plans/REV_20251112_remediation_plan.md`](docs/plans/REV_20251112_remediation_plan.md)

## Estructura de carpetas relevante
| Carpeta | Propósito |
| --- | --- |
| `docs/` | Documentación vigente, análisis y guías (ver índice consolidado). |
| `scripts/` | Scripts de validación, CI y utilidades operativas. |
| `infrastructure/` | Artefactos y herramientas de soporte (ej. builder de CPython). |
| `logs_data/` | JSON temporales y reportes generados manualmente. |
| `respaldo/` | Documentación histórica etiquetada como legado. |

## Recursos adicionales
- [Índice general de documentación](docs/index.md)
- [Guía de planes y seguimiento](docs/plans/)
- [Estrategia de git hooks](docs/ESTRATEGIA_GIT_HOOKS.md)
- [Análisis de reorganización de scripts](docs/ANALISIS_REORGANIZACION_SCRIPTS.md)
- [Guía de estilo](docs/gobernanza/GUIA_ESTILO.md)

Para dudas específicas consulta el directorio correspondiente en `docs/` o registra la pregunta en el backlog del proyecto.
