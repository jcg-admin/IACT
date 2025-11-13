# ExecPlan: Integrar la presentación "Hamilton Framework" siguiendo las 6 fases SDLC IA

Esta ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo. Se rige por las pautas de `.agent/PLANS.md`.

## Purpose / Big Picture

Queremos incorporar a la base documental del proyecto un entregable que traduzca la presentación "Hamilton Framework - Presentación Completa" al contexto del repositorio, utilizando el marco de 6 fases del SDLC IA descrito en `docs/gobernanza/ai/FASES_IMPLEMENTACION_IA.md`. El resultado permitirá que cualquier integrante acceda a un plan aplicable para adoptar Hamilton dentro del flujo de agentes SDLC. El cambio debe incluir trazabilidad mediante pruebas automáticas que garanticen la existencia del documento y su indexación.

## Progress

- [x] (2025-11-18 12:00Z) ExecPlan creado, contexto inicial documentado.
- [x] (2025-11-18 12:15Z) Pruebas añadidas para exigir la guía Hamilton y su enlace en el índice.
- [x] (2025-11-18 13:00Z) Documento `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` creado con secciones por fase y referencias SDLC.
- [x] (2025-11-18 13:20Z) Índices y guías (`docs/index.md`, `docs/ai/SDLC_AGENTS_GUIDE.md`) enlazados al nuevo material.
- [x] (2025-11-18 13:40Z) Ejecutado `pytest` sobre la prueba nueva (`test_hamilton_framework_integration_doc_is_published`); se documentan fallos heredados de la suite completa.

## Surprises & Discoveries

- Observación: Pytest fija `rootdir` en `docs/`; para validar el nuevo recurso se añadió la constante `PROJECT_ROOT` en la suite y así apuntar al repositorio completo al verificar la guía Hamilton.
- Observación: La ejecución completa de `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` sigue fallando por ausencias heredadas (guías en rutas legacy). Se dejó constancia y se ejecutó la prueba puntual asociada al nuevo documento.

## Decision Log

- Decision: Ubicar el nuevo documento dentro de `docs/gobernanza/ai/` para mantenerlo junto a las guías de gobierno IA y las fases SDLC.
  Rationale: El contenido complementa `FASES_IMPLEMENTACION_IA.md` y refuerza la gobernanza de agentes SDLC.
  Date/Author: 2025-11-18 / Coding Agent.
- Decision: Declarar `PROJECT_ROOT` en la suite de documentación para referenciar rutas del repositorio al comprobar la guía Hamilton.
  Rationale: Evita modificar el comportamiento histórico del resto de validaciones y permite apuntar al nuevo documento dentro de `docs/gobernanza/ai/`.
  Date/Author: 2025-11-18 / Coding Agent.

## Outcomes & Retrospective

- Se incorporó la guía Hamilton dentro de `docs/gobernanza/ai/` con trazabilidad hacia las seis fases del SDLC IA y los agentes documentados.
- La suite de documentación ahora protege la existencia del recurso mediante `test_hamilton_framework_integration_doc_is_published` (ejecución individual en pytest superada).
- Queda como seguimiento abordar las fallas heredadas de la suite completa de documentación, registradas en esta ExecPlan.

## Context and Orientation

El repositorio exige que cambios significativos sigan un ExecPlan (`AGENTS.md`). Las guías de agentes SDLC viven en `docs/ai/SDLC_AGENTS_GUIDE.md`. El marco de 6 fases está documentado en `docs/gobernanza/ai/FASES_IMPLEMENTACION_IA.md`. Actualmente no existe documentación específica sobre Hamilton (`rg "Hamilton"` no devuelve resultados). Las pruebas de alineación documental residen en `docs/qa/testing/test_documentation_alignment.py` y cubren la presencia de documentos clave, por lo que ampliaremos esta suite.

## Plan of Work

1. Añadir una prueba en `docs/qa/testing/test_documentation_alignment.py` que verifique la existencia del nuevo archivo `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` y que el índice principal `docs/index.md` contenga su referencia. Esto debe hacerse antes de crear el documento para cumplir TDD.
2. Redactar `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` describiendo cómo aplicar Hamilton en cada una de las seis fases. El documento debe incluir:
   - Resumen ejecutivo vinculado a la presentación proporcionada.
   - Secciones por fase (Evaluación, Estrategia, Fundamentos, Despliegue, Medición, Escalamiento) con acciones concretas, roles, métricas y uso del agente SDLC.
   - Referencias internas a recursos existentes (por ejemplo, `docs/ai/SDLC_AGENTS_GUIDE.md`, scripts, pruebas) para mantener la gobernanza.
   - Requisitos de pruebas o validaciones que permitan demostrar adopción controlada.
3. Actualizar `docs/index.md` en la sección correspondiente (probablemente "[PLANIFICADO] Visión futura" o "[DOCS] Documentación activa") para listar el nuevo documento con el estado adecuado. Validar si es necesario actualizar otras guías (por ejemplo, `docs/ai/SDLC_AGENTS_GUIDE.md`) con una mención explícita al nuevo recurso.
4. Revisar si es necesario registrar decisiones adicionales (por ejemplo, si se agregan enlaces cruzados) y documentarlas en el `Decision Log`.
5. Ejecutar `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` para confirmar que la prueba añadida pasa y que no se introducen regresiones.
6. Completar la sección `Outcomes & Retrospective` con el resumen del trabajo y actualizar `Progress` marcando cada hito.

## Concrete Steps

- Working directory: `/workspace/IACT---project`.
- Comandos previstos:
  - `python3 -m pytest docs/qa/testing/test_documentation_alignment.py`
  - Ediciones en archivos especificados usando el editor disponible (`cat <<'EOF' > file`, `sed -i`, etc.).

## Validation and Acceptance

El cambio se considera exitoso cuando:
- La prueba añadida en `docs/qa/testing/test_documentation_alignment.py` pasa y falla antes de crear el documento.
- `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` existe, contiene la estructura por fases y referencias internas solicitadas.
- `docs/index.md` enlaza al nuevo documento.
- La prueba `test_hamilton_framework_integration_doc_is_published` pasa en pytest; los fallos heredados del resto de la suite se documentan para seguimiento.

## Idempotence and Recovery

La modificación de documentos y pruebas es aditiva. Si la prueba falla después de crear el documento, revisar rutas y enlaces. Los cambios pueden revertirse mediante `git checkout -- <archivo>` en caso de errores.

## Artifacts and Notes

Se anexarán fragmentos relevantes (por ejemplo, resultados de pytest) en las actualizaciones futuras del plan si aportan evidencia.

## Interfaces and Dependencies

- Documentación base: `docs/gobernanza/ai/FASES_IMPLEMENTACION_IA.md`, `docs/ai/SDLC_AGENTS_GUIDE.md`.
- Pruebas: `docs/qa/testing/test_documentation_alignment.py` (suite de documentación).
- No se introducen dependencias externas; el contenido es documental.
