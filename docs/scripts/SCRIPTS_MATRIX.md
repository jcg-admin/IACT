# Matriz de Scripts del Proyecto IACT

Tabla completa de todos los scripts del proyecto.

## SDLC Core

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| sdlc_agent.py | SDLC | CLI principal SDLC | Daily | @tech-lead | Production | [sdlc-agent-guide.md](./sdlc-agent-guide.md) |
| sdlc_orchestrator.py | SDLC | Pipeline orchestrator | Weekly | @tech-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| sdlc_planner.py | SDLC | Planning phase | Daily | @tech-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| sdlc_feasibility.py | SDLC | Feasibility analysis | Weekly | @arquitecto-senior | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| sdlc_design.py | SDLC | Design generation | Weekly | @arquitecto-senior | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| sdlc_testing.py | SDLC | Testing strategy | Weekly | @qa-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| sdlc_deployment.py | SDLC | Deployment planning | Weekly | @devops-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |

## CI/CD

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| backend_test.sh | CI/CD | Backend tests | Daily | @devops-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| frontend_test.sh | CI/CD | Frontend tests | Daily | @devops-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| security_scan.sh | CI/CD | Security scanning | Daily | @devops-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| test_pyramid_check.sh | CI/CD | Test pyramid validation | Daily | @qa-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| deploy.sh | Deployment | Blue-green deployment | Weekly | @devops-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| health_check.sh | Deployment | Health verification | Daily | @devops-lead | Production | [ci-cd-scripts.md](./ci-cd-scripts.md) |
| run_all_tests.sh | Testing | Execute all tests | Daily | @qa-lead | Production | [README.md](./README.md) |
| run_integration_tests.sh | Testing | Integration tests | Daily | @qa-lead | Production | [README.md](./README.md) |

## Metricas

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| dora_metrics.py | Metrics | DORA metrics calculation | Weekly | @devops-lead | Production | [metrics-and-reporting.md](./metrics-and-reporting.md) |
| generate_dora_report.sh | Metrics | HTML report generation | Weekly | @devops-lead | Production | [metrics-and-reporting.md](./metrics-and-reporting.md) |
| dora_sdlc_integration.py | Metrics | DORA + SDLC integration | Daily | @tech-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |

## Documentacion

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| generate_guides.py | Documentation | Generate operational guides | Monthly | @doc-lead | Production | [README.md](./README.md) |
| sync_documentation.py | Documentation | Sync docs | Weekly | @doc-lead | Production | [README.md](./README.md) |
| validar_estructura_docs.sh | Documentation | Validate docs structure | Daily | @doc-lead | Production | [README.md](./README.md) |
| reorganizar_docs_por_dominio.sh | Documentation | Reorganize docs | Monthly | @doc-lead | Production | [README.md](./README.md) |
| documentation_sync_agent.py | Documentation | Auto sync agent | Daily | @doc-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |

## Requisitos

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| generar_indices.py | Requirements | Generate requirements indices | Daily | @product-owner | Production | [requirements-management.md](./requirements-management.md) |
| validar_frontmatter.py | Requirements | Validate YAML frontmatter | Daily | @product-owner | Production | [requirements-management.md](./requirements-management.md) |
| contar_requisitos.sh | Requirements | Count requirements | Weekly | @product-owner | Production | [requirements-management.md](./requirements-management.md) |
| listar_requisitos.sh | Requirements | List requirements | Weekly | @product-owner | Production | [requirements-management.md](./requirements-management.md) |
| traceability_matrix_generator.py | Requirements | Generate traceability matrix | Weekly | @arquitecto-senior | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |

## Disaster Recovery

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| backup_mysql.sh | DR | MySQL backup | Daily | @dba-lead | Production | [disaster-recovery.md](./disaster-recovery.md) |
| backup_cassandra.sh | DR | Cassandra backup | Daily | @dba-lead | Production | [disaster-recovery.md](./disaster-recovery.md) |
| restore_mysql.sh | DR | MySQL restore | On-demand | @dba-lead | Production | [disaster-recovery.md](./disaster-recovery.md) |
| test_dr.sh | DR | DR procedures testing | Monthly | @devops-lead | Production | [disaster-recovery.md](./disaster-recovery.md) |
| backup_data_centralization.sh | DR | Centralize backups | Daily | @devops-lead | Production | [README.md](./README.md) |

## Validacion

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| validate_critical_restrictions.sh | Validation | Validate RNF-002 compliance | Daily | @arquitecto-senior | Production | [README.md](./README.md) |
| validate_security_config.sh | Validation | Security config validation | Daily | @devops-lead | Production | [README.md](./README.md) |
| validate_database_router.sh | Validation | DB router validation | Daily | @dba-lead | Production | [README.md](./README.md) |
| check_no_emojis.py | Validation | Check for emojis | Daily | @tech-lead | Production | [README.md](./README.md) |

## Database

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| install-cassandra.sh | Database | Install Cassandra | On-demand | @dba-lead | Production | [README.md](./README.md) |
| configure-django.sh | Database | Configure Django for Cassandra | On-demand | @backend-lead | Production | [README.md](./README.md) |
| setup-cron-jobs.sh | Database | Setup backup cron jobs | On-demand | @devops-lead | Production | [README.md](./README.md) |

## Business Analysis

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| business_analysis_generator.py | Business | Generate business analysis | Weekly | @product-owner | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| business_analysis_pipeline.py | Business | BA pipeline | Weekly | @product-owner | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| generate_business_analysis.py | Business | CLI for BA generation | Weekly | @product-owner | Production | [README.md](./README.md) |

## Testing

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| test_runner.py | Testing | Test execution orchestrator | Daily | @qa-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| run_test_generation.sh | Testing | Generate tests | Weekly | @qa-lead | Production | [README.md](./README.md) |
| test_generation_orchestrator.py | Testing | Test generation pipeline | Weekly | @qa-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |

## Utilities

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| cleanup_sessions.sh | Utilities | Clean Django sessions | Daily | @backend-lead | Production | [README.md](./README.md) |
| cleanup_branches.sh | Utilities | Clean merged branches | Weekly | @tech-lead | Production | [README.md](./README.md) |
| clean_emojis.sh | Utilities | Remove emojis | On-demand | @tech-lead | Production | [README.md](./README.md) |
| install_hooks.sh | Utilities | Install git hooks | On-demand | @tech-lead | Production | [README.md](./README.md) |
| complete_sync.sh | Utilities | Complete sync | Weekly | @tech-lead | Production | [README.md](./README.md) |

## Automation

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| pdca_automation_agent.py | Automation | PDCA cycle automation | Monthly | @tech-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| pr_creator.py | Automation | Auto PR creation | On-demand | @tech-lead | Production | [sdlc-agents-reference.md](./sdlc-agents-reference.md) |
| generate_workflow_from_template.py | Automation | Generate GH workflows | On-demand | @devops-lead | Production | [README.md](./README.md) |

## Load Testing

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| locustfile.py | Load Testing | Locust load tests | Weekly | @qa-lead | Production | [README.md](./README.md) |
| simple_load_test.sh | Load Testing | Simple load test | Weekly | @qa-lead | Production | [README.md](./README.md) |

## Logging

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| alert_on_errors.py | Logging | Error alerting | Real-time | @devops-lead | Production | [README.md](./README.md) |
| cassandra_handler.py | Logging | Cassandra log handler | Real-time | @backend-lead | Production | [README.md](./README.md) |
| infrastructure_log_collector.py | Logging | Infrastructure log collector | Real-time | @devops-lead | Production | [README.md](./README.md) |
| infrastructure_logs_daemon.py | Logging | Logs daemon | Real-time | @devops-lead | Production | [README.md](./README.md) |

## ML

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| retrain_deployment_risk_model.py | ML | Retrain risk model | Monthly | @ai-lead | Beta | [README.md](./README.md) |

## Development

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| check_all.sh | Development | Check all validations | Daily | @tech-lead | Production | [README.md](./README.md) |
| generate_plan.sh | Development | Generate dev plan | Weekly | @tech-lead | Production | [README.md](./README.md) |
| validate_spec.sh | Development | Validate spec | Daily | @arquitecto-senior | Production | [README.md](./README.md) |

## Templates

| Script | Categoria | Proposito | Frecuencia | Owner | Status | Docs |
|--------|-----------|-----------|------------|-------|--------|------|
| bash_script_template.sh | Templates | Bash script template | On-demand | @tech-lead | Production | [script-development-guide.md](./script-development-guide.md) |
| posix_script_template.sh | Templates | POSIX sh template | On-demand | @tech-lead | Production | [script-development-guide.md](./script-development-guide.md) |
| library_template.sh | Templates | Library template | On-demand | @tech-lead | Production | [script-development-guide.md](./script-development-guide.md) |

---

## Resumen por Categoria

| Categoria | Cantidad | Owner Principal |
|-----------|----------|-----------------|
| SDLC | 7 | @tech-lead |
| CI/CD | 8 | @devops-lead |
| Metrics | 3 | @devops-lead |
| Documentation | 5 | @doc-lead |
| Requirements | 5 | @product-owner |
| Disaster Recovery | 5 | @dba-lead |
| Validation | 4 | @arquitecto-senior |
| Database | 3 | @dba-lead |
| Business Analysis | 3 | @product-owner |
| Testing | 3 | @qa-lead |
| Utilities | 5 | @tech-lead |
| Automation | 3 | @tech-lead |
| Load Testing | 2 | @qa-lead |
| Logging | 4 | @devops-lead |
| ML | 1 | @ai-lead |
| Development | 3 | @tech-lead |
| Templates | 3 | @tech-lead |

**Total:** 67 scripts

---

## Leyenda

### Frecuencia
- **Real-time:** Corriendo continuamente
- **Daily:** Ejecutado diariamente (manual o cron)
- **Weekly:** Ejecutado semanalmente
- **Monthly:** Ejecutado mensualmente
- **On-demand:** Ejecutado cuando se necesita

### Status
- **Production:** Usado en produccion, estable
- **Beta:** En testing, no 100% estable
- **Deprecated:** Marcado para eliminacion

---

**Ultima actualizacion:** 2025-11-07
**Version:** 1.0
