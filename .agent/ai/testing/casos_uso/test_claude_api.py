#!/usr/bin/env python3
"""Test rápido de API de Claude"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.shared.env_loader import get_llm_config_from_env
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

print("=" * 70)
print("TEST: Claude API con .env")
print("=" * 70)

# Cargar config desde .env
config = get_llm_config_from_env()

if not config:
    print("\nERROR: No se pudo cargar config desde .env")
    print("Verifica que ANTHROPIC_API_KEY esté en .env")
    sys.exit(1)

print(f"\nProvider: {config['llm_provider']}")
print(f"Model: {config['model']}")
print(f"Use LLM: {config['use_llm']}")

# Crear agente con Claude
print("\nCreando agente con Claude...")
agent = SDLCFeasibilityAgent(config=config)

# Test simple
print("\nEjecutando análisis de viabilidad con Claude...\n")

issue = {
    "title": "Add real-time notifications",
    "description": "Users receive instant notifications for important events",
    "requirements": [
        "WebSocket connection",
        "Notification service",
        "Browser push API"
    ],
    "estimated_story_points": 5
}

try:
    result = agent.run({"issue": issue})

    phase_result = result["phase_result"]

    print("=" * 70)
    print("RESULTADO DEL ANALISIS CON CLAUDE")
    print("=" * 70)
    print(f"\nDecision: {phase_result.decision.upper()}")
    print(f"Confidence: {phase_result.confidence:.0%}")
    print(f"Method: {result.get('feasibility_method', 'unknown')}")
    print(f"Risks identified: {len(phase_result.risks)}")

    if phase_result.risks:
        print("\nTop 3 riesgos:")
        for i, risk in enumerate(phase_result.risks[:3], 1):
            print(f"   {i}. [{risk.get('severity', 'unknown').upper()}] {risk.get('description', 'N/A')}")

    print(f"\nReport: {result.get('report_path', 'N/A')}")
    print("\n" + "=" * 70)
    print("TEST EXITOSO - Claude API funciona correctamente")
    print("=" * 70 + "\n")

except Exception as e:
    print(f"\nERROR al ejecutar análisis:")
    print(f"   {type(e).__name__}: {e}")
    print("\nPosibles causas:")
    print("   1. API key inválida o expirada")
    print("   2. Sin créditos en cuenta de Anthropic")
    print("   3. Problema de conexión a internet")
    print("   4. Rate limit excedido")
    sys.exit(1)
