---
id: DOC-INDICE-GENERAL
tipo: indice
categoria: documentacion
version: 1.6.0
fecha_creacion: 2025-11-06
fecha_migracion: 2025-11-06
fecha_actualizacion: 2025-11-07
propietario: equipo-gobernanza
archivos_totales: 124
lineas_totales: 37500
relacionados: ["docs_legacy/README.md", "gobernanza/procesos/MAPEO_PROCESOS_TEMPLATES.md", ".claude/workflow_template_mapping.json", "gobernanza/ai/ESTRATEGIA_IA.md", "gobernanza/ai/FASES_IMPLEMENTACION_IA.md", "gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md", "gobernanza/ai/GAPS_SUMMARY_QUICK_REF.md"]
---

# INDICE GENERAL - Documentacion IACT

**VERSION:** 1.6.0
**FECHA MIGRACION:** 2025-11-06
**FECHA ACTUALIZACION:** 2025-11-07
**ARCHIVOS TOTALES:** 124 (+4)
**LINEAS TOTALES:** ~37,500 (+1,700)
**ESTRUCTURA:** BABOK v3 + PMBOK 7 + ISO/IEC/IEEE 29148:2018 + DORA 2025

---

## Proposito

Este indice documenta la estructura completa de documentacion del proyecto IACT despues de la migracion desde docs_legacy/. Toda la documentacion sigue los estandares definidos en GUIA_ESTILO.md.

---

## Navegacion Rapida

| Seccion | Descripcion | Archivos |
|---------|-------------|----------|
| [1. Gobernanza](#1-gobernanza) | Estilos, procesos, procedimientos, lineamientos, mapeos, AI | 41 |
| [2. Proyecto](#2-proyecto) | Vision, tracking, planificacion, roadmap | 5 |
| [3. Requisitos](#3-requisitos) | Analisis de negocio, Business Needs | 8 |
| [4. Implementacion](#4-implementacion) | Infrastructure, agentes, runbooks | 13 |
| [5. Plantillas](#5-plantillas) | Templates reutilizables | 34 |

**Total:** 101 archivos de documentacion (+4)

---

## 1. Gobernanza

Documentacion de estilos, estandares, procesos y lineamientos del proyecto.

### 1.1 Estilos y Estandares

**Ubicacion:** `docs/gobernanza/estilos/`

| Archivo | Descripcion | Lineas | Prioridad |
|---------|-------------|--------|-----------|
| [GUIA_ESTILO.md](gobernanza/estilos/GUIA_ESTILO.md) | Guia oficial de estilo del proyecto (NO emojis, conventional commits, etc) | 786 | CRITICA |
| [estandares_codigo.md](gobernanza/estilos/estandares_codigo.md) | Estandares de codigo Python, JavaScript | - | ALTA |
| [shell_scripting_guide.md](gobernanza/estilos/shell_scripting_guide.md) | Guia de scripting Bash | - | MEDIA |

**Reglas clave:**
- NO usar emojis en ningun documento
- Conventional Commits obligatorio
- Black + isort para Python
- Coverage >= 80%
- Scripts primero, CI/CD despues

---

### 1.2 Procesos

**Ubicacion:** `docs/gobernanza/procesos/`

#### 1.2.1 Agentes

**Ubicacion:** `docs/gobernanza/procesos/agentes/`

| Archivo | Descripcion |
|---------|-------------|
| [README.md](gobernanza/procesos/agentes/README.md) | Indice de agentes y uso |
| [constitution.md](gobernanza/procesos/agentes/constitution.md) | Constitucion de agentes AI |

**Ver tambien:** [AGENTES_SDLC.md](gobernanza/procesos/AGENTES_SDLC.md) - Documentacion completa de 5 agentes SDLC

---

#### 1.2.2 Checklists

**Ubicacion:** `docs/gobernanza/procesos/checklists/`

| Archivo | Descripcion | Uso |
|---------|-------------|-----|
| [README.md](gobernanza/procesos/checklists/README.md) | Indice de checklists | Referencia |
| [checklist_desarrollo.md](gobernanza/procesos/checklists/checklist_desarrollo.md) | Pre-commit, pre-push, PR | Diario |
| [checklist_testing.md](gobernanza/procesos/checklists/checklist_testing.md) | Unit, integration, E2E, coverage | Diario |
| [checklist_cambios_documentales.md](gobernanza/procesos/checklists/checklist_cambios_documentales.md) | Cambios en documentacion | Por necesidad |
| [checklist_trazabilidad_requisitos.md](gobernanza/procesos/checklists/checklist_trazabilidad_requisitos.md) | Trazabilidad Business Need -> Code | Por feature |

**Integracion:** Estos checklists estan integrados en [GUIA_USO.md](gobernanza/ci_cd/GUIA_USO.md) para Developer/QA/DevOps

---

#### 1.2.3 QA

**Ubicacion:** `docs/gobernanza/procesos/`

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [estrategia_qa.md](gobernanza/procesos/estrategia_qa.md) | Estrategia QA oficial (coverage 80%, TDD, metricas) | CRITICA |
| [actividades_garantia_documental.md](gobernanza/procesos/actividades_garantia_documental.md) | Actividades de garantia documental | MEDIA |

**Checklists QA:**
| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [checklist_testing.md](gobernanza/procesos/checklists/checklist_testing.md) | Unit, integration, E2E, coverage | ALTA |
| [checklist_auditoria_restricciones.md](gobernanza/procesos/checklists/checklist_auditoria_restricciones.md) | Auditoria de restricciones IACT (RNF-002, NO Redis) | ALTA |

**Registros de Testing:**
**Ubicacion:** `docs/testing/registros/`

Historico de ejecuciones de pytest y validaciones QA.

**Metricas QA:**
- Cobertura unitaria: >= 80%
- Tiempo medio para corregir fallos criticos: <= 2 dias
- Actividades de control documental: 100% por release

**Integracion:** Vinculado con workflow test-pyramid y procedimiento_qa.md

---

#### 1.2.4 CI/CD

**Ubicacion:** `docs/gobernanza/ci_cd/`

**Ver documentacion completa en:**
- [INDICE.md](gobernanza/ci_cd/INDICE.md) - Indice completo de workflows CI/CD
- [GUIA_USO.md](gobernanza/ci_cd/GUIA_USO.md) - Guias por rol (Developer/QA/DevOps/TechLead)
- [TROUBLESHOOTING.md](gobernanza/ci_cd/TROUBLESHOOTING.md) - Problemas comunes
- [EJEMPLOS.md](gobernanza/ci_cd/EJEMPLOS.md) - Ejemplos end-to-end

**Workflows implementados:** 8 (backend-ci, frontend-ci, test-pyramid, deploy, migrations, infrastructure-ci, security-scan, incident-response)

---

#### 1.2.5 Procedimientos

**Ubicacion:** `docs/gobernanza/procesos/procedimientos/`

**Total:** 11 procedimientos operativos detallados

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [README.md](gobernanza/procesos/procedimientos/README.md) | Indice de procedimientos | ALTA |
| [procedimiento_instalacion_entorno.md](gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md) | Setup inicial de entorno de desarrollo | ALTA |
| [procedimiento_desarrollo_local.md](gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md) | Desarrollo en entorno local | ALTA |
| [procedimiento_qa.md](gobernanza/procesos/procedimientos/procedimiento_qa.md) | Procedimiento de QA | ALTA |
| [procedimiento_diseno_tecnico.md](gobernanza/procesos/procedimientos/procedimiento_diseno_tecnico.md) | Diseno tecnico de features | ALTA |
| [procedimiento_trazabilidad_requisitos.md](gobernanza/procesos/procedimientos/procedimiento_trazabilidad_requisitos.md) | Trazabilidad de requisitos | ALTA |
| [procedimiento_release.md](gobernanza/procesos/procedimientos/procedimiento_release.md) | Procedimiento de release | ALTA |
| [procedimiento_analisis_seguridad.md](gobernanza/procesos/procedimientos/procedimiento_analisis_seguridad.md) | Analisis de seguridad | ALTA |
| [guia_completa_desarrollo_features.md](gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md) | Guia completa de desarrollo | ALTA |
| [procedimiento_revision_documental.md](gobernanza/procesos/procedimientos/procedimiento_revision_documental.md) | Revision de documentos | MEDIA |
| [procedimiento_gestion_cambios.md](gobernanza/procesos/procedimientos/procedimiento_gestion_cambios.md) | Gestion de cambios | MEDIA |

**Caracteristicas:**
- Procedimientos paso a paso para operaciones criticas
- Incluyen comandos especificos
- Troubleshooting integrado
- Ejemplos practicos

---

#### 1.2.6 Mapeo Procesos-Templates-Workflows

**Ubicacion:** `docs/gobernanza/procesos/`

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [MAPEO_PROCESOS_TEMPLATES.md](gobernanza/procesos/MAPEO_PROCESOS_TEMPLATES.md) | Mapeo completo entre procedimientos, workflows CI/CD, templates y agentes SDLC | CRITICA |

**Contenido clave:**
- Matriz de trazabilidad completa (Proceso → Workflow → Template)
- Mapeo por fase SDLC (Planning, Design, Development, Testing, Deployment, Operations)
- Decision trees: Que template usar, que procedimiento seguir, que workflow se ejecuta
- Flujos end-to-end completos (Feature, Bugfix, ETL failure)
- Referencias cruzadas completas

**Uso:** Consultar ANTES de empezar cualquier tarea para saber exactamente que proceso, template y workflow usar.

**Ver tambien:**
- [AGENTES_SDLC.md](gobernanza/procesos/AGENTES_SDLC.md) - Documentacion de agentes
- [procedimientos/README.md](gobernanza/procesos/procedimientos/README.md) - Indice de procedimientos
- [../ci_cd/INDICE.md](gobernanza/ci_cd/INDICE.md) - Indice de workflows
- [../../plantillas/README.md](plantillas/README.md) - Indice de plantillas

---

#### 1.2.7 Metodologias

**Ubicacion:** `docs/gobernanza/metodologias/`

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [README.md](gobernanza/metodologias/README.md) | Indice de metodologias | ALTA |
| [METODOLOGIA_DESARROLLO_POR_LOTES.md](gobernanza/metodologias/METODOLOGIA_DESARROLLO_POR_LOTES.md) | Metodologia de desarrollo incremental por lotes | ALTA |
| [WORKFLOWS_COMPLETOS.md](gobernanza/metodologias/WORKFLOWS_COMPLETOS.md) | Documentacion completa de workflows CI/CD | ALTA |
| [agentes_automatizacion.md](gobernanza/metodologias/agentes_automatizacion.md) | Vision general de agentes IA para automatizacion | MEDIA |
| [arquitectura_agentes_especializados.md](gobernanza/metodologias/arquitectura_agentes_especializados.md) | Arquitectura detallada de agentes SDLC especializados | MEDIA |

**Uso:** Consultar antes de empezar desarrollo para entender metodologia de lotes y uso de agentes IA.

---

#### 1.2.8 Marco Integrado IACT

**Ubicacion:** `docs/gobernanza/marco_integrado/`

**Total:** 8 archivos | **Estandares:** BABOK v3, ISO/IEC/IEEE 29148:2018

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [00_resumen_ejecutivo_mejores_practicas.md](gobernanza/marco_integrado/00_resumen_ejecutivo_mejores_practicas.md) | Resumen ejecutivo del marco integrado | ALTA |
| [01_marco_conceptual_iact.md](gobernanza/marco_integrado/01_marco_conceptual_iact.md) | Marco conceptual completo IACT | ALTA |
| [02_relaciones_fundamentales_iact.md](gobernanza/marco_integrado/02_relaciones_fundamentales_iact.md) | Relaciones entre conceptos BA | ALTA |
| [03_matrices_trazabilidad_iact.md](gobernanza/marco_integrado/03_matrices_trazabilidad_iact.md) | Matrices de trazabilidad completas | ALTA |
| [04_metodologia_analisis_iact.md](gobernanza/marco_integrado/04_metodologia_analisis_iact.md) | Metodologia de analisis reproducible | ALTA |
| [05a_casos_practicos_iact.md](gobernanza/marco_integrado/05a_casos_practicos_iact.md) | Casos practicos reales del proyecto | MEDIA |
| [05b_caso_didactico_generico.md](gobernanza/marco_integrado/05b_caso_didactico_generico.md) | Caso didactico generico | MEDIA |
| [06_plantillas_integradas_iact.md](gobernanza/marco_integrado/06_plantillas_integradas_iact.md) | Plantillas integradas | MEDIA |

**Proposito:** Framework completo de analisis de negocio con trazabilidad desde necesidades hasta implementacion.

---

### 1.3 Archivos Root de Gobernanza

**Ubicacion:** `docs/gobernanza/`

| Archivo | Descripcion |
|---------|-------------|
| [README.md](gobernanza/README.md) | Indice de gobernanza |
| [casos_de_uso_guide.md](gobernanza/casos_de_uso_guide.md) | Guia de casos de uso |
| [documentacion_corporativa.md](gobernanza/documentacion_corporativa.md) | Estandares de documentacion corporativa |
| [lineamientos_gobernanza.md](gobernanza/lineamientos_gobernanza.md) | Lineamientos generales de gobernanza |
| [plan_general.md](gobernanza/plan_general.md) | Plan general del proyecto |
| [registro_decisiones.md](gobernanza/registro_decisiones.md) | Registro de decisiones arquitectonicas (ADRs) |

---

### 1.4 IA y Excelencia con IA (DORA 2025)

**Ubicacion:** `docs/gobernanza/ai/`

**Fuente:** [DORA Report 2025 - AI Capabilities Model](https://dora.dev/dora-report-2025)

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [ESTRATEGIA_IA.md](gobernanza/ai/ESTRATEGIA_IA.md) | Estrategia completa de IA basada en DORA 2025 - 7 practicas AI Capabilities, AI stance del proyecto, roadmap Q4 2025-Q2 2026 | CRITICA |
| [AI_CAPABILITIES.md](gobernanza/ai/AI_CAPABILITIES.md) | Checklist diario de 7 practicas DORA - Para Developers (diario), Tech Leads (semanal), Arquitectos (mensual), QA (por feature) | ALTA |
| [FASES_IMPLEMENTACION_IA.md](gobernanza/ai/FASES_IMPLEMENTACION_IA.md) | Metodologia tecnica 6 fases implementacion IA + Master Workflow Canvas - Planning, Gobierno, Plataforma, Despliegue, Medicion, Escalamiento (144 SP, Q2 2026) | CRITICA |
| [ANALISIS_GAPS_POST_DORA_2025.md](gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md) | Analisis detallado de gaps post-integracion DORA 2025 - Estado 5/7 practicas completas, 2/7 parciales, plan 29 SP para 100%, Q1 2026 | ALTA |
| [GAPS_SUMMARY_QUICK_REF.md](gobernanza/ai/GAPS_SUMMARY_QUICK_REF.md) | Quick reference de gaps criticos y acciones - Sistema metrics (8 SP), Logging (3 SP), Data centralization (5 SP), Quick wins (3h total) | ALTA |
| [DORA_SDLC_INTEGRATION_GUIDE.md](gobernanza/ai/DORA_SDLC_INTEGRATION_GUIDE.md) | Guia integracion DORA + SDLC Agents - Rastreo automatico metricas por fase, DORATrackedSDLCAgent, PDCA automation, GitHub sync | ALTA |
| [DORA_CASSANDRA_INTEGRATION.md](gobernanza/ai/DORA_CASSANDRA_INTEGRATION.md) | Integracion 3 capas observabilidad - DORA (metrics proceso), SDLCAgent (ejecutor), Cassandra (logs runtime), separation of concerns | ALTA |

**Practicas DORA AI Capabilities (7):**
1. **User-centric Focus** - Templates, vision, trazabilidad (Implementado)
2. **Strong Version Control** - Git, CODEOWNERS, CI/CD (Implementado)
3. **AI-accessible Internal Data** - Docs OK, metrics pendientes (Parcial)
4. **Working in Small Batches** - Metodologia por lotes (Implementado)
5. **Clear + Communicated AI Stance** - ESTRATEGIA_IA.md (Implementado)
6. **Quality Internal Platform** - Django + 8 workflows + 13 scripts (Implementado)
7. **Healthy Data Ecosystems** - PostgreSQL+MySQL OK, metrics pendientes (Parcial)

**Score actual:** 5/7 (71%) | **Target Q1 2026:** 7/7 (100%)

**Uso:**
- **ESTRATEGIA_IA.md**: Consultar al inicio de proyecto y mensualmente para vision estrategica
- **AI_CAPABILITIES.md**: Checklist diario para developers, semanal para tech leads
- **FASES_IMPLEMENTACION_IA.md**: Roadmap tecnico de implementacion IA en 6 fases - Consultar al planificar sprints
- **ANALISIS_GAPS_POST_DORA_2025.md**: Analisis completo de gaps post-DORA, estado 5/7 practicas (71%), plan 29 SP para 100% - Consultar al planificar roadmap Q1 2026
- **GAPS_SUMMARY_QUICK_REF.md**: Quick reference de gaps criticos P0-P1, quick wins <3h total - Consultar diario/semanal para priorizar tareas
- **DORA_SDLC_INTEGRATION_GUIDE.md**: Guia para integrar metricas DORA con agentes SDLC - Consultar al desarrollar agentes
- **DORA_CASSANDRA_INTEGRATION.md**: Arquitectura 3 capas (DORA metrics + SDLCAgent + Cassandra logs), separation of concerns - Consultar al implementar observabilidad
- **AI stance**: Define cuando usar/no usar IA en el proyecto

**Ver tambien:**
- [ROADMAP.md](proyecto/ROADMAP.md) - EPICA-006: AI Excellence
- [TAREAS_ACTIVAS.md](proyecto/TAREAS_ACTIVAS.md) - Tareas AI pendientes
- [AGENTES_SDLC.md](gobernanza/procesos/AGENTES_SDLC.md) - Agentes IA implementados

---

## 2. Proyecto

Documentacion de vision, alcance y planificacion del proyecto.

### 2.1 Vision y Alcance

**Ubicacion:** `docs/proyecto/`

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [vision_y_alcance.md](proyecto/vision_y_alcance.md) | Vision y alcance del proyecto IACT | CRITICA |
| [glossary.md](proyecto/glossary.md) | Glosario de terminos del proyecto | ALTA |

**Uso:** Consultar antes de empezar cualquier feature para entender vision y alcance del proyecto.

---

### 2.2 Tracking y Planificacion

**Ubicacion:** `docs/proyecto/`

| Archivo | Descripcion | Prioridad |
|---------|-------------|-----------|
| [ROADMAP.md](proyecto/ROADMAP.md) | Vision estrategica Q4 2025 - Q2 2026, epicas, hitos, metricas DORA | CRITICA |
| [TAREAS_ACTIVAS.md](proyecto/TAREAS_ACTIVAS.md) | Tareas activas < 2 semanas, tracking diario, story points | CRITICA |
| [CHANGELOG.md](proyecto/CHANGELOG.md) | Historial completo de cambios, features completadas, versiones | ALTA |

**Caracteristicas:**
- **ROADMAP.md**: Planificacion quarters, 5 epicas mayores, 3 hitos criticos
- **TAREAS_ACTIVAS.md**: Sistema P0-P3, estados, velocity tracking, burndown
- **CHANGELOG.md**: Formato Keep a Changelog, versionado semantico

**Uso:**
- **ROADMAP.md**: Consultar mensualmente para vision de largo plazo
- **TAREAS_ACTIVAS.md**: Consultar diariamente (standup), actualizar tareas
- **CHANGELOG.md**: Actualizar al completar features mayores o releases

**Reemplaza:** TODO.md en raiz (obsoleto) - Ver nota en TODO.md

---

## 3. Requisitos

Documentacion de requisitos, analisis de negocio, y business needs.

### 3.1 Analisis de Negocio - Marco Integrado

**Ubicacion:** `docs/requisitos/analisis_negocio/marco_integrado/`

**Total:** 7,419 lineas | **Estandares:** ISO/IEC/IEEE 29148:2018, BABOK v3, UML 2.5

| Archivo | Descripcion | Lineas | Seccion |
|---------|-------------|--------|---------|
| [00_resumen_ejecutivo_mejores_practicas.md](requisitos/analisis_negocio/marco_integrado/00_resumen_ejecutivo_mejores_practicas.md) | Resumen ejecutivo del marco integrado | ~800 | Inicio |
| [01_marco_conceptual_iact.md](requisitos/analisis_negocio/marco_integrado/01_marco_conceptual_iact.md) | Marco conceptual IACT | ~1000 | Fundamentos |
| [02_relaciones_fundamentales_iact.md](requisitos/analisis_negocio/marco_integrado/02_relaciones_fundamentales_iact.md) | Relaciones entre conceptos BA | ~900 | Fundamentos |
| [03_matrices_trazabilidad_iact.md](requisitos/analisis_negocio/marco_integrado/03_matrices_trazabilidad_iact.md) | Matrices de trazabilidad completas | ~1200 | Trazabilidad |
| [04_metodologia_analisis_iact.md](requisitos/analisis_negocio/marco_integrado/04_metodologia_analisis_iact.md) | Metodologia de analisis reproducible | ~1000 | Metodologia |
| [05a_casos_practicos_iact.md](requisitos/analisis_negocio/marco_integrado/05a_casos_practicos_iact.md) | Casos practicos reales del proyecto | ~1300 | Ejemplos |
| [05b_caso_didactico_generico.md](requisitos/analisis_negocio/marco_integrado/05b_caso_didactico_generico.md) | Caso didactico generico | ~700 | Ejemplos |
| [06_plantillas_integradas_iact.md](requisitos/analisis_negocio/marco_integrado/06_plantillas_integradas_iact.md) | Plantillas integradas | ~519 | Templates |

**Navegacion:** Los documentos tienen enlaces entre si, empezar por 00_resumen_ejecutivo

**Proposito:** Framework completo de analisis de negocio con:
- Trazabilidad completa desde necesidades hasta implementacion
- Metodologia reproducible para derivar requisitos
- Patrones probados con ejemplos reales
- Conformidad con estandares internacionales

---

### 3.2 Business Needs

**Ubicacion:** `docs/requisitos/business_needs/`

**Estado:** Directorio creado, pendiente migrar solicitudes de cambio (SC00-SC03) desde docs_legacy/solicitudes/

**Estructura futura:**
```
business_needs/
├── BN-001-nombre-corto.md
├── BN-002-nombre-corto.md
└── ...
```

---

## 4. Implementacion

Documentacion tecnica de implementacion, infrastructure, agentes, y runbooks operacionales.

### 4.1 Infrastructure

**Ubicacion:** `docs/implementacion/infrastructure/`

#### 4.1.1 Archivos Root

| Archivo | Descripcion |
|---------|-------------|
| [README.md](implementacion/infrastructure/README.md) | Indice de infrastructure |
| [contenedores_devcontainer.md](implementacion/infrastructure/contenedores_devcontainer.md) | Configuracion de devcontainers |
| [mcp-github-quickstart.md](implementacion/infrastructure/mcp-github-quickstart.md) | Quickstart para MCP GitHub integration |

---

#### 4.1.2 Runbooks

**Ubicacion:** `docs/implementacion/infrastructure/runbooks/`

**Total:** 6 runbooks operacionales

| Runbook | Descripcion | Cuando Usar | Lineas |
|---------|-------------|-------------|--------|
| [verificar_servicios.md](implementacion/infrastructure/runbooks/verificar_servicios.md) | Validar PostgreSQL y MariaDB operativos | Despues de vagrant up, troubleshooting DB | 353 |
| [reprocesar_etl_fallido.md](implementacion/infrastructure/runbooks/reprocesar_etl_fallido.md) | Reprocesar ETL jobs fallidos | Cuando ETL falla | - |
| [merge_y_limpieza_ramas.md](implementacion/infrastructure/runbooks/merge_y_limpieza_ramas.md) | Merge de feature branch y limpieza | Despues de merge a main | - |
| [post_create.md](implementacion/infrastructure/runbooks/post_create.md) | Post-creacion de ambiente | Despues de crear nuevo ambiente | - |
| [claude_code.md](implementacion/infrastructure/runbooks/claude_code.md) | Uso de Claude Code CLI | Troubleshooting Claude Code | - |
| [github_copilot_codespaces.md](implementacion/infrastructure/runbooks/github_copilot_codespaces.md) | GitHub Copilot en Codespaces | Setup de Copilot | - |

**Caracteristicas:**
- Procedimientos paso a paso
- Troubleshooting incluido
- Comandos listos para copiar/pegar
- Output esperado documentado

---

### 4.2 Agentes

**Ubicacion:** `docs/implementacion/agentes/`

#### 4.2.1 Agentes SDLC (Activos)

**Ver:** [docs/gobernanza/procesos/AGENTES_SDLC.md](gobernanza/procesos/AGENTES_SDLC.md)

**Agentes implementados:** 5
1. SDLCPlannerAgent - Planning phase
2. SDLCFeasibilityAgent - Go/No-Go decisions
3. SDLCDesignAgent - HLD/LLD/ADRs
4. SDLCTestingAgent - Test plan/cases
5. SDLCDeploymentAgent - Deployment plans
6. SDLCOrchestratorAgent - Pipeline coordination

**Scripts:** `scripts/ai/agents/sdlc_*.py`

---

#### 3.2.2 Agentes Legacy (Archivado)

**Ubicacion:** `docs/implementacion/agentes/legacy/`

| Archivo | Descripcion |
|---------|-------------|
| [METODOLOGIA_DESARROLLO_POR_LOTES.md](implementacion/agentes/legacy/METODOLOGIA_DESARROLLO_POR_LOTES.md) | Metodologia de desarrollo por lotes (version anterior) |
| [WORKFLOWS_COMPLETOS.md](implementacion/agentes/legacy/WORKFLOWS_COMPLETOS.md) | Workflows completos (version anterior) |
| [agentes_automatizacion.md](implementacion/agentes/legacy/agentes_automatizacion.md) | Agentes de automatizacion (version anterior) |
| [arquitectura_agentes_especializados.md](implementacion/agentes/legacy/arquitectura_agentes_especializados.md) | Arquitectura de agentes (version anterior) |

**Nota:** Contenido legacy para referencia historica. Ver AGENTES_SDLC.md para documentacion actual.

---

## 4. Plantillas

Templates reutilizables para desarrollo, documentacion, y procesos.

**Ubicacion:** `docs/plantillas/`

**Total:** 34 templates

### 4.1 Indice de Plantillas

#### 4.1.1 Templates de Requisitos (5)

| Plantilla | Descripcion | Prioridad |
|-----------|-------------|-----------|
| [template_necesidad.md](plantillas/template_necesidad.md) | Template para necesidad de negocio | ALTA |
| [template_requisito_negocio.md](plantillas/template_requisito_negocio.md) | Template para requisito de negocio | ALTA |
| [template_requisito_funcional.md](plantillas/template_requisito_funcional.md) | Template para requisito funcional | ALTA |
| [template_requisito_no_funcional.md](plantillas/template_requisito_no_funcional.md) | Template para requisito no funcional | ALTA |
| [template_requisito_stakeholder.md](plantillas/template_requisito_stakeholder.md) | Template para requisito stakeholder | MEDIA |

#### 4.1.2 Templates de Desarrollo (10)

| Plantilla | Descripcion | Tamano | Prioridad |
|-----------|-------------|--------|-----------|
| [plantilla_django_app.md](plantillas/plantilla_django_app.md) | Template para crear apps Django | 19 KB | ALTA |
| [plantilla_etl_job.md](plantillas/plantilla_etl_job.md) | Template para crear ETL jobs | 25 KB | ALTA |
| [plantilla_regla_negocio.md](plantillas/plantilla_regla_negocio.md) | Template para reglas de negocio | - | ALTA |
| [plantilla_spec.md](plantillas/plantilla_spec.md) | Template para especificacion tecnica | - | ALTA |
| [plantilla_srs.md](plantillas/plantilla_srs.md) | Template para Software Requirements Specification | - | ALTA |
| [plantilla_tdd.md](plantillas/plantilla_tdd.md) | Template para Test Driven Development | - | ALTA |
| [plantilla_troubleshooting.md](plantillas/plantilla_troubleshooting.md) | Template para troubleshooting | - | ALTA |
| [plantilla_plan.md](plantillas/plantilla_plan.md) | Template para plan generico | - | MEDIA |
| [plantilla_sad.md](plantillas/plantilla_sad.md) | Template para Software Architecture Document | - | MEDIA |
| [plantilla_ui_ux.md](plantillas/plantilla_ui_ux.md) | Template para diseno UI/UX | - | MEDIA |

#### 4.1.3 Templates de Testing (2)

| Plantilla | Descripcion | Prioridad |
|-----------|-------------|-----------|
| [plantilla_plan_pruebas.md](plantillas/plantilla_plan_pruebas.md) | Template para plan de pruebas | MEDIA |
| [plantilla_caso_prueba.md](plantillas/plantilla_caso_prueba.md) | Template para casos de prueba | MEDIA |

#### 4.1.4 Templates de Diseño (2)

| Plantilla | Descripcion | Prioridad |
|-----------|-------------|-----------|
| [plantilla_database_design.md](plantillas/plantilla_database_design.md) | Template para diseno de base de datos | ALTA |
| [plantilla_caso_de_uso.md](plantillas/plantilla_caso_de_uso.md) | Template para casos de uso | ALTA |

#### 4.1.5 Templates de Documentacion (4)

| Plantilla | Descripcion | Prioridad |
|-----------|-------------|-----------|
| [plantilla_api_reference.md](plantillas/plantilla_api_reference.md) | Template para documentacion de APIs | MEDIA |
| [plantilla_espacio_documental.md](plantillas/plantilla_espacio_documental.md) | Template para espacios documentales | BAJA |
| [plantilla_manual_usuario.md](plantillas/plantilla_manual_usuario.md) | Template para manual de usuario | BAJA |
| [plantilla_seccion_limitaciones.md](plantillas/plantilla_seccion_limitaciones.md) | Template para seccion de limitaciones | BAJA |

#### 4.1.6 Templates de Infraestructura y DevOps (4)

| Plantilla | Descripcion | Prioridad |
|-----------|-------------|-----------|
| [plantilla_runbook.md](plantillas/plantilla_runbook.md) | Template para runbook operacional | ALTA |
| [plantilla_deployment_guide.md](plantillas/plantilla_deployment_guide.md) | Template para guia de deployment | MEDIA |
| [plantilla_setup_entorno.md](plantillas/plantilla_setup_entorno.md) | Template para setup de entorno | MEDIA |
| [plantilla_setup_qa.md](plantillas/plantilla_setup_qa.md) | Template para setup QA | MEDIA |

#### 4.1.7 Templates de Gestion (6)

| Plantilla | Descripcion | Tamano | Prioridad |
|-----------|-------------|--------|-----------|
| [plantilla_release_plan.md](plantillas/plantilla_release_plan.md) | Template para plan de release | - | ALTA |
| [plantilla_business_case.md](plantillas/plantilla_business_case.md) | Template para business cases | - | BAJA |
| [plantilla_project_charter.md](plantillas/plantilla_project_charter.md) | Template para project charters | - | BAJA |
| [plantilla_project_management_plan.md](plantillas/plantilla_project_management_plan.md) | Template para plan de gestion | - | MEDIA |
| [plantilla_stakeholder_analysis.md](plantillas/plantilla_stakeholder_analysis.md) | Template para analisis de stakeholders | - | MEDIA |
| [plantilla_registro_actividad.md](plantillas/plantilla_registro_actividad.md) | Template para registros de actividad | 2.1 KB | BAJA |

#### 4.1.8 Indice

| Archivo | Descripcion |
|---------|-------------|
| [README.md](plantillas/README.md) | Indice de plantillas |

### 4.2 Uso de Plantillas

**Proceso:**
1. Copiar plantilla correspondiente
2. Renombrar segun convencion (ej: `BN-001-nombre.md`)
3. Completar metadata en header YAML
4. Completar secciones marcadas con TODO
5. Validar con checklist correspondiente

**Ver tambien:** [plantillas_integradas_iact.md](requisitos/analisis_negocio/marco_integrado/06_plantillas_integradas_iact.md) del marco integrado

---

## 5. Vision y Alcance

Documentacion de vision del proyecto y glosario de terminos.

**Ubicacion:** `docs/vision_y_alcance/`

| Archivo | Descripcion |
|---------|-------------|
| [README.md](vision_y_alcance/README.md) | Vision general del proyecto IACT |
| [glossary.md](vision_y_alcance/glossary.md) | Glosario de terminos y acronimos |

---

## 6. Scripts de Utilidad

Scripts para automatizacion y mantenimiento de documentacion.

**Ubicacion:** `scripts/`

| Script | Descripcion | Uso |
|--------|-------------|-----|
| [clean_emojis.sh](../scripts/clean_emojis.sh) | Limpiar emojis de archivos markdown | `./scripts/clean_emojis.sh <directorio>` |

**Ejemplo:**
```bash
# Limpiar emojis de toda la documentacion
./scripts/clean_emojis.sh docs/

# Limpiar emojis de directorio especifico
./scripts/clean_emojis.sh docs/gobernanza/
```

---

## 7. Estructura Visual Completa

```
docs/
├── INDICE.md                                  [ESTE ARCHIVO]
│
├── gobernanza/
│   ├── estilos/
│   │   ├── GUIA_ESTILO.md                    [786 lines - CRITICA]
│   │   ├── estandares_codigo.md
│   │   └── shell_scripting_guide.md
│   ├── procesos/
│   │   ├── agentes/
│   │   │   ├── README.md
│   │   │   └── constitution.md
│   │   ├── checklists/
│   │   │   ├── README.md
│   │   │   ├── checklist_desarrollo.md
│   │   │   ├── checklist_testing.md
│   │   │   ├── checklist_cambios_documentales.md
│   │   │   └── checklist_trazabilidad_requisitos.md
│   │   ├── qa/
│   │   │   ├── ESTRATEGIA_QA.md              [CRITICA]
│   │   │   ├── README.md
│   │   │   ├── actividades_garantia_documental.md
│   │   │   └── checklist_auditoria_restricciones.md
│   │   ├── AGENTES_SDLC.md                   [109 KB]
│   │   └── INDICE_WORKFLOWS.md
│   ├── ci_cd/
│   │   ├── INDICE.md
│   │   ├── GUIA_USO.md                       [104 KB]
│   │   ├── TROUBLESHOOTING.md                [90 KB]
│   │   └── EJEMPLOS.md                       [85 KB]
│   ├── README.md
│   ├── casos_de_uso_guide.md
│   ├── documentacion_corporativa.md
│   ├── lineamientos_gobernanza.md
│   ├── plan_general.md
│   └── registro_decisiones.md
│
├── requisitos/
│   ├── analisis_negocio/
│   │   └── marco_integrado/                  [7,419 lines total]
│   │       ├── 00_resumen_ejecutivo_mejores_practicas.md
│   │       ├── 01_marco_conceptual_iact.md
│   │       ├── 02_relaciones_fundamentales_iact.md
│   │       ├── 03_matrices_trazabilidad_iact.md
│   │       ├── 04_metodologia_analisis_iact.md
│   │       ├── 05a_casos_practicos_iact.md
│   │       ├── 05b_caso_didactico_generico.md
│   │       └── 06_plantillas_integradas_iact.md
│   └── business_needs/                       [PENDIENTE migrar SC00-SC03]
│
├── implementacion/
│   ├── infrastructure/
│   │   ├── runbooks/
│   │   │   ├── verificar_servicios.md        [353 lines]
│   │   │   ├── reprocesar_etl_fallido.md
│   │   │   ├── merge_y_limpieza_ramas.md
│   │   │   ├── post_create.md
│   │   │   ├── claude_code.md
│   │   │   └── github_copilot_codespaces.md
│   │   ├── README.md
│   │   ├── contenedores_devcontainer.md
│   │   └── mcp-github-quickstart.md
│   └── agentes/
│       └── legacy/
│           ├── METODOLOGIA_DESARROLLO_POR_LOTES.md
│           ├── WORKFLOWS_COMPLETOS.md
│           ├── agentes_automatizacion.md
│           └── arquitectura_agentes_especializados.md
│
├── plantillas/                               [12 templates]
│   ├── README.md
│   ├── plantilla_django_app.md              [19 KB]
│   ├── plantilla_etl_job.md                 [25 KB]
│   ├── plantilla_caso_de_uso.md
│   ├── plantilla_database_design.md
│   ├── plantilla_api_reference.md
│   ├── plantilla_plan_pruebas.md
│   ├── plantilla_caso_prueba.md
│   ├── plantilla_espacio_documental.md
│   ├── plantilla_registro_actividad.md
│   ├── plantilla_business_case.md
│   └── plantilla_project_charter.md
│
└── vision_y_alcance/
    ├── README.md
    └── glossary.md
```

---

## 8. Puntos de Entrada Recomendados

### Para Nuevos Miembros del Equipo

**Empezar aqui:**
1. [vision_y_alcance/README.md](vision_y_alcance/README.md) - Vision general del proyecto
2. [gobernanza/estilos/GUIA_ESTILO.md](gobernanza/estilos/GUIA_ESTILO.md) - Convenciones obligatorias
3. [gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md](gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md) - Setup inicial
4. [gobernanza/procesos/checklists/](gobernanza/procesos/checklists/) - Checklists operacionales

**Por rol:**

**Developer:**
- [gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md](gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md) - Desarrollo local
- [gobernanza/ci_cd/GUIA_USO.md](gobernanza/ci_cd/GUIA_USO.md) - Seccion Developer
- [gobernanza/procesos/checklists/checklist_desarrollo.md](gobernanza/procesos/checklists/checklist_desarrollo.md)
- [plantillas/plantilla_django_app.md](plantillas/plantilla_django_app.md)
- [gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md](gobernanza/procesos/procedimientos/guia_completa_desarrollo_features.md)

**QA:**
- [gobernanza/procesos/qa/ESTRATEGIA_QA.md](gobernanza/procesos/qa/ESTRATEGIA_QA.md)
- [gobernanza/procesos/procedimientos/procedimiento_qa.md](gobernanza/procesos/procedimientos/procedimiento_qa.md)
- [gobernanza/procesos/checklists/checklist_testing.md](gobernanza/procesos/checklists/checklist_testing.md)
- [gobernanza/ci_cd/GUIA_USO.md](gobernanza/ci_cd/GUIA_USO.md) - Seccion QA

**DevOps:**
- [implementacion/infrastructure/runbooks/](implementacion/infrastructure/runbooks/)
- [gobernanza/procesos/procedimientos/procedimiento_release.md](gobernanza/procesos/procedimientos/procedimiento_release.md)
- [gobernanza/ci_cd/GUIA_USO.md](gobernanza/ci_cd/GUIA_USO.md) - Seccion DevOps
- [gobernanza/ci_cd/TROUBLESHOOTING.md](gobernanza/ci_cd/TROUBLESHOOTING.md)
- [plantillas/plantilla_runbook.md](plantillas/plantilla_runbook.md)

**Business Analyst:**
- [requisitos/analisis_negocio/marco_integrado/00_resumen_ejecutivo_mejores_practicas.md](requisitos/analisis_negocio/marco_integrado/00_resumen_ejecutivo_mejores_practicas.md)
- [gobernanza/casos_de_uso_guide.md](gobernanza/casos_de_uso_guide.md)
- [gobernanza/procesos/procedimientos/procedimiento_trazabilidad_requisitos.md](gobernanza/procesos/procedimientos/procedimiento_trazabilidad_requisitos.md)
- [plantillas/template_necesidad.md](plantillas/template_necesidad.md)
- [plantillas/plantilla_caso_de_uso.md](plantillas/plantilla_caso_de_uso.md)

**Tech Lead:**
- [gobernanza/procesos/AGENTES_SDLC.md](gobernanza/procesos/AGENTES_SDLC.md)
- [gobernanza/procesos/procedimientos/procedimiento_diseno_tecnico.md](gobernanza/procesos/procedimientos/procedimiento_diseno_tecnico.md)
- [gobernanza/registro_decisiones.md](gobernanza/registro_decisiones.md)
- [gobernanza/ci_cd/INDICE.md](gobernanza/ci_cd/INDICE.md)
- [gobernanza/procesos/procedimientos/procedimiento_analisis_seguridad.md](gobernanza/procesos/procedimientos/procedimiento_analisis_seguridad.md)

---

## 9. Restricciones IACT (Criticas)

**Definidas en:** [gobernanza/procesos/qa/checklist_auditoria_restricciones.md](gobernanza/procesos/qa/checklist_auditoria_restricciones.md)

### RNF-002: NO Redis/Memcached
- Sesiones DEBEN estar en MySQL: `django.contrib.sessions.backends.db`
- Cache PUEDE usar MySQL o filesystem
- PROHIBIDO: Redis, Memcached, cualquier servicio externo de cache

### NO Email/SMTP
- PROHIBIDO: Envio de emails por SMTP
- USAR: `InternalMessage.objects.create()` para notificaciones internas
- ALTERNATIVA: Notificaciones in-app

### NO Emojis/Iconos
- PROHIBIDO: Emojis UTF-8 en codigo, docs, commits
- USAR: Texto ASCII ([OK], [FAIL], [WARNING])
- VALIDACION: Script `clean_emojis.sh`

### Scripts Primero, CI/CD Despues
- Scripts shell DEBEN funcionar offline/local
- Workflows CI/CD SOLO llaman scripts
- NO duplicar logica en workflows

**Ver:** [gobernanza/estilos/GUIA_ESTILO.md](gobernanza/estilos/GUIA_ESTILO.md) para todas las restricciones

---

## 10. Metricas de Calidad

**Definidas en:** [gobernanza/procesos/qa/ESTRATEGIA_QA.md](gobernanza/procesos/qa/ESTRATEGIA_QA.md)

| Metrica | Target | Fuente |
|---------|--------|--------|
| Cobertura de codigo | >= 80% | pytest --cov |
| Test Pyramid | 60% Unit / 30% Integration / 10% E2E | pytest |
| Complejidad ciclomatica | <= 10 | radon |
| Longitud de funciones | <= 50 lineas | manual |
| Longitud de archivos | <= 500 lineas | manual |
| Tamano de PR | <= 400 lineas | manual |
| MTTR (criticos) | <= 2 dias | registros QA |

---

## 11. Workflows CI/CD

**Ver documentacion completa:** [gobernanza/ci_cd/INDICE.md](gobernanza/ci_cd/INDICE.md)

**Workflows implementados:** 8

1. **backend-ci.yml** - CI para backend (tests, coverage, RNF-002)
2. **frontend-ci.yml** - CI para frontend (tests, lint, build)
3. **test-pyramid.yml** - Validacion test pyramid (60/30/10)
4. **deploy.yml** - Deployment staging/production (blue-green)
5. **migrations.yml** - Validacion de migraciones Django
6. **infrastructure-ci.yml** - CI para infrastructure as code
7. **security-scan.yml** - Security scanning (Bandit, secrets, SQL injection)
8. **incident-response.yml** - Automatizacion de respuesta a incidentes

**Scripts locales:**
- `scripts/ci/backend_test.sh`
- `scripts/ci/frontend_test.sh`
- `scripts/ci/test_pyramid_check.sh`
- `scripts/ci/security_scan.sh`

---

## 12. Historial de Migracion

| Fecha | Version | Cambios | Archivos | Commit |
|-------|---------|---------|----------|--------|
| 2025-11-06 | 1.0.0 | Migracion inicial desde docs_legacy/ (Fases 1-5) | 56 | 2700591 |
| 2025-11-06 | 1.0.1 | Creacion de INDICE.md maestro | +1 | 0062e64 |
| 2025-11-06 | 1.1.0 | Fases 6-7: Procedimientos (11) + Plantillas (22) | +33 | 1c28337 |
| 2025-11-06 | 1.2.0 | Creacion de MAPEO_PROCESOS_TEMPLATES.md | +1 | PENDING |

**Total migrado:** 90 archivos

**Detalles de migracion:**
- Origen: `docs_legacy/` (estructura anterior pre-BABOK v3 + PMBOK 7)
- Destino: `docs/` (nueva estructura organizacional)
- Archivos migrados: 89 (de 125 totales en docs_legacy/)
- Archivos creados: 1 (MAPEO_PROCESOS_TEMPLATES.md)
- Total archivos activos: 90
- Lineas totales: ~30,000
- Transformaciones: Limpieza de emojis en 10 archivos
- Archivos NO migrados: Registros historicos (qa/registros/), legacy_analysis/, solicitudes/

**Fases completadas:**
- FASE 1-5: Fundamentos, Operaciones, Framework BA, Agentes, Archivos root
- FASE 6: Procedimientos gobernanza (11 archivos)
- FASE 7: Plantillas faltantes (22 archivos)
- MAPEO: Documento maestro de mapeo Procesos-Templates-Workflows (1 archivo)

**Ver:** [docs_legacy/README.md](../docs_legacy/README.md) para detalles de archivado

---

## 13. Proximos Pasos (Pendientes)

### 13.1 Migracion Pendiente (Prioridad BAJA)

- [ ] Migrar solicitudes SC00-SC03 desde `docs_legacy/solicitudes/` a `docs/requisitos/business_needs/` (22 archivos)
- [ ] Migrar archivos restantes de baja prioridad (planificacion_y_releases, diseno_detallado, procedimientos) (4 archivos)
- [ ] Revisar overlap entre `docs/implementacion/agentes/legacy/` y `docs/gobernanza/procesos/AGENTES_SDLC.md`
- [ ] Consolidar documentacion duplicada si existe

**Archivos pendientes:** 26 de 125 (21%)
**Progreso:** 89 migrados (71%), 10 archivados (8%)

### 13.2 Mejoras Futuras

- [ ] Crear indice de ADRs (Architecture Decision Records)
- [ ] Automatizar validacion de metadata en headers YAML
- [ ] Crear script de validacion de links rotos
- [ ] Generar visualizacion grafica de estructura (Mermaid diagrams)

---

## 14. Mantenimiento de Este Indice

**Responsable:** Equipo Gobernanza

**Cuando actualizar:**
- Al agregar nuevos directorios bajo `docs/`
- Al migrar contenido desde `docs_legacy/`
- Al crear nuevas plantillas
- Al agregar nuevos procesos/checklists
- Cambios mayores en estructura

**Proceso:**
1. Actualizar este INDICE.md
2. Actualizar metadata (version, fecha)
3. Commit con mensaje: `docs(indice): actualizar INDICE.md - <descripcion>`
4. Notificar al equipo

---

## 15. Contacto y Soporte

**Para preguntas sobre:**
- **Estructura de documentacion:** Equipo Gobernanza
- **GUIA_ESTILO.md:** Tech Lead
- **Requisitos y BA:** BA Lead
- **QA y Testing:** QA Lead
- **CI/CD:** DevOps Lead
- **Runbooks:** Equipo DevOps

---

## 16. Referencias Externas

### Estandares

- [BABOK v3](https://www.iiba.org/standards-and-resources/babok/) - Business Analysis Body of Knowledge
- [PMBOK 7](https://www.pmi.org/pmbok-guide-standards) - Project Management Body of Knowledge
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) - Requirements Engineering
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

### Guias de Estilo

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 8](https://pep8.org/) - Style Guide for Python Code
- [PEP 257](https://www.python.org/dev/peps/pep-0257/) - Docstring Conventions

---

**FIN DEL INDICE**

**VERSION:** 1.0.0
**ULTIMA ACTUALIZACION:** 2025-11-06
**ARCHIVOS TOTALES:** 58
**ESTRUCTURA COMPLETA Y OPERACIONAL**
