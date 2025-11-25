"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import metrics_collector_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(metrics_collector_agent, "main"):
        metrics_collector_agent.main()
