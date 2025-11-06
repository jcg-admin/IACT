---
id: README-SDLC-AGENTS
tipo: documentation
version: 1.0
fecha: 2025-11-06
---

# Agentes SDLC del Proyecto IACT

Sistema de agentes IA que automatizan y asisten en cada fase del Software Development Life Cycle (SDLC) del proyecto IACT.

## Visión General

Los agentes SDLC transforman el desarrollo de software al automatizar tareas repetitivas de planificación, análisis, diseño, testing y deployment, permitiendo al equipo enfocarse en resolver problemas complejos.

**Beneficios**:
- Planificación consistente y completa de features
- Análisis de viabilidad automatizado
- Generación de documentación de diseño
- Testing comprehensivo automatizado
- Deployment seguro con rollback plans
- Trazabilidad completa del ciclo de vida

## Arquitectura

Ver documentación completa: `scripts/ai/agents/ARCHITECTURE_SDLC_AGENTS.md`

```
┌─────────────────────────────────────────────────────────────────┐
│                     SDLC Agent System                            │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Planning      │─>│ Feasibility    │─>│  Design        │   │
│  │  Agent         │  │ Agent          │  │  Agent         │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│         │                   │                    │              │
│         ▼                   ▼                    ▼              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │Implementation  │<─│  Testing       │<─│  Deployment    │   │
│  │  Assistant     │  │  Agent         │  │  Agent         │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Maintenance & Monitoring Agent              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Orchestrator Agent                      │  │
│  │          (Coordina todo el pipeline SDLC)                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Agentes Implementados

### SDLCPlannerAgent (Fase 1: Planning)

**Estado**: ✅ Implementado

**Responsabilidad**: Convierte feature requests en issues/tickets completos con user stories, acceptance criteria, estimación y priorización.

**Inputs**:
- `feature_request` (str): Descripción del feature
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
  --input "Implementar sistema de autenticación de 2 factores"
```

**Output**:
```
================================================================================
RESULTADO DE EJECUCIÓN
================================================================================

Estado: SUCCESS

Issue generado:
  Título: Implementar sistema de autenticación de 2 factores
  Story Points: 8
  Prioridad: P1
  Artefacto: docs/sdlc_outputs/planning/ISSUE_20251106_150610.md

Acceptance Criteria (7):
  1. Sistema de autenticación funciona correctamente
  2. Validación de credenciales implementada
  3. API endpoints documentados en OpenAPI/Swagger
  4. Validación de inputs implementada
  5. El feature está implementado según especificación
  ...

Requisitos Técnicos:
  - Django REST API endpoint
  - Serializers y validación
  - Tests de API (pytest)
  - Authentication/Authorization
  - Permission checks
  - Audit logging

Decisión de fase: GO
Confianza: 85.0%

Recomendaciones:
  - Issue generado con éxito
  - Story points estimados: 8
  - Prioridad recomendada: P1
  - Siguiente fase: Feasibility Analysis
```

### Agentes Pendientes

**Estado**: 🔄 En desarrollo

- SDLCFeasibilityAgent (Fase 2: Feasibility Analysis)
- SDLCDesignAgent (Fase 3: System Design)
- SDLCTestingAgent (Fase 5: Testing)
- SDLCDeploymentAgent (Fase 6: Deployment)
- SDLCMaintenanceAgent (Fase 7: Maintenance)
- SDLCOrchestratorAgent (Coordinador del pipeline completo)

## Uso

### CLI Básico

```bash
# Ejecutar planning phase
python scripts/sdlc_agent.py --phase planning \
  --input "Feature request aquí"

# Leer desde archivo
python scripts/sdlc_agent.py --phase planning \
  --input-file feature_request.txt

# Output en JSON (para integración)
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

### Pipeline Completo (Cuando esté implementado)

```bash
# Ejecutar todo el pipeline SDLC
python scripts/sdlc_agent.py --pipeline \
  --input "Feature: Dashboard de métricas"

# Auto-proceder sin confirmación humana
python scripts/sdlc_agent.py --pipeline \
  --input "..." \
  --auto-proceed
```

### Configuración Personalizada

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
├── planning/
│   ├── ISSUE_20251106_150610.md
│   ├── ISSUE_20251106_150615.md
│   └── ...
├── feasibility/
│   ├── FEASIBILITY_REPORT_20251106_160000.md
│   └── ...
├── design/
│   ├── HLD_feature_name.md
│   ├── LLD_feature_name.md
│   ├── ADR_001_decision_name.md
│   └── diagrams/
│       ├── architecture.mermaid
│       └── sequence.mermaid
├── testing/
│   ├── TEST_PLAN_feature_name.md
│   └── TEST_REPORT_20251106_170000.md
└── deployment/
    ├── DEPLOYMENT_PLAN_feature_name.md
    └── ROLLBACK_PLAN_feature_name.md
```

## Integración con Workflow Existente

### 1. Integración con GitHub Issues

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

### 2. Integración con CI/CD

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
  --input "RETROSPECTIVO: Implementé CODEOWNERS para docs/ con asignación automática de revisores para backend, frontend, infrastructure y requisitos."

# El issue generado documenta lo que debería haberse hecho en Planning
# Útil para auditoría y aprendizaje
```

## Buenas Prácticas

### 1. Usar Planning Antes de Implementar

**INCORRECTO** ❌:
```bash
# Implementar directamente sin planificación
git checkout -b feature/2fa
# ... codear ...
git commit -m "Add 2FA"
```

**CORRECTO** ✅:
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
# ... codear según plan ...
```

### 2. Estimación Realista

Los story points son Fibonacci (1, 2, 3, 5, 8, 13, 21):
- **1-2**: Cambios triviales (< 2 horas)
- **3-5**: Features pequeños (1-2 días)
- **8**: Features medianos (3-5 días)
- **13**: Features grandes (1-2 semanas)
- **21**: Epic (> 2 semanas) - considerar dividir

Si el agente estima **21 story points**, dividir en sub-features.

### 3. Trazabilidad Completa

Cada issue generado debe linkear a:
- Requisitos funcionales (RF-XXX)
- Requisitos no funcionales (RN-XXX)
- Especificaciones (SPEC-XXX)
- ADRs relacionados

### 4. Iteración y Mejora

Si el planning generado no es satisfactorio:

```bash
# Regenerar con más contexto
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: 2FA" \
  --project-context "Stack: Django + React. Ya tenemos autenticación básica con JWT. El feature debe integrarse con sistema existente de users y audit." \
  --verbose
```

## Troubleshooting

### Error: "Falta ANTHROPIC_API_KEY"

**Causa**: El agente requiere API key de Anthropic para LLM.

**Solución**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/sdlc_agent.py --phase planning --input "..."
```

### Warning: "Constitution no encontrada"

**Causa**: Constitution loader busca `docs/gobernanza/agentes/constitution.md` que no existe en la ruta esperada.

**Solución**: Ignorar el warning. Los agentes SDLC tienen guardrails personalizados que no dependen de constitution.

### Issue generado tiene Technical Requirements incorrectos

**Causa**: El agente usa heurísticas simples para detectar requisitos técnicos.

**Solución**: Especificar contexto técnico explícitamente:

```bash
python scripts/sdlc_agent.py --phase planning \
  --input "Feature: Dashboard de métricas. TECH: Backend Django REST API, Frontend React + Redux, Database PostgreSQL con agregaciones, Caching Redis" \
  --verbose
```

## Roadmap

### v1.0 (Actual)
- [x] SDLCPlannerAgent
- [x] Base classes (SDLCAgent, SDLCPipeline)
- [x] CLI básico
- [x] Documentación completa

### v1.1 (Próxima)
- [ ] SDLCFeasibilityAgent
- [ ] SDLCDesignAgent con generación de diagramas Mermaid
- [ ] Integración con GitHub API para crear issues automáticamente
- [ ] Mejora de estimación con ML

### v1.2
- [ ] SDLCTestingAgent
- [ ] SDLCDeploymentAgent
- [ ] SDLCOrchestratorAgent (pipeline completo)
- [ ] Integración LLM real (Anthropic/OpenAI)

### v2.0 (Futuro)
- [ ] SDLCMaintenanceAgent
- [ ] Real-time monitoring
- [ ] Predictive analytics (predecir bugs, delays)
- [ ] Integración con Jira
- [ ] Dashboard web para visualización

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
        # Tu lógica aquí
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
        # Validaciones específicas
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

**Última actualización**: 2025-11-06
**Versión**: 1.0
**Mantenedor**: @arquitecto-senior
