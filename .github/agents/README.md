# Catálogo Estratégico de Agentes Copilot

Este índice define cómo deben operar los agentes personalizados y documenta la estructura solicitada para que cada ficha y guía maestra
del repositorio mantenga consistencia.

<Goals>
- Reduce la probabilidad de que un PR falle por problemas de CI/CD, validaciones o comportamientos inesperados.
- Minimiza fallas en comandos bash, builds o pipelines reutilizando secuencias validadas.
- Acelera el trabajo del agente evitando búsquedas innecesarias en favor de instrucciones curadas.
</Goals>

<Limitations>
- Las instrucciones no deben exceder dos páginas cuando se compartan con otros agentes.
- El contenido debe permanecer genérico respecto a tareas específicas para que sea reutilizable.
</Limitations>

<WhatToAdd>

### <HighLevelDetails>
- **Resumen del repositorio**: Plataforma integral de call center con backend Django 5.x, frontend React y más de 200 scripts de automatización para CI/CD, IA y SDLC.
- **Características clave**: ~100 archivos de código principales, miles de artefactos de documentación, soporte multi-base de datos (PostgreSQL/MariaDB), estándares de TDD y commits convencionales.
- **Lenguajes y frameworks**: Python 3.11+, Django, DRF, React, TypeScript, Shell, Terraform/Ansible en infraestructura, YAML/JSON para pipelines.
</HighLevelDetails>

### <BuildInstructions>
- **Bootstrap backend**: `python3.11 -m venv .venv && source .venv/bin/activate && cd api/callcentersite && pip install -e .` (verifica `python --version` == 3.11+).
- **Bootstrap frontend**: `cd ui && npm install` con Node 18 LTS (usa `nvm use 18`).
- **Bases de datos**: desde la raíz o `infrastructure/vagrant/`, ejecutar `vagrant up`; siempre valida `vagrant status` antes de correr tests.
- **Build backend**: `cd api/callcentersite && python manage.py check` seguido de `python manage.py collectstatic --noinput` si necesitas assets.
- **Build frontend**: `cd ui && npm run build`; si falla por dependencias, reinstala `node_modules` y limpia cache (`npm cache verify`).
- **Tests**: backend `pytest --cov=.`, frontend `npm test -- --runInBand`; ejecuta `pre-commit run --all-files` para linting (Black line-length=100, flake8, ESLint, prettier, YAML/JSON validators).
- **Run**: backend `python manage.py runserver 0.0.0.0:8000` (solo contra PostgreSQL), frontend `npm run dev -- --host`.
- **Lint**: `black .`, `flake8`, `isort`, `eslint . --ext .ts,.tsx`; evita comandos fuera de los directorios raíz correspondientes.
- **Validaciones especiales**: `./scripts/ci-local.sh` replica workflows, `./scripts/security/run_gitleaks.sh` valida secretos, `./scripts/tests/enforce_coverage.sh 80` confirma cobertura mínima.
- **Errores comunes**: si `python manage.py migrate` intenta usar MariaDB, revisa routers y ejecuta solo sobre PostgreSQL; si `npm install` falla por memoria, exporta `NODE_OPTIONS=--max-old-space-size=4096`.
</BuildInstructions>

### <ProjectLayout>
- **Arquitectura principal**: `api/callcentersite/` (apps Django, routers multi-DB, settings segmentados), `ui/` (React + Vite/Webpack), `scripts/coding/ai/` (agentes Python), `infrastructure/` (Terraform y Vagrant), `docs/` (MkDocs, playbooks), `.github/` (workflows, agentes Copilot).
- **Configuraciones relevantes**: `.constitucion.yaml` (principios R1-R5), `.pre-commit-config.yaml`, `pyproject.toml` (Black/isort), `ui/.eslintrc.cjs`, `ui/tsconfig.json`, `scripts/coding/ai/requirements.txt`, `.github/workflows/*.yml`.
- **Checks previos al commit**: `pre-commit run --all-files`, `pytest --cov`, `npm test`, `npm run lint`, `python manage.py makemigrations --check`, `python manage.py check --deploy`, `./scripts/security/run_bandit.sh`, `./scripts/security/run_safety.sh`.
- **Workflows CI**: `python.yml` (tests Django), `frontend.yml` (React build/tests), `security.yml` (Bandit, Safety, gitleaks), `emoji-validation.yml`, `architecture-check.yml`, `docs.yml`.
- **Validaciones adicionales**: `docs/` contiene runbooks; `scripts/qa/` aloja verificadores; `tests/` centraliza suites; `PLAN_CONSOLIDACION_PRS.md` y `CONSOLIDATION_STATUS.md` definen hitos.
- **Inventario rápido**:
  - Raíz: `api/`, `ui/`, `scripts/`, `docs/`, `.agent/`, `.github/`, `tests/`, `schemas/`, `infrastructure/`, `monitoring/`, `logs_data/`.
  - `scripts/`: subcarpetas `coding/ai`, `ci`, `security`, `sdlc`; busca scripts por prefijo funcional.
  - `docs/`: agrupa gobernanza, AI, analítica, runbooks; usa índices `README.md` por dominio.
</ProjectLayout>

</WhatToAdd>

## <StepsToFollow>
1. Inventariar documentación (`README.md`, `CONTRIBUTING.md`, `docs/**`), scripts y pipelines antes de modificar agentes.
2. Revisar instrucciones de build/test en `scripts/` y `.github/workflows/`; documenta comandos que fallan y las mitigaciones aplicadas.
3. Registrar errores comunes (timeouts, dependencias faltantes, configuraciones obligatorias) con tiempos aproximados y soluciones.
4. Ejecutar siempre `npm install` antes de build frontend y `pip install -e .` antes de build backend; anotar cualquier workaround aplicado.
5. Documentar pasos de validación adicionales (gitleaks, Bandit, Safety, coverage ≥80%).
6. Solo realizar búsquedas adicionales (`rg`, `find`) si la guía no cubre la necesidad o si detectas información obsoleta; confía primero en estas instrucciones.
7. Cuando generes prompts o instrucciones nuevas, referénciate en la biblioteca de meta-prompts adjunta y mantén registros de los casos de prueba.
</StepsToFollow>

## Catálogo de Agentes
- **SDLC**: planner, feasibility, design, testing, deployment, orchestrator, DORA-tracked.
- **Automatización**: coherencia, PDCA, constitución, devcontainer, métricas, esquemas, pipelines, compliance.
- **Calidad**: cobertura, sintaxis, shell analysis/remediation, completeness, permisos, route lint.
- **Documentación**: business analysis generator, template/traceability generators, documentation sync agents.
- **Planificación**: Implementation Planner Agent (traduce objetivos difusos en especificaciones accionables con TDD y controles anti-alucinación).
- **DevOps/Operaciones**: GitOps, release, dependency, security, CodeTasker.
- **TDD/Técnicas**: feature/tdd agents, Auto-CoT, Chain-of-Verification, Self-Consistency, Tree-of-Thoughts.

Cada agente cuenta con una ficha `.agent.md` que describe propósito, responsabilidades, procedimientos recomendados, validaciones y criterios de éxito.

## Convenciones Clave
- **Metodología**: aplicar TDD (Red → Green → Refactor) con cobertura ≥80% antes del merge.
- **Commits**: seguir Conventional Commits (`type(scope): description`).
- **Documentación**: crear ADRs para decisiones arquitectónicas; comentar lógicas no obvias.
- **Estándares**: Python (Black 100 chars, isort, flake8), JS (ESLint + Prettier), infra (Terraform fmt, ansible-lint), docs (markdownlint, Vale opcional).

### Lineamientos para la propiedad `tools`
- Declara explícitamente las herramientas que cada agente puede usar: `read`, `search` y `edit` cubren las capacidades básicas del runtime de Copilot.
- Si omites `tools`, Copilot habilita **todas las herramientas disponibles**, incluidos los endpoints expuestos por servidores MCP declarados en el repositorio o en el propio perfil.
- Para agentes de inspección/validación, limita el set a `"read"` y `"search"`; reserva `"edit"` para roles que realmente deban modificar archivos.
- Cuando necesites capacidades MCP específicas, referencia cada herramienta con el formato `"alias/tool"` (por ejemplo, `"playwright/browser"`). Documenta en la ficha `.agent.md` por qué el agente requiere ese permiso.
- Revisa este README al agregar o quitar herramientas para asegurarte de que las automatizaciones y auditores conozcan la justificación.

### Ciclo de pruebas y liberación de agentes
1. **Laboratorio privado**: crea o reutiliza el repositorio organizacional `.github-private` y agrega la carpeta `.github/agents/`. Los perfiles alojados ahí solo son visibles para quienes tengan acceso a ese repositorio.
2. **Creación/actualización**: redacta el `.agent.md` en el laboratorio (puedes duplicar un perfil existente) y haz merge a la rama por defecto para generar una versión candidata.
3. **Validación**: abre `https://github.com/copilot/agents`, selecciona el repositorio privado en el desplegable, elige el agente y ejecuta prompts reales. Usa la sección **Recent sessions** para revisar logs, herramientas utilizadas y resultados.
4. **Iteración**: ajusta instrucciones, `tools`, prompts base o servidores MCP hasta que el agente cumpla los estándares de desempeño y cumplimiento.
5. **Promoción**: mueve el archivo `.agent.md` desde `.github-private/.github/agents/` al repositorio público (`agents/`) y fusiona el cambio. A partir de ese momento, el agente queda disponible para toda la organización.
6. **Monitoreo**: consulta el audit log filtrando por `actor:Copilot` o los paneles de actividad del enterprise para verificar adopción, detectar fallos y respaldar auditorías.

## Referencia de Meta-Prompting
Consulta [`META_PROMPTS_LIBRARY.md`](META_PROMPTS_LIBRARY.md) para los 10 bloques solicitados (generación, optimización, anti-alucinación, evaluaciones, A/B testing, debugging, variaciones multi-LLM y validación). Estos patrones deben acompañar cualquier ficha que guíe a un agente Copilot o a los scripts en `scripts/coding/ai/`.
