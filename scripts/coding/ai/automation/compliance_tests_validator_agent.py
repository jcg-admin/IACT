#!/usr/bin/env python3
"""
ComplianceTestsValidatorAgent - Fase 1: Analisis y Requisitos

Agente de validacion de especificaciones de tests de compliance para garantizar
cobertura completa de reglas de negocio, nombres siguiendo Clean Code, y
estructura correcta de tests por niveles (unit, integration, e2e).

Tareas:
- Validar cobertura de reglas de negocio (BR-R**, BR-H**, etc.)
- Verificar estructura Given/When/Then en especificaciones
- Validar nombres de tests (Clean Code: concisos, pronunciables, sin codificaciones)
- Verificar organizacion por niveles (unit, integration, e2e)
- Garantizar independencia de framework en tests unitarios
- Validar criterios de aceptacion y metricas de compliance

Autor: SDLC Agent
Fecha: 2025-11-14
Relacionado: docs/gobernanza/requisitos/REGLAS_NEGOCIO/ESPECIFICACION_TESTS_COMPLIANCE.md
Arquitectura: docs/devops/automatizacion/planificacion/AGENTS_ARCHITECTURE.md
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ExitCode(IntEnum):
    """Exit codes for CLI interface."""
    VALID = 0
    INVALID = 1
    FILE_NOT_FOUND = 2
    CONFIG_ERROR = 3


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    type: str  # coverage, structure, naming, levels, framework_independence
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    severity: str = "error"  # error, warning, info

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "severity": self.severity
        }


@dataclass
class ValidationResult:
    """Result of compliance tests validation."""
    is_valid: bool
    spec_file_path: str
    tests_found: int = 0
    rules_covered: Set[str] = field(default_factory=set)
    rules_missing: Set[str] = field(default_factory=set)
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    coverage_valid: bool = True
    structure_valid: bool = True
    naming_valid: bool = True
    levels_valid: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "status": "valid" if self.is_valid else "invalid",
            "is_valid": self.is_valid,
            "spec_file_path": self.spec_file_path,
            "tests_found": self.tests_found,
            "rules_covered": sorted(list(self.rules_covered)),
            "rules_missing": sorted(list(self.rules_missing)),
            "errors": [err.to_dict() for err in self.errors],
            "warnings": [warn.to_dict() for warn in self.warnings],
            "info": [i.to_dict() for i in self.info],
            "summary": {
                "coverage_valid": self.coverage_valid,
                "structure_valid": self.structure_valid,
                "naming_valid": self.naming_valid,
                "levels_valid": self.levels_valid,
                "total_checks": 4,
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings),
                "info_count": len(self.info),
                "coverage_percentage": len(self.rules_covered) / (len(self.rules_covered) + len(self.rules_missing)) * 100 if (self.rules_covered or self.rules_missing) else 100
            },
            "timestamp": self.timestamp
        }


class ComplianceTestsValidatorAgent:
    """Validates compliance test specifications."""

    def __init__(
        self,
        spec_file: Path,
        check_coverage: bool = True,
        check_structure: bool = True,
        check_naming: bool = True,
        check_levels: bool = True,
        output_format: str = "json"
    ):
        """Initialize validator."""
        self.spec_file = spec_file
        self.check_coverage = check_coverage
        self.check_structure = check_structure
        self.check_naming = check_naming
        self.check_levels = check_levels
        self.output_format = output_format

        # Expected business rules from REGLAS_NEGOCIO docs
        self.expected_rules = {
            "BR-R08",  # Grabaciones requieren consentimiento
            "BR-R11",  # Datos personales encriptados
            "BR-R12",  # Acceso a datos auditado
            "BR-R13",  # Retención de datos
        }

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult(
            is_valid=True,
            spec_file_path=str(self.spec_file)
        )

        if not self.spec_file.exists():
            result.is_valid = False
            result.errors.append(ValidationIssue(
                type="file",
                message=f"Specification file not found: {self.spec_file}",
                severity="error"
            ))
            return result

        content = self.spec_file.read_text(encoding='utf-8')

        if self.check_coverage:
            self._validate_coverage(content, result)

        if self.check_structure:
            self._validate_structure(content, result)

        if self.check_naming:
            self._validate_naming(content, result)

        if self.check_levels:
            self._validate_levels(content, result)

        # Update overall validity
        result.is_valid = (
            result.coverage_valid and
            result.structure_valid and
            result.naming_valid and
            result.levels_valid and
            len(result.errors) == 0
        )

        return result

    def _validate_coverage(self, content: str, result: ValidationResult) -> None:
        """Validate that all expected business rules have test specifications."""
        # Find all BR-XXX references in content
        br_pattern = r'BR-[A-Z]\d+'
        found_rules = set(re.findall(br_pattern, content))

        result.rules_covered = found_rules.intersection(self.expected_rules)
        result.rules_missing = self.expected_rules - found_rules

        if result.rules_missing:
            result.coverage_valid = False
            result.errors.append(ValidationIssue(
                type="coverage",
                message=f"Missing test specifications for rules: {', '.join(sorted(result.rules_missing))}",
                file=str(self.spec_file),
                severity="error"
            ))
        else:
            result.info.append(ValidationIssue(
                type="coverage",
                message=f"All {len(self.expected_rules)} expected rules have test coverage",
                file=str(self.spec_file),
                severity="info"
            ))

    def _validate_structure(self, content: str, result: ValidationResult) -> None:
        """Validate Given/When/Then structure in test specifications."""
        # Find test specifications (under "**Test Specification:**" sections)
        spec_sections = re.findall(
            r'\*\*Test Specification:\*\*\s*```python\s*(.*?)```',
            content,
            re.DOTALL
        )

        test_count = 0
        for section in spec_sections:
            # Find all test function definitions in this spec section
            test_pattern = r'def (test_\w+)\([^)]*\):\s*"""([^"]+)"""'
            tests = re.findall(test_pattern, section, re.MULTILINE | re.DOTALL)

            for test_name, docstring in tests:
                test_count += 1
                # Check for Given/When/Then structure
                has_given = 'Given' in docstring
                has_when = 'When' in docstring
                has_then = 'Then' in docstring

                if not (has_given and has_when and has_then):
                    result.structure_valid = False
                    result.errors.append(ValidationIssue(
                        type="structure",
                        message=f"Test '{test_name}' missing Given/When/Then structure in specification",
                        file=str(self.spec_file),
                        severity="error"
                    ))

        result.tests_found = test_count

        if test_count == 0:
            result.structure_valid = False
            result.errors.append(ValidationIssue(
                type="structure",
                message="No test specifications found with Given/When/Then structure",
                file=str(self.spec_file),
                severity="error"
            ))

    def _validate_naming(self, content: str, result: ValidationResult) -> None:
        """Validate test naming follows Clean Code principles."""
        # Find test specifications (under "**Test Specification:**" sections)
        spec_sections = re.findall(
            r'\*\*Test Specification:\*\*\s*```python\s*(.*?)```',
            content,
            re.DOTALL
        )

        for section in spec_sections:
            # Find all test function names in spec sections
            test_pattern = r'def (test_\w+)\('
            test_names = re.findall(test_pattern, section)

            for test_name in test_names:
                # Check for codifications (BR-XXX in name)
                if re.search(r'br_[a-z]\d+', test_name, re.IGNORECASE):
                    result.naming_valid = False
                    result.errors.append(ValidationIssue(
                        type="naming",
                        message=f"Test '{test_name}' contains codification (BR-XXX). Use descriptive name instead",
                        file=str(self.spec_file),
                        severity="error"
                    ))

                # Check for excessive length (>50 chars = dissertation)
                if len(test_name) > 50:
                    result.naming_valid = False
                    result.warnings.append(ValidationIssue(
                        type="naming",
                        message=f"Test '{test_name}' too long ({len(test_name)} chars). Keep names concise (<50 chars)",
                        file=str(self.spec_file),
                        severity="warning"
                    ))

                # Check for underscores (should be readable)
                parts = test_name.replace('test_', '').split('_')
                if len(parts) > 6:
                    result.warnings.append(ValidationIssue(
                        type="naming",
                        message=f"Test '{test_name}' has too many parts ({len(parts)}). Consider simplifying",
                        file=str(self.spec_file),
                        severity="warning"
                    ))

    def _validate_levels(self, content: str, result: ValidationResult) -> None:
        """Validate test organization by levels (unit, integration, e2e)."""
        required_levels = [
            ("Nivel 1: Tests Unitarios", "unit"),
            ("Nivel 2: Tests de Integración", "integration"),
            ("Nivel 3: Tests End-to-End", "e2e")
        ]

        for level_header, level_type in required_levels:
            if level_header not in content:
                result.levels_valid = False
                result.errors.append(ValidationIssue(
                    type="levels",
                    message=f"Missing '{level_header}' section",
                    file=str(self.spec_file),
                    severity="error"
                ))

        # Validate framework independence for unit tests
        if "Nivel 1" in content:
            unit_section_match = re.search(
                r'### Nivel 1.*?(?=### Nivel 2|---|\Z)',
                content,
                re.DOTALL
            )
            if unit_section_match:
                unit_section = unit_section_match.group(0)

                # Check for framework dependencies
                framework_indicators = ['django', 'pytest.mark.django_db', 'APIClient', 'models.Model']
                for indicator in framework_indicators:
                    if indicator in unit_section:
                        result.warnings.append(ValidationIssue(
                            type="framework_independence",
                            message=f"Unit tests section contains '{indicator}' - should be framework-independent",
                            file=str(self.spec_file),
                            severity="warning"
                        ))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate compliance test specifications"
    )
    parser.add_argument(
        "--spec-file",
        type=Path,
        default=Path("docs/gobernanza/requisitos/REGLAS_NEGOCIO/ESPECIFICACION_TESTS_COMPLIANCE.md"),
        help="Path to test specification file"
    )
    parser.add_argument(
        "--check-coverage",
        action="store_true",
        default=True,
        help="Check business rule coverage"
    )
    parser.add_argument(
        "--check-structure",
        action="store_true",
        default=True,
        help="Check Given/When/Then structure"
    )
    parser.add_argument(
        "--check-naming",
        action="store_true",
        default=True,
        help="Check Clean Code naming conventions"
    )
    parser.add_argument(
        "--check-levels",
        action="store_true",
        default=True,
        help="Check test level organization"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    validator = ComplianceTestsValidatorAgent(
        spec_file=args.spec_file,
        check_coverage=args.check_coverage,
        check_structure=args.check_structure,
        check_naming=args.check_naming,
        check_levels=args.check_levels,
        output_format=args.output_format
    )

    result = validator.validate()

    if args.output_format == "json":
        print(json.dumps(result.to_json(), indent=2))
    else:
        # Text output
        print(f"Compliance Tests Validation: {'PASS' if result.is_valid else 'FAIL'}")
        print(f"Spec file: {result.spec_file_path}")
        print(f"Tests found: {result.tests_found}")
        print(f"Rules covered: {len(result.rules_covered)}/{len(result.rules_covered) + len(result.rules_missing)}")

        if result.errors:
            print("\nErrors:")
            for err in result.errors:
                print(f"  [{err.type}] {err.message}")

        if result.warnings:
            print("\nWarnings:")
            for warn in result.warnings:
                print(f"  [{warn.type}] {warn.message}")

    return ExitCode.VALID if result.is_valid else ExitCode.INVALID


if __name__ == "__main__":
    sys.exit(main())
