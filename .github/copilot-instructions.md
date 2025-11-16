# Copilot Coding Agent Onboarding Guide

<Goals>
- Reduce PR rejection risk by mirroring the local CI toolchain (pytest + coverage, npm test, security scans) before shipping fixes.
- Minimize bash/build failures by following the validated bootstrap/build/test/run/lint flows captured below.
- Accelerate delivery by pointing directly to the repos' key apps, scripts, and workflows so extra `rg`/`find` passes stay optional.
</Goals>

<Limitations>
- Keep instructions under two pages when echoed elsewhere; link to deeper docs (e.g., `docs/`, `.github/agents/`) instead of pasting them entirely.
- Remain task-agnostic: describe reusable processes, not feature-specific steps.
</Limitations>

<WhatToAdd>

<HighLevelDetails>
- **Repositorio**: Plataforma omnicanal para contact centers con backend Django 5+/DRF (`api/`), frontend React+TypeScript (`ui/`), paquetes de automatización (`scripts/`), infraestructura IaC (`infrastructure/`), y una extensa biblioteca documental (`docs/`).
- **Tamaño/tecnologías**: Miles de archivos, principales lenguajes Python 3.11, TypeScript/Node 18, Shell, Terraform/Ansible, YAML/JSON; CI se ejecuta en GitHub Actions reutilizando scripts locales.
- **Estrategia SDLC**: TDD obligatorio (Red→Green→Refactor), ≥80% coverage, Conventional Commits, ADRs para decisiones clave; meta-prompts estandarizados en `.github/agents/META_PROMPTS_LIBRARY.md` para agentes y automatizaciones IA.
</HighLevelDetails>

<BuildInstructions>
- **Bootstrap general**:
  1. `python3.11 -m venv .venv && source .venv/bin/activate` en la raíz; confirma `python --version`.
  2. `pip install -r api/requirements-dev.txt` seguido de `pip install -e api/callcentersite` para habilitar entrypoints Django.
  3. `cd ui && nvm use 18 && npm install` (si `nvm` no está disponible, instala Node 18 LTS manualmente).
  4. Ejecuta `pre-commit install` para alinear hooks locales con CI.
- **Build backend**:
  - Siempre corre `python manage.py check` y `python manage.py makemigrations --check` desde `api/callcentersite` después de instalar dependencias.
  - Compila assets con `python manage.py collectstatic --noinput` cuando modifiques archivos estáticos.
  - Si usas múltiples bases de datos, exporta `DJANGO_SETTINGS_MODULE=callcentersite.settings.local` y valida routers antes de migrar.
- **Build frontend**:
  - Desde `ui/`, ejecuta `npm run lint` (ESLint+Prettier) y `npm run build` (Vite/Webpack). Si falla por caché, `rm -rf node_modules && npm cache verify && npm install`.
  - Ajusta `NODE_OPTIONS=--max-old-space-size=4096` para builds grandes.
- **Tests**:
  - Backend: `cd api/callcentersite && pytest --cov=. --cov-report=xml` (scripts en `scripts/tests/` exigen ≥80%).
  - Frontend: `cd ui && npm test -- --runInBand` para suites Jest/Vitest, `npm run test:ci` en pipelines.
  - Infra/scripts: usa `scripts/security/run_bandit.sh`, `scripts/security/run_safety.sh`, `scripts/security/run_gitleaks.sh`, `scripts/ci-local.sh` (emula GitHub Actions) y `scripts/tests/enforce_coverage.sh 80`.
- **Run**:
  - Backend dev server: `python manage.py runserver 0.0.0.0:8000` apuntando a PostgreSQL; levanta servicios auxiliares con `docker compose up db redis` o `infrastructure/vagrant/vagrant up`.
  - Frontend: `npm run dev -- --host` para Vite, o `npm start` si se usa CRA legacy.
- **Lint/format**:
  - Python: `black .`, `isort .`, `flake8` (usa configuraciones de `pyproject.toml` y `.flake8` si existe).
  - JS/TS: `npm run lint` (ESLint), `npm run format` (Prettier) según scripts `package.json`.
  - Infra/Docs: `terraform fmt`, `ansible-lint`, `markdownlint` (`scripts/docs/lint_docs.sh`).
- **Validaciones adicionales**:
  - Ejecuta `./scripts/security/run_gitleaks.sh` antes de abrir PRs.
  - Usa `./scripts/monitoring/report_dora_metrics.sh` (si aplica) para actualizar métricas DORA.
  - Documenta hallazgos en ADRs (`docs/architecture/adr/`) cuando alteres arquitectura, y enlaza a `PLAN_CONSOLIDACION_PRS.md` si afecta hitos activos.
</BuildInstructions>

<ProjectLayout>
- **Arquitectura**:
  - `api/callcentersite/`: apps Django (`apps/`), configuración (`callcentersite/settings/`), routers multi-DB, management commands, fixtures tests.
  - `ui/`: src React/TypeScript (`src/`), configuraciones lint/build (`package.json`, `tsconfig.json`, `.eslintrc.cjs`).
  - `scripts/coding/ai/`: agentes Python consumidos por automatizaciones; cada módulo tiene README y tests correspondientes.
  - `scripts/ci/`, `scripts/security/`, `scripts/tests/`: orquestadores para pipelines, seguridad y coverage.
  - `docs/`: gobernanza, AI, operaciones; índices dentro de cada subcarpeta (`docs/**/README.md`).
  - `.github/`: workflows, agentes Copilot (`agents/`, `copilot/agents.json`), plantillas PR/Issue.
  - `infrastructure/`: Terraform, Ansible, Vagrant, docker-compose.
- **Configuraciones**: `.pre-commit-config.yaml`, `.constitucion.yaml` (principios), `pyproject.toml`, `.coveragerc`, `ui/.eslintrc.cjs`, `ui/package.json`, `scripts/coding/ai/requirements.txt`, `.github/workflows/*.yml`.
- **Checks obligatorios antes de merge**:
  1. `pre-commit run --all-files`.
  2. Backend `pytest --cov` + cobertura ≥80% (`coverage.xml`).
  3. Frontend `npm run lint && npm test`.
  4. Seguridad: `run_bandit.sh`, `run_safety.sh`, `run_gitleaks.sh`.
  5. Infra/Docs según impacto (`terraform validate`, `markdownlint`).
- **Workflows CI**: `python.yml`, `frontend.yml`, `security.yml`, `docs.yml`, `architecture-check.yml`, `emoji-validation.yml` (nomenclatura de commits/emojis), `release.yml`.
- **Dependencias implícitas**: PostgreSQL + Redis para backend, Node 18 + npm 9 para frontend, acceso opcional a servicios externos (LLM providers) configurados vía variables de entorno, `pre-commit` para hooks.
- **Inventario raíz**: `api/`, `ui/`, `scripts/`, `docs/`, `.agent/`, `.github/`, `tests/`, `schemas/`, `infrastructure/`, `monitoring/`, `logs_data/`, `respaldo/`.
- **Referencias rápidas**: `README.md` describe visión general; `CONSOLIDATION_STATUS.md` y `PLAN_CONSOLIDACION_PRS.md` rastrean esfuerzos coordinados; `META_PROMPTS_LIBRARY.md` recopila 10 meta-prompts obligatorios para agentes.
</ProjectLayout>

</WhatToAdd>

<StepsToFollow>
1. Realiza un inventario de documentación (`README.md`, `docs/**`), scripts (`scripts/`), pipelines (`.github/workflows/`) antes de modificar código.
2. Sigue los comandos documentados exactamente; si un comando falla, registra error, tiempo y workaround en el PR o ADR correspondiente.
3. Siempre instala dependencias (`pip install -e api/callcentersite`, `npm install`, `pre-commit install`) antes de correr builds/tests.
4. Mantén el ciclo TDD (escribe tests primero) y ejecuta `scripts/tests/enforce_coverage.sh 80` para validar cobertura.
5. Usa los meta-prompts de `META_PROMPTS_LIBRARY.md` cuando diseñes nuevas instrucciones/agentes IA.
6. Confía en estas instrucciones y evita búsquedas adicionales salvo que la información esté incompleta o desactualizada.
7. Documenta cualquier desviación (nuevos scripts, flags, errores) para mantener esta guía vigente.
</StepsToFollow>

Confirma siempre que tus cambios respeten TDD, cobertura ≥80%, y Conventional Commits.
