---
id: DOC-REQ-INDEX
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-02-18
relacionados: ["RQ-ANL-000", "DOC-GOB-INDEX", "DOC-ARQ-INDEX"]
---
# Requisitos

Centraliza especificaciones funcionales y no funcionales. Este espacio asegura trazabilidad entre acuerdos operativos, validaciones de QA y decisiones técnicas.

## Rol dentro del flujo de documentación
- **Agenda y discusiones.** Cada requisito nace de acuerdos capturados en minutas y rituales documentados en [`../gobernanza/readme.md`](../gobernanza/readme.md).
- **Seguimiento.** Registra estados, criterios de aceptación y dependencias hacia releases.
- **Material complementario.** Agrupa anexos técnicos, diagramas y referencias cruzadas necesarias para diseño y desarrollo.

## Artefactos obligatorios
- Plantilla de requisitos (`rq_plantilla.md`).
- Registro de trazabilidad (`trazabilidad.md`).
- Backlog priorizado (pendiente, derivado de la plantilla `../plantillas/plantilla_runbook.md`).

## Backlog inmediato
| Identificador | Tarea | Estado | Comentarios |
| --- | --- | --- | --- |
| WKF-SDLC-120 | Catalogar requisitos existentes | Pendiente | Importar desde sesiones documentadas |
| WKF-SDLC-121 | Completar matriz de trazabilidad | En progreso | Conectar con casos de uso y pruebas |
| WKF-SDLC-122 | Registrar requisitos no funcionales críticos | Pendiente | Coordinar con Arquitectura y QA |

## Relaciones
- Depende del contexto establecido en [`../vision_y_alcance/readme.md`](../vision_y_alcance/readme.md).
- Requiere decisiones operativas de [`../gobernanza/readme.md`](../gobernanza/readme.md).
- Entrega criterios de diseño a [`../arquitectura/readme.md`](../arquitectura/readme.md) y [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md).
