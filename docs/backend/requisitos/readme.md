---
<<<<<<< HEAD
id: DOC-REQ-BACKEND
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-REQ-INDEX", "DOC-ARQ-BACKEND", "ADR-2025-001"]
---
# Requisitos del backend

Extiende la visión corporativa descrita en [`../../requisitos/readme.md`](../../requisitos/readme.md) con acuerdos específicos para servicios, integraciones y contratos públicos del backend.
=======
id: DOC-REQ-INDEX
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-02-18
relacionados: ["RQ-ANL-000", "DOC-GOB-INDEX", "DOC-ARQ-BACKEND"]
---
# Requisitos

Centraliza especificaciones funcionales y no funcionales. Este espacio asegura trazabilidad entre acuerdos operativos, validaciones de QA y decisiones técnicas.
>>>>>>> origin/docs

## Página padre
- [`../readme.md`](../readme.md)

<<<<<<< HEAD
## Relación con otros espacios
- Arquitectura técnica: [`../arquitectura/readme.md`](../arquitectura/readme.md)
- Diseño detallado: [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md)
- Gobernanza operativa: [`../../infrastructure/gobernanza/readme.md`](../../infrastructure/gobernanza/readme.md)

## Alcance
- **Servicios expuestos.** Requisitos sobre endpoints REST, eventos y tareas batch.
- **Integraciones internas.** Dependencias con módulos compartidos y orquestadores.
- **Restricciones no funcionales.** SLAs, observabilidad y políticas de seguridad aplicables al backend.

## Artefactos reutilizados
- Plantilla corporativa: [`../../requisitos/rq_plantilla.md`](../../requisitos/rq_plantilla.md)
- Matriz de trazabilidad global: [`../../requisitos/trazabilidad.md`](../../requisitos/trazabilidad.md)
- Registro de releases: [`../../infrastructure/planificacion_y_releases/readme.md`](../../infrastructure/planificacion_y_releases/readme.md)

## Próximos pasos
- [ ] Definir catálogo de requisitos pendientes del backend priorizado por valor de negocio.
- [ ] Mapear requisitos no funcionales críticos (latencia, observabilidad, resiliencia).
- [ ] Alinear dependencias con QA para asegurar cobertura de pruebas automatizadas.
=======
## Páginas hijas
- [`rq_plantilla.md`](rq_plantilla.md)
- [`trazabilidad.md`](trazabilidad.md)

## Información clave
### Rol dentro del flujo de documentación
- **Agenda y discusiones.** Cada requisito nace de acuerdos capturados en minutas y rituales documentados en [`../../infrastructure/gobernanza/readme.md`](../../infrastructure/gobernanza/readme.md).
- **Seguimiento.** Registra estados, criterios de aceptación y dependencias hacia releases.
- **Material complementario.** Agrupa anexos técnicos, diagramas y referencias cruzadas necesarias para diseño y desarrollo.

### Artefactos obligatorios
- Plantilla de requisitos (`rq_plantilla.md`).
- Registro de trazabilidad (`trazabilidad.md`).
- Backlog priorizado (pendiente, derivado de la plantilla `../../plantillas/plantilla_runbook.md`).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de requisitos | Sí | Este archivo replica metadatos y navegación del espacio corporativo. |
| Plantilla de levantamiento de requisitos | Sí | Disponible en [`rq_plantilla.md`](rq_plantilla.md). |
| Matriz de trazabilidad vigente | Sí | Documentada en [`trazabilidad.md`](trazabilidad.md). |
| Backlog priorizado con estado | No | Debe construirse a partir de los acuerdos más recientes. |

## Integración con el flujo documental principal
- Depende del contexto establecido en [`../../gerencia/vision_y_alcance/readme.md`](../../gerencia/vision_y_alcance/readme.md).
- Requiere decisiones operativas de [`../../infrastructure/gobernanza/readme.md`](../../infrastructure/gobernanza/readme.md).
- Entrega criterios de diseño a [`../arquitectura/readme.md`](../arquitectura/readme.md) y [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md).

## Acciones prioritarias
- [ ] WKF-SDLC-120 – Catalogar requisitos existentes _(Pendiente; importar desde sesiones documentadas)_.
- [ ] WKF-SDLC-121 – Completar matriz de trazabilidad _(En progreso; conectar con casos de uso y pruebas)_.
- [ ] WKF-SDLC-122 – Registrar requisitos no funcionales críticos _(Pendiente; coordinar con Arquitectura y QA)_.
>>>>>>> origin/docs
