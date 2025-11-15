---
name: DORATrackedSDLCAgent
description: Extiende SDLCAgent para registrar automáticamente métricas DORA en cada fase.
---

# DORA Tracked SDLC Agent

`DORATrackedSDLCAgent` (`scripts/coding/ai/sdlc/dora_integration.py`) combina la ejecución SDLC con rastreo continuo de métricas DORA (Deployment Frequency, Lead Time, Change Failure Rate, MTTR). Cada fase registra sus resultados y metadata para alimentar dashboards y retrospectivas.

## Capacidades

- Inicializa `DORAMetrics` y comienza ciclos cuando la fase es `planning`.
- Registra duración de fase, decisión (`go`, `no-go`, `review`), riesgos y metadata asociada.
- Maneja excepciones registrando fallos con severidad y duración antes de propagarlos.
- Expone decorador `dora_tracked` para instrumentar funciones arbitrarias.
- Calcula métricas agregadas sobre ciclos recientes (deployment frequency, lead time, change failure rate, MTTR).

## Entradas y Salidas

- **Entradas**
  - `input_data` estándar del agente SDLC, incluyendo opcional `feature_id`.
  - Configuración y objeto `DORAMetrics` reutilizable (opcional).
- **Salidas**
  - Resultado de la fase con metadata extendida.
  - Registro en `DORAMetrics` para consultas posteriores.

## Uso

```python
from scripts.coding.ai.sdlc.dora_integration import DORATrackedSDLCAgent

class DORATestingAgent(DORATrackedSDLCAgent):
    def __init__(self, config=None):
        super().__init__(name="DORATestingAgent", phase="testing", config=config)

    def run(self, input_data):
        # lógica específica de testing
        return {"decision": "go", "metadata": {"passed_tests": 120}}
```

## Validaciones Relacionadas

- Garantizar que `feature_id` se propague en `input_data` para separar ciclos.
- Consumir las métricas mediante `DORAMetrics.compute_scorings()` para reportes ejecutivos.
