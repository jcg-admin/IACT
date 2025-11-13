# ApiAgent

## Propósito

Guiar cualquier automatización relacionada con el backend (`api/`) asegurando que la planificación, la selección de LLMs y los scripts de soporte sigan los ExecPlans vigentes. ApiAgent actúa como punto de unión entre los agentes por proveedor y los runbooks de infraestructura de la API.

## Integraciones Clave

- **ExecPlans**: `docs/plans/EXECPLAN_agents_domain_alignment.md` (relación dominio ↔ agentes) y `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` (estrategia multi-LLM).
- **Catálogo de prompts**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` indica qué técnicas aplicar con Claude, ChatGPT u Hugging Face antes de generar especificaciones para la API.
- **Guías SDLC**: `docs/ai/SDLC_AGENTS_GUIDE.md` y `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` para coordinación multi-agente.
- **Scripts**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` (briefs de trabajo) y `scripts/coding/ai/generators/llm_generator.py` (TDD asistido).
- **Config**: variables en `.env` gestionadas por `scripts/coding/ai/shared/env_loader.py` (autodetección de `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`).
- **Infraestructura API**: pipelines documentados en `infrastructure/` y runbooks en `docs/operaciones/`.

## Procedimiento Recomendado

1. **Planificación**: crea o actualiza el ExecPlan del cambio siguiendo `.agent/PLANS.md`. Referencia explícita al agente proveedor (ClaudeAgent, ChatGPTAgent, HuggingFaceAgent) que soportará la implementación.
2. **Selección de LLM**: usa `CodexMCPWorkflowBuilder` para generar briefs ajustados al proveedor elegido y habilita MCP si se requiere colaboración multi-agente.
3. **Desarrollo guiado por TDD**:
    - Genera pruebas con `LLMGenerator` y `pytest` antes de modificar código en `api/`.
    - Ejecuta suites específicas (`pytest api/tests` o equivalentes) tras cada iteración Red→Green→Refactor.
4. **Documentación**: actualiza el ExecPlan (`Progress`, `Decision Log`, `Surprises`) y registra resultados en `docs/qa/registros/`.
5. **Release**: coordina con `GitOpsAgent` o `ReleaseAgent` según corresponda para despliegues y tagging.

## Validación

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest docs/testing/test_documentation_alignment.py`
- Suites de backend (`pytest api/tests` o equivalentes definidos en el ExecPlan específico).

ApiAgent garantiza que cada modificación al backend se ejecute con planificación trazable, soporte multi-LLM y validaciones consistentes con las políticas del repositorio.
