---
name: SDLCOrchestratorAgent
description: Coordina todas las fases del SDLC, aplica decisiones Go/No-Go y genera reportes integrales.
---

# SDLC Orchestrator Agent

`SDLCOrchestratorAgent` (`scripts/coding/ai/sdlc/orchestrator.py`) ejecuta el pipeline SDLC completo desde planning hasta deployment. Instancia los agentes especializados de cada fase y decide si avanzar basándose en heurísticas o en un LLM opcional.

## Capacidades

- Valida fases inicial y final (`start_phase`, `end_phase`) y orden correcto.
- Invoca `SDLCPlannerAgent`, `SDLCFeasibilityAgent`, `SDLCDesignAgent`, `SDLCTestingAgent` y `SDLCDeploymentAgent` en secuencia.
- Calcula decisiones Go/No-Go por fase con heurísticas (decisión + confianza) o delegando en `LLMGenerator`.
- Genera reportes completos con artefactos y recomendaciones finales.
- Soporta reanudaciones desde fases intermedias y configuración compartida.

## Entradas y Salidas

- **Entradas**
  - `feature_request`: descripción de la funcionalidad a implementar.
  - `project_context`: contexto adicional.
  - Configuración (`start_phase`, `end_phase`, proveedor/modelo LLM, etc.).
- **Salidas**
  - Reporte SDLC con artefactos por fase, métricas y recomendación final.
  - Indicadores por fase (`decision`, `confidence`, riesgos, tiempos).

## Uso

```python
from scripts.coding.ai.sdlc.orchestrator import SDLCOrchestratorAgent

orchestrator = SDLCOrchestratorAgent({"llm_provider": "anthropic"})
report = orchestrator.execute({
    "feature_request": "Implementar autenticación MFA",
    "project_context": "Plataforma IACT"
})
print(report["final_decision"], report["phases"].keys())
```

## Validaciones Relacionadas

- Ejecutar `orchestrator.validate_input(...)` para asegurar parámetros válidos.
- Integrar con `DORATrackedSDLCAgent` para registrar métricas de flujo continuo.
