---
id: INDEX
tipo: indice
categoria: documentacion
version: 2.0.0
fecha_actualizacion: 2025-11-07
mantenedor: arquitecto-senior
---

# INDICE COMPLETO - Documentacion del Proyecto IACT

Indice completo de toda la documentacion del proyecto IACT, organizado por categoria y dominio.

**Version:** 2.0.0
**Ultima actualizacion:** 2025-11-07
**Total archivos:** 297 documentos .md
**Estructura:** Por dominio (backend, frontend, infrastructure) + transversal

---

## Documentos Principales

### Vision y Alcance

- [README.md](README.md) - Punto de entrada principal
- [INDICE.md](INDICE.md) - Indice navegable anterior (deprecado, usar INDEX.md)

### Proyecto

- [docs/proyecto/](proyecto/) - Documentacion de gestion del proyecto
  - [ONBOARDING.md](proyecto/ONBOARDING.md) - Guia de onboarding con AI guidelines
  - [TASK-012-ai-guidelines-onboarding.md](proyecto/TASK-012-ai-guidelines-onboarding.md)
  - [TAREAS_ACTIVAS.md](../TAREAS_ACTIVAS.md) (raiz)
  - [PLAN_EJECUCION_COMPLETO.md](../PLAN_EJECUCION_COMPLETO.md) (raiz)

---

## Arquitectura y Diseño

### Arquitectura Transversal

- [docs/arquitectura/](arquitectura/) - Arquitectura general del sistema
  - [STORAGE_ARCHITECTURE.md](arquitectura/STORAGE_ARCHITECTURE.md) - Arquitectura de almacenamiento (MySQL + Cassandra)
  - [OBSERVABILITY_LAYERS.md](arquitectura/OBSERVABILITY_LAYERS.md) - Capas de observabilidad
  - [lineamientos_codigo.md](arquitectura/lineamientos_codigo.md)
  - **Tareas completadas:**
    - [TASK-010-logging-estructurado-json.md](arquitectura/TASK-010-logging-estructurado-json.md)
    - [TASK-011-data-centralization-layer.md](arquitectura/TASK-011-data-centralization-layer.md)

### ADRs (Architecture Decision Records)

- [docs/adr/](adr/) - Decisiones arquitectonicas documentadas
  - [plantilla_adr.md](adr/plantilla_adr.md)
  - [ADR_008_cpython_features_vs_imagen_base.md](adr/ADR_008_cpython_features_vs_imagen_base.md)
  - [ADR_009_distribucion_artefactos_strategy.md](adr/ADR_009_distribucion_artefactos_strategy.md)
  - [ADR_010_organizacion_proyecto_por_dominio.md](adr/ADR_010_organizacion_proyecto_por_dominio.md)
  - [ADR_011_frontend_modular_monolith.md](adr/ADR_011_frontend_modular_monolith.md)
  - [ADR_012_redux_toolkit_state_management.md](adr/ADR_012_redux_toolkit_state_management.md)
  - [ADR_013_webpack_bundler.md](adr/ADR_013_webpack_bundler.md)
  - [ADR_014_testing_strategy_jest_testing_library.md](adr/ADR_014_testing_strategy_jest_testing_library.md)
  - [adr_2025_001_vagrant_mod_wsgi.md](adr/adr_2025_001_vagrant_mod_wsgi.md)
  - [adr_2025_002_suite_calidad_codigo.md](adr/adr_2025_002_suite_calidad_codigo.md)
  - [adr_2025_003_dora_sdlc_integration.md](adr/adr_2025_003_dora_sdlc_integration.md)
  - [adr_2025_004_centralized_log_storage.md](adr/adr_2025_004_centralized_log_storage.md)

---

## Requisitos

### Requisitos Transversales

- [docs/requisitos/](requisitos/) - Requisitos de nivel sistema

### Requisitos por Dominio

#### Backend

- [docs/backend/requisitos/](backend/requisitos/)
  - [INDICE_REQUISITOS.md](backend/requisitos/INDICE_REQUISITOS.md)
  - [trazabilidad.md](backend/requisitos/trazabilidad.md)
  - **Necesidades (N-XXX):**
    - [n001_visibilidad_metricas_ivr_tiempo_real.md](backend/requisitos/necesidades/n001_visibilidad_metricas_ivr_tiempo_real.md)
    - [n002_datos_actualizados_toma_decisiones.md](backend/requisitos/necesidades/n002_datos_actualizados_toma_decisiones.md)
    - [n003_visibilidad_metricas_operativas.md](backend/requisitos/necesidades/n003_visibilidad_metricas_operativas.md)
  - **Requisitos de Negocio (RN-XXX):**
    - [rn001_sistema_seguridad_auditoria_conforme_iso27001.md](backend/requisitos/negocio/rn001_sistema_seguridad_auditoria_conforme_iso27001.md)
    - [rn_c01_autenticacion_sesiones.md](backend/requisitos/negocio/rn_c01_autenticacion_sesiones.md)
  - **Requisitos de Stakeholders (RS-XXX):**
    - [rs001_auditoria_requiere_trazabilidad_completa.md](backend/requisitos/stakeholders/rs001_auditoria_requiere_trazabilidad_completa.md)
    - [rs002_reportes_automatizados_compliance.md](backend/requisitos/stakeholders/rs002_reportes_automatizados_compliance.md)
    - [rs002_usuarios_requieren_acceso_rapido.md](backend/requisitos/stakeholders/rs002_usuarios_requieren_acceso_rapido.md)
  - **Requisitos Funcionales (RF-XXX):**
    - RF-001 a RF-010: Autenticacion, permisos, segmentacion
  - **Requisitos No Funcionales (RNF-XXX):**
    - [rnf001_tiempo_respuesta_login.md](backend/requisitos/no_funcionales/rnf001_tiempo_respuesta_login.md)
    - [rnf002_sesiones_en_bd.md](backend/requisitos/no_funcionales/rnf002_sesiones_en_bd.md) - CRITICO

#### Frontend

- [docs/frontend/requisitos/](frontend/requisitos/)

#### Infrastructure

- [docs/infrastructure/requisitos/](infrastructure/requisitos/)

---

## Implementacion por Dominio

### Backend

- [docs/backend/](backend/)
  - **Arquitectura:**
    - [analytics.md](backend/arquitectura/analytics.md)
    - [audit.md](backend/arquitectura/audit.md)
    - [authentication.md](backend/arquitectura/authentication.md)
    - [common.md](backend/arquitectura/common.md)
    - [dashboard.md](backend/arquitectura/dashboard.md)
    - [etl.md](backend/arquitectura/etl.md)
    - [patrones_arquitectonicos.md](backend/arquitectura/patrones_arquitectonicos.md)
    - [guia_decision_patrones.md](backend/arquitectura/guia_decision_patrones.md)
  - **Diseño:**
    - [DISENO_TECNICO_AUTENTICACION.md](backend/diseno/DISENO_TECNICO_AUTENTICACION.md)
  - **Seguridad:**
    - [ANALISIS_SEGURIDAD_AMENAZAS.md](backend/seguridad/ANALISIS_SEGURIDAD_AMENAZAS.md)
  - **DevOps:**
    - [docs/backend/devops/](backend/devops/)
  - **QA:**
    - [docs/backend/qa/](backend/qa/)
    - [TASK-004-tests-auditoria-inmutable.md](backend/qa/TASK-004-tests-auditoria-inmutable.md)

### Frontend

- [docs/frontend/](frontend/)
  - **Arquitectura:**
    - [docs/frontend/arquitectura/](frontend/arquitectura/)
  - **Componentes:**
    - [docs/frontend/componentes/](frontend/componentes/)

### Infrastructure

- [docs/infrastructure/](infrastructure/)
  - **DevOps:**
    - [docs/infrastructure/devops/](infrastructure/devops/)
  - **Cassandra:**
    - [docs/infrastructure/cassandra/](infrastructure/cassandra/)

---

## Gobernanza

### Metodologias y Procesos

- [docs/gobernanza/](gobernanza/)
  - **Metodologias:**
    - [docs/gobernanza/metodologias/](gobernanza/metodologias/)
  - **Marco Integrado:**
    - [docs/gobernanza/marco_integrado/](gobernanza/marco_integrado/)
  - **Procesos:**
    - [INDICE_WORKFLOWS.md](gobernanza/procesos/INDICE_WORKFLOWS.md)
    - **Procedimientos:**
      - [procedimiento_analisis_seguridad.md](gobernanza/procesos/procedimientos/procedimiento_analisis_seguridad.md)
      - [procedimiento_trazabilidad_requisitos.md](gobernanza/procesos/procedimientos/procedimiento_trazabilidad_requisitos.md)
      - [guia_completa_desarrollo_features.md](gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)

### AI y Agentes

- [docs/gobernanza/ai/](gobernanza/ai/)
  - [ESTRATEGIA_IA.md](gobernanza/ai/ESTRATEGIA_IA.md)
  - [AI_CAPABILITIES.md](gobernanza/ai/AI_CAPABILITIES.md)
  - [ANALISIS_GAPS_POST_DORA_2025.md](gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md)
  - [TASK-009-comunicar-ai-stance.md](gobernanza/ai/TASK-009-comunicar-ai-stance.md)
- [docs/gobernanza/agentes/](gobernanza/agentes/)

---

## DORA Metrics

- [docs/dora/](dora/)
  - [DORA_REPORT_20251107.md](dora/DORA_REPORT_20251107.md)
  - [TASK-007-primer-reporte-dora.md](dora/TASK-007-primer-reporte-dora.md)
  - [TASK-008-cron-job-dora-mensuales.md](dora/TASK-008-cron-job-dora-mensuales.md)

---

## Operaciones

- [docs/operaciones/](operaciones/)
  - [TASK-013-cron-jobs-maintenance.md](operaciones/TASK-013-cron-jobs-maintenance.md)
  - **Runbooks:**
    - [claude_code.md](operaciones/claude_code.md)
    - [github_copilot_codespaces.md](operaciones/github_copilot_codespaces.md)
    - [merge_y_limpieza_ramas.md](operaciones/merge_y_limpieza_ramas.md)
    - [post_create.md](operaciones/post_create.md)
    - [reprocesar_etl_fallido.md](operaciones/reprocesar_etl_fallido.md)
    - [verificar_servicios.md](operaciones/verificar_servicios.md)

---

## Features

- [docs/features/](features/)
  - [TASK-014-custom-dashboards-admin.md](features/TASK-014-custom-dashboards-admin.md)

---

## Testing y QA

- [docs/testing/](testing/)
- [docs/qa/](qa/)
  - [TASK-001-ejecutar-suite-tests.md](qa/TASK-001-ejecutar-suite-tests.md)
  - [TASK-002-validar-restricciones-criticas.md](qa/TASK-002-validar-restricciones-criticas.md)
  - [TASK-003-verificar-session-engine.md](qa/TASK-003-verificar-session-engine.md)

---

## Plantillas

- [docs/plantillas/](plantillas/)
  - Plantillas de documentos
  - Templates de codigo

---

## Anexos

- [docs/anexos/](anexos/)
  - [glosario.md](anexos/glosario.md)
  - [glosario_babok_pmbok_iso.md](anexos/glosario_babok_pmbok_iso.md)
  - [catalogo_reglas_negocio.md](anexos/catalogo_reglas_negocio.md)
  - [faq.md](anexos/faq.md)
  - **Analisis Noviembre 2025:**
    - [RESUMEN_EJECUTIVO_REORGANIZACION.md](anexos/analisis_nov_2025/RESUMEN_EJECUTIVO_REORGANIZACION.md)
    - [ESTRATEGIA_REORGANIZACION_TODO_POR_DOMINIO.md](anexos/analisis_nov_2025/ESTRATEGIA_REORGANIZACION_TODO_POR_DOMINIO.md)
    - [REPORTE_DUPLICADOS.md](anexos/analisis_nov_2025/REPORTE_DUPLICADOS.md)

---

## Tareas Completadas (TASK-XXX)

### Sprint 1 (Semana 1) - 14 SP

- [x] **TASK-001:** Ejecutar Suite Completa de Tests (2 SP)
  - [docs/qa/TASK-001-ejecutar-suite-tests.md](qa/TASK-001-ejecutar-suite-tests.md)
- [x] **TASK-002:** Validar Restricciones Criticas (1 SP)
  - [docs/qa/TASK-002-validar-restricciones-criticas.md](qa/TASK-002-validar-restricciones-criticas.md)
- [x] **TASK-003:** Verificar SESSION_ENGINE en Settings (1 SP)
  - [docs/qa/TASK-003-verificar-session-engine.md](qa/TASK-003-verificar-session-engine.md)
- [x] **TASK-004:** Tests de Auditoria Inmutable (2 SP)
  - [docs/backend/qa/TASK-004-tests-auditoria-inmutable.md](backend/qa/TASK-004-tests-auditoria-inmutable.md)
- [x] **TASK-005:** Sistema de Metrics Interno MySQL (8 SP)
  - [docs/backend/TASK-005-sistema-metrics-mysql.md](backend/TASK-005-sistema-metrics-mysql.md)
- [x] **TASK-006:** Validar Estructura de Docs (1 SP)
  - [docs/proyecto/TASK-006-validar-estructura-docs.md](proyecto/TASK-006-validar-estructura-docs.md)

### Sprint 2 (Semana 2) - 12 SP

- [x] **TASK-007:** Ejecutar Primer DORA Metrics Report (1 SP)
  - [docs/dora/TASK-007-primer-reporte-dora.md](dora/TASK-007-primer-reporte-dora.md)
- [x] **TASK-008:** Configurar Cron Job DORA Mensuales (1 SP)
  - [docs/dora/TASK-008-cron-job-dora-mensuales.md](dora/TASK-008-cron-job-dora-mensuales.md)
- [x] **TASK-009:** Comunicar AI Stance al Equipo (1 SP)
  - [docs/gobernanza/ai/TASK-009-comunicar-ai-stance.md](gobernanza/ai/TASK-009-comunicar-ai-stance.md)
- [x] **TASK-010:** Logging Estructurado JSON (3 SP)
  - [docs/arquitectura/TASK-010-logging-estructurado-json.md](arquitectura/TASK-010-logging-estructurado-json.md)
- [x] **TASK-011:** Data Centralization Layer (5 SP)
  - [docs/arquitectura/TASK-011-data-centralization-layer.md](arquitectura/TASK-011-data-centralization-layer.md)
- [x] **TASK-012:** Agregar AI Guidelines a Onboarding (2 SP)
  - [docs/proyecto/TASK-012-ai-guidelines-onboarding.md](proyecto/TASK-012-ai-guidelines-onboarding.md)

### Sprint 3 (Semana 3) - En Progreso

- [x] **TASK-013:** Configurar Cron Jobs Maintenance (2 SP)
  - [docs/operaciones/TASK-013-cron-jobs-maintenance.md](operaciones/TASK-013-cron-jobs-maintenance.md)
- [x] **TASK-014:** Custom Dashboards Django Admin (5 SP)
  - [docs/features/TASK-014-custom-dashboards-admin.md](features/TASK-014-custom-dashboards-admin.md)
- [ ] **TASK-015:** Actualizar Documentacion Tecnica (1 SP) - EN PROGRESO
- [ ] **TASK-016:** Validar Compliance RNF-002 (3 SP)

---

## Metricas de Documentacion

**Ultima actualizacion:** 2025-11-07

### Conteo por Categoria

- **Backend:** 58 archivos .md
- **Frontend:** 13 archivos .md
- **Infrastructure:** 25 archivos .md
- **Gobernanza:** 45+ archivos .md
- **ADRs:** 11 archivos
- **DORA:** 3 archivos
- **Operaciones:** 7+ archivos
- **Features:** 1 archivo
- **QA/Testing:** 4 archivos
- **Arquitectura:** 4 archivos
- **Total:** 297 archivos .md

### Estado de Documentacion

- Directorios legacy eliminados: `docs/implementacion/`
- Estructura por dominio: COMPLETADA
- Links rotos identificados: 3 (en proceso de correccion)
- CODEOWNERS actualizado: SI
- Indice completo: SI (este documento)

---

## Scripts de Documentacion

### Validacion

- [scripts/validar_estructura_docs.sh](../scripts/validar_estructura_docs.sh)
  - Valida estructura de directorios
  - Busca links rotos
  - Detecta referencias a directorios legacy

### Sincronizacion

- [scripts/sync_documentation.py](../scripts/sync_documentation.py)
  - Sincroniza documentacion entre directorios
  - Genera reportes de duplicados

### Reorganizacion

- [scripts/reorganizar_docs_por_dominio.sh](../scripts/reorganizar_docs_por_dominio.sh)
  - Reorganiza docs por dominio

---

## Navegacion Rapida

### Por Rol

**Desarrollador Backend:**
- [docs/backend/](backend/)
- [docs/backend/arquitectura/](backend/arquitectura/)
- [docs/backend/requisitos/](backend/requisitos/)

**Desarrollador Frontend:**
- [docs/frontend/](frontend/)
- [docs/frontend/arquitectura/](frontend/arquitectura/)

**DevOps:**
- [docs/infrastructure/](infrastructure/)
- [docs/operaciones/](operaciones/)
- [docs/dora/](dora/)

**Arquitecto:**
- [docs/arquitectura/](arquitectura/)
- [docs/adr/](adr/)

**Product Owner:**
- [docs/requisitos/](requisitos/)
- [docs/backend/requisitos/](backend/requisitos/)

**QA Lead:**
- [docs/testing/](testing/)
- [docs/qa/](qa/)

### Por Tema

**DORA Metrics:**
- [docs/dora/](dora/)
- [docs/features/TASK-014-custom-dashboards-admin.md](features/TASK-014-custom-dashboards-admin.md)

**AI y Agentes:**
- [docs/gobernanza/ai/](gobernanza/ai/)
- [docs/gobernanza/agentes/](gobernanza/agentes/)

**Seguridad:**
- [docs/backend/seguridad/](backend/seguridad/)
- [RNF-002: Sesiones en BD](backend/requisitos/no_funcionales/rnf002_sesiones_en_bd.md)

**Logging y Observabilidad:**
- [docs/arquitectura/OBSERVABILITY_LAYERS.md](arquitectura/OBSERVABILITY_LAYERS.md)
- [docs/arquitectura/TASK-010-logging-estructurado-json.md](arquitectura/TASK-010-logging-estructurado-json.md)

---

## Contactos

### Owners por Area

- **Arquitectura:** @arquitecto-senior
- **Backend:** @equipo-backend-lead
- **Frontend:** @equipo-frontend-lead
- **DevOps:** @devops-lead
- **Product:** @product-owner
- **QA:** @qa-lead
- **Tech Lead:** @tech-lead

Ver [.github/CODEOWNERS](../.github/CODEOWNERS) para detalles completos.

---

## Versionado

- **v1.0.0:** Indice inicial (INDICE.md)
- **v2.0.0:** Indice completo reorganizado (INDEX.md) - 2025-11-07
  - Estructura por dominio
  - Eliminacion directorios legacy
  - Tareas TASK-XXX indexadas
  - Metricas de documentacion
  - Navegacion por rol y tema

---

**Mantenido por:** @arquitecto-senior
**Proxima revision:** 2025-11-14 (semanal)
**Feedback:** Crear issue en GitHub con label `documentation`
