#!/usr/bin/env python3
"""
BusinessRulesValidatorAgent - Fase 1: Analisis y Requisitos

Agente de validacion de documentacion de reglas de negocio para garantizar
estructura correcta, categorizacion adecuada, ejemplos IACT y cumplimiento
con estandares del proyecto.

Tareas:
- Validar estructura de documentacion de reglas de negocio
- Verificar categorizacion de 5 tipos (Hechos, Restricciones, Triggers, Inferencias, Calculos)
- Validar matrices de roles y permisos
- Verificar presencia de ejemplos especificos IACT
- Validar referencias cruzadas entre documentos
- Garantizar cumplimiento con LFPDPPP

Autor: SDLC Agent
Fecha: 2025-11-14
Relacionado: docs/gobernanza/requisitos/REGLAS_NEGOCIO/, ADR_010_organizacion_proyecto_por_dominio.md
Arquitectura: docs/devops/automatizacion/planificacion/AUTOMATION_ARCHITECTURE.md
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
    type: str  # structure, categorization, example, reference, matrix
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
    """Result of business rules validation."""
    is_valid: bool
    directory_path: str
    files_checked: List[str] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    structure_valid: bool = True
    categorization_valid: bool = True
    examples_valid: bool = True
    references_valid: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "status": "valid" if self.is_valid else "invalid",
            "is_valid": self.is_valid,
            "directory_path": self.directory_path,
            "files_checked": self.files_checked,
            "errors": [err.to_dict() for err in self.errors],
            "warnings": [warn.to_dict() for warn in self.warnings],
            "info": [i.to_dict() for i in self.info],
            "summary": {
                "structure_valid": self.structure_valid,
                "categorization_valid": self.categorization_valid,
                "examples_valid": self.examples_valid,
                "references_valid": self.references_valid,
                "total_checks": 4,
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings),
                "info_count": len(self.info)
            },
            "timestamp": self.timestamp
        }


class BusinessRulesValidator:
    """Validator for business rules documentation."""

    REQUIRED_FILES = [
        "README.md",
        "INTRODUCCION.md",
        "HECHOS_RESTRICCIONES.md"
    ]

    OPTIONAL_FILES = [
        "TIPOS_AVANZADOS.md",
        "APLICACION_IACT.md"
    ]

    RULE_TYPES = {
        "Hechos": ["Facts", "Declaraciones verdaderas", "inmutables"],
        "Restricciones": ["Constraints", "debe", "no debe", "no puede", "solo puede"],
        "Desencadenadores": ["Triggers", "Activadores", "si.*entonces"],
        "Inferencias": ["Inferences", "derivar", "inferir"],
        "Cálculos": ["Computations", "fórmula", "algoritmo", "calcular"]
    }

    IACT_KEYWORDS = [
        "IACT", "IVR", "agente", "supervisor", "gerente",
        "llamada", "campaña", "call center", "LFPDPPP"
    ]

    def __init__(self, docs_dir: Path):
        """Initialize validator with documentation directory."""
        self.docs_dir = docs_dir
        self.result = ValidationResult(
            is_valid=True,
            directory_path=str(docs_dir)
        )

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        if not self.docs_dir.exists():
            self.result.errors.append(ValidationIssue(
                type="structure",
                message=f"Documentation directory not found: {self.docs_dir}",
                severity="error"
            ))
            self.result.is_valid = False
            self.result.structure_valid = False
            return self.result

        # Run validation checks
        self._validate_structure()
        self._validate_categorization()
        self._validate_examples()
        self._validate_references()
        self._validate_matrices()
        self._validate_use_case_traceability()

        # Determine overall validity
        self.result.is_valid = (
            self.result.structure_valid and
            self.result.categorization_valid and
            self.result.examples_valid and
            self.result.references_valid and
            len(self.result.errors) == 0
        )

        return self.result

    def _validate_structure(self) -> None:
        """Validate directory structure and required files."""
        for required_file in self.REQUIRED_FILES:
            file_path = self.docs_dir / required_file
            if not file_path.exists():
                self.result.errors.append(ValidationIssue(
                    type="structure",
                    message=f"Required file missing: {required_file}",
                    file=required_file,
                    severity="error"
                ))
                self.result.structure_valid = False
            else:
                self.result.files_checked.append(required_file)

        for optional_file in self.OPTIONAL_FILES:
            file_path = self.docs_dir / optional_file
            if not file_path.exists():
                self.result.warnings.append(ValidationIssue(
                    type="structure",
                    message=f"Optional file missing: {optional_file}",
                    file=optional_file,
                    severity="warning"
                ))
            else:
                self.result.files_checked.append(optional_file)

    def _validate_categorization(self) -> None:
        """Validate that business rules are properly categorized."""
        # Check HECHOS_RESTRICCIONES.md for Facts and Constraints
        hechos_file = self.docs_dir / "HECHOS_RESTRICCIONES.md"
        if hechos_file.exists():
            content = hechos_file.read_text(encoding='utf-8')

            # Check for Facts section
            if "## 1. HECHOS" not in content and "## HECHOS" not in content:
                self.result.errors.append(ValidationIssue(
                    type="categorization",
                    message="Missing 'Hechos (Facts)' section",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="error"
                ))
                self.result.categorization_valid = False

            # Check for Constraints section
            if "## 2. RESTRICCIONES" not in content and "## RESTRICCIONES" not in content:
                self.result.errors.append(ValidationIssue(
                    type="categorization",
                    message="Missing 'Restricciones (Constraints)' section",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="error"
                ))
                self.result.categorization_valid = False

            # Check for constraint keywords
            constraint_keywords = ["debe", "no debe", "no puede", "solo puede"]
            found_keywords = sum(1 for kw in constraint_keywords if kw in content)
            if found_keywords == 0:
                self.result.warnings.append(ValidationIssue(
                    type="categorization",
                    message="No constraint keywords found (debe, no debe, no puede, solo puede)",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="warning"
                ))

        # Check TIPOS_AVANZADOS.md for advanced types (if it exists)
        tipos_file = self.docs_dir / "TIPOS_AVANZADOS.md"
        if tipos_file.exists():
            content = tipos_file.read_text(encoding='utf-8')

            advanced_types = ["Desencadenadores", "Inferencias", "Cálculos"]
            for rule_type in advanced_types:
                if rule_type.lower() not in content.lower():
                    self.result.warnings.append(ValidationIssue(
                        type="categorization",
                        message=f"Missing '{rule_type}' section in advanced types",
                        file="TIPOS_AVANZADOS.md",
                        severity="warning"
                    ))

    def _validate_examples(self) -> None:
        """Validate presence of IACT-specific examples."""
        for file_name in self.result.files_checked:
            file_path = self.docs_dir / file_name
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')

                # Check for IACT keywords
                found_keywords = [kw for kw in self.IACT_KEYWORDS if kw in content]

                if len(found_keywords) == 0:
                    self.result.warnings.append(ValidationIssue(
                        type="example",
                        message=f"No IACT-specific examples found",
                        file=file_name,
                        severity="warning"
                    ))
                else:
                    self.result.info.append(ValidationIssue(
                        type="example",
                        message=f"Found {len(found_keywords)} IACT keywords: {', '.join(found_keywords[:3])}",
                        file=file_name,
                        severity="info"
                    ))

                # Check for LFPDPPP compliance references
                if "LFPDPPP" in content or "protección de datos" in content.lower():
                    self.result.info.append(ValidationIssue(
                        type="example",
                        message="Contains LFPDPPP compliance references",
                        file=file_name,
                        severity="info"
                    ))

    def _validate_references(self) -> None:
        """Validate cross-references between documents."""
        for file_name in self.result.files_checked:
            file_path = self.docs_dir / file_name
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')

                # Find markdown links
                links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

                for link_text, link_path in links:
                    # Skip external links and anchors
                    if link_path.startswith('http') or link_path.startswith('#'):
                        continue

                    # Check if referenced file exists (relative to docs_dir)
                    if link_path.endswith('.md') or link_path.endswith('.yaml'):
                        # Handle relative paths
                        if link_path.startswith('..'):
                            # Skip validation for parent directory references
                            # (would need full project context)
                            continue

                        referenced_file = self.docs_dir / link_path
                        if not referenced_file.exists():
                            self.result.warnings.append(ValidationIssue(
                                type="reference",
                                message=f"Referenced file not found: {link_path}",
                                file=file_name,
                                severity="warning"
                            ))

    def _validate_matrices(self) -> None:
        """Validate role-permission matrices structure."""
        hechos_file = self.docs_dir / "HECHOS_RESTRICCIONES.md"
        if hechos_file.exists():
            content = hechos_file.read_text(encoding='utf-8')

            # Check for matrix section
            if "Matriz de Roles y Permisos" not in content:
                self.result.warnings.append(ValidationIssue(
                    type="matrix",
                    message="Missing 'Matriz de Roles y Permisos' section",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="warning"
                ))
                return

            # Check for role keywords
            roles = ["AGENTE", "SUPERVISOR", "GERENTE", "ADMIN"]
            found_roles = [role for role in roles if role in content]

            if len(found_roles) < 3:
                self.result.warnings.append(ValidationIssue(
                    type="matrix",
                    message=f"Role-permission matrix may be incomplete. Found roles: {', '.join(found_roles)}",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="warning"
                ))
            else:
                self.result.info.append(ValidationIssue(
                    type="matrix",
                    message=f"Role-permission matrix found with {len(found_roles)} roles",
                    file="HECHOS_RESTRICCIONES.md",
                    severity="info"
                ))

    def _validate_use_case_traceability(self) -> None:
        """Validate traceability between business rules and use cases."""
        # Look for use cases directory
        use_cases_dir = self.docs_dir.parent.parent / "casos_de_uso"

        if not use_cases_dir.exists():
            self.result.info.append(ValidationIssue(
                type="traceability",
                message="Use cases directory not found. Skipping traceability validation.",
                severity="info"
            ))
            return

        # Find all use case files
        use_case_files = list(use_cases_dir.glob("UC-*.md"))

        if len(use_case_files) == 0:
            self.result.warnings.append(ValidationIssue(
                type="traceability",
                message="No use case files found in casos_de_uso/",
                severity="warning"
            ))
            return

        # Extract business rule IDs from use cases
        br_references_in_ucs = set()
        ucs_with_br = []

        for uc_file in use_case_files:
            content = uc_file.read_text(encoding='utf-8')

            # Find BR-XXX references
            br_pattern = r'BR-[A-Z]\d+'
            found_brs = re.findall(br_pattern, content)

            if found_brs:
                br_references_in_ucs.update(found_brs)
                ucs_with_br.append(uc_file.name)

        # Report findings
        if len(ucs_with_br) > 0:
            self.result.info.append(ValidationIssue(
                type="traceability",
                message=f"Found {len(ucs_with_br)} use cases referencing business rules: {', '.join(ucs_with_br[:3])}{'...' if len(ucs_with_br) > 3 else ''}",
                severity="info"
            ))

            self.result.info.append(ValidationIssue(
                type="traceability",
                message=f"Use cases reference {len(br_references_in_ucs)} unique business rules: {', '.join(sorted(list(br_references_in_ucs))[:5])}{'...' if len(br_references_in_ucs) > 5 else ''}",
                severity="info"
            ))
        else:
            self.result.warnings.append(ValidationIssue(
                type="traceability",
                message=f"Found {len(use_case_files)} use case files but none reference business rules (BR-XXX)",
                severity="warning"
            ))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate business rules documentation structure and content"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs/gobernanza/requisitos/REGLAS_NEGOCIO"),
        help="Path to business rules documentation directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file path (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = BusinessRulesValidator(args.docs_dir)

    # Run validation
    result = validator.validate()

    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result.to_json(), f, indent=2, ensure_ascii=False)
        print(f"Validation results written to: {args.output}")
    else:
        print(json.dumps(result.to_json(), indent=2, ensure_ascii=False))

    # Print summary to stderr if verbose
    if args.verbose:
        print("\n=== Validation Summary ===", file=sys.stderr)
        print(f"Status: {'VALID' if result.is_valid else 'INVALID'}", file=sys.stderr)
        print(f"Files checked: {len(result.files_checked)}", file=sys.stderr)
        print(f"Errors: {len(result.errors)}", file=sys.stderr)
        print(f"Warnings: {len(result.warnings)}", file=sys.stderr)
        print(f"Info: {len(result.info)}", file=sys.stderr)

        if result.errors:
            print("\n=== Errors ===", file=sys.stderr)
            for error in result.errors:
                print(f"  [{error.type}] {error.message} ({error.file})", file=sys.stderr)

        if result.warnings:
            print("\n=== Warnings ===", file=sys.stderr)
            for warning in result.warnings:
                print(f"  [{warning.type}] {warning.message} ({warning.file})", file=sys.stderr)

    # Return exit code
    return ExitCode.VALID if result.is_valid else ExitCode.INVALID


if __name__ == "__main__":
    sys.exit(main())
