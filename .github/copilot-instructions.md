# Copilot Onboarding Instructions

## Repository Overview

### Project Description
Sistema de gestión de call center que integra backend Django con frontend React, diseñado para manejar comunicaciones, seguimiento de llamadas y administración de recursos de contact center.

### Repository Characteristics
- **Project Type**: Web application for call center management
- **Total Size**: ~100 archivos principales
- **Primary Languages**: Python (Backend), JavaScript/React (Frontend)
- **Key Frameworks**: Django 5.x, React, Webpack
- **Target Runtimes**: Python 3.11+, Node.js 16+
- **Deployment Environment**: Web-based application

### Current State
The repository is in **consolidation phase**, aligning code with extensive documentation. Some features are documented but not yet implemented (marked as [PLANIFICADO] vs [IMPLEMENTADO] in docs).

## Build and Validation Process

### Environment Setup Requirements
1. Crear entorno virtual Python 3.11+
2. Instalar dependencias backend (usar `api/callcentersite/pyproject.toml`, **NO** hay requirements.txt en root)
3. Levantar bases de datos con Vagrant (`vagrant up` desde root o `infrastructure/vagrant/`)
4. Configurar variables de entorno (.env con credenciales DB)
5. Ejecutar migraciones Django **SOLO** en PostgreSQL (nunca en MariaDB)
6. Instalar dependencias frontend (`ui/package.json`)

### Critical Setup Steps
```bash
# Backend
python3.11 -m venv .venv && source .venv/bin/activate
cd api/callcentersite && pip install -e .
python manage.py migrate  # SOLO PostgreSQL

# Frontend
cd ui && npm install

# Databases (en root o infrastructure/vagrant/)
vagrant up  # PostgreSQL:15432, MariaDB:13306
```

### Database Architecture (CRITICAL)
**Two-database setup** managed via Vagrant:

1. **PostgreSQL** (analytics, port 15432)
   - Purpose: Django models, analytics data
   - **Run migrations here**: `python manage.py migrate`
   - Credentials: DB_ANALYTICS_* variables in .env

2. **MariaDB** (IVR read-only, port 13306)
   - Purpose: Legacy IVR data
   - **NEVER run migrations here** - read-only via Django database router
   - Credentials: DB_IVR_* variables in .env

### Potential Pitfalls to Avoid
- **NUNCA** ejecutar migraciones en MariaDB (es read-only para datos IVR legacy)
- **NO** modificar directamente archivos de migración Django sin ExecPlan
- **SIEMPRE** usar Black (line-length=100) y flake8 antes de commit
- **VERIFICAR** que estás en `api/callcentersite/` antes de `python manage.py` commands
- **NO** commitear emojis (R2 principle enforcement via CI/emoji-validation.yml)
- **INSTALAR** pre-commit hooks: `pre-commit install && pre-commit run --all-files`
- **EVITAR** cambios en .github/agents/ directory (contiene instrucciones para otros agentes)
- **NO** usar `git rebase` o `git reset --hard` (force push no disponible)

## Architectural Overview

### Directory Structure
- `api/callcentersite/`: Django backend principal (manage.py, settings, apps)
- `ui/`: React frontend (Webpack config, componentes)
- `infrastructure/vagrant/`: Vagrantfile para PostgreSQL + MariaDB
- `scripts/`: 200+ scripts utilitarios (CI, automation, SDLC agents)
- `docs/`: 1000+ archivos documentación (MkDocs, AI guides, runbooks)
- `.agent/`: Definiciones de agentes custom (my_agent, gitops_agent, etc.)
- `.github/copilot/`: Configuración agentes custom (agents.json)

### Configuration Files Location
- Django settings: `api/callcentersite/callcentersite/settings.py`
- React config: `ui/package.json`, `ui/webpack.config.js`
- Automation principles: `.constitucion.yaml` (5 principles: idempotencia, sin emojis, verificación, documentación, trazabilidad)
- Pre-commit hooks: `.pre-commit-config.yaml`
- Custom agents: `.github/copilot/agents.json`

### Continuous Integration Checks
- Python: Black, flake8, pytest, Bandit (security), safety (CVE)
- JavaScript: ESLint, Prettier, Jest
- Django: migrations check, test-pyramid.yml
- Security: gitleaks (secrets), CodeQL
- Docs: markdown linting, link checking
- Meta: emoji-validation.yml (R2 enforcement), architecture-check.yml

### Hidden Dependencies
- **Dual-database**: PostgreSQL (analytics, Django models) + MariaDB (IVR read-only via router)
- **No root Makefile**: usar scripts documentados en `scripts/`
- **ExecPlans**: documentos de planificación para features complejos (`.agent/PLANS.md`, `docs/plans/`)
- **30+ Python SDLC agents**: en `scripts/coding/ai/` con soporte multi-LLM (Claude, ChatGPT, HuggingFace)
- **5 custom Copilot agents**: `@my_agent`, `@gitops_agent`, `@release_agent`, `@dependency_agent`, `@security_agent`

## Agent Interaction Guidelines

### Exploration Strategy
1. Leer completamente estas instrucciones (ya lo hiciste)
2. Consultar README.md del proyecto para overview
3. Revisar `.constitucion.yaml` para automation principles
4. Buscar ExecPlans en `docs/plans/` si feature es compleja
5. Validar setup: `vagrant status`, `pre-commit run --all-files`

### Search and Exploration Recommendations
- Realizar búsquedas adicionales SOLO si:
  1. Estas instrucciones son incompletas para tu task específica
  2. Necesitas detalles de implementación muy específicos no cubiertos aquí
  3. La información parece desactualizada
- **PRIORIZAR**: Confiar en estas instrucciones antes que búsqueda extensiva

### Validation Approach
- Ejecutar tests: `cd api/callcentersite && pytest`, `cd ui && npm test`
- Validar formatting: `black . --line-length=100`, `pre-commit run --all-files`
- Verificar CI localmente: `./scripts/ci-local.sh` (si disponible)
- Comprobar databases: `vagrant status`, conectar via `vagrant ssh postgres/mariadb`

### Error Handling Recommendations
**Common Errors & Solutions**:

1. **`"No module named 'callcentersite'"`**
   - Causa: Estás en directorio incorrecto
   - Solución: `cd api/callcentersite/` antes de ejecutar `python manage.py`

2. **`"django.db.utils.OperationalError: could not connect to server"`**
   - Causa: Bases de datos no están corriendo
   - Solución: `vagrant up` en root o `infrastructure/vagrant/`
   - Verificar: `vagrant status`

3. **`"Black would reformat"`**
   - Causa: Código no formateado según estándar Black
   - Solución: `black . --line-length=100` o `pre-commit run black --all-files`

4. **`"Agent not found: @agent_name"`**
   - Causa: Configuración de agentes custom falta o incorrecta
   - Solución: Verificar `.github/copilot/agents.json` existe y `.agent/agents/*.md` están presentes

5. **`"ImportError: No module named 'anthropic'"`**
   - Causa: Dependencias de agentes AI no instaladas
   - Solución: `pip install -r scripts/coding/ai/requirements.txt`

6. **Emoji validation failures**
   - Causa: Emojis en código/automation outputs (viola R2)
   - Solución: Remover todos los emojis, usar texto plano
   - Workflow: `.github/workflows/emoji-validation.yml`

7. **Migration errors on MariaDB**
   - Causa: Intentando migrar base de datos read-only
   - Solución: **NUNCA** migrar MariaDB, solo PostgreSQL
   - Verificar: Database router en `settings.py`

### Compliance and Standards
- **Commits**: Usar conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.)
- **Branches**: `feature/*`, `hotfix/*`, `docs`, **NO** commit directo a main/master
- **Code Style**: 
  - Python: PEP 8, Black (line-length=100), flake8
  - JavaScript/React: ESLint, Prettier
- **Secrets**: **NUNCA** commitear, usar .env, validar con gitleaks
- **Documentation**: Actualizar docs cuando cambias funcionalidad
- **Tests**: Test pyramid (70% unit, 20% integration, 10% E2E)

### Testing Strategy
- **Backend**: `cd api/callcentersite && pytest` (con coverage: `pytest --cov=.`)
- **Frontend**: `cd ui && npm test`
- **Pre-commit**: `pre-commit run --all-files` (ejecuta Black, flake8, ESLint, etc.)
- **CI Local**: `./scripts/ci-local.sh` (si disponible, simula CI localmente)

### Performance Optimization
- Django: usar `.select_related()`, `.prefetch_related()`, evitar N+1 queries
- React: code splitting, lazy loading routes
- CI/CD: matrix builds, caching (pip, npm), conditional jobs

### Security Considerations
- **Secrets Management**: Usar .env para desarrollo, GitHub Secrets para CI/CD
- **Security Scanning**: Bandit (Python), Safety (CVE), gitleaks (secrets), CodeQL
- **Database**: Credenciales separadas PostgreSQL vs MariaDB, MariaDB read-only
- **Validation**: Gitleaks corre en CI para detectar secrets expuestos

### Git Workflow Best Practices
- **Branch Strategy**: main (producción) → develop (integración) → feature/* (desarrollo)
- **Conventional Commits**: `type(scope): subject` (types: feat, fix, docs, style, refactor, test, chore, ci)
- **Pre-commit Checks**: Black, flake8, ESLint, YAML/JSON validation, no debug statements
- **No Force Push**: `git reset --hard` y `git rebase` no disponibles (no force push)

### Key Commands Reference
```bash
# Backend
cd api/callcentersite
python manage.py runserver
python manage.py migrate
python manage.py test

# Frontend
cd ui && npm install && npm run dev

# Database
vagrant up  # Start both DBs
vagrant ssh postgres
vagrant ssh mariadb

# Quality
pre-commit run --all-files
black . --line-length=100
pytest --cov=.

# Custom Agents
@my_agent: [programming task]
@gitops_agent: [git operation]
@security_agent: [security audit]
```

### Final Recommendations
- **Simplicidad**: Evitar over-engineering
- **Legibilidad**: Código debe ser auto-explicativo
- **Tests**: Agregar tests para nuevas funcionalidades
- **Docs**: Mantener docs sincronizadas con código
- **Principles**: Seguir R1-R5 de `.constitucion.yaml` estrictamente:
  - R1: Idempotencia (operaciones repetibles con mismo resultado)
  - R2: Sin Emojis (texto plano para compatibilidad automation)
  - R3: Verificación (validar cada cambio)
  - R4: Documentación (documentar cada modificación)
  - R5: Trazabilidad (logging completo con contexto)
- **Agents**: Aprovechar custom agents (`@my_agent`, etc.) para tasks especializadas
- **ExecPlans**: Para features complejos, crear ExecPlan en `.agent/PLANS.md` format antes de implementar

### When Things Go Wrong
- **Check Docs**: `docs/operaciones/` tiene runbooks para troubleshooting
- **Verify Services**: `./scripts/verificar_servicios.sh` valida configuración
- **Review Logs**: Django logs, workflow logs en `.github/workflows/`, agent outputs
- **Consult Custom Agents**: Usar `@security_agent` para auditorías, `@gitops_agent` para Git issues

---
**Version**: 2.1.0 | **Last Updated**: 2025-11-14 | **Lines**: ~220 | **Status**: Enhanced with error prevention details
