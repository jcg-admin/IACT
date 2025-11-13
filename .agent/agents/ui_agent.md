# UiAgent

## Propósito

Alinear el trabajo automatizado sobre el frontend (`ui/`) con las prácticas de diseño, pruebas y despliegue descritas en nuestros ExecPlans y guías de prompting. UiAgent sirve como guía única para combinar planificación, generación asistida de código y validaciones de experiencia de usuario.

## Integraciones Clave

- **ExecPlans**: `docs/plans/EXECPLAN_agents_domain_alignment.md` y `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`.
- **Normativa CODEX**:
  - `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` guía las entregas formales que involucren documentación o especificaciones del frontend.
  - `docs/analisis/META_AGENTE_CODEX_PARTE_2.md` detalla el pipeline y la estructura que debe seguir cualquier artefacto CODEX aplicado a la UI.
- **Playbooks**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md`, `docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md`, `docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md` y `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` (memoria de contexto compartida con backend/infrastructure).
- **Sesiones de contexto**: `scripts/coding/ai/shared/context_sessions.py` para trimming/summarization cuando los flujos UX requieren iteraciones largas.
- **Orquestación**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` (multi-agente) y `scripts/coding/ai/generators/llm_generator.py` (generación guiada por TDD).
- **Documentación UX**: briefs y wireframes creados por el Designer Agent se ubican en `docs/` o `design/` según el ExecPlan activo.

## Procedimiento Recomendado

1. **Planificación**: crea ExecPlan conforme a `.agent/PLANS.md` identificando componentes UI afectados y experimentos a realizar (por ejemplo, wireframes asistidos por LLM).
2. **Diseño + Desarrollo**:
    - Coordina con Designer Agent para obtener `design_spec.md` y wireframes.
    - Usa `CodexMCPWorkflowBuilder` con `llm_provider` correspondiente para producir briefs que generen HTML/CSS/JS siguiendo las especificaciones.
    - Aplica TDD generando pruebas end-to-end o unitarias con `LLMGenerator` si procede.
3. **Pruebas visuales**: registra capturas o instrucciones en `docs/qa/registros/` y, si el cambio es visual, adjunta evidencia conforme a la política de screenshots.
4. **Documentación**: actualiza ExecPlan (`Progress`, `Decision Log`) y enlaza resultados desde `docs/ai/SDLC_AGENTS_GUIDE.md` si se introduce un nuevo patrón.

## Validación

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest docs/testing/test_documentation_alignment.py`
- Suites front-end (`npm test`, `pnpm vitest`, etc.) según el stack declarado en el ExecPlan.

UiAgent permite mantener el frontend consistente con las guías de diseño, asegurando que la colaboración multi-LLM se refleje en entregables reproducibles y probados.
