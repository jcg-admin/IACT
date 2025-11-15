---
name: Architecture Analysis Agent
description: Agente especializado en analisis arquitectonico de sistemas, evaluacion de patrones, identificacion de mejoras y generacion de recomendaciones de arquitectura.
---

# Architecture Analysis Agent

Agente especializado en realizar analisis profundo de arquitecturas de software, evaluando estructuras, patrones, dependencias y proponiendo mejoras arquitectonicas alineadas con principios SOLID, Clean Architecture y mejores practicas de la industria.

## Capacidades

### Analisis Arquitectonico
- Evaluacion de arquitectura actual (monolitica, microservicios, serverless)
- Identificacion de patrones arquitectonicos utilizados
- Analisis de dependencias entre componentes
- Mapeo de flujos de datos y comunicacion
- Deteccion de acoplamiento excesivo

### Evaluacion de Calidad
- Cohesion y acoplamiento de modulos
- Adherencia a principios SOLID
- Analisis de complejidad ciclomatica
- Evaluacion de mantenibilidad
- Identificacion de code smells arquitectonicos

### Recomendaciones
- Propuestas de refactorizacion arquitectonica
- Sugerencias de patrones aplicables
- Estrategias de migracion (monolito a microservicios)
- Optimizaciones de performance
- Mejoras de escalabilidad

### Generacion de Artefactos
- Diagramas C4 (Context, Container, Component, Code)
- Diagramas de dependencias
- Documentacion de decisiones arquitectonicas (ADRs)
- Matrices de trazabilidad

## Cuando Usar

- Evaluacion inicial de arquitectura existente
- Planificacion de refactorizacion mayor
- Preparacion para escalamiento
- Migracion de arquitectura
- Auditoria de calidad arquitectonica
- Documentacion de sistema legacy

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/architecture_analysis_agent.py \
  --project-root /ruta/al/proyecto \
  --analysis-scope full \
  --output-format markdown
```

### Analisis de Modulo Especifico

```bash
python scripts/coding/ai/meta/architecture_analysis_agent.py \
  --project-root . \
  --target-module api/authentication \
  --analysis-type dependencies \
  --depth 3
```

### Generacion de C4 Diagrams

```bash
python scripts/coding/ai/meta/architecture_analysis_agent.py \
  --project-root . \
  --generate-c4 \
  --c4-level container \
  --output-dir docs/architecture
```

### Evaluacion de Calidad

```bash
python scripts/coding/ai/meta/architecture_analysis_agent.py \
  --project-root . \
  --quality-check \
  --metrics cohesion,coupling,complexity \
  --threshold-warn 7 \
  --threshold-error 10
```

## Parametros

- `--project-root`: Directorio raiz del proyecto
- `--analysis-scope`: Alcance (module, application, full)
- `--target-module`: Modulo especifico a analizar
- `--analysis-type`: Tipo (structure, dependencies, quality, patterns)
- `--output-format`: Formato (markdown, json, html)
- `--generate-c4`: Generar diagramas C4
- `--c4-level`: Nivel C4 (context, container, component, code)
- `--quality-check`: Ejecutar evaluacion de calidad
- `--metrics`: Metricas a evaluar
- `--depth`: Profundidad de analisis de dependencias

## Salida

```markdown
# Architecture Analysis Report
Project: IACT Call Center
Date: 2025-11-15
Scope: Full System

## Architecture Overview
Type: Modular Monolith (transitioning to microservices)
Pattern: Layered Architecture with DDD elements
Framework: Django 5.x

## Component Analysis

### Backend (api/)
- Type: REST API
- Layers: Presentation, Application, Domain, Infrastructure
- Dependencies: PostgreSQL, MariaDB (read-only), Redis
- Coupling: Medium (76/100)
- Cohesion: High (88/100)

### Frontend (ui/)
- Type: SPA
- Framework: React
- State Management: Redux
- Coupling: Low (82/100)
- Cohesion: High (91/100)

## Quality Metrics

| Metric | Score | Threshold | Status |
|--------|-------|-----------|--------|
| Cohesion | 88/100 | >70 | PASS |
| Coupling | 76/100 | <80 | PASS |
| Complexity | 6.2 | <10 | PASS |
| Maintainability | 85/100 | >70 | PASS |

## Identified Issues

1. MEDIUM: Circular dependency between authentication and user modules
2. LOW: Infrastructure layer partially exposed to presentation
3. INFO: Opportunity for CQRS pattern in reporting module

## Recommendations

1. Break circular dependency via dependency injection
2. Introduce anti-corruption layer for infrastructure
3. Consider CQRS for read-heavy reporting endpoints
4. Extract notification service to separate microservice

## Architecture Decision Records Generated

- ADR-001: Adopt Repository Pattern for data access
- ADR-002: Implement CQRS for reporting module
- ADR-003: Use Event Sourcing for audit trail

[End of Report]
```

## Herramientas y Dependencias

- **radon**: Metricas de complejidad y mantenibilidad
- **pydeps**: Analisis de dependencias Python
- **graphviz**: Generacion de diagramas
- **pylint**: Metricas de calidad estatica
- **diagrams**: Generacion de diagramas programaticos

## Mejores Practicas

1. Ejecutar analisis completo al inicio de proyecto
2. Re-analizar despues de cambios arquitectonicos mayores
3. Integrar en CI para detectar regresiones arquitectonicas
4. Mantener ADRs actualizados con decisiones
5. Revisar metricas de acoplamiento en cada release
6. Documentar justificaciones de patrones elegidos

## Restricciones

- Requiere acceso completo al codigo fuente
- Analisis profundo puede tomar 5-15 minutos en proyectos grandes
- Algunos patrones complejos requieren revision manual
- Metricas son indicativas, no absolutas
- No detecta problemas de runtime o performance

## Ubicacion

Archivo: `scripts/coding/ai/meta/architecture_analysis_agent.py`
