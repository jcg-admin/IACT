#!/usr/bin/env python3
"""
scripts/ai/examples/example_specific_module.py

Ejemplo: Generar tests para un módulo específico con configuración custom.
"""

import sys
from pathlib import Path

# Agregar parent al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_generation_orchestrator import TestGenerationOrchestrator


def main():
    """Ejemplo de uso programático del orquestador."""

    # Configuración custom
    config = {
        "save_results": True,
        "output_dir": "output/test_generation_custom",
        "agents": {
            "coverage_analyzer": {
                "min_coverage": 85,
                "threshold_low": 70,
                # Filtrar solo archivos específicos
                "include_patterns": ["**/models.py", "**/views.py"],
                "exclude_patterns": ["**/migrations/**", "**/tests/**"]
            },
            "test_planner": {
                "max_tests_per_run": 5,
                # Estrategias de generación
                "strategies": [
                    "happy_path",      # Casos normales
                    "edge_cases",      # Casos límite
                    "error_handling",  # Manejo de errores
                    "boundary_values"  # Valores frontera
                ]
            },
            "llm_generator": {
                "llm_provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.3,
                # Contexto adicional para el LLM
                "system_prompt": """
                Eres un experto en testing de Django.
                Genera tests usando pytest y factory_boy.
                Sigue las convenciones AAA (Arrange, Act, Assert).
                Incluye docstrings descriptivos.
                """,
                "few_shot_examples": [
                    {
                        "input": "def calculate_total(items): ...",
                        "output": "def test_calculate_total_with_items(): ..."
                    }
                ]
            },
            "syntax_validator": {
                "run_mypy": True,
                "run_ruff": True,
                "run_black": True,
                "strict_mode": True
            },
            "test_runner": {
                "timeout": 300,
                "verbose": True,
                "fail_fast": False
            },
            "coverage_verifier": {
                "min_coverage_increase": 5.0,
                "allow_regression": False,
                # Métricas adicionales
                "check_branch_coverage": True,
                "min_branch_coverage": 80.0
            },
            "pr_creator": {
                "enabled": True,
                "branch_prefix": "test/auto-generated",
                "labels": ["bot-generated-tests", "needs-review"],
                "reviewers": ["@team-qa"],
                "draft": True  # Crear como draft PR
            }
        }
    }

    # Crear orquestador
    orchestrator = TestGenerationOrchestrator(config)

    # Ejecutar
    project_path = Path(__file__).parent.parent.parent.parent / "api" / "callcentersite"

    print(f"Generando tests para: {project_path}")
    print("Configuración: Custom con validación estricta")
    print("")

    results = orchestrator.execute(project_path)

    # Procesar resultados
    if results.get("status") == "success":
        print("\nGENERACIÓN EXITOSA")
        print("-" * 50)

        data = results.get("data", {})
        print(f"Cobertura anterior: {data.get('previous_coverage', 0):.2f}%")
        print(f"Cobertura nueva:    {data.get('new_coverage', 0):.2f}%")
        print(f"Incremento:         +{data.get('coverage_increase', 0):.2f}%")
        print(f"Tests generados:    {data.get('total_generated', 0)}")
        print(f"Tests validados:    {data.get('total_validated', 0)}")
        print(f"Tests pasaron:      {data.get('total_passed', 0)}")

        if data.get('pr_created'):
            print(f"\nPull Request: {data.get('pr_url')}")
            print(f"Branch:       {data.get('branch_name')}")

        return 0
    else:
        print("\nGENERACIÓN FALLIDA")
        print("-" * 50)
        print(f"Error: {results.get('errors')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
