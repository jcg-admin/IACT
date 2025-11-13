# Catálogo central de agentes

Este directorio concentra la gobernanza operativa de los agentes autónomos del proyecto. Aquí conviven las guías de ejecución (`PLANS.md`) y el inventario de agentes especializados ubicados en `.agent/agents/`.

## Relación con la documentación oficial
- La guía funcional completa se encuentra en `docs/ai/SDLC_AGENTS_GUIDE.md`, donde se documenta el flujo de trabajo esperado para cada agente y cómo coordinarse con el resto del SDLC.
- Las revisiones consolidadas y lineamientos de documentación están centralizados en `docs/analisis/`, siguiendo lo establecido por el ETA-AGENTE CODEX.
- El ExecPlan maestro para la orquestación multi-LLM es `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`; la evolución del catálogo por dominio se mantiene en `docs/plans/EXECPLAN_agents_domain_alignment.md`.

## Relación con los ejecutables
- Los agentes que ejecutan validaciones automáticas viven en `scripts/coding/ai/agents/` (por ejemplo `scripts/coding/ai/agents/documentation/eta_codex_agent.py`).
- Sus pruebas unitarias están en `scripts/coding/tests/ai/agents/`, lo que permite garantizar cobertura mínima del 80 % conforme a nuestra política TDD.
- Los orquestadores y builders multi-LLM residen en `scripts/coding/ai/orchestrators/` y se verifican con `pytest scripts/coding/tests/ai/orchestrators/`.

## Mapa de dominios y agentes

El proyecto está dividido en cinco dominios operativos. Cada uno cuenta con una ficha de agente dedicada en `.agent/agents/` que explica procedimientos, relaciones con ExecPlans y scripts de soporte.

| Dominio | Directorio raíz | Agente principal | ExecPlans y guías clave |
|---------|-----------------|------------------|-------------------------|
| Backend (API) | `api/` | ApiAgent (`api_agent.md`) | `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/ai/SDLC_AGENTS_GUIDE.md`, `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` |
| Frontend (UI) | `ui/` | UiAgent (`ui_agent.md`) | `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md` |
| Infrastructure | `infrastructure/` | InfrastructureAgent (`infrastructure_agent.md`) | `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/gobernanza/metodologias/agentes_automatizacion.md` |
| Documentación | `docs/` | DocsAgent (`docs_agent.md`) | `docs/analisis/AGENTS.md`, `scripts/coding/ai/agents/documentation/eta_codex_agent.py` |
| Scripts/Automatización | `scripts/` | ScriptsAgent (`scripts_agent.md`) | `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`, `scripts/coding/ai/generators/llm_generator.py` |

Cada agente de dominio describe cómo coordinarse con los agentes por proveedor (Claude, ChatGPT, Hugging Face) y con los agentes operativos (GitOps, Release, Dependency).

## Cómo usar este directorio
1. **Planifica primero**: para cada refactor o feature relevante crea un ExecPlan según `.agent/PLANS.md` y referencia si aplica los planes existentes (`EXECPLAN_codex_mcp_multi_llm.md`, `EXECPLAN_agents_domain_alignment.md`).
2. **Selecciona el agente**: consulta `.agent/agents/README.md` para elegir el agente por proveedor o por dominio adecuado, o para crear uno nuevo siguiendo el estándar.
3. **Documenta y prueba**: enlaza el ExecPlan desde el issue template correspondiente y asegura que los scripts/pruebas mencionados arriba respalden la automatización. Captura resultados en `docs/qa/registros/`.

Al mantener este repositorio unificado en `.agent/`, los colaboradores encuentran en un solo lugar la planificación, la documentación de alto nivel y las rutas a los artefactos ejecutables que soportan a cada agente y dominio del proyecto.
