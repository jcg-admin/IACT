# JSON Log Schemas

**Proposito**: Definir esquemas para logs JSON temporales (hasta migracion a Cassandra)

## deployment_logs.json

Schema para logs de deployment:

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

Schema para metricas DORA calculadas:

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

Schema para logs de incidentes:

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

## Uso desde scripts

### scripts/dora_metrics.py

```python
import json
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs_data"

def log_deployment(deployment_data):
    log_file = LOGS_DIR / "deployment_logs.json"
    logs = json.loads(log_file.read_text()) if log_file.exists() else []
    logs.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **deployment_data
    })
    log_file.write_text(json.dumps(logs, indent=2))

def log_dora_metrics(metrics_data):
    log_file = LOGS_DIR / "dora_metrics.json"
    logs = json.loads(log_file.read_text()) if log_file.exists() else []
    logs.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **metrics_data
    })
    log_file.write_text(json.dumps(logs, indent=2))

def log_incident(incident_data):
    log_file = LOGS_DIR / "incident_logs.json"
    logs = json.loads(log_file.read_text()) if log_file.exists() else []
    logs.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **incident_data
    })
    log_file.write_text(json.dumps(logs, indent=2))
```

## Migracion a Cassandra

Cuando Cassandra este disponible:

1. Crear tablas correspondientes:
   - deployments
   - dora_metrics
   - incidents

2. Script de migracion:
   - Leer JSONs
   - Validar esquemas
   - Insertar en Cassandra
   - Backup JSONs
   - Limpiar JSONs

3. Actualizar scripts para escribir directo a Cassandra

## Validacion

Todos los logs deben validarse antes de escribir:

- timestamp en formato ISO 8601
- Campos requeridos presentes
- Tipos de datos correctos
- Valores enum validos

## Rotacion de Logs

Mientras se usen JSONs:

- Rotar cuando archivo > 10MB
- Mantener ultimos 30 dias
- Comprimir archivos antiguos
- Backup diario automatico
