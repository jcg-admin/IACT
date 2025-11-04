"""
CoverageVerifier Agent

Responsabilidad: Verificar que los tests aumenten la cobertura.
Input: Tests que pasaron
Output: Verificación de incremento de cobertura
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class CoverageVerifier(Agent):
    """
    Agente especializado en verificación de cobertura.

    Verifica que:
    - La cobertura aumentó
    - El incremento es >= objetivo (5% por defecto)
    - No hay regresiones
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="CoverageVerifier", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan datos previos de cobertura."""
        errors = []

        if "current_coverage" not in input_data:
            errors.append("Falta 'current_coverage' en input")

        if "test_results" not in input_data:
            errors.append("Falta 'test_results' en input")

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la verificación de cobertura."""
        current_coverage = input_data["current_coverage"]
        test_results = input_data["test_results"]
        project_path = Path(input_data["project_path"])
        min_increase = self.get_config("min_coverage_increase", 5.0)

        self.logger.info(f"Verificando incremento de cobertura desde {current_coverage}%")

        # Escribir los tests nuevos al proyecto
        written_files = self._write_tests_to_project(
            test_results,
            project_path,
            input_data.get("validated_tests", [])
        )

        # Ejecutar coverage nuevamente
        new_coverage_data = self._run_coverage(project_path)
        new_coverage = new_coverage_data.get("total_coverage", 0)

        # Calcular incremento
        coverage_increase = new_coverage - current_coverage

        # Análisis detallado por archivo
        file_improvements = self._analyze_file_improvements(
            input_data.get("prioritized_targets", []),
            new_coverage_data
        )

        # Limpiar archivos temporales
        self._cleanup_tests(written_files)

        return {
            "previous_coverage": current_coverage,
            "new_coverage": new_coverage,
            "coverage_increase": coverage_increase,
            "min_increase_required": min_increase,
            "meets_requirement": coverage_increase >= min_increase,
            "file_improvements": file_improvements,
            "total_files_improved": len([
                f for f in file_improvements
                if f["improvement"] > 0
            ])
        }

    def _write_tests_to_project(
        self,
        test_results: List[Dict[str, Any]],
        project_path: Path,
        validated_tests: List[Dict[str, Any]]
    ) -> List[Path]:
        """
        Escribe los tests en el proyecto temporalmente.

        Args:
            test_results: Tests que pasaron
            project_path: Ruta del proyecto
            validated_tests: Tests validados con código

        Returns:
            Lista de archivos escritos
        """
        written_files = []

        # Mapear test_file a código
        test_code_map = {
            t["test_file"]: t["validated_code"]
            for t in validated_tests
        }

        for result in test_results:
            test_file = result["test_file"]

            if test_file not in test_code_map:
                self.logger.warning(f"No se encontró código para {test_file}")
                continue

            code = test_code_map[test_file]

            # Escribir en el proyecto
            full_path = project_path / test_file
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(code)

            written_files.append(full_path)
            self.logger.info(f"Escrito {full_path}")

        return written_files

    def _run_coverage(self, project_path: Path) -> Dict[str, Any]:
        """
        Ejecuta pytest con coverage.

        Args:
            project_path: Ruta del proyecto

        Returns:
            Datos de cobertura
        """
        try:
            cmd = [
                "pytest",
                "--cov=.",
                "--cov-report=json",
                "--cov-report=term-missing",
                "-q"
            ]

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            self.logger.info(f"Coverage exit code: {result.returncode}")

            # Leer coverage.json
            coverage_json = project_path / "coverage.json"
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)

                total_coverage = data.get("totals", {}).get("percent_covered", 0)

                return {
                    "total_coverage": total_coverage,
                    "files": data.get("files", {})
                }
            else:
                self.logger.warning("No se generó coverage.json")
                return {"total_coverage": 0, "files": {}}

        except Exception as e:
            self.logger.error(f"Error ejecutando coverage: {e}")
            return {"total_coverage": 0, "files": {}}

    def _analyze_file_improvements(
        self,
        prioritized_targets: List[Dict[str, Any]],
        new_coverage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analiza mejoras por archivo.

        Args:
            prioritized_targets: Targets originales con baja cobertura
            new_coverage_data: Nueva data de cobertura

        Returns:
            Lista con mejoras por archivo
        """
        improvements = []
        new_files = new_coverage_data.get("files", {})

        for target in prioritized_targets:
            filepath = target["file"]
            old_coverage = target["current_coverage"]

            # Buscar en nueva cobertura
            if filepath in new_files:
                file_data = new_files[filepath]
                new_coverage = file_data.get("summary", {}).get("percent_covered", 0)
            else:
                new_coverage = old_coverage

            improvement = new_coverage - old_coverage

            improvements.append({
                "file": filepath,
                "old_coverage": old_coverage,
                "new_coverage": new_coverage,
                "improvement": improvement,
                "status": "improved" if improvement > 0 else "unchanged"
            })

        return improvements

    def _cleanup_tests(self, written_files: List[Path]) -> None:
        """
        Limpia los archivos de tests escritos.

        Args:
            written_files: Lista de archivos a eliminar
        """
        for filepath in written_files:
            try:
                filepath.unlink()
                self.logger.info(f"Eliminado {filepath}")
            except Exception as e:
                self.logger.warning(f"No se pudo eliminar {filepath}: {e}")

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que la cobertura haya aumentado."""
        errors = []

        coverage_increase = output_data.get("coverage_increase", 0)
        min_increase = output_data.get("min_increase_required", 5.0)
        meets_requirement = output_data.get("meets_requirement", False)

        if not meets_requirement:
            errors.append(
                f"Incremento de cobertura insuficiente: "
                f"{coverage_increase:.2f}% (requerido: {min_increase}%)"
            )

        # Verificar que no haya regresión
        if coverage_increase < 0:
            errors.append(
                f"REGRESIÓN: La cobertura disminuyó {abs(coverage_increase):.2f}%"
            )

        # Verificar que al menos algunos archivos mejoraron
        total_improved = output_data.get("total_files_improved", 0)
        if total_improved == 0:
            errors.append("Ningún archivo mejoró su cobertura")

        return errors
