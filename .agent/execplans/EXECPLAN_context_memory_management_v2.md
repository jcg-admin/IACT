---
title: Integrar gestión de contexto multi-LLM en agentes y documentación
date: 2025-11-13
domain: general
status: active
---

# Integrar gestión de contexto multi-LLM en agentes y documentación

Este ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo.

Este documento se mantiene según `.agent/PLANS.md` y gobierna las integraciones de memoria de contexto para todos los modelos LLM en el repositorio.

## Purpose / Big Picture

Permitir que cualquier agente basado en Claude, ChatGPT u otros LLMs ejecute flujos prolongados sin perder coherencia ni desperdiciar tokens, incorporando sesiones con recorte y resumen de contexto dentro de los scripts y documentando el procedimiento oficial en la guía de capacidades. Al finalizar, los equipos podrán reutilizar la misma política de memoria desde scripts Python probados y seguir un manual unificado dentro de `docs/`.

## Progress

- [x] (2025-11-13 06:54Z) Redactar especificaciones de sesiones de contexto (trimming y summarizing) con API pública en `scripts/coding/ai/shared/`.
- [x] (2025-11-13 06:54Z) Implementar pruebas TDD en `scripts/coding/tests/ai/` que cubran recorte de turnos, resúmenes sintéticos y metadata.
- [x] (2025-11-13 06:54Z) Implementar módulos de sesiones y asegurarse de que las pruebas pasen.
- [x] (2025-11-13 06:57Z) Documentar el cookbook de gestión de contexto en `docs/ai_capabilities/orchestration/` y enlazarlo desde los índices y fichas de agentes.
- [x] (2025-11-13 06:57Z) Actualizar catálogos/README/SDLC para reflejar disponibilidad de la nueva política de contexto.
- [x] (2025-11-13 06:57Z) Ejecutar pytest relevante y actualizar esta sección con el resultado.

## Surprises & Discoveries

- Pending.

## Decision Log

- Pending.

## Outcomes & Retrospective

- Pending.

## Context and Orientation

El proyecto separa responsabilidades en `api/`, `ui/`, `infrastructure/`, `docs/` y `scripts/`. Las automatizaciones de agentes viven en `scripts/coding/ai/` y las guías en `docs/ai_capabilities/`. Actualmente no existe un módulo centralizado que maneje trimming/summarizing con sesiones compatibles con el Agents SDK; el usuario entregó un cookbook detallado que debemos adaptar a nuestras convenciones, manteniendo compatibilidad multi-LLM y con la política de ExecPlans.

## Plan of Work

1. Revisar los lineamientos del cookbook y diseñar la API Python que expondrá clases `TrimmingSession` y `SummarizingSession` bajo `scripts/coding/ai/shared/context_sessions.py`, incluyendo opciones de turnos y resúmenes.
2. Definir antes del código los casos de prueba unitarios que cubran recorte de turnos, preservación de metadatos y reemplazo por resúmenes, ubicándolos en `scripts/coding/tests/ai/shared/test_context_sessions.py`.
3. Implementar las clases siguiendo TDD, asegurando que se integren con `agents` SDK de OpenAI (sin dependencia directa cuando no esté instalado) mediante abstracciones claras.
4. Documentar el flujo completo en un nuevo manual `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md`, incorporando trimming y summarization para todos los modelos, con requisitos previos, comparativas y tablas.
5. Actualizar índices (`docs/ai_capabilities/orchestration/README.md`, `docs/ai_capabilities/prompting/README.md` si aplica) y fichas de agentes multi-LLM en `.agent/agents/` para enlazar el playbook.
6. Ajustar pruebas de alineación documental en `docs/testing/test_documentation_alignment.py` para exigir referencias cruzadas al nuevo playbook.
7. Ejecutar la batería de pruebas relevante (`pytest scripts/coding/tests/ai/shared/test_context_sessions.py` y `pytest docs/testing/test_documentation_alignment.py`) y registrar resultados.

## Concrete Steps

1. Crear archivo de pruebas unitarias con los escenarios TDD descritos.
2. Implementar módulo `context_sessions.py` con clases y helpers necesarios hasta que las pruebas pasen.
3. Redactar el playbook en `docs/ai_capabilities/orchestration/` utilizando el contenido proporcionado por el usuario, adaptado a nuestras convenciones (sin emojis, con secciones claras y referencias multi-LLM).
4. Enlazar el nuevo playbook desde los índices, README y fichas, además de actualizar la prueba de alineación documental.
5. Ejecutar `pytest` para las rutas afectadas.

## Validation and Acceptance

- `pytest scripts/coding/tests/ai/shared/test_context_sessions.py` debe pasar al final.
- `pytest docs/testing/test_documentation_alignment.py` debe pasar y validar los nuevos enlaces.
- El README y las fichas de agentes deben mencionar explícitamente la política de contexto multi-LLM.
- El playbook debe describir trimming y summarization, incluir pros/contras y comparativas, y proveer instrucciones reproducibles.

## Idempotence and Recovery

- Las pruebas unitarias pueden ejecutarse repetidamente sin modificar el entorno.
- El playbook y los enlaces son aditivos; en caso de error, revertir commits parciales y volver a correr `pytest`.

## Artifacts and Notes

- Pending.

## Interfaces and Dependencies

- El módulo `context_sessions` expondrá clases `TrimmingSession` y `SummarizingSession` con métodos `get_items`, `add_items`, `pop_item`, `clear_session`, `get_full_history` y configuraciones `max_turns`, `keep_last_n_turns`.
- Las pruebas importarán desde `scripts.coding.ai.shared.context_sessions` y simularán mensajes en formato dict compatible con Agents SDK (`{"role": "user", "content": "..."}` y metadatos opcionales).
