#!/usr/bin/env python3
"""
TDD Feature Agent - Implementacion automatizada siguiendo TDD.

Este agente implementa features siguiendo estrictamente la metodologia TDD:
- RED: Escribir tests que fallen
- GREEN: Implementar codigo para que pasen
- REFACTOR: Optimizar sin romper tests

Incluye validacion de constitution, metricas de calidad y reportes completos.

Referencia: TDD Feature Agent con garantias de calidad
"""

from __future__ import annotations

import glob
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.llm_generator import LLMGenerator
from .code_quality_validator import CodeQualityValidator
from .sdlc_base import SDLCAgent, SDLCPhaseResult
from .tdd_constitution import TDDConstitution
from .tdd_execution_logger import TDDExecutionLogger
from .tdd_metrics_dashboard import TDDMetricsDashboard

logger = logging.getLogger(__name__)


class TDDFeatureAgent(SDLCAgent):
    """
    Agente para implementar features siguiendo TDD.

    Ejecuta el ciclo completo RED-GREEN-REFACTOR con validacion
    de constitution y generacion de reportes.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el TDD Feature Agent.

        Args:
            config: Configuracion con:
                - project_root: Path (raiz del proyecto)
                - output_dir: Path (directorio para outputs)
                - minimum_coverage: float (cobertura minima, default 90.0)
                - llm_provider: str (anthropic o openai, default anthropic)
                - model: str (modelo a usar)
        """
        super().__init__(
            name="TDDFeatureAgent",
            phase="implementation",
            config=config or {},
        )

        self.minimum_coverage = self.config.get("minimum_coverage", 90.0)
        self.validator = CodeQualityValidator(self.project_root)

        # Inicializar LLM Generator
        llm_config = {
            "llm_provider": self.config.get("llm_provider", "anthropic"),
            "model": self.config.get("model", "claude-sonnet-4-5-20250929"),
        }
        self.llm_generator = LLMGenerator(config=llm_config)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta implementacion TDD de un feature.

        Args:
            input_data: Datos de entrada con:
                - issue_title: str (titulo del issue)
                - acceptance_criteria: List[str]
                - technical_requirements: List[str]
                - target_module: str (modulo donde implementar)

        Returns:
            Diccionario con:
                - status: str (success, failed)
                - artifacts: List[Path]
                - constitution_result: Dict
                - metrics: Dict
                - execution_log: Path
                - dashboard: Path
        """
        logger.info(f"Starting TDD implementation: {input_data.get('issue_title')}")

        # Inicializar execution logger
        feature_name = self._sanitize_feature_name(input_data.get("issue_title", "feature"))
        execution_logger = TDDExecutionLogger(
            feature_name=feature_name,
            output_dir=self.output_dir / "tdd_logs",
        )

        try:
            # ===== FASE RED: Escribir tests que fallen =====
            logger.info("=== RED PHASE: Writing failing tests ===")
            execution_logger.log_phase("red_phase", {
                "status": "started",
                "timestamp": datetime.now().isoformat(),
            })

            red_result = self._execute_red_phase(input_data, execution_logger)

            execution_logger.log_phase("red_phase", {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "details": red_result,
            })

            # ===== FASE GREEN: Implementar codigo =====
            logger.info("=== GREEN PHASE: Implementing code ===")
            execution_logger.log_phase("green_phase", {
                "status": "started",
                "timestamp": datetime.now().isoformat(),
            })

            green_result = self._execute_green_phase(input_data, execution_logger)

            execution_logger.log_phase("green_phase", {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "details": green_result,
            })

            # ===== FASE REFACTOR: Optimizar codigo =====
            logger.info("=== REFACTOR PHASE: Optimizing code ===")
            execution_logger.log_phase("refactor_phase", {
                "status": "started",
                "timestamp": datetime.now().isoformat(),
            })

            refactor_result = self._execute_refactor_phase(input_data, execution_logger)

            execution_logger.log_phase("refactor_phase", {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "details": refactor_result,
            })

            # ===== VALIDAR CONSTITUTION =====
            logger.info("=== Validating TDD Constitution ===")
            constitution_result = TDDConstitution.validate_tdd_compliance(
                execution_log=execution_logger.log
            )

            # ===== GENERAR REPORTES =====
            logger.info("=== Generating reports ===")
            execution_log_path = execution_logger.finalize(constitution_result)

            dashboard_path = self.output_dir / "tdd_logs" / f"dashboard_{feature_name}.md"
            TDDMetricsDashboard.generate_dashboard(
                execution_log=execution_log_path,
                output_path=dashboard_path,
            )

            # ===== DETERMINAR RESULTADO FINAL =====
            if not constitution_result["compliant"]:
                logger.error(
                    f"TDD Constitution FAILED. Score: {constitution_result['score']}/100"
                )
                return {
                    "status": "failed",
                    "error": "TDD Constitution violated",
                    "constitution_result": constitution_result,
                    "execution_log": str(execution_log_path),
                    "dashboard": str(dashboard_path),
                }

            logger.info(
                f"TDD implementation SUCCESSFUL. Score: {constitution_result['score']}/100"
            )

            return {
                "status": "success",
                "constitution_result": constitution_result,
                "metrics": execution_logger.log["metrics"],
                "execution_log": str(execution_log_path),
                "dashboard": str(dashboard_path),
                "artifacts": [
                    artifact["file_path"]
                    for artifact in execution_logger.log["artifacts"]
                ],
            }

        except Exception as e:
            logger.exception(f"Error during TDD implementation: {e}")

            execution_logger.log_phase("error", {
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"error": str(e)},
            })

            # Generar reporte con error
            constitution_result = {"compliant": False, "score": 0.0, "violations": []}
            execution_log_path = execution_logger.finalize(constitution_result)

            return {
                "status": "failed",
                "error": str(e),
                "execution_log": str(execution_log_path),
            }

    def _execute_red_phase(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> Dict[str, Any]:
        """
        Ejecuta fase RED: genera tests unitarios que deben fallar.

        Args:
            input_data: Datos del feature
            execution_logger: Logger de ejecucion

        Returns:
            Diccionario con resultados de la fase RED
        """
        # TODO: Implementar generacion de tests usando LLM
        # Por ahora, placeholder que simula la generacion

        logger.info("Generating unit tests from acceptance criteria")

        # Placeholder: generar archivos de test
        test_files = self._generate_test_files(input_data, execution_logger)

        # Ejecutar tests (deben fallar en RED phase)
        test_result = self._run_tests(test_files)

        # Log test execution
        execution_logger.log_test_execution("red_phase", test_result)

        return {
            "test_files_generated": len(test_files),
            "test_files": [str(f) for f in test_files],
            "tests_failed": test_result.get("failed", 0),
            "tests_total": test_result.get("total", 0),
        }

    def _execute_green_phase(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> Dict[str, Any]:
        """
        Ejecuta fase GREEN: implementa codigo para que tests pasen.

        Args:
            input_data: Datos del feature
            execution_logger: Logger de ejecucion

        Returns:
            Diccionario con resultados de la fase GREEN
        """
        # TODO: Implementar generacion de codigo usando LLM
        # Por ahora, placeholder

        logger.info("Implementing code to pass tests")

        # Placeholder: generar archivos fuente
        source_files = self._generate_source_files(input_data, execution_logger)

        # Ejecutar tests (deben pasar en GREEN phase)
        test_files = self._get_test_files(input_data)
        test_result = self._run_tests(test_files)

        # Log test execution
        execution_logger.log_test_execution("green_phase", test_result)

        # Ejecutar validaciones de calidad
        quality_metrics = self.validator.run_all_checks(
            test_files=test_files,
            source_files=source_files,
            minimum_coverage=self.minimum_coverage,
        )

        # Log metrics
        execution_logger.log_metrics(quality_metrics)

        return {
            "source_files_generated": len(source_files),
            "source_files": [str(f) for f in source_files],
            "tests_passed": test_result.get("passed", 0),
            "tests_total": test_result.get("total", 0),
            "coverage_percent": quality_metrics.get("coverage", {}).get("percent", 0.0),
        }

    def _execute_refactor_phase(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> Dict[str, Any]:
        """
        Ejecuta fase REFACTOR: optimiza codigo sin romper tests.

        Args:
            input_data: Datos del feature
            execution_logger: Logger de ejecucion

        Returns:
            Diccionario con resultados de la fase REFACTOR
        """
        logger.info("Refactoring code using LLM and auto-fix")

        source_files = self._get_source_files(input_data)
        test_files = self._get_test_files(input_data)

        refactorings_applied = []

        # Paso 1: Auto-fix linting issues
        logger.info("Step 1: Auto-fixing linting issues")
        self._auto_fix_linting(source_files)
        refactorings_applied.append("Auto-fixed linting issues with ruff")

        # Ejecutar tests después de auto-fix
        test_result = self._run_tests(test_files)
        if test_result.get("failed", 0) > 0:
            logger.error("Tests failed after auto-fix, reverting changes")
            return {
                "refactoring_applied": False,
                "error": "Auto-fix broke tests",
                "tests_still_passing": False,
                "tests_passed": test_result.get("passed", 0),
                "tests_total": test_result.get("total", 0),
            }

        # Paso 2: Analizar código con LLM para sugerir refactorings
        logger.info("Step 2: Analyzing code with LLM for refactoring opportunities")

        for source_file in source_files:
            try:
                with open(source_file) as f:
                    source_code = f.read()

                # Construir prompt para análisis de refactoring
                refactor_prompt = self._build_refactor_prompt(source_code)

                # Obtener sugerencias del LLM
                refactored_code = self.llm_generator._call_llm(refactor_prompt)

                if refactored_code and refactored_code != source_code:
                    # Guardar código original como backup
                    backup_path = source_file.with_suffix(".py.backup")
                    with open(backup_path, "w") as f:
                        f.write(source_code)

                    # Aplicar refactoring
                    with open(source_file, "w") as f:
                        f.write(refactored_code)

                    logger.info(f"Applied LLM refactoring to {source_file}")
                    refactorings_applied.append(f"LLM refactoring: {source_file.name}")

                    # Log al execution logger
                    execution_logger.log_generated_file(
                        str(source_file.relative_to(self.project_root)),
                        refactored_code
                    )

            except Exception as e:
                logger.warning(f"Error refactoring {source_file}: {e}")
                continue

        # Paso 3: Ejecutar tests para validar refactorings
        logger.info("Step 3: Validating refactorings with tests")
        test_result = self._run_tests(test_files)

        # Log test execution
        execution_logger.log_test_execution("refactor_phase", test_result)

        # Si los tests fallan, revertir cambios
        tests_passing = test_result.get("passed", 0) == test_result.get("total", 0)

        if not tests_passing:
            logger.error("Refactorings broke tests, reverting changes")
            # Restaurar backups
            for source_file in source_files:
                backup_path = source_file.with_suffix(".py.backup")
                if backup_path.exists():
                    with open(backup_path) as f:
                        original_code = f.read()
                    with open(source_file, "w") as f:
                        f.write(original_code)
                    backup_path.unlink()

            return {
                "refactoring_applied": False,
                "error": "Refactorings broke tests, reverted",
                "tests_still_passing": False,
                "tests_passed": test_result.get("passed", 0),
                "tests_total": test_result.get("total", 0),
                "refactorings_attempted": refactorings_applied,
            }

        # Limpiar backups si todo salió bien
        for source_file in source_files:
            backup_path = source_file.with_suffix(".py.backup")
            if backup_path.exists():
                backup_path.unlink()

        # Paso 4: Ejecutar validaciones de calidad
        logger.info("Step 4: Running quality checks")
        quality_metrics = self.validator.run_all_checks(
            test_files=test_files,
            source_files=source_files,
            minimum_coverage=self.minimum_coverage,
        )

        # Actualizar metrics
        execution_logger.log_metrics(quality_metrics)

        return {
            "refactoring_applied": True,
            "refactorings_applied": refactorings_applied,
            "tests_still_passing": True,
            "tests_passed": test_result.get("passed", 0),
            "tests_total": test_result.get("total", 0),
            "quality_metrics": quality_metrics,
        }

    def _generate_test_files(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> List[Path]:
        """
        Genera archivos de test usando LLM.

        Args:
            input_data: Datos con acceptance_criteria, technical_requirements, target_module
            execution_logger: Logger de ejecucion

        Returns:
            Lista de Paths de archivos de test generados
        """
        logger.info("Generating test files using LLM")

        target_module = input_data.get("target_module", "app")
        acceptance_criteria = input_data.get("acceptance_criteria", [])
        technical_requirements = input_data.get("technical_requirements", [])

        # Determinar archivos fuente a testear basados en target_module
        source_files = self._discover_source_files_for_module(target_module)

        if not source_files:
            logger.warning(f"No source files found for module: {target_module}")
            return []

        # Crear test plans para cada archivo fuente
        test_plans = []
        for source_file in source_files:
            test_cases = self._create_test_cases_from_criteria(
                source_file,
                acceptance_criteria,
                technical_requirements
            )

            test_file_path = self._determine_test_file_path(source_file)

            test_plans.append({
                "source_file": str(source_file.relative_to(self.project_root)),
                "test_file": str(test_file_path.relative_to(self.project_root)),
                "test_cases": test_cases,
            })

        # Generar tests con LLM
        try:
            llm_input = {
                "test_plans": test_plans,
                "project_path": str(self.project_root),
            }

            result = self.llm_generator.run(llm_input)
            generated_tests = result.get("generated_tests", [])

            # Escribir archivos generados
            created_files = []
            for test in generated_tests:
                test_file_path = self.project_root / test["test_file"]
                test_file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(test_file_path, "w") as f:
                    f.write(test["generated_code"])

                logger.info(f"Generated test file: {test_file_path}")
                created_files.append(test_file_path)

                # Log a execution logger
                execution_logger.log_generated_file(
                    str(test_file_path.relative_to(self.project_root)),
                    test["generated_code"]
                )

            return created_files

        except Exception as e:
            logger.error(f"Error generating test files: {e}")
            return []

    def _generate_source_files(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> List[Path]:
        """
        Genera archivos fuente usando LLM para hacer pasar los tests.

        Args:
            input_data: Datos con acceptance_criteria, technical_requirements, target_module
            execution_logger: Logger de ejecucion

        Returns:
            Lista de Paths de archivos fuente generados
        """
        logger.info("Generating source files using LLM")

        target_module = input_data.get("target_module", "app")
        acceptance_criteria = input_data.get("acceptance_criteria", [])
        technical_requirements = input_data.get("technical_requirements", [])

        # Obtener archivos de test generados en RED phase
        test_files = self._get_test_files(input_data)

        if not test_files:
            logger.warning("No test files found to implement against")
            return []

        # Leer contenido de tests para entender qué implementar
        test_contents = {}
        for test_file in test_files:
            try:
                with open(test_file) as f:
                    test_contents[str(test_file)] = f.read()
            except Exception as e:
                logger.error(f"Error reading test file {test_file}: {e}")

        # Construir prompt para LLM
        prompt = self._build_source_generation_prompt(
            acceptance_criteria=acceptance_criteria,
            technical_requirements=technical_requirements,
            test_contents=test_contents,
            target_module=target_module
        )

        # Generar código con LLM usando llamada directa
        try:
            # Usar el método interno del LLMGenerator para generar código
            generated_code = self.llm_generator._call_llm(prompt)

            if not generated_code:
                logger.error("LLM returned empty response")
                return []

            # Determinar ruta del archivo fuente
            source_file_path = self._determine_source_file_path(target_module)
            source_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Escribir archivo fuente
            with open(source_file_path, "w") as f:
                f.write(generated_code)

            logger.info(f"Generated source file: {source_file_path}")

            # Log a execution logger
            execution_logger.log_generated_file(
                str(source_file_path.relative_to(self.project_root)),
                generated_code
            )

            return [source_file_path]

        except Exception as e:
            logger.error(f"Error generating source files: {e}")
            return []

    def _get_test_files(self, input_data: Dict[str, Any]) -> List[Path]:
        """
        Obtiene lista de archivos de test del feature.

        Args:
            input_data: Datos con target_module

        Returns:
            Lista de Paths de archivos de test encontrados
        """
        target_module = input_data.get("target_module", "app")

        # Buscar archivos de test usando patrones comunes
        test_patterns = [
            f"**/tests/test_{target_module}*.py",
            f"**/test_{target_module}*.py",
            f"**/{target_module}/tests/test_*.py",
            f"**/{target_module}/test_*.py",
        ]

        test_files = []
        for pattern in test_patterns:
            pattern_path = str(self.project_root / pattern)
            matches = glob.glob(pattern_path, recursive=True)
            test_files.extend([Path(f) for f in matches if Path(f).is_file()])

        # Remover duplicados
        test_files = list(set(test_files))

        logger.info(f"Found {len(test_files)} test files for module {target_module}")
        return test_files

    def _get_source_files(self, input_data: Dict[str, Any]) -> List[Path]:
        """
        Obtiene lista de archivos fuente del feature.

        Args:
            input_data: Datos con target_module

        Returns:
            Lista de Paths de archivos fuente encontrados
        """
        target_module = input_data.get("target_module", "app")

        # Buscar archivos fuente usando patrones comunes
        source_patterns = [
            f"**/{target_module}.py",
            f"**/{target_module}/**/*.py",
            f"**/apps/{target_module}/**/*.py",
            f"**/src/{target_module}/**/*.py",
        ]

        source_files = []
        for pattern in source_patterns:
            pattern_path = str(self.project_root / pattern)
            matches = glob.glob(pattern_path, recursive=True)
            for f in matches:
                file_path = Path(f)
                # Excluir archivos de test y __pycache__
                if (file_path.is_file() and
                    not file_path.name.startswith("test_") and
                    "__pycache__" not in str(file_path) and
                    not file_path.name.startswith("__")):
                    source_files.append(file_path)

        # Remover duplicados
        source_files = list(set(source_files))

        logger.info(f"Found {len(source_files)} source files for module {target_module}")
        return source_files

    def _run_tests(self, test_files: List[Path]) -> Dict[str, Any]:
        """
        Ejecuta tests con pytest.

        Args:
            test_files: Lista de archivos de test

        Returns:
            Diccionario con resultados:
                - total: int
                - passed: int
                - failed: int
                - skipped: int
                - duration_seconds: float
                - details: str
        """
        if not test_files:
            logger.warning("No test files to run")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_seconds": 0.0,
                "details": "No tests to run",
            }

        try:
            # Ejecutar pytest
            cmd = ["pytest", "-v", "--tb=short"]
            for test_file in test_files:
                cmd.append(str(test_file))

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parsear output (simplificado)
            # En implementacion real, usar pytest-json-report para JSON output
            output = result.stdout

            # Placeholder: parsear summary line
            # Formato: "=== 5 passed, 2 failed in 1.23s ==="
            import re
            match = re.search(r"(\d+) passed", output)
            passed = int(match.group(1)) if match else 0

            match = re.search(r"(\d+) failed", output)
            failed = int(match.group(1)) if match else 0

            match = re.search(r"(\d+) skipped", output)
            skipped = int(match.group(1)) if match else 0

            match = re.search(r"in ([\d.]+)s", output)
            duration = float(match.group(1)) if match else 0.0

            total = passed + failed + skipped

            return {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "duration_seconds": duration,
                "details": output,
            }

        except subprocess.TimeoutExpired:
            logger.error("Test execution timeout")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_seconds": 0.0,
                "details": "Timeout",
                "error": "Timeout",
            }
        except Exception as e:
            logger.exception(f"Error running tests: {e}")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_seconds": 0.0,
                "details": str(e),
                "error": str(e),
            }

    def _auto_fix_linting(self, source_files: List[Path]) -> None:
        """
        Auto-fix linting issues con ruff.

        Args:
            source_files: Lista de archivos fuente
        """
        if not source_files:
            return

        try:
            # Ejecutar ruff --fix
            cmd = ["ruff", "check", "--fix"]
            for source_file in source_files:
                cmd.append(str(source_file))

            subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                timeout=60,
            )

            logger.info("Auto-fixed linting issues with ruff")

        except FileNotFoundError:
            logger.warning("ruff not installed, skipping auto-fix")
        except Exception as e:
            logger.warning(f"Error auto-fixing linting: {e}")

    @staticmethod
    def _sanitize_feature_name(name: str) -> str:
        """
        Sanitiza nombre de feature para usar como filename.

        Args:
            name: Nombre original

        Returns:
            Nombre sanitizado
        """
        # Remover caracteres especiales
        import re
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        sanitized = sanitized.lower().strip('_')

        # Limitar longitud
        if len(sanitized) > 50:
            sanitized = sanitized[:50]

        return sanitized or "feature"

    def _discover_source_files_for_module(self, target_module: str) -> List[Path]:
        """
        Descubre archivos fuente para un modulo dado.

        Args:
            target_module: Nombre del modulo

        Returns:
            Lista de archivos fuente encontrados
        """
        # Usar patrones comunes de estructura de proyectos
        patterns = [
            f"**/{target_module}.py",
            f"**/{target_module}/**/*.py",
            f"**/apps/{target_module}/**/*.py",
            f"**/src/{target_module}/**/*.py",
        ]

        source_files = []
        for pattern in patterns:
            pattern_path = str(self.project_root / pattern)
            matches = glob.glob(pattern_path, recursive=True)
            for f in matches:
                file_path = Path(f)
                if (file_path.is_file() and
                    not file_path.name.startswith("test_") and
                    "__pycache__" not in str(file_path)):
                    source_files.append(file_path)

        # Si no se encuentran archivos, retornar lista vacia
        # El llamador decidirá qué hacer
        return list(set(source_files))[:5]  # Limitar a 5 archivos

    def _create_test_cases_from_criteria(
        self,
        source_file: Path,
        acceptance_criteria: List[str],
        technical_requirements: List[str]
    ) -> List[Dict[str, str]]:
        """
        Crea casos de test basados en criterios de aceptacion.

        Args:
            source_file: Archivo fuente a testear
            acceptance_criteria: Lista de criterios de aceptacion
            technical_requirements: Lista de requisitos tecnicos

        Returns:
            Lista de test cases con nombre y descripcion
        """
        test_cases = []

        # Generar casos de test desde acceptance criteria
        for i, criterion in enumerate(acceptance_criteria, 1):
            test_cases.append({
                "name": f"test_acceptance_criterion_{i}",
                "description": criterion
            })

        # Agregar test cases básicos
        test_cases.extend([
            {
                "name": "test_happy_path",
                "description": "Test del flujo principal exitoso"
            },
            {
                "name": "test_error_handling",
                "description": "Test del manejo de errores y excepciones"
            },
            {
                "name": "test_edge_cases",
                "description": "Test de casos edge y limites"
            }
        ])

        return test_cases

    def _determine_test_file_path(self, source_file: Path) -> Path:
        """
        Determina la ruta del archivo de test para un archivo fuente.

        Args:
            source_file: Path del archivo fuente

        Returns:
            Path del archivo de test correspondiente
        """
        # Convertir path relativo
        try:
            relative_path = source_file.relative_to(self.project_root)
        except ValueError:
            relative_path = source_file

        # Determinar directorio de tests
        parts = list(relative_path.parts)

        # Si está en apps/, poner tests en apps/module/tests/
        if "apps" in parts:
            app_index = parts.index("apps")
            if app_index + 1 < len(parts):
                module_name = parts[app_index + 1]
                test_dir = self.project_root / "apps" / module_name / "tests"
                test_file = test_dir / f"test_{source_file.stem}.py"
                return test_file

        # Default: tests/ en la raiz
        test_dir = self.project_root / "tests"
        test_file = test_dir / f"test_{source_file.stem}.py"
        return test_file

    def _build_source_generation_prompt(
        self,
        acceptance_criteria: List[str],
        technical_requirements: List[str],
        test_contents: Dict[str, str],
        target_module: str
    ) -> str:
        """
        Construye prompt para generar codigo fuente.

        Args:
            acceptance_criteria: Criterios de aceptacion
            technical_requirements: Requisitos tecnicos
            test_contents: Diccionario test_file -> contenido
            target_module: Modulo objetivo

        Returns:
            Prompt formateado para el LLM
        """
        # Formatear acceptance criteria
        criteria_text = "\n".join([
            f"{i}. {criterion}"
            for i, criterion in enumerate(acceptance_criteria, 1)
        ])

        # Formatear technical requirements
        requirements_text = "\n".join([
            f"- {req}"
            for req in technical_requirements
        ])

        # Formatear test contents
        tests_text = ""
        for test_file, content in test_contents.items():
            tests_text += f"\n\nTest file: {test_file}\n```python\n{content}\n```"

        prompt = f"""Eres un experto desarrollador Python siguiendo TDD estricto.

Tu tarea es implementar el codigo fuente que haga pasar TODOS los tests proporcionados.

CRITERIOS DE ACEPTACION:
{criteria_text}

REQUISITOS TECNICOS:
{requirements_text}

TESTS QUE DEBEN PASAR:
{tests_text}

INSTRUCCIONES:

1. Implementa el codigo MINIMO necesario para pasar los tests
2. Sigue principios SOLID y clean code
3. Usa type hints de Python
4. Agrega docstrings a funciones y clases
5. Maneja errores apropiadamente
6. NO implementes nada que no esté cubierto por los tests

FORMATO DE RESPUESTA:

Retorna SOLO el codigo Python, sin explicaciones adicionales.
El codigo debe ser un modulo Python completo y ejecutable.

Codigo:"""

        return prompt

    def _determine_source_file_path(self, target_module: str) -> Path:
        """
        Determina la ruta del archivo fuente a crear.

        Args:
            target_module: Nombre del modulo

        Returns:
            Path del archivo fuente
        """
        # Buscar estructura del proyecto
        # Prioridad: apps/, src/, raiz
        apps_dir = self.project_root / "apps" / target_module
        src_dir = self.project_root / "src" / target_module

        if apps_dir.exists():
            return apps_dir / f"{target_module}.py"
        elif src_dir.exists():
            return src_dir / f"{target_module}.py"
        else:
            # Crear en src/ por defecto
            return self.project_root / "src" / target_module / f"{target_module}.py"

    def _build_refactor_prompt(self, source_code: str) -> str:
        """
        Construye prompt para refactoring de codigo.

        Args:
            source_code: Codigo fuente a refactorizar

        Returns:
            Prompt formateado para el LLM
        """
        prompt = f"""Eres un experto en refactoring de codigo Python.

Tu tarea es refactorizar el siguiente codigo para mejorar su calidad sin cambiar su comportamiento.

CODIGO ACTUAL:
```python
{source_code}
```

OBJETIVOS DE REFACTORING:

1. Mejorar legibilidad y mantenibilidad
2. Eliminar codigo duplicado (DRY)
3. Aplicar principios SOLID donde sea apropiado
4. Extraer funciones auxiliares si es necesario
5. Mejorar nombres de variables y funciones
6. Simplificar logica compleja
7. Mejorar type hints y docstrings
8. NO cambiar el comportamiento externo del codigo

RESTRICCIONES CRITICAS:

- NO agregues nuevas funcionalidades
- NO cambies firmas de funciones publicas
- NO cambies el comportamiento observable
- MANTÉN todos los tests pasando
- Solo refactoriza, no agregues features

FORMATO DE RESPUESTA:

Retorna SOLO el codigo refactorizado, sin explicaciones adicionales.
El codigo debe ser Python valido y ejecutable.

Codigo refactorizado:"""

        return prompt
