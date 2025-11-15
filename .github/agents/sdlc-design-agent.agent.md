---
name: SDLCDesignAgent
description: Agente especializado en generación de diseños técnicos HLD/LLD, diagramas de arquitectura, especificaciones de APIs y documentación técnica detallada para implementación.
---

# SDLC Design Agent

SDLCDesignAgent es un agente Python especializado en la fase de Design del ciclo SDLC. Su función principal es generar diseños técnicos detallados incluyendo High-Level Design (HLD), Low-Level Design (LLD), diagramas de arquitectura, especificaciones de APIs y documentación técnica necesaria para la implementación.

## Capacidades

### Generación de Diseños

- Creación de High-Level Design (HLD) con arquitectura general
- Generación de Low-Level Design (LLD) con detalles de implementación
- Especificación de componentes y sus interacciones
- Definición de interfaces y contratos
- Documentación de flujos de datos

### Diagramas y Visualizaciones

- Generación de diagramas de arquitectura (C4 Model)
- Diagramas de secuencia para flujos críticos
- Diagramas de clases y entidades
- Diagramas de despliegue
- Representación en PlantUML, Mermaid o draw.io

### Especificaciones de APIs

- Definición de endpoints REST/GraphQL
- Especificación de request/response schemas
- Documentación de códigos de error
- Definición de autenticación y autorización
- Generación de OpenAPI/Swagger specs

### Diseño de Base de Datos

- Esquemas de tablas y relaciones
- Definición de índices y constraints
- Estrategias de migración
- Optimizaciones de performance
- Documentación de queries críticos

## Cuándo Usarlo

### Antes de Implementación

- Generación de diseño técnico detallado
- Documentación de arquitectura de solución
- Definición de interfaces entre componentes
- Planificación de estructura de código

### Review de Arquitectura

- Generación de documentos para architecture review
- Visualización de decisiones de diseño
- Documentación de trade-offs
- Preparación de presentaciones técnicas

### Onboarding y Documentación

- Generación de documentación para nuevos devs
- Visualización de arquitectura existente
- Documentación de patrones utilizados
- Explicación de decisiones técnicas

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/design_agent.py \
  --feature-spec feature_spec.md \
  --design-type hld \
  --output-dir designs/
```

### Generación Completa (HLD + LLD + Diagramas)

```bash
python scripts/coding/ai/sdlc/design_agent.py \
  --feature-spec specs/notifications.md \
  --design-type full \
  --include-diagrams \
  --diagram-format mermaid \
  --api-spec \
  --db-schema \
  --project-root .
```

### Parámetros Principales

- `--feature-spec`: Archivo con especificación de la feature
- `--design-type`: Tipo de diseño (hld, lld, full, api, db)
- `--output-dir`: Directorio para outputs generados
- `--include-diagrams`: Generar diagramas
- `--diagram-format`: Formato de diagramas (plantuml, mermaid, drawio)
- `--api-spec`: Generar especificación OpenAPI
- `--db-schema`: Generar esquema de base de datos
- `--architecture-style`: Estilo arquitectónico (mvc, layered, microservices)

## Ejemplos de Uso

### Ejemplo 1: High-Level Design

```bash
python scripts/coding/ai/sdlc/design_agent.py \
  --feature-spec specs/payment_integration.md \
  --design-type hld \
  --include-diagrams
```

Genera:
- Documento HLD con componentes principales
- Diagrama de arquitectura C4 Level 2
- Descripción de interacciones entre sistemas
- Identificación de dependencias externas

### Ejemplo 2: API Design Completo

```bash
python scripts/coding/ai/sdlc/design_agent.py \
  --feature-spec specs/user_api.md \
  --design-type api \
  --api-spec \
  --output-format openapi
```

Genera:
- Especificación OpenAPI 3.0
- Documentación de endpoints
- Schemas de request/response
- Ejemplos de uso
- Códigos de error

### Ejemplo 3: Diseño de Base de Datos

```bash
python scripts/coding/ai/sdlc/design_agent.py \
  --feature-spec specs/reporting_module.md \
  --design-type db \
  --db-schema \
  --include-migrations
```

Genera:
- Esquema de tablas con tipos de datos
- Relaciones y constraints
- Índices recomendados
- Scripts de migración Django
- Queries de ejemplo

## Outputs Generados

### High-Level Design (HLD)

```markdown
# HLD: Sistema de Notificaciones en Tiempo Real

## Arquitectura General
- WebSocket Server (Django Channels)
- Message Broker (Redis pub/sub)
- Notification Service (FastAPI)
- Client Library (JavaScript SDK)

## Componentes Principales
[Diagrama C4]

## Flujo de Datos
1. User action → API Gateway
2. API Gateway → Notification Service
3. Notification Service → Redis pub/sub
4. Redis → WebSocket Server
5. WebSocket Server → Client

## Decisiones de Diseño
- Redis para pub/sub (baja latencia)
- WebSockets para conexión persistente
- Fallback a polling para browsers legacy
```

### Low-Level Design (LLD)

```markdown
# LLD: Notification Service

## Clases y Módulos
- NotificationManager: Coordinación de notificaciones
- WebSocketHandler: Manejo de conexiones
- MessageSerializer: Serialización de mensajes
- AuthMiddleware: Autenticación de conexiones

## Algoritmos Críticos
- Connection pooling con límite de 10K conexiones
- Backpressure handling con buffer circular
- Reconnection con exponential backoff

## Estructuras de Datos
[Diagramas de clases]
```

### API Specification (OpenAPI)

```yaml
openapi: 3.0.0
paths:
  /api/notifications:
    post:
      summary: Send notification
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id: string
                message: string
                type: enum
```

## Herramientas y Dependencias

- **Diagramming**: PlantUML, Mermaid, Graphviz
- **API Specs**: OpenAPI Generator, Swagger
- **Database**: Django ORM introspection, SQLAlchemy
- **LLM Providers**: Claude, GPT-4 para generación de diseños
- **Templates**: Jinja2 para generación de documentos

## Mejores Prácticas

### Inputs de Calidad

- Feature spec clara y completa
- Requisitos no funcionales especificados
- Restricciones técnicas documentadas
- Referencias a arquitectura existente

### Validación de Diseños

- Review de diagramas con equipo técnico
- Validación de APIs con consumidores
- Verificación de esquemas DB con DBA
- Feedback iterativo sobre LLD

### Mantenimiento

- Actualizar diseños cuando cambie implementación
- Versionar documentos de diseño
- Mantener diagramas sincronizados con código
- Documentar cambios significativos

## Restricciones

- Calidad depende de especificación de entrada
- Diagramas pueden requerir ajustes manuales
- No valida constraints de performance automáticamente
- Requiere revisión humana antes de implementación

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/design_agent.py`
