#!/usr/bin/env python3
"""
Ejemplo: Análisis de Viabilidad (Feasibility) solamente

Este script demuestra cómo usar SDLCFeasibilityAgent para evaluar
rápidamente si una feature es viable antes de invertir tiempo en diseño.

Uso:
    python3 examples/sdlc_feasibility_only.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent


def evaluate_feature(feature_title, feature_desc, requirements, story_points, use_llm=False):
    """
    Evalúa la viabilidad de una feature.

    Args:
        feature_title: Título de la feature
        feature_desc: Descripción detallada
        requirements: Lista de requisitos
        story_points: Estimación de complejidad (1-13)
        use_llm: Si usar LLM o solo heurísticas
    """
    print(f"\n{'='*70}")
    print(f"🔍 Evaluando: {feature_title}")
    print(f"{'='*70}\n")

    # Configurar agente
    config = None
    if use_llm:
        config = {
            "llm_provider": "ollama",
            "model": "llama3.1:8b",  # Modelo rápido para evaluación
            "use_llm": True
        }
        print("🤖 Modo: LLM (Ollama llama3.1:8b)")
    else:
        print("⚙️  Modo: Heurísticas (rápido)")

    agent = SDLCFeasibilityAgent(config=config)

    # Ejecutar análisis
    print("📊 Analizando viabilidad técnica...\n")

    result = agent.run({
        "issue": {
            "title": feature_title,
            "description": feature_desc,
            "requirements": requirements,
            "acceptance_criteria": [],
            "estimated_story_points": story_points
        }
    })

    # Extraer el reporte de feasibility
    report = result.get("feasibility_report")
    if not report:
        print("❌ Error: No se pudo generar el reporte")
        return result

    # Mostrar resultados
    decision_icons = {
        "go": "✅ GO",
        "no-go": "❌ NO-GO",
        "review": "⚠️  REVIEW"
    }
    decision = decision_icons.get(report.decision, report.decision.upper())

    print(f"📋 DECISIÓN: {decision}")
    print(f"🎯 Confianza: {report.confidence:.2%}\n")

    # Viabilidad técnica
    print("💻 Viabilidad Técnica:")
    feasibility = result.get('technical_feasibility', {})
    print(f"   Feasible: {'Sí' if feasibility.get('is_feasible') else 'No'}")
    print(f"   Complejidad: {feasibility.get('complexity', 'unknown')}")
    if feasibility.get('concerns'):
        print(f"   Preocupaciones: {', '.join(feasibility['concerns'][:3])}")
    print()

    # Riesgos
    print(f"⚠️  Riesgos Identificados: {len(report.risks)}")
    if report.risks:
        # Agrupar por severidad
        critical = [r for r in report.risks if r.get('severity') == 'critical']
        high = [r for r in report.risks if r.get('severity') == 'high']
        medium = [r for r in report.risks if r.get('severity') == 'medium']

        if critical:
            print(f"\n   🔴 CRÍTICOS ({len(critical)}):")
            for risk in critical:
                print(f"      - {risk['description']}")

        if high:
            print(f"\n   🟠 ALTOS ({len(high)}):")
            for risk in high[:3]:  # Mostrar máximo 3
                print(f"      - {risk['description']}")

        if medium:
            print(f"\n   🟡 MEDIOS ({len(medium)}):")
            for risk in medium[:2]:  # Mostrar máximo 2
                print(f"      - {risk['description']}")
    print()

    # Esfuerzo estimado
    effort = result.get('effort_analysis', {})
    print("⏱️  Estimación de Esfuerzo:")
    print(f"   Story Points: {effort.get('story_points', story_points)}")
    print(f"   Días estimados: {effort.get('estimated_days', 'N/A')}")
    print(f"   Personas recomendadas: {effort.get('recommended_team_size', 1)}")
    print()

    # Recomendaciones
    if report.recommendations:
        print(f"💡 Recomendaciones ({len(report.recommendations)}):")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"   {i}. {rec}")
        print()

    # Next steps
    if report.next_steps:
        print("🎯 Próximos Pasos:")
        for i, step in enumerate(report.next_steps[:3], 1):
            print(f"   {i}. {step}")
        print()

    # Artifacts
    if report.artifacts:
        print(f"📄 Reporte generado: {report.artifacts[0]}")
        print()

    print("="*70)

    return result


def main():
    """Evalúa múltiples features con diferentes características."""

    print("\n🚀 Análisis de Viabilidad: Evaluación Rápida de Features\n")

    # Feature 1: Simple, viable
    result1 = evaluate_feature(
        feature_title="Add User Avatar Upload",
        feature_desc="Allow users to upload profile pictures (PNG/JPG, max 5MB)",
        requirements=[
            "File upload endpoint",
            "Image validation (format, size)",
            "Storage in /media/avatars/",
            "Thumbnail generation (150x150)",
            "Default avatar for new users"
        ],
        story_points=3,
        use_llm=False  # Heurísticas son suficientes para cases simples
    )

    # Feature 2: Compleja, con riesgos
    result2 = evaluate_feature(
        feature_title="Real-time Chat with WebSockets",
        feature_desc="Implement real-time chat between users using WebSockets",
        requirements=[
            "WebSocket server setup",
            "Message persistence",
            "Online status tracking",
            "Typing indicators",
            "Message delivery confirmation",
            "Support 1000+ concurrent connections"
        ],
        story_points=13,
        use_llm=True  # LLM para análisis profundo de features complejas
    )

    # Feature 3: BLOCKER (violates IACT constraints)
    result3 = evaluate_feature(
        feature_title="Add Redis Cache Layer",
        feature_desc="Use Redis for caching database queries and session storage",
        requirements=[
            "Redis server setup",
            "Cache invalidation strategy",
            "Session storage in Redis",
            "Query result caching"
        ],
        story_points=5,
        use_llm=False
    )

    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE EVALUACIONES")
    print("="*70 + "\n")

    features = [
        ("User Avatar Upload", result1),
        ("Real-time Chat", result2),
        ("Redis Cache", result3)
    ]

    for name, result in features:
        report = result.get("feasibility_report")
        if report:
            icon = "✅" if report.decision == "go" else "❌" if report.decision == "no-go" else "⚠️"
            print(f"{icon} {name:30s} → {report.decision.upper():10s} "
                  f"(confidence: {report.confidence:.0%}, risks: {len(report.risks)})")
        else:
            print(f"❌ {name:30s} → ERROR")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
