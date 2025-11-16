---
name: CoherenceAnalyzerAgent
description: Agente especializado en analisis de coherencia entre API endpoints y servicios UI, detectando gaps, inconsistencias y validando correspondencia entre backend y frontend.
---

# Automation: Coherence Analyzer Agent

El CoherenceAnalyzerAgent es un agente de automatizacion que realiza analisis avanzado de coherencia entre API endpoints (REST/GraphQL) y servicios UI (TypeScript/JavaScript) utilizando parsing AST, analisis de correlacion y deteccion de gaps.

## Capacidades

### Analisis de API
- Extraccion de endpoints REST (ViewSets, APIViews)
- Analisis de endpoints GraphQL (queries, mutations)
- Deteccion de serializadores Django REST
- Parsing de patrones URL
- Identificacion de acciones y metodos HTTP

### Analisis de UI
- Extraccion de servicios TypeScript/JavaScript
- Identificacion de metodos que consumen APIs
- Analisis de llamadas HTTP (GET, POST, PUT, DELETE)
- Deteccion de endpoints invocados

### Deteccion de Gaps
- APIs sin tests
- APIs sin consumo en UI
- Servicios UI sin API correspondiente
- Endpoints duplicados o inconsistentes
- Metodos HTTP no mapeados

### Analisis de Correlacion
- Mapeo API-UI bidireccional
- Validacion de correspondencia de campos
- Deteccion de inconsistencias de naming
- Analisis de cobertura de tests

### Reportes
- Reporte JSON estructurado
- Reporte Markdown formateado
- Metricas de coherencia
- Recomendaciones de accion

## Cuando usar

- **Pre-Merge**: Validar coherencia antes de integrar cambios
- **Refactoring**: Identificar gaps antes de reestructurar
- **Code Review**: Detectar inconsistencias API-UI
- **Documentation**: Generar mapeo automatico API-UI
- **Quality Gates**: Validar cobertura de tests
- **Onboarding**: Entender arquitectura existente

## Como usar

### Analisis Completo

```bash
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --api-path api/callcentersite \
  --ui-path ui/src \
  --test-path api/callcentersite/tests \
  --output coherence_report.json \
  --markdown
```

### Analisis Especifico

```bash
# Solo analisis de APIs REST
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --api-path api/callcentersite \
  --analysis-type rest \
  --output api_analysis.json

# Solo analisis GraphQL
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --api-path api/callcentersite \
  --analysis-type graphql \
  --output graphql_analysis.json

# Solo deteccion de gaps
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --api-path api/callcentersite \
  --ui-path ui/src \
  --gap-detection-only \
  --output gaps.json
```

### Integracion CI/CD

```bash
# Validacion en pipeline
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --api-path api/callcentersite \
  --ui-path ui/src \
  --fail-on-gaps \
  --threshold 0.95
```

## Output esperado

### Reporte JSON

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "api_endpoints": {
    "rest": 45,
    "graphql_queries": 12,
    "graphql_mutations": 8
  },
  "ui_services": {
    "total": 38,
    "methods": 156
  },
  "gaps": {
    "apis_without_tests": [
      "CallViewSet.custom_action",
      "CustomerViewSet.batch_update"
    ],
    "apis_without_ui": [
      "StatisticsViewSet.export"
    ],
    "ui_without_api": [
      "ReportService.generateCustomReport"
    ]
  },
  "correlation": {
    "coverage": 0.92,
    "mapped_apis": 41,
    "mapped_ui_methods": 144
  },
  "recommendations": [
    "Add tests for CallViewSet.custom_action",
    "Create UI service for StatisticsViewSet.export",
    "Implement API for ReportService.generateCustomReport"
  ]
}
```

### Reporte Markdown

```markdown
# Coherence Analysis Report

## Summary
- API Endpoints: 65 (45 REST, 20 GraphQL)
- UI Services: 38
- Coverage: 92%

## Gaps Detected
### APIs without Tests (2)
- CallViewSet.custom_action
- CustomerViewSet.batch_update

### APIs without UI Consumption (1)
- StatisticsViewSet.export

### UI without API (1)
- ReportService.generateCustomReport

## Recommendations
1. Prioridad ALTA: Add tests for CallViewSet.custom_action
2. Prioridad MEDIA: Create UI service for StatisticsViewSet.export
```

## Herramientas y dependencias

- **Python 3.11+**
- **AST parsing**: ast, astroid
- **Analisis estatico**: radon, complexity
- **Formato**: json, markdown

## Buenas practicas

1. **Ejecutar regularmente**: Integrar en CI/CD pipeline
2. **Analizar antes de merge**: Validar cambios en PRs
3. **Mantener threshold**: Definir cobertura minima aceptable
4. **Documentar excepciones**: Justificar gaps deliberados
5. **Iterar sobre gaps**: Priorizar resolucion de inconsistencias

## Restricciones

- **Solo Django REST y GraphQL**: No soporta otros frameworks
- **Solo TypeScript/JavaScript**: No analiza otros lenguajes frontend
- **AST parsing**: Requiere codigo sintacticamente valido
- **Estructura esperada**: Asume convenciones Django/React estandar

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/coherence_analyzer_agent.py`
Tests: `scripts/coding/ai/tests/test_coherence_analyzer_agent.py`
