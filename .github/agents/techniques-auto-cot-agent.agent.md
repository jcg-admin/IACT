---
name: AutoCoTAgent
description: Implementa Auto-CoT para generar demostraciones de chain-of-thought a partir de lotes de preguntas clusterizadas.
---

# Auto-CoT Technique Agent

`AutoCoTAgent` automatiza la técnica **Automatic Chain-of-Thought** descrita por Zhang et al. (2022) para generar demostraciones de razonamiento paso a paso sin curación manual. El agente vive en `scripts/coding/ai/agents/base/auto_cot_agent.py` y puede ejecutarse tanto con modelos LLM reales como en modo template.

## Capacidades

- Agrupa preguntas similares mediante clustering (usa `sklearn.KMeans` cuando está disponible o un fallback determinista). 
- Selecciona preguntas representativas para cubrir la diversidad del dominio y limitar la cantidad de demostraciones.
- Genera demostraciones Zero-Shot por cluster con `LLMGenerator` o funciones personalizadas.
- Valida la calidad de cada demostración y descarta las que no cumplan los criterios mínimos.
- Exporta cada demostración con pregunta original, razonamiento y respuesta final.

## Entradas y Salidas

- **Entradas**
  - `questions`: lista de preguntas en texto libre.
  - `domain`: etiqueta opcional para ajustar prompts.
  - Parámetros opcionales (`k_clusters`, `max_demonstrations`, proveedor/modelo LLM, modo offline).
- **Salidas**
  - Lista de `Demonstration` con razonamiento paso a paso y puntaje de calidad.
  - Métricas de clustering y conteo de demostraciones aceptadas.

## Uso

```bash
python scripts/coding/ai/agents/base/auto_cot_agent.py \
  --input questions.json \
  --k-clusters 6 \
  --max-demonstrations 12 \
  --llm-provider anthropic
```

> El script acepta JSON con `questions` o lee desde STDIN. En entornos sin NumPy/Sklearn se utiliza el modo determinista.

## Validaciones Relacionadas

- Se recomienda generar suites de tests automáticos con `scripts/coding/ai/sdlc/testing_agent.py` empleando la técnica `auto-cot` para cubrir el flujo de generación y guardado de demostraciones.
- Revisar cobertura mediante `scripts/coding/ai/tests/techniques/test_auto_cot_agent.py` cuando esté disponible.
