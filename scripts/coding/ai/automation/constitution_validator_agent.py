"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import constitution_validator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(constitution_validator_agent, "main"):
        constitution_validator_agent.main()
