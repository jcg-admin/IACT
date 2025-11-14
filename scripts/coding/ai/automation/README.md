# Automation Agents

Agentes de automatización para validación de calidad, gobernanza y procesos.

## Agentes Implementados

### Governance & Compliance

- **`business_rules_validator_agent.py`** - Valida documentación de reglas de negocio (5 tipos: Hechos, Restricciones, Desencadenadores, Inferencias, Cálculos)
- **`compliance_validator_agent.py`** - Valida especificaciones de tests de compliance (cobertura, estructura Given/When/Then, Clean Code naming)

### Process Automation

- **`pdca_agent.py`** - Automatización de ciclo PDCA (Plan-Do-Check-Act) para mejora continua

## Uso

### Business Rules Validator

```bash
python3 scripts/coding/ai/automation/business_rules_validator_agent.py \
  --docs-dir docs/gobernanza/requisitos/REGLAS_NEGOCIO \
  --output-format json
```

### Compliance Tests Validator

```bash
python3 scripts/coding/ai/automation/compliance_validator_agent.py \
  --spec-file docs/gobernanza/requisitos/REGLAS_NEGOCIO/ESPECIFICACION_TESTS_COMPLIANCE.md \
  --output-format json
```

### PDCA Agent

```python
from scripts.ai.automation.pdca_agent import PDCAAgent

agent = PDCAAgent()
result = agent.run_cycle()
```

## Configuración

Los agentes se configuran en `.constitucion.yaml`:

```yaml
automation_agents:
  business_rules_validator_agent:
    docs_dir: docs/gobernanza/requisitos/REGLAS_NEGOCIO
    check_structure: true
    check_categorization: true
    output_format: json

  compliance_validator_agent:
    spec_file: docs/gobernanza/requisitos/REGLAS_NEGOCIO/ESPECIFICACION_TESTS_COMPLIANCE.md
    check_coverage: true
    check_structure: true
    check_naming: true
    check_levels: true
    output_format: json
```

## Tests

Tests ubicados en `scripts/coding/tests/ai/automation/`:

```bash
pytest scripts/coding/tests/ai/automation/test_compliance_validator_agent.py -v
```
