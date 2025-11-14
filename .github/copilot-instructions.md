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

## Build and Validation Process

### Environment Setup Requirements
1. Crear entorno virtual Python 3.11+
2. Instalar dependencias backend (usar `api/callcentersite/pyproject.toml`, NO hay requirements.txt en root)
3. Levantar bases de datos con Vagrant (`vagrant up` desde root o `infrastructure/vagrant/`)
4. Configurar variables de entorno (.env con credenciales DB)
5. Ejecutar migraciones Django SOLO en PostgreSQL
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

### Potential Pitfalls to Avoid
- **NUNCA** ejecutar migraciones en MariaDB (es read-only para datos IVR legacy)
- **NO** modificar directamente archivos de migración Django sin ExecPlan
- **SIEMPRE** usar Black (line-length=100) y flake8 antes de commit
- **VERIFICAR** que estás en `api/callcentersite/` antes de `python manage.py` commands
- **NO** commitear emojis (R2 principle enforcement via CI)
- **INSTALAR** pre-commit hooks: `pre-commit install && pre-commit run --all-files`

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
- `"No module named 'callcentersite'"` → cd `api/callcentersite/` antes de manage.py
- `"could not connect to server"` → `vagrant up` para levantar DBs
- `"Black would reformat"` → `black . --line-length=100`
- `"Agent not found"` → verificar `.github/copilot/agents.json` y `.agent/agents/*.md`
- `"ImportError: anthropic"` → `pip install -r scripts/coding/ai/requirements.txt`

### Compliance and Standards
- **Commits**: Usar conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Branches**: `feature/*`, `hotfix/*`, `docs`, NO commit directo a main/master
- **Code Style**: Python (PEP 8, Black 100), React (ESLint)
- **Secrets**: NUNCA commitear, usar .env, validar con gitleaks
- **Documentation**: Actualizar docs cuando cambias funcionalidad
- **Tests**: Test pyramid (70% unit, 20% integration, 10% E2E)

### Performance Optimization
- Django: usar `.select_related()`, `.prefetch_related()`, evitar N+1 queries
- React: code splitting, lazy loading routes
- CI/CD: matrix builds, caching (pip, npm), conditional jobs

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
- **Principles**: Seguir R1-R5 de `.constitucion.yaml` estrictamente
- **Agents**: Aprovechar custom agents (`@my_agent`, etc.) para tasks especializadas

---
**Version**: 2.0.0 | **Last Updated**: 2025-11-14 | **Lines**: <120
