# ClaudeAgent

## Propósito

Orquestar las integraciones con modelos Claude (Anthropic) dentro del flujo SDLC del proyecto. ClaudeAgent sirve como punto de entrada documentado para cualquier actividad que requiera planificación (`.agent/PLANS.md`), generación automática de código o ejecución de flujos Codex MCP respaldados por modelos de Anthropic.

## Integraciones Clave

- **Configuración de credenciales**: `docs/ai/CONFIGURACION_API_KEYS.md` describe cómo declarar `ANTHROPIC_API_KEY` en `.env` y validar la detección automática del proveedor.
- **ExecPlan vivo**: `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` resume la estrategia multi-LLM y mantiene el historial de decisiones para Codex MCP.
- **Catálogo de prompts**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` reúne las técnicas multi-LLM recomendadas antes de diseñar prompts especializados para Claude.
- **Gestión de contexto**: `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` y `scripts/coding/ai/shared/context_sessions.py` definen trimming y summarization compartidos entre proveedores.
- **Agente generador de tests**: `scripts/coding/ai/generators/llm_generator.py` soporta `llm_provider="anthropic"` y usa Claude como backend por defecto.
- **Builder MCP**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` genera briefs single/multi-agent asegurando banderas MCP correctas cuando el proveedor es Anthropic.
- **Guía operativa**: `docs/ai/SDLC_AGENTS_GUIDE.md` contiene los lineamientos de uso y compara el modo LLM vs heurístico.
- **Playbook MCP**: `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` documenta prerequisitos y trazas para todos los proveedores.

## Procedimiento Recomendado

1. **Planifica**: crea o actualiza un ExecPlan siguiendo `.agent/PLANS.md` y enlázalo desde el issue correspondiente.
2. **Configura el entorno**: completa la sección de Anthropic en `.env` y ejecuta `python3 scripts/coding/ai/shared/env_loader.py` para verificar la detección de Claude.
3. **Selecciona el flujo**:
    - Para generación de tests o documentación asistida usa `LLMGenerator` con `llm_provider="anthropic"`.
    - Para flujos MCP ejecuta los briefs construidos con `CodexMCPWorkflowBuilder` usando el proveedor `anthropic`.
4. **Evidencia y seguimiento**: captura resultados en `docs/qa/registros/` y actualiza el ExecPlan (`Progress`, `Decision Log`, `Outcomes`).

## Validación

- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest docs/testing/test_documentation_alignment.py`

ClaudeAgent garantiza que la documentación, la configuración y los flujos automatizados permanezcan alineados cada vez que Claude sea el LLM seleccionado.
