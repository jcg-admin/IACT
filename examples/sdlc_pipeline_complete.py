#!/usr/bin/env python3
"""
Ejemplo Completo: Pipeline SDLC de principio a fin

Este script demuestra cómo ejecutar un pipeline SDLC completo
para una feature desde feasibility hasta deployment.

Uso:
    python3 examples/sdlc_pipeline_complete.py
"""

import sys
from pathlib import Path

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.sdlc.orchestrator import SDLCOrchestratorAgent


def main():
    """Ejecuta pipeline SDLC completo para una feature de autenticación JWT."""

    print("Iniciando Pipeline SDLC Completo\n")
    print("=" * 70)

    # Configuración del LLM
    # Opción 1: Ollama (local, gratis)
    config = {
        "llm_provider": "ollama",
        "model": "qwen2.5-coder:32b",  # o "llama3.1:8b" si tienes menos RAM
        "ollama_base_url": "http://localhost:11434",
        "use_llm": True
    }

    # Opción 2: Anthropic Claude (nube, requiere API key)
    # config = {
    #     "llm_provider": "anthropic",
    #     "model": "claude-sonnet-4-5-20250929",
    #     "use_llm": True
    # }

    # Opción 3: OpenAI GPT-4 (nube, requiere API key)
    # config = {
    #     "llm_provider": "openai",
    #     "model": "gpt-4-turbo-preview",
    #     "use_llm": True
    # }

    # Opción 4: Sin LLM (solo heurísticas)
    # config = None

    # Definir la feature request
    feature_request = {
        "title": "Implement JWT Authentication",
        "description": """
        Implementar sistema de autenticación basado en JWT (JSON Web Tokens)
        que permita a los usuarios registrarse, iniciar sesión y acceder a
        recursos protegidos de forma segura.

        El sistema debe manejar:
        - Registro de nuevos usuarios
        - Login con email/password
        - Generación de access tokens (1h TTL)
        - Generación de refresh tokens (7d TTL)
        - Logout con invalidación de tokens
        - Middleware para proteger rutas
        """,
        "requirements": [
            "Hash seguro de passwords con bcrypt",
            "Tokens firmados con RS256",
            "Refresh token rotation",
            "Token blacklist para logout",
            "Rate limiting en endpoints de auth",
            "Validación de email format",
            "Password strength validation (min 8 chars, uppercase, number)"
        ],
        "acceptance_criteria": [
            "Los usuarios pueden registrarse con email/password",
            "Los usuarios pueden hacer login y recibir tokens",
            "Access tokens expiran después de 1 hora",
            "Refresh tokens permiten obtener nuevos access tokens",
            "Logout invalida ambos tokens",
            "Rutas protegidas rechazan requests sin token válido",
            "Rate limit: máximo 5 login attempts por minuto",
            "Tests tienen coverage >85%"
        ],
        "estimated_story_points": 8,
        "priority": "high",
        "labels": ["security", "authentication", "backend"]
    }

    # Crear orchestrator
    print("Configurando orchestrador...")
    orchestrator = SDLCOrchestratorAgent(config=config)
    print(f"   Provider: {config['llm_provider'] if config else 'heuristic'}")
    print(f"   Model: {config.get('model', 'N/A') if config else 'N/A'}\n")

    # Ejecutar pipeline completo
    print("Ejecutando pipeline SDLC...\n")
    print("-" * 70)

    result = orchestrator.run({
        "feature_request": feature_request,
        "start_phase": "planning",
        "end_phase": "deployment",
        "skip_phases": []  # No saltear ninguna fase
    })

    print("\n" + "=" * 70)
    print("Resultados del Pipeline\n")

    # Mostrar resultado final
    if result['final_decision'] == 'success':
        print("Pipeline completado EXITOSAMENTE\n")

        # Fases completadas
        print(f"Fases completadas: {result['phases_completed']}/{result['total_phases']}")
        for phase in result['execution_log']:
            status_icon = "OK" if phase['status'] == 'completed' else "FAIL"
            print(f"   [{status_icon}] {phase['phase'].upper()}: {phase['decision']} "
                  f"(confidence: {phase.get('confidence', 0):.2f})")

        # Artifacts generados
        print(f"\nArtifacts generados: {len(result['all_artifacts'])}")
        for i, artifact in enumerate(result['all_artifacts'][:10], 1):  # Mostrar primeros 10
            print(f"   {i}. {artifact}")
        if len(result['all_artifacts']) > 10:
            print(f"   ... y {len(result['all_artifacts']) - 10} más")

        # Riesgos identificados
        print(f"\nRiesgos identificados: {len(result['aggregated_risks'])}")
        for risk in result['aggregated_risks'][:5]:  # Mostrar top 5
            severity_label = "[HIGH]" if risk['severity'] == 'high' else "[MEDIUM]"
            print(f"   {severity_label} {risk['description']}")

        # Recomendaciones
        print(f"\nRecomendaciones: {len(result['recommendations'])}")
        for i, rec in enumerate(result['recommendations'][:5], 1):  # Mostrar top 5
            print(f"   {i}. {rec}")

        # Reporte final
        print(f"\nReporte final: {result['report_path']}")
        print(f"   Abrir con: cat {result['report_path']}")

        # Next steps
        if result.get('next_steps'):
            print(f"\nProximos pasos:")
            for i, step in enumerate(result['next_steps'][:5], 1):
                print(f"   {i}. {step}")

        # Método usado
        method = result.get('orchestration_method', 'heuristic')
        print(f"\nMetodo de analisis: {method.upper()}")

    else:
        print("Pipeline DETENIDO antes de completar\n")
        print(f"Detenido en fase: {result.get('stopped_at_phase', 'unknown').upper()}")
        print(f"   Razon: {result.get('stop_reason', 'Unknown reason')}")

        # Mostrar qué fases se completaron
        print(f"\nFases completadas antes de detener: {result['phases_completed']}")
        for phase in result['execution_log']:
            if phase['status'] == 'completed':
                print(f"   [OK] {phase['phase'].upper()}: {phase['decision']}")
            else:
                print(f"   [FAIL] {phase['phase'].upper()}: {phase.get('decision', 'failed')}")

        # Artifacts parciales
        if result['all_artifacts']:
            print(f"\nArtifacts generados (parciales): {len(result['all_artifacts'])}")
            for artifact in result['all_artifacts']:
                print(f"   - {artifact}")

    print("\n" + "=" * 70)
    print("Pipeline finalizado\n")

    return result


if __name__ == "__main__":
    result = main()

    # Salir con código apropiado
    exit_code = 0 if result['final_decision'] == 'success' else 1
    sys.exit(exit_code)
