#!/usr/bin/env python3
"""
Ejemplo: Agentes que se Adaptan al Ambiente

Muestra como los agentes SDLC detectan automaticamente el ambiente
y ajustan su comportamiento:

- Desarrollo: Usa Ollama local (gratis)
- Staging: Usa Claude Haiku (barato)
- Produccion: Usa Claude Sonnet (mejor)

Uso:
    # Desarrollo
    ENVIRONMENT=development python3 examples/agent_environment_example.py

    # Staging
    ENVIRONMENT=staging python3 examples/agent_environment_example.py

    # Produccion
    ENVIRONMENT=production python3 examples/agent_environment_example.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.shared.environment_config import get_environment_config
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent


def print_section(title: str):
    """Imprime una seccion con formato."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def analyze_feature_in_current_environment():
    """
    Analiza una feature usando la configuracion del ambiente actual.
    """
    # Obtener configuracion del ambiente
    config = get_environment_config()

    print_section(f"AMBIENTE: {config.environment.upper()}")

    # Mostrar configuracion de LLM
    llm_config = config.get_llm_config()

    print("Configuracion LLM:")
    print(f"  Provider: {llm_config['llm_provider']}")
    print(f"  Model: {llm_config['model']}")
    print(f"  Use LLM: {llm_config['use_llm']}")
    print(f"  Prefer Local: {llm_config.get('prefer_local', False)}")
    print(f"  Max Tokens: {llm_config['max_tokens']}")

    if 'monthly_budget' in llm_config:
        print(f"  Monthly Budget: ${llm_config['monthly_budget']}")

    # Caracteristicas del ambiente
    print("\nCaracteristicas del ambiente:")

    if config.is_dev:
        print("  - Desarrollo local")
        print("  - LLM: Ollama (GRATIS, local)")
        print("  - Fallback: Heuristicas")
        print("  - Database: VM localhost")
        print("  - Velocidad: Media (depende de hardware)")
        print("  - Costo: $0")

    elif config.is_staging:
        print("  - Testing pre-produccion")
        print("  - LLM: Claude Haiku (barato)")
        print("  - Fallback: Heuristicas")
        print("  - Database: Staging server")
        print("  - Velocidad: Rapida")
        print("  - Costo: ~$0.001 por request")

    elif config.is_prod:
        print("  - Produccion real")
        print("  - LLM: Claude Sonnet (mejor)")
        print("  - Fallback: Heuristicas")
        print("  - Database: Production server")
        print("  - Velocidad: Muy rapida")
        print("  - Costo: ~$0.003 por request")

    # Feature a analizar
    print_section("FEATURE A ANALIZAR")

    issue = {
        "title": "Implement Two-Factor Authentication (2FA)",
        "description": """
        Add TOTP-based 2FA for user accounts.
        Users can enable 2FA in their profile settings.
        """,
        "requirements": [
            "TOTP library integration (pyotp)",
            "QR code generation",
            "Backup codes (10 codes)",
            "Rate limiting (max 3 attempts per 5 min)"
        ],
        "acceptance_criteria": [
            "Users can enable 2FA with QR code",
            "Backup codes work for login",
            "Rate limiting prevents brute force"
        ],
        "estimated_story_points": 8
    }

    print(f"Title: {issue['title']}")
    print(f"Story Points: {issue['estimated_story_points']}")
    print(f"Requirements: {len(issue['requirements'])}")

    # Crear agente con config del ambiente
    print_section("EJECUTANDO ANALISIS")

    print("Creando SDLCFeasibilityAgent...")
    agent = SDLCFeasibilityAgent(config=llm_config)

    print(f"Agente configurado para: {config.environment}")

    # Ejecutar analisis
    start_time = time.time()

    print("\nAnalizando viabilidad...")
    result = agent.run({"issue": issue})

    duration = time.time() - start_time

    # Resultados
    print_section("RESULTADOS")

    phase_result = result["phase_result"]

    print(f"Decision: {phase_result.decision.upper()}")
    print(f"Confidence: {phase_result.confidence:.1%}")
    print(f"Risks: {len(phase_result.risks)}")
    print(f"Duration: {duration:.2f}s")

    if phase_result.risks:
        print("\nRiesgos identificados:")
        for i, risk in enumerate(phase_result.risks, 1):
            severity = risk.get('severity', 'unknown')
            description = risk.get('risk', 'N/A')
            print(f"  {i}. [{severity.upper()}] {description}")

    effort = result.get('effort_analysis', {})
    if effort:
        print("\nEsfuerzo estimado:")
        print(f"  Story Points: {effort.get('story_points', 'N/A')}")
        print(f"  Hours: {effort.get('estimated_hours', 'N/A')}")
        print(f"  Days: {effort.get('estimated_days', 'N/A')}")

    # Reporte generado
    report_path = result.get('report_path')
    if report_path:
        print(f"\nReporte generado: {report_path}")

    # Analisis de costo/performance
    print_section("ANALISIS DE COSTO/PERFORMANCE")

    if config.is_dev:
        print("Desarrollo:")
        print(f"  Tiempo: {duration:.2f}s")
        print(f"  Costo: $0 (Ollama local)")
        print(f"  Recomendacion: Ideal para iteracion rapida")

    elif config.is_staging:
        estimated_cost = 0.001  # Claude Haiku
        print("Staging:")
        print(f"  Tiempo: {duration:.2f}s")
        print(f"  Costo: ~${estimated_cost:.4f} (Claude Haiku)")
        print(f"  Recomendacion: Bueno para testing pre-produccion")

    elif config.is_prod:
        estimated_cost = 0.003  # Claude Sonnet
        print("Produccion:")
        print(f"  Tiempo: {duration:.2f}s")
        print(f"  Costo: ~${estimated_cost:.4f} (Claude Sonnet)")
        print(f"  Recomendacion: Mejor calidad para decisiones criticas")

        # Proyeccion mensual
        monthly_requests = 1000
        monthly_cost = estimated_cost * monthly_requests
        print(f"\n  Proyeccion mensual (1000 requests):")
        print(f"    Costo: ${monthly_cost:.2f}/mes")
        print(f"    Budget: ${llm_config['monthly_budget']}/mes")

        if monthly_cost > llm_config['monthly_budget']:
            print(f"    [WARNING] Excede budget por ${monthly_cost - llm_config['monthly_budget']:.2f}")
        else:
            print(f"    [OK] Dentro del budget")


def compare_environments():
    """
    Compara como se comportaria el mismo analisis en diferentes ambientes.
    """
    print_section("COMPARACION ENTRE AMBIENTES")

    print("""
┌─────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Aspecto     │ Development      │ Staging          │ Production       │
├─────────────┼──────────────────┼──────────────────┼──────────────────┤
│ LLM         │ Ollama (local)   │ Claude Haiku     │ Claude Sonnet    │
│ Model       │ llama3.1:8b      │ claude-3-haiku   │ claude-3-5-sonnet│
│ Costo       │ $0               │ ~$0.001/request  │ ~$0.003/request  │
│ Velocidad   │ 2-5s             │ 1-2s             │ 1-2s             │
│ Calidad     │ Buena            │ Muy buena        │ Excelente        │
│ Database    │ VM localhost     │ staging-db       │ prod-db (SSL)    │
│ Cache       │ Memoria          │ Redis            │ Redis            │
│ Monitoring  │ Logs console     │ Logs + Sentry    │ Sentry + APM     │
└─────────────┴──────────────────┴──────────────────┴──────────────────┘
    """)

    print("\nRecomendaciones:")
    print("""
1. DESARROLLO (dia a dia):
   - Usar Ollama local (gratis, privado)
   - Iteracion rapida sin costos
   - Fallback a heuristicas si Ollama no disponible

2. STAGING (testing):
   - Usar Claude Haiku (barato)
   - Probar flujo completo antes de prod
   - Validar integraciones

3. PRODUCCION (decisiones reales):
   - Usar Claude Sonnet (mejor calidad)
   - Monitorear costos con llm_cost_optimizer
   - Habilitar Sentry para error tracking
    """)


def main():
    """Ejecuta ejemplo de agente adaptativo."""
    print("\n" + "="*70)
    print(" EJEMPLO: AGENTES ADAPTATIVOS POR AMBIENTE")
    print("="*70)

    # Analizar en ambiente actual
    analyze_feature_in_current_environment()

    # Comparar ambientes
    compare_environments()

    # Tips finales
    print_section("COMO CAMBIAR DE AMBIENTE")

    print("""
Metodo 1: Variable de entorno
    export ENVIRONMENT=development
    python3 examples/agent_environment_example.py

    export ENVIRONMENT=staging
    python3 examples/agent_environment_example.py

    export ENVIRONMENT=production
    python3 examples/agent_environment_example.py

Metodo 2: Archivo .env
    # Editar .env
    ENVIRONMENT=production

    # Ejecutar
    python3 examples/agent_environment_example.py

Metodo 3: Parametro programatico
    import os
    os.environ['ENVIRONMENT'] = 'staging'

    from scripts.ai.shared.environment_config import get_environment_config
    config = get_environment_config()
    """)

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
