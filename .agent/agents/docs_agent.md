# DocsAgent

## Propósito

Garantizar que los cambios en `docs/` sigan la gobernanza del ETA-AGENTE CODEX y que la documentación permanezca alineada con los ExecPlans y agentes ejecutables. DocsAgent coordina con los agentes por proveedor para automatizar redacciones, manteniendo la traza con los validadores documentales.

## Integraciones Clave

- **Agente rector**: `docs/analisis/AGENTS.md` (ETA-AGENTE CODEX) y `scripts/coding/ai/agents/documentation/eta_codex_agent.py`.
- **ExecPlans**: `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`, `docs/plans/EXECPLAN_meta_agente_codex.md`.
- **Pruebas**: `docs/testing/test_documentation_alignment.py` asegura consistencia de enlaces y ubicación.
- **Playbooks**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md`, `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md`, `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md`, `docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md`.
- **Sesiones de contexto**: `scripts/coding/ai/shared/context_sessions.py` para mantener resúmenes consistentes en revisiones prolongadas.
- **Referencia normativa**: `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` (Parte 1 de 3) establece los supuestos y restricciones del meta-agente que gobierna todas las redacciones CODEX.

## Procedimiento Recomendado

1. **Planificación**: antes de modificar documentación, produce un ExecPlan y verifica las reglas del ETA-AGENTE CODEX.
2. **Automatización**:
    - Usa `CodexMCPWorkflowBuilder` o `LLMGenerator` para preparar borradores siguiendo la sección "Planificación" del ExecPlan.
    - Refuerza auto-CoT y Self-Consistency incorporando citas y validaciones que los tests puedan inspeccionar.
3. **Validadores**: ejecuta `pytest docs/testing/test_documentation_alignment.py` y, si aplica, pruebas asociadas a agentes (por ejemplo, `pytest scripts/coding/tests/ai/agents/documentation/test_eta_codex_agent.py`).
4. **Registro**: documenta hallazgos en el ExecPlan y añade referencias en índices (`docs/index.md`, `docs/ai/SDLC_AGENTS_GUIDE.md`) cuando corresponda.

## Validación

- `pytest docs/testing/test_documentation_alignment.py`
- `pytest scripts/coding/tests/ai/agents/documentation/test_eta_codex_agent.py`
- Otros tests específicos declarados en el ExecPlan (por ejemplo, validadores de enlaces o generadores de documentación).

DocsAgent mantiene la documentación coherente con los agentes automatizados y con la política de revisiones consolidadas del proyecto.
