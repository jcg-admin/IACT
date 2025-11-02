---
id: DOC-DEVOPS-BACKEND
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-DEVOPS-INFRA", "DOC-ARQ-BACKEND"]
---
# DevOps del backend

Procedimientos operativos específicos del backend que complementan los runbooks de Infraestructura. Aquí se documentan tareas recurrentes que afectan a servicios y jobs del monolito Python.

## Página padre
- [`../readme.md`](../readme.md)

## Páginas hijas
- [`runbooks/`](runbooks/)

## Información clave
### Artefactos disponibles
- Runbook de recuperación [`reprocesar_etl_fallido.md`](runbooks/reprocesar_etl_fallido.md).

### Integraciones operativas
- Coordina ventanas de intervención con [`../../infrastructure/planificacion_y_releases/readme.md`](../../infrastructure/planificacion_y_releases/readme.md).
- Requiere lineamientos de despliegue publicados en [`../../infrastructure/devops/readme.md`](../../infrastructure/devops/readme.md).
- Reporta métricas de ejecución a [`../checklists/checklist_testing.md`](../checklists/checklist_testing.md) para garantizar trazabilidad.

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio DevOps del backend | Sí | Este archivo documenta el alcance y las dependencias clave con Infraestructura. |
| Runbooks del backend | Parcial | [`runbooks/reprocesar_etl_fallido.md`](runbooks/reprocesar_etl_fallido.md) describe el proceso principal; faltan otros jobs críticos. |
| Bitácora de intervenciones | No | Debe generarse `runbooks/bitacora.md` para registrar ejecuciones manuales. |

## Acciones prioritarias
- [ ] Crear runbooks adicionales para los servicios de reporting y colas de tareas.
- [ ] Integrar alertas y métricas con el tablero de releases.
- [ ] Coordinar la automatización del reinicio del scheduler con Infraestructura.
