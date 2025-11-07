---
id: TASK-029-data-quality-framework
tipo: documentacion_arquitectura
categoria: arquitectura
prioridad: P3
story_points: 5
estado: completado
fecha_inicio: 2025-11-07
fecha_fin: 2025-11-07
asignado: backend-lead
relacionados: ["TASK-028"]
---

# TASK-029: Data Quality Framework

Framework de calidad de datos con validaciones automaticas.

## Arquitectura

```
Data Input → Validators → Quality Checks → Alerts/Logs
     ↓           ↓              ↓              ↓
   API      Schema        Profiling       Signals
  File      Range         Anomalies        Logs
  ETL       Nulls         Consistency
```

## Validaciones Implementadas

### 1. Schema Validation

```python
from pydantic import BaseModel, validator

class DORAMetricSchema(BaseModel):
    cycle_id: str
    feature_id: str
    phase_name: str
    decision: str
    duration_seconds: float

    @validator('duration_seconds')
    def validate_duration(cls, v):
        if v < 0:
            raise ValueError('duration must be positive')
        if v > 86400:  # >24 horas
            raise ValueError('duration too long')
        return v
```

### 2. Range Validation

```python
def validate_metric_ranges(metric):
    """Validate metric values are within expected ranges."""
    validations = []

    # Lead time should be < 7 days (604800 seconds)
    if metric.phase_name == 'deployment':
        if metric.duration_seconds > 604800:
            validations.append({
                'field': 'duration_seconds',
                'issue': 'exceeds_expected_range',
                'value': metric.duration_seconds,
                'expected': '< 604800 (7 days)'
            })

    return validations
```

### 3. Null Checks

```python
required_fields = ['cycle_id', 'feature_id', 'phase_name']
for field in required_fields:
    if getattr(metric, field) is None:
        raise ValueError(f'{field} cannot be null')
```

### 4. Consistency Checks

```python
# Verificar que cycle_id existe
if not DORAMetric.objects.filter(cycle_id=metric.cycle_id).exists():
    # Primer metric del ciclo - OK
    pass
else:
    # Verificar consistency con ciclo existente
    existing = DORAMetric.objects.filter(cycle_id=metric.cycle_id).first()
    if existing.feature_id != metric.feature_id:
        raise ValueError('Inconsistent feature_id for cycle')
```

## Data Profiling

### Statistics

```python
def profile_dataset(queryset):
    """Generate data quality profile."""
    return {
        'total_records': queryset.count(),
        'null_counts': {
            field: queryset.filter(**{f'{field}__isnull': True}).count()
            for field in ['cycle_id', 'feature_id', 'phase_name']
        },
        'value_ranges': {
            'duration_seconds': {
                'min': queryset.aggregate(min=Min('duration_seconds'))['min'],
                'max': queryset.aggregate(max=Max('duration_seconds'))['max'],
                'avg': queryset.aggregate(avg=Avg('duration_seconds'))['avg'],
            }
        },
        'distinct_counts': {
            'phase_name': queryset.values('phase_name').distinct().count(),
        }
    }
```

## Anomaly Detection

### Simple Statistical Method

```python
def detect_anomalies(metrics):
    """Detect anomalies using IQR method."""
    durations = [m.duration_seconds for m in metrics]

    q1 = np.percentile(durations, 25)
    q3 = np.percentile(durations, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    anomalies = [m for m in metrics
                 if m.duration_seconds < lower_bound
                 or m.duration_seconds > upper_bound]

    return anomalies
```

## Quality Scores

```python
def calculate_quality_score(dataset):
    """Calculate overall quality score (0-100)."""
    score = 100

    # Penalize nulls
    null_rate = dataset['null_counts']['cycle_id'] / dataset['total_records']
    score -= null_rate * 20

    # Penalize anomalies
    anomaly_rate = len(detect_anomalies()) / dataset['total_records']
    score -= anomaly_rate * 30

    # Penalize schema violations
    schema_violations = validate_all_schemas()
    score -= len(schema_violations) / dataset['total_records'] * 50

    return max(0, score)
```

## Alertas de Calidad

```python
from dora_metrics.alerts import warning_alert

def check_data_quality():
    """Check data quality and alert if low."""
    score = calculate_quality_score(get_recent_data())

    if score < 70:
        warning_alert.send(
            sender=None,
            message=f"Data quality score low: {score}/100",
            context={'score': score, 'threshold': 70}
        )
```

## Reporting

### Quality Dashboard

Agregar a DORA dashboard:
```python
# dora_metrics/views.py
def dora_dashboard(request):
    # ... existing code ...

    quality_score = calculate_quality_score(metrics)

    context = {
        # ... existing metrics ...
        'data_quality_score': quality_score,
    }
```

---

**VERSION:** 1.0.0
**ESTADO:** COMPLETADO
**STORY POINTS:** 5 SP
**FECHA:** 2025-11-07
