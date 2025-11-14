---
id: DOC-GOBERNANZA-DORA-SDLC-INTEGRATION
tipo: guia_tecnica
categoria: ai
version: 1.0.0
fecha_creacion: 2025-11-06
propietario: arquitecto-senior
fuente: FASES_IMPLEMENTACION_IA.md + dora_sdlc_integration.py
relacionados: ["ESTRATEGIA_IA.md", "FASES_IMPLEMENTACION_IA.md", "AI_CAPABILITIES.md"]
date: 2025-11-13
---

# Guia de Integracion DORA + SDLC Agents

Como se integran las metricas DORA con los agentes SDLC del proyecto IACT.

**Version:** 1.0.0
**Fecha:** 2025-11-06
**Basado en:** FASES_IMPLEMENTACION_IA.md (Fase 1: T1.2, Fase 5: T5.1)

---

## Vision General

Los agentes SDLC del proyecto IACT rastrean automaticamente metricas DORA durante
cada fase del ciclo de desarrollo, permitiendo medicion continua de performance
sin intervencion manual.

**Beneficios:**
- Metricas DORA en tiempo real por cada feature/issue
- Identificacion temprana de cuellos de botella
- Validacion automatica de mejoras IA
- Feedback loop rapido (< 5 min)

---

## Arquitectura de Integracion

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    SDLC Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Planning -> Feasibility -> Design -> Testing -> Deployment │
│      ↓           ↓           ↓          ↓          ↓       │
│  [DORA Tracker] [DORA Tracker] ... ... [DORA Tracker]      │
│      ↓           ↓           ↓          ↓          ↓       │
│  ┌───────────────────────────────────────────────────┐     │
│  │        DORAMetrics (in-memory storage)            │     │
│  │   - Lead Time tracking                            │     │
│  │   - Change Failure Rate                           │     │
│  │   - Deployment Frequency                          │     │
│  │   - MTTR calculation                              │     │
│  └───────────────────────────────────────────────────┘     │
│                         ↓                                   │
│  ┌───────────────────────────────────────────────────┐     │
│  │   .dora_sdlc_metrics.json (persistent storage)    │     │
│  └───────────────────────────────────────────────────┘     │
│                         ↓                                   │
│  ┌───────────────────────────────────────────────────┐     │
│  │   PDCA Automation Agent (Fase 5: T5.5)           │     │
│  │   - Analiza metricas baseline                     │     │
│  │   - Propone mejoras automaticas                   │     │
│  │   - Valida cambios (APPLY/REVERT)                │     │
│  └───────────────────────────────────────────────────┘     │
│                         ↓                                   │
│  ┌───────────────────────────────────────────────────┐     │
│  │   GitHub API Integration (opcional)               │     │
│  │   - Combina metricas locales + GitHub            │     │
│  │   - Genera reportes DORA completos                │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **SDLC Agent inicia** -> `DORAMetrics.start_cycle(feature_id, phase)`
2. **Cada fase completa** -> `DORAMetrics.record_phase(phase, decision, duration)`
3. **Deployment ejecuta** -> Calcula Lead Time, Deployment Frequency
4. **Testing ejecuta** -> Calcula Change Failure Rate
5. **Maintenance ejecuta** -> Calcula MTTR
6. **Pipeline completa** -> `DORAMetrics.complete_cycle(decision)`
7. **PDCA Agent analiza** -> Propone mejoras basadas en metricas
8. **Opcional: GitHub sync** -> `integrate_dora_with_github()` combina datos

---

## Mapeo SDLC Phase -> DORA Metric

| SDLC Phase | DORA Metric | Que Mide | Como |
|------------|-------------|----------|------|
| **Planning** | Lead Time (start) | Inicio del ciclo | Timestamp de inicio |
| **Design** | Lead Time (checkpoint) | Progreso del ciclo | Timestamp intermedio |
| **Testing** | Change Failure Rate | % tests fallidos | `(tests_failed / total) * 100` |
| **Deployment** | Deployment Frequency | Frecuencia deploys | Deploys / dias |
| **Deployment** | Lead Time (end) | Tiempo total | `end_time - start_time` |
| **Maintenance** | MTTR | Tiempo de recuperacion | `resolved_at - created_at` |

---

## Implementacion Tecnica

### Opcion 1: Usar DORATrackedSDLCAgent (Recomendado)

Todos los agentes SDLC que hereden de `DORATrackedSDLCAgent` registran
automaticamente sus metricas.

```python
from agents.dora_sdlc_integration import DORATrackedSDLCAgent, DORAMetrics

class MyPlanningAgent(DORATrackedSDLCAgent):
    """Planning agent con rastreo DORA automatico."""

    def __init__(self, config=None):
        # Crear instancia compartida de metricas
        dora_metrics = DORAMetrics()

        super().__init__(
            name="PlanningAgent",
            phase="planning",
            config=config,
            dora_metrics=dora_metrics  # Compartida entre agentes
        )

    def run(self, input_data):
        # Logica del agente
        feature_request = input_data['feature_request']

        # ... procesar request ...

        return self.create_phase_result(
            decision='go',
            confidence=0.9,
            artifacts=['plan.md'],
            recommendations=['Priorizar seguridad']
        )

# Uso
agent = MyPlanningAgent()
result = agent.execute({'feature_id': 'FEAT-001', 'feature_request': '...'})

# Metricas registradas automaticamente
print(agent.dora_metrics.get_summary())
```

**Que registra automaticamente:**
- Duracion de la fase (en segundos)
- Decision (go, no-go, review, blocked, failed)
- Metadata extraida del resultado
- Timestamp de completacion

### Opcion 2: Usar decorador @dora_tracked

Para funciones individuales fuera del contexto SDLC.

```python
from agents.dora_sdlc_integration import dora_tracked

@dora_tracked
def deploy_to_production(feature_id: str, version: str) -> bool:
    """Deploy con rastreo DORA automatico."""
    # ... logica de deployment ...
    return True

# Uso
deploy_to_production(feature_id='FEAT-001', version='1.2.3')

# Metricas registradas automaticamente
```

### Opcion 3: Manual con DORAMetrics

Para control fino del rastreo.

```python
from agents.dora_sdlc_integration import DORAMetrics
import time

metrics = DORAMetrics()

# Iniciar ciclo
metrics.start_cycle(feature_id='FEAT-001', phase='planning')

# Fase 1: Planning
start = time.time()
# ... ejecutar planning ...
duration = time.time() - start
metrics.record_phase('planning', 'go', duration)

# Fase 2: Design
start = time.time()
# ... ejecutar design ...
duration = time.time() - start
metrics.record_phase('design', 'go', duration)

# Fase 3: Testing
start = time.time()
tests_passed = 95
tests_failed = 5
duration = time.time() - start
metrics.record_phase('testing', 'go', duration, {
    'tests_passed': tests_passed,
    'tests_failed': tests_failed
})

# Fase 4: Deployment
start = time.time()
# ... ejecutar deployment ...
duration = time.time() - start
metrics.record_phase('deployment', 'go', duration)

# Completar ciclo
summary = metrics.complete_cycle('success')

# Ver metricas
print(f"Lead Time: {summary['metrics']['lead_time']}h")
print(f"CFR: {summary['metrics']['change_failure_rate']}%")
```

---

## Integracion con GitHub API

Para combinar metricas SDLC locales con datos de GitHub (commits, PRs, issues).

```python
from agents.dora_sdlc_integration import integrate_dora_with_github

# Combinar metricas locales + GitHub
combined_report = integrate_dora_with_github(
    repo='2-Coatl/IACT---project',
    github_token=os.getenv('GITHUB_TOKEN'),
    days=30
)

print(combined_report['local_sdlc_metrics'])
print(combined_report['github_metrics'])
print(combined_report['overall_classification'])  # Elite, High, Medium, Low
```

**Datos GitHub utilizados:**
- Deployments a production (Deployment Frequency)
- Commits -> Production (Lead Time)
- Issues con label "incident" (MTTR)
- PRs revertidos (Change Failure Rate)

---

## Integracion con PDCA Automation Agent

El agente PDCA (Fase 5: T5.5) consume metricas DORA para mejora continua.

```python
from agents.pdca_automation_agent import PDCAAutomationAgent

# Crear agente PDCA
pdca = PDCAAutomationAgent(
    repo='2-Coatl/IACT---project',
    github_token=os.getenv('GITHUB_TOKEN'),
    baseline_days=30,
    validation_threshold=0.05  # 5% mejora minima
)

# Ejecutar ciclo PDCA completo
result = pdca.run_cycle(auto_execute=False)

# Fases ejecutadas:
# 1. PLAN: Analizar metricas DORA baseline y proponer mejoras
# 2. DO: Ejecutar cambios propuestos (ej: activar AI tools)
# 3. CHECK: Validar metricas post-cambio vs baseline
# 4. ACT: Decidir APPLY, REVERT, CONTINUE o ESCALATE

print(f"Decision: {result['act']['decision']}")
print(f"Score: {result['act']['weighted_score']}%")
```

**Umbrales PDCA:**
- `auto_apply_threshold: 15%` - Aplicar si mejora >= 15%
- `auto_revert_threshold: -5%` - Revertir si empeora >= 5%
- `validation_threshold: 5%` - Umbral minimo de validacion

---

## Ejemplo Completo: Pipeline SDLC con DORA

```python
#!/usr/bin/env python3
"""
Pipeline SDLC completo con rastreo DORA automatico.
"""

from agents.dora_sdlc_integration import DORATrackedSDLCAgent, DORAMetrics
from agents.sdlc_base import SDLCPipeline

# Crear instancia compartida de metricas
dora_metrics = DORAMetrics()

# Agentes SDLC con rastreo DORA
class PlanningAgent(DORATrackedSDLCAgent):
    def run(self, input_data):
        # ... logica planning ...
        return self.create_phase_result('go', 0.9)

class DesignAgent(DORATrackedSDLCAgent):
    def run(self, input_data):
        # ... logica design ...
        return self.create_phase_result('go', 0.85)

class TestingAgent(DORATrackedSDLCAgent):
    def run(self, input_data):
        # ... ejecutar tests ...
        return self.create_phase_result('go', 0.95, metadata={
            'tests_passed': 95,
            'tests_failed': 5
        })

class DeploymentAgent(DORATrackedSDLCAgent):
    def run(self, input_data):
        # ... deployment ...
        return self.create_phase_result('go', 1.0)

# Crear pipeline
agents = [
    PlanningAgent(config={}, dora_metrics=dora_metrics),
    DesignAgent(config={}, dora_metrics=dora_metrics),
    TestingAgent(config={}, dora_metrics=dora_metrics),
    DeploymentAgent(config={}, dora_metrics=dora_metrics)
]

pipeline = SDLCPipeline(name="DORA_Tracked_SDLC", agents=agents)

# Ejecutar pipeline
input_data = {
    'feature_id': 'FEAT-001',
    'feature_request': 'Implementar autenticacion 2FA'
}

result = pipeline.execute(input_data)

# Completar ciclo DORA
summary = dora_metrics.complete_cycle('success')

# Imprimir metricas
print(f"\n=== DORA METRICS ===")
print(f"Lead Time: {summary['metrics']['lead_time']}h")
print(f"CFR: {summary['metrics']['change_failure_rate']}%")
print(f"Deployment Frequency: {summary['metrics']['deployment_frequency']} deploys/day")
```

---

## Almacenamiento de Metricas

### Archivo: .dora_sdlc_metrics.json

```json
{
  "cycles": [
    {
      "feature_id": "FEAT-001",
      "cycle_id": "cycle-20251106-143022",
      "start_time": "2025-11-06T14:30:22.123456",
      "end_time": "2025-11-06T16:45:33.654321",
      "start_phase": "planning",
      "phases": [
        {
          "phase": "planning",
          "decision": "go",
          "timestamp": "2025-11-06T14:35:22.123456",
          "duration_seconds": 300.0,
          "metadata": {}
        },
        {
          "phase": "testing",
          "decision": "go",
          "timestamp": "2025-11-06T16:30:22.123456",
          "duration_seconds": 7200.0,
          "metadata": {
            "tests_passed": 95,
            "tests_failed": 5
          }
        },
        {
          "phase": "deployment",
          "decision": "go",
          "timestamp": "2025-11-06T16:45:22.123456",
          "duration_seconds": 900.0,
          "metadata": {}
        }
      ],
      "metrics": {
        "deployment_frequency": 0.5,
        "lead_time": 2.25,
        "change_failure_rate": 5.0,
        "mttr": null
      },
      "status": "completed",
      "final_decision": "success",
      "total_duration_seconds": 8111.0
    }
  ],
  "last_updated": "2025-11-06T16:45:33.654321"
}
```

---

## APIs Disponibles

### DORAMetrics

```python
# Iniciar ciclo
start_cycle(feature_id: str, phase: str) -> None

# Registrar fase
record_phase(
    phase: str,
    decision: str,
    duration_seconds: float,
    metadata: Optional[Dict] = None
) -> None

# Completar ciclo
complete_cycle(final_decision: str) -> Dict[str, Any]

# Obtener resumen
get_summary(last_n_cycles: int = 30) -> Dict[str, Any]
```

### DORATrackedSDLCAgent

```python
# Ejecutar con rastreo automatico
execute(input_data: Dict[str, Any]) -> Any

# Acceder a metricas
agent.dora_metrics.get_summary()
```

### integrate_dora_with_github()

```python
# Combinar metricas locales + GitHub
integrate_dora_with_github(
    repo: str,
    github_token: str,
    days: int = 30
) -> Dict[str, Any]
```

---

## Visualizacion de Metricas

### CLI

```bash
# Ver metricas SDLC locales
python scripts/ai/agents/dora_sdlc_integration.py

# Ver metricas GitHub (ultimos 30 dias)
python scripts/dora_metrics.py --repo 2-Coatl/IACT---project --days 30

# Ejecutar ciclo PDCA con validacion
python scripts/ai/agents/pdca_automation_agent.py --repo 2-Coatl/IACT---project
```

### Programatico

```python
from agents.dora_sdlc_integration import DORAMetrics, print_dora_summary

metrics = DORAMetrics()
summary = metrics.get_summary(last_n_cycles=30)
print_dora_summary(summary)
```

**Output:**
```
================================================================================
DORA METRICS SUMMARY (SDLC Integration)
================================================================================

Periodo: 30 ciclos (~30 dias)

Metricas:
  Deployment Frequency: 0.50 deployments/day
  Lead Time: 2.25 hours
    (basado en 30 muestras)
  Change Failure Rate: 5.00%
    (basado en 30 muestras)
  MTTR: 0.00 hours
    (basado en 0 muestras)

================================================================================
```

---

## Mejores Practicas

### 1. Compartir instancia DORAMetrics entre agentes

```python
# BIEN - instancia compartida
dora_metrics = DORAMetrics()
agent1 = PlanningAgent(dora_metrics=dora_metrics)
agent2 = DesignAgent(dora_metrics=dora_metrics)

# MAL - instancias separadas
agent1 = PlanningAgent(dora_metrics=DORAMetrics())
agent2 = DesignAgent(dora_metrics=DORAMetrics())
```

### 2. Incluir feature_id en input_data

```python
# BIEN
input_data = {
    'feature_id': 'FEAT-001',  # Identificador claro
    'feature_request': '...'
}

# MAL
input_data = {
    'feature_request': '...'  # Sin identificador
}
```

### 3. Completar ciclo al final del pipeline

```python
# Ejecutar pipeline completo
result = pipeline.execute(input_data)

# IMPORTANTE: Completar ciclo DORA
summary = dora_metrics.complete_cycle('success')
```

### 4. Metadata rica en testing phase

```python
# BIEN - incluir tests_passed y tests_failed
metadata = {
    'tests_passed': 95,
    'tests_failed': 5,
    'coverage': 92.5,
    'test_duration': 120.0
}

# MAL - metadata vacia
metadata = {}
```

### 5. Sincronizar con GitHub periodicamente

```bash
# Cron job diario: 2am
0 2 * * * python scripts/dora_sync.py --repo 2-Coatl/IACT---project
```

---

## Troubleshooting

### Error: "No hay ciclo activo"

**Causa:** No se llamo `start_cycle()` antes de `record_phase()`

**Solucion:**
```python
# Iniciar ciclo antes de registrar fases
metrics.start_cycle('FEAT-001', 'planning')
metrics.record_phase('planning', 'go', 300.0)
```

### Metricas en cero o None

**Causa:** Fases no registradas correctamente

**Solucion:** Verificar que cada fase llama `record_phase()`:
```python
# Planning -> Lead Time start
# Testing -> CFR (requiere tests_passed/failed en metadata)
# Deployment -> Lead Time end + Deployment Frequency
# Maintenance -> MTTR (requiere incident_duration_hours en metadata)
```

### GitHub API falla

**Causa:** GITHUB_TOKEN no configurado o sin permisos

**Solucion:**
```bash
# Exportar token
export GITHUB_TOKEN="ghp_xxxxx"

# Verificar permisos: repo, read:org
gh auth status
```

---

## Roadmap de Mejoras

**Q1 2026:**
- [ ] Dashboard Grafana con metricas DORA en tiempo real
- [ ] Alertas automaticas cuando metricas empeoran >10%
- [ ] Integracion con sistema de metrics interno MySQL
- [ ] API REST para consultar metricas

**Q2 2026:**
- [ ] Machine learning para predecir Lead Time
- [ ] Anomaly detection en CFR
- [ ] Auto-scaling basado en Deployment Frequency
- [ ] Reportes semanales automaticos por email

---

## Referencias

- **Codigo:**
  - `scripts/ai/agents/dora_sdlc_integration.py`
  - `scripts/ai/agents/pdca_automation_agent.py`
  - `scripts/dora_metrics.py`

- **Documentacion:**
  - `FASES_IMPLEMENTACION_IA.md` (Fase 1: T1.2, Fase 5: T5.1, T5.5)
  - `ESTRATEGIA_IA.md` (Practica 3: AI-accessible Internal Data)
  - `AI_CAPABILITIES.md` (Checklist DORA metrics)

- **DORA Research:**
  - [DORA Report 2025](https://dora.dev/)
  - [DORA Core Metrics](https://dora.dev/guides/dora-metrics-four-keys/)

---

**VERSION:** 1.0.0
**ULTIMA ACTUALIZACION:** 2025-11-06
**PROXIMA REVISION:** 2025-11-20
**ESTADO:** DOCUMENTACION COMPLETA, IMPLEMENTACION FUNCIONAL
