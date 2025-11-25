# B2 — Actualización de plantillas v2 con campos de trazabilidad

## Objetivo
Actualizar y publicar las plantillas v2 (BR, UC, ADR, TEST, GOB) asegurando que incluyen los campos `trazabilidad_upward` y `trazabilidad_downward` requeridos por el plan.

## Alcance
- Revisar y ajustar `BR_v2.md`, `UC_v2.md`, `ADR_v2.md`, `TEST_v2.md` y `GOB_v2.md` con los campos obligatorios.
- Incorporar en las plantillas las relaciones RN/RF/BR hacia UC y, en sentido descendente, UML/API/Código/Tests/Evidencia según aplique.
- Documentar en cada plantilla los riesgos y evidencia mínima, alineando el contenido con la cadena RN→RF→UC→UML.

## Entradas
- Requerimientos de la sección 5.2 del plan para contenidos mínimos de plantillas v2.
- Reglas de regex y metadatos mencionadas para PRs (`UC-\d+`, `ADR-\d+`).

## Salidas esperadas
- Plantillas v2 actualizadas en `docs/trazabilidad/plantillas/` (o ruta equivalente) con trazabilidad bidireccional explícita.
- Notas de uso para desarrolladores y QA indicando los campos que bloquean CI/CD.

## Criterios de done
- Cada plantilla define campos upward/downward completos y ejemplos mínimos.
- Las referencias de trazabilidad coinciden con RTM-IACT y con los controles `lint-trazabilidad` y `uml-check`.
- Se mantienen las convenciones de IDs (`UC-XXX`, `ADR-XXX`, `TEST-XXX`) y se documenta su uso en PRs.
