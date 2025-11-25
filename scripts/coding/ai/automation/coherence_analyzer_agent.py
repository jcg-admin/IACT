"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import coherence_analyzer_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(coherence_analyzer_agent, "main"):
        coherence_analyzer_agent.main()
