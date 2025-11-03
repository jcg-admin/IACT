---
id: DOC-ANEXO-DIAGRAMAS
estado: activo
propietario: equipo-documentacion
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-ANEXO-INDEX", "DOC-ARQ-INDEX"]
---
# Diagramas de Referencia

Este espacio almacena diagramas técnicos, arquitectónicos y de proceso del proyecto IACT.

## Página padre
- [Anexos](../readme.md)

## Información clave

### Tipos de Diagramas

**Arquitectura:**
- Diagramas C4 (Context, Container, Component, Code)
- Diagramas de infraestructura
- Topología de red
- Diagramas de deployment

**Procesos:**
- Diagramas de flujo
- Diagramas de secuencia
- Diagramas de actividad
- BPMN (Business Process Model and Notation)

**Datos:**
- Diagramas ER (Entity-Relationship)
- Esquemas de base de datos
- Modelos de datos

**UML:**
- Diagramas de clases
- Diagramas de paquetes
- Diagramas de estados

### Formato Recomendado

**Mermaid (Preferido):**
```mermaid
graph LR
    A[Usuario] --> B[API Gateway]
    B --> C[Backend Django]
    C --> D[PostgreSQL]
    C --> E[MariaDB]
```

**Ventajas de Mermaid:**
- ✅ Texto plano (versionable en Git)
- ✅ Renderiza en GitHub, MkDocs, VS Code
- ✅ Fácil de mantener y actualizar
- ✅ No requiere herramientas externas

**Otros formatos aceptados:**
- PlantUML (.puml)
- Draw.io (.drawio) - exportar también como SVG
- Imágenes (PNG, SVG) - con fuente editable

### Estructura de Archivos

```
diagramas/
├── arquitectura/
│   ├── c4-context.mmd
│   ├── c4-container.mmd
│   └── infraestructura.mmd
├── procesos/
│   ├── etl-flow.mmd
│   └── deployment-flow.mmd
├── datos/
│   ├── er-analytics.mmd
│   └── er-ivr.mmd
└── uml/
    ├── clases-servicios.mmd
    └── secuencia-etl.mmd
```

### Convenciones de Nombrado

```
{tipo}-{descripcion}.{extension}

Ejemplos:
- c4-context-iact.mmd
- sequence-etl-process.mmd
- er-analytics-database.mmd
- flow-deployment-prod.mmd
```

### Ejemplos

**Diagrama C4 - Context:**
```mermaid
C4Context
    title Sistema IACT - Diagrama de Contexto

    Person(usuario, "Analista", "Usuario del dashboard")
    System(iact, "IACT Platform", "Plataforma de analítica de call center")
    System_Ext(ivr, "Sistema IVR", "Sistema telefónico existente")

    Rel(usuario, iact, "Consulta métricas", "HTTPS")
    Rel(iact, ivr, "Extrae datos", "MySQL")
```

**Diagrama de Secuencia - ETL:**
```mermaid
sequenceDiagram
    participant Scheduler
    participant ETL
    participant IVR_DB
    participant Analytics_DB

    Scheduler->>ETL: Trigger daily job
    ETL->>IVR_DB: Extract calls data
    IVR_DB-->>ETL: Raw data
    ETL->>ETL: Transform & calculate metrics
    ETL->>Analytics_DB: Load processed data
    Analytics_DB-->>ETL: Confirmation
    ETL-->>Scheduler: Job complete
```

## Buenas Prácticas

1. **Versionado**: Incluir fecha o versión en el nombre del archivo
2. **Documentación**: Agregar descripción en comentario al inicio
3. **Simplicidad**: Un diagrama por concepto
4. **Actualización**: Marcar diagramas obsoletos claramente
5. **Fuente**: Guardar archivos editables (no solo imágenes)

## Herramientas Recomendadas

- **Mermaid Live Editor**: https://mermaid.live
- **VS Code Extension**: Mermaid Preview
- **PlantUML**: https://plantuml.com
- **Draw.io**: https://app.diagrams.net

## Recursos relacionados
- [Arquitectura](../../arquitectura/readme.md)
- [Diseño Detallado](../../diseno_detallado/readme.md)
- [Ejemplos Completos](../ejemplos/readme.md)
