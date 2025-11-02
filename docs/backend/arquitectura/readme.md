---
id: DOC-ARQ-BACKEND
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-REQ-INDEX", "DOC-DIS-BACKEND"]
---
# Arquitectura del backend

Agrupa decisiones técnicas, diagramas y lineamientos de código que sostienen el monolito modular del backend. Este espacio conecta
los acuerdos de negocio con documentación formal como ADR, modelos de despliegue y convenciones de desarrollo.

## Página padre
- [`../readme.md`](../readme.md)

## Páginas hijas
- [`lineamientos_codigo.md`](lineamientos_codigo.md)
- [`../../infrastructure/arquitectura/adr/`](../../infrastructure/arquitectura/adr/)

## Información clave
### Rol dentro del flujo de documentación
- **Dependencias y relaciones.** Evalúa el impacto técnico de acuerdos capturados en minutas y requisitos priorizados.
- **Material complementario.** Hospeda diagramas, lineamientos reutilizables y enlaza con los ADR gestionados por Infraestructura.
- **Checklists técnicos.** Garantiza el cumplimiento de estándares antes de liberar diseños y desarrollos.

### Artefactos obligatorios
- Lineamientos de código del backend (`lineamientos_codigo.md`).
- ADR vigentes (`../../infrastructure/arquitectura/adr/`).
- Inventario de diagramas y topologías (pendiente, referenciar `../../plantillas/plantilla_sad.md`).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de arquitectura | Sí | Este archivo replica la estructura y metadatos corporativos adaptados al backend. |
| Lineamientos de codificación actualizados | Sí | Documentados en [`lineamientos_codigo.md`](lineamientos_codigo.md). |
| Registro de ADR vigente | Parcial | Carpeta [`../../infrastructure/arquitectura/adr/`](../../infrastructure/arquitectura/adr/) gestionada por Infraestructura. |
| Inventario de diagramas/topologías | No | Debe construirse siguiendo la plantilla SAD. |

## Integración con el flujo documental principal
- Recibe restricciones desde [`../../gerencia/vision_y_alcance/readme.md`](../../gerencia/vision_y_alcance/readme.md).
- Alinea decisiones con la priorización de [`../requisitos/readme.md`](../requisitos/readme.md).
- Provee insumos a [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md) y coordina despliegues con [`../../infrastructure/devops/readme.md`](../../infrastructure/devops/readme.md).

## Acciones prioritarias
- [ ] WKF-SDLC-130 – Crear repositorio de diagramas _(Pendiente; seguir formato documentado en el flujo)_.
- [ ] WKF-SDLC-131 – Documentar arquitectura actual del monolito _(En progreso; basarse en ADR-2025-001)_.
- [ ] WKF-SDLC-132 – Definir criterios de revisión técnica _(Pendiente; coordinar con Gobernanza)_.
