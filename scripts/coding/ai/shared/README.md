# Shared Components

Componentes compartidos entre todos los agentes.

## Módulos

- `agent_base.py` - Clase base para todos los agentes (Agent, AgentResult, AgentStatus, Pipeline)
- `constitution_loader.py` - Carga de constitutions para agentes
- `pr_creator.py` - Creación de Pull Requests
- `test_runner.py` - Ejecución de tests

## Uso

```python
from scripts.ai.shared.agent_base import Agent, AgentResult, AgentStatus

class MyAgent(Agent):
    def run(self, input_data):
        # implementación
        return AgentResult(status=AgentStatus.SUCCESS, data=result)
```
