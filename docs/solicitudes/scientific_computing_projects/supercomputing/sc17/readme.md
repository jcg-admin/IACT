---
id: SCP-SC17-INDEX
estado: borrador
propietario: coordinacion-sc17
ultima_actualizacion: 2025-02-18
relacionados: ["SCP-SUPER-INDEX", "DOC-SPACES-INDEX", "DOC-GOB-INDEX"]
---
# SC17 · Denver, CO

Replica la página principal `SC17` definida en la base documental maestra de IACT. Permite verificar que la documentación local mantiene la misma estructura, enlaces y solicitudes de información asociadas a la iniciativa.

## Página padre
- [`../readme.md`](../readme.md)

## Páginas hijas
- [`meeting_and_discussion_notes/readme.md`](meeting_and_discussion_notes/readme.md)
- [`sc17_documents/readme.md`](sc17_documents/readme.md)
- [`sc17_task_report/readme.md`](sc17_task_report/readme.md)

## Información destacada
- **Sede:** [Denver Convention Center](http://denverconvention.com)
- **Fechas de conferencia:** 12-17 noviembre 2017
- **Fechas de exhibición:** 13-16 noviembre 2017
- **Guía de archivos:** pendiente de incorporarse como anexo local (`../../../planificacion_y_releases/readme.md`).

## Alineación con la base documental maestra
| Elemento de la página SC17 | Representación local | Estado |
| --- | --- | --- |
| Encabezado con breadcrumbs (`Home > Supercomputing > SC17`) | Se refleja mediante la jerarquía de directorios `spaces/scientific_computing_projects/supercomputing/sc17`. | Cumplido |
| Sección de enlaces (SC17 Documents, Meeting Notes, Task Report) | Directorios dedicados con `readme.md` y listas de pendientes. | Cumplido |
| Enlaces externos (sitio oficial, fechas, floor plan) | Referenciados en la sección **Información destacada** y **Recursos**. | Cumplido |
| Solicitudes de información (`<--- input request`) | Convertidas en elementos pendientes dentro de las páginas hijas. | Cumplido |

## Recursos
- [SC17 Conference Home Page](http://sc17.supercomputing.org)
- [Important Deadlines and Dates](http://sc17.supercomputing.org/attendees/important-deadlines/)
- [Convention Center Floor plan](http://iebms.heiexpo.com/sc/SC17Floorplan.pdf)

## Integración con el flujo documental principal
- Los acuerdos y minutas registrados en `meeting_and_discussion_notes` alimentan las secciones de gobernanza (`../../../gobernanza/readme.md`).
- Los artefactos publicados en `sc17_documents` sirven como anexos dentro de `../../../planificacion_y_releases/readme.md`.
- El seguimiento operativo consignado en `sc17_task_report` complementa los tableros de calidad y DevOps (`../../../qa/estrategia_qa.md`, `../../../devops/runbooks/`).

## Checklist de verificación
- [ ] Revisar mensualmente que los enlaces externos continúan vigentes.
- [ ] Confirmar que los child pages locales están sincronizados con la base documental maestra antes de cada entrega.
- [ ] Registrar nuevos action items usando `../../../plantillas/plantilla_registro_actividad.md` y vincularlos en las secciones correspondientes.
