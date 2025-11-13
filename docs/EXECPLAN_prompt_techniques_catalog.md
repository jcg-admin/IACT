# Integrar catálogo completo de técnicas de prompts multi-LLM

Este ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo.

Si el archivo PLANS.md está en el repositorio, referencia su ruta: `.agent/PLANS.md`. Este documento debe mantenerse en conformidad con dicha guía.

## Purpose / Big Picture

Unificar el catálogo completo de técnicas de prompting para que los equipos de Backend (API), Frontend (UI), Infrastructure, Docs y Scripts dispongan de una referencia homogénea aplicable a Claude, ChatGPT y Hugging Face. Tras la implementación, cualquier colaborador podrá ubicar las técnicas según el flujo SDLC y vincularlas con los agentes y orquestadores multi-LLM existentes.

## Progress

- [x] (2025-02-14 12:00Z) Redactar prueba de alineación documental que asegure la existencia y el enlace del nuevo catálogo.
- [x] (2025-02-14 12:05Z) Incorporar el catálogo completo de técnicas en `docs/ai_capabilities/prompting/` con referencias cruzadas hacia los agentes por proveedor y dominios.
- [x] (2025-02-14 12:06Z) Actualizar README y guías de agentes para reflejar la nueva fuente canónica.
- [x] (2025-02-14 12:07Z) Ejecutar la batería de pruebas (`pytest docs/testing/test_documentation_alignment.py`).

## Surprises & Discoveries

- No se identificaron descubrimientos imprevistos; la estructura existente de agentes ya contemplaba puntos de enlace.

## Decision Log

- Decision: Centralizar el catálogo en `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` y referenciarlo desde todas las fichas de agentes y guías SDLC.
  Rationale: Evitar duplicación de técnicas y asegurar consistencia multi-LLM para los dominios Backend/UI/Infrastructure/Docs/Scripts.
  Date/Author: 2025-02-14 / Automatización.

## Outcomes & Retrospective

- Catálogo multi-LLM publicado y enlazado desde README, prompting index, agentes por proveedor y por dominio.
- Las pruebas de alineación documental fueron extendidas para proteger la presencia del catálogo y pasaron exitosamente (`pytest docs/testing/test_documentation_alignment.py`).

## Context and Orientation

El repositorio ya contiene guías de prompting específicas (`CODE_GENERATION_GUIDE.md`, `PHI3_PROMPT_ENGINEERING_PLAYBOOK.md`, etc.) y catálogos de agentes en `.agent/agents/`. La política exige que nuevas piezas documentales se integren con los agentes de dominio (ApiAgent, UiAgent, etc.) y con los agentes por proveedor (Claude, ChatGPT, Hugging Face). Las pruebas automáticas de documentación residen en `docs/testing/test_documentation_alignment.py` y deben extenderse para incluir cualquier documento nuevo.

## Plan of Work

1. Extender `docs/testing/test_documentation_alignment.py` para exigir la presencia del catálogo de técnicas de prompting y sus enlaces desde el índice de prompting y desde los agentes pertinentes.
2. Crear `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` incorporando el contenido proporcionado, organizándolo para todos los modelos LLM y añadiendo referencias cruzadas hacia ExecPlans y agentes relevantes.
3. Actualizar `docs/ai_capabilities/prompting/README.md`, `.agent/agents/README.md`, y las fichas de agentes por proveedor para enlazar el nuevo catálogo.
4. Revisar `docs/ai/SDLC_AGENTS_GUIDE.md` y cualquier guía de dominio que requiera citar el catálogo, asegurando consistencia con el mapeo Backend/UI/Infrastructure/Docs/Scripts.
5. Ejecutar pruebas (`pytest docs/testing/test_documentation_alignment.py`) y documentar resultados.

## Concrete Steps

- Trabajar desde la raíz del repositorio (`/workspace/IACT---project`).
- Ejecutar `pytest docs/testing/test_documentation_alignment.py` tras implementar los cambios.
- Si es necesario validar cobertura adicional, reutilizar suites existentes bajo `scripts/coding/tests/`.

## Validation and Acceptance

- `pytest docs/testing/test_documentation_alignment.py` debe pasar y confirmar que el catálogo está enlazado correctamente.
- Los README y fichas de agentes deben contener referencias explícitas al catálogo.
- La documentación debe mencionar que el catálogo es aplicable a Claude, ChatGPT y Hugging Face.

## Idempotence and Recovery

- Las modificaciones son aditivas. Si una prueba falla por enlaces rotos, corregir los paths y reejecutar la suite.
- Para revertir, restaurar los archivos modificados con `git checkout -- <archivo>`.

## Artifacts and Notes

- Se adjuntarán fragmentos relevantes de pruebas exitosas en la sección de resultados.

## Interfaces and Dependencies

- Documentación principal: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` (nuevo).
- Índices y catálogos: `.agent/agents/README.md`, `docs/ai_capabilities/prompting/README.md`, `docs/ai/SDLC_AGENTS_GUIDE.md`.
- Validadores: `docs/testing/test_documentation_alignment.py`.
