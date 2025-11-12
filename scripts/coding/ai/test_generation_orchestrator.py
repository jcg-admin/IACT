#!/usr/bin/env python3
"""
Test Generation Orchestrator

Orquestador principal que coordina los 7 agentes especializados para
generación automática de tests con LLM.

Flujo:
1. CoverageAnalyzer → Analiza gaps de cobertura
2. TestPlanner → Planifica tests a generar
3. LLMGenerator → Genera código con LLM
4. SyntaxValidator → Valida sintaxis y estilo
5. TestRunner → Ejecuta tests
6. CoverageVerifier → Verifica incremento de cobertura
7. PRCreator → Crea Pull Request

Uso:
    python test_generation_orchestrator.py --project-path /path/to/project
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Importar agentes
from agents.base import Pipeline
from agents.coverage_analyzer import CoverageAnalyzer
from agents.test_planner import TestPlanner
from agents.llm_generator import LLMGenerator
from agents.syntax_validator import SyntaxValidator
from agents.test_runner import TestRunner
from agents.coverage_verifier import CoverageVerifier
from agents.pr_creator import PRCreator


class TestGenerationOrchestrator:
    """
    Orquestador principal del pipeline de generación de tests.

    Coordina la ejecución secuencial de los 7 agentes especializados
    y gestiona el flujo de datos entre ellos.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el orquestador.

        Args:
            config: Configuración del pipeline
        """
        self.config = config
        self.logger = self._setup_logger()
        self.pipeline = self._build_pipeline()

    def _setup_logger(self) -> logging.Logger:
        """Configura el logger principal."""
        logger = logging.getLogger("TestGenerationOrchestrator")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _build_pipeline(self) -> Pipeline:
        """
        Construye el pipeline con los 7 agentes.

        Returns:
            Pipeline configurado
        """
        # Configuración de cada agente
        agent_configs = self.config.get("agents", {})

        agents = [
            CoverageAnalyzer(agent_configs.get("coverage_analyzer")),
            TestPlanner(agent_configs.get("test_planner")),
            LLMGenerator(agent_configs.get("llm_generator")),
            SyntaxValidator(agent_configs.get("syntax_validator")),
            TestRunner(agent_configs.get("test_runner")),
            CoverageVerifier(agent_configs.get("coverage_verifier")),
            PRCreator(agent_configs.get("pr_creator"))
        ]

        return Pipeline(name="TestGenerationPipeline", agents=agents)

    def execute(self, project_path: Path) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo.

        Args:
            project_path: Ruta del proyecto a analizar

        Returns:
            Diccionario con los resultados del pipeline
        """
        self.logger.info("=" * 80)
        self.logger.info("Iniciando Test Generation Pipeline")
        self.logger.info("=" * 80)

        # Datos iniciales
        initial_data = {
            "project_path": str(project_path)
        }

        # Ejecutar pipeline
        results = self.pipeline.execute(initial_data)

        # Guardar resultados
        if self.config.get("save_results", True):
            output_dir = Path(self.config.get("output_dir", "output/test_generation"))
            self.pipeline.save_results(output_dir)
            self.logger.info(f"Resultados guardados en {output_dir}")

        # Mostrar resumen
        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """
        Imprime un resumen de los resultados.

        Args:
            results: Resultados del pipeline
        """
        self.logger.info("=" * 80)
        self.logger.info("RESUMEN DEL PIPELINE")
        self.logger.info("=" * 80)

        status = results.get("status")

        if status == "success":
            data = results.get("data", {})

            self.logger.info("\nRESULTADO: EXITOSO\n")

            # Cobertura
            self.logger.info("COBERTURA:")
            self.logger.info(f"  Anterior: {data.get('previous_coverage', 0):.2f}%")
            self.logger.info(f"  Nueva:    {data.get('new_coverage', 0):.2f}%")
            self.logger.info(f"  Incremento: +{data.get('coverage_increase', 0):.2f}%")

            # Tests
            self.logger.info("\nTESTS:")
            self.logger.info(f"  Generados: {data.get('total_generated', 0)}")
            self.logger.info(f"  Validados: {data.get('total_validated', 0)}")
            self.logger.info(f"  Pasaron:   {data.get('total_passed', 0)}")

            # PR
            if data.get('pr_created'):
                self.logger.info("\nPULL REQUEST:")
                self.logger.info(f"  URL: {data.get('pr_url')}")
                self.logger.info(f"  Branch: {data.get('branch_name')}")
                self.logger.info(f"  Archivos: {len(data.get('files_added', []))}")

        elif status == "failed":
            self.logger.error("\nRESULTADO: FALLIDO\n")
            self.logger.error(f"Agente fallido: {results.get('failed_agent')}")
            self.logger.error(f"Errores: {results.get('errors')}")

        elif status == "blocked":
            self.logger.warning("\nRESULTADO: BLOQUEADO\n")
            self.logger.warning(f"Agente bloqueado: {results.get('blocked_agent')}")
            self.logger.warning(f"Errores: {results.get('errors')}")

        self.logger.info("=" * 80)


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo JSON.

    Args:
        config_path: Ruta al archivo de configuración

    Returns:
        Diccionario con la configuración
    """
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    else:
        # Configuración por defecto
        return {
            "save_results": True,
            "output_dir": "output/test_generation",
            "agents": {
                "coverage_analyzer": {
                    "min_coverage": 85,
                    "threshold_low": 70
                },
                "test_planner": {
                    "max_tests_per_run": 5
                },
                "llm_generator": {
                    "llm_provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929"
                },
                "syntax_validator": {
                    "run_mypy": False
                },
                "test_runner": {},
                "coverage_verifier": {
                    "min_coverage_increase": 5.0
                },
                "pr_creator": {}
            }
        }


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Generación automática de tests con LLM"
    )

    parser.add_argument(
        "--project-path",
        type=Path,
        required=True,
        help="Ruta del proyecto a analizar"
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("scripts/ai/config/test_generation.json"),
        help="Ruta al archivo de configuración"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar sin crear PR (solo análisis)"
    )

    args = parser.parse_args()

    # Validar proyecto
    if not args.project_path.exists():
        print(f"ERROR: Directorio no existe: {args.project_path}")
        sys.exit(1)

    # Cargar configuración
    config = load_config(args.config)

    # Dry run: deshabilitar PR creation
    if args.dry_run:
        print("MODO DRY-RUN: No se creará Pull Request")
        config["agents"]["pr_creator"] = {"enabled": False}

    # Crear orquestador
    orchestrator = TestGenerationOrchestrator(config)

    # Ejecutar pipeline
    try:
        results = orchestrator.execute(args.project_path)

        # Exit code según resultado
        status = results.get("status")
        if status == "success":
            sys.exit(0)
        elif status == "blocked":
            sys.exit(2)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nPipeline interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
