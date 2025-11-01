---
id: DOC-REQ-INDEX
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-02-18
relacionados: ["RQ-ANL-000", "DOC-GOB-INDEX", "DOC-ARQ-INDEX"]
---
# Requisitos

Centraliza especificaciones funcionales y no funcionales. Este espacio asegura trazabilidad entre acuerdos operativos, validaciones de QA y decisiones técnicas.

## Página padre
- [`../index.md`](../index.md)

## Páginas hijas
- [`rq_plantilla.md`](rq_plantilla.md)
- [`trazabilidad.md`](trazabilidad.md)

## Información clave
### Rol dentro del flujo de documentación
- **Agenda y discusiones.** Cada requisito nace de acuerdos capturados en minutas y rituales documentados en [`../gobernanza/readme.md`](../gobernanza/readme.md).
- **Seguimiento.** Registra estados, criterios de aceptación y dependencias hacia releases.
- **Material complementario.** Agrupa anexos técnicos, diagramas y referencias cruzadas necesarias para diseño y desarrollo.

### Artefactos obligatorios
- Plantilla de requisitos (`rq_plantilla.md`).
- Registro de trazabilidad (`trazabilidad.md`).
- Backlog priorizado (pendiente, derivado de la plantilla `../plantillas/plantilla_runbook.md`).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de requisitos | Sí | Este archivo replica metadatos y navegación del espacio corporativo. |
| Plantilla de levantamiento de requisitos | Sí | Disponible en [`rq_plantilla.md`](rq_plantilla.md). |
| Matriz de trazabilidad vigente | Sí | Documentada en [`trazabilidad.md`](trazabilidad.md). |
| Backlog priorizado con estado | No | Debe construirse a partir de los acuerdos más recientes. |

## Integración con el flujo documental principal
- Depende del contexto establecido en [`../vision_y_alcance/readme.md`](../vision_y_alcance/readme.md).
- Requiere decisiones operativas de [`../gobernanza/readme.md`](../gobernanza/readme.md).
- Entrega criterios de diseño a [`../arquitectura/readme.md`](../arquitectura/readme.md) y [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md).

## Acciones prioritarias
- [ ] WKF-SDLC-120 – Catalogar requisitos existentes _(Pendiente; importar desde sesiones documentadas)_.
- [ ] WKF-SDLC-121 – Completar matriz de trazabilidad _(En progreso; conectar con casos de uso y pruebas)_.
- [ ] WKF-SDLC-122 – Registrar requisitos no funcionales críticos _(Pendiente; coordinar con Arquitectura y QA)_.
