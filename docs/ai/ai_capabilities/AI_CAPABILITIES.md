---
id: DOC-GOBERNANZA-AI-CAPABILITIES
tipo: checklist
categoria: ai
version: 1.0.0
fecha_creacion: 2025-11-06
propietario: arquitecto-senior
fuente: DORA Report 2025
relacionados: ["ESTRATEGIA_IA.md"]
date: 2025-11-13
---

# AI Capabilities Checklist - DORA 2025

Checklist diario de las 7 practicas clave del DORA AI Capabilities Model.

**Version:** 1.0.0
**Fuente:** [DORA Report 2025](https://dora.dev/dora-report-2025)

---

## Para Developers - Checklist Diario

### Antes de Usar IA

- [ ] **Tengo clara la necesidad del usuario?** (Practica 1: User-centric Focus)
  - Consulte: `docs/proyecto/vision_y_alcance.md`
  - Template: `docs/plantillas/template_necesidad.md`

- [ ] **Mi branch esta actualizado?** (Practica 2: Version Control)
  - `git pull origin main`
  - Feature branch desde main

- [ ] **Tengo acceso a documentacion relevante?** (Practica 3: AI-accessible Data)
  - Consulte: `docs/INDICE.md`
  - Query tool: `python scripts/generate_workflow_from_template.py --interactive`

### Al Usar IA

- [ ] **Estoy trabajando en lote pequeno?** (Practica 4: Small Batches)
  - Task <= 13 story points
  - PR <= 300 lineas
  - Commit cada feature pequena

- [ ] **Uso IA segun stance del proyecto?** (Practica 5: AI Stance)
  - SI: Boilerplate, docs, code review, refactoring, tests
  - NO: Decisiones arquitectonicas criticas, security final, merge sin review
  - Ver: `docs/gobernanza/ai/ESTRATEGIA_IA.md` seccion "Stance de IA"

### Despues de Usar IA

- [ ] **Valide el codigo generado por IA?** (Practica 3: Effective Use)
  - Revise linea por linea
  - Valide contra restricciones (RNF-002: NO Redis, NO Email)
  - Tests escritos o actualizados

- [ ] **Ejecute validaciones locales?** (Practica 6: Quality Platform)
  - `./scripts/run_all_tests.sh`
  - `./scripts/validate_critical_restrictions.sh`
  - Pre-commit hooks (si instalados)

- [ ] **Documentacion actualizada?** (Practica 7: Data Ecosystems)
  - README actualizado si necesario
  - Docstrings agregados
  - CHANGELOG.md actualizado si feature mayor

---

## Para Tech Leads - Checklist Semanal

### Lunes (Planning)

- [ ] **Sprint planning con sistemas view** (Consejo 1: Systems View)
  - Consulte: `docs/proyecto/TAREAS_ACTIVAS.md`
  - Consulte: `docs/gobernanza/procesos/MAPEO_PROCESOS_TEMPLATES.md`
  - Priorice tareas P0-P1

- [ ] **Validar que equipo sigue AI stance** (Practica 5)
  - Review de PRs de semana anterior
  - AI usage apropiado?

### Miercoles (Mid-sprint)

- [ ] **Platform health check** (Practica 6: Quality Platform)
  - `./scripts/health_check.sh`
  - Session table < 50K rows? (`./scripts/cleanup_sessions.sh --dry-run`)

- [ ] **Data ecosystems saludables?** (Practica 7)
  - Backups recientes?
  - Logs no desbordados?

### Viernes (Review)

- [ ] **Metricas DORA actualizadas?**
  - `python scripts/dora_metrics.py --days 7`
  - Deployment frequency mejorando?
  - Lead time reduciendo?

- [ ] **Retrospective con lecciones IA**
  - Que funciono bien con IA esta semana?
  - Que no funciono?
  - Ajustar AI stance si necesario

---

## Para Arquitectos - Checklist Mensual

### Foundation Systems (Consejo 2)

- [ ] **Platform investment review**
  - Django platform estable?
  - Database performance OK?
  - CI/CD workflows funcionando?

- [ ] **AI infrastructure review**
  - 7 agentes SDLC operativos?
  - Scripts de automatizacion funcionando?
  - Documentacion actualizada?

### AI Capabilities Assessment

- [ ] **Score de 7 practicas actualizado**
  - Practica 1 (User-centric): [ ] OK / [ ] Needs work
  - Practica 2 (Version Control): [ ] OK / [ ] Needs work
  - Practica 3 (AI-accessible Data): [ ] OK / [ ] Needs work
  - Practica 4 (Small Batches): [ ] OK / [ ] Needs work
  - Practica 5 (AI Stance): [ ] OK / [ ] Needs work
  - Practica 6 (Quality Platform): [ ] OK / [ ] Needs work
  - Practica 7 (Data Ecosystems): [ ] OK / [ ] Needs work

- [ ] **Score actual: ___/7 (target: 7/7)**

### Risk Calibration (Imperativo 3)

- [ ] **Risk appetite revisado**
  - Incidents este mes: ___
  - Caused by AI misuse: ___
  - Security issues: ___
  - Restricciones violadas: ___ (debe ser 0)

- [ ] **Ajustes necesarios?**
  - Actualizar AI stance?
  - Agregar validaciones?
  - Training adicional?

---

## Para QA - Checklist por Feature

### Pre-Testing

- [ ] **Feature sigue user-centric focus?** (Practica 1)
  - User story clara?
  - Acceptance criteria definidos?

- [ ] **AI-generated code revisado?**
  - Developer hizo code review?
  - Tests incluidos?

### During Testing

- [ ] **Tests automatizados ejecutados?** (Practica 6)
  - `./scripts/run_all_tests.sh`
  - Coverage >= 80%?
  - Security scan passed?

- [ ] **Platform health OK?**
  - `./scripts/health_check.sh`
  - Todos los checks verdes?

### Post-Testing

- [ ] **Documentacion de tests actualizada?** (Practica 7)
  - Test results en `docs/testing/registros/`
  - Issues identificados documentados

- [ ] **Restricciones validadas?**
  - `./scripts/validate_critical_restrictions.sh`
  - RNF-002: NO Redis? [OK]
  - NO Email? [OK]

---

## Metricas Rapidas

### Adoption (Target: 90%)

**Pregunta:** Cuantos en el equipo usan IA diariamente?

- Team size: ___
- Using AI daily: ___
- Adoption rate: ___% (target: >= 90%)

### Productivity (Target: 70%)

**Pregunta:** Cuantos perciben aumento de productividad con IA?

- Team size: ___
- Perceive increase: ___
- Rate: ___% (target: >= 70%)

### Code Quality

**Metricas:**
- Coverage: ___% (target: >= 80%)
- Security critical issues: ___ (target: 0)
- Lint errors: ___ (target: 0)

### DORA Metrics

**Deployment Frequency:**
- Ultimo mes: ___ deploys
- Frequency: ___ per week
- Target Q4 2025: >= 1/week

**Lead Time:**
- Promedio commits: ___ dias
- Target Q4 2025: < 7 dias

**Change Failure Rate:**
- Total changes: ___
- Failed: ___
- Rate: ___% (target: < 20%)

**MTTR:**
- Incidents: ___
- Average recovery: ___ horas
- Target Q4 2025: < 24 horas

---

## Red Flags - Cuando Algo Esta Mal

### AI Misuse Indicators

- [ ] **Pull requests > 500 lineas** - No small batches
- [ ] **AI-generated code sin review** - Missing validation
- [ ] **Restricciones violadas** (Redis, Email) - Critical failure
- [ ] **Tests < 80% coverage** - Quality issue
- [ ] **Security scan failures** - Security risk
- [ ] **Commit sin conventional format** - Version control issue
- [ ] **Documentacion desactualizada** - Data ecosystem problem

**Accion:** Si cualquier red flag: STOP, revisar ESTRATEGIA_IA.md, corregir

---

## Quick Commands

```bash
# Baseline DORA metrics
python scripts/dora_metrics.py --days 30 --format markdown > DORA_baseline.md

# Health check
./scripts/health_check.sh

# Run all tests
./scripts/run_all_tests.sh

# Validate restrictions
./scripts/validate_critical_restrictions.sh

# Query AI-accessible data
python scripts/generate_workflow_from_template.py --interactive

# Session cleanup
./scripts/cleanup_sessions.sh --dry-run
```

---

## Referencias

- **ESTRATEGIA_IA.md**: Estrategia completa
- **ROADMAP.md**: Roadmap de mejoras IA
- **TAREAS_ACTIVAS.md**: Tareas IA en progreso
- **AGENTES_SDLC.md**: Documentacion de agentes

---

## Actualizacion

Este checklist se actualiza cuando:
- AI stance cambia
- Nuevas herramientas IA se adoptan
- Metricas DORA cambian significativamente
- Team size cambia

**Ultima actualizacion:** 2025-11-06
**Version:** 1.0.0
**Mantenedor:** @arquitecto-senior
