---
id: DOC-PLANTILLAS-INDEX
estado: borrador
propietario: equipo-documentacion
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-INDEX-GENERAL", "DOC-REQ-INDEX"]
---
# Plantillas

Colección de formatos reutilizables para discovery, análisis, diseño, QA y operación. Las plantillas se mantienen en Markdown para facilitar su adaptación.

## Página padre
- [`../index.md`](../index.md)

## Páginas hijas
- [`plantilla_project_charter.md`](plantilla_project_charter.md)
- [`plantilla_business_case.md`](plantilla_business_case.md)
- [`plantilla_srs.md`](plantilla_srs.md)
- [`plantilla_sad.md`](plantilla_sad.md)
- [`plantilla_plan_pruebas.md`](plantilla_plan_pruebas.md)
- [`plantilla_runbook.md`](plantilla_runbook.md)
- [`plantilla_espacio_documental.md`](plantilla_espacio_documental.md)

## Información clave
### Uso recomendado
1. Clonar el archivo correspondiente y registrar la relación en el front matter del nuevo documento.
2. Actualizar campos resaltados con `TODO` o comentarios antes de compartir el artefacto.
3. Notificar cambios relevantes en [`../gobernanza/readme.md`](../gobernanza/readme.md) para asegurar que todos los equipos utilicen la versión vigente.

### Categorías destacadas
- **Producto y alcance:** `plantilla_project_charter.md`, `plantilla_business_case.md`.
- **Requisitos y análisis:** `plantilla_srs.md`, `plantilla_regla_negocio.md`, `plantilla_caso_de_uso.md`.
- **Diseño y arquitectura:** `plantilla_sad.md`, `plantilla_database_design.md`, `plantilla_api_reference.md`.
- **QA y soporte:** `plantilla_plan_pruebas.md`, `plantilla_caso_prueba.md`, `plantilla_runbook.md`.
- **Documentación corporativa:** `plantilla_espacio_documental.md` para replicar portadas y jerarquías alineadas con la base maestra.

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de plantillas | Sí | Este archivo replica metadatos y navegación requeridos. |
| Plantillas de discovery y negocio | Sí | Incluyen Project Charter y Business Case. |
| Plantillas de ingeniería y QA | Sí | Están disponibles las guías de SRS, SAD, plan de pruebas y runbooks. |
| Plantilla para espacios documentales | Sí | Documentada en [`plantilla_espacio_documental.md`](plantilla_espacio_documental.md). |
| Registro de versiones y owners | No | Falta crear un inventario que detalle responsables y fecha de vigencia. |

## Acciones prioritarias
- [ ] Elaborar inventario maestro de plantillas con responsables y fechas de revisión.
- [ ] Automatizar la verificación de enlaces rotos dentro de las plantillas.
- [ ] Coordinar con Gobernanza la publicación de la guía de adopción de plantillas en rituales oficiales.
