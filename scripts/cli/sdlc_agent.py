#!/usr/bin/env python3
"""
CLI para ejecutar agentes SDLC.

Permite ejecutar fases individuales del SDLC o el pipeline completo.

Uso:
    # Planning phase
    python scripts/sdlc_agent.py --phase planning --input "Feature: Implementar 2FA"

    # Completeness analysis
    python scripts/sdlc_agent.py --phase completeness_analysis --docs-path docs/

    # Pipeline completo
    python scripts/sdlc_agent.py --pipeline --input "Feature: Sistema de notificaciones"

    # Dry-run (no guarda artefactos)
    python scripts/sdlc_agent.py --phase planning --input "..." --dry-run
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add scripts/ai to path
sys.path.insert(0, str(Path(__file__).parent / "ai"))

from agents.sdlc_base import SDLCAgent, SDLCPipeline
from agents.sdlc_planner import SDLCPlannerAgent
from agents.tdd_feature_agent import TDDFeatureAgent

# Add scripts/ to path for completeness_analysis_agent
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_logging(verbose: bool = False) -> None:
    """Configura logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def _detect_docs_structure() -> str:
    """
    Auto-detecta la estructura de directorios de documentación del proyecto.

    Técnica de Prompt Engineering: Pattern Recognition
    - Examina estructuras existentes (backend, frontend, infrastructure)
    - Identifica patrón común de subdirectorios
    - Infiere estructura para nuevos componentes (agents)

    Returns:
        Directorio base para documentación de agentes
    """
    project_root = Path.cwd()
    docs_dir = project_root / "docs"

    # Pattern Recognition: Detectar componentes existentes con estructura SDLC
    existing_components = ["backend", "frontend", "infrastructure", "api"]
    detected_pattern = None

    for component in existing_components:
        component_dir = docs_dir / component
        if component_dir.exists():
            # Verificar subdirectorios típicos de SDLC
            expected_subdirs = [
                "arquitectura",
                "diseno_detallado",
                "planificacion_y_releases",
                "requisitos"
            ]

            has_pattern = all(
                (component_dir / subdir).exists()
                for subdir in expected_subdirs[:2]  # Al menos arquitectura y diseno_detallado
            )

            if has_pattern:
                detected_pattern = {
                    "base": "docs",
                    "component_level": True,
                    "subdirs": expected_subdirs
                }
                break

    # Si se detectó el patrón, aplicarlo a "agent"
    if detected_pattern:
        # Patrón: docs/{component}/{fase}/
        # Para agents: docs/agent/
        return "docs/agent"
    else:
        # Fallback: estructura legacy
        return "docs/sdlc_outputs"


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Carga configuración de agentes SDLC.

    Args:
        config_path: Ruta a archivo de configuración (opcional)

    Returns:
        Diccionario de configuración
    """
    if config_path and config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    # Configuración por defecto
    # Auto-detect output directory structure pattern from project
    output_dir = _detect_docs_structure()

    return {
        "project_root": str(Path.cwd()),
        "output_dir": output_dir,
        "llm_provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929"
    }


def run_planning_phase(
    feature_request: str,
    config: Dict[str, Any],
    project_context: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Ejecuta la fase de Planning.

    Args:
        feature_request: Descripción del feature
        config: Configuración
        project_context: Contexto del proyecto (opcional)
        dry_run: Si True, no guarda artefactos

    Returns:
        Resultado de la ejecución
    """
    if dry_run:
        config = {**config, "output_dir": "/tmp/sdlc_outputs"}

    agent = SDLCPlannerAgent(config=config)

    input_data = {
        "feature_request": feature_request,
        "project_context": project_context or "",
        "backlog": []
    }

    result = agent.execute(input_data)

    return result.to_dict()


def run_implementation_phase(
    issue_data: Dict[str, Any],
    config: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Ejecuta la fase de Implementation con TDD.

    Args:
        issue_data: Datos del issue con:
            - issue_title: str
            - acceptance_criteria: List[str]
            - technical_requirements: List[str]
            - target_module: str
        config: Configuración
        dry_run: Si True, no guarda artefactos

    Returns:
        Resultado de la ejecución
    """
    if dry_run:
        config = {**config, "output_dir": "/tmp/sdlc_outputs"}

    agent = TDDFeatureAgent(config=config)

    result = agent.execute(issue_data)

    return result.to_dict()


def run_completeness_analysis(
    docs_path: str,
    output_path: Optional[str] = None,
    format_type: str = "text"
) -> Dict[str, Any]:
    """
    Ejecuta el agente de análisis de completitud de documentación.

    Args:
        docs_path: Ruta al directorio de documentación
        output_path: Ruta para guardar el reporte JSON (opcional)
        format_type: Formato de salida (text o json)

    Returns:
        Resultado del análisis
    """
    try:
        from completeness_analysis_agent import CompletenessAnalysisAgent
    except ImportError:
        return {
            "status": "failed",
            "errors": ["No se pudo importar CompletenessAnalysisAgent. Verifica que el script esté en scripts/"]
        }

    try:
        # Crear y ejecutar agente
        agent = CompletenessAnalysisAgent(base_path=docs_path)
        results = agent.run_full_analysis()

        # Imprimir resumen si es formato text
        if format_type == "text":
            agent.print_summary()

        # Guardar reporte
        if output_path:
            report_path = agent.save_report(output_path)
        else:
            report_path = agent.save_report()  # Usa default en /tmp/

        return {
            "status": "success",
            "data": {
                "results": results,
                "report_path": report_path
            }
        }

    except Exception as e:
        return {
            "status": "failed",
            "errors": [f"Error ejecutando completeness analysis: {str(e)}"]
        }


def run_pipeline(
    feature_request: str,
    config: Dict[str, Any],
    auto_proceed: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline SDLC completo.

    Args:
        feature_request: Descripción del feature
        config: Configuración
        auto_proceed: Si True, no pide confirmación humana
        dry_run: Si True, no guarda artefactos

    Returns:
        Resultado del pipeline
    """
    if dry_run:
        config = {**config, "output_dir": "/tmp/sdlc_outputs"}

    # Por ahora solo Planning está implementado
    agents = [
        SDLCPlannerAgent(config=config),
        # TODO: Agregar más agentes cuando estén implementados
        # SDLCFeasibilityAgent(config=config),
        # SDLCDesignAgent(config=config),
        # ...
    ]

    pipeline = SDLCPipeline(
        name="SDLC_Complete",
        agents=agents,
        auto_proceed=auto_proceed
    )

    input_data = {
        "feature_request": feature_request,
        "project_context": "",
        "backlog": []
    }

    result = pipeline.execute(input_data)

    return result


def read_input_file(input_file: Path) -> str:
    """Lee feature request desde archivo."""
    return input_file.read_text(encoding="utf-8")


def print_result(result: Dict[str, Any], output_format: str = "text") -> None:
    """
    Imprime resultado en formato especificado.

    Args:
        result: Resultado de la ejecución
        output_format: Formato (text, json)
    """
    if output_format == "json":
        print(json.dumps(result, indent=2))
        return

    # Formato text
    print("\n" + "="*80)
    print("RESULTADO DE EJECUCIÓN")
    print("="*80)

    status = result.get("status", "unknown")
    print(f"\nEstado: {status.upper()}")

    if status == "success":
        data = result.get("data", {})

        if "issue_title" in data:
            print(f"\nIssue generado:")
            print(f"  Título: {data['issue_title']}")
            print(f"  Story Points: {data.get('story_points', 'N/A')}")
            print(f"  Prioridad: {data.get('priority', 'N/A')}")
            print(f"  Artefacto: {data.get('issue_path', 'N/A')}")

        if "acceptance_criteria" in data:
            print(f"\nAcceptance Criteria ({len(data['acceptance_criteria'])}):")
            for i, criterion in enumerate(data['acceptance_criteria'][:5], 1):
                print(f"  {i}. {criterion}")
            if len(data['acceptance_criteria']) > 5:
                print(f"  ... y {len(data['acceptance_criteria']) - 5} más")

        if "technical_requirements" in data:
            print(f"\nRequisitos Técnicos ({len(data['technical_requirements'])}):")
            for req in data['technical_requirements'][:5]:
                print(f"  - {req}")

        phase_result = data.get("phase_result")
        if phase_result:
            print(f"\nDecisión de fase: {phase_result.decision.upper()}")
            print(f"Confianza: {phase_result.confidence * 100:.1f}%")

            if phase_result.recommendations:
                print(f"\nRecomendaciones:")
                for rec in phase_result.recommendations:
                    print(f"  - {rec}")

    elif status == "failed":
        print(f"\nErrores:")
        for error in result.get("errors", []):
            print(f"  - {error}")

    elif status == "blocked":
        print(f"\nBloqueado en fase: {result.get('blocked_phase', 'unknown')}")
        print(f"Razones:")
        for error in result.get("errors", []):
            print(f"  - {error}")

    print("\n" + "="*80 + "\n")


def main() -> int:
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="CLI para agentes SDLC del proyecto IACT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:

  # Ejecutar planning phase
  python scripts/cli/sdlc_agent.py --phase planning --input "Feature: Sistema de notificaciones push"

  # Ejecutar implementation phase con TDD
  python scripts/cli/sdlc_agent.py --phase implementation --issue-file issue_data.json

  # Ejecutar completeness analysis
  python scripts/cli/sdlc_agent.py --phase completeness_analysis --docs-path docs/

  # Completeness analysis con output personalizado
  python scripts/cli/sdlc_agent.py --phase completeness_analysis --docs-path docs/ --output-path /tmp/report.json

  # Leer desde archivo
  python scripts/cli/sdlc_agent.py --phase planning --input-file feature_request.txt

  # Pipeline completo (cuando esté implementado)
  python scripts/cli/sdlc_agent.py --pipeline --input "Feature: Dashboard de métricas"

  # Dry-run (no guarda artefactos)
  python scripts/cli/sdlc_agent.py --phase planning --input "..." --dry-run

  # Output en JSON
  python scripts/cli/sdlc_agent.py --phase planning --input "..." --format json
        """
    )

    parser.add_argument(
        "--phase",
        choices=["planning", "implementation", "feasibility", "design", "testing", "deployment", "maintenance", "completeness_analysis"],
        help="Fase SDLC a ejecutar"
    )

    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Ejecutar pipeline SDLC completo"
    )

    parser.add_argument(
        "--input",
        type=str,
        help="Feature request (texto directo)"
    )

    parser.add_argument(
        "--input-file",
        type=Path,
        help="Archivo con feature request"
    )

    parser.add_argument(
        "--issue-file",
        type=Path,
        help="Archivo JSON con issue data (para fase implementation)"
    )

    parser.add_argument(
        "--docs-path",
        type=str,
        default="docs",
        help="Ruta al directorio de documentación (para completeness_analysis)"
    )

    parser.add_argument(
        "--output-path",
        type=str,
        help="Ruta para guardar reporte JSON (para completeness_analysis)"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Archivo de configuración JSON (opcional)"
    )

    parser.add_argument(
        "--project-context",
        type=str,
        help="Contexto del proyecto (opcional)"
    )

    parser.add_argument(
        "--auto-proceed",
        action="store_true",
        help="Auto-proceder sin confirmación humana (solo para pipeline)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No guardar artefactos (modo prueba)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Formato de output (default: text)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logging verbose"
    )

    args = parser.parse_args()

    # Validar argumentos
    if not args.phase and not args.pipeline:
        parser.error("Debes especificar --phase o --pipeline")

    # Validar input segun la fase
    if args.phase == "implementation":
        if not args.issue_file:
            parser.error("Fase implementation requiere --issue-file con datos del issue")
    elif args.phase == "completeness_analysis":
        # completeness_analysis no requiere input, usa --docs-path
        pass
    elif not args.input and not args.input_file:
        parser.error("Debes especificar --input o --input-file")

    # Setup
    setup_logging(args.verbose)

    # Cargar configuración
    config = load_config(args.config)

    # Leer input
    if args.input_file:
        feature_request = read_input_file(args.input_file)
    else:
        feature_request = args.input

    try:
        # Ejecutar fase o pipeline
        if args.pipeline:
            result = run_pipeline(
                feature_request=feature_request,
                config=config,
                auto_proceed=args.auto_proceed,
                dry_run=args.dry_run
            )
        elif args.phase == "planning":
            result = run_planning_phase(
                feature_request=feature_request,
                config=config,
                project_context=args.project_context,
                dry_run=args.dry_run
            )
        elif args.phase == "implementation":
            # Leer issue data desde archivo JSON
            with open(args.issue_file, encoding="utf-8") as f:
                issue_data = json.load(f)

            result = run_implementation_phase(
                issue_data=issue_data,
                config=config,
                dry_run=args.dry_run
            )
        elif args.phase == "completeness_analysis":
            result = run_completeness_analysis(
                docs_path=args.docs_path,
                output_path=args.output_path,
                format_type=args.format
            )
        else:
            print(f"ERROR: Fase '{args.phase}' no implementada aún")
            return 1

        # Imprimir resultado
        print_result(result, args.format)

        # Return code basado en status
        status = result.get("status", "unknown")
        if status in ["success", "requires_approval"]:
            return 0
        elif status == "blocked":
            return 2
        else:
            return 1

    except Exception as e:
        logging.exception(f"Error ejecutando agente SDLC: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
