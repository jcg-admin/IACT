#!/usr/bin/env python3
"""
TDD Constitution - Reglas inmutables de cumplimiento TDD.

Este modulo define las reglas que NO PUEDEN ser violadas durante
la ejecucion del TDDFeatureAgent. Violaciones CRITICAL causan fallo inmediato.

Referencia: Diseño de TDD Feature Agent con garantias de calidad
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Niveles de severidad para violaciones de constitution."""
    CRITICAL = "CRITICAL"  # Causa fallo inmediato del agente
    HIGH = "HIGH"          # Debe corregirse antes de continuar
    MEDIUM = "MEDIUM"      # Advertencia, pero puede continuar


@dataclass
class ConstitutionRule:
    """Representa una regla de la constitution TDD."""
    code: str
    description: str
    severity: Severity
    auto_fix: bool
    threshold: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convierte a diccionario."""
        return {
            "code": self.code,
            "description": self.description,
            "severity": self.severity.value,
            "auto_fix": self.auto_fix,
            "threshold": self.threshold,
        }


@dataclass
class ConstitutionViolation:
    """Representa una violacion de la constitution."""
    rule_code: str
    severity: Severity
    message: str
    evidence: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convierte a diccionario."""
        return {
            "rule_code": self.rule_code,
            "severity": self.severity.value,
            "message": self.message,
            "evidence": self.evidence or {},
        }


class TDDConstitution:
    """
    Constitution TDD - Reglas inmutables de cumplimiento.

    Estas reglas garantizan que el proceso TDD se ejecute correctamente:
    - RED: Tests escritos primero, deben fallar
    - GREEN: Codigo implementado, tests pasan
    - REFACTOR: Optimizacion sin romper tests

    Violaciones CRITICAL causan fallo inmediato del agente.
    """

    # Reglas de la constitution
    RULES: Dict[str, ConstitutionRule] = {
        "RED_BEFORE_GREEN": ConstitutionRule(
            code="RED_BEFORE_GREEN",
            description="Tests deben escribirse ANTES del codigo de implementacion",
            severity=Severity.CRITICAL,
            auto_fix=False,
        ),

        "TESTS_MUST_FAIL_FIRST": ConstitutionRule(
            code="TESTS_MUST_FAIL_FIRST",
            description="Tests deben fallar inicialmente en la fase RED",
            severity=Severity.CRITICAL,
            auto_fix=False,
        ),

        "ALL_TESTS_MUST_PASS": ConstitutionRule(
            code="ALL_TESTS_MUST_PASS",
            description="Todos los tests deben pasar despues de la fase GREEN",
            severity=Severity.CRITICAL,
            auto_fix=False,
        ),

        "TESTS_STAY_GREEN_AFTER_REFACTOR": ConstitutionRule(
            code="TESTS_STAY_GREEN_AFTER_REFACTOR",
            description="Tests deben seguir pasando despues de la fase REFACTOR",
            severity=Severity.CRITICAL,
            auto_fix=False,
        ),

        "MINIMUM_COVERAGE": ConstitutionRule(
            code="MINIMUM_COVERAGE",
            description="Cobertura de tests debe ser >= 90%",
            severity=Severity.HIGH,
            auto_fix=False,
            threshold=90.0,
        ),

        "NO_SECURITY_ISSUES": ConstitutionRule(
            code="NO_SECURITY_ISSUES",
            description="No debe haber vulnerabilidades de seguridad detectadas",
            severity=Severity.HIGH,
            auto_fix=False,
        ),

        "CODE_QUALITY_PASSING": ConstitutionRule(
            code="CODE_QUALITY_PASSING",
            description="Codigo debe pasar verificaciones de calidad (linting, types)",
            severity=Severity.MEDIUM,
            auto_fix=True,
        ),

        "DOCUMENTATION_REQUIRED": ConstitutionRule(
            code="DOCUMENTATION_REQUIRED",
            description="Funciones publicas deben tener docstrings",
            severity=Severity.MEDIUM,
            auto_fix=False,
        ),
    }

    @classmethod
    def validate_tdd_compliance(
        cls,
        execution_log: Dict,
    ) -> Dict[str, object]:
        """
        Valida cumplimiento de la constitution TDD.

        Args:
            execution_log: Log de ejecucion del TDDFeatureAgent con:
                - phases: Dict con datos de cada fase (red, green, refactor)
                - test_executions: List de resultados de tests
                - artifacts: Dict con archivos generados
                - metrics: Dict con metricas de calidad

        Returns:
            Diccionario con:
                - compliant: bool (True si cumple todas las reglas CRITICAL)
                - violations: List[ConstitutionViolation]
                - score: float (0-100, ponderado por severidad)
                - evidence: Dict con evidencia de cada regla
        """
        violations: List[ConstitutionViolation] = []
        evidence: Dict[str, Dict] = {}

        # Validar RED_BEFORE_GREEN
        red_evidence = cls._validate_red_before_green(execution_log)
        evidence["RED_BEFORE_GREEN"] = red_evidence
        if not red_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="RED_BEFORE_GREEN",
                    severity=Severity.CRITICAL,
                    message=red_evidence["message"],
                    evidence=red_evidence,
                )
            )

        # Validar TESTS_MUST_FAIL_FIRST
        fail_first_evidence = cls._validate_tests_must_fail_first(execution_log)
        evidence["TESTS_MUST_FAIL_FIRST"] = fail_first_evidence
        if not fail_first_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="TESTS_MUST_FAIL_FIRST",
                    severity=Severity.CRITICAL,
                    message=fail_first_evidence["message"],
                    evidence=fail_first_evidence,
                )
            )

        # Validar ALL_TESTS_MUST_PASS
        all_pass_evidence = cls._validate_all_tests_must_pass(execution_log)
        evidence["ALL_TESTS_MUST_PASS"] = all_pass_evidence
        if not all_pass_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="ALL_TESTS_MUST_PASS",
                    severity=Severity.CRITICAL,
                    message=all_pass_evidence["message"],
                    evidence=all_pass_evidence,
                )
            )

        # Validar TESTS_STAY_GREEN_AFTER_REFACTOR
        stay_green_evidence = cls._validate_tests_stay_green_after_refactor(execution_log)
        evidence["TESTS_STAY_GREEN_AFTER_REFACTOR"] = stay_green_evidence
        if not stay_green_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="TESTS_STAY_GREEN_AFTER_REFACTOR",
                    severity=Severity.CRITICAL,
                    message=stay_green_evidence["message"],
                    evidence=stay_green_evidence,
                )
            )

        # Validar MINIMUM_COVERAGE
        coverage_evidence = cls._validate_minimum_coverage(execution_log)
        evidence["MINIMUM_COVERAGE"] = coverage_evidence
        if not coverage_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="MINIMUM_COVERAGE",
                    severity=Severity.HIGH,
                    message=coverage_evidence["message"],
                    evidence=coverage_evidence,
                )
            )

        # Validar NO_SECURITY_ISSUES
        security_evidence = cls._validate_no_security_issues(execution_log)
        evidence["NO_SECURITY_ISSUES"] = security_evidence
        if not security_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="NO_SECURITY_ISSUES",
                    severity=Severity.HIGH,
                    message=security_evidence["message"],
                    evidence=security_evidence,
                )
            )

        # Validar CODE_QUALITY_PASSING
        quality_evidence = cls._validate_code_quality_passing(execution_log)
        evidence["CODE_QUALITY_PASSING"] = quality_evidence
        if not quality_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="CODE_QUALITY_PASSING",
                    severity=Severity.MEDIUM,
                    message=quality_evidence["message"],
                    evidence=quality_evidence,
                )
            )

        # Validar DOCUMENTATION_REQUIRED
        docs_evidence = cls._validate_documentation_required(execution_log)
        evidence["DOCUMENTATION_REQUIRED"] = docs_evidence
        if not docs_evidence["passed"]:
            violations.append(
                ConstitutionViolation(
                    rule_code="DOCUMENTATION_REQUIRED",
                    severity=Severity.MEDIUM,
                    message=docs_evidence["message"],
                    evidence=docs_evidence,
                )
            )

        # Calcular compliance
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        compliant = len(critical_violations) == 0

        # Calcular score (0-100)
        score = cls._calculate_compliance_score(violations, evidence)

        return {
            "compliant": compliant,
            "violations": [v.to_dict() for v in violations],
            "score": score,
            "evidence": evidence,
            "summary": {
                "total_rules": len(cls.RULES),
                "passed_rules": len(cls.RULES) - len(violations),
                "critical_violations": len(critical_violations),
                "high_violations": len([v for v in violations if v.severity == Severity.HIGH]),
                "medium_violations": len([v for v in violations if v.severity == Severity.MEDIUM]),
            }
        }

    @staticmethod
    def _validate_red_before_green(execution_log: Dict) -> Dict:
        """Valida que tests se escribieron antes del codigo."""
        phases = execution_log.get("phases", {})

        # Verificar que existe fase RED y GREEN
        red_phase = phases.get("red_phase")
        green_phase = phases.get("green_phase")

        if not red_phase or not green_phase:
            return {
                "passed": False,
                "message": "Fases RED o GREEN no encontradas en execution log",
                "red_timestamp": None,
                "green_timestamp": None,
            }

        # Verificar timestamps
        red_timestamp = red_phase.get("timestamp")
        green_timestamp = green_phase.get("timestamp")

        if not red_timestamp or not green_timestamp:
            return {
                "passed": False,
                "message": "Timestamps faltantes en fases RED o GREEN",
                "red_timestamp": red_timestamp,
                "green_timestamp": green_timestamp,
            }

        # RED debe ser antes que GREEN
        if red_timestamp >= green_timestamp:
            return {
                "passed": False,
                "message": f"Fase GREEN ejecutada antes o al mismo tiempo que RED",
                "red_timestamp": red_timestamp,
                "green_timestamp": green_timestamp,
            }

        return {
            "passed": True,
            "message": "Tests escritos antes del codigo de implementacion",
            "red_timestamp": red_timestamp,
            "green_timestamp": green_timestamp,
        }

    @staticmethod
    def _validate_tests_must_fail_first(execution_log: Dict) -> Dict:
        """Valida que tests fallaron en la fase RED."""
        test_executions = execution_log.get("test_executions", [])

        # Buscar ejecucion de tests en fase RED
        red_test_execution = None
        for test_exec in test_executions:
            if test_exec.get("phase") == "red_phase":
                red_test_execution = test_exec
                break

        if not red_test_execution:
            return {
                "passed": False,
                "message": "No se encontro ejecucion de tests en fase RED",
                "failed_count": 0,
                "total_count": 0,
            }

        result = red_test_execution.get("result", {})
        failed = result.get("failed", 0)
        total = result.get("total", 0)

        if failed == 0:
            return {
                "passed": False,
                "message": "Tests no fallaron en fase RED (deben fallar inicialmente)",
                "failed_count": failed,
                "total_count": total,
            }

        return {
            "passed": True,
            "message": f"{failed}/{total} tests fallaron en fase RED como esperado",
            "failed_count": failed,
            "total_count": total,
        }

    @staticmethod
    def _validate_all_tests_must_pass(execution_log: Dict) -> Dict:
        """Valida que todos los tests pasaron en fase GREEN."""
        test_executions = execution_log.get("test_executions", [])

        # Buscar ejecucion de tests en fase GREEN
        green_test_execution = None
        for test_exec in test_executions:
            if test_exec.get("phase") == "green_phase":
                green_test_execution = test_exec
                break

        if not green_test_execution:
            return {
                "passed": False,
                "message": "No se encontro ejecucion de tests en fase GREEN",
                "passed_count": 0,
                "total_count": 0,
            }

        result = green_test_execution.get("result", {})
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        total = result.get("total", 0)

        if failed > 0:
            return {
                "passed": False,
                "message": f"{failed}/{total} tests aun fallan en fase GREEN",
                "passed_count": passed,
                "failed_count": failed,
                "total_count": total,
            }

        if total == 0:
            return {
                "passed": False,
                "message": "No se ejecutaron tests en fase GREEN",
                "passed_count": 0,
                "total_count": 0,
            }

        return {
            "passed": True,
            "message": f"Todos los tests ({total}) pasaron en fase GREEN",
            "passed_count": passed,
            "total_count": total,
        }

    @staticmethod
    def _validate_tests_stay_green_after_refactor(execution_log: Dict) -> Dict:
        """Valida que tests siguen pasando despues de REFACTOR."""
        test_executions = execution_log.get("test_executions", [])

        # Buscar ejecucion de tests en fase REFACTOR
        refactor_test_execution = None
        for test_exec in test_executions:
            if test_exec.get("phase") == "refactor_phase":
                refactor_test_execution = test_exec
                break

        if not refactor_test_execution:
            # Si no hay fase REFACTOR, es valido (puede ser que no hubo refactor)
            return {
                "passed": True,
                "message": "No se ejecuto fase REFACTOR (opcional)",
                "passed_count": 0,
                "total_count": 0,
            }

        result = refactor_test_execution.get("result", {})
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        total = result.get("total", 0)

        if failed > 0:
            return {
                "passed": False,
                "message": f"{failed}/{total} tests fallan despues de REFACTOR",
                "passed_count": passed,
                "failed_count": failed,
                "total_count": total,
            }

        return {
            "passed": True,
            "message": f"Todos los tests ({total}) siguen pasando despues de REFACTOR",
            "passed_count": passed,
            "total_count": total,
        }

    @staticmethod
    def _validate_minimum_coverage(execution_log: Dict) -> Dict:
        """Valida cobertura minima de tests."""
        metrics = execution_log.get("metrics", {})
        coverage = metrics.get("coverage", {})
        coverage_percent = coverage.get("percent", 0.0)

        threshold = TDDConstitution.RULES["MINIMUM_COVERAGE"].threshold

        if coverage_percent < threshold:
            return {
                "passed": False,
                "message": f"Cobertura {coverage_percent:.1f}% es menor que threshold {threshold}%",
                "coverage_percent": coverage_percent,
                "threshold": threshold,
            }

        return {
            "passed": True,
            "message": f"Cobertura {coverage_percent:.1f}% cumple threshold {threshold}%",
            "coverage_percent": coverage_percent,
            "threshold": threshold,
        }

    @staticmethod
    def _validate_no_security_issues(execution_log: Dict) -> Dict:
        """Valida que no hay vulnerabilidades de seguridad."""
        metrics = execution_log.get("metrics", {})
        security = metrics.get("security", {})
        issues_count = security.get("issues_count", 0)

        if issues_count > 0:
            return {
                "passed": False,
                "message": f"Se encontraron {issues_count} vulnerabilidades de seguridad",
                "issues_count": issues_count,
                "issues": security.get("issues", []),
            }

        return {
            "passed": True,
            "message": "No se encontraron vulnerabilidades de seguridad",
            "issues_count": 0,
        }

    @staticmethod
    def _validate_code_quality_passing(execution_log: Dict) -> Dict:
        """Valida que el codigo pasa verificaciones de calidad."""
        metrics = execution_log.get("metrics", {})
        quality = metrics.get("quality", {})

        linting_passed = quality.get("linting_passed", False)
        type_check_passed = quality.get("type_check_passed", False)

        if not linting_passed or not type_check_passed:
            return {
                "passed": False,
                "message": "Codigo no pasa verificaciones de calidad",
                "linting_passed": linting_passed,
                "type_check_passed": type_check_passed,
            }

        return {
            "passed": True,
            "message": "Codigo pasa todas las verificaciones de calidad",
            "linting_passed": linting_passed,
            "type_check_passed": type_check_passed,
        }

    @staticmethod
    def _validate_documentation_required(execution_log: Dict) -> Dict:
        """Valida que funciones publicas tienen docstrings."""
        metrics = execution_log.get("metrics", {})
        documentation = metrics.get("documentation", {})

        missing_docstrings = documentation.get("missing_docstrings", [])
        total_public_functions = documentation.get("total_public_functions", 0)

        if len(missing_docstrings) > 0:
            return {
                "passed": False,
                "message": f"{len(missing_docstrings)}/{total_public_functions} funciones publicas sin docstrings",
                "missing_count": len(missing_docstrings),
                "total_functions": total_public_functions,
                "missing_functions": missing_docstrings,
            }

        return {
            "passed": True,
            "message": f"Todas las funciones publicas ({total_public_functions}) tienen docstrings",
            "missing_count": 0,
            "total_functions": total_public_functions,
        }

    @staticmethod
    def _calculate_compliance_score(
        violations: List[ConstitutionViolation],
        evidence: Dict[str, Dict],
    ) -> float:
        """
        Calcula score de compliance (0-100).

        Pesos por severidad:
        - CRITICAL: 40 puntos (10 por regla)
        - HIGH: 30 puntos (15 por regla)
        - MEDIUM: 30 puntos (7.5 por regla)

        Total: 100 puntos
        """
        score = 100.0

        # Deducir puntos por violaciones
        for violation in violations:
            if violation.severity == Severity.CRITICAL:
                score -= 10.0  # 4 reglas CRITICAL x 10 = 40 puntos
            elif violation.severity == Severity.HIGH:
                score -= 15.0  # 2 reglas HIGH x 15 = 30 puntos
            elif violation.severity == Severity.MEDIUM:
                score -= 7.5   # 4 reglas MEDIUM x 7.5 = 30 puntos

        # Asegurar que score no sea negativo
        score = max(0.0, score)

        return round(score, 1)
