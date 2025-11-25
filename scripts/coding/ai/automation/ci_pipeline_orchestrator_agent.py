"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import ci_pipeline_orchestrator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(ci_pipeline_orchestrator_agent, "main"):
        ci_pipeline_orchestrator_agent.main()
