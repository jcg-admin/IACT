# Codex MCP Multi-Agent Workflows

Esta guía consolida los patrones compartidos para ejecutar flujos con Codex CLI como servidor MCP usando los tres proveedores LLM soportados por el proyecto (Claude/Anthropic, ChatGPT/OpenAI y modelos locales Hugging Face). El objetivo es que cualquier colaborador pueda preparar el entorno, configurar agentes y observar sus trazas sin duplicar esfuerzos para cada proveedor.

## 1. Prerrequisitos

- Familiaridad básica con Python o JavaScript.
- Un IDE con soporte para agentes (VS Code, Cursor, JetBrains Gateway).
- Claves de API según el proveedor elegido:
  - `OPENAI_API_KEY` para ChatGPT.
  - `ANTHROPIC_API_KEY` para Claude.
  - `HUGGINGFACEHUB_API_TOKEN` opcional para modelos hospedados en Hugging Face (los checkpoints locales no lo requieren).
- Node.js 18+ para ejecutar `npx codex`.
- Dependencias del SDK:
  ```bash
  pip install openai-agents openai
  ```

### Estructura de `.env`

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=anthropic-...
HUGGINGFACEHUB_API_TOKEN=hf-...
```

Solo es necesario definir la variable correspondiente al proveedor activo.

## 2. Inicializar Codex CLI como servidor MCP

Todos los flujos comparten la misma configuración base del servidor MCP. El módulo `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` expone `CodexMCPWorkflowBuilder`, que entrega esta configuración en forma declarativa.

```python
from scripts.coding.ai.orchestrators import CodexMCPWorkflowBuilder

builder = CodexMCPWorkflowBuilder("openai")  # o "anthropic", "huggingface"
server_cfg = builder.server_config()
```

El builder produce el diccionario:

```python
{
    "command": "npx",
    "args": ["-y", "codex", "mcp"],
    "client_session_timeout_seconds": 360000,
}
```

Este bloque puede pasarse directamente a `MCPServerStdio` del Agents SDK:

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(**server_cfg) as codex_mcp_server:
    ...
```

## 3. Flujos single-agent

El builder genera un brief con dos agentes (`designer` y `developer`) que encapsula el ejemplo de “Implement a fun new game!”.

```python
single_agent = builder.build_single_agent_brief()
```

Elementos destacados:

- `provider` y `model` incluyen los valores por defecto para el proveedor actual (`gpt-4.1`, `claude-3-5-sonnet-20241022`, `TinyLlama/TinyLlama-1.1B-Chat-v1.0`).
- El agente `developer` incorpora las banderas MCP obligatorias: `"approval-policy": "never"` y `"sandbox": "workspace-write"`.
- `required_env` devuelve las variables de entorno necesarias para el proveedor.

Uso básico con el SDK:

```python
from agents import Agent, Runner

brief = builder.build_single_agent_brief()

developer_agent = Agent(
    name=brief["agents"]["developer"]["name"],
    instructions=brief["agents"]["developer"]["instructions"],
    mcp_servers=[codex_mcp_server],
)

designer_agent = Agent(
    name=brief["agents"]["designer"]["name"],
    instructions=brief["agents"]["designer"]["instructions"],
    model=brief["model"],
    handoffs=[developer_agent],
)

await Runner.run(designer_agent, brief["runner"]["task"])
```

## 4. Orquestación multi-agente con gating

Para flujos más largos se utiliza `build_multi_agent_brief()`:

```python
multi_agent = builder.build_multi_agent_brief()
```

Este brief define cinco roles:

- `project_manager`: crea REQUIREMENTS.md, TEST.md y AGENT_TASKS.md, y controla el avance mediante handoffs.
- `designer`: genera `design/design_spec.md` y `wireframe.md`.
- `frontend_developer`: crea `frontend/index.html`, `styles.css` y `game.js`.
- `backend_developer`: prepara `backend/package.json` y `server.js`.
- `tester`: documenta `tests/TEST_PLAN.md` y un script opcional.

Cada agente incluye la política MCP para escritura y devuelve el control al Project Manager. El brief también expone `workflow["gate_checks"]` para validar que los artefactos existen antes de continuar:

```python
for gate in multi_agent["workflow"]["gate_checks"]:
    assert Path(gate["artifact"]).exists()
```

El Project Manager implementa el gating mediante strings como `transfer_to_designer_agent`, `transfer_to_frontend_developer_agent`, etc., replicando la coreografía descrita en la guía original.

### Task list incorporado

`workflow["task"]` contiene un backlog textual que los agentes pueden usar como referencia (objetivo “Bug Busters”, endpoints del backend, restricciones de simplicidad, etc.).

## 5. Observabilidad con Traces

El brief multi-agente activa observabilidad por defecto:

```python
multi_agent["tracing"] == {
    "enabled": True,
    "notes": "Enable OpenAI Traces (or Anthropic/Hugging Face equivalents) ..."
}
```

Cada proveedor maneja sus trazas:

| Proveedor | Herramienta sugerida | Notas |
|-----------|----------------------|-------|
| OpenAI    | [OpenAI Traces](https://platform.openai.com/docs/guides/reports/traces) | Visualiza prompts, herramientas y transferencias. |
| Anthropic | Panel de sesiones Claude | Registrar `client_session_timeout_seconds` amplio para ejecuciones largas. |
| Hugging Face | Logging local + `hf` callbacks | Útil cuando se ejecutan checkpoints locales sin telemetría externa. |

## 6. Relación con `.agent`

- El catálogo `.agent/agents/README.md` documenta el **Codex MCP Workflow Orchestrator** y enlaza a esta guía.
- Los issues de tipo feature deben adjuntar el ExecPlan relevante (`docs/plans/EXECPLAN_codex_mcp_multi_llm.md`) para mantener la trazabilidad.
- Las plantillas de bug report/custom issues reenvían al catálogo de agentes para seleccionar quién ejecutará el flujo MCP.

## 7. Validación automática

`CodexMCPWorkflowBuilder` cuenta con pruebas en `scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` que cubren:

- Presencia de banderas MCP en el brief single-agent.
- Declaración de variables de entorno por proveedor.
- Gatekeeping de artefactos y activación de trazas en el brief multi-agente.

Ejecuta las pruebas con:

```bash
pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py
```

## 8. Checklist rápido

1. Configura `.env` con la API key del proveedor.
2. Instala `openai-agents` y `openai` en tu entorno de trabajo.
3. Inicializa `MCPServerStdio` usando `builder.server_config()`.
4. Obtén el brief single o multi-agente según el alcance.
5. Verifica que los artefactos de `gate_checks` existan antes de continuar con el siguiente handoff.
6. Revisa las trazas para depurar comportamientos y retroalimentar el ExecPlan.

Con esta guía, los flujos Codex MCP quedan normalizados para todos los modelos LLM soportados, alineando documentación, agentes y pruebas automatizadas.
