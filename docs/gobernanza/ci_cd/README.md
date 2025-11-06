# CI/CD - Documentacion Completa

**Principio IACT**: Scripts Primero, CI/CD Despues

Los workflows de GitHub Actions son SECUNDARIOS. Los scripts shell locales son PRIMARIOS.
Todos los workflows llaman a scripts shell que funcionan offline/local.

## Indice

1. [Scripts Shell Locales](#scripts-shell-locales)
2. [Workflows GitHub Actions](#workflows-github-actions)
3. [Uso Local](#uso-local)
4. [Restricciones IACT](#restricciones-iact)

---

## Scripts Shell Locales

### Ubicacion

```
scripts/ci/
  backend_test.sh         - Tests backend Django
  frontend_test.sh        - Tests frontend React
  test_pyramid_check.sh   - Validacion test pyramid 60/30/10
  security_scan.sh        - Security scan completo
```

### 1. backend_test.sh

Ejecuta tests y validaciones de backend Django.

**Uso**:
```bash
# Ejecutar con MySQL
./scripts/ci/backend_test.sh --mysql

# Ejecutar con PostgreSQL
./scripts/ci/backend_test.sh --postgresql

# Ejecutar con ambos
./scripts/ci/backend_test.sh --all
```

**Requisitos**:
- Python 3.11+
- MySQL y/o PostgreSQL corriendo
- Variables de entorno: DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

**Que hace**:
1. Lint: flake8, black, isort
2. Validacion RNF-002 (NO Redis, sesiones en MySQL)
3. Tests con MySQL (pytest con coverage >80%)
4. Tests con PostgreSQL
5. Integration tests
6. Validacion scripts (validate_critical_restrictions.sh)

**RNF-002**: Script valida restricciones IACT automaticamente.

### 2. frontend_test.sh

Ejecuta tests y validaciones de frontend React/TypeScript.

**Uso**:
```bash
# Todos los tests
./scripts/ci/frontend_test.sh --all

# Solo unit tests
./scripts/ci/frontend_test.sh --unit

# Solo integration tests
./scripts/ci/frontend_test.sh --integration

# Solo E2E tests
./scripts/ci/frontend_test.sh --e2e
```

**Requisitos**:
- Node.js 18+
- npm dependencies instaladas (npm ci)

**Que hace**:
1. Install dependencies (si falta)
2. ESLint
3. TypeScript type checking
4. Prettier format check
5. Unit tests con Jest (coverage check)
6. Integration tests
7. E2E tests con Playwright
8. npm audit (security)

### 3. test_pyramid_check.sh

Valida que la distribucion de tests siga patron 60/30/10.

**Uso**:
```bash
./scripts/ci/test_pyramid_check.sh

# Con reporte
REPORT_FILE=test-pyramid-report.md ./scripts/ci/test_pyramid_check.sh
```

**Validaciones**:
- Unit tests >= 50% (target 60%)
- Integration tests 20-40% (target 30%)
- E2E tests <= 20% (target 10%)

**Salida**:
```
============================================
TEST PYRAMID METRICS
============================================
Total Tests: 150

Unit Tests: 90 (60%)
Integration Tests: 45 (30%)
E2E Tests: 15 (10%)
============================================

[OK] Unit tests are 60% (>= 50%)
[OK] Integration tests are 30% (20-40%)
[OK] E2E tests are 10% (<= 20%)

[OK] Test pyramid validation PASSED
```

### 4. security_scan.sh

Ejecuta escaneos de seguridad completos.

**Uso**:
```bash
./scripts/ci/security_scan.sh
```

**Que hace**:
1. Validacion RNF-002 (NO Redis, sesiones MySQL)
2. Django security checks (manage.py check --deploy)
3. Bandit (Python security)
4. Safety (Python dependencies)
5. npm audit (frontend security)
6. SQL Injection check
7. XSS protection check
8. CSRF protection check

**CRITICO**: Falla si encuentra Redis o SQL injection.

---

## Workflows GitHub Actions

Todos los workflows en `.github/workflows/` llaman a los scripts shell locales.

### 1. backend-ci.yml

Ejecuta: `scripts/ci/backend_test.sh`

**Triggers**:
- Push a main, develop, feature/**
- Pull requests a main, develop
- Paths: api/**

**Jobs**:
- lint
- test-mysql
- test-postgresql
- validate-restrictions (RNF-002)
- integration-tests
- summary

### 2. frontend-ci.yml

Ejecuta: `scripts/ci/frontend_test.sh`

**Triggers**:
- Push a main, develop, feature/**
- Pull requests a main, develop
- Paths: frontend/**

**Jobs**:
- lint
- test-unit
- test-integration
- test-e2e
- build
- accessibility
- security
- summary

### 3. test-pyramid.yml

Ejecuta: `scripts/ci/test_pyramid_check.sh`

**Triggers**:
- Push a main, develop
- Pull requests a main, develop
- Schedule: Weekly (domingos 00:00)

**Output**: Reporte en artifact + comment en PR

### 4. security-scan.yml

Ejecuta: `scripts/ci/security_scan.sh`

**Triggers**:
- Push a main, develop
- Pull requests a main, develop
- Schedule: Weekly (lunes 02:00)

**Jobs**:
- bandit-scan
- npm-audit
- safety-check
- django-security-check
- trivy-scan
- secrets-scan
- sql-injection-check
- xss-check
- csrf-check
- generate-security-report

### 5. deploy.yml

Deployment workflow con blue-green strategy.

**Triggers**:
- Push a main (staging)
- Tag v*.*.* (production)
- Manual workflow_dispatch

**Jobs**:
- pre-deployment-checks
- run-tests
- build-backend
- build-frontend
- deploy-staging
- deploy-production
- post-deployment-monitoring

**Features**:
- Blue-green deployment (zero downtime)
- Database backup automatico
- Rollback automatico en health check fail
- RNF-002 validation

### 6. migrations.yml

Validacion automatica de migraciones Django.

**Triggers**:
- Push/PR con cambios en: api/**/migrations/**, api/**/models.py

**Jobs**:
- detect-migrations
- validate-migrations (MySQL + PostgreSQL)
- check-migration-safety (dangerous operations)
- generate-migration-report

### 7. infrastructure-ci.yml

Validacion de infraestructura y scripts.

**Triggers**:
- Push/PR con cambios en: infrastructure/**, scripts/**

**Jobs**:
- validate-shell-scripts (shellcheck)
- test-validation-scripts
- validate-terraform
- validate-docker
- validate-configurations (YAML/JSON)
- test-health-check

### 8. incident-response.yml

Workflow manual para manejo de incidentes.

**Triggers**:
- Manual workflow_dispatch

**Inputs**:
- incident_type: production_down, performance_degradation, security_breach, etc.
- severity: critical, high, medium, low
- description
- affected_services

**Jobs**:
- create-incident-issue (GitHub issue automatico)
- gather-diagnostics
- execute-incident-playbook (playbook por tipo)
- notify-team (via InternalMessage, NO email per RNF-002)

---

## Uso Local

### Setup Inicial

```bash
# Instalar dependencias Python
cd api
pip install -r requirements.txt
pip install flake8 black isort bandit safety pytest pytest-django pytest-cov

# Instalar dependencias Node.js
cd frontend
npm ci
```

### Ejecutar Tests Localmente

```bash
# Backend
./scripts/ci/backend_test.sh --all

# Frontend
./scripts/ci/frontend_test.sh --all

# Test Pyramid
./scripts/ci/test_pyramid_check.sh

# Security Scan
./scripts/ci/security_scan.sh
```

### Ejecutar Antes de Push

```bash
# Script completo de pre-push
#!/bin/bash
set -e

echo "Running pre-push checks..."

./scripts/ci/backend_test.sh --mysql
./scripts/ci/frontend_test.sh --all
./scripts/ci/test_pyramid_check.sh
./scripts/ci/security_scan.sh

echo "All checks passed! Safe to push."
```

---

## Restricciones IACT

Todos los scripts y workflows validan:

### RNF-002: NO Redis, Sesiones en MySQL

**Validacion automatica**:
```bash
# Check NO Redis
if grep -r "redis" api/callcentersite/settings*.py; then
    echo "ERROR: Redis prohibited by RNF-002"
    exit 1
fi

# Check session backend
if ! grep -q "django.contrib.sessions.backends.db" api/callcentersite/settings*.py; then
    echo "ERROR: SESSION_ENGINE must be django.contrib.sessions.backends.db"
    exit 1
fi
```

**Enforzamiento**:
- backend-ci.yml: Job `validate-restrictions`
- security-scan.yml: Step "Validate IACT RNF-002"
- deploy.yml: Pre-deployment checks
- scripts/ci/backend_test.sh: Step 2
- scripts/ci/security_scan.sh: Step 1

### NO Email/SMTP

**Uso**: InternalMessage para notificaciones

**Validacion**:
- Warning si se detecta send_mail, EmailMessage, EmailMultiAlternatives
- Requerido: Usar InternalMessage.objects.create()

### NO Emojis, NO Iconos

**GUIA_ESTILO.md**: Texto ASCII puro

**Output scripts**:
- [OK] = exito
- [FAIL] = fallo
- [WARNING] = advertencia
- [INFO] = informacion

### Scripts Primero, CI/CD Despues

**Filosofia**:
1. Crear script shell local
2. Probar localmente
3. Workflow llama al script

**Beneficios**:
- Funciona sin GitHub Actions
- Debugging mas facil
- Reutilizable
- Portable

---

## Referencias

- SDLC Process: docs/gobernanza/procesos/SDLC_PROCESS.md
- DevOps Automation: docs/gobernanza/procesos/DEVOPS_AUTOMATION.md
- Workflows Index: docs/gobernanza/procesos/INDICE_WORKFLOWS.md
- Guia de Estilo: docs/gobernanza/estilos/GUIA_ESTILO.md
- RNF-002: docs/backend/requisitos/restricciones_y_lineamientos.md

---

**Version**: 1.0
**Fecha**: 2025-11-06
**Autor**: SDLCOrchestratorAgent
