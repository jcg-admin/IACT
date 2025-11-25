"""Stub de compatibilidad.

El script real se movió a scripts/gobernanza_sdlc/automation/.
"""
from scripts.gobernanza_sdlc.automation import business_rules_validator_agent  # type: ignore

if __name__ == "__main__":
    if hasattr(business_rules_validator_agent, "main"):
        business_rules_validator_agent.main()
