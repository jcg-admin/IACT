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
## Project Architecture

### Key Directories
- `/api/callcentersite`: Código fuente Django/DRF
  - `settings/` (incluye `local.py`, `ci.py`), `urls.py`, `wsgi.py`, `asgi.py`
  - `apps/`: microservicios internos y APIs públicas
  - `tests/`: suites pytest parametrizadas y fixtures compartidas
- `/ui`: Código React+TypeScript
  - `package.json`, `tsconfig.json`, `webpack.config.js` (o `vite.config.ts` según feature)
  - `src/` (componentes, hooks, servicios), `public/` (assets estáticos)
  - `tests/` para Jest/Vitest
- `/scripts/coding/ai`: agentes Python que automatizan análisis/validaciones
- `/scripts/ci`, `/scripts/security`, `/scripts/tests`: wrappers para pipelines locales
- `/docs`: lineamientos, ADRs, catálogos AI, monitoreo
- `/infrastructure`: Terraform, Ansible, docker-compose y Vagrant
- `.github`: Workflows, agentes Copilot, plantillas, hooks

### Configuration Files
- `api/callcentersite/settings.py`: ajustes principales, incluye configuración multi-DB
- `api/requirements*.txt`: dependencias (prod/dev/test)
- `ui/package.json`, `ui/webpack.config.js`, `ui/.eslintrc.cjs`, `ui/tsconfig.json`
- `.pre-commit-config.yaml`, `.coveragerc`, `pyproject.toml`, `.constitucion.yaml`
- `.github/workflows/*.yml`: CI/CD y validaciones auxiliares

### Webpack Configuration Example
```javascript
// ui/webpack.config.js
module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      { test: /\.(js|jsx)$/, exclude: /node_modules/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  },
  resolve: { extensions: ['.js', '.jsx'] }
}
```

### Django Project Structure
```
backend/
└── api/
    └── callcentersite/
        ├── __init__.py
        ├── settings/
        ├── urls.py
        ├── wsgi.py
        └── asgi.py
```

### React Project Structure
```
ui/
├── package.json
├── webpack.config.js
├── public/
│   ├── index.html
│   └── favicon.ico
└── src/
    ├── index.js
    ├── App.js
    ├── components/
    └── services/
```

### Continuous Integration
- Workflows: `python.yml`, `frontend.yml`, `security.yml`, `docs.yml`, `architecture-check.yml`, `emoji-validation.yml`, `release.yml`
- Checks por pipeline: lint (backend/frontend), pruebas unitarias, cobertura ≥80%, compilación Webpack/Vite, validaciones de tipos, escaneos Bandit/Safety/Gitleaks
- Siempre replica `scripts/ci-local.sh` antes de subir cambios para detectar fallos

### Dependency Management
- Backend: `api/requirements.txt` + `api/requirements-dev.txt`
- Frontend: `ui/package.json` (usa `npm install` o `npm ci`)
- Infra/scripts: `scripts/**/requirements.txt`, `infrastructure/**/versions.tf`
- Hooks: `pre-commit` controla formateo y escaneos rápidos

### Merge Gates y Validaciones Explícitas
1. `pre-commit run --all-files`
2. `pytest --cov=. --cov-report=xml` desde `api/callcentersite`
3. `npm run lint && npm test` desde `ui/`
4. `scripts/security/run_bandit.sh`, `run_safety.sh`, `run_gitleaks.sh`
5. Validaciones específicas del área impactada (`terraform validate`, `markdownlint`, `scripts/tests/enforce_coverage.sh 80`)

### Inventario Rápido y Referencias
- Raíz: `api/`, `ui/`, `scripts/`, `docs/`, `.agent/`, `.github/`, `tests/`, `schemas/`, `infrastructure/`, `monitoring/`, `logs_data/`, `respaldo/`
- Documentación clave: `README.md`, `CONSOLIDATION_STATUS.md`, `PLAN_CONSOLIDACION_PRS.md`, `.github/agents/META_PROMPTS_LIBRARY.md`
- Dependencias ocultas: PostgreSQL, Redis, credenciales LLM, Node 18 + npm 9, Python 3.11 + virtualenv, `pre-commit`
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
