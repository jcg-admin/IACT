---
name: BasePermissionAgent
description: Clase base para agentes de permisos que gestiona prompts, métricas y logging estructurado.
---

# Permissions Base Agent

`BasePermissionAgent` (`scripts/coding/ai/agents/permissions/base.py`) provee utilidades comunes para agentes de permisos. Gestiona carga de prompts Markdown, logging estructurado, registro de métricas y formato uniforme de resultados.

## Capacidades

- Inicializa agentes con nombre, ruta de prompt y modo verbose.
- Carga prompts desde rutas relativas, validando existencia.
- Registra inicio y fin de ejecución con métricas de duración.
- Expone helpers para loguear métricas (`log_metric`) y violaciones (`log_violation`).
- Formatea resúmenes estandarizados y guarda metadata temporal.

## Entradas y Salidas

- **Entradas**
  - Se configuran al instanciar: `name`, `prompt_path`, `verbose`.
- **Salidas**
  - Métodos auxiliares que retornan cadenas (prompt, resúmenes) o métricas.

## Uso

```python
from scripts.coding.ai.agents.permissions.base import BasePermissionAgent

base_agent = BasePermissionAgent(
    name="custom-permission-check",
    prompt_path="docs/backend/permisos/promptops/custom.md",
    verbose=True
)
prompt = base_agent.load_prompt()
base_agent.start_execution()
# ejecutar lógica propia
base_agent.log_metric("files_analyzed", 42)
base_agent.end_execution()
```

## Validaciones Relacionadas

- Asegurarse de que `prompt_path` exista para evitar `FileNotFoundError`.
- Utilizar como clase base al implementar nuevos gates de permisos (ej. `RouteLintAgent`).
