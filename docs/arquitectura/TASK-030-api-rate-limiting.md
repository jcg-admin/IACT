---
id: TASK-030-api-rate-limiting
tipo: documentacion_arquitectura
categoria: arquitectura
prioridad: P3
story_points: 3
estado: completado
fecha_inicio: 2025-11-07
fecha_fin: 2025-11-07
asignado: backend-lead
relacionados: ["TASK-031"]
---

# TASK-030: API Rate Limiting

Implementacion de rate limiting en API endpoints para prevenir abuso.

## Implementacion

**Framework:** Django REST Framework Throttling

**Throttle Classes:**
- BurstRateThrottle: 100 requests/min (anonimo)
- SustainedRateThrottle: 1000 requests/hour (anonimo)
- UserBurstRateThrottle: 200 requests/min (autenticado)
- UserSustainedRateThrottle: 5000 requests/hour (autenticado)

## Configuracion

```python
# dora_metrics/views.py
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def dora_metrics_summary(request):
    ...
```

## Response Headers

Cuando se aplica throttling:
- `X-RateLimit-Limit`: Limite de requests
- `X-RateLimit-Remaining`: Requests restantes
- `X-RateLimit-Reset`: Timestamp de reset

Status code: **429 Too Many Requests**

## Testing

```bash
# Test rate limiting
for i in {1..150}; do curl http://localhost:8000/api/dora/metrics/; done

# Deberia retornar 429 despues de 100 requests
```

---

**VERSION:** 1.0.0
**ESTADO:** COMPLETADO
**STORY POINTS:** 3 SP
**FECHA:** 2025-11-07
