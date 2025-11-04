"""
TestRunner Agent

Responsabilidad: Ejecutar los tests generados y verificar que pasen.
Input: Tests validados
Output: Resultados de ejecución de tests
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class TestRunner(Agent):
    """
    Agente especializado en ejecución de tests.

    Ejecuta los tests generados en un entorno aislado y verifica:
    - Tests pasan correctamente
    - No hay errores inesperados
    - Performance aceptable
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="TestRunner", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan tests validados."""
        errors = []

        if "validated_tests" not in input_data:
            errors.append("Falta 'validated_tests' en input")

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta los tests generados."""
        validated_tests = input_data["validated_tests"]
        project_path = Path(input_data["project_path"])

        self.logger.info(f"Ejecutando {len(validated_tests)} archivos de tests")

        test_results = []
        execution_errors = []

        for test in validated_tests:
            test_file = test["test_file"]
            code = test["validated_code"]

            self.logger.info(f"Ejecutando tests de {test_file}")

            # Escribir archivo temporal
            temp_test_file = self._write_temp_test(code, test_file)

            # Ejecutar pytest
            success, output, metrics = self._run_pytest(
                temp_test_file,
                project_path
            )

            if success:
                test_results.append({
                    "test_file": test_file,
                    "status": "passed",
                    "output": output,
                    "metrics": metrics
                })
            else:
                execution_errors.append({
                    "test_file": test_file,
                    "status": "failed",
                    "output": output,
                    "metrics": metrics
                })

            # Limpiar archivo temporal
            temp_test_file.unlink(missing_ok=True)

        return {
            "test_results": test_results,
            "execution_errors": execution_errors,
            "total_passed": len(test_results),
            "total_failed": len(execution_errors),
            "success_rate": (
                len(test_results) / len(validated_tests) * 100
                if validated_tests else 0
            )
        }

    def _write_temp_test(self, code: str, test_file: str) -> Path:
        """
        Escribe el código en un archivo temporal.

        Args:
            code: Código del test
            test_file: Nombre del archivo de test

        Returns:
            Path del archivo temporal
        """
        temp_dir = Path(tempfile.gettempdir()) / "ai_test_runner"
        temp_dir.mkdir(exist_ok=True)

        # Usar nombre descriptivo
        filename = Path(test_file).name
        temp_path = temp_dir / filename

        with open(temp_path, 'w') as f:
            f.write(code)

        return temp_path

    def _run_pytest(
        self,
        test_file: Path,
        project_path: Path
    ) -> tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta pytest en el archivo de tests.

        Args:
            test_file: Ruta del archivo de test
            project_path: Ruta del proyecto (para PYTHONPATH)

        Returns:
            Tupla (éxito, output, métricas)
        """
        try:
            cmd = [
                "pytest",
                str(test_file),
                "-v",
                "--tb=short",
                "--no-header",
                "-q"
            ]

            # Configurar PYTHONPATH para imports
            import os
            env = os.environ.copy()
            pythonpath = str(project_path)
            if "PYTHONPATH" in env:
                pythonpath = f"{pythonpath}:{env['PYTHONPATH']}"
            env["PYTHONPATH"] = pythonpath

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutos máximo
                env=env
            )

            output = result.stdout + result.stderr

            # Parsear métricas
            metrics = self._parse_pytest_output(output)

            success = result.returncode == 0

            return success, output, metrics

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout ejecutando {test_file}")
            return False, "TIMEOUT: Test tardó más de 2 minutos", {}
        except Exception as e:
            self.logger.error(f"Error ejecutando {test_file}: {e}")
            return False, f"ERROR: {str(e)}", {}

    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """
        Parsea el output de pytest para extraer métricas.

        Args:
            output: Output completo de pytest

        Returns:
            Diccionario con métricas
        """
        metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration_seconds": 0.0
        }

        lines = output.split('\n')

        for line in lines:
            # Buscar línea de resumen: "5 passed in 0.23s"
            if " passed" in line or " failed" in line:
                parts = line.split()

                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        try:
                            metrics["passed"] = int(parts[i-1])
                        except:
                            pass

                    if part == "failed" and i > 0:
                        try:
                            metrics["failed"] = int(parts[i-1])
                        except:
                            pass

                    if part == "skipped" and i > 0:
                        try:
                            metrics["skipped"] = int(parts[i-1])
                        except:
                            pass

                    if part == "in" and i < len(parts) - 1:
                        try:
                            duration_str = parts[i+1].rstrip('s')
                            metrics["duration_seconds"] = float(duration_str)
                        except:
                            pass

        metrics["total_tests"] = (
            metrics["passed"] +
            metrics["failed"] +
            metrics["skipped"]
        )

        return metrics

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que los tests ejecuten correctamente."""
        errors = []

        test_results = output_data.get("test_results", [])
        execution_errors = output_data.get("execution_errors", [])

        if not test_results:
            errors.append("Ningún test pasó correctamente")

        # Si más del 30% falló, hay un problema con la generación
        total = len(test_results) + len(execution_errors)
        if total > 0:
            failure_rate = len(execution_errors) / total
            if failure_rate > 0.3:
                errors.append(
                    f"Tasa de fallo muy alta: {failure_rate:.1%} "
                    f"({len(execution_errors)}/{total})"
                )

        # Validar que no haya tests extremadamente lentos
        for result in test_results:
            duration = result.get("metrics", {}).get("duration_seconds", 0)
            if duration > 60:  # 1 minuto
                errors.append(
                    f"Test muy lento: {result['test_file']} "
                    f"({duration:.1f}s)"
                )

        return errors
