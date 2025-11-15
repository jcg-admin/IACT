---
name: SDLCPlanValidationAgent
description: Agente especializado en validación de planes SDLC, verificación de completitud, consistencia entre fases, identificación de gaps y recomendaciones de mejora en documentación.
---

# SDLC Plan Validation Agent

SDLCPlanValidationAgent es un agente Python especializado en validar la completitud y consistencia de planes SDLC. Su función principal es verificar que todos los artefactos de planning, diseño, testing y deployment estén completos, sean consistentes entre sí, identificar gaps y proporcionar recomendaciones de mejora.

## Capacidades

### Validación de Completitud

- Verificación de artefactos requeridos por fase
- Identificación de documentación faltante
- Validación de secciones obligatorias
- Checklist de requisitos mínimos
- Detección de placeholders sin completar

### Análisis de Consistencia

- Verificación de consistencia entre fases
- Validación de trazabilidad requisitos-tests
- Coherencia entre diseño e implementación
- Alineación de estimaciones entre fases
- Consistencia de terminología y nomenclatura

### Identificación de Gaps

- Detección de requisitos no cubiertos
- Identificación de casos de prueba faltantes
- Análisis de cobertura de diseño
- Gaps en documentación de deployment
- Riesgos no documentados

### Recomendaciones de Mejora

- Sugerencias de documentación adicional
- Mejoras en claridad y detalle
- Optimizaciones de procesos
- Best practices no seguidas
- Referencias a estándares

## Cuándo Usarlo

### Antes de Implementación

- Validación de plan completo antes de comenzar
- Verificación de approval readiness
- Identificación temprana de gaps
- Aseguramiento de calidad de planning

### Durante Sprint Planning

- Validación de issues antes de commitment
- Verificación de acceptance criteria
- Validación de estimaciones
- Checklist de readiness

### Code Review

- Validación de implementación vs diseño
- Verificación de tests vs requisitos
- Consistencia de documentación
- Validación de deployment plan

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/plan_validation_agent.py \
  --plan-dir plans/feature_xyz/ \
  --validate-all
```

### Validación Específica por Fase

```bash
python scripts/coding/ai/sdlc/plan_validation_agent.py \
  --planning-doc plans/planning.md \
  --design-doc plans/design.md \
  --test-plan plans/test_plan.md \
  --deployment-plan plans/deployment.md \
  --check-consistency
```

### Parámetros Principales

- `--plan-dir`: Directorio con todos los documentos de plan
- `--planning-doc`: Documento de planning a validar
- `--design-doc`: Documento de diseño a validar
- `--test-plan`: Plan de testing a validar
- `--deployment-plan`: Plan de deployment a validar
- `--validate-all`: Validar todas las fases
- `--check-consistency`: Verificar consistencia entre documentos
- `--identify-gaps`: Identificar gaps en cobertura
- `--output-format`: Formato de reporte (markdown, json, html)

## Ejemplos de Uso

### Ejemplo 1: Validación Completa de Plan

```bash
python scripts/coding/ai/sdlc/plan_validation_agent.py \
  --plan-dir plans/payment_integration/ \
  --validate-all \
  --check-consistency \
  --identify-gaps
```

Genera:
- Reporte de completitud por fase
- Lista de documentos faltantes
- Inconsistencias identificadas
- Gaps de cobertura
- Recomendaciones priorizadas

### Ejemplo 2: Validación de Planning Document

```bash
python scripts/coding/ai/sdlc/plan_validation_agent.py \
  --planning-doc plans/user_authentication.md \
  --validate-structure \
  --check-acceptance-criteria
```

Genera:
- Validación de estructura de user story
- Verificación de acceptance criteria
- Identificación de requisitos ambiguos
- Sugerencias de mejora

### Ejemplo 3: Validación de Trazabilidad

```bash
python scripts/coding/ai/sdlc/plan_validation_agent.py \
  --planning-doc plans/planning.md \
  --test-plan plans/test_plan.md \
  --check-traceability
```

Genera:
- Matriz de trazabilidad requisitos-tests
- Requisitos sin tests identificados
- Tests sin requisitos asociados
- Recomendaciones de coverage

## Outputs Generados

### Reporte de Validación

```markdown
# Validation Report: Payment Integration Feature

## Executive Summary
- Overall Status: PASS WITH WARNINGS
- Completeness: 85%
- Consistency: 90%
- Gaps Identified: 5
- Critical Issues: 0
- Warnings: 3

## Completeness Analysis

### Planning Phase: COMPLETE
- [OK] User story defined
- [OK] Acceptance criteria (5 items)
- [OK] Story points estimated (8 points)
- [OK] Technical requirements documented
- [WARNING] No risk analysis section

### Design Phase: COMPLETE
- [OK] HLD document present
- [OK] LLD document present
- [OK] API specification (OpenAPI)
- [OK] Database schema
- [WARNING] Missing sequence diagrams for error flows

### Testing Phase: NEEDS ATTENTION
- [OK] Unit test plan
- [OK] Integration test plan
- [ERROR] E2E test scenarios missing
- [OK] Coverage target defined (80%)

### Deployment Phase: COMPLETE
- [OK] Deployment runbook
- [OK] Rollback procedure
- [OK] Communication plan
- [OK] Success metrics

## Consistency Analysis

### Requirements → Design: CONSISTENT
- All user stories have corresponding design sections
- Technical requirements reflected in architecture

### Design → Tests: MOSTLY CONSISTENT
- [OK] All API endpoints have integration tests
- [WARNING] Error handling paths not fully tested
- [OK] Database schema has migration tests

### Tests → Deployment: CONSISTENT
- All smoke tests referenced in runbook
- Health checks aligned with test expectations

## Gaps Identified

### Critical Gaps: 0
(None)

### Important Gaps: 2
1. **E2E Test Scenarios Missing**
   - Impact: Cannot validate complete user flows
   - Recommendation: Add 2-3 E2E scenarios covering happy path and error cases
   - Effort: 3-5 hours

2. **Error Flow Sequence Diagrams Missing**
   - Impact: Difficult to understand error handling architecture
   - Recommendation: Add sequence diagrams for payment failure flows
   - Effort: 2 hours

### Minor Gaps: 3
1. No risk analysis in planning document
2. Missing performance benchmarks in test plan
3. Monitoring dashboard not referenced in deployment plan

## Recommendations

### Priority 1 (Must Have)
1. Add E2E test scenarios for payment flows
2. Document error handling in design

### Priority 2 (Should Have)
1. Add risk analysis section to planning
2. Include performance testing in test plan
3. Reference monitoring dashboards in runbook

### Priority 3 (Nice to Have)
1. Add more sequence diagrams for clarity
2. Include rollback test procedure
3. Document post-deployment validation steps

## Traceability Matrix

| Requirement | Design Section | Unit Tests | Integration Tests | E2E Tests |
|-------------|----------------|------------|-------------------|-----------|
| REQ-1: Process payment | HLD-3.2 | ✓ | ✓ | [MISSING] |
| REQ-2: Validate card | LLD-4.1 | ✓ | ✓ | [MISSING] |
| REQ-3: Handle errors | LLD-4.3 | ✓ | ✓ | [MISSING] |
| REQ-4: Send notification | HLD-3.4 | ✓ | ✓ | ✓ |
| REQ-5: Log transaction | LLD-4.5 | ✓ | ✓ | ✓ |

Coverage: 3/5 requirements have E2E tests (60%)

## Action Items

1. [ ] Add E2E test scenarios (Owner: QA Lead, Due: 2 days)
2. [ ] Add error flow diagrams (Owner: Tech Lead, Due: 1 day)
3. [ ] Add risk analysis (Owner: Product Owner, Due: 1 day)
4. [ ] Review and approve (Owner: Engineering Manager)
```

### Validation Checklist

```markdown
# SDLC Plan Validation Checklist

## Planning Phase
- [ ] User story in standard format
- [ ] Acceptance criteria clear and testable
- [ ] Story points estimated
- [ ] Technical requirements identified
- [ ] Dependencies documented
- [ ] Risk analysis included

## Design Phase
- [ ] HLD document present
- [ ] LLD document present
- [ ] API specifications complete
- [ ] Database schema defined
- [ ] Sequence diagrams for key flows
- [ ] Architecture decisions documented

## Testing Phase
- [ ] Unit test plan (70% of tests)
- [ ] Integration test plan (20% of tests)
- [ ] E2E test plan (10% of tests)
- [ ] Coverage target defined (≥80%)
- [ ] Test data strategy
- [ ] Performance testing included

## Deployment Phase
- [ ] Deployment runbook complete
- [ ] Rollback procedure defined
- [ ] Communication plan
- [ ] Success metrics
- [ ] Monitoring and alerts
- [ ] Post-deployment validation

## Cross-Phase Validation
- [ ] Requirements traced to tests
- [ ] Design consistent with requirements
- [ ] Tests cover all acceptance criteria
- [ ] Deployment plan references tests
```

## Herramientas y Dependencias

- **Document Parsing**: Markdown, YAML, JSON parsers
- **Validation**: Schema validators, regex patterns
- **Analysis**: NLP for semantic consistency
- **LLM**: Claude, GPT-4 para análisis de contenido
- **Reporting**: Jinja2 templates, HTML/PDF generation

## Mejores Prácticas

### Validación Regular

- Ejecutar al final de cada fase SDLC
- Validar antes de sprint planning
- Re-validar después de cambios significativos
- Incluir en definition of done

### Interpretación de Resultados

- PASS: Proceder con confianza
- PASS WITH WARNINGS: Addressar warnings antes de implementar
- NEEDS ATTENTION: Completar gaps críticos antes de continuar
- FAIL: No proceder hasta resolver issues críticos

### Mejora Continua

- Actualizar checklists basados en lecciones aprendidas
- Refinar criterios de validación
- Automatizar validaciones en CI/CD
- Mantener templates actualizados

## Restricciones

- Validación automática no reemplaza code review
- Algunos aspectos requieren validación manual
- Calidad de validación depende de calidad de inputs
- No detecta todos los tipos de inconsistencias lógicas

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/plan_validation_agent.py`
