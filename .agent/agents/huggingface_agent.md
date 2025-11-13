# HuggingFaceAgent

## Propósito

Guiar el uso de modelos Hugging Face (locales o alojados) dentro de los pipelines del proyecto. HuggingFaceAgent cubre desde la configuración de modelos fine-tuned (p. ej. TinyLlama) hasta su participación en los flujos Codex MCP y generación de pruebas.

## Integraciones Clave

- **Configuración de entorno**: `docs/ai/CONFIGURACION_API_KEYS.md` detalla cómo definir rutas locales (`HF_LOCAL_MODEL_PATH`) o `HF_MODEL_ID` y cuándo se requiere `HUGGINGFACEHUB_API_TOKEN`.
- **ExecPlan vivo**: `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` mantiene la estrategia para balancear los tres proveedores y debe reflejar cualquier cambio en modelos Hugging Face.
- **Agente generador de tests**: `scripts/coding/ai/generators/llm_generator.py` soporta `llm_provider="huggingface"` y permite reutilizar modelos QLoRA o checkpoints locales.
- **Builder MCP**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` expone defaults y banderas MCP al usar el proveedor `huggingface`.
- **Guías de capacidad**:
    - `docs/ai/SDLC_AGENTS_GUIDE.md` explica cuándo preferir modos locales vs nube.
    - `docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md` y `docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md` muestran patrones de prompting reutilizables.
    - `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` unifica el procedimiento multi-agente.

## Procedimiento Recomendado

1. **Planificación**: crea o actualiza un ExecPlan conforme a `.agent/PLANS.md` antes de preparar experimentos o migraciones con modelos Hugging Face.
2. **Configuración de modelo**:
    - Ajusta `.env` con rutas locales o `HF_MODEL_ID` según `docs/ai/CONFIGURACION_API_KEYS.md`.
    - Si se utilizarán pesos fine-tuned, documenta su origen en el ExecPlan.
3. **Ejecución**:
    - Usa `LLMGenerator` con `llm_provider="huggingface"` para generación de tests o snippets.
    - Emplea `CodexMCPWorkflowBuilder` indicando el proveedor `huggingface` para validar flujos multi-agente.
4. **Registro**: captura resultados en `docs/qa/registros/` y mantén actualizado el `Decision Log` del ExecPlan con hallazgos de performance.

## Validación

- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest docs/testing/test_documentation_alignment.py`

HuggingFaceAgent facilita que los equipos adopten modelos locales manteniendo coherencia con la planificación y las herramientas compartidas del repositorio.
