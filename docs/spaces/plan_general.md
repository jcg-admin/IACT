# Plan general de documentación

## Inventario actual

| Ruta | Observaciones |
| --- | --- |
| docs/spaces/vision_y_alcance/glossary.md | Glosario oficial alineado con negocio. |
| docs/spaces/vision_y_alcance/readme.md | Portada estratégica con backlog de visión. |
| docs/spaces/gobernanza/lineamientos_gobernanza.md | Lineamientos vigentes para comités y RACI. |
| docs/spaces/gobernanza/readme.md | Portada de gobernanza y backlog operativo. |
| docs/spaces/requisitos/rq_plantilla.md | Plantilla estándar de requisitos. |
| docs/spaces/requisitos/trazabilidad.md | Registro maestro de trazabilidad. |
| docs/spaces/requisitos/readme.md | Índice funcional y catálogo de pendientes. |
| docs/spaces/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md | ADR publicado con convenciones vigentes. |
| docs/spaces/arquitectura/adr/plantilla_adr.md | Plantilla base para nuevas decisiones. |
| docs/spaces/arquitectura/lineamientos_codigo.md | Guía de estilo para el monolito modular. |
| docs/spaces/arquitectura/readme.md | Índice técnico y backlog arquitectónico. |
| docs/spaces/diseno_detallado/readme.md | Portada de especificaciones por módulo. |
| docs/spaces/planificacion_y_releases/readme.md | Roadmap y calendario de releases. |
| docs/spaces/qa/estrategia_qa.md | Línea base de QA y bitácora de pruebas. |
| docs/spaces/qa/registros/2025_02_16_ejecucion_pytest.md | Registro histórico de ejecución Pytest. |
| docs/spaces/devops/runbooks/post_create.md | Runbook para aprovisionamiento Vagrant. |
| docs/spaces/anexos/catalogo_reglas_negocio.md | Catálogo de reglas de negocio del call center. |
| docs/spaces/plantillas/ | Colección de plantillas reutilizables. |
| docs/spaces/checklists/ | Checklists operativos y de control. |
| docs/spaces/scientific_computing_projects/index.md | Índice del espacio corporativo SCP. |

## Convenciones de nomenclatura
- Directorios en minúsculas con guiones bajos (`vision_y_alcance`, `planificacion_y_releases`).
- Archivos `readme.md` como portadas con front matter en YAML.
- Referencias relativas entre espacios para compatibilidad con GitHub y MkDocs (`../gobernanza/readme.md`).
- Identificadores de tareas con prefijo `WKF-SDLC-XXX` para mantener trazabilidad.

## Estructura objetivo
```text
docs/
└── spaces/
    ├── vision_y_alcance/
    ├── gobernanza/
    ├── requisitos/
    ├── arquitectura/
    ├── diseno_detallado/
    ├── planificacion_y_releases/
    ├── qa/
    ├── devops/
    ├── anexos/
    ├── plantillas/
    ├── checklists/
    └── scientific_computing_projects/
```

## Próximos pasos sugeridos
1. Completar portadas pendientes en `devops/`, `anexos/`, `plantillas/` y `checklists/`.
2. Crear `bitacora.md` en `devops/` para registrar ejecuciones de runbooks.
3. Migrar artefactos adicionales desde repositorios externos manteniendo la convención de enlaces relativos.
4. Revisar mensualmente que la configuración de `mkdocs.yml` refleje esta estructura.

## Integración con MkDocs
- `mkdocs.yml` utiliza `docs/spaces` como `docs_dir` y expone un menú principal con los espacios estratégicos.
- Las nuevas páginas deben añadirse al bloque `nav` para aparecer en la navegación superior.
- Los anexos pueden omitirse del menú principal y seguir siendo accesibles mediante búsqueda.
