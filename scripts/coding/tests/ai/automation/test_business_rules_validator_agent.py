"""
Comprehensive tests for BusinessRulesValidatorAgent following TDD strict approach.

Test Coverage:
- Structure validation (required/optional files)
- Categorization validation (5 rule types: Hechos, Restricciones, Desencadenadores, Inferencias, Cálculos)
- Matrix validation (roles and permissions)
- Examples validation (IACT-specific keywords)
- Cross-reference validation (markdown links)
- Use case traceability validation (BR-XXX references)

TDD Process Applied:
- RED: Write failing test
- GREEN: Minimal hardcoded implementation
- RED: Test forcing real data reading
- GREEN: Real implementation
- REFACTOR: Consolidate and clean up

Author: SDLC Agent (TDD Process)
Date: 2025-11-14
Related: scripts/coding/ai/automation/business_rules_validator_agent.py
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
import importlib.util

# Load the agent module directly
agent_module_path = Path(__file__).parent.parent.parent.parent / "ai" / "automation" / "business_rules_validator_agent.py"
spec = importlib.util.spec_from_file_location("business_rules_validator_agent", agent_module_path)
agent_module = importlib.util.module_from_spec(spec)
sys.modules["business_rules_validator_agent"] = agent_module
spec.loader.exec_module(agent_module)

# Import classes
BusinessRulesValidator = agent_module.BusinessRulesValidator
ValidationResult = agent_module.ValidationResult
ValidationIssue = agent_module.ValidationIssue
ExitCode = agent_module.ExitCode


class TestBusinessRulesValidatorAgent:
    """Test suite for BusinessRulesValidatorAgent following TDD strict."""

    # ======================
    # FIXTURES
    # ======================

    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary documentation directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_path = Path(tmpdir) / "REGLAS_NEGOCIO"
            docs_path.mkdir(parents=True)
            yield docs_path

    @pytest.fixture
    def valid_readme_content(self):
        """Valid README.md content."""
        return """# Business Rules Documentation

This directory contains business rules for IACT call center system.
"""

    @pytest.fixture
    def readme_without_iact_keywords(self):
        """README.md content without IACT-specific keywords."""
        return """# Business Rules Documentation

This directory contains business rules for the system.
"""

    @pytest.fixture
    def valid_introduccion_content(self):
        """Valid INTRODUCCION.md content."""
        return """# Introducción a Reglas de Negocio

Business rules define the behavior and constraints of IACT system.
Following LFPDPPP compliance requirements.
"""

    @pytest.fixture
    def valid_hechos_restricciones_content(self):
        """Valid HECHOS_RESTRICCIONES.md with Facts and Constraints."""
        return """# Hechos y Restricciones

## 1. HECHOS (Facts)

### H-001: Sistema de Call Center
El sistema IACT es un call center que gestiona llamadas de agentes.

## 2. RESTRICCIONES (Constraints)

### R-001: Acceso por Rol
Un agente solo puede ver sus propias llamadas.
Un supervisor debe poder ver llamadas de su equipo.
No puede acceder a datos de otros equipos.

## Matriz de Roles y Permisos

| Rol | Ver Llamadas | Editar Datos | Eliminar |
|-----|--------------|--------------|----------|
| AGENTE | Propias | No | No |
| SUPERVISOR | Equipo | Equipo | No |
| GERENTE | Todas | Todas | No |
| ADMIN | Todas | Todas | Sí |
"""

    @pytest.fixture
    def valid_tipos_avanzados_content(self):
        """Valid TIPOS_AVANZADOS.md with advanced rule types."""
        return """# Tipos Avanzados de Reglas

## Desencadenadores (Triggers)

### T-001: Notificación de Llamada Larga
Si una llamada supera 30 minutos, entonces notificar al supervisor.

## Inferencias (Inferences)

### I-001: Cliente VIP
Si un cliente tiene más de 50 llamadas, entonces inferir que es VIP.

## Cálculos (Computations)

### C-001: Tiempo Promedio
El tiempo promedio de atención se calcula como la suma de duraciones dividido entre cantidad de llamadas.
"""

    @pytest.fixture
    def iact_examples_content(self):
        """Content with IACT-specific examples and LFPDPPP references."""
        return """# Aplicación IACT

## Ejemplos Específicos

### Ejemplo 1: Agente recibe llamada
Un agente de IACT recibe una llamada en el IVR.
La campaña asigna la llamada al agente disponible.

### Ejemplo 2: LFPDPPP Compliance
Según LFPDPPP, los datos personales del cliente deben estar protegidos.
El supervisor puede acceder a grabaciones con consentimiento.
"""

    @pytest.fixture
    def markdown_with_links_content(self):
        """Content with cross-references."""
        return """# References Test

See also:
- [Introduction](INTRODUCCION.md)
- [Facts and Constraints](HECHOS_RESTRICCIONES.md)
- [External Link](https://example.com)
- [Anchor](#section)
"""

    @pytest.fixture
    def use_cases_dir_with_br_refs(self, temp_docs_dir):
        """Create use cases directory with BR references."""
        uc_dir = temp_docs_dir.parent.parent / "casos_de_uso"
        uc_dir.mkdir(parents=True, exist_ok=True)

        # Create use cases with business rule references
        (uc_dir / "UC-001-login.md").write_text("""
# UC-001: Login

Business rules:
- BR-R001: Usuario debe autenticarse
- BR-R002: Contraseña debe ser segura
""")

        (uc_dir / "UC-002-llamada.md").write_text("""
# UC-002: Gestión de Llamada

Business rules:
- BR-T001: Si llamada >30min, notificar
- BR-R005: Agente solo ve sus llamadas
""")

        return uc_dir

    # ======================
    # CICLO 1: ESTRUCTURA
    # ======================

    def test_structure_validation_missing_directory_fails(self):
        """
        RED Test 1.1: Directory not found

        Given a non-existent documentation directory
        When validating structure
        Then should report error and mark structure as invalid
        """
        validator = BusinessRulesValidator(Path("/nonexistent/path"))
        result = validator.validate()

        assert result.is_valid is False
        assert result.structure_valid is False
        assert len(result.errors) > 0
        assert any("not found" in err.message.lower() for err in result.errors)

    def test_structure_validation_missing_required_files(self, temp_docs_dir):
        """
        RED Test 1.2: Missing required files

        Given an empty documentation directory
        When validating structure
        Then should report missing required files
        """
        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.structure_valid is False
        assert len(result.errors) >= 3  # README, INTRODUCCION, HECHOS_RESTRICCIONES

        error_messages = [err.message for err in result.errors]
        assert any("README.md" in msg for msg in error_messages)
        assert any("INTRODUCCION.md" in msg for msg in error_messages)
        assert any("HECHOS_RESTRICCIONES.md" in msg for msg in error_messages)

    def test_structure_validation_required_files_present(self, temp_docs_dir,
                                                         valid_readme_content,
                                                         valid_introduccion_content,
                                                         valid_hechos_restricciones_content):
        """
        GREEN Test 1.3: All required files present

        Given a documentation directory with all required files
        When validating structure
        Then should mark structure as valid
        And should list all checked files
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        # Structure validation should pass
        assert result.structure_valid is True
        assert "README.md" in result.files_checked
        assert "INTRODUCCION.md" in result.files_checked
        assert "HECHOS_RESTRICCIONES.md" in result.files_checked

    def test_structure_validation_optional_files_warning(self, temp_docs_dir,
                                                          valid_readme_content,
                                                          valid_introduccion_content,
                                                          valid_hechos_restricciones_content):
        """
        GREEN Test 1.4: Optional files missing generates warnings

        Given a documentation directory without optional files
        When validating structure
        Then should generate warnings (not errors)
        And structure should still be valid
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.structure_valid is True

        # Should have warnings for optional files
        warning_messages = [w.message for w in result.warnings]
        assert any("TIPOS_AVANZADOS.md" in msg for msg in warning_messages)
        assert any("APLICACION_IACT.md" in msg for msg in warning_messages)

    # ======================
    # CICLO 2: CATEGORIZACIÓN
    # ======================

    def test_categorization_missing_hechos_section_fails(self, temp_docs_dir,
                                                          valid_readme_content,
                                                          valid_introduccion_content):
        """
        RED Test 2.1: Missing Hechos section

        Given HECHOS_RESTRICCIONES.md without Hechos section
        When validating categorization
        Then should report missing Hechos section
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text("# No sections here")

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.categorization_valid is False
        assert any("Hechos" in err.message for err in result.errors if err.type == "categorization")

    def test_categorization_missing_restricciones_section_fails(self, temp_docs_dir,
                                                                 valid_readme_content,
                                                                 valid_introduccion_content):
        """
        RED Test 2.2: Missing Restricciones section

        Given HECHOS_RESTRICCIONES.md without Restricciones section
        When validating categorization
        Then should report missing Restricciones section
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text("## 1. HECHOS\nSome facts")

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.categorization_valid is False
        assert any("Restricciones" in err.message for err in result.errors if err.type == "categorization")

    def test_categorization_all_sections_present(self, temp_docs_dir,
                                                  valid_readme_content,
                                                  valid_introduccion_content,
                                                  valid_hechos_restricciones_content):
        """
        GREEN Test 2.3: All required sections present

        Given HECHOS_RESTRICCIONES.md with Hechos and Restricciones sections
        When validating categorization
        Then should mark categorization as valid
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.categorization_valid is True
        # No categorization errors
        cat_errors = [e for e in result.errors if e.type == "categorization"]
        assert len(cat_errors) == 0

    def test_categorization_constraint_keywords_present(self, temp_docs_dir,
                                                         valid_readme_content,
                                                         valid_introduccion_content,
                                                         valid_hechos_restricciones_content):
        """
        GREEN Test 2.4: Constraint keywords detected

        Given HECHOS_RESTRICCIONES.md with constraint keywords
        When validating categorization
        Then should not generate warnings about missing keywords
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        # Should not have warning about missing constraint keywords
        constraint_warnings = [w for w in result.warnings
                               if "constraint keywords" in w.message.lower()]
        assert len(constraint_warnings) == 0

    def test_categorization_advanced_types_validation(self, temp_docs_dir,
                                                       valid_readme_content,
                                                       valid_introduccion_content,
                                                       valid_hechos_restricciones_content,
                                                       valid_tipos_avanzados_content):
        """
        GREEN Test 2.5: Advanced types validation

        Given TIPOS_AVANZADOS.md with Desencadenadores, Inferencias, Cálculos
        When validating categorization
        Then should not generate warnings about missing advanced types
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)
        (temp_docs_dir / "TIPOS_AVANZADOS.md").write_text(valid_tipos_avanzados_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        # Should have TIPOS_AVANZADOS.md in checked files
        assert "TIPOS_AVANZADOS.md" in result.files_checked

        # Should not have warnings about missing advanced types
        advanced_warnings = [w for w in result.warnings
                             if w.type == "categorization" and "TIPOS_AVANZADOS.md" in (w.file or "")]
        # If there are warnings, they should not be about missing sections
        for w in advanced_warnings:
            assert "missing" not in w.message.lower() or "section" not in w.message.lower()

    # ======================
    # CICLO 3: MATRICES
    # ======================

    def test_matrix_validation_missing_matrix_section(self, temp_docs_dir,
                                                       valid_readme_content,
                                                       valid_introduccion_content):
        """
        RED Test 3.1: Missing matrix section

        Given HECHOS_RESTRICCIONES.md without matrix section
        When validating matrices
        Then should generate warning about missing matrix
        """
        content_without_matrix = """# Hechos y Restricciones

## 1. HECHOS
Some facts

## 2. RESTRICCIONES
Some constraints
"""
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(content_without_matrix)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        matrix_warnings = [w for w in result.warnings if w.type == "matrix"]
        assert len(matrix_warnings) > 0
        assert any("Matriz de Roles y Permisos" in w.message for w in matrix_warnings)

    def test_matrix_validation_incomplete_roles(self, temp_docs_dir,
                                                 valid_readme_content,
                                                 valid_introduccion_content):
        """
        RED Test 3.2: Matrix with few roles

        Given HECHOS_RESTRICCIONES.md with matrix but only 1-2 roles
        When validating matrices
        Then should warn about incomplete matrix
        """
        content_with_incomplete_matrix = """# Hechos y Restricciones

## Matriz de Roles y Permisos

| Rol | Permiso |
|-----|---------|
| AGENTE | Ver |
"""
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(content_with_incomplete_matrix)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        matrix_warnings = [w for w in result.warnings if w.type == "matrix"]
        assert any("incomplete" in w.message.lower() for w in matrix_warnings)

    def test_matrix_validation_complete_matrix(self, temp_docs_dir,
                                                valid_readme_content,
                                                valid_introduccion_content,
                                                valid_hechos_restricciones_content):
        """
        GREEN Test 3.3: Complete matrix with multiple roles

        Given HECHOS_RESTRICCIONES.md with complete matrix (3+ roles)
        When validating matrices
        Then should report info about found roles
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        matrix_info = [i for i in result.info if i.type == "matrix"]
        assert len(matrix_info) > 0
        assert any("Role-permission matrix found" in i.message for i in matrix_info)

    # ======================
    # CICLO 4: EJEMPLOS IACT
    # ======================

    def test_examples_validation_no_iact_keywords(self, temp_docs_dir,
                                                   readme_without_iact_keywords):
        """
        RED Test 4.1: File without IACT keywords

        Given a file without IACT-specific keywords
        When validating examples
        Then should warn about missing IACT examples
        """
        (temp_docs_dir / "README.md").write_text(readme_without_iact_keywords)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        example_warnings = [w for w in result.warnings if w.type == "example"]
        assert any("No IACT-specific examples" in w.message for w in example_warnings)

    def test_examples_validation_iact_keywords_found(self, temp_docs_dir,
                                                      iact_examples_content):
        """
        GREEN Test 4.2: File with IACT keywords

        Given a file with IACT-specific keywords
        When validating examples
        Then should report info about found keywords
        """
        (temp_docs_dir / "APLICACION_IACT.md").write_text(iact_examples_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        example_info = [i for i in result.info if i.type == "example"]
        assert any("Found" in i.message and "IACT keywords" in i.message for i in example_info)

    def test_examples_validation_lfpdppp_compliance(self, temp_docs_dir,
                                                     iact_examples_content):
        """
        GREEN Test 4.3: LFPDPPP compliance references

        Given a file with LFPDPPP references
        When validating examples
        Then should report info about compliance references
        """
        (temp_docs_dir / "APLICACION_IACT.md").write_text(iact_examples_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        lfpdppp_info = [i for i in result.info
                        if i.type == "example" and "LFPDPPP" in i.message]
        assert len(lfpdppp_info) > 0

    # ======================
    # CICLO 5: REFERENCIAS CRUZADAS
    # ======================

    def test_references_validation_broken_link(self, temp_docs_dir,
                                                valid_readme_content):
        """
        RED Test 5.1: Broken internal link

        Given a file with broken markdown link
        When validating references
        Then should warn about missing referenced file
        """
        content_with_broken_link = """# Test

See [Broken Link](NONEXISTENT.md)
"""
        (temp_docs_dir / "README.md").write_text(content_with_broken_link)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        ref_warnings = [w for w in result.warnings if w.type == "reference"]
        assert any("not found" in w.message.lower() for w in ref_warnings)

    def test_references_validation_valid_links(self, temp_docs_dir,
                                                valid_readme_content,
                                                valid_introduccion_content,
                                                valid_hechos_restricciones_content,
                                                markdown_with_links_content):
        """
        GREEN Test 5.2: Valid internal links

        Given files with valid markdown links to existing files
        When validating references
        Then should not warn about broken links
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)
        (temp_docs_dir / "LINKS.md").write_text(markdown_with_links_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        # Filter warnings for broken links to existing files
        ref_warnings = [w for w in result.warnings
                        if w.type == "reference"
                        and ("INTRODUCCION.md" in w.message or "HECHOS_RESTRICCIONES.md" in w.message)]
        assert len(ref_warnings) == 0

    def test_references_validation_external_links_ignored(self, temp_docs_dir,
                                                           markdown_with_links_content):
        """
        GREEN Test 5.3: External links are ignored

        Given files with external HTTP links
        When validating references
        Then should not validate external links
        """
        (temp_docs_dir / "LINKS.md").write_text(markdown_with_links_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        # Should not have warnings about external links
        ref_warnings = [w for w in result.warnings
                        if w.type == "reference" and "example.com" in w.message]
        assert len(ref_warnings) == 0

    # ======================
    # CICLO 6: TRAZABILIDAD UC
    # ======================

    def test_traceability_no_use_cases_directory(self, temp_docs_dir,
                                                  valid_readme_content):
        """
        GREEN Test 6.1: No use cases directory

        Given no use cases directory exists
        When validating traceability
        Then should report info (not error) about skipping traceability
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)

        # Ensure casos_de_uso does not exist
        uc_dir = temp_docs_dir.parent.parent / "casos_de_uso"
        if uc_dir.exists():
            import shutil
            shutil.rmtree(uc_dir)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        trace_info = [i for i in result.info if i.type == "traceability"]
        assert len(trace_info) > 0
        assert any("directory not found" in i.message.lower() or "skipping" in i.message.lower() for i in trace_info)

    def test_traceability_use_cases_without_br_refs(self, temp_docs_dir,
                                                     valid_readme_content):
        """
        RED Test 6.2: Use cases without BR references

        Given use case files without BR-XXX references
        When validating traceability
        Then should warn about missing BR references
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)

        # Clean and create use cases dir without BR refs
        uc_dir = temp_docs_dir.parent.parent / "casos_de_uso"
        if uc_dir.exists():
            import shutil
            shutil.rmtree(uc_dir)
        uc_dir.mkdir(parents=True, exist_ok=True)
        (uc_dir / "UC-001-test.md").write_text("# UC-001\nNo business rules here")

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        trace_warnings = [w for w in result.warnings if w.type == "traceability"]
        assert len(trace_warnings) > 0
        assert any("but none reference" in w.message.lower() or "no.*business rules" in w.message.lower() for w in trace_warnings)

    def test_traceability_use_cases_with_br_refs(self, temp_docs_dir,
                                                  valid_readme_content,
                                                  use_cases_dir_with_br_refs):
        """
        GREEN Test 6.3: Use cases with BR references

        Given use case files with BR-XXX references
        When validating traceability
        Then should report info about found references
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        trace_info = [i for i in result.info if i.type == "traceability"]
        assert any("use cases referencing business rules" in i.message.lower() for i in trace_info)
        assert any("unique business rules" in i.message.lower() for i in trace_info)

    # ======================
    # INTEGRATION TESTS
    # ======================

    def test_full_validation_complete_docs(self, temp_docs_dir,
                                            valid_readme_content,
                                            valid_introduccion_content,
                                            valid_hechos_restricciones_content,
                                            valid_tipos_avanzados_content,
                                            iact_examples_content,
                                            use_cases_dir_with_br_refs):
        """
        Integration Test: Complete documentation validation

        Given a complete documentation directory with all files
        When running full validation
        Then should pass all validations
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)
        (temp_docs_dir / "TIPOS_AVANZADOS.md").write_text(valid_tipos_avanzados_content)
        (temp_docs_dir / "APLICACION_IACT.md").write_text(iact_examples_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        assert result.is_valid is True
        assert result.structure_valid is True
        assert result.categorization_valid is True
        assert result.examples_valid is True
        assert result.references_valid is True
        assert len(result.errors) == 0

    def test_to_json_format(self, temp_docs_dir, valid_readme_content):
        """
        Test JSON serialization format

        Given a validation result
        When converting to JSON
        Then should include all expected fields
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()
        json_data = result.to_json()

        assert "status" in json_data
        assert "is_valid" in json_data
        assert "directory_path" in json_data
        assert "files_checked" in json_data
        assert "errors" in json_data
        assert "warnings" in json_data
        assert "info" in json_data
        assert "summary" in json_data
        assert "timestamp" in json_data

        # Summary should include all validation types
        assert "structure_valid" in json_data["summary"]
        assert "categorization_valid" in json_data["summary"]
        assert "examples_valid" in json_data["summary"]
        assert "references_valid" in json_data["summary"]

    # ======================
    # CLI TESTS
    # ======================

    def test_exit_code_valid(self, temp_docs_dir,
                              valid_readme_content,
                              valid_introduccion_content,
                              valid_hechos_restricciones_content):
        """
        Test CLI exit code for valid documentation

        Given valid documentation
        When running validator
        Then should return VALID exit code (0)
        """
        (temp_docs_dir / "README.md").write_text(valid_readme_content)
        (temp_docs_dir / "INTRODUCCION.md").write_text(valid_introduccion_content)
        (temp_docs_dir / "HECHOS_RESTRICCIONES.md").write_text(valid_hechos_restricciones_content)

        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        exit_code = ExitCode.VALID if result.is_valid else ExitCode.INVALID
        assert exit_code == ExitCode.VALID

    def test_exit_code_invalid(self, temp_docs_dir):
        """
        Test CLI exit code for invalid documentation

        Given invalid documentation (missing files)
        When running validator
        Then should return INVALID exit code (1)
        """
        validator = BusinessRulesValidator(temp_docs_dir)
        result = validator.validate()

        exit_code = ExitCode.VALID if result.is_valid else ExitCode.INVALID
        assert exit_code == ExitCode.INVALID


class TestValidationIssue:
    """Test ValidationIssue data class."""

    def test_validation_issue_to_dict(self):
        """
        Test ValidationIssue serialization

        Given a ValidationIssue instance
        When converting to dict
        Then should include all fields
        """
        issue = ValidationIssue(
            type="structure",
            message="Test error",
            file="test.md",
            line=10,
            severity="error"
        )

        issue_dict = issue.to_dict()

        assert issue_dict["type"] == "structure"
        assert issue_dict["message"] == "Test error"
        assert issue_dict["file"] == "test.md"
        assert issue_dict["line"] == 10
        assert issue_dict["severity"] == "error"


# Run tests with: pytest -v test_business_rules_validator_agent.py
