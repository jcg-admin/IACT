# Plan de corrección de workflows de GitHub Actions

Este plan resume las acciones necesarias para corregir y optimizar los workflows bajo `.github/workflows/`, priorizando triggers completos (`push`, `pull_request`, `workflow_dispatch`), permisos mínimos, caching de dependencias, matrices de pruebas y controles de seguridad.

## Principios generales
- **Triggers consistentes**: cada workflow debe soportar `push`, `pull_request` y `workflow_dispatch` salvo que exista una restricción explícita.
- **Permisos mínimos**: definir `permissions` explícitos a nivel de workflow con el mínimo necesario (p. ej., `contents: read`, `pull-requests: write` solo cuando aplique).
- **Caching**: habilitar `actions/cache` o cachés nativas (pip/npm) según el stack para reducir tiempos.
- **Matrices de pruebas**: cubrir versiones soportadas (Python 3.10-3.12, Node 18-20) y SO donde aplique.
- **Seguridad**: fijar versiones de acciones (SHA/digest cuando aplique), evitar secretos inline y añadir `concurrency` para evitar solapes.
- **Observabilidad**: añadir upload de artefactos y resultados (coverage, logs) cuando aporte valor al debug.

## Estrategia por ambiente (producción, QA y desarrollo)
- **Workflows por entorno**: definir tres pipelines alineados a ramas y entornos (`main` → producción, `release/*` o `qa/*` → QA, `develop` → desarrollo). Cada pipeline debe heredar los principios generales anteriores.
- **Configuración diferenciada**:
  - **Producción**: jobs protegidos con `environment: production`, `concurrency` por tag o ref, `required_reviewers`/`protection rules`, y despliegue mediante MCP/Codex; ejecución en `push` a `main` + `workflow_dispatch` con inputs para rollback.
  - **QA**: `environment: qa` con despliegue a entornos de staging, tests extendidos (smoke + integración), matrices completas de versiones, y `concurrency` por rama de release; triggers en `push` a `qa/*` y `workflow_dispatch` para validaciones manuales.
  - **Desarrollo**: `environment: development` orientado a feedback rápido (lint + unit + cobertura), caching agresivo y matrices mínimas; triggers en `push`/`pull_request` hacia `develop` y `workflow_dispatch` opcional.
- **Notificaciones**: usar comentarios en PR/commit status en lugar de Slack; habilitar `actions/github-script` para anotar fallos por entorno.
- **Variables y secretos**: centralizar variables comunes en `env` y secretos por entorno en `environment secrets`; validar su presencia con `if: env.SECRET != ''` antes de usarlos.
- **Plantillas reutilizables**: crear un workflow reusable (p. ej., `.github/workflows/reusable-ci.yml`) con matrices, caching y permisos mínimos, que reciba como inputs el entorno (`environment`), la rama y el modo (`deploy`/`validate`).

## Acciones transversales
1. Añadir plantilla base reutilizable para permisos mínimos y estrategia de caching (composite o reusable workflow).
2. Incorporar `concurrency` para despliegue, incident-response y pipelines largos.
3. Revisar secretos: documentar requeridos y validar existencia antes de usarlos (ej. `if: env.SECRET != ''`).
4. Añadir validaciones de seguridad ligeras (Semgrep/Trivy) en ramas principales si no duplican CodeQL.
5. Documentar en README de workflows los triggers esperados y variables.

## Acciones por workflow
- **actionlint.yml**: fijar digest del contenedor y añadir cache para dependencias de verificación si aplica.
- **agents-ci.yml**: añadir `permissions` mínimos; declarar `CODECOV_TOKEN` como `env` opcional con guardas; revisar que `bandit` falle en hallazgos críticos y habilitar cache pip.
- **backend-ci.yml**: agregar `workflow_dispatch`; definir permisos mínimos; usar secretos no triviales para MySQL y cerrar puerto con `ports: ["3306:3306"]` solo si es estrictamente necesario; cache pip y matriz de Python 3.10-3.12; añadir `concurrency` por ref.
- **code-quality.yml**: incluir `push` y `workflow_dispatch`; permisos mínimos; cache según herramienta (npm/pip); revisar matrices si hay múltiples linters.
- **codeql.yml**: agregar `workflow_dispatch`; permisos mínimos (`security-events: write`, `contents: read`); cache de dependencias del lenguaje y fijar versiones de `actions/checkout`/`setup-*` por SHA.
- **dependency-review.yml**: añadir `push` y `workflow_dispatch`; permisos mínimos (`contents: read`); documentar política de bloqueo.
- **deploy.yml**: habilitar `pull_request` (dry-run), permisos mínimos; reusar artefactos de build con checksum; cache de dependencias; añadir `concurrency` por entorno y validaciones previas.
- **docs-validation.yml**: sumar `workflow_dispatch`; permisos mínimos; cache pip y Sphinx; paralelizar validaciones si posible.
- **docs.yml**: incorporar cache de dependencias y `concurrency` por ref; revisar publicación segura (sin write innecesario).
- **emoji-validation.yml**: añadir `workflow_dispatch` y permisos mínimos; cache de dependencias y fijar versiones de acciones.
- **frontend-ci.yml**: agregar `workflow_dispatch` y permisos mínimos; cache npm/pnpm; matriz Node 18-20; considerar `concurrency` por ref.
- **incident-response.yml**: sumar `push`/`pull_request` si aplica; permisos mínimos; cache de herramientas; añadir `concurrency` para evitar ejecuciones paralelas.
- **infrastructure-ci.yml**: añadir `workflow_dispatch`; permisos mínimos; cache de proveedores/Terraform; proteger `terraform apply` con `environment`; validar backend remoto.
- **lint.yml**: agregar `workflow_dispatch`; permisos mínimos; cache de dependencias; fijar versiones de acciones.
- **meta-architecture-check.yml**: definir permisos mínimos; cache de dependencias; fijar versiones.
- **migrations.yml**: añadir `workflow_dispatch`; permisos mínimos; eliminar credenciales inline (`testpass`); cerrar puertos o usar servicios internos; cache pip; considerar matrices de DB si soportadas.
- **pr-review.yml**: evaluar añadir `push`/`pull_request` o mantener sólo comentario pero con filtro `if: github.event.issue.pull_request` para limitar; cache dependencias; revisar permisos mínimos.
- **python_ci.yml**: definir permisos mínimos; cache pip; añadir `concurrency`; ampliar matriz Python 3.10-3.12.
- **release.yml**: incluir `pull_request` (dry-run); permisos explícitos; verificar integridad de artefactos; cache dependencias; añadir `concurrency` por versión/tag.
- **requirements_index.yml**: añadir cache pip y matriz Python adicional; mantener permisos explícitos.
- **requirements_validate_traceability.yml**: definir permisos mínimos; cache pip; fijar acciones.
- **security-scan.yml**: sumar `workflow_dispatch`; permisos mínimos; cache cuando sea seguro; fijar versiones y limitar scope de escaneos.
- **sync-docs.yml**: agregar `push`/`pull_request`; permisos mínimos; validar PAT/SSH presentes; cache dependencias; añadir `concurrency`.
- **test-pyramid.yml**: añadir `workflow_dispatch`; permisos mínimos; cache pip; ampliar matriz Python; fijar acciones.
- **validate-guides.yml**: definir permisos mínimos; cache dependencias; fijar versiones de acciones.

## Entregables
- PRs incrementales por workflow o por categoría (permisos, triggers, caching) para reducir riesgo.
- Documentación de cambios y secretos requeridos en cada PR.
