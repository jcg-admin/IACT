---
title: Análisis: Restricciones del Proyecto vs Mejoras Propuestas al Middleware
date: 2025-11-13
domain: backend
status: active
---

# Análisis: Restricciones del Proyecto vs Mejoras Propuestas al Middleware

**Fecha**: 2025-11-11
**Versión**: 1.0
**Estado**: Análisis de Compliance

---

## Resumen Ejecutivo

De las **5 fases de mejora propuestas**, hay **2 CONFLICTOS** con restricciones del proyecto:

| Mejora | Estado | Conflicto |
|--------|--------|-----------|
| Fase 1: Caching con Redis | **DUDOSO** | Restricción "NO Redis" aplica solo a sesiones, pero necesita clarificación |
| Fase 2: DRF Permission Classes | **OK** | Sin conflictos |
| Fase 3: Logging + Prometheus | **CONFLICTO PARCIAL** | Prometheus podría violar "NO servicios externos de monitoreo" |
| Fase 4: Django Middleware | **OK** | Sin conflictos |
| Fase 5: Object-Level Permissions | **OK** | Sin conflictos |

---

## Análisis Detallado

### Restricciones Críticas del Proyecto

**Fuente**: `docs/backend/requisitos/restricciones_y_lineamientos.md`

```yaml
RESTRICCIONES CRÍTICAS (NO NEGOCIABLES):

1. NO Email (línea 47-59):
   - PROHIBIDO: SMTP, SendGrid, Mailgun, cualquier servicio de email
   - OK: Solo buzón interno (InternalMessage)

2. Sesiones en BD, NO Redis/Memcached (línea 75-103):
   - PROHIBIDO: Redis para sesiones
   - PROHIBIDO: Memcached para sesiones
   - OK OBLIGATORIO: Sesiones en base de datos MySQL/PostgreSQL

3. BD IVR READONLY (línea 106-143):
   - PROHIBIDO: INSERT, UPDATE, DELETE en BD IVR
   - OK: Solo SELECT

4. NO Real-time updates (línea 147-177):
   - PROHIBIDO: WebSockets, SSE, polling automático
   - OK: ETL cada 6-12 horas + refresh manual (F5)

5. NO Sentry (ADR-002 línea 32):
   - PROHIBIDO: Servicios externos de monitoreo
   - OK: Logging local con archivos rotativos

6. NO Código peligroso:
   - PROHIBIDO: eval(), exec(), pickle.load()

7. NO WebSockets/SSE:
   - PROHIBIDO: Channels, EventSource
```

---

## Análisis por Fase de Mejora

### Fase 1: Caching con Redis - **DUDOSO** [EN_PROGRESO]

**Propuesta Original**:
```python
# settings/base.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

**Restricción Aplicable**:
```yaml
NO PROHIBIDO:
  - Redis para sesiones
  - Memcached para sesiones

OK OBLIGATORIO:
  - Sesiones en base de datos MySQL
```

**Análisis**:
- [OK] La restricción dice "NO Redis **para sesiones**", no "NO Redis en general"
- [NO] Sin embargo, la justificación es: "Infraestructura del cliente NO tiene Redis"
- 🤔 Si la infraestructura NO tiene Redis, entonces Redis para cache TAMPOCO está disponible

**Veredicto**: **CONFLICTO** - No se puede usar Redis porque no existe en infraestructura

**Alternativa Propuesta**:
```python
# settings/base.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',  # [OK] Usar BD en lugar de Redis
        'LOCATION': 'permissions_cache_table',
        'TIMEOUT': 300,  # 5 minutos
    }
}
```

**Comandos**:
```bash
# Crear tabla de cache en BD
python manage.py createcachetable permissions_cache_table
```

**Pros de usar DB cache**:
- [OK] Cumple con infraestructura disponible
- [OK] No requiere servicios adicionales
- [OK] Funciona con PostgreSQL/MySQL existente
- [OK] Persistente (sobrevive reinicios)

**Contras de usar DB cache**:
- [NO] Más lento que Redis (~50ms vs ~1ms)
- [NO] Más carga en BD (pero tolerable para permisos)
- [OK] PERO: Aún es 10x más rápido que queries individuales

**Métricas esperadas**:
- Sin cache: 5+ queries, ~250ms
- Con DB cache: 1 query cache, ~50ms (5x mejor)
- Con Redis cache (si estuviera disponible): ~1ms (250x mejor)

---

### Fase 2: DRF Permission Classes - **OK** [OK]

**Propuesta**:
```python
from rest_framework.permissions import BasePermission

class HasCapacidad(BasePermission):
    def has_permission(self, request, view):
        return PermisoService.usuario_tiene_permiso(...)
```

**Restricciones Aplicables**: Ninguna

**Veredicto**: **SIN CONFLICTOS**

**Justificación**:
- [OK] Solo clases Python, no usa servicios externos
- [OK] No modifica restricciones de seguridad
- [OK] Compatible con arquitectura Django/DRF
- [OK] No requiere infraestructura adicional

---

### Fase 3: Logging + Métricas Prometheus - **CONFLICTO PARCIAL** 🟠

**Propuesta Original**:
```python
# Logging estructurado - OK [OK]
logger = logging.getLogger('permissions')
logger.info("Acceso permitido", extra=log_context)

# Métricas Prometheus - CONFLICTO [NO]
from prometheus_client import Counter
permission_checks_total = Counter('permission_checks_total', ...)
```

**Restricción Aplicable**:
```yaml
NO Sentry (ADR-002):
  - PROHIBIDO: Servicios externos de monitoreo
  - PROHIBIDO: Sentry, New Relic, Datadog
  - OK: Logging local con archivos rotativos
```

**Análisis**:

#### Logging Estructurado JSON - **OK** [OK]

**Sin conflictos**:
```python
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',  # [OK] Local
            'filename': 'logs/permissions.log',
            'formatter': 'json',
        },
    },
}
```

[OK] Archivos locales rotativos (cumple restricción)
[OK] JSON parseable (no requiere servicio externo)
[OK] Retención configurable (30/90 días según restricción)

#### Prometheus Metrics - **CONFLICTO** [NO]

**Problema**:
- [NO] Prometheus es un "servicio externo de monitoreo"
- [NO] Requiere infraestructura adicional (Prometheus server)
- [NO] Similar a Sentry/Datadog en concepto

**Veredicto**: **VIOLA** restricción de "NO servicios externos de monitoreo"

**Alternativa Propuesta - Métricas en DB**:
```python
# models.py
class PermissionMetric(models.Model):
    """Métricas de permisos almacenadas en BD."""

    timestamp = models.DateTimeField(auto_now_add=True)
    capacidad = models.CharField(max_length=200)
    resultado = models.CharField(
        max_length=20,
        choices=[("permitido", "Permitido"), ("denegado", "Denegado")]
    )
    duration_ms = models.FloatField(help_text="Duración en milisegundos")
    cache_hit = models.BooleanField(default=False)
    user_id = models.IntegerField(null=True)

    class Meta:
        db_table = "permission_metrics"
        indexes = [
            models.Index(fields=['timestamp', 'capacidad']),
            models.Index(fields=['resultado']),
        ]

# services.py
class PermisoService:

    @staticmethod
    def usuario_tiene_permiso(usuario_id: int, capacidad_requerida: str) -> bool:
        start_time = time.time()

        # ... verificación de permisos ...

        # Registrar métrica en BD (async para no impactar performance)
        duration_ms = (time.time() - start_time) * 1000

        # Solo guardar cada N verificaciones para no saturar BD
        if random.random() < 0.1:  # 10% sampling
            PermissionMetric.objects.create(
                capacidad=capacidad_requerida,
                resultado="permitido" if resultado else "denegado",
                duration_ms=duration_ms,
                cache_hit=cached_result is not None,
                user_id=usuario_id
            )

        return resultado
```

**Consultas de métricas**:
```python
# Management command: python manage.py permission_stats
from django.db.models import Avg, Count, Max

# Cache hit rate últimas 24h
metrics = PermissionMetric.objects.filter(
    timestamp__gte=timezone.now() - timedelta(days=1)
).aggregate(
    total=Count('id'),
    cache_hits=Count('id', filter=Q(cache_hit=True)),
    avg_duration=Avg('duration_ms'),
    max_duration=Max('duration_ms'),
)

cache_hit_rate = (metrics['cache_hits'] / metrics['total']) * 100
print(f"Cache Hit Rate: {cache_hit_rate:.2f}%")
print(f"Avg Duration: {metrics['avg_duration']:.2f}ms")

# Top capacidades verificadas
top_capacidades = PermissionMetric.objects.values('capacidad').annotate(
    count=Count('id')
).order_by('-count')[:10]
```

**Ventajas sobre Prometheus**:
- [OK] No requiere infraestructura externa
- [OK] Cumple con restricciones del proyecto
- [OK] Queries con Django ORM
- [OK] Puede exportarse a CSV para análisis
- [OK] Integrado con sistema de auditoría

**Desventajas**:
- [NO] No tiene dashboards como Grafana
- [NO] Queries manuales vs visualización automática
- [NO] Sampling necesario para no saturar BD

---

### Fase 4: Django Middleware Real - **OK** [OK]

**Propuesta**:
```python
class PermissionsMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            request.user_capacidades = cache.get(f"caps:{request.user.id}")
        return self.get_response(request)
```

**Restricciones Aplicables**: Ninguna

**Veredicto**: **SIN CONFLICTOS**

**Justificación**:
- [OK] Middleware estándar de Django
- [OK] No requiere servicios externos
- [OK] Solo agrega contexto al request
- [OK] Compatible con restricciones de seguridad

---

### Fase 5: Object-Level Permissions - **OK** [OK]

**Propuesta**:
```python
class HasCapacidad(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verificar permiso sobre objeto específico
        return obj.owner == request.user or request.user.is_staff
```

**Restricciones Aplicables**: Ninguna

**Veredicto**: **SIN CONFLICTOS**

**Justificación**:
- [OK] Feature estándar de DRF
- [OK] No requiere infraestructura adicional
- [OK] Solo lógica de negocio en Python

---

## Resumen de Compliance

### Fases Aprobadas (3/5)

| Fase | Estado | Requiere Modificación |
|------|--------|----------------------|
| **Fase 2**: DRF Permission Classes | [OK] OK | No |
| **Fase 4**: Django Middleware | [OK] OK | No |
| **Fase 5**: Object-Level Permissions | [OK] OK | No |

### Fases con Modificaciones Requeridas (2/5)

| Fase | Conflicto | Alternativa Propuesta |
|------|-----------|----------------------|
| **Fase 1**: Caching | Redis no disponible | Usar `DatabaseCache` en lugar de `RedisCache` |
| **Fase 3**: Métricas | Prometheus = servicio externo | Métricas en BD con sampling, queries manuales |

---

## Propuesta Final Ajustada

### Fase 1 (Modificada): Caching con Database Backend

```python
# settings/base.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'permissions_cache_table',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 10000,  # Límite de entradas
        }
    }
}

# Crear tabla
# python manage.py createcachetable permissions_cache_table
```

**Performance esperado**:
- Reducción de queries: 5+ → 1 (cache hit)
- Latencia: 250ms → 50ms (5x mejor)
- Cache hit rate esperado: 90%+

### Fase 3 (Modificada): Logging + Métricas en BD

```python
# Solo logging estructurado JSON (sin Prometheus)
LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'permissions_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/permissions.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'permissions': {
            'handlers': ['permissions_file'],
            'level': 'INFO',
        },
    },
}

# Métricas simples en BD (ver modelo PermissionMetric arriba)
# Consultas con management command: python manage.py permission_stats
```

---

## Recomendación Final

### Implementar en Este Orden

**Quick Wins (Semana 1)**:
1. [OK] Fase 2: DRF Permission Classes (1-2 horas)
   - Sin conflictos
   - Mejora inmediata en legibilidad
   - Reduce boilerplate 50%

**Medium Impact (Semana 2)**:
2. [OK] Fase 1 (modificada): Database Cache (2-3 horas)
   - Requiere ajuste (DB en lugar de Redis)
   - Mejora performance 5x
   - Cache hit rate 90%+

3. [OK] Fase 3 (modificada): Logging JSON (1 hora)
   - Solo logging estructurado
   - Sin Prometheus (usar métricas BD)
   - Cumple restricciones

**Future Enhancements (Mes 1)**:
4. [OK] Fase 4: Django Middleware (2 horas)
   - Sin conflictos
   - Context global útil

5. [OK] Fase 5: Object-Level Permissions (según necesidad)
   - Implementar cuando se requiera
   - No urgente

---

## Conclusión

**2 de 5 fases** requieren modificaciones para cumplir con restricciones:

1. **Caching**: Usar `DatabaseCache` en lugar de `RedisCache` (infraestructura no disponible)
2. **Métricas**: Usar modelo Django + queries en lugar de Prometheus (no servicios externos)

Las otras **3 fases** están 100% OK sin modificaciones.

**Impacto en beneficios**:
- [OK] Aún se logra 5x mejora en performance (con DB cache vs sin cache)
- [OK] Logging estructurado completo (JSON parseable)
- [OK] DRF integration completa
- [NO] Sin dashboards Grafana (queries manuales en su lugar)
- [NO] Cache más lento (50ms vs 1ms con Redis, pero aún 5x mejor que sin cache)

**Veredicto**: Las mejoras **SIGUEN SIENDO VALIOSAS** con las modificaciones propuestas.

---

**Fin del análisis**
