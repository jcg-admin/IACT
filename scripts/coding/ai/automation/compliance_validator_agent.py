"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import compliance_validator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(compliance_validator_agent, "main"):
        compliance_validator_agent.main()
