# Catálogo central de agentes

Este directorio concentra la gobernanza operativa de los agentes autónomos del proyecto. Aquí conviven las guías de ejecución (`PLANS.md`) y el inventario de agentes especializados ubicados en `.agent/agents/`.

## Relación con la documentación oficial
- La guía funcional completa se encuentra en `docs/ai/SDLC_AGENTS_GUIDE.md`, donde se documenta el flujo de trabajo esperado para cada agente y cómo coordinarse con el resto del SDLC.
- Las revisiones consolidadas y lineamientos de documentación están centralizados en `docs/analisis/`, siguiendo lo establecido por el ETA-AGENTE CODEX.

## Relación con los ejecutables
- Los agentes que ejecutan validaciones automáticas viven en `scripts/coding/ai/agents/` (por ejemplo `scripts/coding/ai/agents/documentation/eta_codex_agent.py`).
- Sus pruebas unitarias están en `scripts/coding/tests/ai/agents/`, lo que permite garantizar cobertura mínima del 80 % conforme a nuestra política TDD.

## Cómo usar este directorio
1. **Planifica primero**: para cada refactor o feature relevante crea un ExecPlan según `.agent/PLANS.md`.
2. **Selecciona el agente**: consulta `.agent/agents/README.md` para elegir el agente adecuado o crear uno nuevo.
3. **Documenta y prueba**: enlaza el ExecPlan desde el issue template correspondiente y asegura que los scripts/pruebas mencionados arriba respalden la automatización.

Al mantener este repositorio unificado en `.agent/`, los colaboradores encuentran en un solo lugar la planificación, la documentación de alto nivel y las rutas a los artefactos ejecutables que soportan a cada agente.
