---
title: Feature: Agente de Análisis Exhaustivo de Scripts Shell
date: 2025-11-13
domain: ai
status: active
---

# Feature: Agente de Análisis Exhaustivo de Scripts Shell

**Issue ID**: FEATURE-SHELL-ANALYSIS-001
**Fecha**: 2025-11-13
**Fase SDLC**: Planning
**Autor**: Claude (SDLC Agent)
**Estado**: Planning

---

## User Story

**Como** ingeniero de DevOps del proyecto IACT
**Quiero** un agente AI que analice exhaustivamente todos los scripts shell del proyecto
**Para** generar reportes automáticos de calidad, cumplimiento constitucional y recomendaciones de refactoring

---

## Contexto del Negocio

El proyecto IACT tiene **253 scripts shell** distribuidos en:
- Validaciones (30+ scripts)
- CI/CD (20+ scripts)
- Infrastructure (100+ scripts)
- Git hooks (10+ scripts)

Actualmente existe:
- `validate_shell_constitution.sh` - Valida 8 reglas constitucionales
- `validate-scripts.sh` - Valida sintaxis básica

**Problema**: No hay análisis exhaustivo automatizado que:
1. Consolide todos los resultados en un solo reporte
2. Identifique patrones de código duplicado
3. Detecte oportunidades de refactoring
4. Genere métricas de calidad agregadas
5. Produzca recomendaciones priorizadas

**Solución propuesta**: Crear `ShellScriptAnalysisAgent` que analice todos los scripts y genere reportes en `docs/scripts/analisis/`.

---

## Acceptance Criteria

### Criterio 1: Estructura del Agente
- [ ] AC-001-01: Agente hereda de `Agent` base class (`scripts/coding/ai/shared/agent_base.py`)
- [ ] AC-001-02: Integra automáticamente con constitution loader
- [ ] AC-001-03: Implementa guardrails automáticos (sin emojis, trazabilidad, etc.)
- [ ] AC-001-04: Ubicado en `scripts/coding/ai/agents/quality/shell_analysis_agent.py`

### Criterio 2: Análisis Constitucional
- [ ] AC-002-01: Valida las 8 reglas de `SHELL_SCRIPTS_CONSTITUTION.md`
- [ ] AC-002-02: Genera score de compliance (0-100) por script
- [ ] AC-002-03: Identifica violaciones con severidad (LOW/MEDIUM/HIGH/CRITICAL)
- [ ] AC-002-04: Proporciona recomendaciones específicas por violación

### Criterio 3: Análisis de Calidad de Código
- [ ] AC-003-01: Detecta code smells (funciones largas, duplicación, etc.)
- [ ] AC-003-02: Calcula métricas (LOC, complejidad ciclomática, número de funciones)
- [ ] AC-003-03: Identifica patrones anti-pattern comunes en shell
- [ ] AC-003-04: Sugiere refactoring opportunities priorizadas

### Criterio 4: Análisis de Seguridad
- [ ] AC-004-01: Detecta command injection vulnerabilities
- [ ] AC-004-02: Identifica uso inseguro de variables sin quotes
- [ ] AC-004-03: Detecta eval/exec usage
- [ ] AC-004-04: Valida input sanitization

### Criterio 5: Generación de Reportes
- [ ] AC-005-01: Genera reporte individual por script en formato Markdown
- [ ] AC-005-02: Genera reporte consolidado de todos los scripts
- [ ] AC-005-03: Exporta datos estructurados en formato JSON
- [ ] AC-005-04: Todos los reportes en `docs/scripts/analisis/`

### Criterio 6: Técnicas de Prompting
- [ ] AC-006-01: Implementa Chain-of-Verification para validación SOLID-like
- [ ] AC-006-02: Usa Auto-CoT para razonamiento sobre complejidad
- [ ] AC-006-03: Aplica Search Optimization para detectar code smells
- [ ] AC-006-04: Documenta qué técnica se usa en cada fase

### Criterio 7: Testing y Calidad
- [ ] AC-007-01: Tests unitarios con coverage >= 90%
- [ ] AC-007-02: Tests de integración que validen scripts de ejemplo
- [ ] AC-007-03: Documentación completa con ejemplos de uso
- [ ] AC-007-04: Pasa pre-commit hooks (no emojis, linting, etc.)

### Criterio 8: Integración y Documentación
- [ ] AC-008-01: Actualiza `docs/gobernanza/agentes/README.md` con nuevo agente
- [ ] AC-008-02: Crea guía de uso en `docs/scripts/shell-analysis-guide.md`
- [ ] AC-008-03: Actualiza `scripts/coding/ai/requirements.txt` con dependencias
- [ ] AC-008-04: Ejemplo de uso en `scripts/coding/ai/examples/`

---

## Technical Requirements

### TR-001: Dependencias
```
pytest>=7.0.0
pytest-cov>=4.0.0
anthropic>=0.72.0 (si usa LLM para análisis avanzado)
ruff>=0.7.0
black>=24.0.0
shellcheck (externo, validar disponibilidad)
```

### TR-002: Input Schema
```python
{
    "script_path": str,              # Path al script o directorio
    "analysis_depth": str,           # "quick" | "standard" | "deep"
    "constitutional_rules": List[int], # [1,2,3,4,5,6,7,8] por defecto
    "include_security": bool,        # True por defecto
    "generate_recommendations": bool, # True por defecto
    "output_format": str             # "markdown" | "json" | "both"
}
```

### TR-003: Output Schema
```python
{
    "script_name": str,
    "analysis_timestamp": str,
    "overall_score": float,          # 0-100
    "constitutional_compliance": {
        "rule_1": {"compliant": bool, "score": float, "violations": List},
        # ... rules 2-8
    },
    "code_quality": {
        "metrics": {"loc": int, "functions": int, "complexity": float},
        "code_smells": List[CodeSmell],
        "refactoring_opportunities": List[Refactoring]
    },
    "security": {
        "issues": List[SecurityIssue],
        "severity_counts": {"critical": int, "high": int, "medium": int, "low": int}
    },
    "recommendations": List[Recommendation]  # Priorizadas por impacto
}
```

### TR-004: Técnicas de Prompting a Usar

1. **Chain-of-Verification** (para análisis constitucional):
   - Baseline analysis
   - Verification questions per rule
   - Independent verifications
   - Final synthesis

2. **Auto-CoT** (para razonamiento sobre complejidad):
   - Automatic chain-of-thought generation
   - Step-by-step reasoning sobre code patterns
   - Self-explanation de decisiones

3. **Search Optimization** (para code smells):
   - Pattern matching optimizado
   - Heuristic search para duplicación
   - Best-first search para refactoring oportunities

### TR-005: Restricciones Constitucionales

Según `docs/gobernanza/agentes/constitution.md`:
- PROHIBIDO: Emojis en output
- OBLIGATORIO: Trazabilidad (REQ-*, SPEC-*, ADR-*)
- OBLIGATORIO: Tests antes de código (TDD)
- OBLIGATORIO: Docstrings formato Google
- OBLIGATORIO: Type hints completos

---

## Story Points Estimation

**Complejidad**: Alta
**Esfuerzo estimado**: 13 puntos

**Desglose**:
- Setup de agente base y estructura: 2 puntos
- Implementación de análisis constitucional: 3 puntos
- Implementación de análisis de calidad: 3 puntos
- Análisis de seguridad: 2 puntos
- Generación de reportes: 2 puntos
- Testing y documentación: 1 punto

---

## Priority

**P1 - High Priority**

**Justificación**:
- Impacta calidad de 253 scripts existentes
- Automatiza trabajo manual actual
- Base para mejora continua de scripts
- Requerido para mantener estándares de calidad

---

## Labels

- `feature`
- `ai-agent`
- `quality`
- `shell-scripts`
- `sdlc`
- `priority-high`

---

## Dependencies

### Dependencias Técnicas:
- Constitution framework (`scripts/coding/ai/shared/agent_base.py`)
- Shell constitution (`docs/SHELL_SCRIPTS_CONSTITUTION.md`)
- Validation tools (`scripts/validation/quality/validate_shell_constitution.sh`)

### Dependencias de Proceso:
- Fase Feasibility (siguiente paso)
- Fase Design (después de feasibility)
- Instalación de dependencias Python

### Bloqueadores Actuales:
- [ ] Dependencias Python no instaladas (pytest, anthropic, ruff, etc.)
- [ ] Falta validar disponibilidad de shellcheck
- [ ] Falta API key de Anthropic (si se usa LLM)

---

## Risks and Mitigations

### Riesgo 1: Análisis muy lento con 253 scripts
**Probabilidad**: Media
**Impacto**: Alto
**Mitigación**:
- Implementar análisis paralelo
- Cache de resultados
- Modo "quick" para análisis rápido

### Riesgo 2: Falsos positivos en validación
**Probabilidad**: Alta
**Impacto**: Medio
**Mitigación**:
- Usar Chain-of-Verification para reducir falsos positivos
- Permitir configuración de reglas a ignorar
- Revisión manual de recomendaciones críticas

### Riesgo 3: Dependencia de API externa (Anthropic)
**Probabilidad**: Baja
**Impacto**: Alto
**Mitigación**:
- Implementar modo heurístico sin LLM
- Fallback a análisis basado en reglas estáticas
- Documentar ambos modos

---

## Next Steps (Workflow)

1. **ACTUAL**: Planning (este documento) ✓
2. **SIGUIENTE**: Feasibility Analysis
   - Validar disponibilidad de herramientas (shellcheck, python deps)
   - Estimar tiempo de ejecución con 253 scripts
   - Validar que framework de agentes funciona
   - Análisis de riesgos técnicos

3. **DESPUÉS**: Design
   - HLD: Arquitectura del agente
   - LLD: Clases y métodos específicos
   - ADR: Decisiones arquitectónicas clave

4. **LUEGO**: Implementation (TDD)
5. **FINALMENTE**: Testing, Deployment

---

## Traceability

**Feature Request Original**: "Análisis exhaustivo de scripts y resultado en docs/scripts/analisis"
**SDLC Phase**: Planning (1/6)
**Document**: `docs/sdlc_outputs/planning/issue-shell-script-analysis-agent.md`
**Related Docs**:
- `docs/gobernanza/agentes/README.md` - Framework de agentes
- `docs/SHELL_SCRIPTS_CONSTITUTION.md` - Reglas constitucionales
- `docs/scripts/sdlc-agent-guide.md` - Metodología SDLC

---

**Generado por**: Claude (SDLCPlannerAgent)
**Timestamp**: 2025-11-13T08:15:00Z
**Metodología**: SDLC Planning Phase
**Próximo paso**: Feasibility Analysis
