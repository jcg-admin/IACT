---
id: DOC-REQ-INDEX
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-02-17
relacionados: ["RQ-ANL-000", "DOC-GOB-INDEX", "DOC-ARQ-INDEX"]
---
# 02 · Requisitos

Centraliza especificaciones funcionales y no funcionales. Vincula el flujo de actividades con la definición de alcance,
asegurando trazabilidad hacia pruebas y arquitectura.

## Rol dentro del flujo de documentación
- **Paso 5. Agenda y discusiones.** Cada requisito se origina en acuerdos documentados en minutas.
- **Paso 8. Seguimiento.** Evolución de requisitos, estados y criterios de aceptación quedan rastreados aquí.
- **Paso 9. Material complementario.** Incluye adjuntos técnicos, diagramas y referencias cruzadas.

## Artefactos obligatorios
- Plantilla de requisitos (`rq_plantilla.md`).
- Registro de trazabilidad (`trazabilidad.md`).
- Backlog de requisitos priorizados (pendiente, derivado de la plantilla `plantilla_runbook.md` o un tablero externo).

## Backlog inmediato
| Identificador | Tarea | Estado | Comentarios |
| --- | --- | --- | --- |
| WKF-SDLC-120 | Catalogar requisitos existentes | Pendiente | Importar desde sesiones documentadas con la nueva plantilla |
| WKF-SDLC-121 | Completar matriz de trazabilidad | En progreso | Conectar con casos de uso y pruebas |
| WKF-SDLC-122 | Registrar requisitos no funcionales críticos | Pendiente | Coordinar con Arquitectura y QA |

## Relaciones
- Depende del contexto establecido en `docs/00_vision_y_alcance/readme.md`.
- Requiere decisiones operativas de `docs/01_gobernanza/readme.md`.
- Entrega criterios de diseño a `docs/03_arquitectura/readme.md` y `docs/04_diseno_detallado/readme.md`.
