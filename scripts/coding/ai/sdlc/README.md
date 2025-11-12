# SDLC Agents

Agentes especializados para cada fase del Software Development Life Cycle.

## Agentes

- `base_agent.py` - Clase base común para todos los agentes SDLC
- `planner_agent.py` - Planning: Convierte feature requests en issues completos
- `feasibility_agent.py` - Feasibility: Analiza viabilidad técnica y riesgos
- `design_agent.py` - Design: Genera documentación de diseño
- `testing_agent.py` - Testing: Crea estrategia y plan de testing
- `deployment_agent.py` - Deployment: Planifica deployment y rollback
- `orchestrator.py` - Orquesta todo el pipeline SDLC
- `dora_integration.py` - Integración con métricas DORA

## Uso

```python
from scripts.ai.sdlc.planner_agent import PlannerAgent

agent = PlannerAgent()
result = agent.run({"feature_request": "Implementar autenticación 2FA"})
```

## Documentación

Ver `scripts/ai/agents/README_SDLC_AGENTS.md` para documentación completa.
