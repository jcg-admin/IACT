---
id: DOC-ARQ-INDEX
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-REQ-INDEX", "DOC-DIS-INDEX"]
---
# Arquitectura

Agrupa decisiones técnicas, diagramas y lineamientos de código que sostienen el monolito modular. Este espacio conecta acuerdos de negocio con documentación formal como ADR y modelos de despliegue.

## Página padre
- [`../index.md`](../index.md)

## Páginas hijas
- [`lineamientos_codigo.md`](lineamientos_codigo.md)
- [`adr/`](adr/)

## Información clave
### Rol dentro del flujo de documentación
- **Dependencias y relaciones.** Evalúa impacto técnico de acuerdos capturados en minutas y requisitos priorizados.
- **Material complementario.** Hospeda diagramas, ADR y lineamientos reutilizables.
- **Checklists técnicos.** Garantiza el cumplimiento de estándares antes de liberar diseños y desarrollos.

### Artefactos obligatorios
- Lineamientos de código (`lineamientos_codigo.md`).
- ADR vigentes (`adr/`).
- Inventario de diagramas y topologías (pendiente, referenciar `../plantillas/plantilla_sad.md`).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de arquitectura | Sí | Este archivo replica la estructura y metadatos corporativos. |
| Lineamientos de codificación actualizados | Sí | Documentados en [`lineamientos_codigo.md`](lineamientos_codigo.md). |
| Registro de ADR vigente | Sí | Carpeta [`adr/`](adr/) con decisiones documentadas. |
| Inventario de diagramas/topologías | No | Debe construirse siguiendo la plantilla SAD. |

## Integración con el flujo documental principal
- Recibe restricciones desde [`../vision_y_alcance/readme.md`](../vision_y_alcance/readme.md).
- Alinea decisiones con la priorización de [`../requisitos/readme.md`](../requisitos/readme.md).
- Provee insumos a [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md) y [`../devops/readme.md`](../devops/readme.md).

## Acciones prioritarias
- [ ] WKF-SDLC-130 – Crear repositorio de diagramas _(Pendiente; seguir formato documentado en el flujo)_.
- [ ] WKF-SDLC-131 – Documentar arquitectura actual del monolito _(En progreso; basarse en ADR-2025-001)_.
- [ ] WKF-SDLC-132 – Definir criterios de revisión técnica _(Pendiente; coordinar con Gobernanza)_.
