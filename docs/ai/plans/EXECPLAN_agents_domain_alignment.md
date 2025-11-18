---
title: Alinear catálogo de agentes con dominios del proyecto
date: 2025-11-13
domain: general
status: active
---

# Alinear catálogo de agentes con dominios del proyecto

Este ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log`, y `Outcomes & Retrospective` deben mantenerse actualizadas conforme avance el trabajo.

Si el archivo PLANS.md está versionado, hace referencia a `.agent/PLANS.md` y se debe respetar íntegramente.

## Purpose / Big Picture

Alinear el catálogo de agentes autónomos con la arquitectura real del proyecto (api, ui, infrastructure, docs y scripts) para que cualquier contribuidor pueda seleccionar rápidamente el agente correcto, comprender sus relaciones con ExecPlans, guías y scripts, y mantener la coherencia entre documentación y automatizaciones multi-LLM.

## Progress

- [x] (2025-11-06 10:00Z) ExecPlan inicial redactado y verificado contra `.agent/PLANS.md`.
- [x] (2025-11-06 11:20Z) Documentación de relaciones dominio ↔ agentes ↔ ExecPlans actualizada.
- [x] (2025-11-06 11:30Z) Nuevos agentes de dominio creados (`api`, `ui`, `infrastructure`, `docs`, `scripts`).
- [x] (2025-11-06 11:40Z) Pruebas y alineadores documentales ajustados para cubrir los nuevos artefactos.
- [x] (2025-11-06 11:55Z) Outcomes & Retrospective actualizado tras validar los cambios.

## Surprises & Discoveries

- Observation: Se requiere que todas las fichas de dominio referencien explícitamente `EXECPLAN_agents_domain_alignment.md` para pasar los nuevos tests.
  Evidence: `test_domain_agents_are_documented_and_linked` valida la cadena de referencias.

## Decision Log

- Decision: Añadir agentes específicos por dominio dentro de `.agent/agents` y mapearlos desde los README principales.
  Rationale: Los colaboradores tenían dificultad para identificar qué agentes y ExecPlans aplicar según la ruta (`api/`, `ui/`, `infrastructure/`, `docs/`, `scripts/`).
  Date/Author: 2025-11-06 / gpt-5-codex

## Outcomes & Retrospective

Las fichas de dominio permiten asociar rápidamente cada directorio (`api/`, `ui/`, `infrastructure/`, `docs/`, `scripts/`) con los ExecPlans y scripts multi-LLM. Los README (`.agent/README.md`, `.agent/agents/README.md`) y la guía `docs/ai/SDLC_AGENTS_GUIDE.md` enlazan los nuevos agentes por nombre. Las suites `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` y `pytest docs/testing/test_documentation_alignment.py` confirman que los vínculos y builders siguen operativos. El nuevo test `test_domain_agents_are_documented_and_linked` protege esta estructura a futuro.

## Context and Orientation

El repositorio está organizado en dominios claros (`api/`, `ui/`, `infrastructure/`, `docs/`, `scripts/`). Actualmente `.agent/agents/README.md` solo cubre agentes por proveedor LLM y algunos operativos (GitOps, Release, Dependency). No existen agentes específicos para los dominios core, lo que genera lagunas para planificar cambios complejos en cada subproyecto. Las guías relevantes incluyen:
- `.agent/PLANS.md`: formato obligatorio para ExecPlans.
- `docs/ai/SDLC_AGENTS_GUIDE.md`: describe el flujo SDLC.
- `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md`: explica orquestaciones multi-LLM.
- `scripts/coding/ai/orchestrators/codex_mcp_workflow.py`: expone builder multi-LLM.

## Plan of Work

1. Extender `.agent/README.md` para reflejar la relación explícita entre los dominios (api, ui, infrastructure, docs, scripts), los ExecPlans y los scripts asociados.
2. Crear nuevos archivos `.agent/agents/api_agent.md`, `ui_agent.md`, `infrastructure_agent.md`, `docs_agent.md` y `scripts_agent.md`, siguiendo el estándar de fichas existentes y referenciando proveedores LLM y pipelines relevantes.
3. Actualizar `.agent/agents/README.md` para incluir una sección "Agentes por dominio" con enlaces a las nuevas fichas y a los directorios del repositorio.
4. Ajustar `docs/ai/SDLC_AGENTS_GUIDE.md` y el ExecPlan `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` para mencionar cómo los agentes de dominio interactúan con los agentes por proveedor y con los orquestadores.
5. Actualizar `docs/testing/test_documentation_alignment.py` para proteger los nuevos vínculos y garantizar que los índices referencien correctamente las fichas de agentes.
6. Ejecutar las suites de pruebas relevantes (`pytest scripts/coding/tests/...` y `pytest docs/testing/test_documentation_alignment.py`).
7. Documentar descubrimientos en `Surprises & Discoveries`, registrar decisiones y concluir con `Outcomes & Retrospective`.

## Concrete Steps

1. Editar `.agent/README.md` y `.agent/agents/README.md` incorporando la matriz de dominios.
2. Generar las fichas de agentes de dominio con secciones estándar (propósito, capacidades, relaciones, ejemplos, validaciones).
3. Modificar `docs/ai/SDLC_AGENTS_GUIDE.md` y `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` para enlazar los nuevos agentes.
4. Ajustar `docs/testing/test_documentation_alignment.py` agregando aserciones para los nuevos archivos.
5. Ejecutar `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` y `pytest docs/testing/test_documentation_alignment.py`.
6. Actualizar las secciones vivas del plan.

## Validation and Acceptance

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` debe pasar sin errores.
- `pytest docs/testing/test_documentation_alignment.py` debe validar los vínculos actualizados.
- Verificar que cada ficha de agente mencione explícitamente sus relaciones con ExecPlans, guías y scripts.
- Confirmar que README y guías referencian todos los dominios y agentes.

## Idempotence and Recovery

- Los cambios en documentación son idempotentes; repetir ediciones sobrescribe contenido sin efectos secundarios.
- Si una prueba falla, revisar el mensaje, ajustar el archivo correspondiente y volver a ejecutar la suite afectada.

## Artifacts and Notes

Pendiente de recopilar ejemplos de salida de pruebas tras la implementación.

## Interfaces and Dependencies

- `.agent/agents/*.md`: nuevas fichas deben seguir el formato documentado en `.agent/agents/README.md`.
- `docs/ai/SDLC_AGENTS_GUIDE.md`: agregar secciones o tablas que relacionen agentes por proveedor y por dominio.
- `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`: incluir referencia cruzada a los agentes de dominio.
- `docs/testing/test_documentation_alignment.py`: expandir validadores para asegurar la existencia de enlaces.
