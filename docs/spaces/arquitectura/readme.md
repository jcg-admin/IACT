---
id: DOC-ARQ-INDEX
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-REQ-INDEX", "DOC-DIS-INDEX"]
---
# Arquitectura

Agrupa decisiones técnicas, diagramas y lineamientos de código que sostienen el monolito modular. Este espacio conecta acuerdos de negocio con documentación formal como ADR y modelos de despliegue.

## Rol dentro del flujo de documentación
- **Dependencias y relaciones.** Evalúa impacto técnico de acuerdos capturados en minutas y requisitos priorizados.
- **Material complementario.** Hospeda diagramas, ADR y lineamientos reutilizables.
- **Checklists técnicos.** Garantiza el cumplimiento de estándares antes de liberar diseños y desarrollos.

## Artefactos obligatorios
- Lineamientos de código (`lineamientos_codigo.md`).
- ADR vigentes (`adr/`).
- Inventario de diagramas y topologías (pendiente, referenciar `../plantillas/plantilla_sad.md`).

## Backlog inmediato
| Identificador | Tarea | Estado | Comentarios |
| --- | --- | --- | --- |
| WKF-SDLC-130 | Crear repositorio de diagramas | Pendiente | Seguir formato documentado en el flujo |
| WKF-SDLC-131 | Documentar arquitectura actual del monolito | En progreso | Basarse en ADR-2025-001 |
| WKF-SDLC-132 | Definir criterios de revisión técnica | Pendiente | Coordinar con Gobernanza |

## Relaciones
- Recibe restricciones desde [`../vision_y_alcance/readme.md`](../vision_y_alcance/readme.md).
- Alinea decisiones con la priorización de [`../requisitos/readme.md`](../requisitos/readme.md).
- Provee insumos a [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md) y [`../devops/runbooks`](../devops/runbooks).
