---
id: DOC-ARQ-INDEX
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-17
relacionados: ["ADR-2025-001", "DOC-REQ-INDEX", "DOC-DIS-INDEX"]
---
# 03 · Arquitectura

Agrupa decisiones técnicas, diagramas y lineamientos de código para sostener el monolito modular. Conecta los acuerdos del
pipeline con documentación formal como ADR y modelos de despliegue.

## Rol dentro del pipeline
- **Paso 6. Dependencias y relaciones.** Evalúa impacto técnico de acuerdos capturados en minutas.
- **Paso 9. Material complementario.** Hospeda diagramas, ADR y lineamientos reutilizables.
- **Paso 10. Checklists y convenciones.** Garantiza que cada decisión arquitectónica cumpla con estándares.

## Artefactos obligatorios
- Lineamientos de código (`lineamientos_codigo.md`).
- ADR vigentes (`adr/`).
- Inventario de diagramas y topologías (pendiente, referenciar `docs/plantillas/plantilla_sad.md`).

## Backlog inmediato
| Identificador | Tarea | Estado | Comentarios |
| --- | --- | --- | --- |
| WKF-SDLC-130 | Crear repositorio de diagramas | Pendiente | Usar formato descrito en pipeline paso 9 |
| WKF-SDLC-131 | Documentar arquitectura actual del monolito | En progreso | Basarse en ADR-2025-001 |
| WKF-SDLC-132 | Definir criterios de revisión técnica para minutas | Pendiente | Coordinar con Gobernanza |

## Relaciones
- Recibe restricciones desde `docs/00_vision_y_alcance/readme.md`.
- Alinea decisiones con priorización de `docs/02_requisitos/readme.md`.
- Provee insumos a `docs/04_diseno_detallado/readme.md` y `docs/07_devops`.
