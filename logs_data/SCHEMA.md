# JSON Log Schemas (estado manual)

**Propósito**: describir los esquemas utilizados para los JSON temporales mientras no exista automatización.

> Automatización pendiente: la generación y rotación se hace manualmente hasta que exista un script oficial.

## deployment_logs.json

```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "deployment_id": "deploy-12345",
  "environment": "production|staging|development",
  "version": "v1.2.3",
  "commit_sha": "abc123def456",
  "status": "success|failed|rolled_back",
  "duration_seconds": 300,
  "deployed_by": "user@example.com",
  "services": ["backend-api", "worker"],
  "rollback_version": "v1.2.2",
  "notes": "Deployment notes"
}
```

## dora_metrics.json

```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "metric_period": "daily|weekly|monthly",
  "deployment_frequency": {
    "count": 5,
    "per_day": 5.0,
    "target": "daily"
  },
  "lead_time_for_changes": {
    "average_hours": 3.5,
    "median_hours": 3.0,
    "p95_hours": 6.0,
    "target_hours": 4.0
  },
  "mean_time_to_recover": {
    "average_hours": 0.75,
    "median_hours": 0.5,
    "target_hours": 1.0
  },
  "change_failure_rate": {
    "total_deployments": 100,
    "failed_deployments": 3,
    "rate_percent": 3.0,
    "target_percent": 5.0
  }
}
```

## incident_logs.json

```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "incident_id": "INC-12345",
  "severity": "critical|high|medium|low",
  "status": "open|investigating|resolved|closed",
  "title": "Service degradation in backend API",
  "description": "Detailed description of incident",
  "affected_services": ["backend-api"],
  "detected_at": "2025-01-15T14:25:00Z",
  "resolved_at": "2025-01-15T15:00:00Z",
  "mttr_minutes": 35,
  "root_cause": "Database connection pool exhausted",
  "resolution": "Increased connection pool size",
  "assigned_to": "oncall@example.com",
  "related_deployments": ["deploy-12344"]
}
```

## Procedimiento manual
1. Edita los JSON con un editor que preserve el formato (`jq`, `python -m json.tool`).
2. Anota en el commit la procedencia de los datos.
3. Mantén backups comprimidos si los archivos superan los 10 MB.
4. Cada vez que se actualicen estos archivos, documenta el contexto en `docs/analisis/` o `docs/backend_analisis/`.

## Próximos pasos (futuros)
- Diseñar un script dedicado para recopilar métricas.
- Definir rotación automática (cron o workflow) cuando se implemente la automatización.
