---
id: DOC-SPACES-INDEX
estado: borrador
propietario: equipo-documentacion
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-ROOT-001", "DOC-VIS-INDEX"]
---
# Índice de espacios documentales

Este árbol replica la jerarquía de espacios publicada en la base documental maestra de IACT. Todas las secciones del proyecto se ubican aquí y conservan metadatos de trazabilidad, responsables y pendientes.

## Convenciones
- Cada carpeta representa un espacio, categoría o página corporativa.
- Las portadas utilizan `readme.md` con front matter en YAML para registrar propietarios y relaciones.
- Los enlaces entre secciones deben ser relativos (`../gobernanza/readme.md`) para que funcionen tanto en GitHub como en MkDocs.

## Navegación principal
- [Visión y alcance](vision_y_alcance/readme.md)
- [Gobernanza](gobernanza/readme.md)
- [Requisitos](requisitos/readme.md)
- [Arquitectura](arquitectura/readme.md)
- [Diseño detallado](diseno_detallado/readme.md)
- [Planificación y releases](planificacion_y_releases/readme.md)
- [Gestión de calidad](qa/estrategia_qa.md)
- [DevOps](devops/readme.md)
- [Anexos](anexos/readme.md)
- [Plantillas](plantillas/readme.md)
- [Checklists](checklists/readme.md)
- [Documentación corporativa](documentacion_corporativa.md)
- [Scientific Computing Projects](scientific_computing_projects/index.md)

## Checklist de alineación
- [ ] Verificar mensualmente que la jerarquía local coincide con la base documental maestra.
- [ ] Registrar diferencias relevantes en `gobernanza/backlog.md` o documento equivalente.
- [ ] Revisar que los enlaces del menú de MkDocs coincidan con esta estructura.

## Uso con MkDocs
La configuración `mkdocs.yml` apunta a este directorio (`docs/spaces`) como `docs_dir`. Cualquier archivo nuevo añadido aquí aparecerá automáticamente en la búsqueda global del sitio generado.
