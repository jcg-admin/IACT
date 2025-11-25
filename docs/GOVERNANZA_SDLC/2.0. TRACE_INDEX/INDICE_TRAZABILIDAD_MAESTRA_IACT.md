# INDICE_TRAZABILIDAD_MAESTRA_IACT.md

## Índice Global de Trazabilidad del Proyecto IACT

| ID Artefacto | Tipo de Requisito | Descripción Breve | Artefacto de Definición (Nivel 1-4) | Artefacto de Implementación (Nivel 5) |
| :--- | :--- | :--- | :--- | :--- |
| **BR-NEG-001** | Negocio (Dato) | Consistencia de datos para el Dashboard; solo llamadas finalizadas válidas alimentan métricas. | `PRODUCTO_DASHBOARD_ANALYTICS/1.0. CATALOGO_BR/CATALOGO_BR.md` | `api/callcentersite/src/callcentersite/apps/llamadas/services.py` (validaciones y filtros de estado) |
| **BR-SEG-007** | Seguridad (Autorización) | El Agente debe tener la capacidad `operaciones.llamadas.registrar` para ejecutar UC-010. | `PRODUCTO_DASHBOARD_ANALYTICS/1.0. CATALOGO_BR/CATALOGO_BR_SEGURIDAD.md` | `api/callcentersite/src/callcentersite/apps/permissions/services.py` (`PermisoService.usuario_tiene_permiso`) |
| **BR-NEG-002** | Negocio (Versión) | Las políticas se versionan de forma inmutable y requieren nueva versión en cada cambio. | `PRODUCTO_DASHBOARD_ANALYTICS/1.0. CATALOGO_BR/CATALOGO_BR.md` | `api/callcentersite/src/callcentersite/apps/politicas/services.py` (`PoliticaService.nueva_version`) |
| **BR-SEG-009** | Seguridad (Publicación) | Solo usuarios autorizados pueden publicar una Política vigente. | `PRODUCTO_DASHBOARD_ANALYTICS/1.0. CATALOGO_BR/CATALOGO_BR_SEGURIDAD.md` | `api/callcentersite/src/callcentersite/apps/politicas/views.py` (acción de publicación) |
| **RNF-AUD-001** | No Funcional (Auditoría) | Registro inmutable de acciones críticas con metadata de contexto. | `PRODUCTO_DASHBOARD_ANALYTICS/2.0. REQUISITOS/RNF/RNF-AUD-001_AUDITORIA.md` | `api/callcentersite/src/callcentersite/apps/audit/` (`AuditLog`, `audit_action`) |
| **RNF-PROC-001** | Proceso (Gobernanza SDLC) | Uso estandarizado y auditable de las fases del SDLC sin agentes IA. | `GOVERNANZA_SDLC/1.0. REQUISITOS/RNF/RNF-PROC-001_PROCESO_SDLC.md` | Guías de proceso y scripts de soporte (`scripts/run_all_tests.sh`, CI/CD). |
| **RNF-PROC-002** | Proceso (Métricas internas) | Recolección y publicación de métricas básicas de despliegue e incidentes (sin esquema DORA). | `GOVERNANZA_SDLC/1.0. REQUISITOS/RNF/RNF-PROC-002_METRICAS_PROCESO.md` | `logs_data/` y `docs/scripts/metrics_and_reporting.md` |
| **ADR-AI-020** | Arquitectura (Validación de planes) | Uso de 5 rutas de razonamiento con consenso ≥80% para aprobar planes SDLC. | `docs/gobernanza/adr/ADR-AI-020-plan-validation-consensus.md` | `scripts/coding/ai/sdlc/plan_validation_agent.py` y `scripts/coding/tests/ai/sdlc/test_plan_validation_agent.py` |
| **UC-010** | Funcional (CU Principal) | Registrar una nueva llamada entrante y dejar trazabilidad de agente y auditoría. | `PRODUCTO_DASHBOARD_ANALYTICS/2.0. REQUISITOS/UC-010_REGISTRAR_LLAMADA_ENTRANTE_FINAL.md` | `api/callcentersite/src/callcentersite/apps/llamadas/services.py` (`LlamadaService.registrar_llamada_entrante`) |

---

## Cierre del Estándar de Trazabilidad IACT

Todos los artefactos fundacionales requeridos para asegurar trazabilidad bidireccional están documentados y enlazados con su implementación en código.

### Resumen de Entregables

| Directorio | Archivo | Nivel de Trazabilidad IACT | Propósito |
| :--- | :--- | :--- | :--- |
| **PRODUCTO_DASHBOARD_ANALYTICS/** | `CATALOGO_BR.md` | **Nivel 1 (BR)** | Reglas de negocio funcionales. |
| **PRODUCTO_DASHBOARD_ANALYTICS/** | `CATALOGO_BR_SEGURIDAD.md` | **Nivel 1 (BR-SEG)** | Reglas de negocio de autorización. |
| **PRODUCTO_DASHBOARD_ANALYTICS/** | `RNF-AUD-001_AUDITORIA.md` | **Nivel 3 (RNF)** | Requisito de auditoría forense. |
| **PRODUCTO_DASHBOARD_ANALYTICS/** | `UC-010_REGISTRAR_LLAMADA_ENTRANTE_FINAL.md` | **Nivel 4 (UC)** | Caso de uso principal del dominio. |
| **PRODUCTO_DASHBOARD_ANALYTICS/** | `COMPONENTES_BASE.md` | **Referencia (Soporte)** | Guía de reutilización de autenticación, permisos, auditoría y métricas para el dashboard. |
| **GOVERNANZA_SDLC/** | `RNF-PROC-001_PROCESO_SDLC.md` | **Nivel 3 (RNF-PROC)** | Gobernanza del proceso SDLC ejecutado por el equipo. |
| **GOVERNANZA_SDLC/** | `RNF-PROC-002_METRICAS_PROCESO.md` | **Nivel 3 (RNF-PROC)** | Procedimiento para métricas internas y reporting. |
| **GOVERNANZA_SDLC/** | `INDICE_TRAZABILIDAD_MAESTRA_IACT.md` | **Nivel 0 (Índice)** | Mapa bidireccional de requisitos y código. |

El proyecto cumple con el estándar de trazabilidad del SDLC (IACT) al conectar reglas de negocio, requisitos no funcionales, casos de uso y servicios implementados, facilitando auditoría y evolución controlada.
