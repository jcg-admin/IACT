# Registro de decisiones de documentación

## 2025-02-17 - Normalización de nombres
- Se reemplazaron guiones medios por guiones bajos en directorios y archivos dentro de `docs/`.
- Se actualizaron enlaces internos en los principales documentos.
- Se habilitaron plantillas y checklists en carpetas dedicadas.

## 2025-02-18 - Consolidación en `docs/spaces`
- Se trasladó toda la documentación principal a `docs/spaces/` eliminando la numeración heredada.
- Se añadieron portadas (`readme.md`) para DevOps, anexos, plantillas y checklists.
- Se creó la configuración `mkdocs.yml` utilizando `docs/spaces` como `docs_dir`.

## 2025-02-19 - Unificación en `docs/`
- Se removió el nivel intermedio `spaces/` para simplificar la navegación y alinear la estructura con la base maestra.
- Se actualizaron enlaces relativos y metadatos (`relacionados`) para reflejar el nuevo identificador `DOC-INDEX-GENERAL`.
- Se ajustó `mkdocs.yml` para utilizar `docs/` como `docs_dir`.

## Próximos pasos
- Revisar nuevas contribuciones para validar que respetan la convención.
- Completar anexos con ejemplos reales a medida que estén disponibles.
- Registrar futuras decisiones en este mismo archivo para mantener trazabilidad.
