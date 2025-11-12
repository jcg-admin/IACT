#!/usr/bin/env python3
"""CASO 1: Evaluacion de Viabilidad Rapida"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent
from scripts.ai.shared.env_loader import get_llm_config_from_env

print("CASO 1: Evaluar si 'Dark Mode' es viable\n")

# Cargar config desde .env (usa Claude si está disponible)
config = get_llm_config_from_env()

if config:
    print(f"Usando: {config['llm_provider']} - {config['model']}\n")
else:
    print("Usando: Heuristicas (sin LLM)\n")

agent = SDLCFeasibilityAgent(config=config)

result = agent.run({
    "issue": {
        "title": "Add dark mode toggle",
        "description": "Users can switch between light and dark themes",
        "requirements": ["Toggle in settings", "localStorage", "CSS variables"],
        "estimated_story_points": 2
    }
})

phase_result = result["phase_result"]
print(f"Decision: {phase_result.decision.upper()}")
print(f"Confidence: {phase_result.confidence:.0%}")
print(f"Risks: {len(phase_result.risks)}")
effort = result.get('effort_analysis', {})
print(f"Estimated days: {effort.get('estimated_days', 'N/A')}")
print(f"\nMarkdown report: {result['report_path']}")
