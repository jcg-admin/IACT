---
title: SDLC Workflow Improvement Proposal: Plan Validation Phase
date: 2025-11-13
domain: ai
status: active
---

# SDLC Workflow Improvement Proposal: Plan Validation Phase

**Proposal ID**: IMPROVEMENT-SDLC-VALIDATION-001
**Fecha**: 2025-11-13
**Estado**: PROPUESTO
**Prioridad**: P1 (Alta)
**Impacto**: Todos los futuros proyectos SDLC

---

## 1. Resumen Ejecutivo

**Problema Identificado**:
Los agentes SDLC actuales carecen de un paso de validación del plan generado en Phase 1 (Planning) ANTES de continuar a Phase 2 (Feasibility).

**Impacto**:
- Riesgo de continuar con plans flawed
- Gaps no identificados tempranamente
- Decisiones críticas no validadas
- Scope mal definido detectado tarde

**Solución Propuesta**:
Agregar **Phase 1.5: Plan Validation** usando Self-Consistency (n=5 reasoning paths) para validar el plan antes de continuar.

---

## 2. Gap Actual en SDLC Workflow

### 2.1 Workflow Actual

```
Phase 1: Planning (SDLCPlannerAgent)
  │
  │ OUTPUT: issue_document.md
  │
  ▼
Phase 2: Feasibility (SDLCFeasibilityAgent)  ← SIN VALIDACIÓN DEL PLAN
  │
  │ OUTPUT: feasibility_study.md
  │
  ▼
Phase 3: Design (SDLCDesignAgent)
  ...
```

### 2.2 Problema

El `SDLCPlannerAgent` genera un issue document con:
- Acceptance criteria
- Story points
- Technical requirements
- Timeline estimates

Pero **NADIE valida si estos son correctos** antes de continuar. El FeasibilityAgent asume que el plan es válido.

---

## 3. Workflow Propuesto (Mejorado)

```
Phase 1: Planning (SDLCPlannerAgent)
  │
  │ OUTPUT: issue_document.md (DRAFT)
  │
  ▼
Phase 1.5: Plan Validation (NEW!)
  │
  │ TECHNIQUE: Self-Consistency (n=5 reasoning paths)
  │ VALIDATES:
  │   - Are acceptance criteria complete?
  │   - Is scope well-defined?
  │   - Are dependencies identified?
  │   - Is timeline realistic?
  │   - Are risks considered?
  │
  │ OUTPUT: validation_report.md
  │          + issue_document.md (REVISED si es necesario)
  │
  ├──> Decision: GO (confidence >= 80%)
  │    └─> Continue to Phase 2
  │
  └──> Decision: NO-GO o REVISE (confidence < 80%)
       └─> Return to Phase 1 con adjustments
  │
  ▼
Phase 2: Feasibility (SDLCFeasibilityAgent)
  ...
```

---

## 4. Self-Consistency Validation Framework

### 4.1 Reasoning Paths

Para cada plan generado, ejecutar n=5 reasoning paths independientes:

**Path 1: Completeness Check**
- ¿Están todos los acceptance criteria bien definidos?
- ¿Falta algún requisito crítico?
- ¿Hay ambigüedades en el scope?

**Path 2: Technical Feasibility**
- ¿Son las dependencias técnicas realistas?
- ¿Hay blockers técnicos no identificados?
- ¿El approach propuesto es viable?

**Path 3: Timeline & Effort**
- ¿Son los story points razonables?
- ¿El timeline es realista?
- ¿Se consideraron todos los tasks?

**Path 4: Risk Analysis**
- ¿Qué risks no están identificados?
- ¿Hay dependencies externas riesgosas?
- ¿Qué puede salir mal?

**Path 5: Integration & Dependencies**
- ¿Cómo se integra con el ecosystem existente?
- ¿Hay conflicts con otros proyectos?
- ¿Se identificaron todas las dependencies?

### 4.2 Consensus Decision

```python
# n=5 paths → 5 decisions
decisions = ["GO", "GO con ajustes", "GO", "REVISE scope", "GO"]

# Majority voting
go_votes = 4/5 = 80%
confidence = 80%

if confidence >= 80%:
    decision = "GO"
    # Proceed to Phase 2
else:
    decision = "REVISE"
    # Return to Phase 1 with recommended adjustments
```

### 4.3 Output Format

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

✓ YES - Confidence threshold (80%) met with minor adjustments
```

---

## 5. Implementation Plan

### 5.1 Create PlanValidationAgent

**File**: `scripts/coding/ai/sdlc/plan_validation_agent.py`

```python
class SDLCPlanValidationAgent(SDLCAgent):
    """
    Agente para validar el plan generado en Phase 1 usando Self-Consistency.

    Ejecuta n=5 reasoning paths independientes y determina si el plan
    es sólido antes de continuar al Feasibility Study.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCPlanValidationAgent",
            phase="planning_validation",
            config=config
        )
        self.n_paths = self.config.get("n_reasoning_paths", 5)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.80)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the plan using Self-Consistency.

        Args:
            input_data: {
                "issue_document": "path/to/issue.md",
                "project_context": {...}
            }

        Returns:
            {
                "decision": "GO" | "REVISE" | "NO-GO",
                "confidence": 0.0 - 1.0,
                "reasoning_paths": [...]
                "recommended_adjustments": [...]
            }
        """
        issue_doc = self._load_issue(input_data["issue_document"])

        # Execute n reasoning paths
        reasoning_results = []
        for i in range(self.n_paths):
            result = self._execute_reasoning_path(i+1, issue_doc)
            reasoning_results.append(result)

        # Consensus analysis
        decision, confidence = self._consensus_decision(reasoning_results)
        adjustments = self._extract_adjustments(reasoning_results)

        # Generate validation report
        report = self._generate_validation_report(
            decision=decision,
            confidence=confidence,
            reasoning_results=reasoning_results,
            adjustments=adjustments
        )

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning_paths": reasoning_results,
            "recommended_adjustments": adjustments,
            "validation_report": report
        }
```

### 5.2 Update SDLCOrchestrator

Add Phase 1.5 to the pipeline:

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
            # Return for human review
            return {
                "status": "requires_revision",
                "adjustments": validation_result.data["recommended_adjustments"]
            }

        # Phase 2: Feasibility (only if GO)
        feasibility_result = self.feasibility_agent.execute({
            "issue_document": plan_result.artifacts[0]
        })

        # Continue...
```

### 5.3 Update Documentation

Files to update:
- `docs/scripts/sdlc-agent-guide.md`: Add Phase 1.5 section
- `scripts/coding/ai/sdlc/README.md`: Update workflow diagram
- `docs/gobernanza/agentes/constitution.md`: Add Principle 9 reference (Self-Consistency)

---

## 6. Benefits

### 6.1 Immediate Benefits
- Detección temprana de gaps en planning
- Validación de decisiones críticas antes de invertir tiempo
- Reducción de rework en fases posteriores
- Mayor confidence en los plans generados

### 6.2 Long-term Benefits
- Mejor calidad de proyectos SDLC
- Pattern reusable para otros validation workflows
- Aprendizaje continuo (ajustar thresholds basado en experiencia)
- Documentación de reasoning para future reference

---

## 7. Effort Estimate

| Task | Effort | Owner |
|------|--------|-------|
| Design PlanValidationAgent | 0.5 day | AI Team |
| Implement PlanValidationAgent | 1 day | AI Team |
| Write unit tests (TDD) | 0.5 day | AI Team |
| Update SDLCOrchestrator | 0.5 day | AI Team |
| Update documentation | 0.5 day | AI Team |
| Integration testing | 0.5 day | QA Team |
| **TOTAL** | **3.5 days** | - |

---

## 8. Example: Plan Validation in Action

### 8.1 Input

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

### 8.2 Validation Process

```bash
$ python scripts/cli/sdlc_agent.py validate-plan \
    --issue docs/ai/agent/planificacion_y_releases/issue_documentation_analysis_agent.md

Running Self-Consistency validation (n=5)...

Reasoning Path 1/5: Completeness Check... GO (75%)
Reasoning Path 2/5: Technical Feasibility... GO with adjustments (80%)
Reasoning Path 3/5: Timeline & Effort... GO (85%)
Reasoning Path 4/5: Risk Analysis... GO with adjustments (90%)
Reasoning Path 5/5: Integration... GO (90%)

Consensus: GO with minor adjustments
Confidence: 84%

Recommended Adjustments:
1. Re-prioritize phases (external link checking to Phase 4)
2. Clarify MVP scope (only Markdown in Phase 1)
3. Use mistune instead of markdown library

Decision: PROCEED TO FEASIBILITY PHASE ✓
```

### 8.3 Output

```markdown
# Plan Validation Report

**Decision**: GO with minor adjustments
**Confidence**: 84%

## Adjustments Required:
1. Re-prioritize phases...
2. Clarify MVP scope...
3. Update dependencies...

## Proceed: YES ✓
```

---

## 9. Integration with Existing Workflow

### 9.1 Backward Compatibility

El nuevo Phase 1.5 es **opcional** para mantener backward compatibility:

```bash
# Old workflow (still works)
$ python scripts/cli/sdlc_agent.py --phase planning --feature "..."
$ python scripts/cli/sdlc_agent.py --phase feasibility --issue "..."

# New workflow (recommended)
$ python scripts/cli/sdlc_agent.py --phase planning --feature "..."
$ python scripts/cli/sdlc_agent.py --phase validation --issue "..."  # NEW!
$ python scripts/cli/sdlc_agent.py --phase feasibility --issue "..."

# Full pipeline (includes validation automatically)
$ python scripts/cli/sdlc_agent.py --pipeline --feature "..."  # Now includes Phase 1.5
```

### 9.2 Manual Override

Para casos donde human review es suficiente:

```bash
$ python scripts/cli/sdlc_agent.py --phase feasibility --issue "..." --skip-validation
```

---

## 10. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Plans requiring revision | Unknown | < 20% | Track validation decisions |
| Average validation confidence | N/A | >= 80% | Average across projects |
| Time saved by early detection | N/A | ~1 day/project | Estimate rework avoided |
| False positive rate | N/A | < 10% | Manual review of "REVISE" decisions |

---

## 11. Next Steps

1. **Week 1**: Implement PlanValidationAgent
2. **Week 2**: Integration testing + Documentation
3. **Week 3**: Pilot with 3 real projects
4. **Week 4**: Rollout to all SDLC workflows
5. **Month 2**: Collect metrics and refine thresholds

---

## 12. Conclusion

Adding Phase 1.5 (Plan Validation) fills a critical gap in our SDLC workflow. Using Self-Consistency, we can validate plans BEFORE investing significant effort in downstream phases, saving time and improving quality.

**Decision**: Implement this improvement in parallel with DocumentationAnalysisAgent project

**Priority**: P1 (should be done first to validate Doc Analysis plan)

---

**Trazabilidad**: IMPROVEMENT-SDLC-VALIDATION-001
**Related**: FEATURE-DOCS-ANALYSIS-001, FEATURE-SHELL-ANALYSIS-001
**Metodología**: Self-Consistency (Principle 9)
**Aprobación**: Pendiente de Tech Lead review
