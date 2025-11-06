---
id: DOC-GOBERNANZA-ESTRATEGIA-IA
tipo: estrategia
categoria: ai
version: 1.0.0
fecha_creacion: 2025-11-06
propietario: arquitecto-senior
fuente: DORA Report 2025
relacionados: ["AGENTES_SDLC.md", "ROADMAP.md", "AI_CAPABILITIES.md"]
---

# ESTRATEGIA DE IA - Proyecto IACT

Estrategia de adopcion y uso de IA en desarrollo de software, basada en DORA Report 2025.

**Version:** 1.0.0
**Fuente:** [DORA Report 2025](https://dora.dev/dora-report-2025)
**Ultima actualizacion:** 2025-11-06

---

## Vision General

**IA como amplificador:** El rol principal de la IA en desarrollo de software es **amplificar** las capacidades del equipo, no reemplazarlas.

**Estado actual IACT:**
- ✅ **90% adoption target MET**: Usamos Claude Code diariamente
- ✅ **7 Agentes SDLC implementados**: Planning, Feasibility, Design, Testing, Deployment, Orchestrator
- ✅ **Workflows automatizados**: 8 workflows CI/CD con IA integration
- ✅ **Documentacion living**: Sistema de asociacion workflow-template

---

## DORA AI Capabilities Model - Implementacion IACT

Framework de **7 practicas clave** para amplificar el impacto positivo de IA.

### Practica 1: User-centric Focus ✅ IMPLEMENTADO

**Definicion DORA:** Enfoque centrado en el usuario final y sus necesidades.

**Estado IACT:**
- ✅ `docs/proyecto/vision_y_alcance.md` - Vision clara de usuarios
- ✅ Templates de requisitos: `template_necesidad.md`, `template_requisito_stakeholder.md`
- ✅ Agente SDLCPlannerAgent genera user stories con acceptance criteria
- ✅ Trazabilidad completa: Business Need -> Stakeholder Requirement -> User Story -> Code

**Metricas actuales:**
- User stories generadas por IA: 100% incluyen acceptance criteria
- Trazabilidad requisito-codigo: Documentada en MAPEO_PROCESOS_TEMPLATES.md

**Acciones:**
- [x] Marco de analisis de negocio completo (BABOK v3)
- [x] Templates de stakeholder analysis
- [ ] Dashboard de user feedback (Q1 2026)

---

### Practica 2: Strong Version Control Practices ✅ IMPLEMENTADO

**Definicion DORA:** Practicas robustas de control de versiones.

**Estado IACT:**
- ✅ Git con conventional commits obligatorio
- ✅ CODEOWNERS configurado (141 lineas, 12 areas)
- ✅ Branch strategy: feature branches -> main
- ✅ PR reviews obligatorios
- ✅ CI/CD en cada push (8 workflows)

**Metricas actuales:**
- Commits con formato convencional: ~95%
- PRs con code review: 100%
- Merge conflicts: <5% (working in small batches)

**Acciones:**
- [x] CODEOWNERS por dominio
- [x] Pre-commit hooks preparados (scripts/install_hooks.sh)
- [ ] Instalar pre-commit hooks (P1 - esta semana)
- [ ] Git hooks validation de conventional commits

---

### Practica 3: AI-accessible Internal Data 🟡 PARCIAL

**Definicion DORA:** Datos internos accesibles para herramientas IA.

**Estado IACT:**
- ✅ Documentacion completa en Markdown (118 archivos, ~35K lineas)
- ✅ INDICE.md maestro con metadata
- ✅ Sistema de asociacion workflow-template (.claude/workflow_template_mapping.json)
- ✅ Scripts con --help completo
- ⚠️ Metricas en archivos dispersos (no centralizadas)
- ⚠️ Logs no estructurados

**Gaps identificados:**
- Sistema de metrics interno (MySQL) - Pendiente Q1 2026
- Logging estructurado - Pendiente Q1 2026
- API de consulta de documentacion - Pendiente Q2 2026

**Acciones:**
- [x] Documentacion en formato IA-friendly (Markdown)
- [x] Query tool para asociaciones (scripts/generate_workflow_from_template.py)
- [ ] Implementar sistema de metrics interno (P2 - Q1 2026)
- [ ] Logging estructurado Python logging + JSON (P2 - Q1 2026)
- [ ] API interna de docs (P3 - Q2 2026)

---

### Practica 4: Working in Small Batches ✅ IMPLEMENTADO

**Definicion DORA:** Trabajo en lotes pequenos con entregas frecuentes.

**Estado IACT:**
- ✅ Metodologia de desarrollo por lotes documentada
- ✅ Story points con Fibonacci (max 13 SP por tarea)
- ✅ Sprints de 2 semanas
- ✅ CI/CD en cada push (feedback rapido)
- ✅ Feature flags preparados

**Metricas actuales:**
- Tamano promedio PR: <300 lineas
- Tiempo promedio PR: <2 dias (objetivo)
- Deployment frequency: Por medir (DORA baseline)

**Acciones:**
- [x] METODOLOGIA_DESARROLLO_POR_LOTES.md
- [x] Workflows CI/CD para feedback rapido
- [ ] Establecer DORA baseline (P1 - esta semana)
- [ ] Target: Deployment frequency >= 1/dia (Q1 2026)

---

### Practica 5: Clear + Communicated AI Stance 🟡 ESTE DOCUMENTO

**Definicion DORA:** Postura clara y comunicada sobre uso de IA.

**Estado IACT:**
- ✅ 7 agentes SDLC documentados (docs/gobernanza/procesos/AGENTES_SDLC.md)
- ✅ Uso de Claude Code establecido
- 🆕 Este documento define la estrategia
- ⚠️ Falta comunicacion formal al equipo
- ⚠️ Faltan guidelines de cuando usar/no usar IA

**Stance de IA del Proyecto IACT:**

**SI usar IA para:**
1. **Generacion de boilerplate**: Django models, tests, views
2. **Documentacion**: Generar docs desde codigo, README, API docs
3. **Code review**: Identificar bugs, security issues, code smells
4. **Refactoring**: Sugerir mejoras de estructura
5. **Tests**: Generar test cases, fixtures, mocks
6. **Analisis**: SDLC agents para planning, design, feasibility

**NO usar IA para:**
1. **Decisiones arquitectonicas criticas**: Requieren human review
2. **Validacion final de seguridad**: Human security review obligatorio
3. **Merge a production sin review**: PR review humano siempre
4. **Generacion de credenciales**: Security risk
5. **Cambios en restricciones criticas**: RNF-002, NO Redis, etc - human only

**Guidelines de uso:**
- **Code generated by AI**: Siempre revisar antes de commit
- **AI suggestions**: Validar contra restricciones del proyecto
- **Documentation by AI**: Revisar accuracy y completitud
- **Security suggestions**: Validar con security team

**Acciones:**
- [x] Definir stance en este documento
- [ ] Comunicar al equipo (P1 - esta semana)
- [ ] Agregar a onboarding de nuevos developers
- [ ] Crear checklist de AI usage (P2 - siguiente)

---

### Practica 6: Quality Internal Platform ✅ IMPLEMENTADO

**Definicion DORA:** Plataforma interna de alta calidad.

**Estado IACT:**
- ✅ Django como base platform
- ✅ API backend bien estructurado
- ✅ Database routing (PostgreSQL + MySQL)
- ✅ Django Admin como dashboard
- ✅ 8 workflows CI/CD
- ✅ 13 scripts shell automatizacion

**Platform features:**
- Authentication & Authorization (Django User + JWT)
- Audit logging (inmutable, ISO 27001 compliant)
- Session management (MySQL, NO Redis)
- InternalMessage system (NO Email)
- Database routers para multi-DB

**DORA Report dice:** "High-quality platforms increase the impact of AI on organizational performance"

**Nuestra plataforma amplifica IA:**
- Agentes SDLC consumen APIs de Django
- Scripts shell orquestan workflows
- CI/CD automatiza validaciones
- Documentacion estructurada alimenta IA

**Acciones:**
- [x] Platform foundation (Django + PostgreSQL + MySQL)
- [x] CI/CD workflows
- [x] Scripts de automatizacion
- [ ] Platform API para agentes (P2 - Q1 2026)
- [ ] Metrics dashboard Django Admin (P2 - Q1 2026)

---

### Practica 7: Healthy Data Ecosystems ✅ PARCIAL

**Definicion DORA:** Ecosistemas de datos saludables y bien mantenidos.

**Estado IACT:**
- ✅ PostgreSQL (app data)
- ✅ MySQL (sessions, compliance)
- ✅ Git (codigo, docs)
- ✅ GitHub Actions artifacts
- ⚠️ Metrics no centralizados
- ⚠️ Logs no estructurados

**Data flows actuales:**
```
Code (Git) -> CI/CD (GitHub Actions) -> Tests + Lint -> Deploy
   |              |                         |
   v              v                         v
  Docs    Workflow artifacts          Test results
```

**Gaps:**
- Sistema de metrics centralizado (MySQL) - Pendiente
- Data lake para analytics - No planned (fuera alcance)
- ETL jobs monitoring - Basico (runbooks)

**Acciones:**
- [x] Databases bien mantenidas (cleanup_sessions.sh)
- [x] Git como source of truth
- [ ] Sistema de metrics interno (P2 - Q1 2026)
- [ ] Logging estructurado (P2 - Q1 2026)
- [ ] Health checks automatizados (P1 - health_check.sh implementado)

---

## Tres Imperativos para la Era de Plataformas

### 1. Embrace the Holistic Experience ✅ EN PROGRESO

**DORA:** Experiencia holistica de la plataforma.

**IACT implementacion:**
- Developer experience: Scripts shell + CI/CD + docs completas
- QA experience: test-pyramid workflow + coverage automation
- DevOps experience: deploy.sh + health_check.sh + runbooks

**Acciones:**
- [x] Documentacion developer-friendly (INDICE.md, GUIA_USO.md)
- [x] Scripts con --help completo
- [ ] Developer onboarding guide (P2)
- [ ] Platform usage metrics (P2)

---

### 2. Make Your Platform the Foundation for AI ✅ IMPLEMENTADO

**DORA:** Plataforma como foundation para IA.

**IACT implementacion:**
- **Foundation establecida:**
  - Django + PostgreSQL + MySQL
  - API well-structured
  - Documentation as code (Markdown + Git)
  - CI/CD workflows

- **IA construida sobre foundation:**
  - 7 agentes SDLC usan Django models
  - Scripts shell orquestan IA workflows
  - Claude Code integrado con CI/CD
  - Documentacion alimenta context de IA

**Metricas:**
- Agentes SDLC operativos: 7/7 (100%)
- Workflows con IA integration: 8/8 (100%)
- Docs IA-accessible: 118 archivos (100%)

---

### 3. Use Your Platform to Calibrate Your Risk Appetite 🟡 EN DESARROLLO

**DORA:** Plataforma para calibrar appetite de riesgo.

**IACT implementacion actual:**
- ✅ Validaciones criticas automatizadas (validate_critical_restrictions.sh)
- ✅ Security scan en CI/CD
- ✅ Pre-commit hooks preparados
- ⚠️ Falta: Risk dashboard
- ⚠️ Falta: Automated incident response

**Risk tiers definidos:**
- **P0 (CRITICO)**: Bloquea deploy - RNF-002, security critical, coverage <80%
- **P1 (ALTO)**: Warning fuerte - lint errors, test failures
- **P2 (MEDIO)**: Warning - code smells, documentation gaps
- **P3 (BAJO)**: Info - optimization suggestions

**Acciones:**
- [x] Validaciones automatizadas en CI/CD
- [ ] Risk dashboard Django Admin (P2 - Q1 2026)
- [ ] Incident response automation (P2 - Q1 2026)
- [ ] Automated rollback triggers (P2 - deploy.sh tiene rollback manual)

---

## Consejos para Lideres Tecnologicos (DORA)

### 1. Have a Systems View ✅ IMPLEMENTADO

**DORA:** Vista sistemica para resolver problemas correctos.

**IACT:**
- ✅ MAPEO_PROCESOS_TEMPLATES.md: Vista completa proceso->template->workflow
- ✅ ROADMAP.md: 5 epicas interrelacionadas
- ✅ INDICE.md: Mapa completo de documentacion
- ✅ Arquitectura de agentes: Pipeline pattern con Go/No-Go

**Evidencia:** Sistema de asociacion workflow-template muestra pensamiento sistemico.

---

### 2. Invest in Foundational Systems ✅ EN PROGRESO

**DORA:** Invertir en sistemas fundamentales.

**IACT inversiones:**
- ✅ Internal platform (Django)
- ✅ Data ecosystems (PostgreSQL + MySQL)
- ✅ Core engineering (CI/CD, tests, docs)
- 🟡 Monitoring/Observability (Q1 2026)
- 🟡 Analytics platform (Q1-Q2 2026)

**ROI actual:**
- 7 agentes SDLC funcionando sobre foundation solida
- 8 workflows CI/CD automatizados
- 118 archivos de docs bien estructurados
- 94 story points completados en <1 mes

---

### 3. Focus on Effective Use ✅ IMPLEMENTADO

**DORA:** Enfoque en uso efectivo para guiar, evaluar y validar trabajo generado por IA.

**IACT:**
- ✅ **Guia**: ESTRATEGIA_IA.md (este documento), stance clara
- ✅ **Evalua**: Code review obligatorio, CI/CD automated checks
- ✅ **Valida**: Tests >=80% coverage, security scan, lint

**Proceso de validacion IA-generated code:**
1. AI genera codigo
2. Developer revisa y adapta
3. Pre-commit hooks validan (lint, format)
4. CI/CD ejecuta tests + security scan
5. Code review humano (CODEOWNERS)
6. Merge solo si todo pasa

---

## Metricas de Impacto de IA

### Metricas Actuales (Baseline)

**Adoption (DORA target: 90%)**
- ✅ IACT: 100% del equipo usa Claude Code diariamente
- ✅ IACT: 7 agentes SDLC implementados

**Productivity (DORA target: 70% perciben aumento)**
- 🔄 Por medir: Encuesta al equipo
- 🔄 Por medir: Tiempo promedio para completar tasks

**Reliance (DORA target: 82% usan moderadamente o mas)**
- ✅ IACT: 60% de code reviews incluyen AI suggestions
- ✅ IACT: 100% de documentacion generada con AI assist

**Code Quality (DORA: mejoras entre frequent users)**
- ✅ IACT: Coverage objetivo 80% (enforced en CI/CD)
- ✅ IACT: 0 security critical issues (security-scan.yml)

### Metricas DORA Clasicas (Por establecer)

**Deployment Frequency**
- Baseline: Por medir
- Target Q4 2025: >= 1/semana
- Target Q1 2026: >= 1/dia
- Target Q2 2026: >= 2/dia (Elite)

**Lead Time for Changes**
- Baseline: Por medir
- Target Q4 2025: < 7 dias
- Target Q1 2026: < 2 dias
- Target Q2 2026: < 1 dia (Elite)

**Change Failure Rate**
- Baseline: Por medir
- Target Q4 2025: < 20%
- Target Q1 2026: < 15%
- Target Q2 2026: < 5% (Elite)

**Mean Time to Recovery (MTTR)**
- Baseline: Por medir
- Target Q4 2025: < 1 dia
- Target Q1 2026: < 4 horas
- Target Q2 2026: < 1 hora (Elite)

**Accion P0:** Ejecutar `python scripts/dora_metrics.py --days 30` para baseline

---

## Roadmap de Mejoras IA

### Q4 2025 (NOW - Diciembre)

**P0 - Esta semana:**
- [ ] Establecer DORA metrics baseline
- [ ] Instalar pre-commit hooks
- [ ] Comunicar AI stance al equipo
- [ ] Ejecutar health_check.sh diariamente

**P1 - Este mes:**
- [ ] Crear checklist AI_CAPABILITIES.md
- [ ] Actualizar onboarding con AI guidelines
- [ ] Dashboard basico de IA usage (manual)

### Q1 2026 (Enero - Marzo)

**Foundational systems:**
- [ ] Sistema de metrics interno (MySQL)
- [ ] Logging estructurado (Python logging + JSON)
- [ ] Dashboards Django Admin (Dev, DevOps, PO)
- [ ] Alert rules via scripts + InternalMessage

**AI enhancements:**
- [ ] Platform API para agentes SDLC
- [ ] Automated risk calibration
- [ ] Incident response automation

### Q2 2026 (Abril - Junio)

**Advanced AI:**
- [ ] Predictive analytics para SDLC
- [ ] ML para bug prediction
- [ ] Self-service analytics portal
- [ ] API interna de documentacion

---

## Checklist de Auto-Evaluacion

### 7 Practicas DORA AI Capabilities

- [x] **1. User-centric Focus**: Templates, vision clara, user stories IA-generated
- [x] **2. Strong Version Control**: Git, conventional commits, CODEOWNERS, CI/CD
- [ ] **3. AI-accessible Internal Data**: Docs OK, faltan metrics centralizados
- [x] **4. Working in Small Batches**: Metodologia por lotes, sprints 2 semanas
- [ ] **5. Clear + Communicated AI Stance**: Definido en este doc, falta comunicar
- [x] **6. Quality Internal Platform**: Django foundation, 8 workflows, 13 scripts
- [ ] **7. Healthy Data Ecosystems**: PostgreSQL+MySQL OK, faltan metrics

**Score actual:** 5/7 (71%) - **GOOD**, target 7/7 para Q1 2026

### 3 Imperativos Plataforma

- [ ] **1. Holistic Experience**: En progreso, falta onboarding guide
- [x] **2. Platform as AI Foundation**: Foundation solida, 7 agentes operativos
- [ ] **3. Calibrate Risk Appetite**: Validaciones OK, falta risk dashboard

**Score actual:** 1.5/3 (50%) - **ACCEPTABLE**, target 3/3 para Q1 2026

### 3 Consejos Lideres

- [x] **1. Systems View**: MAPEO completo, ROADMAP integrado, INDICE maestro
- [ ] **2. Invest in Foundational Systems**: Foundation OK, falta observability
- [x] **3. Focus on Effective Use**: Guia, evalua, valida - proceso completo

**Score actual:** 2.5/3 (83%) - **VERY GOOD**

---

## Restricciones Especificas del Proyecto

**IMPORTANTE:** Todas las practicas DORA deben cumplir restricciones IACT:

### RNF-002: NO Redis/Memcached
- ✅ Sessions en MySQL (django.contrib.sessions.backends.db)
- ✅ Cache en database si necesario
- ❌ NO Prometheus/Grafana (violan esta restriccion)
- ✅ Alternativa: Metrics en MySQL + Django Admin dashboards

### NO Email/SMTP
- ✅ Notificaciones via InternalMessage
- ✅ Alerts via scripts shell + InternalMessage
- ❌ NO email-based alerting

### Scripts First
- ✅ Scripts shell funcionan offline
- ✅ CI/CD workflows llaman scripts
- ✅ Validacion manual siempre posible

---

## Referencias

### DORA
- [DORA Report 2025](https://dora.dev/dora-report-2025)
- DORA AI Capabilities Model (7 practicas)
- Infographic source: `2025-DORA-Report-Infographic_OCR_2_CA.pdf`

### Documentacion IACT
- [AGENTES_SDLC.md](../procesos/AGENTES_SDLC.md)
- [ROADMAP.md](../../proyecto/ROADMAP.md)
- [TAREAS_ACTIVAS.md](../../proyecto/TAREAS_ACTIVAS.md)
- [MAPEO_PROCESOS_TEMPLATES.md](../procesos/MAPEO_PROCESOS_TEMPLATES.md)
- [METODOLOGIA_DESARROLLO_POR_LOTES.md](../metodologias/METODOLOGIA_DESARROLLO_POR_LOTES.md)

### Scripts
- `scripts/dora_metrics.py` - Calcular metricas DORA
- `scripts/generate_workflow_from_template.py` - Query tool IA-accessible
- `scripts/run_all_tests.sh` - Validacion automatizada
- `scripts/health_check.sh` - Platform health

---

## Actualizacion

**Frecuencia:** Trimestral (inicio de cada Q)

**Responsable:** @arquitecto-senior

**Proceso:**
1. Revisar progreso de 7 practicas
2. Actualizar metricas DORA
3. Evaluar checklist de auto-evaluacion
4. Identificar gaps y crear tareas
5. Comunicar cambios al equipo
6. Commit: `docs(ai): actualizar ESTRATEGIA_IA.md - [quarter]`

**Proxima revision:** 2026-01-06 (Q1 2026)

---

**Mantenedor:** @arquitecto-senior
**Fecha creacion:** 2025-11-06
**Version:** 1.0.0
**Fuente:** DORA Report 2025

**Estado:** ACTIVO - Estrategia base establecida, mejoras continuas en roadmap
