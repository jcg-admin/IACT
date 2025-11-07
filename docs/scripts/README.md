# Scripts del Proyecto IACT

Documentacion completa del sistema de scripts del proyecto IACT.

## Tabla de Contenidos

- [Inicio Rapido](#inicio-rapido)
- [Scripts SDLC](#scripts-sdlc)
- [Scripts de CI/CD](#scripts-de-cicd)
- [Scripts de Metricas](#scripts-de-metricas)
- [Scripts de Requisitos](#scripts-de-requisitos)
- [Scripts de Disaster Recovery](#scripts-de-disaster-recovery)
- [Scripts de Base de Datos](#scripts-de-base-de-datos)
- [Scripts de Testing](#scripts-de-testing)
- [Scripts de Deployment](#scripts-de-deployment)
- [Scripts de Documentacion](#scripts-de-documentacion)
- [Templates](#templates)
- [Recursos Adicionales](#recursos-adicionales)

## Inicio Rapido

Para comenzar rapidamente con los scripts mas usados, consulta la [Guia de Inicio Rapido (QUICKSTART.md)](./QUICKSTART.md).

## Scripts SDLC

### sdlc_agent.py

**Path:** `/home/user/IACT---project/scripts/sdlc_agent.py`

CLI principal para ejecutar agentes SDLC (Planning, Design, Testing, Deployment).

**Como ejecutar:**
```bash
# Ejecutar fase de Planning
python scripts/sdlc_agent.py --phase planning --input "Feature: Sistema de notificaciones"

# Ejecutar pipeline completo
python scripts/sdlc_agent.py --pipeline --input "Feature: Dashboard de metricas"

# Dry-run (no guarda artefactos)
python scripts/sdlc_agent.py --phase planning --input "..." --dry-run
```

**Documentacion completa:** [sdlc-agent-guide.md](./sdlc-agent-guide.md)

### Agentes SDLC (scripts/ai/agents/)

20+ agentes especializados para automatizar el ciclo SDLC:

- **sdlc_orchestrator.py** - Orquestador del pipeline SDLC completo
- **sdlc_planner.py** - Genera issues estructurados desde feature requests
- **sdlc_design.py** - Genera HLD, LLD, ADRs y diagramas
- **sdlc_testing.py** - Genera estrategias de testing y test cases
- **sdlc_deployment.py** - Genera planes de deployment y rollback
- **sdlc_feasibility.py** - Analiza viabilidad tecnica y riesgos
- **business_analysis_generator.py** - Genera analisis de negocio
- **business_analysis_pipeline.py** - Pipeline de analisis de negocio
- **documentation_sync_agent.py** - Sincroniza documentacion
- **traceability_matrix_generator.py** - Genera matriz de trazabilidad
- **pdca_automation_agent.py** - Automatizacion PDCA
- **dora_sdlc_integration.py** - Integracion DORA metrics con SDLC

**Documentacion completa:** [sdlc-agents-reference.md](./sdlc-agents-reference.md)

## Scripts de CI/CD

### backend_test.sh

**Path:** `/home/user/IACT---project/scripts/ci/backend_test.sh`

Ejecuta suite completa de tests del backend (pytest).

**Como ejecutar:**
```bash
./scripts/ci/backend_test.sh
```

### frontend_test.sh

**Path:** `/home/user/IACT---project/scripts/ci/frontend_test.sh`

Ejecuta suite completa de tests del frontend (Jest + Cypress).

**Como ejecutar:**
```bash
./scripts/ci/frontend_test.sh
```

### security_scan.sh

**Path:** `/home/user/IACT---project/scripts/ci/security_scan.sh`

Ejecuta escaneo de seguridad (Bandit, Safety, npm audit).

**Como ejecutar:**
```bash
./scripts/ci/security_scan.sh
```

### test_pyramid_check.sh

**Path:** `/home/user/IACT---project/scripts/ci/test_pyramid_check.sh`

Valida que la distribucion de tests cumple con la piramide (60% unit, 30% integration, 10% E2E).

**Como ejecutar:**
```bash
./scripts/ci/test_pyramid_check.sh
```

**Documentacion completa:** [ci-cd-scripts.md](./ci-cd-scripts.md)

## Scripts de Metricas

### dora_metrics.py

**Path:** `/home/user/IACT---project/scripts/dora_metrics.py`

Calcula las 4 metricas DORA (Deployment Frequency, Lead Time, Change Failure Rate, MTTR).

**Como ejecutar:**
```bash
# Ultimos 30 dias
python scripts/dora_metrics.py --repo 2-Coatl/IACT---project

# Periodo especifico
python scripts/dora_metrics.py --start 2025-01-01 --end 2025-01-31 --format json

# Solo metricas de documentacion
python scripts/dora_metrics.py --docs-only
```

### generate_dora_report.sh

**Path:** `/home/user/IACT---project/scripts/generate_dora_report.sh`

Genera reporte HTML de DORA metrics.

**Como ejecutar:**
```bash
./scripts/generate_dora_report.sh
```

**Documentacion completa:** [metrics-and-reporting.md](./metrics-and-reporting.md)

## Scripts de Requisitos

### generar_indices.py

**Path:** `/home/user/IACT---project/scripts/requisitos/generar_indices.py`

Genera automaticamente indices de requisitos (RF, RNF).

**Como ejecutar:**
```bash
python scripts/requisitos/generar_indices.py
```

### validar_frontmatter.py

**Path:** `/home/user/IACT---project/scripts/requisitos/validar_frontmatter.py`

Valida que todos los requisitos tienen frontmatter YAML correcto.

**Como ejecutar:**
```bash
python scripts/requisitos/validar_frontmatter.py
```

### contar_requisitos.sh

**Path:** `/home/user/IACT---project/scripts/requisitos/contar_requisitos.sh`

Cuenta requisitos por categoria (RF, RNF).

**Como ejecutar:**
```bash
./scripts/requisitos/contar_requisitos.sh
```

### listar_requisitos.sh

**Path:** `/home/user/IACT---project/scripts/requisitos/listar_requisitos.sh`

Lista todos los requisitos del proyecto.

**Como ejecutar:**
```bash
./scripts/requisitos/listar_requisitos.sh
```

**Documentacion completa:** [requirements-management.md](./requirements-management.md)

## Scripts de Disaster Recovery

### backup_mysql.sh

**Path:** `/home/user/IACT---project/scripts/disaster_recovery/backup_mysql.sh`

Realiza backup de base de datos MySQL.

**Como ejecutar:**
```bash
./scripts/disaster_recovery/backup_mysql.sh
```

### restore_mysql.sh

**Path:** `/home/user/IACT---project/scripts/disaster_recovery/restore_mysql.sh`

Restaura backup de MySQL.

**Como ejecutar:**
```bash
./scripts/disaster_recovery/restore_mysql.sh <backup_file>
```

### backup_cassandra.sh

**Path:** `/home/user/IACT---project/scripts/disaster_recovery/backup_cassandra.sh`

Realiza backup de Cassandra (logs).

**Como ejecutar:**
```bash
./scripts/disaster_recovery/backup_cassandra.sh
```

### test_dr.sh

**Path:** `/home/user/IACT---project/scripts/disaster_recovery/test_dr.sh`

Prueba procedimientos de disaster recovery.

**Como ejecutar:**
```bash
./scripts/disaster_recovery/test_dr.sh
```

**Documentacion completa:** [disaster-recovery.md](./disaster-recovery.md)

## Scripts de Base de Datos

### validate_database_router.sh

**Path:** `/home/user/IACT---project/scripts/validate_database_router.sh`

Valida configuracion de database router (MySQL + Cassandra).

**Como ejecutar:**
```bash
./scripts/validate_database_router.sh
```

### Cassandra Scripts

- **install-cassandra.sh** - Instala Cassandra
- **configure-django.sh** - Configura Django para Cassandra
- **setup-cron-jobs.sh** - Configura cron jobs

## Scripts de Testing

### run_all_tests.sh

**Path:** `/home/user/IACT---project/scripts/run_all_tests.sh`

Ejecuta TODOS los tests del proyecto (backend + frontend).

**Como ejecutar:**
```bash
./scripts/run_all_tests.sh
```

### run_integration_tests.sh

**Path:** `/home/user/IACT---project/scripts/run_integration_tests.sh`

Ejecuta solo tests de integracion.

**Como ejecutar:**
```bash
./scripts/run_integration_tests.sh
```

## Scripts de Deployment

### deploy.sh

**Path:** `/home/user/IACT---project/scripts/deploy.sh`

Script principal de deployment (staging/production).

**Como ejecutar:**
```bash
# Deploy a staging
./scripts/deploy.sh staging

# Deploy a production
./scripts/deploy.sh production
```

### health_check.sh

**Path:** `/home/user/IACT---project/scripts/health_check.sh`

Verifica salud de la aplicacion desplegada.

**Como ejecutar:**
```bash
./scripts/health_check.sh <environment>
```

## Scripts de Documentacion

### generate_guides.py

**Path:** `/home/user/IACT---project/scripts/generate_guides.py`

Genera guias operativas automaticamente.

**Como ejecutar:**
```bash
# Generar guias P0
python scripts/generate_guides.py --priority P0

# Dry-run
python scripts/generate_guides.py --priority P0 --dry-run
```

### sync_documentation.py

**Path:** `/home/user/IACT---project/scripts/sync_documentation.py`

Sincroniza documentacion entre diferentes locations.

**Como ejecutar:**
```bash
python scripts/sync_documentation.py
```

### validar_estructura_docs.sh

**Path:** `/home/user/IACT---project/scripts/validar_estructura_docs.sh`

Valida estructura de directorio docs/.

**Como ejecutar:**
```bash
./scripts/validar_estructura_docs.sh
```

## Scripts de Validacion

### validate_critical_restrictions.sh

**Path:** `/home/user/IACT---project/scripts/validate_critical_restrictions.sh`

Valida que el codigo NO usa tecnologias prohibidas (Redis, RabbitMQ, Celery, MongoDB, Elasticsearch).

**Como ejecutar:**
```bash
./scripts/validate_critical_restrictions.sh
```

### validate_security_config.sh

**Path:** `/home/user/IACT---project/scripts/validate_security_config.sh`

Valida configuracion de seguridad.

**Como ejecutar:**
```bash
./scripts/validate_security_config.sh
```

### check_no_emojis.py

**Path:** `/home/user/IACT---project/scripts/check_no_emojis.py`

Verifica que no hay emojis en el codigo/documentacion.

**Como ejecutar:**
```bash
python scripts/check_no_emojis.py
```

## Scripts de Utilidades

### cleanup_sessions.sh

**Path:** `/home/user/IACT---project/scripts/cleanup_sessions.sh`

Limpia sesiones antiguas de Django.

**Como ejecutar:**
```bash
./scripts/cleanup_sessions.sh
```

### cleanup_branches.sh

**Path:** `/home/user/IACT---project/scripts/cleanup_branches.sh`

Limpia branches mergeadas en Git.

**Como ejecutar:**
```bash
./scripts/cleanup_branches.sh
```

### install_hooks.sh

**Path:** `/home/user/IACT---project/scripts/install_hooks.sh`

Instala Git hooks del proyecto.

**Como ejecutar:**
```bash
./scripts/install_hooks.sh
```

## Templates

**Path:** `/home/user/IACT---project/scripts/templates/`

Templates para crear nuevos scripts:

- **bash_script_template.sh** - Template para scripts Bash
- **posix_script_template.sh** - Template para scripts POSIX sh
- **library_template.sh** - Template para librerias Bash

**Como usar:**
```bash
cp scripts/templates/bash_script_template.sh scripts/mi_nuevo_script.sh
# Editar y personalizar
```

## Recursos Adicionales

- **[Guia de Inicio Rapido](./QUICKSTART.md)** - Comandos mas comunes
- **[Matriz de Scripts](./SCRIPTS_MATRIX.md)** - Tabla completa de todos los scripts
- **[Guia de Desarrollo de Scripts](./script-development-guide.md)** - Como crear nuevos scripts
- **[Guia Detallada sdlc_agent.py](./sdlc-agent-guide.md)** - Uso avanzado del CLI SDLC
- **[Referencia de Agentes SDLC](./sdlc-agents-reference.md)** - Documentacion de todos los agentes

## Estructura de Directorios

```
scripts/
├── ai/                          # Agentes AI y SDLC
│   ├── agents/                  # 20+ agentes SDLC
│   ├── examples/                # Ejemplos de uso
│   └── run_test_generation.sh
├── ci/                          # Scripts de CI/CD
│   ├── backend_test.sh
│   ├── frontend_test.sh
│   ├── security_scan.sh
│   └── test_pyramid_check.sh
├── disaster_recovery/           # Backup y restore
│   ├── backup_mysql.sh
│   ├── backup_cassandra.sh
│   ├── restore_mysql.sh
│   └── test_dr.sh
├── requisitos/                  # Gestion de requisitos
│   ├── generar_indices.py
│   ├── validar_frontmatter.py
│   ├── contar_requisitos.sh
│   └── listar_requisitos.sh
├── templates/                   # Templates de scripts
│   ├── bash_script_template.sh
│   ├── posix_script_template.sh
│   └── library_template.sh
├── cassandra/                   # Scripts Cassandra
├── dev/                         # Scripts de desarrollo
├── load_testing/                # Scripts de carga
├── logging/                     # Scripts de logging
├── ml/                          # Scripts ML
├── benchmarking/                # Benchmarks
├── sdlc_agent.py               # CLI principal SDLC
├── dora_metrics.py             # Calculador DORA metrics
├── generate_guides.py          # Generador de guias
├── deploy.sh                   # Script deployment
├── run_all_tests.sh            # Ejecutor tests
└── ...                         # Otros scripts
```

## Prerequisitos

### Python Scripts
- Python 3.11+
- Dependencias: `pip install -r requirements.txt`

### Bash Scripts
- Bash 4.0+
- Utilidades: git, jq, curl

### Variables de Entorno Requeridas

```bash
# Para DORA metrics y GitHub integrations
export GITHUB_TOKEN="ghp_..."

# Para deployment
export DEPLOY_KEY="..."

# Para base de datos
export DB_USER="..."
export DB_PASSWORD="..."
```

## Troubleshooting

### Script no ejecuta

```bash
# Dar permisos de ejecucion
chmod +x scripts/nombre_script.sh
```

### Python module not found

```bash
# Instalar dependencias
pip install -r requirements.txt

# O agregar al PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### GITHUB_TOKEN no configurado

```bash
# Crear personal access token en GitHub
# Settings -> Developer settings -> Personal access tokens
export GITHUB_TOKEN="ghp_..."
```

## Mejores Practicas

1. **Siempre ejecuta scripts desde raiz del proyecto:**
   ```bash
   cd /home/user/IACT---project
   ./scripts/nombre_script.sh
   ```

2. **Usa dry-run cuando este disponible:**
   ```bash
   python scripts/sdlc_agent.py --phase planning --input "..." --dry-run
   ```

3. **Revisa logs en caso de error:**
   ```bash
   # Los logs suelen estar en /tmp/ o logs/
   tail -f /tmp/script_name.log
   ```

4. **Valida antes de commitear:**
   ```bash
   ./scripts/validate_critical_restrictions.sh
   ./scripts/check_no_emojis.py
   ```

## Contribuir

Para agregar nuevos scripts, consulta la [Guia de Desarrollo de Scripts](./script-development-guide.md).

## Ownership

Ver [CODEOWNERS](../../.github/CODEOWNERS) para responsables de cada script.

## Contacto

- Tech Lead: @tech-lead
- DevOps Lead: @devops-lead
- QA Lead: @qa-lead

---

**Ultima actualizacion:** 2025-11-07
**Version:** 1.0
