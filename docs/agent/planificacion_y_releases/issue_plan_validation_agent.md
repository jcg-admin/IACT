# Issue: PlanValidationAgent

**Issue ID**: IMPROVEMENT-SDLC-VALIDATION-001
**Tipo**: SDLC Workflow Improvement
**Prioridad**: P1 (Alta)
**Story Points**: 8
**Fecha Creacion**: 2025-11-13
**Estado**: PLANNING
**Asignado**: AI Agent Development Team

---

## 1. Descripcion

Crear un agente de validacion de planes SDLC que ejecute Self-Consistency (n=5 reasoning paths) para validar el plan generado en Phase 1 (Planning) ANTES de continuar a Phase 2 (Feasibility).

### 1.1 Contexto

**Gap Actual en SDLC Workflow**:
El workflow SDLC actual va directamente de:
```
Phase 1: Planning (SDLCPlannerAgent)
  |
  v
Phase 2: Feasibility (SDLCFeasibilityAgent)  <- SIN VALIDACION DEL PLAN
```

**Problema**:
- El SDLCPlannerAgent genera issue_document.md con acceptance criteria, story points, timeline
- NADIE valida si estos son correctos antes de continuar
- El FeasibilityAgent asume que el plan es valido
- Riesgo de continuar con plans flawed

**Impacto**:
- Gaps no identificados tempranamente
- Decisiones criticas no validadas
- Scope mal definido detectado tarde
- Rework en fases posteriores

### 1.2 Motivacion

**Solution Propuesta**:
Agregar **Phase 1.5: Plan Validation** usando Self-Consistency (n=5 reasoning paths) para validar el plan antes de continuar.

**Beneficios**:
- Deteccion temprana de gaps en planning
- Validacion de decisiones criticas antes de invertir tiempo
- Reduccion de rework en fases posteriores
- Mayor confidence en los plans generados

---

## 2. Requisitos Funcionales

### RF-001: Self-Consistency Validation
El agente DEBE ejecutar n=5 reasoning paths independientes:
1. **Path 1: Completeness Check** - Todos los acceptance criteria bien definidos
2. **Path 2: Technical Feasibility** - Dependencias tecnicas realistas
3. **Path 3: Timeline & Effort** - Story points y timeline razonables
4. **Path 4: Risk Analysis** - Risks identificados y mitigados
5. **Path 5: Integration & Dependencies** - Integracion con ecosystem

### RF-002: Consensus Decision
El agente DEBE:
- Ejecutar n=5 paths en paralelo (opcional)
- Aplicar majority voting
- Calcular confidence score (0-100%)
- Decidir: GO (>=80%), REVISE (<80%), NO-GO (<50%)

### RF-003: Validation Report Generation
El agente DEBE generar:
- validation_report.md con consensus analysis
- Tabla de reasoning paths con decisions
- Recommended adjustments (si aplica)
- Decision final: GO, REVISE, o NO-GO

### RF-004: Issue Document Revision
Si decision = REVISE, el agente DEBE:
- Identificar gaps especificos
- Generar recommended adjustments
- Permitir revision del issue_document.md
- Re-ejecutar validacion

### RF-005: Integration con SDLCOrchestrator
El agente DEBE:
- Integrarse como Phase 1.5 en pipeline
- Recibir issue_document path como input
- Retornar decision + confidence + adjustments
- Bloquear continuacion si NO-GO

---

## 3. Requisitos No Funcionales

### RNF-001: Performance
- Validation time: < 30 segundos (n=5 paths)
- Si paths en paralelo: < 10 segundos

### RNF-002: Confidence Threshold
- Default threshold: 80%
- Configurable via config
- Threshold >= 50% (minimo razonable)

### RNF-003: Extensibilidad
- Facil agregar nuevos reasoning paths
- Configurable n (default: 5, range: 3-7)
- Pluggable validation strategies

### RNF-004: Constitution Compliance
- Seguir Principles 1-8
- Sin emojis en output
- Trazabilidad completa
- Testing exhaustivo (TDD)

---

## 4. Acceptance Criteria

### AC-1: Componentes Implementados
- [ ] SDLCPlanValidationAgent class (hereda de SDLCAgent)
- [ ] 5 reasoning path implementations
- [ ] Consensus decision logic (majority voting)
- [ ] Validation report generator
- [ ] Integration con SDLCOrchestrator

### AC-2: Self-Consistency Execution
El agente ejecuta 5 reasoning paths independientes:
- Path 1: Completeness Check
- Path 2: Technical Feasibility
- Path 3: Timeline & Effort
- Path 4: Risk Analysis
- Path 5: Integration & Dependencies

Cada path retorna: decision (GO/REVISE/NO-GO), confidence (0-100%), findings

### AC-3: Consensus Decision
- Majority voting implementado correctamente
- Confidence score calculado como promedio ponderado
- Decision final basada en threshold (default: 80%)
- Output: decision, confidence, recommended_adjustments

### AC-4: Validation Report
Genera validation_report.md con:
- Issue ID y metadata
- Tabla de reasoning paths con decisions
- Overall decision y confidence
- Recommended adjustments (si aplica)
- Proceed to Phase 2? (YES/NO)

### AC-5: Integration con SDLCOrchestrator
- SDLCOrchestrator.execute_pipeline() incluye Phase 1.5
- Si decision = NO-GO: bloquea pipeline
- Si decision = REVISE: retorna adjustments para human review
- Si decision = GO: continua a Phase 2

### AC-6: Backward Compatibility
- Phase 1.5 es opcional (flag --skip-validation)
- Old workflow sigue funcionando
- New workflow incluye validation por default

### AC-7: Testing Coverage
- Unit tests: >= 12 tests
- Integration tests: >= 3 tests
- E2E test: Validacion de plan real (DocumentationAnalysisAgent)
- Coverage: >= 90%

### AC-8: Documentation Completa
- SDLC Phase 1: Planning (este documento)
- SDLC Phase 2: Feasibility study con Self-Consistency
- SDLC Phase 3: HLD, ADRs, LLD
- SDLC Phase 4: Implementation + Tests (TDD)
- SDLC Phase 5: Testing strategy
- SDLC Phase 6: Deployment plan

---

## 5. Self-Consistency Reasoning Paths (Detailed)

### Path 1: Completeness Check
**Objetivo**: Verificar que todos los acceptance criteria estan bien definidos

**Validations**:
- Todos los ACs son SMART (Specific, Measurable, Achievable, Relevant, Time-bound)?
- Hay ambiguedades en el scope?
- Faltan requisitos criticos?
- Los ACs cubren functional + non-functional requirements?

**Output**: GO (90%+), GO con ajustes (70-89%), REVISE (<70%)

### Path 2: Technical Feasibility
**Objetivo**: Verificar viabilidad tecnica del approach propuesto

**Validations**:
- Dependencias tecnicas son realistas?
- Hay blockers tecnicos no identificados?
- El approach propuesto es viable con stack actual?
- Hay alternatives mas simples?

**Output**: GO, GO con ajustes, REVISE, NO-GO

### Path 3: Timeline & Effort
**Objetivo**: Verificar razonabilidad de estimates

**Validations**:
- Story points son razonables comparados con proyectos similares?
- Timeline considera todos los tasks?
- Hay buffers para imprevistos?
- Estimaciones son conservative o aggressive?

**Output**: GO, GO con ajustes, REVISE

### Path 4: Risk Analysis
**Objetivo**: Identificar risks no considerados

**Validations**:
- Que risks no estan identificados?
- Hay dependencies externas riesgosas?
- Que puede salir mal (pre-mortem)?
- Hay mitigations para top 3 risks?

**Output**: GO, GO con ajustes, REVISE

### Path 5: Integration & Dependencies
**Objetivo**: Verificar integracion con ecosystem

**Validations**:
- Como se integra con sistema existente?
- Hay conflicts con otros proyectos?
- Todas las dependencies estan identificadas?
- Hay breaking changes?

**Output**: GO, GO con ajustes, REVISE

---

## 6. Consensus Decision Logic

### 6.1 Majority Voting

```python
# n=5 paths → 5 decisions
decisions = ["GO", "GO con ajustes", "GO", "REVISE", "GO"]
confidences = [85, 75, 90, 60, 85]

# Map to numeric
decision_map = {"GO": 2, "GO con ajustes": 1, "REVISE": 0, "NO-GO": -1}
numeric_decisions = [2, 1, 2, 0, 2]

# Majority voting
average_decision = mean(numeric_decisions) = 1.4

if average_decision >= 1.5:
    final_decision = "GO"
elif average_decision >= 0.5:
    final_decision = "GO con ajustes"
elif average_decision >= -0.5:
    final_decision = "REVISE"
else:
    final_decision = "NO-GO"

# Confidence
average_confidence = mean(confidences) = 79%
```

### 6.2 Decision Thresholds

| Average Decision | Confidence | Final Decision |
|------------------|------------|----------------|
| >= 1.5 | >= 80% | GO |
| >= 1.5 | < 80% | GO con ajustes |
| >= 0.5 | >= 70% | GO con ajustes |
| >= 0.5 | < 70% | REVISE |
| >= -0.5 | any | REVISE |
| < -0.5 | any | NO-GO |

---

## 7. Output Format: validation_report.md

```markdown
# Plan Validation Report: [PROJECT_NAME]

**Issue ID**: [ISSUE_ID]
**Validation Date**: [DATE]
**Validation Method**: Self-Consistency (n=5)

## Consensus Analysis

| Reasoning Path | Decision | Confidence | Key Findings |
|----------------|----------|------------|--------------|
| Path 1: Completeness | GO | 85% | All ACs well-defined |
| Path 2: Tech Feasibility | GO con ajustes | 75% | Need to clarify dependency X |
| Path 3: Timeline | GO | 90% | Realistic estimates |
| Path 4: Risks | REVISE | 60% | Missing risk mitigation for Y |
| Path 5: Integration | GO | 85% | Good integration plan |

**Overall Decision**: GO con ajustes menores
**Confidence**: 79%

## Recommended Adjustments

1. Clarify dependency on library X (version compatibility)
2. Add risk mitigation for scalability concern Y
3. Consider adding acceptance criterion for Z

## Proceed to Phase 2?

✓ YES - Confidence threshold (80%) nearly met with minor adjustments
```

---

## 8. Architecture Overview

### 8.1 Components

```
SDLCPlanValidationAgent
  |
  +-- ReasoningPath1: CompletenessChecker
  +-- ReasoningPath2: TechnicalFeasibilityAnalyzer
  +-- ReasoningPath3: TimelineEffortValidator
  +-- ReasoningPath4: RiskAnalyzer
  +-- ReasoningPath5: IntegrationValidator
  +-- ConsensusDecider
  +-- ValidationReportGenerator
```

### 8.2 Data Flow

```
Input: issue_document.md
  |
  v
Load and parse issue
  |
  v
Execute 5 reasoning paths (parallel)
  |
  v
Collect results
  |
  v
Consensus decision (majority voting)
  |
  v
Generate validation_report.md
  |
  v
Output: {decision, confidence, adjustments, report}
```

---

## 9. Integration with SDLCOrchestrator

### 9.1 Updated Pipeline

```python
class SDLCOrchestrator:
    def execute_pipeline(self, feature_request: str):
        # Phase 1: Planning
        plan_result = self.planner_agent.execute({
            "feature_request": feature_request
        })

        # Phase 1.5: Plan Validation (NEW!)
        validation_result = self.plan_validation_agent.execute({
            "issue_document": plan_result.artifacts[0],
            "project_context": self.project_context
        })

        if validation_result.data["decision"] == "NO-GO":
            return {
                "status": "blocked",
                "reason": "Plan validation failed",
                "confidence": validation_result.data["confidence"]
            }

        if validation_result.data["decision"] == "REVISE":
            return {
                "status": "requires_revision",
                "adjustments": validation_result.data["recommended_adjustments"]
            }

        # Phase 2: Feasibility (only if GO or GO con ajustes)
        feasibility_result = self.feasibility_agent.execute({
            "issue_document": plan_result.artifacts[0]
        })

        # Continue...
```

### 9.2 CLI Integration

```bash
# Old workflow (still works)
python scripts/cli/sdlc_agent.py --phase planning --feature "..."
python scripts/cli/sdlc_agent.py --phase feasibility --issue "..."

# New workflow (recommended)
python scripts/cli/sdlc_agent.py --phase planning --feature "..."
python scripts/cli/sdlc_agent.py --phase validation --issue "..."  # NEW!
python scripts/cli/sdlc_agent.py --phase feasibility --issue "..."

# Full pipeline (includes validation automatically)
python scripts/cli/sdlc_agent.py --pipeline --feature "..."  # Now includes Phase 1.5

# Skip validation (backward compatibility)
python scripts/cli/sdlc_agent.py --phase feasibility --issue "..." --skip-validation
```

---

## 10. Dependencies

### 10.1 Python Libraries
- Existing: `pathlib`, `json`, `dataclasses`, `typing`, `enum`
- No new external dependencies needed

### 10.2 Existing Components
- `scripts.coding.ai.sdlc.base_agent.SDLCAgent`: Base class
- `scripts.coding.ai.sdlc.planner_agent.SDLCPlannerAgent`: Upstream
- `scripts.coding.ai.sdlc.feasibility_agent.SDLCFeasibilityAgent`: Downstream
- `scripts.cli.sdlc_agent.py`: CLI orchestrator

---

## 11. Risks and Mitigations

### Risk 1: False Positives (Plan rechazado innecesariamente)
**Impact**: MEDIUM
**Probability**: MEDIUM
**Mitigation**:
- Threshold configurable (default: 80%)
- Majority voting reduce false positives
- Human review para REVISE cases

### Risk 2: False Negatives (Plan malo aprobado)
**Impact**: HIGH
**Probability**: LOW
**Mitigation**:
- n=5 paths aumenta coverage
- Diverse reasoning strategies
- Manual review option siempre disponible

### Risk 3: Performance (30s puede ser lento)
**Impact**: LOW
**Probability**: LOW
**Mitigation**:
- Parallel execution de paths (reduce a ~10s)
- Cache de LLM responses si aplica
- Skip validation option para iteration rapida

---

## 12. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Validation time | < 30s (sequential), < 10s (parallel) | Actual runtime |
| False positive rate | < 10% | Manual review de REVISE decisions |
| False negative rate | < 5% | Retrospective analysis |
| Plans requiring revision | < 20% | Track validation decisions |
| Average confidence | >= 80% | Average across projects |

---

## 13. Timeline (Estimated)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Planning (Phase 1) | 0.5 day | This document |
| Feasibility (Phase 2) | 0.5 day | Feasibility study with Self-Consistency |
| Design (Phase 3) | 1 day | HLD, ADRs, LLD |
| Implementation RED (Phase 4) | 0.5 day | Tests written (failing) |
| Implementation GREEN (Phase 4) | 1 day | Agent implemented, tests passing |
| Implementation REFACTOR (Phase 4) | 0.5 day | Code cleanup, 0 ruff issues |
| Testing Strategy (Phase 5) | 0.25 day | Testing documentation |
| Deployment Plan (Phase 6) | 0.25 day | Deployment documentation |
| **TOTAL** | **4 days** | Fully functional agent |

---

## 14. Example: Plan Validation in Action

### 14.1 Input

```markdown
# Issue: DocumentationAnalysisAgent

**Story Points**: 13
**Priority**: P1

## Acceptance Criteria
1. Agent analyzes Markdown files
2. Generates reports
3. Scores documentation quality
... (8 total)
```

### 14.2 Validation Process

```bash
$ python scripts/cli/sdlc_agent.py validate-plan \
    --issue docs/agent/planificacion_y_releases/issue_documentation_analysis_agent.md

Running Self-Consistency validation (n=5)...

Reasoning Path 1/5: Completeness Check... GO (75%)
Reasoning Path 2/5: Technical Feasibility... GO con ajustes (80%)
Reasoning Path 3/5: Timeline & Effort... GO (85%)
Reasoning Path 4/5: Risk Analysis... GO con ajustes (90%)
Reasoning Path 5/5: Integration... GO (90%)

Consensus: GO con ajustes menores
Confidence: 84%

Recommended Adjustments:
1. Re-prioritize phases (external link checking to Phase 4)
2. Clarify MVP scope (only Markdown in Phase 1)
3. Use mistune instead of markdown library

Decision: PROCEED TO FEASIBILITY PHASE
```

### 14.3 Output

```markdown
# Plan Validation Report

**Decision**: GO con ajustes menores
**Confidence**: 84%

## Adjustments Required:
1. Re-prioritize phases...
2. Clarify MVP scope...
3. Update dependencies...

## Proceed: YES
```

---

## 15. Related Issues & Traceability

- **Parent**: N/A (SDLC workflow improvement)
- **Related**:
  - FEATURE-DOCS-ANALYSIS-001 (beneficiario inmediato)
  - FEATURE-SHELL-ANALYSIS-001 (pattern reference)
- **Blocks**: All future SDLC projects
- **References**:
  - `docs/agent/gobernanza/sdlc_workflow_improvement_proposal.md`
  - `scripts/coding/ai/sdlc/base_agent.py`
  - `scripts/cli/sdlc_agent.py`

---

## 16. Approval & Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | TBD | Pending | - |
| Tech Lead | TBD | Pending | - |
| AI Agent Developer | Claude | Proposed | 2025-11-13 |

---

**Trazabilidad**: IMPROVEMENT-SDLC-VALIDATION-001
**Metodologia**: SDLC + TDD + Self-Consistency
**Prioridad**: P1 (debe implementarse antes de continuar otros agentes)
**Impacto**: Todos los futuros proyectos SDLC
**Estado**: PLANNING - Listo para Feasibility Phase
