---
id: README-SDLC-AGENTS
tipo: documentation
version: 1.1
fecha: 2025-01-15
---

# Agentes SDLC del Proyecto IACT

Sistema de agentes IA que automatizan y asisten en cada fase del Software Development Life Cycle (SDLC) del proyecto IACT.

## Visi?n General

Los agentes SDLC transforman el desarrollo de software al automatizar tareas repetitivas de planificaci?n, an?lisis, dise?o, testing y deployment, permitiendo al equipo enfocarse en resolver problemas complejos.

**Beneficios**:
- Planificaci?n consistente y completa de features
- An?lisis de viabilidad automatizado
- Generaci?n de documentaci?n de dise?o
- Testing comprehensivo automatizado
- Deployment seguro con rollback plans
- Trazabilidad completa del ciclo de vida

## Arquitectura

Ver documentaci?n completa: `scripts/ai/agents/ARCHITECTURE_SDLC_AGENTS.md`

```
+-----------------------------------------------------------------+
|                     SDLC Agent System                            |
|                                                                  |
|  +----------------+  +----------------+  +----------------+   |
|  |  Planning      |->| Feasibility    |->|  Design        |   |
|  |  Agent         |  | Agent          |  |  Agent         |   |
|  +----------------+  +----------------+  +----------------+   |
|         |                   |                    |              |
|         ?                   ?                    ?              |
|  +----------------+  +----------------+  +----------------+   |
|  |Implementation  |<-|  Testing       |<-|  Deployment    |   |
|  |  Assistant     |  |  Agent         |  |  Agent         |   |
|  +----------------+  +----------------+  +----------------+   |
|                                                                  |
|  +----------------------------------------------------------+  |
|  |              Maintenance & Monitoring Agent              |  |
|  +----------------------------------------------------------+  |
|                                                                  |
|  +----------------------------------------------------------+  |
|  |                   Orchestrator Agent                      |  |
|  |          (Coordina todo el pipeline SDLC)                |  |
|  +----------------------------------------------------------+  |
+-----------------------------------------------------------------+
```

## Agentes Implementados

### SDLCPlannerAgent (Fase 1: Planning)

**Estado**: [IMPLEMENTADO]

**Responsabilidad**: Convierte feature requests en issues/tickets completos con user stories, acceptance criteria, estimaci?n y priorizaci?n.

**Inputs**:
- `feature_request` (str): Descripci?n del feature
- `project_context` (str, opcional): Contexto del proyecto
- `backlog` (List[Dict], opcional): Backlog actual

**Outputs**:
- Issue/ticket formateado (GitHub Issue)
- User story completa
- Acceptance criteria
- Story points estimation (Fibonacci: 1, 2, 3, 5, 8, 13, 21)
- Priority recommendation (P0, P1, P2, P3)
- Technical requirements identificados
- Dependencies con otros issues

**Ejemplo de uso**:
```bash
python scripts/sdlc_agent.py --phase planning \
  --input "Implementar sistema de autenticaci?n de 2 factores"
```

**Output**:
```
================================================================================
RESULTADO DE EJECUCI?N
================================================================================

Estado: SUCCESS

Issue generado:
  T?tulo: Implementar sistema de autenticaci?n de 2 factores
  Story Points: 8
  Prioridad: P1
  Artefacto: docs/sdlc_outputs/planning/ISSUE_20251106_150610.md

Acceptance Criteria (7):
  1. Sistema de autenticaci?n funciona correctamente
  2. Validaci?n de credenciales implementada
  3. API endpoints documentados en OpenAPI/Swagger
  4. Validaci?n de inputs implementada
  5. El feature est? implementado seg?n especificaci?n
  ...

Requisitos T?cnicos:
  - Django REST API endpoint
  - Serializers y validaci?n
  - Tests de API (pytest)
  - Authentication/Authorization
  - Permission checks
  - Audit logging

Decisi?n de fase: GO
Confianza: 85.0%

Recomendaciones:
  - Issue generado con ?xito
  - Story points estimados: 8
  - Prioridad recomendada: P1
  - Siguiente fase: Feasibility Analysis
```

### TDDFeatureAgent (Fase 4: Implementation)

**Estado**: [IMPLEMENTADO]

**Responsabilidad**: Implementa features siguiendo metodologia TDD (Test-Driven Development) con garantias de calidad y compliance automatizado.

**Inputs**:
- `issue_title` (str): Titulo del feature
- `acceptance_criteria` (List[str]): Criterios de aceptacion
- `technical_requirements` (List[str]): Requisitos tecnicos
- `target_module` (str): Modulo donde implementar

**Outputs**:
- Archivos de tests (unit, integration)
- Archivos de codigo fuente
- Execution log (JSON completo con audit trail)
- Markdown report (reporte human-readable)
- Dashboard visual con badges (compliance, coverage, security)
- Constitution compliance result (score 0-100)

**Proceso TDD**:
1. **RED Phase**: Genera tests unitarios que deben fallar
2. **GREEN Phase**: Implementa codigo para pasar tests
3. **REFACTOR Phase**: Optimiza codigo manteniendo tests verdes
4. **VALIDATION**: Valida 8 reglas de TDD constitution
5. **REPORTING**: Genera reportes y dashboards automaticos

**Constitution Checks** (8 reglas):
- RED_BEFORE_GREEN (CRITICAL): Tests antes del codigo
- TESTS_MUST_FAIL_FIRST (CRITICAL): Tests fallan en RED
- ALL_TESTS_MUST_PASS (CRITICAL): Tests pasan en GREEN
- TESTS_STAY_GREEN_AFTER_REFACTOR (CRITICAL): Tests siguen pasando
- MINIMUM_COVERAGE (HIGH): Cobertura >= 90%
- NO_SECURITY_ISSUES (HIGH): Sin vulnerabilidades
- CODE_QUALITY_PASSING (MEDIUM): Linting y type checking
- DOCUMENTATION_REQUIRED (MEDIUM): Docstrings presentes

**Ejemplo de uso**:
```bash
# Preparar issue data
cat > issue_data.json << EOF
{
  "issue_title": "Implement user authentication with 2FA",
  "acceptance_criteria": [
    "Users can register with email and password",
    "Users can login with credentials"
  ],
  "technical_requirements": [
    "Use Django authentication backend",
    "Minimum 90% test coverage"
  ],
  "target_module": "apps.users"
}
EOF

# Ejecutar TDD agent
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json \
  --verbose
```

**Output**:
```
INFO - Starting TDD implementation: Implement user authentication with 2FA
INFO - === RED PHASE: Writing failing tests ===
INFO - Generated 15 test cases
INFO - Running tests... (should fail)
INFO - ? RED phase complete: 15/15 tests failed as expected

INFO - === GREEN PHASE: Implementing code ===
INFO - Running tests... (should pass)
INFO - ? GREEN phase complete: 15/15 tests passed

INFO - === REFACTOR PHASE: Optimizing code ===
INFO - Auto-fixing linting issues
INFO - ? REFACTOR phase complete: 15/15 tests still passing

INFO - === Validating TDD Constitution ===
INFO - Checking 8 constitution rules...
INFO - ? All CRITICAL rules passed
INFO - Compliance Score: 95.5/100

INFO - Status: ? COMPLIANT
INFO - Execution log: docs/sdlc_outputs/tdd_logs/tdd_execution_*.json
INFO - Dashboard: docs/sdlc_outputs/tdd_logs/dashboard_*.md
```

**Herramientas QA Integradas**:
- pytest + coverage (test execution y cobertura)
- ruff (code linting)
- mypy (type checking)
- bandit (security scanning)
- AST parser (docstring validation)

**Documentacion completa**:
- Guia tecnica: `docs/gobernanza/agentes/tdd-feature-agent.md`
- Workflow de uso: `docs/guias/workflows/workflow-implement-feature-with-tdd-agent.md`
- Referencia rapida: `docs/scripts/sdlc-agents-reference.md`

### Agentes Implementados Adicionales

**Estado**: [IMPLEMENTADO - Sin LLM]

Estos agentes están completamente funcionales usando heurísticas y análisis estático:

- SDLCFeasibilityAgent (Fase 2: Feasibility Analysis) - Análisis de viabilidad
- SDLCDesignAgent (Fase 3: System Design) - Generación de HLD/LLD/ADRs/Diagramas
- SDLCTestingAgent (Fase 5: Testing) - Planes de testing
- SDLCDeploymentAgent (Fase 6: Deployment) - Planes de deployment/rollback
- SDLCOrchestratorAgent (Coordinador del pipeline completo) - Orquestación

### Agentes Pendientes

**Estado**: [EN DESARROLLO]

- SDLCMaintenanceAgent (Fase 7: Maintenance) - Análisis post-deployment

### Limitaciones Conocidas

**SDLCPlannerAgent**:
- Integración LLM: COMPLETA (usa Anthropic Claude o OpenAI GPT)
- Requiere: ANTHROPIC_API_KEY o OPENAI_API_KEY
- Fallback: Heurísticas si LLM falla

**TDDFeatureAgent**:
- Integración LLM: COMPLETA (usa LLMGenerator para todo el ciclo TDD)
- Requiere: ANTHROPIC_API_KEY o OPENAI_API_KEY
- Generación de tests: LLM
- Generación de código: LLM
- Refactoring: LLM + auto-fix

**Agentes sin LLM**:
- SDLCFeasibilityAgent, SDLCDesignAgent, SDLCTestingAgent, SDLCDeploymentAgent
- Usan templates y heurísticas (no requieren API keys)
- Funcionan offline
- Resultados determinísticos

**Agentes Meta**:
- ChainOfVerificationAgent, AutoCoTAgent, SelfConsistencyAgent, TreeOfThoughtsAgent
- ArchitectureAnalysisAgent, DesignPatternsAgent, RefactoringOpportunitiesAgent
- TestGenerationAgent, UMLValidationAgent
- Estado: FRAMEWORK COMPLETO - Requieren conexión con LLMGenerator
- Ver: docs/desarrollo/TAREAS_PENDIENTES_AGENTES_IA.md para detalles de implementación

## Uso

### CLI B?sico

```bash
# Ejecutar planning phase
python scripts/sdlc_agent.py --phase planning \
  --input "Feature request aqu?"

# Leer desde archivo
python scripts/sdlc_agent.py --phase planning \
  --input-file feature_request.txt

# Output en JSON (para integraci?n)
python scripts/sdlc_agent.py --phase planning \
  --input "..." \
  --format json

# Dry-run (no guarda artefactos)
python scripts/sdlc_agent.py --phase planning \
  --input "..." \
  --dry-run

# Con contexto del proyecto
python scripts/sdlc_agent.py --phase planning \
  --input "..." \
  --project-context "Stack: Django + React + PostgreSQL"

# Verbose logging
python scripts/sdlc_agent.py --phase planning \
  --input "..." \
  --verbose
```

### Pipeline Completo (Cuando est? implementado)

```bash
# Ejecutar todo el pipeline SDLC
python scripts/sdlc_agent.py --pipeline \
  --input "Feature: Dashboard de m?tricas"

# Auto-proceder sin confirmaci?n humana
python scripts/sdlc_agent.py --pipeline \
  --input "..." \
  --auto-proceed
```

### Configuraci?n Personalizada

Crear `config/sdlc_agents.json`:

```json
{
  "project_root": "/home/user/IACT---project",
  "output_dir": "docs/sdlc_outputs",
  "llm_provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "agents": {
    "planner": {
      "enabled": true,
      "default_priority": "P2"
    },
    "feasibility": {
      "enabled": true,
      "risk_threshold": 0.7
    },
    "design": {
      "enabled": true,
      "generate_diagrams": true,
      "diagram_format": "mermaid"
    }
  }
}
```

Uso:
```bash
python scripts/sdlc_agent.py --phase planning \
  --config config/sdlc_agents.json \
  --input "..."
```

## Artefactos Generados

Los agentes guardan sus outputs en `docs/sdlc_outputs/` organizados por fase:

```
docs/sdlc_outputs/
+-- planning/
|   +-- ISSUE_20251106_150610.md
|   +-- ISSUE_20251106_150615.md
|   +-- ...
+-- feasibility/
|   +-- FEASIBILITY_REPORT_20251106_160000.md
|   +-- ...
+-- design/
|   +-- HLD_feature_name.md
|   +-- LLD_feature_name.md
|   +-- ADR_001_decision_name.md
|   +-- diagrams/
|       +-- architecture.mermaid
|       +-- sequence.mermaid
+-- testing/
|   +-- TEST_PLAN_feature_name.md
|   +-- TEST_REPORT_20251106_170000.md
+-- deployment/
    +-- DEPLOYMENT_PLAN_feature_name.md
    +-- ROLLBACK_PLAN_feature_name.md
```

## Integraci?n con Workflow Existente

### 1. Integraci?n con GitHub Issues

```bash
# Generar issue con CLI
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: Notificaciones push" \
  --format json > issue.json

# Crear en GitHub
gh issue create \
  --title "$(jq -r '.data.issue_title' issue.json)" \
  --body "$(jq -r '.data.issue_body' issue.json)"
```

### 2. Integraci?n con CI/CD

Agregar a `.github/workflows/sdlc-planning.yml`:

```yaml
name: SDLC Planning

on:
  issues:
    types: [labeled]

jobs:
  auto-plan:
    if: github.event.label.name == 'needs-planning'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run SDLC Planner
        run: |
          python scripts/sdlc_agent.py --phase planning \
            --input "${{ github.event.issue.body }}" \
            --format json > planning_result.json

      - name: Comment on Issue
        uses: actions/github-script@v6
        with:
          script: |
            const result = require('./planning_result.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## SDLC Planning Result\n\n${result.data.issue_body}`
            });
```

### 3. Uso Retrospectivo

Aplicar proceso SDLC a trabajo ya completado:

```bash
# Generar issue retrospectivo
python scripts/sdlc_agent.py --phase planning \
  --input "RETROSPECTIVO: Implement? CODEOWNERS para docs/ con asignaci?n autom?tica de revisores para backend, frontend, infrastructure y requisitos."

# El issue generado documenta lo que deber?a haberse hecho en Planning
# ?til para auditor?a y aprendizaje
```

## Buenas Pr?cticas

### 1. Usar Planning Antes de Implementar

**INCORRECTO**:
```bash
# Implementar directamente sin planificaci?n
git checkout -b feature/2fa
# ... codear ...
git commit -m "Add 2FA"
```

**CORRECTO**:
```bash
# 1. Planificar primero
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: 2FA" > planning.txt

# 2. Revisar planning
cat docs/sdlc_outputs/planning/ISSUE_*.md

# 3. Crear issue en GitHub
gh issue create --title "..." --body "..."

# 4. LUEGO implementar
git checkout -b feature/2fa-issue-123
# ... codear seg?n plan ...
```

### 2. Estimaci?n Realista

Los story points son Fibonacci (1, 2, 3, 5, 8, 13, 21):
- **1-2**: Cambios triviales (< 2 horas)
- **3-5**: Features peque?os (1-2 d?as)
- **8**: Features medianos (3-5 d?as)
- **13**: Features grandes (1-2 semanas)
- **21**: Epic (> 2 semanas) - considerar dividir

Si el agente estima **21 story points**, dividir en sub-features.

### 3. Trazabilidad Completa

Cada issue generado debe linkear a:
- Requisitos funcionales (RF-XXX)
- Requisitos no funcionales (RN-XXX)
- Especificaciones (SPEC-XXX)
- ADRs relacionados

### 4. Iteraci?n y Mejora

Si el planning generado no es satisfactorio:

```bash
# Regenerar con m?s contexto
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: 2FA" \
  --project-context "Stack: Django + React. Ya tenemos autenticaci?n b?sica con JWT. El feature debe integrarse con sistema existente de users y audit." \
  --verbose
```

## Troubleshooting

### Error: "Falta ANTHROPIC_API_KEY"

**Causa**: El agente requiere API key de Anthropic para LLM.

**Soluci?n**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/sdlc_agent.py --phase planning --input "..."
```

### Warning: "Constitution no encontrada"

**Causa**: Constitution loader busca `docs/gobernanza/agentes/constitution.md` que no existe en la ruta esperada.

**Soluci?n**: Ignorar el warning. Los agentes SDLC tienen guardrails personalizados que no dependen de constitution.

### Issue generado tiene Technical Requirements incorrectos

**Causa**: El agente usa heur?sticas simples para detectar requisitos t?cnicos.

**Soluci?n**: Especificar contexto t?cnico expl?citamente:

```bash
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: Dashboard de m?tricas. TECH: Backend Django REST API, Frontend React + Redux, Database PostgreSQL con agregaciones, Caching Redis" \
  --verbose
```

## Roadmap

### v1.0 (Actual)
- [x] SDLCPlannerAgent
- [x] Base classes (SDLCAgent, SDLCPipeline)
- [x] CLI b?sico
- [x] Documentaci?n completa

### v1.1 (Pr?xima)
- [ ] SDLCFeasibilityAgent
- [ ] SDLCDesignAgent con generaci?n de diagramas Mermaid
- [ ] Integraci?n con GitHub API para crear issues autom?ticamente
- [ ] Mejora de estimaci?n con ML

### v1.2
- [ ] SDLCTestingAgent
- [ ] SDLCDeploymentAgent
- [ ] SDLCOrchestratorAgent (pipeline completo)
- [ ] Integraci?n LLM real (Anthropic/OpenAI)

### v2.0 (Futuro)
- [ ] SDLCMaintenanceAgent
- [ ] Real-time monitoring
- [ ] Predictive analytics (predecir bugs, delays)
- [ ] Integraci?n con Jira
- [ ] Dashboard web para visualizaci?n

## Contribuir

### Agregar un Nuevo Agente

1. Heredar de `SDLCAgent`:

```python
from scripts.ai.agents.sdlc_base import SDLCAgent, SDLCPhaseResult

class SDLCFeasibilityAgent(SDLCAgent):
    def __init__(self, config=None):
        super().__init__(
            name="SDLCFeasibilityAgent",
            phase="feasibility",
            config=config
        )

    def run(self, input_data):
        # Tu l?gica aqu?
        ...

        return {
            "phase_result": self.create_phase_result(
                decision="go",
                confidence=0.8,
                artifacts=[...],
                recommendations=[...]
            ),
            ...
        }

    def _custom_guardrails(self, output_data):
        # Validaciones espec?ficas
        return []
```

2. Agregar a CLI en `scripts/sdlc_agent.py`

3. Documentar en este README

4. Crear tests

## Referencias

- **Arquitectura completa**: `scripts/ai/agents/ARCHITECTURE_SDLC_AGENTS.md`
- **Proceso SDLC**: `docs/gobernanza/procesos/SDLC_PROCESS.md`
- **Base Agent**: `scripts/ai/agents/base.py`
- **Issues generados**: `docs/sdlc_outputs/planning/`

---

**?ltima actualizaci?n**: 2025-11-06
**Versi?n**: 1.0
**Mantenedor**: @arquitecto-senior
