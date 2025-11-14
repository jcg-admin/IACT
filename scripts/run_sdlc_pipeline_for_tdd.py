#!/usr/bin/env python3
"""
Script para ejecutar el pipeline SDLC completo para generar TDD
para las técnicas de prompting.

Ejecuta todas las fases:
1. Planning
2. Feasibility
3. Design
4. Testing (usando Auto-CoT y Self-Consistency)
5. Deployment

Genera tests TDD para las técnicas de prompting implementadas.
"""

import json
import os
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts" / "coding" / "ai"))

# Import agents
from sdlc.planner_agent import SDLCPlannerAgent
from sdlc.feasibility_agent import SDLCFeasibilityAgent
from sdlc.design_agent import SDLCDesignAgent
from sdlc.testing_agent import SDLCTestingAgent
from sdlc.deployment_agent import SDLCDeploymentAgent


def main():
    """Ejecuta el pipeline SDLC completo."""

    print("=" * 80)
    print("SDLC Pipeline para Generación de TDD - Técnicas de Prompting")
    print("=" * 80)

    # Configuración
    config = {
        "llm_provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "project_root": str(project_root),
        "output_dir": str(project_root / "docs" / "agent")
    }

    # Verificar API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY no está configurada")
        print("Por favor, configura la API key en variables de entorno")
        return 1

    # Feature request
    feature_request = """
Implementar tests TDD completos para todas las técnicas de prompting en scripts/coding/ai/agents/base/

Requisitos:
- Generar tests unitarios con cobertura 80%+ para cada técnica de prompting
- Usar pytest como framework de testing
- Aplicar TDD estricto siguiendo la metodología del proyecto
- Documentar cada test con docstrings claros
- Incluir tests para casos edge y manejo de errores
- Usar técnicas Auto-CoT y Self-Consistency para la generación

Módulos a testear:
1. auto_cot_agent.py - Automatic Chain-of-Thought
2. self_consistency.py - Multiple reasoning paths
3. chain_of_verification.py - Step-by-step verification
4. tree_of_thoughts.py - Tree exploration
5. fundamental_techniques.py - Role, Few-Shot, Zero-Shot
6. knowledge_techniques.py - ReAct, RAG, Tool-use
7. optimization_techniques.py - Constitutional AI, Constrained
8. prompt_templates.py - Template engine
9. search_optimization_techniques.py - Binary Search, Greedy
10. specialized_techniques.py - Expert, Meta-prompting
11. structuring_techniques.py - Chaining, Decomposition

Prioridad: HIGH
Target: 2025-11-14
"""

    project_context = """
Proyecto IACT - Sistema de agentes IA con arquitectura SDLC.
Todos los agentes SDLC y de automatización siguen TDD estricto.
Ubicación tests: scripts/coding/ai/tests/
Framework: pytest
Cobertura mínima: 80%
Guardarraíles: Constitutional AI aplicados a todos los agentes
"""

    try:
        # FASE 1: PLANNING
        print("\n" + "=" * 80)
        print("FASE 1: PLANNING - SDLCPlannerAgent")
        print("=" * 80)

        planner = SDLCPlannerAgent(config=config)
        planning_input = {
            "feature_request": feature_request,
            "project_context": project_context
        }

        planning_result = planner.execute(planning_input)

        print(f"\nDecisión: {planning_result.decision}")
        print(f"Issue título: {planning_result.output.get('issue_title', 'N/A')}")
        print(f"Story points: {planning_result.output.get('story_points', 'N/A')}")
        print(f"Prioridad: {planning_result.output.get('priority', 'N/A')}")

        # Guardar resultado
        with open(project_root / "docs" / "agent" / "planning" / "planning_result.json", "w") as f:
            json.dump(planning_result.output, f, indent=2)

        if planning_result.decision != "go":
            print(f"\nPlanning decision: {planning_result.decision}")
            print("No se puede proceder a la siguiente fase.")
            return 1

        # FASE 2: FEASIBILITY
        print("\n" + "=" * 80)
        print("FASE 2: FEASIBILITY - SDLCFeasibilityAgent")
        print("=" * 80)

        feasibility = SDLCFeasibilityAgent(config=config)
        feasibility_input = {
            "issue": planning_result.output,
            "project_context": project_context
        }

        feasibility_result = feasibility.execute(feasibility_input)

        print(f"\nDecisión: {feasibility_result.decision}")
        print(f"Riesgos identificados: {len(feasibility_result.output.get('risks', []))}")

        # Guardar resultado
        with open(project_root / "docs" / "agent" / "feasibility" / "feasibility_result.json", "w") as f:
            json.dump(feasibility_result.output, f, indent=2)

        if feasibility_result.decision == "no-go":
            print("\nFeasibility analysis: NO-GO")
            print("Proyecto no es viable.")
            return 1

        # FASE 3: DESIGN
        print("\n" + "=" * 80)
        print("FASE 3: DESIGN - SDLCDesignAgent")
        print("=" * 80)

        design = SDLCDesignAgent(config=config)
        design_input = {
            "issue": planning_result.output,
            "feasibility_result": feasibility_result.output
        }

        design_result = design.execute(design_input)

        print(f"\nDecisión: {design_result.decision}")
        print(f"HLD generado: {'Sí' if design_result.output.get('hld') else 'No'}")
        print(f"LLD generado: {'Sí' if design_result.output.get('lld') else 'No'}")

        # Guardar resultado
        with open(project_root / "docs" / "agent" / "design" / "design_result.json", "w") as f:
            json.dump(design_result.output, f, indent=2)

        if design_result.decision != "go":
            print(f"\nDesign decision: {design_result.decision}")
            return 1

        # FASE 4: TESTING
        print("\n" + "=" * 80)
        print("FASE 4: TESTING - SDLCTestingAgent")
        print("=" * 80)
        print("Generando tests usando Auto-CoT y Self-Consistency...")

        testing = SDLCTestingAgent(config=config)
        testing_input = {
            "issue": planning_result.output,
            "design_result": design_result.output,
            "implementation_status": "pending"
        }

        testing_result = testing.execute(testing_input)

        print(f"\nDecisión: {testing_result.decision}")
        print(f"Test cases generados: {len(testing_result.output.get('test_cases', []))}")
        print(f"Coverage target: {testing_result.output.get('coverage_target', 'N/A')}%")

        # Guardar resultado
        with open(project_root / "docs" / "agent" / "testing" / "testing_result.json", "w") as f:
            json.dump(testing_result.output, f, indent=2)

        # FASE 5: DEPLOYMENT
        print("\n" + "=" * 80)
        print("FASE 5: DEPLOYMENT - SDLCDeploymentAgent")
        print("=" * 80)

        deployment = SDLCDeploymentAgent(config=config)
        deployment_input = {
            "issue": planning_result.output,
            "design_result": design_result.output,
            "testing_result": testing_result.output
        }

        deployment_result = deployment.execute(deployment_input)

        print(f"\nDecisión: {deployment_result.decision}")
        print(f"Deployment plan generado: {'Sí' if deployment_result.output.get('deployment_plan') else 'No'}")

        # Guardar resultado
        with open(project_root / "docs" / "agent" / "deployment" / "deployment_result.json", "w") as f:
            json.dump(deployment_result.output, f, indent=2)

        # RESUMEN
        print("\n" + "=" * 80)
        print("PIPELINE SDLC COMPLETADO")
        print("=" * 80)
        print(f"\n1. Planning: {planning_result.decision}")
        print(f"2. Feasibility: {feasibility_result.decision}")
        print(f"3. Design: {design_result.decision}")
        print(f"4. Testing: {testing_result.decision}")
        print(f"5. Deployment: {deployment_result.decision}")

        print("\nResultados guardados en: docs/agent/")
        print("\nPróximo paso: Revisar los test cases generados y ejecutar la generación de tests")

        return 0

    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
