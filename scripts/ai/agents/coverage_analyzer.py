"""
CoverageAnalyzer Agent

Responsabilidad: Analizar cobertura de tests e identificar gaps.
Input: Directorio del proyecto
Output: Lista de archivos con baja cobertura y funciones sin tests
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class CoverageAnalyzer(Agent):
    """
    Agente especializado en análisis de cobertura de tests.

    Identifica:
    - Archivos sin tests
    - Funciones sin cobertura
    - Porcentaje de cobertura actual
    - Priorización de targets
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="CoverageAnalyzer", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan los paths necesarios."""
        errors = []

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")
        else:
            project_path = Path(input_data["project_path"])
            if not project_path.exists():
                errors.append(f"Directorio no existe: {project_path}")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el análisis de cobertura."""
        project_path = Path(input_data["project_path"])
        min_coverage = self.get_config("min_coverage", 85)
        threshold_low = self.get_config("threshold_low", 70)

        self.logger.info(f"Analizando cobertura en {project_path}")

        # Ejecutar pytest con coverage
        coverage_data = self._run_coverage(project_path)

        # Analizar resultados
        gaps = self._identify_gaps(coverage_data, threshold_low)

        # Priorizar targets
        prioritized = self._prioritize_targets(gaps)

        current_coverage = coverage_data.get("total_coverage", 0)

        return {
            "current_coverage": current_coverage,
            "min_coverage": min_coverage,
            "coverage_gap": max(0, min_coverage - current_coverage),
            "low_coverage_files": gaps,
            "prioritized_targets": prioritized,
            "coverage_report_path": str(project_path / "coverage.json"),
            "total_files_analyzed": len(coverage_data.get("files", [])),
            "files_below_threshold": len(gaps)
        }

    def _run_coverage(self, project_path: Path) -> Dict[str, Any]:
        """
        Ejecuta pytest con coverage y retorna los resultados.

        Args:
            project_path: Directorio del proyecto

        Returns:
            Diccionario con datos de cobertura
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

            self.logger.info(f"Coverage command exit code: {result.returncode}")

            # Leer el archivo JSON generado
            coverage_json = project_path / "coverage.json"
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)
                return data
            else:
                self.logger.warning("No se generó coverage.json")
                return {"files": {}, "totals": {"percent_covered": 0}}

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout ejecutando coverage")
            return {"files": {}, "totals": {"percent_covered": 0}}
        except Exception as e:
            self.logger.error(f"Error ejecutando coverage: {e}")
            return {"files": {}, "totals": {"percent_covered": 0}}

    def _identify_gaps(
        self,
        coverage_data: Dict[str, Any],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Identifica archivos con baja cobertura.

        Args:
            coverage_data: Datos de coverage.py
            threshold: Umbral mínimo de cobertura

        Returns:
            Lista de archivos con baja cobertura
        """
        gaps = []
        files = coverage_data.get("files", {})

        for filepath, file_data in files.items():
            summary = file_data.get("summary", {})
            percent_covered = summary.get("percent_covered", 0)

            if percent_covered < threshold:
                # Identificar líneas sin cobertura
                missing_lines = file_data.get("missing_lines", [])
                executed_lines = file_data.get("executed_lines", [])

                gaps.append({
                    "file": filepath,
                    "current_coverage": percent_covered,
                    "missing_lines": missing_lines,
                    "executed_lines": len(executed_lines),
                    "total_lines": summary.get("num_statements", 0),
                    "priority_score": self._calculate_priority(
                        percent_covered,
                        summary.get("num_statements", 0)
                    )
                })

        return gaps

    def _calculate_priority(self, coverage: float, num_statements: int) -> float:
        """
        Calcula score de prioridad para un archivo.

        Criterios:
        - Menor cobertura = mayor prioridad
        - Más líneas = mayor prioridad
        - Balancear ambos factores

        Args:
            coverage: Porcentaje de cobertura actual
            num_statements: Número de statements en el archivo

        Returns:
            Score de prioridad (mayor = más prioritario)
        """
        # Normalizar coverage (0-100 → 100-0)
        coverage_score = 100 - coverage

        # Normalizar número de statements (logarítmico)
        import math
        size_score = math.log(max(num_statements, 1) + 1) * 10

        # Combinar (70% coverage, 30% size)
        priority = (coverage_score * 0.7) + (size_score * 0.3)

        return round(priority, 2)

    def _prioritize_targets(
        self,
        gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ordena targets por prioridad.

        Args:
            gaps: Lista de archivos con gaps

        Returns:
            Lista ordenada por prioridad (descendente)
        """
        sorted_gaps = sorted(
            gaps,
            key=lambda x: x["priority_score"],
            reverse=True
        )

        # Agregar ranking
        for i, gap in enumerate(sorted_gaps, 1):
            gap["rank"] = i

        return sorted_gaps

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que el análisis sea coherente."""
        errors = []

        current_coverage = output_data.get("current_coverage", 0)
        if current_coverage < 0 or current_coverage > 100:
            errors.append(f"Cobertura inválida: {current_coverage}%")

        prioritized = output_data.get("prioritized_targets", [])
        if not prioritized:
            # WARNING, no error - puede ser que todo tenga buena cobertura
            self.logger.warning("No se encontraron gaps de cobertura")

        return errors
