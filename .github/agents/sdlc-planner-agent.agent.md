---
name: SDLCPlannerAgent
description: Agente especializado en planificación de features, generación de user stories, estimación de esfuerzo y definición de requisitos técnicos para el ciclo SDLC.
---

# SDLC Planner Agent

SDLCPlannerAgent es un agente Python especializado en la fase de Planning del ciclo de vida de desarrollo de software (SDLC). Su función principal es analizar feature requests y convertirlos en issues o tickets bien estructurados con user stories completas, acceptance criteria, estimaciones de story points y requisitos técnicos identificados.

## Capacidades

### Análisis de Feature Requests

- Procesamiento de solicitudes en texto libre o URLs de issues
- Extracción de requisitos funcionales y no funcionales
- Identificación de dependencias técnicas
- Análisis de contexto del proyecto
- Detección de ambigüedades en requisitos

### Generación de User Stories

- Creación de user stories en formato estándar (Como... Quiero... Para...)
- Definición de acceptance criteria claros y verificables
- Especificación de criterios de aceptación INVEST
- Identificación de actores y roles involucrados
- Documentación de escenarios de uso

### Estimación y Priorización

- Cálculo de story points basado en complejidad
- Análisis de esfuerzo técnico requerido
- Recomendaciones de prioridad (P0-P4)
- Identificación de riesgos técnicos
- Evaluación de viabilidad técnica

### Documentación Técnica

- Generación de requisitos técnicos detallados
- Especificación de arquitectura necesaria
- Identificación de tecnologías requeridas
- Definición de criterios de completitud
- Enlaces a documentación relevante

## Cuándo Usarlo

### Inicio de Features

- Análisis inicial de nuevas funcionalidades
- Conversión de ideas en requisitos formales
- Creación de backlog estructurado
- Definición de épicas y features

### Planning Meetings

- Preparación de sprint planning
- Generación de issues para refinamiento
- Estimación de esfuerzo técnico
- Priorización de backlog

### Refinamiento de Backlog

- Desglose de features grandes
- Clarificación de requisitos ambiguos
- Actualización de estimaciones
- Identificación de dependencias

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/planner_agent.py \
  --feature-request "Implementar autenticación JWT" \
  --project-root . \
  --output-format github
```

### Con Contexto de Proyecto

```bash
python scripts/coding/ai/sdlc/planner_agent.py \
  --feature-request-file feature_request.md \
  --project-context docs/architecture/README.md \
  --backlog-file backlog.json \
  --output-file issue_draft.md
```

### Parámetros Principales

- `--feature-request`: Descripción de la feature en texto libre
- `--feature-request-file`: Archivo con la descripción de la feature
- `--project-root`: Directorio raíz del proyecto (default: .)
- `--project-context`: Archivo con contexto del proyecto
- `--backlog`: Archivo JSON con backlog existente
- `--output-format`: Formato de salida (github, jira, markdown)
- `--llm-provider`: Proveedor LLM (anthropic, openai, huggingface)
- `--model`: Modelo específico a usar

## Ejemplos de Uso

### Ejemplo 1: Feature Simple

```bash
python scripts/coding/ai/sdlc/planner_agent.py \
  --feature-request "Los usuarios deben poder exportar reportes a PDF"
```

Genera:
- User story completa
- 3-5 acceptance criteria
- Estimación de story points
- Requisitos técnicos (librerías PDF, formato, permisos)

### Ejemplo 2: Feature Compleja con Contexto

```bash
python scripts/coding/ai/sdlc/planner_agent.py \
  --feature-request "Sistema de notificaciones en tiempo real" \
  --project-context docs/architecture/backend.md \
  --output-format github
```

Genera:
- Análisis de arquitectura necesaria (WebSockets, Redis, etc.)
- Desglose en sub-tasks
- Estimación de esfuerzo por componente
- Identificación de riesgos técnicos

### Ejemplo 3: Refinamiento de Issue Existente

```bash
python scripts/coding/ai/sdlc/planner_agent.py \
  --feature-request "https://github.com/org/repo/issues/123" \
  --backlog backlog.json \
  --output-file refined_issue.md
```

## Outputs Generados

### GitHub Issue Format

```markdown
## User Story
Como [rol], quiero [funcionalidad] para [beneficio]

## Acceptance Criteria
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Technical Requirements
- Backend: Django REST Framework
- Frontend: React components
- Database: PostgreSQL migrations

## Story Points
Estimación: 5 points

## Priority
P2 - High Priority
```

### Información Adicional

- Enlaces a documentación técnica
- Diagramas de arquitectura sugeridos
- Dependencias identificadas
- Riesgos técnicos evaluados

## Herramientas y Dependencias

- **LLM Providers**: Claude (Anthropic), GPT-4 (OpenAI), Llama (HuggingFace)
- **Input Formats**: Texto libre, Markdown, URLs de issues
- **Output Formats**: GitHub Issues, JIRA tickets, Markdown
- **Análisis**: Parsing de requisitos, NLP para extracción
- **Integración**: GitHub API, contexto de proyecto

## Mejores Prácticas

### Calidad de Inputs

- Proporcionar contexto de proyecto cuando esté disponible
- Incluir enlaces a documentación relevante
- Especificar restricciones técnicas conocidas
- Mencionar integraciones existentes

### Revisión de Outputs

- Validar acceptance criteria son verificables
- Confirmar estimaciones con equipo técnico
- Ajustar prioridades según roadmap
- Refinar requisitos técnicos identificados

### Integración con Workflow

- Usar en ceremonias de planning
- Alimentar con feedback de sprints anteriores
- Iterar sobre estimaciones basadas en velocidad real
- Mantener consistencia en formato de issues

## Restricciones

- Requiere conexión a internet para LLM providers
- Calidad depende del contexto proporcionado
- Estimaciones son orientativas, no definitivas
- No reemplaza discusión técnica del equipo

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/planner_agent.py`
