#!/usr/bin/env python3
"""
TDD Agent v1.1

Automatiza el ciclo Test-Driven Development completo:
1. Genera código de tests completo desde requisitos (no templates)
2. Ejecuta pytest con JSON report
3. Analiza errores con detalle
4. Auto-fix de errores comunes
5. Documenta el proceso

Versión v1.1 Features:
- Generación automática de código de tests completo
- Auto-fix de errores comunes (imports, paths)
- pytest-json-report para parsing robusto
- Ciclo iterativo con auto-fixes

Uso:
    python tdd_operativo.py --component audit_validator --requirements "..."
    python tdd_operativo.py --config requirements.json
    python tdd_operativo.py --component route_linter --requirements "..." --auto-fix
"""

import json
import subprocess
import sys
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Import del nuevo TestGenerator
from .test_generator import TestGenerator, TestCase


@dataclass
class TDDRequirements:
    """Requisitos para el componente a testear."""
    component_name: str
    requirements: str
    agent_type: str  # gate | chain | template
    expected_behavior: Dict[str, any]
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Resultado de ejecución de tests."""
    exit_code: int
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    failures: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class TDDCycleReport:
    """Reporte completo del ciclo TDD."""
    component: str
    cycle_date: str
    iterations: int
    initial_state: Dict[str, any]
    final_state: Dict[str, any]
    errors_discovered: List[Dict[str, any]]
    duration_total_seconds: float
    success: bool


class TDDAgent:
    """
    Agente que automatiza el ciclo Test-Driven Development.

    Workflow v1.1:
    1. parse_requirements() - Parsear requisitos del usuario
    2. generate_test_code() - Generar código completo de tests (no templates)
    3. run_tests() - Ejecutar pytest con JSON report
    4. analyze_failures() - Analizar fallos con detalle
    5. auto_fix_errors() - Corregir errores comunes automáticamente
    6. generate_documentation() - Documentar errores
    7. iterate() - Repetir hasta 100% pass o max_iterations
    """

    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.project_root = self._find_project_root()
        self.cycle_number = 1
        self.fixes_applied = []

    def _find_project_root(self) -> Path:
        """Encuentra la raíz del proyecto."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent
        return current.parent.parent.parent.parent

    def run_tdd_cycle(
        self,
        requirements: TDDRequirements,
        max_iterations: int = 5
    ) -> TDDCycleReport:
        """
        Ejecuta ciclo TDD completo v1.1.

        Args:
            requirements: Requisitos del componente
            max_iterations: Máximo de iteraciones

        Returns:
            TDDCycleReport con resultados completos
        """
        print(f"Starting TDD cycle v1.1 for: {requirements.component_name}")
        print(f"Auto-fix: {'ENABLED' if self.auto_fix else 'DISABLED'}")
        start_time = datetime.now()

        # Paso 1: Generar código completo de tests (v1.1)
        test_file = self.generate_test_code(requirements)
        print(f"[OK] Test code generated: {test_file}")

        # Paso 2: Ejecutar tests (initial run - expected to fail)
        initial_result = self.run_tests(test_file)
        print(f"\n[INFO] Initial run: {initial_result.passed}/{initial_result.total_tests} passing")

        if initial_result.total_tests == 0:
            print("[WARNING] No tests found!")
            return self._create_report(
                requirements,
                initial_result,
                initial_result,
                [],
                0,
                False
            )

        if initial_result.failed == 0 and initial_result.skipped == 0:
            print("[OK] All tests passing from start!")
            return self._create_report(
                requirements,
                initial_result,
                initial_result,
                [],
                (datetime.now() - start_time).total_seconds(),
                True
            )

        # Paso 3: Analizar fallos
        errors = self.analyze_failures(initial_result)
        print(f"[ERROR] {len(errors)} errors discovered")

        # Paso 4: Ciclo iterativo con auto-fix (v1.1)
        current_result = initial_result
        iteration = 1

        while iteration <= max_iterations and current_result.failed > 0:
            print(f"\n[INFO] Iteration {iteration}/{max_iterations}")

            if self.auto_fix:
                # Paso 4a: Intentar auto-fix
                fixes_made = self.auto_fix_errors(test_file, errors)

                if fixes_made > 0:
                    print(f"[OK] Applied {fixes_made} auto-fixes")

                    # Re-ejecutar tests
                    current_result = self.run_tests(test_file)
                    print(f"[INFO] After fixes: {current_result.passed}/{current_result.total_tests} passing")

                    # Re-analizar errores
                    errors = self.analyze_failures(current_result)

                    if current_result.failed == 0:
                        print("[OK] All tests passing after auto-fix!")
                        break
                else:
                    print("[WARNING] No auto-fixable errors found")
                    break
            else:
                # Sin auto-fix, salir después de primera iteración
                print("[INFO] Auto-fix disabled, manual fixes required")
                break

            iteration += 1

        # Paso 5: Documentar errores
        doc_file = self.generate_documentation(
            requirements.component_name,
            current_result,
            errors
        )
        print(f"[OK] Documentation generated: {doc_file}")

        # Verificar éxito
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        success = current_result.failed == 0 and current_result.skipped == 0

        if not success and not self.auto_fix:
            print("\n[INFO] Manual fixes required")
            print("      Review documentation and fix code manually")
            print(f"      Then run: pytest {test_file} -v")

        return self._create_report(
            requirements,
            initial_result,
            current_result,
            errors,
            duration,
            success
        )

    def generate_test_code(
        self,
        requirements: TDDRequirements
    ) -> Path:
        """
        Genera código completo de tests (v1.1).

        Args:
            requirements: Requisitos del componente

        Returns:
            Path al archivo de tests generado
        """
        # Usar TestGenerator v1.1
        generator = TestGenerator(
            component_name=requirements.component_name,
            agent_type=requirements.agent_type
        )

        # Analizar requisitos y generar test cases
        test_cases = generator.analyze_requirements(
            requirements.requirements,
            requirements.expected_behavior
        )

        print(f"[INFO] Generated {len(test_cases)} test cases")

        # Generar archivo de tests
        test_dir = self.project_root / "scripts" / "ai" / "agents" / requirements.component_name / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)

        test_file = test_dir / f"test_{requirements.component_name}.py"

        generator.generate_test_file(test_file)

        return test_file

    def generate_test_template(
        self,
        requirements: TDDRequirements
    ) -> Path:
        """
        Genera template de archivo de tests.

        Args:
            requirements: Requisitos del componente

        Returns:
            Path al archivo de tests generado
        """
        component = requirements.component_name
        test_dir = self.project_root / "scripts" / "ai" / "agents" / component / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)

        test_file = test_dir / f"test_{component}.py"

        # Template básico
        template = f'''"""
Tests para {component.title()} Agent

Generado por TDD Agent en {datetime.now().isoformat()}

Requirements:
{requirements.requirements}

Expected Behavior:
- Happy path: {requirements.expected_behavior.get("happy_path", "TBD")}
- Edge cases: {len(requirements.expected_behavior.get("edge_cases", []))} cases
- Error cases: {len(requirements.expected_behavior.get("error_cases", []))} cases
"""

import pytest
from pathlib import Path
from textwrap import dedent

# TODO: Import your agent here
# from scripts.coding.ai.agents.{component}.{component}_agent import {component.title()}Agent


class Test{component.title()}Basics:
    """Tests básicos de funcionalidad."""

    @pytest.fixture
    def agent(self):
        """Fixture: Create agent instance."""
        # TODO: Implement
        pytest.skip("Not implemented yet")

    def test_agent_initialization(self, agent):
        """Test: Agente se inicializa correctamente."""
        # TODO: Implement
        assert agent is not None

    def test_happy_path(self, agent):
        """Test: Caso exitoso básico."""
        # TODO: Implement based on requirements:
        # {requirements.expected_behavior.get("happy_path", "")}
        pytest.skip("Not implemented yet")


class Test{component.title()}EdgeCases:
    """Tests de casos edge."""

    @pytest.fixture
    def agent(self):
        pytest.skip("Not implemented yet")

'''

        # Agregar tests para edge cases
        edge_cases = requirements.expected_behavior.get("edge_cases", [])
        for i, case in enumerate(edge_cases, 1):
            test_method = f'''    def test_edge_case_{i}(self, agent):
        """Test: {case}"""
        # TODO: Implement test for: {case}
        pytest.skip("Not implemented yet")

'''
            template += test_method

        template += f'''
class Test{component.title()}ErrorHandling:
    """Tests de manejo de errores."""

    @pytest.fixture
    def agent(self):
        pytest.skip("Not implemented yet")

'''

        # Agregar tests para error cases
        error_cases = requirements.expected_behavior.get("error_cases", [])
        for i, case in enumerate(error_cases, 1):
            test_method = f'''    def test_error_case_{i}(self, agent):
        """Test: {case}"""
        # TODO: Implement test for: {case}
        pytest.skip("Not implemented yet")

'''
            template += test_method

        template += f'''
class Test{component.title()}Integration:
    """Tests de integración end-to-end."""

    def test_full_cycle_pass(self, tmp_path):
        """Test E2E: Ciclo completo exitoso."""
        # TODO: Implement full integration test
        pytest.skip("Not implemented yet")

    def test_full_cycle_fail(self, tmp_path):
        """Test E2E: Ciclo con errores esperados."""
        # TODO: Implement failure scenario
        pytest.skip("Not implemented yet")


# Pytest marks
pytestmark = [
    pytest.mark.unit,
    pytest.mark.tdd_generated
]
'''

        # Escribir archivo
        test_file.write_text(template)

        return test_file

    def auto_fix_errors(self, test_file: Path, errors: List[Dict[str, any]]) -> int:
        """
        Aplica auto-fix para errores comunes (v1.1).

        Args:
            test_file: Path al archivo de tests
            errors: Lista de errores analizados

        Returns:
            Número de fixes aplicados
        """
        fixes_applied = 0

        for error in errors:
            error_type = error.get("error_type", "Unknown")
            error_message = error.get("root_cause", "")

            # Fix 1: ImportError - Agregar imports faltantes
            if "ImportError" in error_type or "ModuleNotFoundError" in error_type:
                if self._fix_import_error(test_file, error_message):
                    fixes_applied += 1
                    self.fixes_applied.append(f"Added missing import: {error_message}")

            # Fix 2: FileNotFoundError - Crear directorios/archivos
            elif "FileNotFoundError" in error_type:
                if self._fix_file_not_found(test_file, error_message):
                    fixes_applied += 1
                    self.fixes_applied.append(f"Created missing file/directory: {error_message}")

            # Fix 3: KeyError: message - Error conocido de logging
            elif "KeyError" in error_type and "message" in error_message.lower():
                if self._fix_logging_message_error(test_file):
                    fixes_applied += 1
                    self.fixes_applied.append("Fixed logging 'message' KeyError")

            # Fix 4: NameError - Typos comunes
            elif "NameError" in error_type:
                if self._fix_name_error(test_file, error_message):
                    fixes_applied += 1
                    self.fixes_applied.append(f"Fixed NameError: {error_message}")

        return fixes_applied

    def _fix_import_error(self, test_file: Path, error_message: str) -> bool:
        """Intenta corregir ImportError agregando import faltante."""
        # Extraer módulo faltante
        match = re.search(r"No module named '(\w+)'", error_message)
        if not match:
            return False

        module = match.group(1)

        # Leer archivo
        content = test_file.read_text()

        # Verificar que no existe ya el import
        if f"import {module}" in content or f"from {module}" in content:
            return False

        # Agregar import al inicio (después de docstring)
        lines = content.split('\n')
        insert_pos = 0

        # Buscar fin de docstring
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                if not in_docstring:
                    insert_pos = i + 1
                    break

        # Insertar import
        lines.insert(insert_pos, f"import {module}")

        # Escribir archivo
        test_file.write_text('\n'.join(lines))

        return True

    def _fix_file_not_found(self, test_file: Path, error_message: str) -> bool:
        """Intenta corregir FileNotFoundError creando archivo/directorio."""
        # Extraer path del error
        match = re.search(r"'([^']+)'", error_message)
        if not match:
            return False

        missing_path = Path(match.group(1))

        # Si es relativo, hacerlo absoluto
        if not missing_path.is_absolute():
            missing_path = test_file.parent / missing_path

        # Crear directorio si es necesario
        if not missing_path.suffix:
            # Es un directorio
            missing_path.mkdir(parents=True, exist_ok=True)
        else:
            # Es un archivo
            missing_path.parent.mkdir(parents=True, exist_ok=True)
            if not missing_path.exists():
                missing_path.touch()

        return True

    def _fix_logging_message_error(self, test_file: Path) -> bool:
        """Corrige el error de 'message' en logging extra dict."""
        content = test_file.read_text()

        # Buscar patrón: extra={...,"message": ...}
        pattern = r'extra=\{([^}]*)"message":\s*[^,}]+,?\s*([^}]*)\}'

        if re.search(pattern, content):
            # Remover "message" del extra dict
            content = re.sub(
                pattern,
                r'extra={\1\2}',
                content
            )

            test_file.write_text(content)
            return True

        return False

    def _fix_name_error(self, test_file: Path, error_message: str) -> bool:
        """Intenta corregir NameError detectando typos comunes."""
        # Extraer nombre no definido
        match = re.search(r"name '(\w+)' is not defined", error_message)
        if not match:
            return False

        undefined_name = match.group(1)

        # Typos comunes conocidos
        typo_map = {
            "tdd": "TDD",
            "ok": "OK",
            "error": "ERROR",
            "warning": "WARNING",
            "pytest": "pytest",
            "tmp_path": "tmp_path",
        }

        if undefined_name.lower() in typo_map:
            correct_name = typo_map[undefined_name.lower()]

            content = test_file.read_text()

            # Reemplazar todas las ocurrencias
            content = re.sub(
                rf'\b{undefined_name}\b',
                correct_name,
                content
            )

            test_file.write_text(content)
            return True

        return False

    def run_tests(self, test_file: Path) -> TestResult:
        """
        Ejecuta pytest con JSON report (v1.1).

        Args:
            test_file: Path al archivo de tests

        Returns:
            TestResult con resultados detallados
        """
        # Intentar usar pytest-json-report si está disponible
        json_report_file = test_file.parent / ".pytest_report.json"

        # Verificar si pytest-json-report está instalado
        check_plugin = subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            text=True
        )

        use_json_report = "pytest-json-report" in check_plugin.stdout or "json-report" in check_plugin.stdout

        if use_json_report:
            # Usar JSON report para parsing robusto
            result = subprocess.run(
                [
                    "pytest", str(test_file), "-v", "--tb=short",
                    "--json-report", f"--json-report-file={json_report_file}"
                ],
                capture_output=True,
                text=True
            )

            # Parsear JSON si existe
            if json_report_file.exists():
                return self._parse_json_report(json_report_file, result.returncode)
        else:
            # Fallback: parsing básico de text output
            result = subprocess.run(
                ["pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True
            )

        # Parsear output
        output = result.stdout + result.stderr

        # Extraer métricas (parsing básico)
        total = passed = failed = skipped = 0
        duration = 0.0

        for line in output.split('\n'):
            if " passed" in line:
                # Ejemplo: "22 passed in 0.17s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        passed = int(parts[i-1])
                    elif part == "failed":
                        failed = int(parts[i-1])
                    elif part == "skipped":
                        skipped = int(parts[i-1])
                    elif part == "in":
                        duration = float(parts[i+1].replace('s', ''))

        total = passed + failed + skipped

        # Extraer failures (parsing simple)
        failures = self._extract_failures_from_output(output)

        return TestResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            failures=failures
        )

    def _extract_failures_from_output(self, output: str) -> List[Dict[str, str]]:
        """Extrae información de failures del output de pytest."""
        failures = []

        # Parsing básico - buscar líneas con FAILED
        for line in output.split('\n'):
            if "FAILED" in line:
                parts = line.split("::")
                if len(parts) >= 2:
                    test_file = parts[0].strip()
                    test_name = parts[1].strip() if len(parts) > 1 else "unknown"

                    failures.append({
                        "test_file": test_file,
                        "test_name": test_name,
                        "error_type": "Unknown",  # Requiere parsing más complejo
                        "error_message": "See pytest output for details"
                    })

        return failures

    def _parse_json_report(self, json_file: Path, exit_code: int) -> TestResult:
        """
        Parsea pytest JSON report (v1.1).

        Args:
            json_file: Path al archivo JSON generado por pytest-json-report
            exit_code: Exit code de pytest

        Returns:
            TestResult con información detallada
        """
        with open(json_file) as f:
            data = json.load(f)

        summary = data.get("summary", {})
        tests = data.get("tests", [])

        # Extraer métricas
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        duration = data.get("duration", 0.0)

        # Extraer failures con detalles completos
        failures = []
        for test in tests:
            if test.get("outcome") == "failed":
                failure = {
                    "test_file": test.get("nodeid", "").split("::")[0],
                    "test_name": test.get("nodeid", "").split("::")[-1],
                    "error_type": self._extract_error_type_from_call(test.get("call", {})),
                    "error_message": test.get("call", {}).get("longrepr", "Unknown error"),
                    "lineno": test.get("lineno", 0),
                    "duration": test.get("duration", 0.0)
                }
                failures.append(failure)

        return TestResult(
            exit_code=exit_code,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            failures=failures
        )

    def _extract_error_type_from_call(self, call_info: Dict) -> str:
        """Extrae el tipo de error del call info de pytest."""
        longrepr = call_info.get("longrepr", "")

        if isinstance(longrepr, str):
            # Buscar nombre de excepción
            match = re.search(r'(\w+Error|Exception)', longrepr)
            if match:
                return match.group(1)

        return "Unknown"

    def analyze_failures(self, result: TestResult) -> List[Dict[str, any]]:
        """
        Analiza fallos y genera reporte de errores.

        Args:
            result: Resultado de tests

        Returns:
            Lista de errores con causa raíz y solución
        """
        errors = []

        for i, failure in enumerate(result.failures, 1):
            error = {
                "error_id": i,
                "test_name": failure["test_name"],
                "error_type": failure["error_type"],
                "root_cause": f"Test {failure['test_name']} failed",
                "affected_code": failure["test_file"],
                "solution": "Review test implementation and fix code",
                "priority": "high"
            }
            errors.append(error)

        return errors

    def generate_documentation(
        self,
        component: str,
        result: TestResult,
        errors: List[Dict[str, any]]
    ) -> Path:
        """
        Genera documentación markdown de errores.

        Args:
            component: Nombre del componente
            result: Resultado de tests
            errors: Lista de errores analizados

        Returns:
            Path al documento generado
        """
        doc_dir = self.project_root / "docs" / "backend" / "permisos" / "promptops"
        doc_dir.mkdir(parents=True, exist_ok=True)

        doc_file = doc_dir / f"TDD_{component.upper()}_ERRORS.md"

        coverage_pct = (result.passed / result.total_tests * 100) if result.total_tests > 0 else 0

        content = f"""# TDD Cycle: {component.title()} - Errors and Solutions

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Component:** {component}
**Cycle:** {self.cycle_number}
**Generated by:** TDD Agent MVP

---

## Summary

**First Test Run:**
- [OK] {result.passed} tests PASSING
- [ERROR] {result.failed} tests FAILING
- [WARNING] {result.skipped} tests SKIPPED

**Coverage:** {coverage_pct:.1f}%
**Duration:** {result.duration:.2f}s

---

## Errors Discovered

Total errors: {len(errors)}

"""

        for error in errors:
            content += f"""
### Error {error['error_id']}: {error['test_name']}

**Type:** {error['error_type']}
**Priority:** {error['priority']}

**Root Cause:**
{error['root_cause']}

**Affected Code:**
`{error['affected_code']}`

**Solution:**
{error['solution']}

---
"""

        content += f"""
## Next Steps

1. Review each error above
2. Fix code based on solutions provided
3. Re-run tests: `pytest {doc_file.parent.parent / 'scripts' / 'ai' / 'agents' / component / 'tests'} -v`
4. Iterate until all tests pass

---

## TDD Cycle Metrics

| Metric | Value |
|--------|-------|
| Total Tests | {result.total_tests} |
| Passing | {result.passed} |
| Failing | {result.failed} |
| Skipped | {result.skipped} |
| Coverage | {coverage_pct:.1f}% |
| Duration | {result.duration:.2f}s |

---

**Generated by TDD Agent MVP v1.0**
"""

        doc_file.write_text(content)

        return doc_file

    def _create_report(
        self,
        requirements: TDDRequirements,
        initial: TestResult,
        final: TestResult,
        errors: List[Dict[str, any]],
        duration: float,
        success: bool
    ) -> TDDCycleReport:
        """Crea reporte final del ciclo TDD."""
        return TDDCycleReport(
            component=requirements.component_name,
            cycle_date=datetime.now().isoformat(),
            iterations=self.cycle_number,
            initial_state={
                "tests_total": initial.total_tests,
                "tests_passing": initial.passed,
                "tests_failing": initial.failed,
                "coverage_percent": (initial.passed / initial.total_tests * 100) if initial.total_tests > 0 else 0
            },
            final_state={
                "tests_total": final.total_tests,
                "tests_passing": final.passed,
                "tests_failing": final.failed,
                "coverage_percent": (final.passed / final.total_tests * 100) if final.total_tests > 0 else 0
            },
            errors_discovered=errors,
            duration_total_seconds=duration,
            success=success
        )


def main():
    """Entry point del TDD Agent."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TDD Agent - Automat Test-Driven Development cycle"
    )
    parser.add_argument(
        '--component',
        required=True,
        help='Component name (e.g., audit_validator)'
    )
    parser.add_argument(
        '--requirements',
        required=True,
        help='Requirements description or path to JSON file'
    )
    parser.add_argument(
        '--type',
        choices=['gate', 'chain', 'template'],
        default='gate',
        help='Agent type'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Enable automatic fixing of common errors (v1.1 feature)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum number of TDD iterations (default: 5)'
    )

    args = parser.parse_args()

    # Crear requirements
    requirements = TDDRequirements(
        component_name=args.component,
        requirements=args.requirements,
        agent_type=args.type,
        expected_behavior={
            "happy_path": "Defined in requirements",
            "edge_cases": [],
            "error_cases": []
        }
    )

    # Ejecutar ciclo TDD v1.1
    agent = TDDAgent(verbose=args.verbose, auto_fix=args.auto_fix)
    report = agent.run_tdd_cycle(requirements)

    # Mostrar reporte
    print("\n" + "="*70)
    print("TDD CYCLE REPORT")
    print("="*70)
    print(f"Component: {report.component}")
    print(f"Success: {report.success}")
    print(f"Duration: {report.duration_total_seconds:.2f}s")
    print(f"\nInitial: {report.initial_state['tests_passing']}/{report.initial_state['tests_total']} passing")
    print(f"Final: {report.final_state['tests_passing']}/{report.final_state['tests_total']} passing")
    print(f"Errors discovered: {len(report.errors_discovered)}")
    print("="*70)

    # Exit code
    sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
