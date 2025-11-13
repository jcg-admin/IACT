# ScriptsAgent

## Propósito

Orquestar cambios en `scripts/` garantizando que las automatizaciones, generadores y validadores permanezcan sincronizados con los ExecPlans multi-LLM y con las pruebas de regresión. ScriptsAgent sirve como guía para extender herramientas CLI, validadores y pipelines internos.

## Integraciones Clave

- **ExecPlans**: `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`.
- **Normativa CODEX**:
  - `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` detalla los requisitos de razonamiento y evidencia que deben cumplir los scripts generadores de artefactos.
  - `docs/analisis/META_AGENTE_CODEX_PARTE_2.md` documenta el pipeline de producción, la entrada requerida y la estructura de salida que deben implementar los scripts automatizados.
- **Catálogo de prompts**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` para seleccionar estrategias multi-LLM antes de automatizar generadores o validadores.
- **Memoria de contexto**: `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` y `scripts/coding/ai/shared/context_sessions.py` habilitan sesiones compartidas en herramientas que atienden hilos extensos.
- **Código**: `scripts/coding/ai/` (generators, orchestrators, shared utilities) y `scripts/tests/`.
- **Pruebas**: `pytest scripts/coding/tests/...` y `pytest scripts/tests/...`.
- **Documentación**: `docs/scripts/README.md`, `docs/scripts/SCRIPTS_MATRIX.md` y `docs/operaciones/verificar_servicios.md`.

## Procedimiento Recomendado

1. **Planificación**: identifica en el ExecPlan qué scripts serán modificados/creados, qué agentes los consumirán y qué cobertura de pruebas se requiere.
2. **Implementación TDD**:
    - Redacta pruebas en `scripts/coding/tests/...` antes de modificar los scripts correspondientes.
    - Usa `LLMGenerator` cuando se necesiten esbozos iniciales, siempre asegurando iteraciones Red→Green→Refactor.
3. **Orquestación multi-LLM**: utiliza `CodexMCPWorkflowBuilder` para generar briefs que coordinen agentes y aseguren políticas MCP (`approval-policy`, `sandbox`).
4. **Documentación**: registra nuevas utilidades en `docs/scripts/README.md` y en la matriz de scripts. Actualiza ExecPlan y `docs/qa/registros/` con resultados de pruebas.

## Validación

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- `pytest scripts/coding/tests/ai/generators/test_llm_generator.py`
- `pytest docs/testing/test_documentation_alignment.py`
- Otras suites específicas (`pytest scripts/tests/test_*.py`, `bash scripts/tests/...`).

ScriptsAgent asegura que la carpeta `scripts/` evolucione con disciplina TDD, manteniendo alineada la automatización interna con los agentes y ExecPlans vigentes.
