---
name: MetricsCollectorAgent
description: Agente especializado en recoleccion, agregacion y analisis de metricas de desarrollo (DORA, code quality, test coverage, performance) para dashboards y reportes de observabilidad.
---

# Automation: Metrics Collector Agent

El MetricsCollectorAgent recolecta, agrega y analiza metricas de desarrollo incluyendo metricas DORA, calidad de codigo, cobertura de tests y performance para dashboards y reportes.

## Capacidades

### Metricas DORA
- **Deployment Frequency**: Frecuencia de deployments
- **Lead Time for Changes**: Tiempo commit-to-production
- **Mean Time to Recovery (MTTR)**: Tiempo de recuperacion
- **Change Failure Rate**: Tasa de fallos en cambios

### Metricas de Calidad
- **Code Coverage**: Cobertura de tests (unit, integration, E2E)
- **Complexity**: Cyclomatic complexity promedio
- **Technical Debt**: Horas estimadas de deuda tecnica
- **Code Smells**: Deteccion de anti-patterns
- **Duplicacion**: Porcentaje de codigo duplicado

### Metricas de Performance
- **Build Time**: Tiempo de construccion
- **Test Execution Time**: Tiempo de ejecucion de tests
- **CI Pipeline Duration**: Duracion de pipeline completo
- **Artifact Size**: Tamaño de artefactos generados

### Metricas de Proceso
- **PR Cycle Time**: Tiempo desde creacion hasta merge de PR
- **Code Review Time**: Tiempo en code review
- **Issue Resolution Time**: Tiempo de resolucion de issues
- **Bug Escape Rate**: Tasa de bugs que llegan a produccion

### Agregacion y Analisis
- Time series data
- Percentiles (P50, P90, P95, P99)
- Trends y regresiones
- Alertas y anomalias
- Correlaciones entre metricas

## Cuando usar

- **Daily Standup**: Revisar metricas del dia anterior
- **Sprint Review**: Analizar metricas del sprint
- **Retrospective**: Identificar areas de mejora
- **Dashboard Updates**: Actualizar dashboards de observabilidad
- **Alerting**: Detectar degradaciones en metricas
- **Capacity Planning**: Proyectar necesidades futuras

## Como usar

### Recoleccion Completa

```bash
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --repo owner/repo \
  --github-token $GITHUB_TOKEN \
  --collect-all \
  --period 30d \
  --output metrics_report.json
```

### Metricas Especificas

```bash
# Solo DORA
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --collect dora \
  --period 7d

# Solo Quality
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --collect quality \
  --coverage-threshold 80

# Solo Performance
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --collect performance \
  --baseline previous-week
```

### Trending y Alertas

```bash
# Detectar regresiones
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --detect-regressions \
  --alert-threshold 10% \
  --notify slack

# Generar trend report
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --trend-analysis \
  --period 90d \
  --output trend_report.md
```

### Dashboard Export

```bash
# Exportar para Grafana
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --export grafana \
  --output metrics.json

# Exportar para DataDog
python scripts/coding/ai/automation/metrics_collector_agent.py \
  --export datadog \
  --api-key $DD_API_KEY
```

## Output esperado

### Reporte de Metricas

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "period": "30d",
  "dora_metrics": {
    "deployment_frequency": {
      "value": 2.3,
      "unit": "per_day",
      "trend": "+15%",
      "percentiles": {
        "p50": 2.1,
        "p90": 3.5,
        "p99": 5.2
      }
    },
    "lead_time": {
      "value": 36.5,
      "unit": "hours",
      "trend": "-12%",
      "percentiles": {
        "p50": 32.0,
        "p90": 48.0,
        "p99": 72.0
      }
    },
    "mttr": {
      "value": 45.2,
      "unit": "minutes",
      "trend": "-8%"
    },
    "change_failure_rate": {
      "value": 0.08,
      "unit": "rate",
      "trend": "-25%"
    }
  },
  "quality_metrics": {
    "coverage": {
      "total": 0.85,
      "unit": 0.92,
      "integration": 0.78,
      "e2e": 0.65
    },
    "complexity": {
      "average": 4.2,
      "max": 15
    },
    "technical_debt": {
      "hours": 120,
      "ratio": 0.08
    }
  },
  "performance_metrics": {
    "build_time": {
      "avg": 180,
      "unit": "seconds"
    },
    "test_time": {
      "avg": 120,
      "unit": "seconds"
    }
  },
  "alerts": [
    {
      "severity": "warning",
      "metric": "change_failure_rate",
      "message": "Change failure rate increased by 12% in last 7 days"
    }
  ]
}
```

### Trend Report Markdown

```markdown
# Metrics Trend Report (90 days)

## DORA Metrics
### Deployment Frequency
- Current: 2.3 per day (+15% vs 90d ago)
- Trend: Improving steadily
- Goal: 3.0 per day by Q1

### Lead Time
- Current: 36.5 hours (-12% vs 90d ago)
- Trend: Improving
- Goal: 24 hours by Q1

## Quality Metrics
### Code Coverage
- Current: 85% (+5% vs 90d ago)
- Trend: Improving
- Goal: 90% by Q1

## Alerts
- [WARNING] Change failure rate increased 12% in last 7 days
```

## Herramientas y dependencias

- **Python 3.11+**
- **GitHub API**: PyGithub
- **Coverage**: coverage.py, pytest-cov
- **Complexity**: radon
- **Time series**: pandas
- **Visualization**: matplotlib

## Buenas practicas

1. **Recolectar regularmente**: Ejecutar diariamente en CI
2. **Baseline establecido**: Mantener datos historicos
3. **Alertas configuradas**: Notificar sobre regresiones
4. **Dashboard actualizado**: Visualizar trends en tiempo real
5. **Correlacion analisis**: Identificar cause-effect relationships
6. **Action-oriented**: Usar metricas para tomar decisiones
7. **Team transparency**: Compartir metricas con equipo

## Restricciones

- **GitHub dependiente**: Requiere GitHub para DORA metrics
- **Coverage tools**: Necesita pytest-cov o coverage.py configurado
- **Historico requerido**: Necesita datos previos para trends
- **CI integration**: Mejor con CI/CD configurado

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/metrics_collector_agent.py`
Tests: `scripts/coding/ai/tests/test_metrics_collector_agent.py`
Config: `.metrics_config.json`
