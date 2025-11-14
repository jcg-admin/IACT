"""
Comprehensive tests for ComplianceValidatorAgent following TDD approach.

Test Coverage:
- Business rule coverage validation
- Given/When/Then structure validation
- Clean Code naming conventions
- Test level organization (unit, integration, e2e)
- Framework independence checks
- CLI interface
- Exit codes
- JSON output format

Author: SDLC Agent
Date: 2025-11-14
Related: docs/gobernanza/requisitos/REGLAS_NEGOCIO/ESPECIFICACION_TESTS_COMPLIANCE.md
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.coding.ai.automation.compliance_validator_agent import (
    ComplianceValidatorAgent,
    ValidationResult,
    ValidationIssue,
    ExitCode
)


class TestComplianceValidatorAgent:
    """Test suite for ComplianceValidatorAgent."""

    @pytest.fixture
    def valid_spec_content(self):
        """Valid compliance test specification content."""
        return """
### Regla: Datos Personales Deben Estar Encriptados

**ID de Referencia:** Mencionado como BR-R11 en documentación
**Test Specification:**
```python
def test_rfc_encrypted():
    \"\"\"
    Given a client with RFC
    When stored in database
    Then should be encrypted
    \"\"\"
    pass
```

### Nivel 1: Tests Unitarios de Lógica de Negocio
**Sin dependencias de framework**

### Nivel 2: Tests de Integración con Modelos
**Con dependencias de Django ORM**

### Nivel 3: Tests End-to-End de API
**Con dependencias de Django REST Framework**
"""

    @pytest.fixture
    def invalid_naming_spec(self):
        """Spec with invalid test naming (codifications)."""
        return """
**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_br_r11_encryption():
    \"\"\"
    Given data
    When stored
    Then encrypted
    \"\"\"
    pass
```
"""

    @pytest.fixture
    def missing_structure_spec(self):
        """Spec missing Given/When/Then structure."""
        return """
**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_encryption():
    \"\"\"Test encryption works\"\"\"
    pass
```
"""

    @pytest.fixture
    def temp_spec_file(self, valid_spec_content):
        """Create temporary spec file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(valid_spec_content)
            return Path(f.name)

    # ==================================================================
    # COVERAGE VALIDATION TESTS
    # ==================================================================

    def test_coverage_all_rules_present(self, temp_spec_file):
        """Test that all expected rules are covered."""
        content = """
**ID de Referencia:** BR-R08
**Test Specification:**
```python
def test_consent_required():
    \"\"\"Given call When record Then require consent\"\"\"
    pass
```

**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_data_encrypted():
    \"\"\"Given data When store Then encrypt\"\"\"
    pass
```

**ID de Referencia:** BR-R12
**Test Specification:**
```python
def test_access_logged():
    \"\"\"Given access When occurs Then log\"\"\"
    pass
```

**ID de Referencia:** BR-R13
**Test Specification:**
```python
def test_retention_enforced():
    \"\"\"Given old data When check Then flag\"\"\"
    pass
```

### Nivel 1: Tests Unitarios de Lógica de Negocio
### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
"""
        temp_spec_file.write_text(content)

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.coverage_valid is True
        assert len(result.rules_covered) == 4
        assert len(result.rules_missing) == 0

        temp_spec_file.unlink()

    def test_coverage_missing_rules(self, temp_spec_file):
        """Test detection of missing rule coverage."""
        content = """
**ID de Referencia:** BR-R08
**Test Specification:**
```python
def test_consent():
    \"\"\"Given call When record Then require consent\"\"\"
    pass
```

### Nivel 1: Tests Unitarios
### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
"""
        temp_spec_file.write_text(content)

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.coverage_valid is False
        assert len(result.rules_missing) == 3  # Missing BR-R11, BR-R12, BR-R13

        temp_spec_file.unlink()

    # ==================================================================
    # STRUCTURE VALIDATION TESTS
    # ==================================================================

    def test_structure_given_when_then_present(self, temp_spec_file):
        """Test validation of Given/When/Then structure."""
        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.structure_valid is True
        assert result.tests_found > 0

        temp_spec_file.unlink()

    def test_structure_missing_given_when_then(self, temp_spec_file, missing_structure_spec):
        """Test detection of missing Given/When/Then."""
        temp_spec_file.write_text(missing_structure_spec + """
### Nivel 1: Tests Unitarios
### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
""")

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.structure_valid is False
        assert any("Given/When/Then" in err.message for err in result.errors)

        temp_spec_file.unlink()

    # ==================================================================
    # NAMING VALIDATION TESTS
    # ==================================================================

    def test_naming_clean_code_compliant(self, temp_spec_file):
        """Test that naming follows Clean Code principles."""
        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.naming_valid is True

        temp_spec_file.unlink()

    def test_naming_detects_codifications(self, temp_spec_file, invalid_naming_spec):
        """Test detection of BR-XXX codifications in names."""
        temp_spec_file.write_text(invalid_naming_spec + """
### Nivel 1: Tests Unitarios
### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
""")

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.naming_valid is False
        assert any("codification" in err.message.lower() for err in result.errors)

        temp_spec_file.unlink()

    def test_naming_warns_excessive_length(self, temp_spec_file):
        """Test warning for excessively long test names."""
        content = """
**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_that_client_rfc_data_is_properly_encrypted_in_database_storage():
    \"\"\"Given data When store Then encrypt\"\"\"
    pass
```

### Nivel 1: Tests Unitarios
### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
"""
        temp_spec_file.write_text(content)

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert any("too long" in warn.message.lower() for warn in result.warnings)

        temp_spec_file.unlink()

    # ==================================================================
    # LEVELS VALIDATION TESTS
    # ==================================================================

    def test_levels_all_present(self, temp_spec_file):
        """Test that all three test levels are documented."""
        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.levels_valid is True

        temp_spec_file.unlink()

    def test_levels_missing_section(self, temp_spec_file):
        """Test detection of missing test level sections."""
        content = """
**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_encryption():
    \"\"\"Given data When store Then encrypt\"\"\"
    pass
```

### Nivel 1: Tests Unitarios
### Nivel 2: Tests de Integración
"""
        temp_spec_file.write_text(content)

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert result.levels_valid is False
        assert any("Nivel 3" in err.message for err in result.errors)

        temp_spec_file.unlink()

    def test_levels_framework_independence_unit_tests(self, temp_spec_file):
        """Test warning for framework dependencies in unit tests."""
        content = """
**ID de Referencia:** BR-R11
**Test Specification:**
```python
def test_encryption():
    \"\"\"Given data When store Then encrypt\"\"\"
    pass
```

### Nivel 1: Tests Unitarios de Lógica de Negocio
```python
import django
from django.test import TestCase

def test_unit():
    pass
```

### Nivel 2: Tests de Integración
### Nivel 3: Tests End-to-End
"""
        temp_spec_file.write_text(content)

        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        assert any("django" in warn.message.lower() for warn in result.warnings)

        temp_spec_file.unlink()

    # ==================================================================
    # FILE HANDLING TESTS
    # ==================================================================

    def test_file_not_found(self):
        """Test handling of non-existent spec file."""
        agent = ComplianceTestsValidatorAgent(spec_file=Path("/nonexistent/file.md"))
        result = agent.validate()

        assert result.is_valid is False
        assert any("not found" in err.message.lower() for err in result.errors)

    # ==================================================================
    # JSON OUTPUT TESTS
    # ==================================================================

    def test_json_output_format(self, temp_spec_file):
        """Test JSON output structure."""
        agent = ComplianceValidatorAgent(spec_file=temp_spec_file)
        result = agent.validate()

        json_output = result.to_json()

        assert "status" in json_output
        assert "is_valid" in json_output
        assert "spec_file_path" in json_output
        assert "tests_found" in json_output
        assert "rules_covered" in json_output
        assert "rules_missing" in json_output
        assert "summary" in json_output
        assert "coverage_percentage" in json_output["summary"]

        temp_spec_file.unlink()

    # ==================================================================
    # CLI INTERFACE TESTS
    # ==================================================================

    def test_cli_success_exit_code(self, temp_spec_file):
        """Test CLI exits with 0 on success."""
        with patch('sys.argv', ['agent', '--spec-file', str(temp_spec_file)]):
            from scripts.coding.ai.automation.compliance_tests_validator_agent import main

            exit_code = main()
            assert exit_code == ExitCode.VALID

        temp_spec_file.unlink()

    def test_cli_failure_exit_code(self, temp_spec_file):
        """Test CLI exits with 1 on validation failure."""
        content = """
**Test Specification:**
```python
def test_invalid():
    \"\"\"Missing structure\"\"\"
    pass
```
"""
        temp_spec_file.write_text(content)

        with patch('sys.argv', ['agent', '--spec-file', str(temp_spec_file)]):
            from scripts.coding.ai.automation.compliance_tests_validator_agent import main

            exit_code = main()
            assert exit_code == ExitCode.INVALID

        temp_spec_file.unlink()
