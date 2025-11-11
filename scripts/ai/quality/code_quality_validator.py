#!/usr/bin/env python3
"""
Code Quality Validator - Validacion automatizada de calidad de codigo.

Este modulo ejecuta herramientas automatizadas para validar:
- Cobertura de tests (pytest + coverage)
- Calidad de codigo (ruff linting)
- Type checking (mypy)
- Seguridad (bandit)
- Duplicacion de codigo

Referencia: TDD Feature Agent - Validacion automatica de QA
"""

from __future__ import annotations

import ast
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeQualityValidator:
    """
    Validador de calidad de codigo.

    Ejecuta herramientas automatizadas para validar calidad del codigo
    generado durante el proceso TDD.
    """

    def __init__(self, project_root: Path):
        """
        Inicializa el validador.

        Args:
            project_root: Directorio raiz del proyecto
        """
        self.project_root = project_root

    def check_test_coverage(
        self,
        test_files: List[Path],
        source_files: List[Path],
        minimum_coverage: float = 90.0,
    ) -> Dict[str, object]:
        """
        Ejecuta tests con coverage.

        Args:
            test_files: Lista de archivos de test
            source_files: Lista de archivos fuente a medir
            minimum_coverage: Cobertura minima requerida (%)

        Returns:
            Diccionario con:
                - passed: bool
                - percent: float (porcentaje de cobertura)
                - total_lines: int
                - covered_lines: int
                - missing_lines: List[str]
                - report: str (texto completo del reporte)
        """
        logger.info(f"Ejecutando tests con coverage para {len(test_files)} archivos")

        try:
            # Construir comando pytest con coverage
            cmd = [
                "pytest",
                "--cov=" + str(self.project_root),
                "--cov-report=json",
                "--cov-report=term",
                "-v",
            ]

            # Agregar archivos de test
            for test_file in test_files:
                cmd.append(str(test_file))

            # Ejecutar pytest
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
            )

            # Leer reporte JSON de coverage
            coverage_json_path = self.project_root / "coverage.json"
            if coverage_json_path.exists():
                with open(coverage_json_path) as f:
                    coverage_data = json.load(f)

                total_percent = coverage_data.get("totals", {}).get("percent_covered", 0.0)
                total_lines = coverage_data.get("totals", {}).get("num_statements", 0)
                covered_lines = coverage_data.get("totals", {}).get("covered_lines", 0)

                # Extraer lineas faltantes por archivo
                missing_lines = []
                for file_path, file_data in coverage_data.get("files", {}).items():
                    missing = file_data.get("missing_lines", [])
                    if missing:
                        missing_lines.append(f"{file_path}: lines {missing}")

                return {
                    "passed": total_percent >= minimum_coverage,
                    "percent": round(total_percent, 2),
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "missing_lines": missing_lines,
                    "report": result.stdout,
                    "minimum_coverage": minimum_coverage,
                }
            else:
                # Coverage JSON no generado, parsear output
                logger.warning("Coverage JSON no encontrado, parseando stdout")
                return self._parse_coverage_from_stdout(
                    result.stdout,
                    minimum_coverage,
                )

        except subprocess.TimeoutExpired:
            logger.error("Timeout ejecutando tests")
            return {
                "passed": False,
                "percent": 0.0,
                "total_lines": 0,
                "covered_lines": 0,
                "missing_lines": [],
                "report": "Timeout ejecutando tests",
                "error": "Timeout",
            }
        except Exception as e:
            logger.exception(f"Error ejecutando coverage: {e}")
            return {
                "passed": False,
                "percent": 0.0,
                "total_lines": 0,
                "covered_lines": 0,
                "missing_lines": [],
                "report": str(e),
                "error": str(e),
            }

    def check_code_quality(
        self,
        source_files: List[Path],
    ) -> Dict[str, object]:
        """
        Ejecuta ruff para verificar calidad de codigo.

        Args:
            source_files: Lista de archivos fuente a verificar

        Returns:
            Diccionario con:
                - passed: bool
                - issues_count: int
                - issues: List[Dict] (ubicacion, codigo, mensaje)
                - report: str
        """
        logger.info(f"Ejecutando ruff para {len(source_files)} archivos")

        try:
            # Ejecutar ruff check
            cmd = ["ruff", "check", "--output-format=json"]
            for source_file in source_files:
                cmd.append(str(source_file))

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parsear output JSON
            issues = []
            if result.stdout:
                try:
                    ruff_output = json.loads(result.stdout)
                    for issue in ruff_output:
                        issues.append({
                            "file": issue.get("filename"),
                            "line": issue.get("location", {}).get("row"),
                            "column": issue.get("location", {}).get("column"),
                            "code": issue.get("code"),
                            "message": issue.get("message"),
                        })
                except json.JSONDecodeError:
                    logger.warning("No se pudo parsear output JSON de ruff")

            return {
                "passed": len(issues) == 0,
                "issues_count": len(issues),
                "issues": issues,
                "report": result.stdout if result.stdout else "No issues found",
            }

        except subprocess.TimeoutExpired:
            logger.error("Timeout ejecutando ruff")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": "Timeout ejecutando ruff",
                "error": "Timeout",
            }
        except FileNotFoundError:
            logger.warning("ruff no esta instalado, saltando verificacion")
            return {
                "passed": True,
                "issues_count": 0,
                "issues": [],
                "report": "ruff no instalado",
                "skipped": True,
            }
        except Exception as e:
            logger.exception(f"Error ejecutando ruff: {e}")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": str(e),
                "error": str(e),
            }

    def check_type_annotations(
        self,
        source_files: List[Path],
    ) -> Dict[str, object]:
        """
        Ejecuta mypy para verificar type hints.

        Args:
            source_files: Lista de archivos fuente a verificar

        Returns:
            Diccionario con:
                - passed: bool
                - issues_count: int
                - issues: List[Dict]
                - report: str
        """
        logger.info(f"Ejecutando mypy para {len(source_files)} archivos")

        try:
            # Ejecutar mypy
            cmd = ["mypy", "--strict", "--show-error-codes"]
            for source_file in source_files:
                cmd.append(str(source_file))

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parsear output
            issues = []
            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    # Formato: "file.py:10: error: Message [code]"
                    match = re.match(r"(.+):(\d+): (error|warning): (.+)", line)
                    if match:
                        issues.append({
                            "file": match.group(1),
                            "line": int(match.group(2)),
                            "severity": match.group(3),
                            "message": match.group(4),
                        })

            return {
                "passed": result.returncode == 0,
                "issues_count": len(issues),
                "issues": issues,
                "report": result.stdout,
            }

        except subprocess.TimeoutExpired:
            logger.error("Timeout ejecutando mypy")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": "Timeout ejecutando mypy",
                "error": "Timeout",
            }
        except FileNotFoundError:
            logger.warning("mypy no esta instalado, saltando verificacion")
            return {
                "passed": True,
                "issues_count": 0,
                "issues": [],
                "report": "mypy no instalado",
                "skipped": True,
            }
        except Exception as e:
            logger.exception(f"Error ejecutando mypy: {e}")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": str(e),
                "error": str(e),
            }

    def check_security(
        self,
        source_files: List[Path],
    ) -> Dict[str, object]:
        """
        Ejecuta bandit para detectar vulnerabilidades.

        Args:
            source_files: Lista de archivos fuente a verificar

        Returns:
            Diccionario con:
                - passed: bool
                - issues_count: int
                - issues: List[Dict] (severidad, confianza, mensaje)
                - report: str
        """
        logger.info(f"Ejecutando bandit para {len(source_files)} archivos")

        try:
            # Ejecutar bandit
            cmd = ["bandit", "-f", "json", "-r"]
            for source_file in source_files:
                cmd.append(str(source_file))

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parsear output JSON
            issues = []
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for issue in bandit_output.get("results", []):
                        issues.append({
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "severity": issue.get("issue_severity"),
                            "confidence": issue.get("issue_confidence"),
                            "test_id": issue.get("test_id"),
                            "message": issue.get("issue_text"),
                        })
                except json.JSONDecodeError:
                    logger.warning("No se pudo parsear output JSON de bandit")

            # Filtrar solo HIGH y MEDIUM severity
            high_issues = [
                i for i in issues
                if i["severity"] in ["HIGH", "MEDIUM"]
            ]

            return {
                "passed": len(high_issues) == 0,
                "issues_count": len(high_issues),
                "issues": high_issues,
                "all_issues_count": len(issues),
                "report": result.stdout if result.stdout else "No security issues found",
            }

        except subprocess.TimeoutExpired:
            logger.error("Timeout ejecutando bandit")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": "Timeout ejecutando bandit",
                "error": "Timeout",
            }
        except FileNotFoundError:
            logger.warning("bandit no esta instalado, saltando verificacion")
            return {
                "passed": True,
                "issues_count": 0,
                "issues": [],
                "report": "bandit no instalado",
                "skipped": True,
            }
        except Exception as e:
            logger.exception(f"Error ejecutando bandit: {e}")
            return {
                "passed": False,
                "issues_count": 0,
                "issues": [],
                "report": str(e),
                "error": str(e),
            }

    def check_documentation(
        self,
        source_files: List[Path],
    ) -> Dict[str, object]:
        """
        Verifica que funciones publicas tienen docstrings.

        Args:
            source_files: Lista de archivos fuente a verificar

        Returns:
            Diccionario con:
                - passed: bool
                - total_public_functions: int
                - missing_docstrings: List[str] (nombres de funciones)
        """
        logger.info(f"Verificando docstrings para {len(source_files)} archivos")

        missing_docstrings = []
        total_public_functions = 0

        for source_file in source_files:
            try:
                with open(source_file) as f:
                    tree = ast.parse(f.read(), filename=str(source_file))

                # Analizar funciones y metodos
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Solo funciones publicas (no empiezan con _)
                        if not node.name.startswith("_"):
                            total_public_functions += 1

                            # Verificar si tiene docstring
                            docstring = ast.get_docstring(node)
                            if not docstring:
                                missing_docstrings.append(
                                    f"{source_file.name}::{node.name}"
                                )

                    elif isinstance(node, ast.ClassDef):
                        # Metodos publicos de clases
                        for class_node in node.body:
                            if isinstance(class_node, ast.FunctionDef):
                                if not class_node.name.startswith("_"):
                                    total_public_functions += 1

                                    docstring = ast.get_docstring(class_node)
                                    if not docstring:
                                        missing_docstrings.append(
                                            f"{source_file.name}::{node.name}.{class_node.name}"
                                        )

            except Exception as e:
                logger.warning(f"Error parseando {source_file}: {e}")

        return {
            "passed": len(missing_docstrings) == 0,
            "total_public_functions": total_public_functions,
            "missing_docstrings": missing_docstrings,
            "missing_count": len(missing_docstrings),
        }

    def run_all_checks(
        self,
        test_files: List[Path],
        source_files: List[Path],
        minimum_coverage: float = 90.0,
    ) -> Dict[str, object]:
        """
        Ejecuta todas las verificaciones de calidad.

        Args:
            test_files: Lista de archivos de test
            source_files: Lista de archivos fuente
            minimum_coverage: Cobertura minima requerida (%)

        Returns:
            Diccionario con resultados de todas las verificaciones:
                - coverage: Dict
                - quality: Dict
                - type_check: Dict
                - security: Dict
                - documentation: Dict
                - overall_passed: bool
        """
        logger.info("Ejecutando todas las verificaciones de calidad")

        # Ejecutar verificaciones
        coverage_result = self.check_test_coverage(
            test_files=test_files,
            source_files=source_files,
            minimum_coverage=minimum_coverage,
        )

        quality_result = self.check_code_quality(source_files=source_files)
        type_check_result = self.check_type_annotations(source_files=source_files)
        security_result = self.check_security(source_files=source_files)
        documentation_result = self.check_documentation(source_files=source_files)

        # Determinar si todas pasaron
        overall_passed = (
            coverage_result.get("passed", False)
            and quality_result.get("passed", False)
            and type_check_result.get("passed", False)
            and security_result.get("passed", False)
            and documentation_result.get("passed", False)
        )

        return {
            "coverage": coverage_result,
            "quality": quality_result,
            "type_check": type_check_result,
            "security": security_result,
            "documentation": documentation_result,
            "overall_passed": overall_passed,
        }

    @staticmethod
    def _parse_coverage_from_stdout(
        stdout: str,
        minimum_coverage: float,
    ) -> Dict[str, object]:
        """
        Parsea porcentaje de coverage desde stdout de pytest.

        Args:
            stdout: Output de pytest --cov
            minimum_coverage: Cobertura minima requerida

        Returns:
            Diccionario con resultados parseados
        """
        # Buscar linea con formato: "TOTAL  123  45  63%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)

        if match:
            percent = float(match.group(1))
            return {
                "passed": percent >= minimum_coverage,
                "percent": percent,
                "total_lines": 0,
                "covered_lines": 0,
                "missing_lines": [],
                "report": stdout,
                "parsed_from_stdout": True,
            }

        return {
            "passed": False,
            "percent": 0.0,
            "total_lines": 0,
            "covered_lines": 0,
            "missing_lines": [],
            "report": stdout,
            "error": "No se pudo parsear coverage de stdout",
        }
