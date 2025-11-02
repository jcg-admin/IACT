---
<<<<<<< HEAD
id: DOC-RQ-TRACE-BE
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-02-14
relacionados: ["DOC-REQ-BACKEND", "DOC-REQ-INDEX", "ADR-2025-001"]
---
## Matriz RQ ↔ UC (Backend)
| RQ | UC asociados | Comentario |
|----|--------------|------------|
| RQ-BE-001 | UC-BE-DASH-001, UC-BE-DASH-003 | Dashboards deben mostrar KPIs diarios y alertas. |
| RQ-BE-002 | UC-BE-IVR-002 | Integración con eventos IVR para clasificar llamadas. |
| RQ-BE-003 | UC-BE-REP-004 | Reportes históricos exportables en CSV y Parquet. |
=======
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
>>>>>>> origin/docs

## Matriz UC ↔ TC
| UC | TC asociados | Comentario |
|----|--------------|------------|
<<<<<<< HEAD
| UC-BE-DASH-001 | TC-BE-USR-010, TC-BE-USR-011 | Validación de filtros por rango horario y cola. |
| UC-BE-DASH-003 | TC-BE-ADM-005 | Admin define widgets visibles por rol RBAC. |
| UC-BE-REP-004 | TC-BE-EXP-002, TC-BE-EXP-003 | Compara totales contra datos de control en PostgreSQL. |
=======
| UC-DASH-001 | TC-USR-010, TC-USR-011 | Validación de filtros por rango horario y cola. |
| UC-DASH-003 | TC-ADM-005 | Admin define widgets visibles por rol RBAC. |
| UC-REP-004 | TC-EXP-002, TC-EXP-003 | Compara totales contra datos de control en PostgreSQL. |
>>>>>>> origin/docs

## Matriz UC ↔ Endpoint o Módulo
| UC | Endpoint/Módulo | Comentario |
|----|-----------------|------------|
<<<<<<< HEAD
| UC-BE-DASH-001 | api.analytics.views.DashboardSummaryView | Endpoint DRF para KPIs en tiempo real. |
| UC-BE-IVR-002 | api.ivr.router.CallTransferService | Servicio de lectura desde MariaDB readonly. |
| UC-BE-REP-004 | api.reports.etl.MonthlyExportJob | Tarea APScheduler que alimenta descargas. |

> Consulta la matriz corporativa en [`../../requisitos/trazabilidad.md`](../../requisitos/trazabilidad.md) para alinear dependencias transversales.
=======
| UC-DASH-001 | api.analytics.views.DashboardSummaryView | Endpoint DRF para KPIs en tiempo real. |
| UC-IVR-002 | api.ivr.router.CallTransferService | Servicio de lectura desde MariaDB readonly. |
| UC-REP-004 | api.reports.etl.MonthlyExportJob | Tarea APScheduler que alimenta descargas. |
>>>>>>> origin/docs
