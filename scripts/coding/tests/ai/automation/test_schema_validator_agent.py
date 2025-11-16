"""
Comprehensive tests for SchemaValidatorAgent following TDD approach.

Test Coverage:
- YAML/JSON syntax validation
- Schema validation (JSON Schema)
- Reference validation (principle_id, dependencies)
- Type checking (severity, booleans, numbers)
- CLI interface
- Exit codes
- JSON output format

Author: SDLC Agent
Date: 2025-11-13
ADR: docs/adr/ADR-040-schema-validator-agent.md
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.coding.ai.automation.schema_validator_agent import (
    SchemaValidatorAgent,
    ValidationResult,
    ValidationError,
    ExitCode
)


class TestSchemaValidatorAgent:
    """Test suite for SchemaValidatorAgent."""

    @pytest.fixture
    def agent(self):
        """Create SchemaValidatorAgent instance."""
        return SchemaValidatorAgent(name="schema_validator_test")

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    # ==================================================================
    # YAML SYNTAX VALIDATION TESTS
    # ==================================================================

    def test_validate_yaml_syntax_valid(self, agent, fixtures_dir):
        """Test validation of valid YAML syntax."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"

        result = agent.validate_syntax(str(yaml_file))

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.file_type == "yaml"

    def test_validate_yaml_syntax_invalid(self, agent, fixtures_dir):
        """Test detection of invalid YAML syntax."""
        yaml_file = fixtures_dir / "sample_invalid_syntax.yaml"

        result = agent.validate_syntax(str(yaml_file))

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("syntax" in err.message.lower() for err in result.errors)

    # ==================================================================
    # JSON SYNTAX VALIDATION TESTS
    # ==================================================================

    def test_validate_json_syntax_valid(self, agent, fixtures_dir):
        """Test validation of valid JSON syntax."""
        json_file = fixtures_dir / "sample_valid.json"

        result = agent.validate_syntax(str(json_file))

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.file_type == "json"

    def test_validate_json_syntax_invalid(self, agent, fixtures_dir):
        """Test detection of invalid JSON syntax."""
        json_file = fixtures_dir / "sample_invalid_syntax.json"

        result = agent.validate_syntax(str(json_file))

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("syntax" in err.message.lower() or "parse" in err.message.lower()
                   for err in result.errors)

    # ==================================================================
    # SCHEMA VALIDATION TESTS
    # ==================================================================

    def test_schema_validation_success(self, agent, fixtures_dir):
        """Test successful schema validation."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_schema(str(yaml_file), str(schema_file))

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_schema_validation_failure(self, agent, fixtures_dir):
        """Test schema validation with invalid data."""
        yaml_file = fixtures_dir / "sample_constitucion_invalid.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_schema(str(yaml_file), str(schema_file))

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_detect_missing_required_fields(self, agent):
        """Test detection of missing required fields."""
        # Create temporary YAML with missing required fields
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("---\nversion: '1.0'\n")
            temp_file = f.name

        try:
            schema = {
                "type": "object",
                "required": ["version", "project", "rules"],
                "properties": {
                    "version": {"type": "string"},
                    "project": {"type": "string"},
                    "rules": {"type": "array"}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(schema, f)
                schema_file = f.name

            try:
                result = agent.validate_schema(temp_file, schema_file)

                assert result.is_valid is False
                assert any("required" in err.message.lower() for err in result.errors)
            finally:
                os.unlink(schema_file)
        finally:
            os.unlink(temp_file)

    # ==================================================================
    # TYPE CHECKING TESTS
    # ==================================================================

    def test_detect_invalid_severity(self, agent, fixtures_dir):
        """Test detection of invalid severity values."""
        yaml_file = fixtures_dir / "sample_constitucion_invalid.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_schema(str(yaml_file), str(schema_file))

        assert result.is_valid is False
        # Should detect "critical" and "invalid_severity" as invalid
        assert any("severity" in err.message.lower() or "enum" in err.message.lower()
                   for err in result.errors)

    def test_validate_type_checking(self, agent):
        """Test type checking for various data types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("---\npipeline:\n  fail_fast: 'not_a_boolean'\n  timeout: 'not_a_number'\n")
            temp_file = f.name

        try:
            schema = {
                "type": "object",
                "properties": {
                    "pipeline": {
                        "type": "object",
                        "properties": {
                            "fail_fast": {"type": "boolean"},
                            "timeout": {"type": "number"}
                        }
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(schema, f)
                schema_file = f.name

            try:
                result = agent.validate_schema(temp_file, schema_file)

                assert result.is_valid is False
                assert len(result.errors) >= 1  # At least 1 type error detected
                assert any("type" in err.message.lower() for err in result.errors)
            finally:
                os.unlink(schema_file)
        finally:
            os.unlink(temp_file)

    # ==================================================================
    # REFERENCE VALIDATION TESTS
    # ==================================================================

    def test_validate_principle_references(self, agent, fixtures_dir):
        """Test validation that principle_id references exist."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"

        result = agent.validate_references(str(yaml_file), "constitucion")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_principle_references_missing(self, agent, fixtures_dir):
        """Test detection of missing principle_id references."""
        yaml_file = fixtures_dir / "sample_constitucion_invalid.yaml"

        result = agent.validate_references(str(yaml_file), "constitucion")

        assert result.is_valid is False
        # Should detect P999 as non-existent
        assert any("P999" in err.message or "principle" in err.message.lower()
                   for err in result.errors)

    def test_validate_stage_dependencies(self, agent, fixtures_dir):
        """Test validation of stage dependencies in CI config."""
        yaml_file = fixtures_dir / "sample_ci_local_invalid.yaml"

        result = agent.validate_references(str(yaml_file), "ci_local")

        assert result.is_valid is False
        # Should detect nonexistent_stage as invalid dependency
        assert any("nonexistent_stage" in err.message or "dependency" in err.message.lower()
                   for err in result.errors)

    # ==================================================================
    # CLI INTERFACE TESTS
    # ==================================================================

    def test_cli_interface_valid_file(self, agent, fixtures_dir):
        """Test CLI interface with valid file."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            args = [
                "--file", str(yaml_file),
                "--schema", str(schema_file),
                "--output", output_file
            ]

            exit_code = agent.run_cli(args)

            assert exit_code == ExitCode.VALID
            assert os.path.exists(output_file)

            # Verify output JSON
            with open(output_file, 'r') as f:
                output_data = json.load(f)

            assert output_data["status"] == "valid"
            assert output_data["is_valid"] is True
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_cli_interface_missing_file(self, agent):
        """Test CLI interface with missing file."""
        args = [
            "--file", "/nonexistent/file.yaml",
            "--schema", "/nonexistent/schema.json",
            "--output", "/tmp/output.json"
        ]

        exit_code = agent.run_cli(args)

        assert exit_code == ExitCode.CONFIG_ERROR

    def test_cli_interface_missing_arguments(self, agent):
        """Test CLI interface with missing required arguments."""
        args = ["--file", "/some/file.yaml"]  # Missing --schema

        exit_code = agent.run_cli(args)

        assert exit_code == ExitCode.CONFIG_ERROR

    # ==================================================================
    # JSON OUTPUT FORMAT TESTS
    # ==================================================================

    def test_json_output_format(self, agent, fixtures_dir):
        """Test JSON output format structure."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_all(str(yaml_file), str(schema_file), "constitucion")
        output = result.to_json()

        # Verify required fields in JSON output
        assert "status" in output
        assert "is_valid" in output
        assert "file_path" in output
        assert "errors" in output
        assert "warnings" in output
        assert "summary" in output
        assert "timestamp" in output

        # Verify types
        assert isinstance(output["is_valid"], bool)
        assert isinstance(output["errors"], list)
        assert isinstance(output["warnings"], list)
        assert isinstance(output["summary"], dict)

    def test_json_output_with_errors(self, agent, fixtures_dir):
        """Test JSON output format with validation errors."""
        yaml_file = fixtures_dir / "sample_constitucion_invalid.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_all(str(yaml_file), str(schema_file), "constitucion")
        output = result.to_json()

        assert output["is_valid"] is False
        assert len(output["errors"]) > 0

        # Verify error structure
        for error in output["errors"]:
            assert "type" in error
            assert "message" in error
            assert "location" in error or "field" in error

    # ==================================================================
    # EXIT CODE TESTS
    # ==================================================================

    def test_exit_codes_valid(self, agent, fixtures_dir):
        """Test exit code 0 for valid file."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            args = [
                "--file", str(yaml_file),
                "--schema", str(schema_file),
                "--output", output_file
            ]

            exit_code = agent.run_cli(args)

            assert exit_code == ExitCode.VALID
            assert exit_code == 0
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_exit_codes_invalid(self, agent, fixtures_dir):
        """Test exit code 1 for invalid file."""
        yaml_file = fixtures_dir / "sample_constitucion_invalid.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            args = [
                "--file", str(yaml_file),
                "--schema", str(schema_file),
                "--output", output_file
            ]

            exit_code = agent.run_cli(args)

            assert exit_code == ExitCode.INVALID
            assert exit_code == 1
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_exit_codes_config_error(self, agent):
        """Test exit code 3 for configuration errors."""
        args = [
            "--file", "/nonexistent/file.yaml",
            "--schema", "/nonexistent/schema.json",
            "--output", "/tmp/output.json"
        ]

        exit_code = agent.run_cli(args)

        assert exit_code == ExitCode.CONFIG_ERROR
        assert exit_code == 3

    # ==================================================================
    # INTEGRATION TESTS
    # ==================================================================

    def test_validate_all_integration(self, agent, fixtures_dir):
        """Integration test: validate all aspects of a file."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_all(str(yaml_file), str(schema_file), "constitucion")

        assert result.is_valid is True
        assert result.syntax_valid is True
        assert result.schema_valid is True
        assert result.references_valid is True

    def test_validate_all_with_multiple_errors(self, agent, fixtures_dir):
        """Integration test: file with syntax, schema, and reference errors."""
        yaml_file = fixtures_dir / "sample_invalid_syntax.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        result = agent.validate_all(str(yaml_file), str(schema_file), "constitucion")

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_end_to_end_cli_workflow(self, agent, fixtures_dir):
        """End-to-end test: full CLI workflow."""
        yaml_file = fixtures_dir / "sample_constitucion.yaml"
        schema_file = fixtures_dir / "constitucion_schema.json"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            # Run full CLI
            args = [
                "--file", str(yaml_file),
                "--schema", str(schema_file),
                "--output", output_file,
                "--type", "constitucion"
            ]

            exit_code = agent.run_cli(args)

            # Verify exit code
            assert exit_code == ExitCode.VALID

            # Verify output file exists and has correct format
            assert os.path.exists(output_file)

            with open(output_file, 'r') as f:
                output_data = json.load(f)

            assert output_data["status"] == "valid"
            assert output_data["is_valid"] is True
            assert "summary" in output_data
            assert output_data["summary"]["total_checks"] > 0
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
