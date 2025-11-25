# B4.5 — Implementación del artefacto y matriz UML

## Objetivo
Crear el artefacto `UML_Model.md` y la matriz `M_UC_UML` que aseguran la trazabilidad UC→UML antes de iniciar los ADRs.

## Alcance
- Definir la estructura de `docs/trazabilidad/modelos/UML_Model.md` y los diagramas requeridos para los UC priorizados.
- Construir la matriz UC→UML (`M_UC_UML`) alineada con RTM-IACT, documentando cualquier hueco con `PENDING`.
- Preparar o actualizar el validador `uml-check` para que falle cuando falte el artefacto o existan relaciones incompletas.

## Entradas
- Casos de uso normalizados (subtarea B4) y plantillas v2 vigentes.
- Reglas de completitud por fase 10.4 del plan.

## Salidas esperadas
- Archivo `docs/trazabilidad/modelos/UML_Model.md` publicado con las vistas UML acordadas.
- Matriz `M_UC_UML` integrada con RTM-IACT y lista para ser consumida por CI/CD.
- Documentación breve del comportamiento esperado de `uml-check` y de los criterios de bloqueo.

## Criterios de done
- Todos los UC prioritarios cuentan con su relación UC→UML documentada.
- `uml-check` identifica ausencia de artefacto o relaciones y está listo para integrarse a CI/CD.
- Las referencias UC y UML se reflejan en RTM-IACT sin inconsistencias.
