"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import schema_validator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(schema_validator_agent, "main"):
        schema_validator_agent.main()
