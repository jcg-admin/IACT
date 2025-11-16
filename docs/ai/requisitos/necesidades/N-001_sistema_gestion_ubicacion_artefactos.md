---
id: N-001
tipo: necesidad
titulo: Sistema de Gestion Automatica de Ubicacion de Artefactos
dominio: ai
owner: equipo-ba
prioridad: alta
estado: aprobado
fecha_creacion: 2025-11-16
fecha_aprobacion: 2025-11-16
sponsor: arquitecto-senior
stakeholders:
  - arquitecto-ai
  - tech-lead
  - equipo-backend
  - equipo-frontend
  - equipo-devops
babok_knowledge_area: "Business Analysis Planning and Monitoring"
iso29148_clause: "6.2"
valor_negocio: alto
urgencia: alta
---

# Necesidad de Negocio: Sistema de Gestion Automatica de Ubicacion de Artefactos

## 1. Descripcion de la Necesidad

### 1.1 Problema u Oportunidad

Los agentes de IA del proyecto IACT generan continuamente artefactos de documentacion (analisis, ADRs, tareas, guias, reportes, scripts) durante el ciclo SDLC. Actualmente, la colocacion de estos artefactos es manual y ambigua, resultando en:

- **Ubicaciones incorrectas**: Documentos guardados en rutas arbitrarias que no siguen ADR-010 (Arquitectura por Dominios)
- **Nomenclatura inconsistente**: Falta de estandarizacion en nombres de archivos (emojis, CamelCase vs snake_case)
- **Duplicacion de contenido**: Mismo documento guardado en multiples ubicaciones
- **Perdida de trazabilidad**: Dificultad para encontrar artefactos relacionados con requisitos/ADRs
- **Overhead cognitivo**: Desarrolladores pierden tiempo decidiendo donde guardar cada archivo

**Cuantificacion del problema:**
- 15-20 minutos promedio por artefacto para decidir ubicacion correcta
- ~200 artefactos generados por mes
- **50-67 horas/mes de tiempo perdido** en decisiones de ubicacion
- 23% de artefactos colocados en ubicaciones incorrectas (auditoria nov 2025)

### 1.2 Situacion Actual (As-Is)

**Proceso actual:**
1. Agente de IA genera artefacto (ej: analisis de documentacion)
2. Usuario o agente decide manualmente donde guardarlo
3. Se crea archivo con nombre arbitrario
4. Se guarda en ubicacion elegida a criterio del momento
5. Sin validacion de convencion de nombres ni frontmatter

**Impacto negativo:**
- **Tiempo perdido**: 50-67 horas/mes en decisiones manuales
- **Deuda tecnica**: Reorganizaciones masivas cada 2-3 meses (ejemplo: cleanup reciente con 14 commits)
- **Friccion en CI/CD**: PRs rechazados por ubicaciones incorrectas
- **Confusion en equipo**: 5-8 consultas diarias sobre "donde va este archivo"

**Frecuencia del problema:**
- Diario: cada artefacto generado requiere decision manual
- Mensual: ~200 artefactos colocados (23% incorrectamente = 46 archivos mal ubicados/mes)

### 1.3 Situacion Deseada (To-Be)

**Proceso objetivo:**
1. Agente de IA genera artefacto con minimo contexto (tipo, tema, dominio opcional)
2. **Sistema de Placement clasifica automaticamente** el artefacto
3. **Determina ubicacion canonica** segun ADR-010 y GUIA_UBICACIONES_ARTEFACTOS.md
4. **Genera nombre estandarizado** (TASK-001-descripcion.md, ADR-001-titulo.md)
5. **Crea frontmatter YAML apropiado** con trazabilidad
6. **Mueve/guarda archivo automaticamente** en ubicacion correcta
7. **Calcula confianza** y solicita clarificacion si es ambiguo

**Beneficios esperados:**
- **Ahorro de tiempo**: 50-67 horas/mes → 0 horas (100% automatizado)
- **Consistencia**: 100% de artefactos siguiendo convencion
- **Trazabilidad**: Frontmatter automatico con enlaces a requisitos/ADRs
- **Reduccion de deuda tecnica**: Sin reorganizaciones masivas futuras
- **Mejora en developer experience**: Cero friccion al generar documentos

**Criterios de exito:**
- Tiempo de decision de ubicacion: 15-20min → < 5 segundos
- Precision de clasificacion: ≥ 95% (confianza ≥ 0.95)
- Tasa de artefactos mal ubicados: 23% → < 2%
- Adopcion: 100% de agentes SDLC usan PlacementAgent

## 2. Justificacion de Negocio

### 2.1 Impacto en el Negocio

| Dimension | Impacto Actual | Impacto Esperado |
|-----------|----------------|-------------------|
| **Financiero** | 50-67 h/mes × $50/h = **$2,500-3,350/mes perdidos** | $0 perdidos, ROI positivo en < 1 mes |
| **Operacional** | Reorganizaciones masivas cada 2-3 meses (3-5 dias/reorganizacion) | Mantenimiento automatico, 0 reorganizaciones |
| **Cliente** | Friccion en flujo de trabajo, frustacion en equipo | Experiencia fluida, foco en valor de negocio |
| **Estrategico** | Desalineacion con ADR-010 (23% incumplimiento) | 100% alineacion con arquitectura por dominios |

### 2.2 Costo de No Hacer Nada

**Costo anual estimado:**
- Tiempo perdido: 50-67 h/mes × 12 meses × $50/h = **$30,000-40,200/año**
- Reorganizaciones: 4 reorganizaciones/año × 40 h/reorganizacion × $50/h = **$8,000/año**
- **Costo total anual: $38,000-48,200**

**Riesgos asociados:**
- Acumulacion exponencial de deuda tecnica
- Reduccion de velocidad de desarrollo (overhead cognitivo)
- Perdida de trazabilidad compliance/auditoria
- Desmoralizacion de equipo por tareas repetitivas

**Oportunidades perdidas:**
- Tiempo que podria dedicarse a features de negocio
- Automatizacion de otros procesos documentales
- Mejora en metricas DORA (Lead Time for Changes)

## 3. Alcance

### 3.1 En Alcance

- [x] Clasificacion automatica de tipos de artefactos (analisis, ADR, task, guia, script, etc.)
- [x] Determinacion de ubicacion canonica segun ADR-010
- [x] Generacion de nombres estandarizados (Clean Code Naming, sin emojis)
- [x] Generacion de frontmatter YAML apropiado por tipo
- [x] Calculo de confianza de clasificacion
- [x] Integracion con agentes SDLC (PlannerAgent, DesignAgent, TDDAgent, etc.)
- [x] CLI para uso manual por desarrolladores
- [x] Validacion de guardrails (confianza minima, ubicaciones prohibidas)

### 3.2 Fuera de Alcance

- [ ] Movimiento retroactivo de artefactos existentes (migracion masiva)
- [ ] Modificacion de contenido de artefactos (solo clasificacion/ubicacion)
- [ ] Deteccion de duplicados (fase futura)
- [ ] Integracion con GitHub Issues/PRs (fase futura)
- [ ] UI web para gestion visual (fase futura)

### 3.3 Supuestos

1. ADR-010 (Arquitectura por Dominios) es la fuente de verdad para estructura de directorios
2. GUIA_UBICACIONES_ARTEFACTOS.md contiene algoritmo completo de clasificacion
3. Clean Code Naming (sin emojis, snake_case) es obligatorio
4. Agentes SDLC pueden integrarse con PlacementAgent via API Python
5. Proyecto sigue usando Git para control de versiones

### 3.4 Restricciones

1. **Tecnologia**: Debe implementarse en Python 3.11+ (stack actual del proyecto)
2. **Performance**: Clasificacion debe completar en < 500ms por artefacto
3. **Compatibilidad**: Debe funcionar con agent_base.py existente
4. **Sin dependencias externas**: No usar LLMs para clasificacion (usar heuristicas)
5. **Presupuesto**: 0 costo adicional (solo tiempo de desarrollo)

## 4. Stakeholders Afectados

| Stakeholder | Rol | Interes | Impacto | Influencia |
|-------------|-----|---------|---------|------------|
| arquitecto-senior | Sponsor | alto | positivo | alta |
| arquitecto-ai | Implementador | alto | positivo | alta |
| tech-lead | Coordinador | alto | positivo | alta |
| equipo-backend | Usuario | medio | positivo | media |
| equipo-frontend | Usuario | medio | positivo | media |
| equipo-devops | Usuario | medio | positivo | media |
| equipo-ba | Beneficiario | medio | positivo | baja |

## 5. Criterios de Exito

### 5.1 Metricas de Exito (KPIs)

| KPI | Baseline Actual | Target | Metodo de Medicion |
|-----|-----------------|--------|--------------------|
| Tiempo de decision de ubicacion | 15-20 min/artefacto | < 5 seg/artefacto | Benchmark automatizado |
| Precision de clasificacion | N/A (manual) | ≥ 95% confianza | Tests con corpus de 100 artefactos |
| Tasa de artefactos mal ubicados | 23% (auditoria nov 2025) | < 2% | Auditoria mensual automatica |
| Adopcion por agentes SDLC | 0% (no existe) | 100% (todos los agentes) | Code review de integracion |
| Reduccion tiempo en ubicacion | 0% | 95% reduccion | 50-67h/mes → < 2.5h/mes |

### 5.2 Criterios de Aceptacion del Negocio

1. **Clasificacion Precisa**: El sistema clasifica correctamente ≥ 95% de artefactos con confianza ≥ 0.90
2. **Ubicacion Canonica**: 100% de artefactos colocados siguiendo ADR-010 (estructura por dominios)
3. **Nomenclatura Estandar**: 100% de nombres siguen Clean Code Naming (sin emojis, snake_case)
4. **Frontmatter Completo**: Todos los artefactos tienen frontmatter YAML con campos requeridos
5. **Performance**: Clasificacion completa en < 500ms en 99th percentile
6. **Adopcion**: Todos los agentes SDLC integrados en primera semana post-deploy

## 6. Analisis de Alternativas

### 6.1 Opciones Evaluadas

#### Opcion 1: Mantener Proceso Manual

- **Descripcion**: Continuar con decisiones manuales de ubicacion
- **Pros**: Sin costo de desarrollo, sin cambios
- **Contras**: Problema persiste, deuda tecnica crece
- **Costo estimado**: $0 desarrollo, $38,000-48,200/año operacional
- **Tiempo estimado**: N/A

#### Opcion 2: Sistema Automatico con LLM (GPT/Claude)

- **Descripcion**: Usar LLM para clasificar artefactos via prompts
- **Pros**: Alta precision, razonamiento contextual avanzado
- **Contras**: Costo API ($0.01-0.05/artefacto), latencia 1-3seg, dependencia externa
- **Costo estimado**: 2 semanas desarrollo + $2,000-10,000/año API
- **Tiempo estimado**: 2 semanas

#### Opcion 3: Sistema Automatico con Heuristicas (Recomendado)

- **Descripcion**: Algoritmo basado en patrones, nombre, contenido, contexto
- **Pros**: 0 costo recurrente, latencia < 100ms, sin dependencias, determinista
- **Contras**: Menor precision que LLM (95% vs 98%), requiere mantenimiento de reglas
- **Costo estimado**: 1 semana desarrollo, $0 recurrente
- **Tiempo estimado**: 1 semana

### 6.2 Recomendacion

**Opcion seleccionada**: Opcion 3 - Sistema Automatico con Heuristicas

**Justificacion:**
- **Valor**: ROI en < 1 mes ($3,000 desarrollo vs $3,000-4,000/mes ahorrado)
- **Viabilidad**: Implementable con recursos existentes, sin dependencias
- **Riesgo**: Bajo riesgo tecnico, algoritmo ya documentado en GUIA_UBICACIONES_ARTEFACTOS.md
- **Precision**: 95% es suficiente (con fallback a clarificacion humana para < 90% confianza)

## 7. Roadmap de Implementacion

### 7.1 Fases Propuestas

| Fase | Descripcion | Duracion | Dependencias |
|------|-------------|----------|--------------|
| Fase 1: SDLC (N→RN→UC→RF) | Completar flujo SDLC hasta requisitos | 1 dia | ninguna |
| Fase 2: TDD Core Module | Implementar placement module con TDD | 2 dias | Fase 1 |
| Fase 3: PlacementAgent | Wrappear modulo en Agent pattern | 1 dia | Fase 2 |
| Fase 4: Integracion SDLC Agents | Integrar con todos agentes SDLC | 1 dia | Fase 3 |
| Fase 5: Testing & Validacion | Tests E2E, validacion con corpus | 1 dia | Fase 4 |

### 7.2 Hitos Principales

- [x] **Hito 1**: Necesidad N-001 aprobada - 2025-11-16
- [ ] **Hito 2**: Requisitos RF-XXX completos y aprobados - 2025-11-17
- [ ] **Hito 3**: Modulo placement con TDD completo - 2025-11-18
- [ ] **Hito 4**: PlacementAgent funcional - 2025-11-19
- [ ] **Hito 5**: Integracion con agentes SDLC completa - 2025-11-20

## 8. Derivacion a Requisitos

Esta necesidad se descompone en los siguientes requisitos:

### 8.1 Requisitos de Negocio (Business Requirements)

- [ ] RN-001 - El sistema debe clasificar artefactos segun tipo (analisis, ADR, task, guia, etc.)
- [ ] RN-002 - El sistema debe determinar ubicacion canonica siguiendo ADR-010
- [ ] RN-003 - El sistema debe generar nombres siguiendo Clean Code Naming
- [ ] RN-004 - El sistema debe crear frontmatter YAML con trazabilidad

### 8.2 Requisitos de Stakeholders

- [ ] RS-001 - Desarrolladores requieren CLI simple para clasificar artefactos manualmente
- [ ] RS-002 - Agentes SDLC requieren API Python para integracion automatica

### 8.3 Requisitos Funcionales

- [ ] RF-001 - Detectar tipo de artefacto desde nombre y contenido
- [ ] RF-002 - Determinar ownership (transversal vs dominio especifico)
- [ ] RF-003 - Construir ubicacion canonica basada en tipo, ownership, temporalidad
- [ ] RF-004 - Generar nombre estandarizado segun tipo
- [ ] RF-005 - Generar frontmatter YAML apropiado por tipo
- [ ] RF-006 - Calcular confianza de clasificacion
- [ ] RF-007 - Aplicar guardrails (confianza minima, ubicaciones prohibidas)

### 8.4 Requisitos No Funcionales

- [ ] RNF-001 - Performance: Clasificacion en < 500ms p99
- [ ] RNF-002 - Precision: ≥ 95% confianza en clasificacion
- [ ] RNF-003 - Compatibilidad: Python 3.11+, sin dependencias externas
- [ ] RNF-004 - Mantenibilidad: Codigo con coverage ≥ 90%

## 9. Trazabilidad

### 9.1 Trazabilidad Upward (Origen)

Esta necesidad esta alineada con:

- **Objetivo estrategico**: OE-AI-001 - Automatizar procesos documentales del SDLC
- **Iniciativa corporativa**: INIT-DORA-2025 - Mejorar metricas DORA (Lead Time for Changes)
- **ADR**: ADR-010 - Arquitectura por Dominios (fuente de estructura de directorios)

### 9.2 Trazabilidad Downward (Derivados)

Esta necesidad genera:

- **Requisitos de negocio**: RN-001, RN-002, RN-003, RN-004
- **Proyectos/Iniciativas**: PROJ-PLACEMENT-AGENT
- **Entregables**:
  - Modulo placement/ (clasificacion, ubicacion, naming, frontmatter)
  - PlacementAgent (wrapper siguiendo Agent pattern)
  - CLI para uso manual
  - Integracion con agentes SDLC

## 10. Riesgos Identificados

| ID | Riesgo | Probabilidad | Impacto | Mitigacion |
|----|--------|--------------|---------|------------|
| R-01 | Precision < 95% con heuristicas | media | medio | Fallback a clarificacion humana si confianza < 0.90 |
| R-02 | Agentes SDLC no adoptan PlacementAgent | baja | alto | Hacer obligatorio via PR checks, documentacion clara |
| R-03 | GUIA_UBICACIONES_ARTEFACTOS queda desactualizada | media | medio | Validacion automatica de reglas vs estructura real |
| R-04 | Cambios en ADR-010 rompen PlacementAgent | baja | alto | Tests con fixtures siguiendo ADR-010, versionado de algoritmo |

## 11. Aprobaciones

| Rol | Nombre | Fecha | Firma/Aprobacion |
|-----|--------|-------|------------------|
| Sponsor | arquitecto-senior | 2025-11-16 | [x] Aprobado |
| BA Lead | equipo-ba | 2025-11-16 | [x] Aprobado |
| PMO | tech-lead | 2025-11-16 | [x] Aprobado |
| Tech Lead | arquitecto-ai | 2025-11-16 | [x] Revisado |

## 12. Referencias

### 12.1 Documentos Relacionados

- [ADR-010 - Arquitectura por Dominios](../../arquitectura/ADR-010-arquitectura-dominios.md)
- [GUIA_UBICACIONES_ARTEFACTOS.md](../../../gobernanza/guias/GUIA_UBICACIONES_ARTEFACTOS.md)
- [Analisis Cleanup Nov 2025](../../../gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_ESTRUCTURA_20251116.md)

### 12.2 Estandares Aplicados

- **BABOK v3**: Knowledge Area - Business Analysis Planning and Monitoring
- **ISO/IEC/IEEE 29148:2018**: Clause 6.2 - Business Analysis Process
- **Clean Code Naming**: No emojis, snake_case, nombres descriptivos

## Control de Cambios

| Version | Fecha | Autor | Descripcion del Cambio |
|---------|-------|-------|------------------------|
| 1.0 | 2025-11-16 | arquitecto-ai | Creacion inicial |
