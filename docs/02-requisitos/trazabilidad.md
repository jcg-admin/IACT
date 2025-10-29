---
id: DOC-RQ-TRACE
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-02-14
relacionados: ["RQ-ANL-001", "UC-DASH-003", "TC-USR-010", "ADR-2025-001"]
---
## Matriz RQ ↔ UC
| RQ | UC asociados | Comentario |
|----|--------------|------------|
| RQ-ANL-001 | UC-DASH-001, UC-DASH-003 | Dashboards deben mostrar KPIs diarios y alertas. |
| RQ-ANL-002 | UC-IVR-002 | Integración con eventos IVR para clasificar llamadas. |
| RQ-ANL-003 | UC-REP-004 | Reportes históricos exportables en CSV y Parquet. |

## Matriz UC ↔ TC
| UC | TC asociados | Comentario |
|----|--------------|------------|
| UC-DASH-001 | TC-USR-010, TC-USR-011 | Validación de filtros por rango horario y cola. |
| UC-DASH-003 | TC-ADM-005 | Admin define widgets visibles por rol RBAC. |
| UC-REP-004 | TC-EXP-002, TC-EXP-003 | Compara totales contra datos de control en PostgreSQL. |

## Matriz UC ↔ Endpoint o Módulo
| UC | Endpoint/Módulo | Comentario |
|----|-----------------|------------|
| UC-DASH-001 | api.analytics.views.DashboardSummaryView | Endpoint DRF para KPIs en tiempo real. |
| UC-IVR-002 | api.ivr.router.CallTransferService | Servicio de lectura desde MariaDB readonly. |
| UC-REP-004 | api.reports.etl.MonthlyExportJob | Tarea APScheduler que alimenta descargas. |
