# CI/CD - Indice General de Documentacion

Documentacion completa del sistema CI/CD de IACT.

## Principios IACT

1. **Scripts Primero, CI/CD Despues**: Scripts shell funcionan offline/local
2. **NO Redis**: RNF-002 - Sesiones en MySQL
3. **NO Email**: InternalMessage para notificaciones
4. **NO Emojis**: Texto ASCII puro

---

## Documentacion Principal

### Guias Generales

- [README.md](README.md) - Vista general del sistema CI/CD
- [GUIA_USO.md](GUIA_USO.md) - Guias de uso por rol (Developer, QA, DevOps)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemas comunes y soluciones
- [EJEMPLOS.md](EJEMPLOS.md) - Flujos completos end-to-end

### Workflows GitHub Actions

Documentacion detallada de cada workflow (8 workflows):

1. [backend-ci.md](workflows/backend-ci.md) - Tests Django (MySQL/PostgreSQL)
2. [frontend-ci.md](workflows/frontend-ci.md) - Tests React/TypeScript
3. [test-pyramid.md](workflows/test-pyramid.md) - Validacion pyramid 60/30/10
4. [deploy.md](workflows/deploy.md) - Blue-green deployment
5. [migrations.md](workflows/migrations.md) - Validacion migraciones
6. [infrastructure-ci.md](workflows/infrastructure-ci.md) - Shellcheck, Terraform
7. [security-scan.md](workflows/security-scan.md) - Security scanning completo
8. [incident-response.md](workflows/incident-response.md) - Manejo de incidentes

### Scripts Shell Locales

Documentacion detallada de cada script (4 scripts):

1. [backend_test.md](scripts/backend_test.md) - Tests Django local
2. [frontend_test.md](scripts/frontend_test.md) - Tests React local
3. [test_pyramid_check.md](scripts/test_pyramid_check.md) - Pyramid validation local
4. [security_scan.md](scripts/security_scan.md) - Security scan local

---

## Quick Start

### Developer

```bash
# Antes de push
./scripts/ci/backend_test.sh --mysql
./scripts/ci/frontend_test.sh --unit
./scripts/ci/security_scan.sh

# Ver docs/gobernanza/ci_cd/GUIA_USO.md#developer
```

### QA

```bash
# Tests completos
./scripts/ci/backend_test.sh --all
./scripts/ci/frontend_test.sh --all
./scripts/ci/test_pyramid_check.sh

# Ver docs/gobernanza/ci_cd/GUIA_USO.md#qa
```

### DevOps

```bash
# Pre-deployment validation
./scripts/ci/security_scan.sh
./scripts/validate_critical_restrictions.sh

# Ver docs/gobernanza/ci_cd/GUIA_USO.md#devops
```

---

## Estructura de Archivos

```
docs/gobernanza/ci_cd/
├── README.md                  # Vista general
├── INDICE.md                  # Este archivo
├── GUIA_USO.md               # Guias por rol
├── TROUBLESHOOTING.md        # Problemas comunes
├── EJEMPLOS.md               # Flujos completos
├── workflows/                # Docs workflows (8)
│   ├── backend-ci.md
│   ├── frontend-ci.md
│   ├── test-pyramid.md
│   ├── deploy.md
│   ├── migrations.md
│   ├── infrastructure-ci.md
│   ├── security-scan.md
│   └── incident-response.md
└── scripts/                  # Docs scripts (4)
    ├── backend_test.md
    ├── frontend_test.md
    ├── test_pyramid_check.md
    └── security_scan.md

scripts/ci/                   # Scripts ejecutables
├── backend_test.sh
├── frontend_test.sh
├── test_pyramid_check.sh
└── security_scan.sh

.github/workflows/            # Workflows GitHub Actions
├── backend-ci.yml
├── frontend-ci.yml
├── test-pyramid.yml
├── deploy.yml
├── migrations.yml
├── infrastructure-ci.yml
├── security-scan.yml
└── incident-response.yml
```

---

## Documentacion Relacionada

### Gobernanza

- [SDLC_PROCESS.md](../procesos/SDLC_PROCESS.md) - Proceso SDLC completo
- [DEVOPS_AUTOMATION.md](../procesos/DEVOPS_AUTOMATION.md) - Automatizacion DevOps
- [AGENTES_SDLC.md](../procesos/AGENTES_SDLC.md) - Sistema multi-agente SDLC
- [INDICE_WORKFLOWS.md](../procesos/INDICE_WORKFLOWS.md) - Indice workflows completo

### Backend

- [restricciones_y_lineamientos.md](../../backend/requisitos/restricciones_y_lineamientos.md) - RNF-002

### Estilos

- [GUIA_ESTILO.md](../estilos/GUIA_ESTILO.md) - NO emojis, NO iconos

---

## Metricas y KPIs

### Code Quality

- **Coverage**: > 80% (enforced)
- **Lint**: flake8, black, isort, ESLint
- **Type Safety**: mypy, TypeScript strict

### Test Pyramid

- **Unit**: 60% target (>= 50% required)
- **Integration**: 30% target (20-40% range)
- **E2E**: 10% target (<= 20% max)

### Security

- **Critical Vulnerabilities**: 0 tolerance
- **High Vulnerabilities**: < 5
- **RNF-002 Compliance**: 100%

### Deployment

- **Deployment Frequency**: Daily (staging), Weekly (production)
- **Lead Time**: < 1 day
- **Change Failure Rate**: < 15%
- **MTTR**: < 1 hour

---

## Actualizaciones

| Fecha | Version | Cambios |
|-------|---------|---------|
| 2025-11-06 | 1.0 | Documentacion inicial completa |

---

**Mantenido por**: DevOps Team
**Ultima revision**: 2025-11-06
