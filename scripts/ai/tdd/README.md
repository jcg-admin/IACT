# TDD Feature Agent System

Sistema completo de Test-Driven Development con garantías de calidad y compliance automatizado.

## Módulos

- `constitution.py` - 8 reglas inmutables de cumplimiento TDD (4 CRITICAL, 2 HIGH, 2 MEDIUM)
- `execution_logger.py` - Audit trail completo con SHA256 hashes y reportes JSON/Markdown
- `feature_agent.py` - Agente principal que ejecuta ciclo RED-GREEN-REFACTOR
- `metrics_dashboard.py` - Dashboards visuales con badges shields.io

## Proceso TDD

1. **RED**: Genera tests unitarios que deben fallar
2. **GREEN**: Implementa código para pasar tests
3. **REFACTOR**: Optimiza código manteniendo tests verdes
4. **VALIDATION**: Valida 8 reglas de constitution
5. **REPORTING**: Genera reportes y dashboards

## Uso

```python
from scripts.ai.tdd.feature_agent import TDDFeatureAgent

agent = TDDFeatureAgent()
result = agent.run({
    "issue_title": "User Authentication",
    "acceptance_criteria": [...],
    "technical_requirements": [...]
})
```

## Tests Incluidos

- `tests/ai/agents/test_tdd_constitution.py` (30 tests)
- `tests/ai/agents/test_execution_logger.py` (37 tests)

Todos los tests pasan (67/67) ✅
