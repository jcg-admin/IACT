# Integrar el META-AGENTE CODEX en la documentación oficial

Este ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo.

Este documento se mantiene según `.agent/PLANS.md` y regula la incorporación del META-AGENTE CODEX dentro de `docs/analisis/`, su enlace con los catálogos de agentes y las pruebas de gobernanza.

## Purpose / Big Picture

Incorporar el documento normativo "META-AGENTE CODEX" (parte 1 de 3) dentro del árbol oficial de análisis, asegurando que la gobernanza del repositorio conozca la nueva especificación, que los índices y catálogos de agentes lo referencien y que la batería de pruebas de alineación lo vigile. Al finalizar, cualquier colaborador podrá localizar el meta-agente y entender cómo se relaciona con los agentes existentes y los dominios del proyecto.

## Progress

- [x] (2025-11-13 08:15Z) Redactar e integrar el documento del META-AGENTE CODEX en `docs/analisis/` siguiendo las pautas del ETA-AGENTE.
- [x] (2025-11-13 08:25Z) Actualizar índices y catálogos (`docs/index.md`, `.agent/agents/README.md`, fichas relevantes) para reflejar el nuevo meta-agente.
- [x] (2025-11-13 08:40Z) Ajustar las pruebas de alineación documental en `docs/testing/test_documentation_alignment.py` para exigir referencias al nuevo documento.
- [x] (2025-11-13 08:55Z) Ejecutar las pruebas relacionadas y registrar resultados.

## Surprises & Discoveries

- Pending.

## Decision Log

- Pending.

## Outcomes & Retrospective

- Pending.

## Context and Orientation

El repositorio separa contenido en `api/`, `ui/`, `infrastructure/`, `docs/` y `scripts/`. Toda revisión consolidada debe vivir en `docs/analisis/` y cumplir con las directrices del ETA-AGENTE CODEX. El usuario entregó la Parte 1 del documento "META-AGENTE CODEX" y espera que se integre para todos los modelos LLM, manteniendo coherencia con los catálogos de agentes y la gobernanza existente.

## Plan of Work

1. Revisar el contenido proporcionado por el usuario y adaptarlo a la convención de `docs/analisis/` (sin emojis, secciones claras, referencias internas cuando proceda).
2. Crear el archivo en `docs/analisis/` con título, versión y estructura preservada, asegurando vínculos a los procesos ya descritos en `docs/plans/` y `.agent/` cuando corresponda.
3. Actualizar los índices y catálogos (`docs/index.md`, `.agent/agents/README.md`, fichas de agentes por proveedor o dominio) para enlazar el nuevo documento.
4. Extender `docs/testing/test_documentation_alignment.py` para verificar la existencia de los enlaces y la ubicación correcta del meta-agente.
5. Ejecutar `pytest docs/testing/test_documentation_alignment.py` y documentar el resultado.

## Concrete Steps

1. Crear `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` con el contenido adaptado proporcionado por el usuario.
2. Añadir referencias al nuevo documento en los índices y catálogos relevantes.
3. Modificar `docs/testing/test_documentation_alignment.py` para cubrir el nuevo enlace.
4. Ejecutar `pytest docs/testing/test_documentation_alignment.py`.

## Validation and Acceptance

- `pytest docs/testing/test_documentation_alignment.py` debe pasar.
- `docs/index.md` y `.agent/agents/README.md` deben incluir enlaces claros al META-AGENTE CODEX.
- El archivo en `docs/analisis/` debe cumplir los lineamientos del ETA-AGENTE CODEX y mencionar su relación con los agentes existentes.

## Idempotence and Recovery

Los cambios son aditivos sobre archivos de texto. Si alguna prueba falla, revertir el archivo afectado con `git checkout -- <archivo>` y rehacer el ajuste. No se ejecutan migraciones ni scripts destructivos.

## Artifacts and Notes

Se anexarán los enlaces actualizados y, de ser necesario, fragmentos relevantes dentro del commit final.

## Interfaces and Dependencies

- Documentos: `docs/analisis/AGENTS.md`, `docs/index.md`, `.agent/agents/README.md`.
- Pruebas: `docs/testing/test_documentation_alignment.py`.
- No se modifican scripts de automatización ni código ejecutable.
