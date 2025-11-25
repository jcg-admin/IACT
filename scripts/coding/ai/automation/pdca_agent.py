"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import pdca_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(pdca_agent, "main"):
        pdca_agent.main()
