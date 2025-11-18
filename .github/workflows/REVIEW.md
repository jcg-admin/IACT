# Revisión de workflows

Resumen automático de los triggers y jobs definidos en `.github/workflows`.

| Workflow | Triggers | Jobs principales |
| --- | --- | --- |
| actionlint.yml | push, pull_request, workflow_dispatch | actionlint |
| agents-ci.yml | push, pull_request, workflow_dispatch | code-quality, tests, module-tests, performance, security-tests, integration-tests, build-status |
| backend-ci.yml | push, pull_request | lint, test-mysql, test-postgresql, validate-restrictions, integration-tests, summary |
| code-quality.yml | pull_request, workflow_dispatch | smoke-checks |
| codeql.yml | push, pull_request, schedule | analyze |
| dependency-review.yml | pull_request | review |
| deploy.yml | push, workflow_dispatch | pre-deployment-checks, run-tests, build-backend, build-frontend, deploy-staging, deploy-production, post-deployment-monitoring |
| docs-validation.yml | pull_request, push | validate-structure, check-old-references, check-markdown-links, validate-auto-generated-docs, count-docs-stats, summary |
| docs.yml | push, pull_request, workflow_dispatch | build, deploy, check-links |
| emoji-validation.yml | pull_request, push | check-emojis |
| frontend-ci.yml | push, pull_request | lint, test-unit, test-integration, test-e2e, build, accessibility, security, summary |
| incident-response.yml | workflow_dispatch | create-incident-issue, gather-diagnostics, execute-incident-playbook, notify-team, summary |
| infrastructure-ci.yml | push, pull_request | validate-shell-scripts, test-validation-scripts, validate-terraform, validate-docker, validate-configurations, test-health-check, summary |
| lint.yml | pull_request, push | lint-frontmatter |
| meta-architecture-check.yml | pull_request, push, workflow_dispatch | architecture-analysis, code-quality-gate |
| migrations.yml | pull_request, push | detect-migrations, validate-migrations, check-migration-safety, generate-migration-report, summary |
| pr-review.yml | issue_comment | pr-validation |
| python_ci.yml | push, pull_request, workflow_dispatch | code-quality, tests, performance, dependency-check, build-status |
| release.yml | push, workflow_dispatch | validate-version, generate-changelog, create-release-packages, update-version-files, create-github-release, notify-stakeholders, release-summary |
| requirements_index.yml | push, pull_request, workflow_dispatch | generate-indices |
| requirements_validate_traceability.yml | pull_request, push, workflow_dispatch | validate-traceability |
| security-scan.yml | push, pull_request, schedule | bandit-scan, npm-audit, safety-check, django-security-check, trivy-scan, secrets-scan, sql-injection-check, xss-check, csrf-check, generate-security-report, summary |
| sync-docs.yml | schedule, workflow_dispatch | sync-documentation, notify-failure |
| test-pyramid.yml | push, pull_request, schedule | analyze-test-pyramid, test-execution-time, summary |
| validate-guides.yml | pull_request, push, workflow_dispatch | validate-structure, check-broken-links, generate-coverage-report, quality-checks, summary |

## Hallazgos destacados

- **requirements_validate_traceability.yml**: el script de validación estaba mal indentado y sin parsing robusto del front matter, lo que podía provocar errores de ejecución. Se reescribió con PyYAML, normalización de listas y reporte explícito de errores para evitar falsos positivos.
- **Cobertura de calidad de YAML**: no existía un guardrail automático para los workflows. Se añadió `actionlint.yml` para validar sintaxis y convenciones de GitHub Actions en `push`, `pull_request` y `workflow_dispatch`.
- **Optimización pendiente**: `deploy.yml` puede beneficiarse de cachear dependencias Python (setup-python con `cache: 'pip'`) para acelerar las ejecuciones. `pr-review.yml` funciona solo con `issue_comment`; si se requiere validación previa al comentario, añadir `workflow_dispatch` como trigger manual daría más control.
