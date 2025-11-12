# Índice consolidado de documentación

> Última actualización: 2025-11-12  
> **Leyenda**: ✅ = Implementado | 📋 = Planificado | ⚠️ = Crítico

Este índice combina lo implementado con la visión futura del proyecto, claramente marcado para evitar confusiones.

## 📍 Puntos de entrada rápidos

### Por actividad
- **Empezar a desarrollar**: [`README.md`](README.md) - Setup completo
- **Entender el estado actual**: [`plans/REV_20251112_remediation_plan.md`](plans/REV_20251112_remediation_plan.md)
- **Seguir estándares**: [`gobernanza/GUIA_ESTILO.md`](gobernanza/GUIA_ESTILO.md)
- **Ejecutar validaciones**: [`scripts/run_all_tests.sh`](../scripts/run_all_tests.sh)

### Por rol
- **Developer**: [`gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md`](gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)
- **QA**: [`qa/`](qa/README.md), [`gobernanza/procesos/qa/ESTRATEGIA_QA.md`](gobernanza/procesos/qa/ESTRATEGIA_QA.md)
- **DevOps**: [`operaciones/`](operaciones/), [`infrastructure/`](infrastructure/)
- **Arquitecto**: [`adr/`](adr/), [`arquitectura/`](arquitectura/)
- **Product Owner**: [`requisitos/`](requisitos/), [`backend/requisitos/`](backend/requisitos/)

## 📚 Documentación activa

### Gobernanza y procesos (✅ Completo)
- **Guía de Estilo**: [`gobernanza/GUIA_ESTILO.md`](gobernanza/GUIA_ESTILO.md) - Convenciones obligatorias
- **Procesos**: [`gobernanza/procesos/`](gobernanza/procesos/)
  - Procedimientos operacionales (11 docs)
  - Checklists de desarrollo, testing, trazabilidad
  - QA: [`gobernanza/procesos/qa/ESTRATEGIA_QA.md`](gobernanza/procesos/qa/ESTRATEGIA_QA.md)
- **CI/CD**: [`gobernanza/ci_cd/`](gobernanza/ci_cd/)
  - Guía de uso por rol: [`GUIA_USO.md`](gobernanza/ci_cd/GUIA_USO.md)
  - Troubleshooting: [`TROUBLESHOOTING.md`](gobernanza/ci_cd/TROUBLESHOOTING.md)
  - Ejemplos: [`EJEMPLOS.md`](gobernanza/ci_cd/EJEMPLOS.md)

### Arquitectura (✅ Documentada, 📋 Evolución continua)
- **ADRs**: [`adr/`](adr/) - 11+ Architecture Decision Records
  - ADR-001: Vagrant + mod_wsgi
  - ADR-002: Suite de calidad de código
  - ADR-008-014: Frontend (React, Redux, Webpack, Jest)
- **Lineamientos**: [`arquitectura/`](arquitectura/)
  - Storage: MySQL + 📋 Cassandra
  - Observability: [`OBSERVABILITY_LAYERS.md`](arquitectura/OBSERVABILITY_LAYERS.md)
- **Por dominio**:
  - Backend: [`backend/arquitectura/`](backend/arquitectura/)
  - Frontend: [`frontend/arquitectura/`](frontend/arquitectura/)
  - Infrastructure: [`infrastructure/`](infrastructure/)

### Requisitos (✅ Estructura definida, 📋 Contenido en construcción)
- **Marco integrado**: [`requisitos/analisis_negocio/marco_integrado/`](requisitos/analisis_negocio/marco_integrado/)
  - Metodología BABOK v3 + ISO/IEC/IEEE 29148:2018
  - 7,419 líneas de framework de análisis
- **Requisitos de backend**: [`backend/requisitos/`](backend/requisitos/)
  - Necesidades (N-XXX): 3 documentados
  - Negocio (RN-XXX): 2 documentados
  - Stakeholders (RS-XXX): 3 documentados
  - Funcionales (RF-XXX): 10 documentados
  - ⚠️ No funcionales (RNF-XXX): **RNF-002 CRÍTICO** (NO Redis)

### Operaciones (✅ Runbooks disponibles)
- **Runbooks**: [`operaciones/`](operaciones/)
  - Verificar servicios (PostgreSQL + MariaDB)
  - Reprocesar ETL fallido
  - Merge y limpieza de ramas
  - Claude Code, GitHub Copilot
- 📋 **Disaster Recovery**: [`scripts/disaster_recovery/`](../scripts/disaster_recovery/) - Scripts pendientes

### Infraestructura (✅ CPython builder completo)
- **CPython Precompilado**: [`infrastructure/cpython/`](../infrastructure/cpython/)
  - README: [`infrastructure/cpython/README.md`](../infrastructure/cpython/README.md)
  - Changelog: [`CHANGELOG-cpython.md`](infrastructure/CHANGELOG-cpython.md)
  - Scripts: `build_cpython.sh`, `validate_build.sh`, `install_prebuilt_cpython.sh`
- **DevContainer**: [`infrastructure/devcontainer/`](infrastructure/devcontainer/)
- 📋 **Cassandra**: Documentación disponible, implementación pendiente

### Scripts y automatización (✅ Parcial, 📋 Muchos planificados)

#### ✅ Implementados
- **CI Gates**: [`scripts/ci/`](../scripts/ci/)
  - `gate-no-emojis.sh`, `gate-docs-structure.sh`
  - `run-all-checks.sh`, `run_architecture_analysis.py`
- **Validaciones**: [`scripts/validation/`](../scripts/validation/)
  - Quality, compliance, security, docs
- **Test runner**: [`scripts/run_all_tests.sh`](../scripts/run_all_tests.sh)
- **Templates**: [`scripts/templates/`](../scripts/templates/)

#### 📋 Planificados (ver [`docs/scripts/README.md`](scripts/README.md))
- `scripts/sdlc_agent.py` - CLI SDLC
- `scripts/dora_metrics.py` - Calculador DORA metrics
- `scripts/requisitos/` - Gestión de requisitos
- 20+ agentes SDLC especializados

### Testing y QA (✅ Framework, 📋 Cobertura en crecimiento)
- **Estrategia**: [`qa/`](qa/), [`gobernanza/procesos/qa/ESTRATEGIA_QA.md`](gobernanza/procesos/qa/ESTRATEGIA_QA.md)
- **Targets**: Coverage >= 80%, Test Pyramid (60/30/10), MTTR <= 2 días
- **Tests**: [`testing/`](testing/)
  - Documentación: `test_documentation_alignment.py`
  - 📋 Backend, frontend, integration tests - en construcción

### Análisis y reportes (✅ Manuales, 📋 Automatización pendiente)
- **Backend**: [`backend_analisis/2025-11-11/`](backend_analisis/2025-11-11/)
  - Análisis de calidad: 93% overall
  - Resultados: [`logs_data/analysis/backend_analysis_results.json`](../logs_data/analysis/backend_analysis_results.json)
- **Logs temporales**: [`logs_data/`](../logs_data/)
  - Schemas: deployment, DORA metrics, incidents
  - Estado: generación manual, rotación pendiente

## 🎯 Proyecto y planificación

### ✅ Tracking activo
- **Roadmap**: [`proyecto/ROADMAP.md`](proyecto/ROADMAP.md) - Q4 2025 - Q2 2026
- **Tareas**: [`proyecto/TAREAS_ACTIVAS.md`](proyecto/TAREAS_ACTIVAS.md) - Sprint actual
- **Changelog**: [`proyecto/CHANGELOG.md`](proyecto/CHANGELOG.md) - Historial completo

### Revisión actual (12 Nov 2025)
- **Plan de remediación**: [`plans/REV_20251112_remediation_plan.md`](plans/REV_20251112_remediation_plan.md)
- **Estado**: Alineación docs ↔ código en progreso

## 📋 Visión futura (planificado)

### DORA Metrics y AI Excellence
- **Estrategia IA**: [`gobernanza/ai/ESTRATEGIA_IA.md`](gobernanza/ai/ESTRATEGIA_IA.md)
- **AI Capabilities**: [`gobernanza/ai/AI_CAPABILITIES.md`](gobernanza/ai/AI_CAPABILITIES.md)
- **Gaps post-DORA 2025**: [`gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md`](gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md)
- **Target**: 7/7 prácticas AI (actual: 5/7 - 71%)
- **Roadmap**: 144 SP, completar Q2 2026

### SDLC Agents
- **Documentación**: [`gobernanza/procesos/AGENTES_SDLC.md`](gobernanza/procesos/AGENTES_SDLC.md)
- **Agentes planificados**: Planner, Feasibility, Design, Testing, Deployment, Orchestrator
- **Estado**: Arquitectura documentada, implementación pendiente

### Workflows CI/CD completos
- **Índice**: [`gobernanza/ci_cd/INDICE.md`](gobernanza/ci_cd/INDICE.md)
- **Workflows**: 8 planificados (backend-ci, frontend-ci, test-pyramid, deploy, etc.)
- **Estado**: Documentación completa, pipelines pendientes

## 📦 Plantillas (✅ 34 templates disponibles)
- **Ubicación**: [`plantillas/`](plantillas/)
- **Categorías**:
  - Requisitos (5): Necesidad, RN, RF, RNF, Stakeholder
  - Desarrollo (10): Django app, ETL, Spec, SRS, TDD, etc.
  - Testing (2): Plan de pruebas, Casos
  - Diseño (2): DB design, Casos de uso
  - Documentación (4): API reference, Manual usuario
  - Infraestructura (4): Runbook, Deployment, Setup
  - Gestión (6): Release plan, Business case, Project charter

## 🗄️ Contenido legado y referencia

### Documentación histórica
- **Legacy docs**: [`../respaldo/docs_legacy/`](../respaldo/docs_legacy/README.md)
  - Estructura pre-reorganización (v3.0)
  - Preservado para consulta
- **Análisis archivados**: [`anexos/analisis_nov_2025/`](anexos/analisis_nov_2025/)
  - Propuestas de reorganización
  - Reporte de duplicados
- **Índices anteriores**: 
  - [`INDEX.md`](INDEX.md) - Versión 2.0 (deprecada)
  - [`INDICE.md`](INDICE.md) - Versión 1.6 (deprecada)

## ⚠️ Restricciones críticas del proyecto

### RNF-002: NO Redis/Memcached (CRÍTICO)
- Sesiones DEBEN estar en MySQL: `django.contrib.sessions.backends.db`
- Cache PUEDE usar MySQL o filesystem
- PROHIBIDO: Redis, Memcached, cualquier servicio externo de cache

### Otras restricciones obligatorias
- ❌ NO Email/SMTP (usar `InternalMessage` para notificaciones)
- ❌ NO Emojis/Iconos UTF-8 (usar texto ASCII: [OK], [FAIL], [WARNING])
- ✅ Scripts primero, CI/CD después (scripts deben funcionar offline)
- ❌ NO RabbitMQ, Celery, MongoDB, Elasticsearch

Ver: [`gobernanza/estilos/GUIA_ESTILO.md`](gobernanza/estilos/GUIA_ESTILO.md)

## 📊 Métricas del proyecto (snapshot Nov 2025)

### Documentación
- **Archivos .md**: 297+ documentos
- **Estructura**: Por dominio (backend, frontend, infrastructure) + transversal
- **ADRs**: 11 decisiones arquitectónicas
- **Plantillas**: 34 templates reutilizables

### Código (backend)
- **Calidad general**: 93%
- **Archivos analizados**: 58 módulos Python
- **Violaciones SOLID**: Identificadas, en remediación
- **Cobertura**: En construcción (target 80%)

### Scripts
- **Total**: 67+ scripts documentados
- **Implementados**: ~30 en `scripts/ci/`, `scripts/validation/`, `scripts/infrastructure/`
- **Planificados**: ~37 (SDLC agents, DORA metrics, requisitos)

## 🔗 Enlaces útiles

### Guías de inicio por rol
- [Developers](gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)
- [QA](qa/README.md)
- [DevOps](operaciones/)
- [Arquitectos](adr/)

### Procedimientos clave
- [Instalación de entorno](gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md)
- [Desarrollo local](gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md)
- [Diseño técnico](gobernanza/procesos/procedimientos/procedimiento_diseno_tecnico.md)
- [Análisis de seguridad](gobernanza/procesos/procedimientos/procedimiento_analisis_seguridad.md)
- [Release](gobernanza/procesos/procedimientos/procedimiento_release.md)

### Recursos externos
- [BABOK v3](https://www.iiba.org/standards-and-resources/babok/)
- [PMBOK 7](https://www.pmi.org/pmbok-guide-standards)
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html)
- [DORA Report 2025](https://dora.dev/dora-report-2025)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Mantenido por**: Equipo Gobernanza  
**Próxima revisión**: Semanal  
**Feedback**: Crear issue en GitHub con label `documentation`
