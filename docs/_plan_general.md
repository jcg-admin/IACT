# Plan general de documentación

## Inventario actual

| Ruta | Nombre usa guion bajo? | Observaciones |
| --- | --- | --- |
| docs/00-vision-y-alcance/glossary.md | No | Usa guiones medios en la carpeta y nombre simple en inglés. |
| docs/01-gobernanza/lineamientos-gobernanza.md | No | Guiones medios para separar palabras. |
| docs/02-requisitos/rq-plantilla.md | No | Archivo de plantilla con prefijo `rq-`. |
| docs/02-requisitos/trazabilidad.md | No | Nombre en una sola palabra. |
| docs/03-arquitectura/adr/adr-2025-001-vagrant-mod-wsgi.md | No | Convención ADR con guiones medios. |
| docs/03-arquitectura/adr/plantilla-adr.md | No | Plantilla ADR con guiones medios. |
| docs/06-qa/estrategia-qa.md | No | Nombre corto con guiones medios. |
| docs/06-qa/registros/2025-02-16-ejecucion-pytest.md | No | Registra fecha y tema separados por guiones. |
| docs/07-devops/contenedores-devcontainer.md | No | Guiones medios para unir palabras. |
| docs/07-devops/runbooks/github-copilot-codespaces.md | No | Guiones medios en todo el nombre. |
| docs/07-devops/runbooks/post-create.md | No | Nombre compuesto con guion medio. |
| docs/07-devops/runbooks/reprocesar-etl-fallido.md | No | Guiones medios entre términos. |
| docs/07-devops/runbooks/verificar-servicios.md | No | Guiones medios en el nombre. |
| docs/readme.md | No | Archivo principal sin guiones bajos. |

## Archivos que requieren normalización a guion bajo

Todos los archivos listados actualmente utilizan guiones medios. Será necesario definir una convención (por ejemplo, reemplazar `-` por `_`) y planificar los cambios en conjunto con el ajuste de enlaces internos.

## Propuesta de estructura objetivo (15 secciones + anexos)

```text
docs/
├── 00_vision_y_alcance/
├── 01_gobernanza/
├── 02_requisitos/
├── 03_arquitectura/
├── 04_diseno_detallado/
├── 05_planificacion_y_releases/
├── 06_gestion_de_calidad/
├── 07_devops/
├── 08_datos_y_integraciones/
├── 09_seguridad/
├── 10_operacion_y_monitorizacion/
├── 11_soporte_y_mantenimiento/
├── 12_experiencia_de_usuario/
├── 13_gestion_del_cambio/
├── 14_metrica_y_analytics/
├── 15_roadmap_y_vision_futura/
└── anexos/
    ├── plantillas/
    ├── registros/
    └── referencias/
```

## Próximos pasos sugeridos

1. Acordar la convención definitiva de nombres (guion bajo vs. guion medio) y calendarizar la normalización.
2. Reubicar los documentos existentes en la nueva estructura cuando se valide el mapa objetivo.
3. Actualizar enlaces internos y referencias externas tras los cambios de nombre y ubicación.
4. Crear plantillas y lineamientos para cada sección con el fin de facilitar su adopción.
