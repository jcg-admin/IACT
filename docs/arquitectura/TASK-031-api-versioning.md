---
id: TASK-031-api-versioning
tipo: documentacion_arquitectura
categoria: arquitectura
prioridad: P3
story_points: 3
estado: completado
fecha_inicio: 2025-11-07
fecha_fin: 2025-11-07
asignado: backend-lead
relacionados: ["TASK-030"]
---

# TASK-031: API Versioning

Sistema de versionado de APIs con deprecation policies.

## Estrategia de Versionado

**Metodo:** URL Path Versioning
**Formato:** `/api/v1/`, `/api/v2/`

## Implementacion

### URLs v1 (Actual)

```python
# callcentersite/urls.py
urlpatterns = [
    path('api/v1/dora/', include('dora_metrics.urls')),  # v1
]
```

### URLs v2 (Futuro)

```python
# Para cambios breaking:
urlpatterns = [
    path('api/v1/dora/', include('dora_metrics.urls_v1')),  # Legacy
    path('api/v2/dora/', include('dora_metrics.urls_v2')),  # New
]
```

## Deprecation Policy

**Timeline:**
1. **v2 Release:** v1 marcada como deprecated
2. **+6 meses:** Warning en responses v1
3. **+12 meses:** v1 eliminada

**Warning Header:**
```
Deprecation: true
Sunset: 2026-11-07T00:00:00Z
Link: <https://docs.iact.com/api/v2>; rel="successor-version"
```

## Backward Compatibility

**Reglas:**
- Nuevos campos: OK (no breaking)
- Cambiar tipo de campo: NO (breaking → v2)
- Eliminar campo: NO (breaking → v2)
- Renombrar campo: NO (breaking → v2)

## Documentacion Versionada

**Ubicacion:** docs/api/
- docs/api/v1/README.md
- docs/api/v2/README.md

**Changelog:** docs/api/CHANGELOG.md

---

**VERSION:** 1.0.0
**ESTADO:** COMPLETADO
**STORY POINTS:** 3 SP
**FECHA:** 2025-11-07
