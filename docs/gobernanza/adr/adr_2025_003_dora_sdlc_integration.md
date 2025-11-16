---
id: ADR-2025-003
estado: aceptada
propietario: arquitecto-senior
ultima_actualizacion: 2025-11-06
relacionados:
  [
    "FASES_IMPLEMENTACION_IA.md",
    "ESTRATEGIA_IA.md",
    "AGENTES_SDLC.md",
    "ADR-002",
  ]
---

# ADR-2025-003: Integracion DORA Metrics con SDLC Agents

**Estado:** aceptada

**Fecha:** 2025-11-06

**Decisores:** Arquitecto Senior, Tech Lead, DevOps Lead

**Contexto tecnico:** Full-stack (Backend + Infrastructure + AI/ML)

## Contexto y Problema

El proyecto IACT ha implementado 16+ agentes SDLC especializados para automatizar
el ciclo de desarrollo (planning, design, testing, deployment, maintenance).
Sin embargo, carecemos de visibilidad sobre el impacto real de estos agentes
en las metricas clave de performance de entrega de software.

**Preguntas clave:**

- Como medimos si los agentes IA estan mejorando nuestro delivery performance?
- Como validamos que cambios en agentes no degradan metricas criticas?
- Como implementamos mejora continua basada en datos (no intuicion)?
- Como escalamos practicas exitosas a toda la organizacion?

**Restricciones actuales:**

- RNF-002: NO Redis - Solo PostgreSQL, MySQL, SQLite
- RNF-NO-EMOJIS: NO emojis en codigo/docs/commits
- Sin herramientas de APM externas (Prometheus/Grafana bloqueadas)
- Metricas DORA baseline no establecidas (GITHUB_TOKEN pendiente)

**Impacto:**

- Sin metricas objetivas, no podemos demostrar ROI de agentes IA
- Ciclos PDCA manuales (lentos, inconsistentes, propensos a sesgo)
- No hay deteccion temprana de regresiones
- Practicas exitosas no se documentan ni escalan

## Factores de Decision

| Factor             | Peso    | Descripcion                                                 |
| ------------------ | ------- | ----------------------------------------------------------- |
| **Performance**    | ALTA    | Overhead minimo (<5% duracion pipeline)                     |
| **Escalabilidad**  | ALTA    | Soportar 100+ ciclos SDLC concurrentes                      |
| **Complejidad**    | MEDIA   | Integracion transparente (sin cambios a agentes existentes) |
| **Costo**          | BAJA    | Usar solo recursos existentes (MySQL, filesystem)           |
| **Seguridad**      | ALTA    | No exponer datos sensibles en metricas                      |
| **Compatibilidad** | CRITICA | Compatible con RNF-002 (NO Redis)                           |
| **Madurez**        | MEDIA   | DORA framework validado (10+ years research)                |
| **Comunidad**      | ALTA    | DORA Report 2025 + Google DORA research                     |

## Opciones Consideradas

### Opcion 1: DORA Metrics via GitHub API (Baseline Manual)

**Descripcion:**
Usar unicamente GitHub API para calcular metricas DORA, ejecutando
scripts manualmente segun necesidad.

**Implementacion:**

```python
# scripts/dora_metrics.py (existente)
python scripts/dora_metrics.py --repo owner/repo --days 30
```

**Pros:**

- OK Simple de implementar (script ya existe)
- OK No requiere almacenamiento adicional
- OK Datos auditables (GitHub como fuente de verdad)
- OK Sin overhead en pipeline SDLC

**Contras:**

- NO Requiere GITHUB_TOKEN (bloqueado actualmente)
- NO Manual (no automatico)
- NO No rastrea metricas por fase SDLC
- NO No integra con ciclos PDCA
- NO Granularidad limitada (solo nivel commit/PR)

---

### Opcion 2: APM Externo (Prometheus + Grafana)

**Descripcion:**
Usar stack de observabilidad externa (Prometheus metrics + Grafana dashboards)
para rastrear metricas DORA en tiempo real.

**Implementacion:**

```python
from prometheus_client import Counter, Histogram

deployment_counter = Counter('deployments_total', 'Total deployments')
lead_time_histogram = Histogram('lead_time_seconds', 'Lead time distribution')
```

**Pros:**

- OK Visualizacion rica (dashboards Grafana)
- OK Alertas en tiempo real
- OK Retention configurable
- OK Amplia adopcion en industria

**Contras:**

- NO Viola RNF-002 (Prometheus requiere infraestructura adicional)
- NO Complejidad operacional (setup, mantenimiento)
- NO Costo de learning curve (nuevo stack)
- NO Overhead de networking (metricas push)

---

### Opcion 3: Integracion DORA + SDLC Agents (In-Process Tracking)

**Descripcion:**
Extender agentes SDLC existentes para rastrear metricas DORA automaticamente
durante cada fase del ciclo. Almacenar metricas localmente (JSON + MySQL futuro).
Integrar con PDCA automation agent para mejora continua.

**Implementacion:**

```python
from agents.dora_sdlc_integration import DORATrackedSDLCAgent

class MyAgent(DORATrackedSDLCAgent):
    def run(self, input_data):
        # Logica del agente
        return result
    # Metricas registradas automaticamente

# Storage
.dora_sdlc_metrics.json  # Persistencia local
MySQL metrics table      # Futuro (P0 - 8 SP)
```

**Pros:**

- OK Automatico (sin intervencion manual)
- OK Granularidad fase-a-fase (planning -> deployment)
- OK Compatible RNF-002 (solo MySQL + filesystem)
- OK Overhead minimo (<1% duracion pipeline)
- OK Integra con PDCA automation agent
- OK Escalable (clase base DORATrackedSDLCAgent)
- OK Sin emojis (RNF-NO-EMOJIS compliant)

**Contras:**

- NO Requiere refactor agentes existentes (minimo: heredar de nueva clase)
- NO Storage local (hasta implementar MySQL metrics)
- NO No reemplaza GitHub API (complementa)

---

### Opcion 4: Logging Estructurado + Post-Procesamiento

**Descripcion:**
Los agentes escriben logs estructurados (JSON), un script posterior
analiza logs y calcula metricas DORA.

**Implementacion:**

```python
import logging
logging.info(json.dumps({
    'phase': 'planning',
    'duration': 300.0,
    'decision': 'go'
}))

# Post-procesamiento
python scripts/analyze_logs.py --days 7
```

**Pros:**

- OK No invasivo (solo logging)
- OK Flexible (analisis offline)
- OK Compatible con cualquier stack

**Contras:**

- NO Manual (requiere ejecutar script)
- NO Parsing complejo (logs multi-linea)
- NO No tiempo real
- NO Dificil correlacionar fases de mismo ciclo

## Decision

**Opcion elegida:** "Opcion 3: Integracion DORA + SDLC Agents (In-Process Tracking)"

**Justificacion:**

1. **Automatizacion Completa:**
   - Rastreo automatico sin intervencion manual
   - Metricas disponibles inmediatamente al completar ciclo
   - Feedback loop rapido (< 5 min)

2. **Compatibilidad Total:**
   - Cumple RNF-002 (NO Redis, solo MySQL + filesystem)
   - Cumple RNF-NO-EMOJIS (ASCII only)
   - No requiere infraestructura adicional (APM, etc)

3. **Integracion Natural:**
   - Extiende agentes SDLC existentes (DORATrackedSDLCAgent)
   - Minimo overhead (<1% duracion pipeline)
   - Transparente para developers

4. **Escalabilidad PDCA:**
   - Integra con PDCA automation agent (Fase 5: T5.5)
   - Decisiones automaticas (APPLY, REVERT, ESCALATE)
   - Ciclos de mejora continua semanales

5. **Roadmap Claro:**
   - Fase 1: Storage local (.dora_sdlc_metrics.json) - COMPLETADO
   - Fase 2: MySQL metrics table (P0 - 8 SP) - Q4 2025
   - Fase 3: Django Admin dashboards (P2 - 5 SP) - Q1 2026
   - Fase 4: GitHub API sync (P1 - 3 SP) - Q1 2026

**Trade-offs aceptados:**

- Storage local inicial (hasta MySQL implementado)
- Refactor minimo agentes existentes (heredar DORATrackedSDLCAgent)
- No reemplaza GitHub API (la complementa)

## Consecuencias

### Positivas

- OK Metricas DORA automaticas por cada feature/issue
- OK Deteccion temprana de regresiones (< 5 min)
- OK Validacion objetiva de mejoras IA (A/B testing)
- OK Ciclos PDCA automatizados (decision en segundos)
- OK Trazabilidad completa (fase-a-fase, feature-level)
- OK ROI cuantificable (Lead Time -25%, CFR -20%, etc.)
- OK Base para escalamiento organizacional (Fase 6)

### Negativas

- WARNING Requiere refactor agentes: heredar de DORATrackedSDLCAgent
- WARNING Storage local temporal (hasta MySQL implementado)
- WARNING Metricas baseline requieren GITHUB_TOKEN (bloqueado)
- WARNING Sin visualizacion rica inicial (hasta Django Admin dashboards)

### Neutrales

- INFO Agentes mantienen compatibilidad hacia atras
- INFO Almacenamiento JSON simple (< 1 MB por 1000 ciclos)
- INFO PDCA agent requiere 48h estabilizacion post-cambio

## Plan de Implementacion

### 1. Fase 1: Core Integration (COMPLETADO - 2025-11-06)

**Acciones:**

- [x] Crear DORAMetrics class (in-memory tracking)
- [x] Crear DORATrackedSDLCAgent (base class)
- [x] Implementar @dora_tracked decorator
- [x] Storage persistente (.dora_sdlc_metrics.json)
- [x] Crear PDCA automation agent
- [x] Documentar workflow (WORKFLOW_AGENTES_DORA.md)
- [x] Crear ADR-2025-003 (este documento)

**Timeframe:** 1 dia (COMPLETADO)

**Archivos creados:**

- `scripts/ai/agents/dora_sdlc_integration.py` (536 lineas)
- `scripts/ai/agents/pdca_automation_agent.py` (658 lineas)
- `docs/gobernanza/ai/DORA_SDLC_INTEGRATION_GUIDE.md` (500 lineas)
- `docs/gobernanza/procesos/agentes/WORKFLOW_AGENTES_DORA.md` (800 lineas)

### 2. Fase 2: Refactor Existing Agents (P1 - 5 SP)

**Acciones:**

- [ ] Refactor SDLCPlannerAgent -> DORATrackedSDLCAgent
- [ ] Refactor SDLCDesignAgent -> DORATrackedSDLCAgent
- [ ] Refactor TestRunner -> DORATrackedSDLCAgent
- [ ] Crear DeploymentAgent (nuevo) con DORA tracking
- [ ] Crear MaintenanceAgent (nuevo) para MTTR tracking

**Timeframe:** 1 semana

**Validacion:**

- Tests unitarios pasan (>90% coverage)
- Metricas registradas correctamente (.dora_sdlc_metrics.json)
- No regresion en performance (<1% overhead)

### 3. Fase 3: MySQL Metrics Storage (P0 - 8 SP)

**Acciones:**

- [ ] Disenar schema MySQL (dora_metrics table)
- [ ] Migration script (JSON -> MySQL)
- [ ] Update DORAMetrics class (MySQL backend)
- [ ] Queries optimizadas (indexes, partitioning)
- [ ] Retention policy (90 dias default)

**Timeframe:** 2 semanas

**Schema:**

```sql
CREATE TABLE dora_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cycle_id VARCHAR(50) UNIQUE NOT NULL,
    feature_id VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    phase_name VARCHAR(50) NOT NULL,
    decision VARCHAR(20),
    duration_seconds DECIMAL(10,2),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_feature (feature_id),
    INDEX idx_start_time (start_time),
    INDEX idx_phase (phase_name)
) ENGINE=InnoDB;
```

### 4. Fase 4: Django Admin Dashboards (P2 - 5 SP)

**Acciones:**

- [ ] ModelAdmin para DORACycle
- [ ] Custom views (metrics summary)
- [ ] Graficos (Chart.js): DF, LT, CFR, MTTR
- [ ] Filtros: feature_id, date range, developer
- [ ] Export CSV/JSON

**Timeframe:** 1.5 semanas

**URL:** `/admin/dora/metrics/`

### 5. Fase 5: GitHub API Sync (P1 - 3 SP)

**Acciones:**

- [ ] Obtener GITHUB_TOKEN (prerequisito)
- [ ] Cron job diario: sync local + GitHub
- [ ] Combined report generator
- [ ] Detectar discrepancias (alertas)

**Timeframe:** 1 semana

**Cron:**

```bash
0 2 * * * python scripts/sync_dora_github.py --repo 2-Coatl/IACT---project
```

### 6. Fase 6: PDCA Automation Operational (P1 - 2 SP)

**Acciones:**

- [ ] Configurar ciclos PDCA semanales (viernes 17:00)
- [ ] Thresholds production (auto_apply: 15%, auto_revert: -5%)
- [ ] Alertas Slack/email en ESCALATE
- [ ] Documentar decisiones PDCA (changelog)

**Timeframe:** 3 dias

**Cron:**

```bash
0 17 * * 5 python scripts/ai/agents/pdca_automation_agent.py --auto-execute
```

## Validacion y Metricas

### Criterios de Exito

**Fase 2 (Refactor Agents):**

- Metrica 1: 100% agentes SDLC con DORA tracking
- Metrica 2: <1% overhead en pipeline duration
- Metrica 3: >95% metricas registradas correctamente

**Fase 3 (MySQL Storage):**

- Metrica 1: <100ms query latency (p95)
- Metrica 2: <5 MB storage per 1000 cycles
- Metrica 3: 100% migracion datos JSON -> MySQL

**Fase 4 (Dashboards):**

- Metrica 1: <2s page load time
- Metrica 2: >80% developer satisfaction (survey)
- Metrica 3: 100% metricas visibles en UI

**Fase 5 (GitHub Sync):**

- Metrica 1: <5% discrepancia local vs GitHub
- Metrica 2: 100% sync success rate
- Metrica 3: <10 min sync duration

**Fase 6 (PDCA Operational):**

- Metrica 1: >=1 ciclo PDCA semanal ejecutado
- Metrica 2: >=15% mejora promedio en metricas DORA
- Metrica 3: <5% decisiones ESCALATE (mayoria APPLY/CONTINUE)

### Como medir

**Metricas DORA:**

```bash
# Local
python scripts/ai/agents/dora_sdlc_integration.py

# GitHub
python scripts/dora_metrics.py --days 30

# PDCA history
python scripts/ai/agents/pdca_automation_agent.py --show-history
```

**Performance overhead:**

```bash
# Medir duracion pipeline sin/con DORA tracking
time python scripts/sdlc_agent.py --phase planning --input "..."

# Analizar .dora_sdlc_metrics.json
jq '.cycles[].phases[].duration_seconds' .dora_sdlc_metrics.json | awk '{s+=$1; c++} END {print s/c}'
```

**Validacion MySQL:**

```sql
-- Count cycles
SELECT COUNT(*) FROM dora_metrics;

-- Avg Lead Time
SELECT AVG(duration_seconds) FROM dora_metrics WHERE phase_name = 'deployment';

-- Top features by CFR
SELECT feature_id, AVG(metadata->>'$.change_failure_rate') as cfr
FROM dora_metrics
WHERE phase_name = 'testing'
GROUP BY feature_id
ORDER BY cfr DESC
LIMIT 10;
```

### Revision

- **Fecha de revision programada:** 2025-11-20 (post Sprint 1 validacion)
- **Responsable de seguimiento:** Arquitecto Senior + DevOps Lead
- **Metricas a revisar:**
  - Lead Time promedio (target: < 4 horas)
  - Deployment Frequency (target: >= 1/dia)
  - Change Failure Rate (target: <= 15%)
  - MTTR (target: <= 1 hora)
  - Overhead pipeline (target: < 1%)

## Alternativas Descartadas

### Herramientas SaaS (DataDog, New Relic, Honeycomb)

**Por que se descarto:**

- Costo alto ($$$ por agente/mes)
- Vendor lock-in
- Datos sensibles en cloud externo
- Overhead de networking
- Viola principio self-hosted del proyecto

### Logs centralizados (ELK Stack)

**Por que se descarto:**

- Complejidad operacional (Elasticsearch cluster)
- Overhead almacenamiento (logs crecen rapido)
- Post-procesamiento manual
- Viola RNF-002 (requiere infraestructura adicional)

### Metricas custom en PostgreSQL

**Por que se descarto:**

- PostgreSQL ya usado para datos de negocio
- Separacion de concerns (metrics != business data)
- MySQL mas eficiente para time-series (partitioning)
- Riesgo de contention en DB principal

## Referencias

- [DORA Report 2025](https://dora.dev/)
- [DORA Metrics: Four Keys](https://dora.dev/guides/dora-metrics-four-keys/)
- [Google DORA Research](https://cloud.google.com/blog/products/devops-sre/announcing-dora-2025-accelerate-state-of-devops-report)
- FASES_IMPLEMENTACION_IA.md (Fase 1: T1.2, Fase 5: T5.1, T5.5)
- ESTRATEGIA_IA.md (Practica 3: AI-accessible Internal Data)
- DORA_SDLC_INTEGRATION_GUIDE.md (guia tecnica completa)
- WORKFLOW_AGENTES_DORA.md (workflow operacional)
- ADR-002: Suite Calidad Codigo (contexto agentes SDLC)

## Notas Adicionales

- **Fecha de discusion inicial:** 2025-11-06
- **Participantes:** Arquitecto Senior, Tech Lead, DevOps Lead
- **POC realizado:** Si - dora_sdlc_integration.py + pdca_automation_agent.py
- **Commits relacionados:**
  - `edada09` - feat(ai): implementar agentes DORA Fase 5 y integracion SDLC
  - `95ec23e` - feat(ai): completar 6 FASES implementacion IA + Master Workflow Canvas

- **Integracion con FASES_IMPLEMENTACION_IA.md:**
  - Fase 1 T1.2: Medicion DORA base (dora_metrics.py)
  - Fase 5 T5.1: Automatizar medicion continua (dora_sdlc_integration.py)
  - Fase 5 T5.5: Ciclo PDCA automatizado (pdca_automation_agent.py)
  - Fase 6 T6.4: Onboarding automation (futuro)

- **Restricciones criticas respetadas:**
  - RNF-002: NO Redis - Solo MySQL + filesystem
  - RNF-NO-EMOJIS: ASCII only en todo el codigo
  - Self-hosted: Sin dependencias cloud externas

---

**VERSION:** 1.0.0
**ESTADO:** Aceptada
**PROXIMA REVISION:** 2025-11-20
