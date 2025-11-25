# B4 — Consolidación de casos de uso con trazabilidad completa

## Objetivo
Actualizar los casos de uso con la plantilla `UC_v2.md`, asegurando trazabilidad upward hacia BR/RN/RF y downward hacia UML, API y Tests antes de avanzar a ADRs.

## Alcance
- Reescribir o migrar los UC relevantes usando `UC_v2.md` con campos de actores, precondiciones, flujos y secciones de trazabilidad.
- Incorporar referencias UC↔BR y UC↔ADR según el plan, manteniendo la cadena RN→RF→UC→UML.
- Preparar la matriz UC→UML (`M_UC_UML`) para que la subtarea B4.5 pueda completarla y validarla con `uml-check`.

## Entradas
- Plantilla `UC_v2.md` actualizada (subtarea B2).
- Lineamientos de fase 10.3 y requisitos de regex para commits/PR (`UC-\d+`).

## Salidas esperadas
- Casos de uso normalizados en `docs/trazabilidad/casos_de_uso/` con referencias upward/downward completas.
- Relación inicial UC→UML registrada y sincronizada con RTM-IACT.

## Criterios de done
- Cada UC incluye trazabilidad upward/downward sin campos vacíos y referencias consistentes con RTM-IACT.
- Se documentan riesgos y evidencia mínima, alineados con los controles `lint-trazabilidad` y `uml-check`.
- Los commits y PRs que afectan UC contienen los IDs `UC-XXX` correspondientes.
