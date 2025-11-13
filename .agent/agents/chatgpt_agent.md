# ChatGPTAgent

## Propósito

Centralizar el uso de modelos ChatGPT/OpenAI dentro de los flujos de automatización del repositorio. ChatGPTAgent documenta los prerequisitos operativos y la relación entre planificación, scripts y guías cuando el proveedor seleccionado es OpenAI.

## Integraciones Clave

- **Configuración de credenciales**: `docs/ai/CONFIGURACION_API_KEYS.md` incluye los pasos para definir `OPENAI_API_KEY` y habilitar modos híbridos.
- **ExecPlan vivo**: `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` mantiene la estrategia multi-LLM y debe actualizarse cuando cambien las capacidades o defaults de OpenAI.
- **Catálogo de prompts**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` consolida las técnicas multi-LLM antes de personalizar prompts para ChatGPT.
- **Agente generador de tests**: `scripts/coding/ai/generators/llm_generator.py` soporta `llm_provider="openai"` para generar pruebas o documentación asistida con ChatGPT.
- **Builder MCP**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` emite briefs con banderas MCP y modelos recomendados (por ejemplo `gpt-5`) para OpenAI.
- **Guía operativa**: `docs/ai/SDLC_AGENTS_GUIDE.md` detalla cuándo alternar entre modos heurísticos y LLM.
- **Playbook MCP**: `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` explica la ejecución multi-agente para todos los proveedores, incluido OpenAI.

## Procedimiento Recomendado

1. **Planificación**: genera o actualiza el ExecPlan conforme a `.agent/PLANS.md` y registra en el issue qué agente ejecutará el trabajo.
2. **Preparación de entorno**: configura `OPENAI_API_KEY` en `.env` y verifica la auto-detección con `python3 scripts/coding/ai/shared/env_loader.py`.
3. **Ejecución**:
    - Usa `LLMGenerator` para generación de tests con `llm_provider="openai"`.
    - Para Codex MCP, alimenta los briefs de `CodexMCPWorkflowBuilder` indicando el proveedor `openai`.
4. **Gobernanza**: documenta resultados en `docs/qa/registros/` y sincroniza `Progress`, `Decision Log` y `Surprises` en el ExecPlan.

## Validación

- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest docs/testing/test_documentation_alignment.py`

ChatGPTAgent evita configuraciones inconsistentes al mantener alineados credenciales, planificación y herramientas cuando ChatGPT es el LLM elegido.
