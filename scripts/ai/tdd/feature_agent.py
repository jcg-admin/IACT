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

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        """
        super().__init__(
            name="TDDFeatureAgent",
            phase="implementation",
            config=config or {},
        )

        self.minimum_coverage = self.config.get("minimum_coverage", 90.0)
        self.validator = CodeQualityValidator(self.project_root)

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
        # TODO: Implementar refactoring usando LLM
        # Por ahora, placeholder que simula auto-fix de linting

        logger.info("Refactoring code (auto-fix linting issues)")

        # Auto-fix linting issues
        source_files = self._get_source_files(input_data)
        self._auto_fix_linting(source_files)

        # Ejecutar tests nuevamente (deben seguir pasando)
        test_files = self._get_test_files(input_data)
        test_result = self._run_tests(test_files)

        # Log test execution
        execution_logger.log_test_execution("refactor_phase", test_result)

        # Ejecutar validaciones de calidad nuevamente
        quality_metrics = self.validator.run_all_checks(
            test_files=test_files,
            source_files=source_files,
            minimum_coverage=self.minimum_coverage,
        )

        # Actualizar metrics
        execution_logger.log_metrics(quality_metrics)

        return {
            "refactoring_applied": True,
            "tests_still_passing": test_result.get("passed", 0) == test_result.get("total", 0),
            "tests_passed": test_result.get("passed", 0),
            "tests_total": test_result.get("total", 0),
        }

    def _generate_test_files(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> List[Path]:
        """
        Genera archivos de test (placeholder).

        TODO: Implementar con LLM para generar tests reales.
        """
        logger.warning("_generate_test_files is a placeholder - implement with LLM")

        # Por ahora retornar lista vacia
        # En implementacion real, aqui se generarian los tests
        return []

    def _generate_source_files(
        self,
        input_data: Dict[str, Any],
        execution_logger: TDDExecutionLogger,
    ) -> List[Path]:
        """
        Genera archivos fuente (placeholder).

        TODO: Implementar con LLM para generar codigo real.
        """
        logger.warning("_generate_source_files is a placeholder - implement with LLM")

        # Por ahora retornar lista vacia
        return []

    def _get_test_files(self, input_data: Dict[str, Any]) -> List[Path]:
        """Obtiene lista de archivos de test del feature."""
        # TODO: Implementar busqueda real de test files
        return []

    def _get_source_files(self, input_data: Dict[str, Any]) -> List[Path]:
        """Obtiene lista de archivos fuente del feature."""
        # TODO: Implementar busqueda real de source files
        return []

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
