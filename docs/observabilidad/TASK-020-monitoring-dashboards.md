---
id: TASK-020-monitoring-dashboards
tipo: documentacion_observabilidad
categoria: observabilidad
prioridad: P2
story_points: 3
estado: completado
fecha_inicio: 2025-11-07
fecha_fin: 2025-11-07
asignado: backend-lead
relacionados: ["TASK-014", "RNF-002"]
---

# TASK-020: Monitoring Dashboards

Dashboards de monitoring self-hosted compliant con RNF-002 (NO Prometheus/Grafana).

## Solucion Implementada

**Dashboard:** Django Admin Custom Dashboard (TASK-014)
**URL:** `/api/dora/dashboard/`
**Tecnologia:** Django + Chart.js
**Compliance:** ✅ Self-hosted, NO Prometheus/Grafana

## Metricas Monitoreadas

### DORA Metrics
- Deployment Frequency (deployments/semana)
- Lead Time for Changes (horas)
- Change Failure Rate (%)
- MTTR (horas)
- DORA Classification (Elite/High/Medium/Low)

### System Health
Via health_check.sh (cron cada 5 min):
- Django status
- PostgreSQL connectivity
- MySQL connectivity
- SESSION_ENGINE validation
- Migrations status
- Session table size

## Dashboards Disponibles

### 1. DORA Dashboard (/api/dora/dashboard/)
- **Metricas en tiempo real**
- **Graficos interactivos** (Chart.js)
- **Filtrado por periodo** (7/30/60/90 dias)
- **Clasificacion DORA**

### 2. Django Admin (/admin/)
- **Database metrics** (modelos)
- **Session management**
- **User activity**

## Alertas Visuales

**Implementacion:** Color-coding en dashboard
- Verde: Elite performance
- Azul: High performance
- Naranja: Medium performance
- Rojo: Low performance

## Acceso

```bash
# URL dashboard
http://localhost:8000/api/dora/dashboard/

# Requiere autenticacion staff
@staff_member_required
```

## Monitoring Alternativo (Sin UI)

Para monitoreo programatico sin UI:

```bash
# Health check JSON
./scripts/health_check.sh --json

# DORA metrics API
curl http://localhost:8000/api/dora/metrics/?days=30
```

## Compliance RNF-002

✅ NO usa Prometheus
✅ NO usa Grafana
✅ Dashboard self-hosted (Django)
✅ Chart.js desde CDN (no requiere instalacion)

---

**VERSION:** 1.0.0
**ESTADO:** COMPLETADO
**STORY POINTS:** 3 SP
**FECHA:** 2025-11-07
