---
name: BusinessRulesValidatorAgent
description: Agente especializado en validacion de reglas de negocio, verificando consistencia logica, integridad de constraints, cumplimiento de invariantes y validacion de flujos de negocio.
---

# Automation: Business Rules Validator Agent

El BusinessRulesValidatorAgent valida reglas de negocio en codigo, verificando consistencia logica, integridad de constraints, cumplimiento de invariantes y correctitud de flujos de negocio.

## Capacidades

### Validacion de Reglas
- Business logic consistency
- Constraint validation
- Invariant checking
- State machine validation
- Workflow correctness

### Deteccion de Inconsistencias
- Conflicting business rules
- Missing validations
- Logic gaps
- Edge case handling
- Error handling completeness

### Analisis de Flujos
- State transitions
- Business process flows
- Decision tree completeness
- Authorization rules
- Data validation rules

### Domain Model Validation
- Entity relationships
- Aggregate consistency
- Domain invariants
- Value object validation

### Scenario Testing
- Business scenario validation
- Rule coverage analysis
- Test case generation
- Counterexample detection

## Cuando usar

- **Pre-Merge**: Validar cambios en business logic
- **Refactoring**: Verificar preservacion de reglas
- **Feature Development**: Validar nuevas reglas de negocio
- **Bug Investigation**: Identificar violaciones de reglas
- **Documentation**: Generar documentacion de reglas
- **Onboarding**: Educar en business rules del dominio

## Como usar

### Validacion Completa

```bash
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --validate-all \
  --domain api/callcentersite \
  --output rules_report.json
```

### Validacion Especifica

```bash
# Validar modelo especifico
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --validate-model Call \
  --domain api/callcentersite/calls

# Validar flujo de negocio
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --validate-workflow call_handling \
  --definition workflows/call_handling.yaml

# Validar constraints
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --validate-constraints \
  --model Customer
```

### Deteccion de Inconsistencias

```bash
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --detect-inconsistencies \
  --domain api/ \
  --report-conflicts
```

### Analisis de Cobertura

```bash
# Verificar coverage de reglas
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --analyze-coverage \
  --rules-file business_rules.yaml \
  --tests tests/

# Generar test cases faltantes
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --generate-missing-tests \
  --rules business_rules.yaml \
  --output tests/generated/
```

### Validacion de Escenarios

```bash
python scripts/coding/ai/automation/business_rules_validator_agent.py \
  --validate-scenarios \
  --scenarios scenarios/call_center.yaml \
  --verify-completeness
```

## Output esperado

### Reporte de Validacion

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "domain": "api/callcentersite",
  "validation_status": "failed",
  "rules_validated": 45,
  "violations": [
    {
      "rule_id": "BR_001",
      "severity": "error",
      "type": "missing_validation",
      "description": "Call duration must be positive",
      "location": "api/calls/models.py:Call.duration",
      "line": 23,
      "recommendation": "Add validation: assert duration > 0",
      "impact": "Invalid data can be persisted"
    },
    {
      "rule_id": "BR_015",
      "severity": "warning",
      "type": "inconsistent_logic",
      "description": "Call status transitions not validated",
      "location": "api/calls/views.py:update_call_status",
      "line": 78,
      "recommendation": "Implement state machine validation",
      "impact": "Invalid state transitions possible"
    }
  ],
  "inconsistencies": [
    {
      "type": "conflicting_rules",
      "rule_1": "BR_005: Agent must be available to take call",
      "rule_2": "BR_012: Call can be assigned to unavailable agent",
      "conflict": "Contradictory assignment rules",
      "resolution": "Clarify priority and update BR_012"
    }
  ],
  "coverage": {
    "total_rules": 45,
    "covered_by_tests": 38,
    "coverage_percentage": 84.4,
    "missing_tests": [
      "BR_023: Overflow routing",
      "BR_031: Emergency call priority"
    ]
  }
}
```

### Business Rules Documentation

```markdown
# Business Rules Validation Report

## Summary
- Total Rules: 45
- Violations: 2
- Coverage: 84.4%
- Status: FAILED

## Critical Violations

### BR_001: Call Duration Validation
**Severity**: ERROR
**Location**: api/calls/models.py:23
**Issue**: Missing validation for positive duration
**Impact**: Invalid data can be persisted
**Recommendation**: Add constraint validation

### BR_015: Call Status Transitions
**Severity**: WARNING
**Location**: api/calls/views.py:78
**Issue**: State transitions not validated
**Impact**: Invalid state changes possible
**Recommendation**: Implement state machine

## Rule Inconsistencies

### Conflict: Agent Assignment Rules
- **BR_005**: Agent must be available to take call
- **BR_012**: Call can be assigned to unavailable agent
- **Resolution**: Update BR_012 to respect BR_005

## Coverage Analysis
- Rules with tests: 38/45 (84.4%)
- Missing test coverage:
  - BR_023: Overflow routing
  - BR_031: Emergency call priority

## Recommendations
1. Fix critical violations before deployment
2. Resolve rule conflicts in business logic
3. Add missing test coverage
4. Implement state machine validation
```

## Herramientas y dependencias

- **Python 3.11+**
- **AST parsing**: ast, astroid
- **Symbolic execution**: z3-solver (optional)
- **State machines**: transitions
- **YAML**: PyYAML para rule definitions

## Buenas practicas

1. **Documentar reglas**: Mantener business_rules.yaml actualizado
2. **Test coverage**: Cada regla debe tener tests
3. **State machines**: Usar para flujos complejos
4. **Validacion temprana**: En models, no en views
5. **Invariantes explicitos**: Documentar constraints
6. **Revision periodica**: Validar reglas regularmente
7. **Domain experts**: Involucrar en validacion de reglas

## Restricciones

- **Code-level validation**: No valida configuracion externa
- **Python-focused**: Optimizado para Django/Python
- **Heuristic detection**: Puede no detectar todas las violaciones
- **Symbolic execution limited**: Requiere z3 para analisis avanzado
- **State machine**: Requiere definicion explicita

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/business_rules_validator_agent.py`
Tests: `scripts/coding/ai/tests/test_business_rules_validator_agent.py`
Rules: `business_rules.yaml`
Workflows: `workflows/*.yaml`
