---
name: ChainOfVerificationAgent
description: Implementa Chain-of-Verification para validar respuestas de LLM mediante preguntas de verificación independientes.
---

# Chain-of-Verification Technique Agent

El `ChainOfVerificationAgent` (archivo `scripts/coding/ai/agents/base/chain_of_verification.py`) aplica la estrategia propuesta por Meta AI para reducir alucinaciones en LLM. Descompone una respuesta inicial en claims verificables, formula preguntas independientes y reconstruye una respuesta corregida con nivel de confianza.

## Capacidades

- Genera preguntas de verificación a partir de la respuesta base y el contexto entregado.
- Ejecuta verificaciones independientes con `LLMGenerator` o generadores personalizados.
- Clasifica cada verificación (`verified`, `failed`, `corrected`, `uncertain`) y contabiliza correcciones.
- Sintetiza una respuesta final corregida y calcula la confianza global según los resultados de verificación.
- Permite ajustar el umbral mínimo aceptable (`verify_threshold`) y el proveedor/modelo LLM.

## Entradas y Salidas

- **Entradas**
  - `question`: pregunta original a validar.
  - `initial_response`: respuesta que generó el LLM antes de la verificación.
  - `context`: diccionario opcional con señales adicionales (ej. snippets de código, facts).
- **Salidas**
  - `VerifiedResponse` con la respuesta final, lista de verificaciones, confianza y número de correcciones.

## Uso

```python
from scripts.coding.ai.agents.base.chain_of_verification import ChainOfVerificationAgent

agent = ChainOfVerificationAgent(verify_threshold=0.75, llm_provider="anthropic")
result = agent.verify_response(
    question="¿Cuál es el tiempo máximo de respuesta en SLA?",
    initial_response="El SLA es de 250 ms para cualquier servicio.",
    context={"service": "api"}
)
print(result.final_response, result.confidence_score)
```

## Validaciones Relacionadas

- Integrar con `scripts/coding/ai/sdlc/testing_agent.py` usando la técnica `chain-of-verification` para generar suites de regresión.
- Registrar métricas en dashboards DORA mediante `scripts/coding/ai/sdlc/dora_integration.py` para medir reducción de fallas por documentación incorrecta.
