---
name: SelfConsistencyAgent
description: Implementa Self-Consistency para muestrear múltiples cadenas de razonamiento y votar por la respuesta más confiable.
---

# Self-Consistency Technique Agent

`SelfConsistencyAgent` (`scripts/coding/ai/agents/base/self_consistency.py`) ejecuta el enfoque de Wang et al. (2022) para mejorar la precisión en tareas de razonamiento. Genera múltiples cadenas de pensamiento, extrae respuestas y aplica votación mayoritaria con métricas de confianza.

## Capacidades

- Genera `num_samples` cadenas de pensamiento usando `LLMGenerator` o un `generator_fn` externo.
- Extrae la respuesta final de cada cadena mediante regex o función personalizada.
- Calcula distribución de votos, confianza, fuerza de consenso y listado completo de reasoning paths.
- Permite fijar temperatura, función de extracción y umbral mínimo de confianza para aceptar resultados.
- Expone logs detallados por cadena para auditoría y tuning de prompts.

## Entradas y Salidas

- **Entradas**
  - `prompt`: problema a resolver con instrucciones de Chain-of-Thought.
  - `generator_fn`: función opcional para generar respuestas si no se usa LLM integrado.
  - Configuración (`num_samples`, `temperature`, `min_confidence`, proveedor/modelo).
- **Salidas**
  - `SelfConsistencyResult` con respuesta ganadora, votos por opción, lista de reasoning paths y métricas de consenso.

## Uso

```python
from scripts.coding.ai.agents.base.self_consistency import SelfConsistencyAgent

agent = SelfConsistencyAgent(num_samples=8, temperature=0.6)
result = agent.solve_with_consistency(
    prompt="Resuelve 124 * 37 usando razonamiento paso a paso"
)
print(result.final_answer, result.vote_distribution)
```

## Validaciones Relacionadas

- Generar pruebas automatizadas con `scripts/coding/ai/tests/techniques/test_self_consistency.py`.
- Integrar con `scripts/coding/ai/sdlc/testing_agent.py` para garantizar cobertura de escenarios de baja confianza y reintentos.
