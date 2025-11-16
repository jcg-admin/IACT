# Regla de Negocio: Frontmatter YAML con Trazabilidad

## Metadatos
- Codigo: RN-004
- Tipo: Restriccion
- Fuente: ISO/IEC/IEEE 29148:2018, BABOK v3, mejores practicas trazabilidad
- Estado: Aprobado
- Fecha: 2025-11-16
- Owner: equipo-ba

## Descripcion

El sistema DEBE generar frontmatter YAML al inicio de cada artefacto Markdown, conteniendo metadatos estructurados que faciliten trazabilidad, busqueda y gestion documental.

### Campos Obligatorios Base (Todos los Tipos)

```yaml
---
fecha: YYYY-MM-DD           # Fecha de creacion
tipo: {tipo_artefacto}      # Tipo segun RN-001
---
```

### Frontmatter por Tipo de Artefacto

#### TASK (Tareas)

```yaml
---
id: TASK-{NNN}
fecha: YYYY-MM-DD
tipo: task
categoria: desarrollo|testing|documentacion|infraestructura
dominio: backend|frontend|infraestructura|ai|transversal
prioridad: alta|media|baja
estado: pendiente|en_progreso|completada|bloqueada
asignado: {username}        # Opcional
relacionado:                # Opcional, lista de IDs relacionados
  - RF-XXX
  - ADR-YYY
---
```

#### ADR (Architecture Decision Records)

```yaml
---
id: ADR-{NNN}
fecha: YYYY-MM-DD
tipo: adr
categoria: arquitectura
estado: propuesto|aceptado|rechazado|deprecado|supersedido
supersede: []               # IDs de ADRs que reemplaza
superseded_by: []           # IDs de ADRs que lo reemplazan
---
```

#### ANALISIS (Documentos de Analisis)

```yaml
---
fecha: YYYY-MM-DD
tipo: analisis
categoria: documentacion
autor: {username|agente}
relacionado:                # Opcional
  - N-XXX
  - RN-YYY
---
```

#### DOCUMENTACION_AGENTE

```yaml
---
id: AGENT-{NAME}
fecha: YYYY-MM-DD
tipo: documentacion_agente
categoria: documentacion
version: X.Y.Z
autor: equipo-arquitectura
status: active|deprecated
---
```

#### GUIA

```yaml
---
id: GUIA-{TEMA}
fecha: YYYY-MM-DD
tipo: guia
categoria: gobernanza
version: X.Y.Z
autor: equipo-arquitectura|tech-lead
---
```

#### REQUISITO FUNCIONAL (para futuro)

```yaml
---
id: RF-{XXX}
fecha: YYYY-MM-DD
tipo: funcional
titulo: {titulo_conciso}
dominio: backend|frontend|infraestructura|ai
owner: equipo-{dominio}
prioridad: critica|alta|media|baja
estado: propuesto|en_revision|aprobado|en_desarrollo|implementado|verificado
trazabilidad_upward:
  - N-XXX
  - RN-YYY
  - UC-ZZZ
trazabilidad_downward:
  - TEST-AAA
  - TASK-BBB
---
```

### Generacion Automatica de Campos

El sistema debe:

1. **Fecha**: Generada automaticamente como `datetime.now().strftime("%Y-%m-%d")`
2. **ID**: Extraido del nombre de archivo o generado secuencialmente
3. **Tipo**: Determinado por RN-001 (clasificacion)
4. **Categoria**: Mapeada desde tipo (task→desarrollo, adr→arquitectura, etc.)
5. **Dominio**: Extraido de contexto o path del archivo
6. **Estado**: Default segun tipo (task→pendiente, adr→propuesto, etc.)

### Campos Opcionales

Estos campos pueden omitirse si no hay informacion disponible:

- `asignado` (tasks)
- `relacionado` (todos)
- `autor` (si no se conoce)
- `version` (si es primera version)
- `trazabilidad_upward/downward` (si no hay aun)

### Validacion de Frontmatter

El frontmatter generado DEBE:

1. **Sintaxis YAML valida**: Parseable por PyYAML
2. **Delimitadores**: Iniciar y terminar con `---`
3. **Campos obligatorios presentes**: `fecha` y `tipo` siempre
4. **IDs validos**: Formato correcto (TASK-001, ADR-010, etc.)
5. **Valores en enumeraciones**: Estados/prioridades/categorias validos

## Impacto en Requisitos

- **RF-005**: Generar frontmatter YAML apropiado por tipo
- **RNF-004**: Mantenibilidad - Facilita busqueda y trazabilidad
- **RF-XXX** (futuro): Trazabilidad automatica upward/downward

## Evidencia

- ISO/IEC/IEEE 29148:2018 - Requiere trazabilidad bidireccional
- BABOK v3 - Gestion de requisitos con trazabilidad
- Plantillas existentes (template_requisito_funcional.md) - usan frontmatter YAML

## Observaciones

- **Flexibilidad**: Agentes pueden agregar campos custom adicionales si es util
- **Evolucion**: Estructura de frontmatter puede evolucionar, mantener backward compatibility
- **Herramientas**: Frontmatter YAML permite indexacion con Jekyll, Hugo, Obsidian, etc.
- **Busqueda**: Permite busquedas tipo `grep "tipo: task" **/*.md` para encontrar todas las tareas
