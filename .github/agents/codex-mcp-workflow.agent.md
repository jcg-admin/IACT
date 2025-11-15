# CodexMCPWorkflow Orchestrator

## Propósito

Establecer una interfaz declarativa para generar briefs de agentes basados en Codex MCP que funcionen de forma homogénea con Claude (Anthropic), ChatGPT (OpenAI) y modelos compatibles de Hugging Face.

## Componentes Clave

- **Builder Python**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py`
  - `server_config()` produce la configuración estándar del servidor MCP (`npx -y codex mcp`).
  - `build_single_agent_brief()` genera el escenario "Implement a fun new game!" listo para ejecutar.
  - `build_multi_agent_brief()` construye la coreografía Project Manager → Designer → Frontend/Backend → Tester con gating y trazas activadas.
- **Guía operativa**: `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md`
  - Detalla prerequisitos, variables de entorno y cómo conectar el builder con el Agents SDK.
  - Documenta el uso de Traces según proveedor y los artefactos esperados (`design/design_spec.md`, `frontend/index.html`, etc.).
- **ExecPlan asociado**: `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` (mantener actualizado durante implementaciones).

## Cuándo Invocarlo

- Se requiere ejecutar flujos agenticos Codex que deben funcionar con más de un proveedor LLM.
- Se necesita demostrar trazabilidad (Traces) y gating de artefactos antes de promover handoffs automáticos.
- Se desea generar documentación reproducible (briefs + guía) para nuevas integraciones basadas en MCP.

## Entradas

- Proveedor (`openai`, `anthropic`, `huggingface`).
- Modelo opcional (si no se usa el default del builder).

## Salidas

- Diccionarios Python listos para usarse en scripts async (`server`, `agents`, `workflow`, `tracing`).
- Briefs que pueden serializarse a JSON/YAML para ejecutar en pipelines externos.

## Validación

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest docs/testing/test_documentation_alignment.py`

Mantén esta ficha sincronizada con la guía y el ExecPlan cuando se añadan nuevos proveedores o roles.
