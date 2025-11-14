---
id: DOC-AI-DORA-CASSANDRA-INTEGRATION
tipo: arquitectura
categoria: integracion
version: 1.0.0
fecha_creacion: 2025-11-06
propietario: arquitecto-senior
relacionados: ["ADR_2025_003", "ADR_2025_004", "OBSERVABILITY_LAYERS.md", "DORA_SDLC_INTEGRATION_GUIDE.md"]
date: 2025-11-13
---

# Integracion DORA Metrics + Cassandra Logs + SDLC Agents

Documento tecnico que explica como se integran las 3 capas de observabilidad en el proyecto IACT.

**Version:** 1.0.0
**Fecha:** 2025-11-06

---

## Por que DORA NO es un Agente

### Pregunta Fundamental

**"Porque DORA no es un agente como SDLCAgent?"**

### Respuesta Corta

**DORA es un SISTEMA DE METRICAS, NO un AGENTE DE EJECUCION.**

- **SDLCAgent** = EJECUTA tareas (planning, testing, deployment)
- **DORA** = MIDE el rendimiento del proceso (Lead Time, CFR, MTTR)
- **Cassandra** = ALMACENA logs de runtime (errores, requests, etc.)

### Analogia

Piensa en un equipo de futbol:

| Componente | Rol en Futbol | Rol en IACT |
|------------|---------------|-------------|
| **SDLCAgent** | Jugadores (ejecutan jugadas) | Agentes que hacen planning, testing, deployment |
| **DORA** | Estadisticas (goles, pases, distancia) | Metricas del proceso (Lead Time, CFR, MTTR) |
| **Cassandra** | Video replay (errores, jugadas criticas) | Logs de runtime (errores, requests, queries) |

**Los jugadores NO son las estadisticas.** Las estadisticas MIDEN el rendimiento de los jugadores.

Del mismo modo: **SDLCAgent NO es DORA.** DORA MIDE el rendimiento de SDLCAgent.

---

## Arquitectura de 3 Capas

```
[1] DORA Metrics (Proceso)        [2] Application Logs (Runtime)      [3] Infrastructure Logs (Sistema)
     |                                  |                                     |
     v                                  v                                     v
.dora_sdlc_metrics.json           Cassandra: application_logs          Cassandra: infrastructure_logs
MySQL (futuro)                    (errores, requests, queries)         (nginx, postgresql, mysql)
     |                                  |                                     |
     v                                  v                                     v
Mide EQUIPO/PIPELINE               Mide APLICACION runtime              Mide INFRAESTRUCTURA
(Lead Time, CFR, MTTR)             (business logic errors)              (server errors, crashes)
```

### Capa 1: DORA Metrics (Proceso de Desarrollo)

**Que mide:** Performance del EQUIPO y PIPELINE, NO del sistema en produccion.

**Preguntas:**
- Que tan rapido desplegamos features? (Deployment Frequency)
- Cuanto tarda un feature desde commit hasta produccion? (Lead Time)
- Cuantos deploys fallan? (Change Failure Rate)
- Cuanto tardamos en recuperar de incidentes? (MTTR)

**Fuente de datos:**
- Git commits, PRs, merges
- CI/CD pipeline events (GitHub Actions)
- **SDLCAgent execution** (planning, testing, deployment)
- Issues con label "incident"

**Storage:**
- Local: `.dora_sdlc_metrics.json`
- Futuro: MySQL `dora_metrics` table

**Quien usa:**
- Tech Lead: Analizar performance del equipo
- Arquitecto: Validar mejoras IA con PDCA
- DevOps: Optimizar CI/CD pipeline

### Capa 2: Application Logs (Business Logic Runtime)

**Que mide:** Comportamiento de la APLICACION Django en runtime (produccion, staging, dev).

**Preguntas:**
- Que requests HTTP recibe la aplicacion?
- Que errores ocurren en business logic?
- Que queries SQL son lentas?
- Como se comportan los usuarios?

**Fuente de datos:**
- Django logging: `logger.info()`, `logger.error()`
- Middleware logs (request processing time)
- ORM query logs (slow queries)
- Celery task logs

**Storage:**
- Cassandra: `logging.application_logs` table
- Backup: Filesystem `logs/django.log`

**Quien usa:**
- Developers: Debug aplicacion durante desarrollo
- QA: Validar comportamiento esperado
- SRE: Troubleshoot errores produccion
- Support: Investigar reportes usuarios

### Capa 3: Infrastructure Logs (Sistema Operativo)

**Que mide:** Comportamiento del SISTEMA OPERATIVO y SERVICIOS (nginx, postgresql, mysql).

**Preguntas:**
- Hay errores a nivel de SO?
- Nginx rechaza conexiones?
- PostgreSQL tiene queries lentas?
- Hay problemas de memoria/CPU?

**Fuente de datos:**
- `/var/log/syslog`, `/var/log/nginx/*`, `/var/log/postgresql/*`
- Python daemon: `tail -f` → Cassandra

**Storage:**
- Cassandra: `logging.infrastructure_logs` table
- Backup: Filesystem `/var/log/*`

**Quien usa:**
- DevOps: Troubleshoot infraestructura
- SysAdmin: Maintenance sistema operativo
- SRE: Investigar outages

---

## Como se Relacionan DORA y SDLCAgent

### SDLCAgent = EJECUTOR

```python
# scripts/ai/agents/sdlc_agent.py
class SDLCAgent:
    """Agente que EJECUTA tareas del SDLC."""

    def execute(self, task):
        # HACE el trabajo
        result = self.run(task)
        return result
```

**Responsabilidades:**
- Analizar requirements (planning)
- Validar calidad (testing)
- Ejecutar despliegues (deployment)
- Resolver incidentes (maintenance)
- Tomar decisiones: GO, NO-GO, ESCALATE

**NO hace:** Medir metricas, calcular Lead Time, almacenar logs

### DORA = MEDIDOR

```python
# scripts/ai/agents/dora_metrics.py
class DORAMetrics:
    """Sistema que MIDE el rendimiento del proceso."""

    def record_phase(self, phase, decision, duration):
        # REGISTRA lo que SDLCAgent hizo
        self.phases.append({
            'phase': phase,
            'decision': decision,
            'duration': duration
        })

    def calculate_lead_time(self):
        # CALCULA metricas basado en lo registrado
        return sum(phase['duration'] for phase in self.phases)
```

**Responsabilidades:**
- Registrar eventos del SDLC (planning, testing, deployment)
- Calcular metricas DORA (Lead Time, CFR, MTTR, DF)
- Almacenar historico de metricas
- Proveer datos para PDCA automation

**NO hace:** Ejecutar tareas, tomar decisiones, desplegar codigo

### Integracion: DORATrackedSDLCAgent

**Como se integran sin mixing concerns?**

Usamos **decorador pattern** para agregar tracking DORA a SDLCAgent sin modificar su logica:

```python
# scripts/ai/agents/dora_sdlc_integration.py
class DORATrackedSDLCAgent(SDLCAgent):
    """SDLCAgent con tracking DORA automatico."""

    def __init__(self, dora_metrics: DORAMetrics):
        super().__init__()
        self.dora_metrics = dora_metrics

    def execute(self, task):
        # Iniciar tracking
        start_time = time.time()

        # EJECUTAR (logica SDLCAgent)
        result = super().execute(task)

        # Registrar en DORA (NO afecta ejecucion)
        duration = time.time() - start_time
        self.dora_metrics.record_phase(
            phase=self.phase,
            decision=result.decision,
            duration=duration
        )

        return result
```

**Ventajas:**
- Separation of concerns: SDLCAgent ejecuta, DORA mide
- Non-invasive: SDLCAgent NO necesita conocer DORA
- Automatic tracking: Metricas registradas sin codigo extra
- Optional: Puedes usar SDLCAgent sin DORA si quieres

---

## Como se Relacionan DORA y Cassandra

### DORA vs Cassandra - Diferentes Propositos

| Aspecto | DORA Metrics | Cassandra Logs |
|---------|--------------|----------------|
| **Que mide** | Proceso desarrollo (EQUIPO) | Runtime aplicacion (SISTEMA) |
| **Scope** | Ciclo de vida feature (planning → deployment) | Request-by-request logs |
| **Granularidad** | Fase-a-fase (minutes → hours) | Log-by-log (milliseconds) |
| **Storage** | MySQL `dora_metrics` (pocos registros) | Cassandra `application_logs` (millones) |
| **Retention** | 90 dias | 90 dias (TTL automatico) |
| **Uso** | Mejora continua (PDCA) | Debug, troubleshooting |

### Ejemplo: Deploy Fallido

Cuando un deploy falla, AMBAS capas capturan informacion DIFERENTE:

#### DORA Metrics (Capa 1) - Impacto en Proceso

```json
{
  "cycle_id": "cycle-20251106-150000",
  "feature_id": "FEAT-001",
  "phase": "deployment",
  "decision": "failed",
  "duration_seconds": 45.0,
  "metrics": {
    "change_failure_rate": 15.0,
    "mttr": 0.25
  }
}
```

**Pregunta respondida:** "Nuestro CFR subio de 5% a 15%, que paso?"

#### Cassandra Logs (Capa 2) - Error Especifico

```cql
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-06'
AND level = 'ERROR'
AND timestamp >= '2025-11-06 15:05:23'
LIMIT 10;
```

**Resultado:**
```
[2025-11-06 15:05:23] ERROR [deployment] Migration 0042 failed
[2025-11-06 15:05:23] ERROR [django.db] IntegrityError: Column 'user_id' cannot be null
[2025-11-06 15:05:23] INFO [deployment] Rollback initiated
```

**Pregunta respondida:** "Cual migration fallo? Que error especifico ocurrio?"

### Integracion: Request ID Tracing

Para correlacionar DORA metrics con Cassandra logs:

```python
# 1. SDLCAgent genera request_id
request_id = f"req-{uuid.uuid4()}"

# 2. SDLCAgent ejecuta + tracking DORA
result = tracked_agent.execute(task, extra={'request_id': request_id})

# 3. DORA registra request_id en metadata
dora_metrics.record_phase('deployment', 'failed', 45.0, {
    'request_id': request_id
})

# 4. Django logs tambien incluyen request_id
logger.error("Migration failed", extra={'request_id': request_id})

# 5. Buscar en Cassandra logs por request_id
SELECT * FROM logging.application_logs WHERE request_id = 'req-...';
```

**Workflow de investigacion:**
1. DORA alerta: CFR subio a 15%
2. Buscar en `.dora_sdlc_metrics.json`: `request_id = 'req-abc123'`
3. Buscar en Cassandra: `WHERE request_id = 'req-abc123'`
4. Encontrar: Migration 0042 failed - IntegrityError user_id
5. Fix: Agregar default value en migration
6. Validation: Re-deploy, verificar DORA metrics mejoran

---

## Workflow Completo: Feature Deployment

### Paso 1: Planning Agent (SDLCAgent)

```python
# EJECUCION
planning_agent = DORATrackedSDLCAgent(phase='planning', dora_metrics=dora)
result = planning_agent.execute({'feature_id': 'FEAT-001'})
# Decision: GO

# DORA TRACKING (automatico)
# - dora_metrics.record_phase('planning', 'go', 300.0)

# CASSANDRA LOGGING (si hay errores)
# - logger.info("Planning completed", extra={'request_id': 'req-123'})
# - Cassandra: INSERT INTO application_logs (...)
```

### Paso 2: Testing Agent (SDLCAgent)

```python
# EJECUCION
testing_agent = DORATrackedSDLCAgent(phase='testing', dora_metrics=dora)
result = testing_agent.execute({'feature_id': 'FEAT-001'})
# Decision: GO (95/100 tests passed)

# DORA TRACKING (automatico)
# - dora_metrics.record_phase('testing', 'go', 7200.0, {'tests_passed': 95})

# CASSANDRA LOGGING
# - logger.info("Tests passed: 95/100")
# - logger.error("Test failed: test_payment_validation", extra={'test_name': 'test_payment_validation'})
# - Cassandra: INSERT INTO application_logs (level='ERROR', logger='pytest', ...)
```

### Paso 3: Deployment Agent (SDLCAgent)

```python
# EJECUCION
deployment_agent = DORATrackedSDLCAgent(phase='deployment', dora_metrics=dora)
result = deployment_agent.execute({'feature_id': 'FEAT-001'})
# Decision: SUCCESS

# DORA TRACKING (automatico)
# - dora_metrics.record_phase('deployment', 'success', 45.0)
# - dora_metrics.complete_cycle('success')
# - Calcula: Lead Time, Deployment Frequency

# CASSANDRA LOGGING
# - logger.info("Deployment started")
# - logger.info("Migration 0042 applied")
# - logger.info("Deployment completed")
# - Cassandra: INSERT INTO application_logs (level='INFO', logger='deployment', ...)
```

### Paso 4: PDCA Automation (analiza DORA metrics)

```python
# ANALISIS DORA (semanal)
pdca_agent = PDCAAutomationAgent(repo='iact')
pdca_agent.analyze_baseline()  # Lee .dora_sdlc_metrics.json

# Propuesta: "Deploy frequency bajo (0.5/dia), incrementar a 1.0/dia"
# Decision: APPLY (mejora >15%)

# VALIDACION (48h despues)
pdca_agent.validate_change()
# Metricas mejoraron: DF 0.5 → 0.8, Lead Time 1.5d → 1.2d
# Decision: APPLY permanente
```

### Paso 5: Error Alerting (analiza Cassandra logs)

```bash
# CRON (cada 5 minutos)
*/5 * * * * python scripts/logging/alert_on_errors.py

# Query Cassandra
SELECT COUNT(*) FROM logging.application_logs
WHERE log_date = '2025-11-06'
AND level = 'ERROR'
AND timestamp >= NOW() - INTERVAL 5 MINUTES;
# Result: 15 errors (threshold: 10)

# Enviar alerta
# - Slack: "High error rate: 15 errors/5min"
# - Email: alerts@iact.com
# - Log: /var/log/iact/log_alerts.log
```

---

## Separacion de Concerns

### Por que NO mezclar DORA y Cassandra?

**Problema si mezclamos:**
```python
# MAL - Mixing concerns
class SDLCAgent:
    def execute(self, task):
        # HACE trabajo
        result = self.run(task)

        # MIDE metricas DORA
        dora_metrics.record_phase(...)

        # ESCRIBE logs Cassandra
        logger.info("Task completed")

        # ENVIA alertas
        if error:
            send_slack_alert(...)

        return result
```

**Problemas:**
- Responsabilidad unica violada (SRP)
- SDLCAgent conoce DORA, Cassandra, Slack (tight coupling)
- Testing complejo (requiere mock de 3 sistemas)
- No se puede usar SDLCAgent sin DORA/Cassandra

**Solucion: Separation of Concerns**
```python
# BIEN - Separation of concerns

# 1. SDLCAgent: Solo ejecuta
class SDLCAgent:
    def execute(self, task):
        return self.run(task)  # Solo logica de negocio

# 2. DORATrackedSDLCAgent: Wrapper con tracking
class DORATrackedSDLCAgent(SDLCAgent):
    def execute(self, task):
        result = super().execute(task)
        self.dora_metrics.record_phase(...)  # Non-invasive
        return result

# 3. CassandraLogHandler: Logging separado
logger.info("Task completed")  # Handler automatico

# 4. AlertManager: Alerting separado (cron)
# Corre independientemente, no bloquea SDLCAgent
```

**Ventajas:**
- Responsabilidad unica (SRP)
- SDLCAgent reutilizable (con o sin DORA)
- Testing simple (mock minimo)
- Performance (logging async, alerting cron)

---

## Resumen

### 3 Capas, 3 Propositos

| Capa | Tipo | Proposito | Quien |
|------|------|-----------|-------|
| **DORA Metrics** | Metrics System | Medir PROCESO desarrollo (equipo) | Tech Lead, Arquitecto |
| **SDLCAgent** | Execution Agent | EJECUTAR tareas (planning → deployment) | Automatizacion IA |
| **Cassandra Logs** | Log Storage | Almacenar LOGS runtime (errores, requests) | Developers, SRE |

### Flujo de Datos

```
[User Story]
     |
     v
[SDLCAgent] -----> EJECUTA tareas
     |                    |
     |                    v
     |              [DORA Metrics] -----> Registra metricas proceso
     |                    |
     |                    v
     |              [PDCA Agent] -----> Analiza y mejora proceso
     |
     v
[Django App] -----> Logging
     |
     v
[CassandraLogHandler] -----> Cassandra application_logs
     |
     v
[AlertManager] -----> Detecta errores criticos -----> Slack/Email
```

### Por que DORA NO es un Agente

**Respuesta final:**

DORA NO es un agente porque NO EJECUTA tareas, solo MIDE el rendimiento del proceso.

- **SDLCAgent** = Jugador (ejecuta jugadas)
- **DORA** = Estadisticas (mide performance)
- **Cassandra** = Video replay (registra errores)

**Analogia:** Un termometro NO es un calentador. El termometro MIDE temperatura, el calentador GENERA temperatura. Del mismo modo, DORA MIDE metricas, SDLCAgent EJECUTA tareas.

---

## Referencias

- ADR_2025_003: DORA + SDLC Integration
- ADR_2025_004: Centralized Log Storage en Cassandra
- OBSERVABILITY_LAYERS.md: 3 capas independientes
- DORA_SDLC_INTEGRATION_GUIDE.md: Guia tecnica integracion
- WORKFLOW_AGENTES_DORA.md: Workflow operacional completo

---

**VERSION:** 1.0.0
**ULTIMA ACTUALIZACION:** 2025-11-06
**PROXIMA REVISION:** 2025-11-20
**ESTADO:** DOCUMENTACION COMPLETA
