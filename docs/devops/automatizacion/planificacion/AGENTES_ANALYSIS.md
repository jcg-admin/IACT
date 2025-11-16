---
title: Analisis Completo Sistema de Agentes - Auto-CoT
issue_number: IACT-AUTO-001
date: 2025-11-13
fase: design
subfase: agentes_architecture
proyecto: IACT---project
parent_doc: LLD_00_OVERVIEW.md
status: in_progress
version: 1.0
---

# Analisis Completo Sistema de Agentes (Auto-CoT + Self-Consistency)

**Issue**: IACT-AUTO-001
**Fase**: DESIGN - Arquitectura Agentes Python
**Fecha**: 2025-11-13
**Metodologia**: Auto-CoT (descomposicion) + Self-Consistency (validacion)

---

## Auto-CoT: Descomposicion del Sistema

### Pregunta Raiz:
Como convertir el sistema de automatizacion (specs en LLDs) en agentes Python especializados en /scripts/coding/ai/?

### Nivel 1: Componentes Principales

Del analisis de LLDs identifico:
1. Sistema Constitucion (6 reglas: R1-R6)
2. Pipeline CI Local (4 stages, 12 jobs)
3. Validaciones especificas (UI/API, DevContainer, schemas)
4. Integracion (Git hooks, DevContainer lifecycle)

### Nivel 2: Descomposicion en Sub-Problemas

**Pregunta 2.1**: Como modelar sistema constitucion como agente(s)?
- Subpregunta 2.1.1: Un agente monolitico o multiples agentes especializados?
- Subpregunta 2.1.2: Como manejar diferentes scopes (pre-commit, pre-push, etc.)?
- Subpregunta 2.1.3: Como manejar severidades (error vs warning)?

**Pregunta 2.2**: Como modelar CI local como agente(s)?
- Subpregunta 2.2.1: Un orquestador + agentes por stage?
- Subpregunta 2.2.2: Como manejar paralelizacion?
- Subpregunta 2.2.3: Como integrar con scripts existentes?

**Pregunta 2.3**: Validaciones especificas como agentes?
- Subpregunta 2.3.1: Agentes independientes o helpers?
- Subpregunta 2.3.2: Como compartir logica comun?

**Pregunta 2.4**: Como integrar agentes con Git hooks y DevContainer?
- Subpregunta 2.4.1: Wrappers Bash que invocan Python?
- Subpregunta 2.4.2: CLI unificado para todos los agentes?

### Nivel 3: Respuestas con Self-Consistency

#### Respuesta 2.1: Sistema Constitucion

**Enfoque A**: 1 agente monolitico ConstitutionAgent
- Pro: Simple, un solo punto entrada
- Contra: Dificil de testear (6 reglas en 1 clase)

**Enfoque B**: 7 agentes (1 orquestador + 6 especializados por regla)
- Pro: Alta modularidad, facil testear
- Contra: Mas archivos, mas complejidad

**Enfoque C**: 1 agente ConstitutionAgent + 6 validators como modulos
- Pro: Balance modularidad/simplicidad
- Contra: Validators no reutilizables fuera constitucion

**Self-Consistency Decision**: ENFOQUE C
- ConstitutionAgent como orquestador
- constitution/validators/ con 6 modulos (R1-R6)
- Reutilizable, testeable, mantenible

#### Respuesta 2.2: CI Local

**Enfoque A**: 1 agente CILocalAgent monolitico
- Pro: Simple orquestacion
- Contra: Dificil manejar 12 jobs diferentes

**Enfoque B**: 5 agentes (1 orquestador + 4 por stage)
- Pro: Modularidad por stage
- Contra: Duplicacion logica paralelizacion

**Enfoque C**: 1 CILocalAgent + pipeline/stages/ + pipeline/jobs/
- Pro: Arquitectura clara, reutilizable
- Contra: Mas estructura directorio

**Self-Consistency Decision**: ENFOQUE C
- CILocalAgent como orquestador principal
- pipeline/stages/ con modulos lint, test, build, validate
- pipeline/jobs/ con job runners especificos
- Smart detection como modulo separado

#### Respuesta 2.3: Validaciones Especificas

**Self-Consistency Decision**: Agentes especializados independientes
- CoherenceAgent: UI/API coherence (R3)
- DevContainerAgent: Env validation (R6)
- ValidationAgent: Schema validator generico
- Cada uno puede invocarse standalone O desde ConstitutionAgent

#### Respuesta 2.4: Integracion

**Self-Consistency Decision**: CLI unificado + wrappers Bash minimos
- scripts/coding/ai/cli.py - CLI principal para todos los agentes
- Git hooks invocan: python scripts/coding/ai/cli.py constitution --mode=pre-commit
- Wrappers Bash legacy para compatibilidad (opcionales)

---

## Arquitectura Final de Agentes

### Estructura Directorios

```
scripts/coding/ai/
├── __init__.py
├── cli.py                          # CLI unificado TODOS los agentes
├── base_agent.py                   # Clase base abstracta
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Logging estandarizado
│   ├── config_loader.py            # Load YAML configs
│   └── git_helper.py               # Git operations
├── constitution/
│   ├── __init__.py
│   ├── constitution_agent.py       # AGENTE 1: Orquestador constitucion
│   └── validators/
│       ├── __init__.py
│       ├── r1_branch_validator.py  # R1: No push main
│       ├── r2_emoji_validator.py   # R2: No emojis
│       ├── r3_coherence_validator.py # R3: UI/API coherence
│       ├── r4_database_validator.py  # R4: DB router
│       ├── r5_tests_validator.py     # R5: Tests pass
│       └── r6_devcontainer_validator.py # R6: DevContainer
├── pipeline/
│   ├── __init__.py
│   ├── ci_local_agent.py           # AGENTE 2: Orquestador CI
│   ├── smart_detection.py          # Smart detection (UI/API/docs changes)
│   ├── stages/
│   │   ├── __init__.py
│   │   ├── lint_stage.py           # Stage: lint (3 jobs)
│   │   ├── test_stage.py           # Stage: test (2 jobs)
│   │   ├── build_stage.py          # Stage: build (2 jobs)
│   │   └── validate_stage.py       # Stage: validate (5 jobs)
│   └── jobs/
│       ├── __init__.py
│       └── job_runner.py           # Job execution engine
├── coherence/
│   ├── __init__.py
│   └── coherence_agent.py          # AGENTE 3: UI/API coherence
├── devcontainer/
│   ├── __init__.py
│   └── devcontainer_agent.py       # AGENTE 4: DevContainer validator
├── validation/
│   ├── __init__.py
│   └── validation_agent.py         # AGENTE 5: Schema validator generico
└── README.md                        # Documentacion completa
```

### Total Archivos Python: 28

---

## Lista Completa de Agentes (5 Principales)

### AGENTE 1: ConstitutionAgent
**Ubicacion**: `scripts/coding/ai/constitution/constitution_agent.py`
**Responsabilidad**: Orquestar validacion 6 reglas constitucion
**Modos**: pre-commit, pre-push, ci-local, devcontainer-init, manual
**Exit codes**: 0=success, 1=error, 2=warning
**Dependencies**: 6 validators (R1-R6), config_loader, logger
**Tests**: tests/ai/constitution/test_constitution_agent.py

### AGENTE 2: CILocalAgent
**Ubicacion**: `scripts/coding/ai/pipeline/ci_local_agent.py`
**Responsabilidad**: Orquestar pipeline CI local (4 stages, 12 jobs)
**Features**: Smart detection, paralelizacion, fail-fast, reports JSON
**Dependencies**: 4 stage modules, job_runner, smart_detection
**Tests**: tests/ai/pipeline/test_ci_local_agent.py

### AGENTE 3: CoherenceAgent
**Ubicacion**: `scripts/coding/ai/coherence/coherence_agent.py`
**Responsabilidad**: Validar coherencia cambios UI/API
**Logic**: Detecta cambios API sin tests/servicios UI correspondientes
**Invocado por**: ConstitutionAgent (R3), CILocalAgent (validate stage)
**Tests**: tests/ai/coherence/test_coherence_agent.py

### AGENTE 4: DevContainerAgent
**Ubicacion**: `scripts/coding/ai/devcontainer/devcontainer_agent.py`
**Responsabilidad**: Validar entorno DevContainer completo
**Checks**: Databases (PostgreSQL, MariaDB), Python 3.12, Node 18, deps (yq, jq)
**Invocado por**: ConstitutionAgent (R6), DevContainer post_create.sh
**Tests**: tests/ai/devcontainer/test_devcontainer_agent.py

### AGENTE 5: ValidationAgent
**Ubicacion**: `scripts/coding/ai/validation/validation_agent.py`
**Responsabilidad**: Validar schemas genericos (YAML, JSON)
**Use cases**: .constitucion.yaml schema, .ci-local.yaml schema
**Invocado por**: ConstitutionAgent (auto-validacion), CILocalAgent (config load)
**Tests**: tests/ai/validation/test_validation_agent.py

---

## Modulos Helpers (No son agentes, son utilities)

### utils/logger.py
**Responsabilidad**: Logging estandarizado con colores
**Funciones**: log_info, log_success, log_warn, log_error, log_debug
**Equivalente**: scripts/utils/logging.sh (Bash version)

### utils/config_loader.py
**Responsabilidad**: Cargar configs YAML (.constitucion.yaml, .ci-local.yaml)
**Funciones**: load_yaml, validate_schema, get_config_value
**Dependencies**: pyyaml

### utils/git_helper.py
**Responsabilidad**: Operaciones Git comunes
**Funciones**: get_current_branch, get_changed_files, is_clean_working_tree
**Dependencies**: GitPython

### pipeline/smart_detection.py
**Responsabilidad**: Deteccion inteligente cambios (UI, API, docs)
**Funciones**: detect_ui_changes, detect_api_changes, detect_docs_changes
**Invocado por**: CILocalAgent

### pipeline/jobs/job_runner.py
**Responsabilidad**: Motor ejecucion jobs (timeout, parallel, fail-fast)
**Funciones**: run_job, run_parallel_jobs, aggregate_results
**Invocado por**: Stage modules

---

## Validators Constitution (6 modulos)

### constitution/validators/r1_branch_validator.py
**Regla**: R1_no_direct_push_main
**Validacion**: Current branch != main/master
**Severity**: error
**Scope**: pre-push

### constitution/validators/r2_emoji_validator.py
**Regla**: R2_no_emojis_anywhere
**Validacion**: No emojis en staged files
**Severity**: error
**Scope**: pre-commit
**Method**: Regex pattern matching Unicode emoji ranges

### constitution/validators/r3_coherence_validator.py
**Regla**: R3_ui_api_coherence
**Validacion**: Cambios API tienen tests/servicios UI
**Severity**: warning
**Scope**: pre-push
**Delegation**: Invoca CoherenceAgent

### constitution/validators/r4_database_validator.py
**Regla**: R4_database_router_validated
**Validacion**: Database router config correcto
**Severity**: error
**Scope**: pre-push
**Integration**: Invoca scripts/validate_database_router.sh

### constitution/validators/r5_tests_validator.py
**Regla**: R5_tests_must_pass
**Validacion**: Tests UI + API pasan
**Severity**: error
**Scope**: pre-push
**Integration**: Invoca scripts/run_all_tests.sh

### constitution/validators/r6_devcontainer_validator.py
**Regla**: R6_devcontainer_compatibility
**Validacion**: Entorno DevContainer completo
**Severity**: warning
**Scope**: devcontainer-init
**Delegation**: Invoca DevContainerAgent

---

## Stages CI Local (4 modulos)

### pipeline/stages/lint_stage.py
**Jobs**: eslint_ui, ruff_api, markdown_lint
**Parallelization**: true
**Dependencies**: None

### pipeline/stages/test_stage.py
**Jobs**: jest_ui, pytest_api
**Parallelization**: true
**Dependencies**: lint

### pipeline/stages/build_stage.py
**Jobs**: webpack_ui, collectstatic_api
**Parallelization**: true
**Dependencies**: test

### pipeline/stages/validate_stage.py
**Jobs**: validate_security, validate_database_router, validate_constitucion, validate_docs_structure, validate_critical_restrictions
**Parallelization**: false (resource-intensive)
**Dependencies**: build

---

## CLI Unificado

### scripts/coding/ai/cli.py

**Comandos**:
```bash
# Constitution
python scripts/coding/ai/cli.py constitution --mode=pre-commit
python scripts/coding/ai/cli.py constitution --mode=pre-push
python scripts/coding/ai/cli.py constitution --mode=manual

# CI Local
python scripts/coding/ai/cli.py ci-local
python scripts/coding/ai/cli.py ci-local --stage=lint
python scripts/coding/ai/cli.py ci-local --job=test_ui --stage=test

# Coherence
python scripts/coding/ai/cli.py coherence --base-branch=main

# DevContainer
python scripts/coding/ai/cli.py devcontainer

# Validation
python scripts/coding/ai/cli.py validate-schema .constitucion.yaml
```

**Estructura CLI**:
- Subcommands para cada agente
- Flags comunes: --verbose, --debug, --dry-run
- Help integrado: --help

---

## Base Agent (Clase Abstracta)

### scripts/coding/ai/base_agent.py

**Proposito**: Interfaz comun para TODOS los agentes

**Metodos abstractos**:
- `run()` - Ejecutar agente
- `validate()` - Validar precondiciones
- `report()` - Generar reporte

**Metodos concretos**:
- `setup_logging()` - Configurar logger
- `load_config()` - Cargar configuracion
- `exit_with_code()` - Exit con codigo estandar

**Herencia**:
- ConstitutionAgent extends BaseAgent
- CILocalAgent extends BaseAgent
- CoherenceAgent extends BaseAgent
- DevContainerAgent extends BaseAgent
- ValidationAgent extends BaseAgent

---

## TDD: Tests Structure

```
tests/
├── ai/
│   ├── __init__.py
│   ├── test_base_agent.py
│   ├── test_cli.py
│   ├── utils/
│   │   ├── test_logger.py
│   │   ├── test_config_loader.py
│   │   └── test_git_helper.py
│   ├── constitution/
│   │   ├── test_constitution_agent.py
│   │   └── validators/
│   │       ├── test_r1_branch_validator.py
│   │       ├── test_r2_emoji_validator.py
│   │       ├── test_r3_coherence_validator.py
│   │       ├── test_r4_database_validator.py
│   │       ├── test_r5_tests_validator.py
│   │       └── test_r6_devcontainer_validator.py
│   ├── pipeline/
│   │   ├── test_ci_local_agent.py
│   │   ├── test_smart_detection.py
│   │   ├── stages/
│   │   │   ├── test_lint_stage.py
│   │   │   ├── test_test_stage.py
│   │   │   ├── test_build_stage.py
│   │   │   └── test_validate_stage.py
│   │   └── jobs/
│   │       └── test_job_runner.py
│   ├── coherence/
│   │   └── test_coherence_agent.py
│   ├── devcontainer/
│   │   └── test_devcontainer_agent.py
│   └── validation/
│       └── test_validation_agent.py
└── fixtures/
    ├── constitucion_valid.yaml
    ├── constitucion_invalid.yaml
    ├── ci_local_valid.yaml
    └── sample_git_diffs/
```

**Total archivos tests**: 26

---

## Documentacion ADRs (5 principales)

### docs/adr/ADR-XXX-constitution-agent-architecture.md
**Decision**: Arquitectura ConstitutionAgent + 6 validators
**Rationale**: Modularidad vs complejidad
**Alternatives**: Monolitico, 7 agentes separados

### docs/adr/ADR-XXX-ci-local-agent-architecture.md
**Decision**: CILocalAgent + stages + jobs modules
**Rationale**: Escalabilidad, facil agregar stages/jobs

### docs/adr/ADR-XXX-agents-cli-unificado.md
**Decision**: CLI unificado vs CLIs separados
**Rationale**: UX consistente, menos scripts

### docs/adr/ADR-XXX-python-vs-bash-agents.md
**Decision**: Python para agentes (no Bash)
**Rationale**: Testability, type hints, async support

### docs/adr/ADR-XXX-base-agent-pattern.md
**Decision**: BaseAgent abstracto para todos
**Rationale**: Interfaz consistente, DRY

---

## Dependencias Python

### requirements.txt (nuevo)

```
pyyaml>=6.0
GitPython>=3.1.40
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
click>=8.1.0           # CLI framework
```

---

## Fases Implementacion (TDD)

### FASE 1: Setup + Base
1. Crear estructura directorios
2. requirements.txt
3. BaseAgent (abstracto)
4. Utils (logger, config_loader, git_helper)
5. Tests base + utils

### FASE 2: ConstitutionAgent (TDD)
1. Tests R1-R6 validators (RED)
2. Implement R1-R6 validators (GREEN)
3. Tests ConstitutionAgent (RED)
4. Implement ConstitutionAgent (GREEN)

### FASE 3: CILocalAgent (TDD)
1. Tests smart_detection (RED)
2. Implement smart_detection (GREEN)
3. Tests job_runner (RED)
4. Implement job_runner (GREEN)
5. Tests 4 stages (RED)
6. Implement 4 stages (GREEN)
7. Tests CILocalAgent (RED)
8. Implement CILocalAgent (GREEN)

### FASE 4: Agentes Especializados (TDD)
1. Tests CoherenceAgent (RED)
2. Implement CoherenceAgent (GREEN)
3. Tests DevContainerAgent (RED)
4. Implement DevContainerAgent (GREEN)
5. Tests ValidationAgent (RED)
6. Implement ValidationAgent (GREEN)

### FASE 5: CLI + Integracion
1. Tests CLI (RED)
2. Implement CLI (GREEN)
3. Integration tests (E2E)
4. Git hooks integration
5. DevContainer integration

### FASE 6: Documentacion
1. ADRs (5 principales)
2. scripts/coding/ai/README.md
3. Actualizacion LLDs referencias

---

## Metricas Estimadas

**Lineas Codigo**:
- Base + Utils: 500 lineas
- ConstitutionAgent + validators: 1200 lineas
- CILocalAgent + stages + jobs: 1500 lineas
- Agentes especializados: 600 lineas
- CLI: 300 lineas
**Total codigo**: 4100 lineas Python

**Lineas Tests**:
- Tests base + utils: 400 lineas
- Tests constitution: 800 lineas
- Tests pipeline: 1000 lineas
- Tests agentes: 400 lineas
- Tests CLI: 200 lineas
- Integration tests: 300 lineas
**Total tests**: 3100 lineas Python

**Documentacion**:
- ADRs: 5 archivos (2000 lineas)
- READMEs: 3 archivos (800 lineas)
**Total docs**: 2800 lineas Markdown

**TOTAL PROYECTO AGENTES**: 10000 lineas (codigo + tests + docs)

**Tiempo Estimado**: 25-30 horas implementacion completa

---

## Self-Consistency: Validacion Arquitectura

### Validacion 1: Cumple requerimientos LLDs?
- VALIDADO: Todas specs LLDs mapeadas a agentes
- Constitution: 6 reglas → 6 validators
- CI Local: 4 stages → 4 stage modules
- Validaciones: 3 agentes especializados

### Validacion 2: TDD compatible?
- VALIDADO: Arquitectura modular permite tests aislados
- Cada validator testeable independiente
- Cada stage testeable independiente
- Mocking facil (interfaces claras)

### Validacion 3: Escalable?
- VALIDADO: Facil agregar nuevos validators (R7, R8...)
- Facil agregar nuevos stages CI
- Facil agregar nuevos agentes especializados

### Validacion 4: Mantenible?
- VALIDADO: Separacion responsabilidades clara
- DRY con BaseAgent y utils
- Type hints para documentacion inline

### Validacion 5: Integrable?
- VALIDADO: CLI unificado simplifica invocacion
- Git hooks simple: python cli.py constitution --mode=pre-push
- DevContainer simple: python cli.py devcontainer

**DECISION FINAL**: Arquitectura APROBADA para implementacion

---

## Proximos Pasos Inmediatos

1. Commit este analisis
2. Crear estructura directorios completa
3. FASE 1: Implementar base + utils (TDD)
4. FASE 2: ConstitutionAgent (TDD)
5. FASE 3: CILocalAgent (TDD)
6. FASE 4: Agentes especializados (TDD)
7. FASE 5: CLI + integracion
8. FASE 6: Documentacion completa

**NO PARAR HASTA COMPLETAR TODO**

---

**Metodologia**:
- Auto-CoT: Descomposicion sistematica en niveles
- Self-Consistency: Validacion multiple perspectivas
- TDD: RED → GREEN → REFACTOR
- NO emojis, NO iconos (texto puro)

**Status**: ANALISIS COMPLETO - LISTO PARA IMPLEMENTACION
**Fecha**: 2025-11-13
**Autor**: SDLC Agent / DevOps Team
