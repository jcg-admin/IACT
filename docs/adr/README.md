---
title: Architecture Decision Records (ADRs) - Index
date: 2025-11-16
tipo: indice
categoria: arquitectura
status: active
---

# Architecture Decision Records (ADRs)

## Proposito

Este directorio contiene las decisiones arquitectonicas (Architecture Decision Records - ADRs) del proyecto IACT relacionadas con agentes de automatizacion y validacion.

**Total ADRs en este directorio:** 6

**Ultima actualizacion:** 2025-11-16

---

## Sistema de Numeracion

**Formato Estandar:** `ADR-{NNN}-{descripcion_con_underscores}.md`

- **NNN:** Numero secuencial (001-999)
- **descripcion:** Descripcion corta en snake_case (underscores)
- Prefijo ADR siempre en UPPERCASE
- Ejemplo: `ADR-040-schema_validator_agent.md`

---

## Indice de ADRs

### ADR-040: Schema Validator Agent
**Archivo:** `ADR-040-schema_validator_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation
**Propietario:** @equipo-ai

**Resumen:** Agente de validacion de esquemas para documentacion tecnica.

**Contexto:** Necesidad de validar estructura y formato de archivos de documentacion automaticamente.

---

### ADR-041: DevContainer Validator Agent
**Archivo:** `ADR-041-devcontainer_validator_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation
**Propietario:** @equipo-ai

**Resumen:** Agente de validacion de configuracion DevContainer.

**Contexto:** Asegurar configuracion correcta de entornos de desarrollo containerizados.

---

### ADR-042: Metrics Collector Agent
**Archivo:** `ADR-042-metrics_collector_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation
**Propietario:** @equipo-ai

**Resumen:** Agente de recoleccion de metricas de desarrollo y calidad.

**Contexto:** Automatizar recoleccion de metricas DORA y metricas de calidad de codigo.

---

### ADR-043: Coherence Analyzer Agent
**Archivo:** `ADR-043-coherence_analyzer_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation
**Propietario:** @equipo-ai

**Resumen:** Agente de analisis de coherencia entre documentacion y codigo.

**Contexto:** Detectar inconsistencias entre documentacion tecnica y implementacion real.

---

### ADR-044: Constitution Validator Agent
**Archivo:** `ADR-044-constitution_validator_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation
**Propietario:** @equipo-ai

**Resumen:** Agente de validacion de conformidad con constitucion del proyecto.

**Contexto:** Asegurar que cambios cumplen con principios y restricciones fundamentales del proyecto.

---

### ADR-045: CI Pipeline Orchestrator Agent
**Archivo:** `ADR-045-ci_pipeline_orchestrator_agent.md`
**Estado:** Aceptada
**Fecha:** 2025-11-XX
**Dominio:** AI/Automation + DevOps
**Propietario:** @equipo-ai @equipo-devops

**Resumen:** Agente orquestador de pipelines CI/CD.

**Contexto:** Coordinar ejecucion de multiples agentes de validacion en pipeline de integracion continua.

---

## ADRs Adicionales por Dominio

Para ADRs de otros dominios, consultar:

- **Gobernanza:** `docs/gobernanza/adr/`
- **Backend:** `docs/backend/arquitectura/adr/` (si existe)
- **Frontend:** `docs/frontend/arquitectura/adr/` (si existe)
- **Infraestructura:** `docs/infraestructura/arquitectura/adr/` (si existe)

**Indice maestro de ADRs:** `docs/gobernanza/INDICE_ADRs.md`

---

## Proceso de ADR

### Cuando Crear un ADR

Crear un ADR cuando:
- Se toma una decision arquitectonica significativa
- La decision tiene impacto en multiples dominios
- La decision establece un patron o estandar
- Se necesita documentar el razonamiento detras de una eleccion tecnica

### Como Crear un ADR

1. Copiar plantilla: `docs/gobernanza/adr/plantilla_adr.md`
2. Asignar siguiente numero secuencial
3. Nombrar archivo: `ADR-{NNN}-{descripcion_breve_snake_case}.md`
4. Completar secciones:
   - Contexto
   - Decision
   - Consecuencias
   - Alternativas consideradas
5. Solicitar revision de arquitecto senior
6. Actualizar este indice
7. Actualizar `docs/gobernanza/INDICE_ADRs.md`

### Template ADR

Usar plantilla oficial: `docs/gobernanza/adr/plantilla_adr.md`

---

## Recursos

- **Plantilla ADR:** `docs/gobernanza/adr/plantilla_adr.md`
- **Guia de Estilo:** `docs/gobernanza/GUIA_ESTILO.md`
- **Indice Maestro:** `docs/gobernanza/INDICE_ADRs.md`

---

**Mantenido por:** Equipo de Arquitectura
**Contacto:** @arquitecto-senior
