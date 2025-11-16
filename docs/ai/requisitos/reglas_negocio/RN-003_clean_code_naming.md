# Regla de Negocio: Clean Code Naming

## Metadatos
- Codigo: RN-003
- Tipo: Restriccion
- Fuente: Clean Code Principles, GUIA_ESTILO.md
- Estado: Aprobado
- Fecha: 2025-11-16
- Owner: tech-lead

## Descripcion

El sistema DEBE generar nombres de archivos siguiendo las convenciones de Clean Code Naming del proyecto. Esto asegura consistencia, legibilidad y facilita busqueda/indexacion.

### Principios de Naming

1. **NO emojis**: Prohibido usar emojis en nombres de archivos (⛔, ❌, ✅, 📊, etc.)
2. **NO iconos**: Prohibido usar caracteres especiales decorativos
3. **snake_case**: Usar snake_case para separar palabras (no CamelCase, kebab-case)
4. **Descriptivo**: Nombres deben ser auto-explicativos
5. **Prefijos standar**: Usar prefijos estandarizados por tipo

### Formatos por Tipo de Artefacto

#### Tareas y Decisiones
- **task**: `TASK-{NNN}-{descripcion_underscores}.md`
  - Ejemplo: `TASK-001-implementar_placement_agent.md`
- **adr**: `ADR-{NNN}-{titulo_underscores}.md`
  - Ejemplo: `ADR-010-arquitectura_por_dominios.md`
- **solicitud**: `REQ-{NNN}-{descripcion_underscores}.md`
  - Ejemplo: `REQ-042-nuevo_endpoint_busqueda.md`

#### Analisis y Reportes
- **analisis**: `ANALISIS_{TEMA_UPPERCASE}_{YYYYMMDD}.md`
  - Ejemplo: `ANALISIS_DOCS_ESTRUCTURA_20251116.md`
- **reporte_limpieza**: `CLEANUP_REPORT_{YYYYMMDD}.md`
  - Ejemplo: `CLEANUP_REPORT_20251116.md`
- **sesion**: `SESSION_{TEMA_UPPERCASE}_{YYYY_MM_DD}.md`
  - Ejemplo: `SESSION_PLANNING_2025_11_16.md`

#### Documentacion
- **documentacion_agente**: `README_{AGENT_NAME_UPPERCASE}.md`
  - Ejemplo: `README_PLACEMENT_AGENT.md`
- **guia**: `GUIA_{TEMA_UPPERCASE}.md`
  - Ejemplo: `GUIA_UBICACIONES_ARTEFACTOS.md`
- **procedimiento**: `PROC-{NNN}-{nombre_underscores}.md`
  - Ejemplo: `PROC-001-deploy_produccion.md`

#### Configuracion y Scripts
- **configuracion_agente**: `{agent_name}_config.json`
  - Ejemplo: `placement_agent_config.json`
- **script**: `{accion}_{objeto}.{ext}`
  - Ejemplo: `backup_database.sh`, `migrate_docs.py`

#### Indices y Plantillas
- **indice**: `INDEX.md` (siempre este nombre exacto)
- **plantilla**: `template_{tipo}.md` o `plantilla_{tipo}.md`
  - Ejemplo: `template_requisito_funcional.md`

### Algoritmo de Normalizacion

Para normalizar una descripcion/titulo a formato valido:

```python
def normalizar_descripcion(desc: str) -> str:
    # 1. Eliminar emojis y caracteres especiales
    desc = re.sub(r'[^\w\s-]', '', desc)

    # 2. Convertir a lowercase
    desc = desc.lower()

    # 3. Reemplazar espacios y guiones por underscores
    desc = desc.replace(' ', '_').replace('-', '_')

    # 4. Eliminar underscores multiples
    desc = re.sub(r'_+', '_', desc)

    # 5. Eliminar underscores al inicio/fin
    desc = desc.strip('_')

    return desc
```

**Ejemplos de transformacion:**
- `"Análisis de Docs 📊"` → `"analisis_de_docs"`
- `"TASK: Fix Bug 🐛"` → `"task_fix_bug"`
- `"Guía---Testing"` → `"guia_testing"`

### Extension de Archivos

- Documentos: `.md` (Markdown)
- Configuraciones: `.json`, `.yaml`, `.yml`
- Scripts: `.py`, `.sh`, `.js`
- Diagramas: `.mermaid`, `.puml`, `.svg`

## Impacto en Requisitos

- **RF-004**: Generar nombre estandarizado segun tipo
- **RN-001**: Clasificacion de tipos determina formato de nombre
- **RNF-002**: Precision en generacion de nombres (100% conformidad)

## Evidencia

- Cleanup reciente (nov 2025): elimino emojis de 47 archivos
- GUIA_ESTILO.md: prohibicion explicita de emojis
- Best practices de Clean Code: nombres descriptivos, sin decoracion

## Observaciones

- **Compatibilidad**: Nombres generados deben ser compatibles con todos OS (Linux, macOS, Windows)
- **Longitud**: Nombres no deben exceder 255 caracteres (limite filesystem)
- **Unicidad**: Si archivo ya existe, agregar sufijo `_v2`, `_v3`, etc.
- **Acentos**: Se permiten acentos en descripciones (UTF-8), pero se normalizan a ASCII en algunos casos
