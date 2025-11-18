---
name: CIPipelineOrchestratorAgent
description: Agente especializado en orquestacion de pipelines CI/CD, coordinando ejecucion de jobs, gestion de dependencias, paralelizacion y optimizacion de flujos de integracion continua.
---

# Automation: CI Pipeline Orchestrator Agent

El CIPipelineOrchestratorAgent orquesta pipelines CI/CD coordinando ejecucion de jobs, gestionando dependencias entre stages, optimizando paralelizacion y monitoreando performance.

## Capacidades

### Orquestacion de Pipeline
- Ejecucion secuencial de stages
- Paralelizacion de jobs independientes
- Gestion de dependencias entre jobs
- Conditional execution basada en eventos
- Retry logic con backoff exponencial

### Optimizacion de Performance
- Analisis de critical path
- Identificacion de bottlenecks
- Paralelizacion automatica
- Cache optimization
- Resource allocation inteligente

### Gestion de Artefactos
- Upload/download de artifacts
- Artifact caching
- Cleanup de artifacts antiguos
- Versionado de artifacts

### Monitoring y Reporting
- Real-time pipeline status
- Duration tracking por job
- Failure analysis
- Trend reporting
- Alerting sobre degradaciones

### Matrix Builds
- Configuracion de matrix strategies
- Version combinations
- Platform-specific builds
- Parallel matrix execution

## Cuando usar

- **CI/CD Setup**: Configurar nuevo pipeline
- **Pipeline Optimization**: Reducir tiempos de ejecucion
- **Troubleshooting**: Diagnosticar fallos de pipeline
- **Scaling**: Manejar aumento de jobs
- **Monitoring**: Trackear performance de CI
- **Cost Optimization**: Reducir costos de CI runners

## Como usar

### Orchestrar Pipeline Completo

```bash
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --pipeline-config .github/workflows/ci.yml \
  --orchestrate \
  --optimize
```

### Analizar Pipeline Performance

```bash
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --analyze-performance \
  --pipeline ci.yml \
  --period 30d \
  --output performance_report.json
```

### Optimizar Pipeline

```bash
# Identificar bottlenecks
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --identify-bottlenecks \
  --pipeline ci.yml

# Sugerir optimizaciones
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --suggest-optimizations \
  --pipeline ci.yml \
  --target-reduction 30%

# Aplicar optimizaciones
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --apply-optimizations \
  --pipeline ci.yml \
  --backup
```

### Matrix Build Configuration

```bash
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --generate-matrix \
  --python-versions "3.11,3.12" \
  --node-versions "18,20" \
  --platforms "ubuntu,macos"
```

### Monitoring y Alerting

```bash
# Monitor pipeline execution
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --monitor \
  --pipeline ci.yml \
  --alert-threshold 300s

# Generate trend report
python scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
  --trend-report \
  --period 90d \
  --output ci_trends.md
```

## Output esperado

### Performance Analysis

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "pipeline": "ci.yml",
  "period": "30d",
  "total_runs": 450,
  "avg_duration": 285,
  "p50_duration": 270,
  "p95_duration": 420,
  "critical_path": [
    {
      "stage": "test",
      "job": "integration-tests",
      "duration": 180,
      "percentage": 63.2
    },
    {
      "stage": "build",
      "job": "frontend-build",
      "duration": 90,
      "percentage": 31.6
    }
  ],
  "bottlenecks": [
    {
      "job": "integration-tests",
      "issue": "Sequential execution",
      "impact": "60s potential reduction",
      "recommendation": "Parallelize test suites"
    }
  ],
  "optimization_opportunities": [
    {
      "type": "caching",
      "target": "pip dependencies",
      "estimated_savings": "45s per run"
    },
    {
      "type": "parallelization",
      "target": "lint jobs",
      "estimated_savings": "30s per run"
    }
  ]
}
```

### Optimized Pipeline Config

```yaml
# Before optimization
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt  # 60s
      - run: pytest tests/unit                # 45s
      - run: pytest tests/integration         # 120s

# After optimization
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-suite: [unit, integration]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v3              # Added caching
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      - run: pip install -r requirements.txt  # Now 15s with cache
      - run: pytest tests/${{ matrix.test-suite }}  # Parallelized
```

### Trend Report

```markdown
# CI Pipeline Performance Trends (90 days)

## Overall Metrics
- Average duration: 285s (-12% vs 90d ago)
- P95 duration: 420s (-8% vs 90d ago)
- Success rate: 96.5% (+2% vs 90d ago)

## Optimizations Applied
1. Pip caching (Day 30): -45s average
2. Test parallelization (Day 60): -60s average
3. Artifact cleanup (Day 75): -5s average

## Bottlenecks Remaining
1. Integration tests: 180s (63% of total)
2. Frontend build: 90s (32% of total)

## Recommendations
- Consider test sharding for integration tests
- Investigate frontend build optimization
```

## Herramientas y dependencias

- **Python 3.11+**
- **YAML parsing**: PyYAML
- **GitHub Actions**: API integration
- **Graphing**: networkx para dependency graphs
- **Monitoring**: prometheus_client

## Buenas practicas

1. **Paralelizar when safe**: Jobs independientes en paralelo
2. **Cache aggressively**: Dependencias, build artifacts
3. **Fail fast**: Cheap checks primero (lint, format)
4. **Monitor trends**: Trackear degradaciones en tiempo
5. **Optimize critical path**: Enfocarse en jobs mas lentos
6. **Resource-aware**: Balancear performance vs costo
7. **Idempotent jobs**: Jobs reintentables sin side effects

## Restricciones

- **GitHub Actions focused**: Optimizado para GitHub Actions
- **YAML-based**: Requiere pipelines definidos en YAML
- **Dependency analysis**: Solo detecta dependencias explicitas
- **Caching limits**: Limitado por CI platform cache limits

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py`
Tests: `scripts/coding/ai/tests/test_ci_pipeline_orchestrator_agent.py`
