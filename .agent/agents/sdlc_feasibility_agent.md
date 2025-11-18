---
name: SDLCFeasibilityAgent
description: Agente especializado en análisis de viabilidad técnica, evaluación de riesgos, identificación de limitaciones y recomendaciones de arquitectura para features propuestas.
---

# SDLC Feasibility Agent

SDLCFeasibilityAgent es un agente Python especializado en la fase de Feasibility del ciclo SDLC. Su función principal es analizar la viabilidad técnica de features propuestas, evaluar riesgos, identificar limitaciones del sistema actual y proporcionar recomendaciones de arquitectura antes de iniciar la implementación.

## Capacidades

### Análisis de Viabilidad Técnica

- Evaluación de factibilidad con stack tecnológico actual
- Identificación de limitaciones de infraestructura
- Análisis de compatibilidad con sistemas existentes
- Verificación de disponibilidad de recursos
- Evaluación de tiempo de implementación realista

### Evaluación de Riesgos

- Identificación de riesgos técnicos (alto, medio, bajo)
- Análisis de impacto en sistemas existentes
- Detección de dependencias críticas
- Evaluación de complejidad técnica
- Análisis de riesgos de seguridad y performance

### Análisis de Arquitectura

- Evaluación de necesidad de cambios arquitectónicos
- Identificación de patrones de diseño aplicables
- Análisis de escalabilidad de la solución propuesta
- Recomendaciones de tecnologías específicas
- Evaluación de deuda técnica generada

### Estimación de Recursos

- Cálculo de recursos técnicos necesarios
- Estimación de capacidad de equipo requerida
- Identificación de skills gaps
- Evaluación de necesidad de capacitación
- Análisis de costo-beneficio técnico

## Cuándo Usarlo

### Antes de Aprobar Features

- Evaluación inicial de propuestas técnicas
- Análisis de viabilidad antes de commitment
- Validación de estimaciones de planning
- Identificación temprana de blockers

### Planning de Arquitectura

- Decisiones de arquitectura técnica
- Evaluación de alternativas de implementación
- Análisis de impacto en sistemas existentes
- Planificación de refactorings necesarios

### Evaluación de RFCs

- Análisis de propuestas técnicas (RFCs)
- Validación de diseños propuestos
- Identificación de riesgos no considerados
- Recomendaciones de mejoras

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/feasibility_agent.py \
  --feature-description "Sistema de notificaciones en tiempo real" \
  --project-root . \
  --analyze-risks
```

### Análisis Completo con Contexto

```bash
python scripts/coding/ai/sdlc/feasibility_agent.py \
  --feature-file feature_spec.md \
  --project-root . \
  --architecture-docs docs/architecture/ \
  --tech-stack-file tech_stack.json \
  --output-file feasibility_report.md
```

### Parámetros Principales

- `--feature-description`: Descripción de la feature a analizar
- `--feature-file`: Archivo con especificación de la feature
- `--project-root`: Directorio raíz del proyecto
- `--architecture-docs`: Directorio con documentación de arquitectura
- `--tech-stack-file`: Archivo JSON con stack tecnológico actual
- `--analyze-risks`: Flag para análisis de riesgos detallado
- `--estimate-effort`: Genera estimación de esfuerzo
- `--llm-provider`: Proveedor LLM (anthropic, openai, huggingface)

## Ejemplos de Uso

### Ejemplo 1: Análisis de Viabilidad Básico

```bash
python scripts/coding/ai/sdlc/feasibility_agent.py \
  --feature-description "Integración con API de terceros para pagos" \
  --project-root .
```

Genera:
- Evaluación de viabilidad: VIABLE / VIABLE CON RIESGOS / NO VIABLE
- Lista de riesgos identificados
- Requisitos técnicos específicos
- Estimación de complejidad

### Ejemplo 2: Análisis con Arquitectura Existente

```bash
python scripts/coding/ai/sdlc/feasibility_agent.py \
  --feature-file specs/realtime_notifications.md \
  --architecture-docs docs/architecture/ \
  --analyze-risks \
  --estimate-effort
```

Genera:
- Análisis de impacto en arquitectura actual
- Identificación de componentes afectados
- Riesgos de seguridad y performance
- Estimación de esfuerzo técnico
- Recomendaciones de implementación

### Ejemplo 3: Evaluación de Alternativas

```bash
python scripts/coding/ai/sdlc/feasibility_agent.py \
  --feature-description "Cache distribuido" \
  --alternatives "Redis,Memcached,Hazelcast" \
  --tech-stack-file tech_stack.json
```

## Outputs Generados

### Reporte de Viabilidad

```markdown
## Feasibility Analysis

### Viabilidad General: VIABLE CON RIESGOS

### Riesgos Identificados
1. [HIGH] Cambio arquitectónico en módulo de autenticación
2. [MEDIUM] Dependencia de servicio externo con SLA desconocido
3. [LOW] Incremento en uso de memoria

### Requisitos Técnicos
- Actualización de Django 4.2 a 5.0
- Implementación de WebSockets (django-channels)
- Configuración de Redis para pub/sub

### Limitaciones Actuales
- Infraestructura actual no soporta conexiones persistentes
- Base de datos no optimizada para queries en tiempo real

### Recomendaciones
1. Implementar caché de sesiones con Redis
2. Migrar endpoints críticos a arquitectura asíncrona
3. Configurar monitoring de performance

### Estimación de Esfuerzo
- Desarrollo: 3-4 sprints
- Testing: 1 sprint
- Despliegue: 2 semanas
```

## Herramientas y Dependencias

- **Análisis**: AST parsing, dependency analysis
- **LLM Providers**: Claude, GPT-4, Llama
- **Inputs**: Feature specs, arquitectura, tech stack
- **Integración**: GitHub API, documentation parsers

## Mejores Prácticas

### Inputs de Calidad

- Proporcionar documentación de arquitectura actualizada
- Incluir tech stack completo y versiones
- Especificar restricciones conocidas (SLA, presupuesto)
- Documentar integraciones existentes

### Interpretación de Resultados

- Riesgos HIGH requieren discusión con arquitectos
- VIABLE CON RIESGOS necesita plan de mitigación
- NO VIABLE debe incluir alternativas
- Validar estimaciones con equipo técnico

### Integración con SDLC

- Ejecutar antes de refinement meetings
- Usar para validar RFCs técnicos
- Incorporar en approval process de features
- Actualizar con feedback post-implementación

## Restricciones

- Análisis basado en documentación disponible
- No reemplaza code review manual
- Requiere contexto actualizado del proyecto
- Estimaciones son orientativas

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/feasibility_agent.py`
