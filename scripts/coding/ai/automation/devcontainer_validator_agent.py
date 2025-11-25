"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import devcontainer_validator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(devcontainer_validator_agent, "main"):
        devcontainer_validator_agent.main()
