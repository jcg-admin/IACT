---
name: PDCAAutomationAgent
description: Agente que implementa ciclos PDCA (Plan-Do-Check-Act) automatizados para optimizacion continua de practicas IA basadas en metricas DORA, ejecutando mejora iterativa de procesos DevOps.
---

# Automation: PDCA Agent

El PDCAAutomationAgent implementa ciclos PDCA (Plan-Do-Check-Act) automatizados para optimizacion continua de practicas de desarrollo basadas en metricas DORA (Deployment Frequency, Lead Time, MTTR, Change Failure Rate).

## Capacidades

### Plan (Planificar)
- Analisis de metricas DORA actuales
- Identificacion de areas de mejora
- Definicion de objetivos medibles
- Generacion de hipotesis de optimizacion
- Priorizacion de iniciativas

### Do (Ejecutar)
- Aplicacion automatica de cambios propuestos
- Ejecucion de experimentos controlados
- Implementacion de mejoras incrementales
- Tracking de intervenciones
- Rollback automatico si falla

### Check (Verificar)
- Medicion de impacto en metricas DORA
- Comparacion baseline vs post-intervencion
- Validacion estadistica de mejoras
- Deteccion de regresiones
- Analisis de efectos secundarios

### Act (Actuar)
- Consolidacion de mejoras exitosas
- Reversion de cambios negativos
- Escalamiento de problemas criticos
- Documentacion de lecciones aprendidas
- Actualizacion de baselines

### Metricas DORA
- **Deployment Frequency**: Frecuencia de deployments
- **Lead Time**: Tiempo commit-to-production
- **MTTR**: Mean Time To Recovery
- **Change Failure Rate**: Tasa de fallos en cambios

## Cuando usar

- **Mejora Continua**: Optimizar procesos DevOps iterativamente
- **Reduccion MTTR**: Acelerar tiempo de recuperacion ante fallos
- **Aumento Deployment Frequency**: Incrementar velocidad de entrega
- **Reduccion Lead Time**: Acortar ciclo commit-to-prod
- **Reduccion Change Failure Rate**: Disminuir fallos en cambios
- **Experimentacion**: Validar hipotesis de mejora con datos

## Como usar

### Iniciar Ciclo PDCA

```bash
python scripts/coding/ai/automation/pdca_agent.py \
  --repo owner/repo \
  --github-token $GITHUB_TOKEN \
  --phase plan \
  --baseline-days 30
```

### Ejecutar Fase Plan

```bash
# Analizar metricas actuales y generar plan
python scripts/coding/ai/automation/pdca_agent.py \
  --phase plan \
  --repo owner/repo \
  --output plan_report.json
```

### Ejecutar Fase Do

```bash
# Aplicar cambios propuestos
python scripts/coding/ai/automation/pdca_agent.py \
  --phase do \
  --plan-file plan_report.json \
  --apply
```

### Ejecutar Fase Check

```bash
# Verificar impacto de cambios
python scripts/coding/ai/automation/pdca_agent.py \
  --phase check \
  --intervention-id pdca-2024-001 \
  --validation-period 7 \
  --threshold 0.05
```

### Ejecutar Fase Act

```bash
# Consolidar o revertir cambios
python scripts/coding/ai/automation/pdca_agent.py \
  --phase act \
  --intervention-id pdca-2024-001 \
  --action apply  # o revert, continue, escalate
```

### Ciclo Completo Automatizado

```bash
# Ejecutar ciclo PDCA completo
python scripts/coding/ai/automation/pdca_agent.py \
  --repo owner/repo \
  --github-token $GITHUB_TOKEN \
  --full-cycle \
  --auto-apply \
  --validation-threshold 0.05
```

## Output esperado

### Fase Plan

```json
{
  "phase": "plan",
  "timestamp": "2025-11-14T12:00:00",
  "current_metrics": {
    "deployment_frequency": 2.3,
    "lead_time_hours": 48.5,
    "mttr_minutes": 85.0,
    "change_failure_rate": 0.12
  },
  "baseline": {
    "period_days": 30,
    "deployments": 69,
    "incidents": 8
  },
  "improvement_hypotheses": [
    {
      "id": "hyp-001",
      "metric": "lead_time_hours",
      "current": 48.5,
      "target": 36.0,
      "action": "Implement automated testing in PR pipeline",
      "expected_impact": -25.8
    }
  ],
  "priority": "high"
}
```

### Fase Check

```json
{
  "phase": "check",
  "intervention_id": "pdca-2024-001",
  "validation_period_days": 7,
  "baseline_metrics": {
    "deployment_frequency": 2.3,
    "lead_time_hours": 48.5
  },
  "post_metrics": {
    "deployment_frequency": 2.8,
    "lead_time_hours": 36.2
  },
  "improvement": {
    "deployment_frequency": "+21.7%",
    "lead_time_hours": "-25.4%"
  },
  "validation": {
    "passed": true,
    "threshold": 0.05,
    "p_value": 0.02
  },
  "recommendation": "APPLY"
}
```

### Fase Act

```json
{
  "phase": "act",
  "decision": "apply",
  "intervention_id": "pdca-2024-001",
  "consolidated": true,
  "new_baseline": {
    "deployment_frequency": 2.8,
    "lead_time_hours": 36.2
  },
  "lessons_learned": [
    "Automated testing reduces lead time significantly",
    "PR validation prevents change failures"
  ],
  "next_cycle": {
    "focus": "mttr_reduction",
    "scheduled": "2025-11-21"
  }
}
```

## Herramientas y dependencias

- **Python 3.11+**
- **GitHub API**: PyGithub
- **Estadisticas**: scipy, numpy
- **Metricas DORA**: Custom collectors
- **Configuracion**: JSON config files

## Buenas practicas

1. **Baseline solido**: Usar al menos 30 dias de datos historicos
2. **Threshold conservador**: Usar validation_threshold >= 0.05
3. **Periodo validacion**: Minimo 7 dias post-intervencion
4. **Rollback rapido**: Revertir si metricas empeoran
5. **Documentar learnings**: Mantener historial de experimentos
6. **Iteracion incremental**: Un cambio a la vez
7. **Auto-aplicacion cautelosa**: Revisar cambios criticos manualmente

## Restricciones

- **Requiere historico**: Necesita datos de al menos 30 dias
- **GitHub dependiente**: Solo funciona con repositorios GitHub
- **Metricas DORA**: Enfocado exclusivamente en metricas DORA
- **Cambios automaticos**: Requiere permisos adecuados para apply
- **Validacion estadistica**: Necesita suficientes muestras

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/pdca_agent.py`
Tests: `scripts/coding/ai/tests/test_pdca_agent.py`
Config: `.pdca_config.json`
History: `.pdca_history.json`
