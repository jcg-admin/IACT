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
- [`patrones_arquitectonicos.md`](patrones_arquitectonicos.md) ⭐ NUEVO
- [`guia_decision_patrones.md`](guia_decision_patrones.md) ⭐ NUEVO
- [`../../infrastructure/arquitectura/adr/`](../../infrastructure/arquitectura/adr/)

## Información clave
### Rol dentro del flujo de documentación
- **Dependencias y relaciones.** Evalúa el impacto técnico de acuerdos capturados en minutas y requisitos priorizados.
- **Material complementario.** Hospeda diagramas, lineamientos reutilizables y enlaza con los ADR gestionados por Infraestructura.
- **Checklists técnicos.** Garantiza el cumplimiento de estándares antes de liberar diseños y desarrollos.

### Artefactos obligatorios
- Lineamientos de código del backend (`lineamientos_codigo.md`).
- Patrones arquitectónicos (`patrones_arquitectonicos.md`) ⭐ NUEVO.
- Guía de decisión de patrones (`guia_decision_patrones.md`) ⭐ NUEVO.
- ADR vigentes (`../../infrastructure/arquitectura/adr/`).
- Inventario de diagramas y topologías (pendiente, referenciar `../../plantillas/plantilla_sad.md`).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de arquitectura | Sí | Este archivo replica la estructura y metadatos corporativos adaptados al backend. |
| Lineamientos de codificación actualizados | Sí | Documentados en [`lineamientos_codigo.md`](lineamientos_codigo.md). |
| Patrones arquitectónicos documentados | Sí | Documentados en [`patrones_arquitectonicos.md`](patrones_arquitectonicos.md). 6 patrones identificados con ejemplos reales. |
| Guía de decisión de patrones | Sí | Documentada en [`guia_decision_patrones.md`](guia_decision_patrones.md). Decision tree y ejemplos prácticos. |
| Registro de ADR vigente | Parcial | Carpeta [`../../infrastructure/arquitectura/adr/`](../../infrastructure/arquitectura/adr/) gestionada por Infraestructura. |
| Inventario de diagramas/topologías | No | Debe construirse siguiendo la plantilla SAD. |

## Integración con el flujo documental principal
- Recibe restricciones desde [`../../vision_y_alcance/readme.md`](../../vision_y_alcance/readme.md).
- Alinea decisiones con la priorización de [`../requisitos/readme.md`](../requisitos/readme.md).
- Provee insumos a [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md) y coordina despliegues con [`../../infrastructure/devops/readme.md`](../../infrastructure/devops/readme.md).

## Acciones prioritarias
- [ ] WKF-SDLC-130 – Crear repositorio de diagramas _(Pendiente; seguir formato documentado en el flujo)_.
- [x] WKF-SDLC-131 – Documentar arquitectura actual del monolito _(Completado; ver patrones_arquitectonicos.md)_.
- [x] Documentar patrones arquitectónicos existentes _(Completado 2025-11-04; 6 patrones identificados)_.
- [x] Crear guía de decisión de patrones _(Completado 2025-11-04; decision tree y ejemplos)_.
- [ ] WKF-SDLC-132 – Definir criterios de revisión técnica _(Pendiente; coordinar con Gobernanza)_.
