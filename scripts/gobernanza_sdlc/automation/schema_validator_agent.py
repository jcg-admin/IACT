"""
SchemaValidatorAgent: YAML/JSON schema validation for automation configs.

This agent validates .constitucion.yaml and .ci-local.yaml files against
their JSON schemas, checking syntax, schema compliance, and references.

Features:
- YAML/JSON syntax validation
- JSON Schema validation
- Reference validation (principle_id, stage dependencies)
- Type checking (severity, booleans, numbers)
- CLI interface with exit codes
- JSON output format

Author: SDLC Agent
Date: 2025-11-13
ADR: docs/adr/ADR-040-schema-validator-agent.md
Architecture: docs/devops/automatizacion/planificacion/AUTOMATION_ARCHITECTURE.md

TDD Implementation:
This module has been rebuilt using strict TDD methodology.
Each feature was developed following RED-GREEN-REFACTOR cycles.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    import jsonschema
    from jsonschema import validate, ValidationError as JsonSchemaValidationError
except ImportError:
    jsonschema = None
    JsonSchemaValidationError = Exception


class ExitCode(IntEnum):
    """Exit codes for CLI interface."""
    VALID = 0
    INVALID = 1
    CONFIG_ERROR = 3


@dataclass
class ValidationError:
    """Represents a validation error."""
    type: str  # syntax, schema, reference, type
    message: str
    location: Optional[str] = None
    field: Optional[str] = None
    severity: str = "error"  # error, warning

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "message": self.message,
            "location": self.location,
            "field": self.field,
            "severity": self.severity
        }


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    file_path: str
    file_type: str  # yaml, json
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    syntax_valid: bool = True
    schema_valid: bool = True
    references_valid: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "status": "valid" if self.is_valid else "invalid",
            "is_valid": self.is_valid,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "errors": [err.to_dict() for err in self.errors],
            "warnings": [warn.to_dict() for warn in self.warnings],
            "summary": {
                "syntax_valid": self.syntax_valid,
                "schema_valid": self.schema_valid,
                "references_valid": self.references_valid,
                "total_checks": 3,
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings)
            },
            "timestamp": self.timestamp
        }


class SchemaValidatorAgent:
    """
    Agent for validating YAML/JSON schemas.

    Validates configuration files against JSON schemas and performs
    additional reference and type checking.

    Built using strict TDD methodology with RED-GREEN-REFACTOR cycles.
    """

    def __init__(self, name: str = "schema_validator", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SchemaValidatorAgent.

        Args:
            name: Agent name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    def validate_syntax(self, file_path: str) -> ValidationResult:
        """
        Validate YAML/JSON syntax.

        Args:
            file_path: Path to file to validate

        Returns:
            ValidationResult with syntax validation results

        TDD Cycle 1: RED-GREEN-REFACTOR
        - RED: Test fails with NotImplementedError
        - GREEN: Minimal implementation to pass tests
        - REFACTOR: Clean up implementation
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_type="unknown",
                syntax_valid=False,
                errors=[ValidationError(
                    type="syntax",
                    message=f"File not found: {file_path}",
                    severity="error"
                )]
            )

        # Determine file type by extension
        file_type = "yaml" if path.suffix in [".yaml", ".yml"] else "json"

        result = ValidationResult(
            is_valid=True,
            file_path=file_path,
            file_type=file_type
        )

        try:
            with open(path, 'r') as f:
                content = f.read()

            # Parse based on file type
            if file_type == "yaml":
                yaml.safe_load(content)
            else:  # json
                json.loads(content)

        except yaml.YAMLError as e:
            result.is_valid = False
            result.syntax_valid = False
            result.errors.append(ValidationError(
                type="syntax",
                message=f"YAML syntax error: {str(e)}",
                severity="error"
            ))
        except json.JSONDecodeError as e:
            result.is_valid = False
            result.syntax_valid = False
            result.errors.append(ValidationError(
                type="syntax",
                message=f"JSON parse error: {str(e)}",
                location=f"line {e.lineno}, column {e.colno}",
                severity="error"
            ))
        except Exception as e:
            result.is_valid = False
            result.syntax_valid = False
            result.errors.append(ValidationError(
                type="syntax",
                message=f"Error reading file: {str(e)}",
                severity="error"
            ))

        return result

    def validate_schema(self, file_path: str, schema_path: str) -> ValidationResult:
        """
        Validate file against JSON schema.

        Args:
            file_path: Path to file to validate
            schema_path: Path to JSON schema file

        Returns:
            ValidationResult with schema validation results

        TDD Cycle 2: RED-GREEN-REFACTOR
        - RED: Test fails with NotImplementedError
        - GREEN: Implementation with JSON Schema validation
        - REFACTOR: Clean up and optimize
        """
        # Check if jsonschema is available
        if jsonschema is None:
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_type="unknown",
                schema_valid=False,
                errors=[ValidationError(
                    type="schema",
                    message="jsonschema library not available",
                    severity="error"
                )]
            )

        # First validate syntax
        syntax_result = self.validate_syntax(file_path)
        if not syntax_result.is_valid:
            return syntax_result

        # Load schema file
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_type=syntax_result.file_type,
                schema_valid=False,
                errors=[ValidationError(
                    type="schema",
                    message=f"Error loading schema: {str(e)}",
                    severity="error"
                )]
            )

        # Load data file
        try:
            with open(file_path, 'r') as f:
                if syntax_result.file_type == "yaml":
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_type=syntax_result.file_type,
                schema_valid=False,
                errors=[ValidationError(
                    type="schema",
                    message=f"Error loading data: {str(e)}",
                    severity="error"
                )]
            )

        result = ValidationResult(
            is_valid=True,
            file_path=file_path,
            file_type=syntax_result.file_type
        )

        # Validate against schema
        try:
            validate(instance=data, schema=schema)
        except JsonSchemaValidationError as e:
            result.is_valid = False
            result.schema_valid = False

            # Extract field path from error
            field_path = ".".join(str(p) for p in e.path) if e.path else "root"

            result.errors.append(ValidationError(
                type="schema",
                message=e.message,
                field=field_path,
                location=f"field: {field_path}",
                severity="error"
            ))
        except Exception as e:
            result.is_valid = False
            result.schema_valid = False
            result.errors.append(ValidationError(
                type="schema",
                message=f"Schema validation error: {str(e)}",
                severity="error"
            ))

        return result

    def validate_references(self, file_path: str, config_type: str) -> ValidationResult:
        """
        Validate references (principle_id, stage dependencies).

        Args:
            file_path: Path to file to validate
            config_type: Type of config ("constitucion" or "ci_local")

        Returns:
            ValidationResult with reference validation results

        TDD Cycle 3: RED-GREEN-REFACTOR
        - RED: Test fails with NotImplementedError
        - GREEN: Implementation with reference validation
        - REFACTOR: Extract helper methods
        """
        # First validate syntax
        syntax_result = self.validate_syntax(file_path)
        if not syntax_result.is_valid:
            return syntax_result

        # Load data
        try:
            with open(file_path, 'r') as f:
                if syntax_result.file_type == "yaml":
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_type=syntax_result.file_type,
                references_valid=False,
                errors=[ValidationError(
                    type="reference",
                    message=f"Error loading data: {str(e)}",
                    severity="error"
                )]
            )

        result = ValidationResult(
            is_valid=True,
            file_path=file_path,
            file_type=syntax_result.file_type
        )

        # Validate based on config type
        if config_type == "constitucion":
            result = self._validate_constitucion_references(data, result)
        elif config_type == "ci_local":
            result = self._validate_ci_local_references(data, result)

        return result

    def _validate_constitucion_references(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> ValidationResult:
        """
        Validate principle_id references in constitucion config.

        TDD Cycle 3.1: Constitucion reference validation
        - Validates that rules reference existing principles
        """
        # Extract principle IDs from principles section
        principles = data.get("principles", [])
        principle_ids = {p.get("principle_id") for p in principles if "principle_id" in p}

        # Validate rule references
        rules = data.get("rules", [])
        for i, rule in enumerate(rules):
            principle_id = rule.get("principle_id")
            if principle_id and principle_id not in principle_ids:
                result.is_valid = False
                result.references_valid = False
                result.errors.append(ValidationError(
                    type="reference",
                    message=f"Rule references non-existent principle: {principle_id}",
                    field=f"rules[{i}].principle_id",
                    severity="error"
                ))

        return result

    def _validate_ci_local_references(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> ValidationResult:
        """
        Validate stage dependencies in CI config.

        TDD Cycle 3.2: CI config reference validation
        - Validates that stage dependencies reference existing stages
        """
        # Extract stage names
        stages = data.get("stages", [])
        stage_names = {s.get("name") for s in stages if "name" in s}

        # Validate stage dependencies
        for i, stage in enumerate(stages):
            depends_on = stage.get("depends_on", [])
            for dependency in depends_on:
                if dependency not in stage_names:
                    result.is_valid = False
                    result.references_valid = False
                    result.errors.append(ValidationError(
                        type="reference",
                        message=f"Stage depends on non-existent stage: {dependency}",
                        field=f"stages[{i}].depends_on",
                        severity="error"
                    ))

        return result

    def validate_all(
        self,
        file_path: str,
        schema_path: str,
        config_type: str
    ) -> ValidationResult:
        """
        Perform all validations: syntax, schema, and references.

        Args:
            file_path: Path to file to validate
            schema_path: Path to JSON schema file
            config_type: Type of config ("constitucion" or "ci_local")

        Returns:
            ValidationResult with all validation results combined

        TDD Cycle 4.1: Integration validation
        - Combines syntax, schema, and reference validation
        """
        # Validate syntax first
        result = self.validate_syntax(file_path)
        if not result.syntax_valid:
            return result

        # Validate schema
        schema_result = self.validate_schema(file_path, schema_path)
        result.schema_valid = schema_result.schema_valid
        result.errors.extend(schema_result.errors)
        result.warnings.extend(schema_result.warnings)

        if not result.schema_valid:
            result.is_valid = False

        # Validate references (only if syntax and schema are valid)
        if result.syntax_valid and result.schema_valid:
            ref_result = self.validate_references(file_path, config_type)
            result.references_valid = ref_result.references_valid
            result.errors.extend(ref_result.errors)
            result.warnings.extend(ref_result.warnings)

            if not result.references_valid:
                result.is_valid = False

        return result

    def run_cli(self, args: List[str]) -> int:
        """
        Run CLI interface.

        Args:
            args: Command-line arguments

        Returns:
            Exit code (0=valid, 1=invalid, 3=config error)

        TDD Cycle 4.2: CLI interface
        - Parses arguments
        - Validates files
        - Returns appropriate exit codes
        """
        parser = argparse.ArgumentParser(
            description="Validate YAML/JSON schemas for automation configs"
        )
        parser.add_argument(
            "--file",
            required=True,
            help="Path to file to validate"
        )
        parser.add_argument(
            "--schema",
            required=True,
            help="Path to JSON schema file"
        )
        parser.add_argument(
            "--output",
            required=True,
            help="Path to output JSON report"
        )
        parser.add_argument(
            "--type",
            default="constitucion",
            choices=["constitucion", "ci_local"],
            help="Type of config file"
        )

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return ExitCode.CONFIG_ERROR

        # Check if files exist
        if not Path(parsed_args.file).exists():
            error_result = ValidationResult(
                is_valid=False,
                file_path=parsed_args.file,
                file_type="unknown",
                errors=[ValidationError(
                    type="config",
                    message=f"File not found: {parsed_args.file}",
                    severity="error"
                )]
            )

            # Write error output
            try:
                with open(parsed_args.output, 'w') as f:
                    json.dump(error_result.to_json(), f, indent=2)
            except Exception:
                pass

            return ExitCode.CONFIG_ERROR

        if not Path(parsed_args.schema).exists():
            error_result = ValidationResult(
                is_valid=False,
                file_path=parsed_args.file,
                file_type="unknown",
                errors=[ValidationError(
                    type="config",
                    message=f"Schema file not found: {parsed_args.schema}",
                    severity="error"
                )]
            )

            # Write error output
            try:
                with open(parsed_args.output, 'w') as f:
                    json.dump(error_result.to_json(), f, indent=2)
            except Exception:
                pass

            return ExitCode.CONFIG_ERROR

        # Perform validation
        result = self.validate_all(
            parsed_args.file,
            parsed_args.schema,
            parsed_args.type
        )

        # Write output
        try:
            with open(parsed_args.output, 'w') as f:
                json.dump(result.to_json(), f, indent=2)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return ExitCode.CONFIG_ERROR

        # Return appropriate exit code
        if result.is_valid:
            return ExitCode.VALID
        else:
            return ExitCode.INVALID


def main():
    """Main entry point for CLI."""
    agent = SchemaValidatorAgent()
    exit_code = agent.run_cli(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
