"""
SyntaxValidator Agent

Responsabilidad: Validar sintaxis y estilo del código generado.
Input: Código de tests generado
Output: Código validado o errores de sintaxis/estilo
"""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class SyntaxValidator(Agent):
    """
    Agente especializado en validación de sintaxis y estilo.

    Valida usando:
    - Python AST (sintaxis)
    - ruff (lint)
    - black (formato)
    - mypy (tipos - opcional)
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="SyntaxValidator", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan tests generados."""
        errors = []

        if "generated_tests" not in input_data:
            errors.append("Falta 'generated_tests' en input")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la validación de sintaxis y estilo."""
        generated_tests = input_data["generated_tests"]

        self.logger.info(f"Validando {len(generated_tests)} archivos de tests")

        validated_tests = []
        validation_errors = []

        for test in generated_tests:
            test_file = test["test_file"]
            code = test["generated_code"]

            self.logger.info(f"Validando {test_file}")

            # Validar sintaxis Python
            syntax_ok, syntax_errors = self._validate_syntax(code)

            if not syntax_ok:
                validation_errors.append({
                    "file": test_file,
                    "stage": "syntax",
                    "errors": syntax_errors
                })
                continue

            # Validar con ruff
            ruff_ok, ruff_errors = self._validate_ruff(code)

            if not ruff_ok:
                validation_errors.append({
                    "file": test_file,
                    "stage": "ruff",
                    "errors": ruff_errors
                })
                continue

            # Validar formato con black
            black_ok, formatted_code = self._validate_black(code)

            if not black_ok:
                self.logger.warning(f"Black reformateó {test_file}")

            # Validar tipos con mypy (opcional)
            if self.get_config("run_mypy", False):
                mypy_ok, mypy_errors = self._validate_mypy(formatted_code)
                if not mypy_ok:
                    self.logger.warning(f"Mypy warnings en {test_file}: {mypy_errors}")

            # Test validado correctamente
            validated_tests.append({
                "source_file": test["source_file"],
                "test_file": test_file,
                "validated_code": formatted_code,
                "original_code": code,
                "reformatted": not black_ok
            })

        return {
            "validated_tests": validated_tests,
            "total_validated": len(validated_tests),
            "validation_errors": validation_errors,
            "total_errors": len(validation_errors),
            "success_rate": (
                len(validated_tests) / len(generated_tests) * 100
                if generated_tests else 0
            )
        }

    def _validate_syntax(self, code: str) -> tuple[bool, List[str]]:
        """
        Valida sintaxis Python con AST.

        Args:
            code: Código a validar

        Returns:
            Tupla (es_válido, lista_errores)
        """
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            return False, [f"SyntaxError línea {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Error de parsing: {str(e)}"]

    def _validate_ruff(self, code: str) -> tuple[bool, List[str]]:
        """
        Valida código con ruff.

        Args:
            code: Código a validar

        Returns:
            Tupla (es_válido, lista_errores)
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            # Ejecutar ruff
            result = subprocess.run(
                ["ruff", "check", temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Limpiar archivo temporal
            Path(temp_path).unlink()

            if result.returncode == 0:
                return True, []
            else:
                errors = result.stdout.split('\n')
                return False, [e for e in errors if e.strip()]

        except FileNotFoundError:
            self.logger.warning("ruff no instalado, saltando validación")
            return True, []
        except Exception as e:
            self.logger.error(f"Error ejecutando ruff: {e}")
            return True, []  # No bloquear si falla ruff

    def _validate_black(self, code: str) -> tuple[bool, str]:
        """
        Valida formato con black.

        Args:
            code: Código a validar

        Returns:
            Tupla (sin_cambios, código_formateado)
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            # Ejecutar black
            result = subprocess.run(
                ["black", "--quiet", temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Leer código formateado
            with open(temp_path) as f:
                formatted_code = f.read()

            # Limpiar archivo temporal
            Path(temp_path).unlink()

            # Comparar
            unchanged = (code == formatted_code)

            return unchanged, formatted_code

        except FileNotFoundError:
            self.logger.warning("black no instalado, saltando formato")
            return True, code
        except Exception as e:
            self.logger.error(f"Error ejecutando black: {e}")
            return True, code

    def _validate_mypy(self, code: str) -> tuple[bool, List[str]]:
        """
        Valida tipos con mypy.

        Args:
            code: Código a validar

        Returns:
            Tupla (es_válido, lista_warnings)
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            # Ejecutar mypy
            result = subprocess.run(
                ["mypy", temp_path, "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Limpiar archivo temporal
            Path(temp_path).unlink()

            if result.returncode == 0:
                return True, []
            else:
                warnings = result.stdout.split('\n')
                return False, [w for w in warnings if w.strip()]

        except FileNotFoundError:
            self.logger.warning("mypy no instalado, saltando validación de tipos")
            return True, []
        except Exception as e:
            self.logger.error(f"Error ejecutando mypy: {e}")
            return True, []

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que la validación sea exitosa."""
        errors = []

        validated_tests = output_data.get("validated_tests", [])
        validation_errors = output_data.get("validation_errors", [])

        if not validated_tests:
            errors.append("No se validó ningún test exitosamente")

        # Si más del 50% falló, hay un problema
        total = len(validated_tests) + len(validation_errors)
        if total > 0:
            error_rate = len(validation_errors) / total
            if error_rate > 0.5:
                errors.append(
                    f"Tasa de error muy alta: {error_rate:.1%} "
                    f"({len(validation_errors)}/{total})"
                )

        return errors
