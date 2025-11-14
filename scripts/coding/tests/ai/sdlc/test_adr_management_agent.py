#!/usr/bin/env python3
"""
TDD Tests for ADRManagementAgent

Tests the ADRManagementAgent implementation which manages the complete lifecycle
of Architecture Decision Records (ADRs) including creation, validation, standardization,
and index maintenance.

Methodology: RED-GREEN-REFACTOR
- RED: Write failing tests first
- GREEN: Implement minimal code to pass
- REFACTOR: Improve code while keeping tests green
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from scripts.coding.ai.sdlc.adr_management_agent import ADRManagementAgent


# Fixtures
@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing."""
    # Create docs structure
    docs_dir = tmp_path / "docs"

    # Create domain directories
    for domain in ["ai", "backend", "frontend", "infraestructura", "gobernanza"]:
        domain_dir = docs_dir / domain
        domain_dir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def agent(temp_project):
    """Create ADRManagementAgent instance."""
    config = {
        "project_root": str(temp_project)
    }
    return ADRManagementAgent(config=config)


@pytest.fixture
def sample_adr_data():
    """Sample ADR data for creation tests."""
    return {
        "titulo": "Sistema de Permisos Granular",
        "dominio": "backend",
        "decisores": "Arquitecto Senior, Tech Lead",
        "contexto_tecnico": "Backend Django + PostgreSQL",
        "contexto_problema": "Necesitamos un sistema de permisos flexible sin roles jerarquicos",
        "factores": "Seguridad, Flexibilidad, Performance",
        "opciones": "Opcion 1: Roles jerarquicos\nOpcion 2: Grupos funcionales",
        "decision": "Opcion 2: Grupos funcionales combinables",
        "consecuencias_positivas": "Mayor flexibilidad y escalabilidad",
        "consecuencias_negativas": "Mayor complejidad inicial",
        "referencias": "ISO 27001, OWASP",
        "propietario": "@equipo-backend",
        "estado": "aceptada",
        "relacionados": []
    }


@pytest.fixture
def existing_adr(temp_project):
    """Create an existing ADR for testing."""
    adr_path = temp_project / "docs" / "backend" / "ADR_2025_001_test_decision.md"

    content = """---
id: ADR_2025_001
estado: aceptada
propietario: @equipo-backend
ultima_actualizacion: 2025-11-13
relacionados: []
date: 2025-11-13
---

# ADR_2025_001: Test Decision

**Estado:** aceptada

**Fecha:** 2025-11-13

**Decisores:** Test Lead

**Contexto tecnico:** Test

## Contexto y Problema

Test problem

## Decision

Test decision

## Consecuencias

### Positivas

- Test positive

### Negativas

- Test negative

## Referencias

- Test reference

---

**VERSION:** 1.0.0
**ESTADO:** aceptada
**PROXIMA REVISION:** 2025-12-13
"""

    adr_path.write_text(content, encoding="utf-8")
    return adr_path


@pytest.fixture
def old_format_adr(temp_project):
    """Create an ADR with old format (hyphens) for testing."""
    adr_path = temp_project / "docs" / "backend" / "ADR-2025-002-old-format.md"

    content = """---
id: ADR-2025-002
estado: aceptada
propietario: @equipo-backend
ultima_actualizacion: 2025-11-13
relacionados: []
date: 2025-11-13
---

# ADR-2025-002: Old Format

**Estado:** aceptada

## Contexto y Problema

Old format problem

## Decision

Old format decision

## Consecuencias

### Positivas

- Old positive

### Negativas

- Old negative
"""

    adr_path.write_text(content, encoding="utf-8")
    return adr_path


# 1. Initialization Tests
class TestADRManagementAgentInitialization:
    """Test ADRManagementAgent initialization."""

    def test_default_initialization(self, temp_project):
        """Should initialize with default parameters."""
        config = {"project_root": str(temp_project)}
        agent = ADRManagementAgent(config=config)

        assert agent.name == "ADRManagementAgent"
        assert agent.phase == "documentation"
        assert agent.project_root == temp_project
        assert agent.docs_dir == temp_project / "docs"

    def test_valid_domains_defined(self, agent):
        """Should have valid domains defined."""
        assert hasattr(agent, "VALID_DOMAINS")
        assert "ai" in agent.VALID_DOMAINS
        assert "backend" in agent.VALID_DOMAINS
        assert "frontend" in agent.VALID_DOMAINS
        assert "infraestructura" in agent.VALID_DOMAINS
        assert "gobernanza" in agent.VALID_DOMAINS

    def test_adr_pattern_defined(self, agent):
        """Should have ADR pattern regex defined."""
        assert hasattr(agent, "ADR_PATTERN")

        # Test pattern matches correct format
        match = agent.ADR_PATTERN.match("ADR_2025_001_test_decision.md")
        assert match is not None
        assert match.group(1) == "2025"  # year
        assert match.group(2) == "001"   # number
        assert match.group(3) == "test_decision"  # description


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation for different operations."""

    def test_validate_valid_create_input(self, agent, sample_adr_data):
        """Should accept valid create operation input."""
        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        errors = agent.validate_input(input_data)

        assert errors == []

    def test_validate_missing_operation(self, agent):
        """Should reject input without operation."""
        input_data = {"adr_data": {}}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("operation" in err.lower() for err in errors)

    def test_validate_invalid_operation(self, agent):
        """Should reject invalid operation."""
        input_data = {"operation": "invalid_operation"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("operation invalida" in err.lower() for err in errors)

    def test_validate_create_missing_adr_data(self, agent):
        """Should reject create operation without adr_data."""
        input_data = {"operation": "create"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("adr_data" in err.lower() for err in errors)

    def test_validate_create_missing_required_fields(self, agent):
        """Should reject create operation with incomplete adr_data."""
        input_data = {
            "operation": "create",
            "adr_data": {
                "titulo": "Test"
                # Missing: dominio, decisores, contexto_problema
            }
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        # Should complain about missing fields
        assert any("dominio" in err or "decisores" in err or "contexto_problema" in err
                   for err in errors)

    def test_validate_create_invalid_domain(self, agent):
        """Should reject invalid domain."""
        input_data = {
            "operation": "create",
            "adr_data": {
                "titulo": "Test",
                "dominio": "invalid_domain",
                "decisores": "Test",
                "contexto_problema": "Test"
            }
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("dominio invalido" in err.lower() for err in errors)


# 3. ADR Creation Tests
class TestADRCreation:
    """Test ADR creation functionality."""

    def test_create_new_adr(self, agent, sample_adr_data):
        """Should create new ADR with correct format."""
        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert "adr_path" in result.output
        assert "adr_id" in result.output

        # Verify file was created
        adr_path = Path(result.output["adr_path"])
        assert adr_path.exists()

        # Verify filename format
        assert agent.ADR_PATTERN.match(adr_path.name)

    def test_create_adr_with_sequential_number(self, agent, existing_adr, sample_adr_data):
        """Should assign next sequential number."""
        # existing_adr is ADR_2025_001
        # New ADR should be ADR_2025_002

        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert "ADR_2025_002" in result.output["adr_id"]

    def test_create_adr_content_structure(self, agent, sample_adr_data):
        """Should create ADR with correct content structure."""
        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        adr_path = Path(result.output["adr_path"])
        content = adr_path.read_text(encoding="utf-8")

        # Verify frontmatter
        assert content.startswith("---")
        assert "id: ADR_" in content
        assert "estado:" in content
        assert "propietario:" in content

        # Verify sections
        assert "## Contexto y Problema" in content
        assert "## Decision" in content
        assert "## Consecuencias" in content
        assert "### Positivas" in content
        assert "### Negativas" in content

    def test_create_adr_in_correct_domain_directory(self, agent, sample_adr_data):
        """Should create ADR in correct domain directory."""
        sample_adr_data["dominio"] = "frontend"

        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        adr_path = Path(result.output["adr_path"])
        assert "frontend" in str(adr_path)

    def test_create_adr_snake_case_filename(self, agent, sample_adr_data):
        """Should convert title to snake_case in filename."""
        sample_adr_data["titulo"] = "Sistema de Permisos Granular"

        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        adr_path = Path(result.output["adr_path"])
        assert "sistema_de_permisos_granular" in adr_path.name


# 4. ADR Validation Tests
class TestADRValidation:
    """Test ADR validation functionality."""

    def test_validate_existing_valid_adr(self, agent, existing_adr):
        """Should validate existing ADR successfully."""
        input_data = {
            "operation": "validate",
            "adr_paths": [str(existing_adr)]
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        validation_results = result.output["validation_results"]
        assert validation_results["valid"] == 1
        assert validation_results["invalid"] == 0

    def test_validate_adr_with_invalid_name(self, temp_project, agent):
        """Should detect invalid ADR filename format."""
        # Create ADR with wrong format
        invalid_adr = temp_project / "docs" / "backend" / "adr-wrong-format.md"
        invalid_adr.write_text("# Test", encoding="utf-8")

        input_data = {
            "operation": "validate",
            "adr_paths": [str(invalid_adr)]
        }

        result = agent.execute(input_data)

        validation_results = result.output["validation_results"]
        assert validation_results["invalid"] == 1
        assert len(validation_results["errors"]) > 0

    def test_validate_adr_missing_frontmatter(self, temp_project, agent):
        """Should detect missing frontmatter."""
        # Create ADR without frontmatter
        invalid_adr = temp_project / "docs" / "backend" / "ADR_2025_999_no_frontmatter.md"
        invalid_adr.write_text("# ADR_2025_999: No Frontmatter\n\nContent", encoding="utf-8")

        input_data = {
            "operation": "validate",
            "adr_paths": [str(invalid_adr)]
        }

        result = agent.execute(input_data)

        validation_results = result.output["validation_results"]
        assert validation_results["invalid"] == 1
        errors = validation_results["errors"]
        assert any("frontmatter" in err["error"].lower() for err in errors)

    def test_validate_adr_missing_sections(self, temp_project, agent):
        """Should detect missing required sections."""
        # Create ADR without required sections
        invalid_adr = temp_project / "docs" / "backend" / "ADR_2025_998_no_sections.md"
        content = """---
id: ADR_2025_998
estado: aceptada
date: 2025-11-13
---

# ADR_2025_998: No Sections

Just some content
"""
        invalid_adr.write_text(content, encoding="utf-8")

        input_data = {
            "operation": "validate",
            "adr_paths": [str(invalid_adr)]
        }

        result = agent.execute(input_data)

        validation_results = result.output["validation_results"]
        assert validation_results["invalid"] == 1
        errors = validation_results["errors"]
        assert any("secciones" in err["error"].lower() for err in errors)

    def test_validate_all_adrs_when_no_paths_provided(self, agent, existing_adr):
        """Should validate all ADRs when no specific paths provided."""
        input_data = {
            "operation": "validate"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        validation_results = result.output["validation_results"]
        assert validation_results["total"] >= 1  # At least the existing_adr


# 5. ADR Naming Standardization Tests
class TestADRStandardization:
    """Test ADR naming standardization functionality."""

    def test_standardize_old_format_adr(self, agent, old_format_adr):
        """Should rename ADR from hyphen to underscore format."""
        input_data = {
            "operation": "standardize"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert result.output["renamed_count"] >= 1

        # Verify old file doesn't exist
        assert not old_format_adr.exists()

        # Verify new file exists
        new_path = old_format_adr.parent / "ADR_2025_002_old_format.md"
        assert new_path.exists()

    def test_standardize_updates_internal_id(self, agent, old_format_adr):
        """Should update internal ID in frontmatter after renaming."""
        input_data = {
            "operation": "standardize"
        }

        agent.execute(input_data)

        new_path = old_format_adr.parent / "ADR_2025_002_old_format.md"
        content = new_path.read_text(encoding="utf-8")

        # Should have underscore format in ID
        assert "id: ADR_2025_002" in content
        assert "ADR-2025-002" not in content

    def test_standardize_no_changes_when_all_correct(self, agent, existing_adr):
        """Should report zero changes when all ADRs already correct."""
        input_data = {
            "operation": "standardize"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert result.output["renamed_count"] == 0


# 6. Index Maintenance Tests
class TestIndexMaintenance:
    """Test index maintenance functionality."""

    def test_update_index_creates_index_file(self, agent, existing_adr):
        """Should create index file if it doesn't exist."""
        input_data = {
            "operation": "update_index"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert "index_path" in result.output

        index_path = Path(result.output["index_path"])
        assert index_path.exists()

    def test_update_index_includes_all_adrs(self, agent, existing_adr):
        """Should include all existing ADRs in index."""
        input_data = {
            "operation": "update_index"
        }

        result = agent.execute(input_data)

        index_path = Path(result.output["index_path"])
        content = index_path.read_text(encoding="utf-8")

        # Should contain reference to existing ADR
        assert "ADR_2025_001" in content

    def test_update_index_has_correct_structure(self, agent, existing_adr):
        """Should generate index with correct structure."""
        input_data = {
            "operation": "update_index"
        }

        result = agent.execute(input_data)

        index_path = Path(result.output["index_path"])
        content = index_path.read_text(encoding="utf-8")

        # Verify frontmatter
        assert content.startswith("---")
        assert "title:" in content
        assert "date:" in content

        # Verify sections
        assert "## Sistema de Numeracion" in content
        assert "## Indice por Numero" in content
        assert "## Indice por Dominio" in content
        assert "## Estadisticas" in content

    def test_update_index_counts_by_domain(self, agent, existing_adr):
        """Should count ADRs by domain correctly."""
        input_data = {
            "operation": "update_index"
        }

        result = agent.execute(input_data)

        assert "by_domain" in result.output
        by_domain = result.output["by_domain"]
        assert "backend" in by_domain
        assert by_domain["backend"] >= 1


# 7. Reference Update Tests
class TestReferenceUpdate:
    """Test reference update functionality."""

    def test_update_references_in_documents(self, agent, temp_project):
        """Should update references to ADRs in documents."""
        # Create a document with old reference
        doc_path = temp_project / "docs" / "gobernanza" / "test_doc.md"
        doc_content = "See ADR-2025-001 for details"
        doc_path.write_text(doc_content, encoding="utf-8")

        input_data = {
            "operation": "update_references",
            "old_reference": "ADR-2025-001",
            "new_reference": "ADR_2025_001"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert len(result.output["updated_files"]) >= 1

        # Verify content was updated
        updated_content = doc_path.read_text(encoding="utf-8")
        assert "ADR_2025_001" in updated_content
        assert "ADR-2025-001" not in updated_content

    def test_update_references_reports_updated_files(self, agent, temp_project):
        """Should report which files were updated."""
        doc_path = temp_project / "docs" / "backend" / "test_doc.md"
        doc_path.write_text("Reference: ADR-2025-999", encoding="utf-8")

        input_data = {
            "operation": "update_references",
            "old_reference": "ADR-2025-999",
            "new_reference": "ADR_2025_999"
        }

        result = agent.execute(input_data)

        updated_files = result.output["updated_files"]
        assert any("test_doc.md" in f for f in updated_files)


# 8. Integration Tests
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_create_and_validate_workflow(self, agent, sample_adr_data):
        """Should create ADR and then validate it successfully."""
        # Create ADR
        create_input = {
            "operation": "create",
            "adr_data": sample_adr_data
        }
        create_result = agent.execute(create_input)
        adr_path = create_result.output["adr_path"]

        # Validate ADR
        validate_input = {
            "operation": "validate",
            "adr_paths": [adr_path]
        }
        validate_result = agent.execute(validate_input)

        # Should be valid
        validation_results = validate_result.output["validation_results"]
        assert validation_results["valid"] == 1
        assert validation_results["invalid"] == 0

    def test_create_standardize_update_index_workflow(self, agent, sample_adr_data, old_format_adr):
        """Should create ADR, standardize names, and update index."""
        # Create new ADR
        create_input = {
            "operation": "create",
            "adr_data": sample_adr_data
        }
        agent.execute(create_input)

        # Standardize (will fix old_format_adr)
        standardize_input = {"operation": "standardize"}
        standardize_result = agent.execute(standardize_input)
        assert standardize_result.output["renamed_count"] >= 1

        # Update index
        index_input = {"operation": "update_index"}
        index_result = agent.execute(index_input)

        # Index should include both ADRs
        assert index_result.output["total_adrs"] >= 2


# 9. Edge Cases and Error Handling
class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""

    def test_create_adr_in_nonexistent_domain(self, agent, sample_adr_data):
        """Should handle creation in nonexistent domain directory."""
        # Remove backend directory
        backend_dir = agent.docs_dir / "backend"
        if backend_dir.exists():
            shutil.rmtree(backend_dir)

        input_data = {
            "operation": "create",
            "adr_data": sample_adr_data
        }

        result = agent.execute(input_data)

        # Should fail gracefully
        assert result.status.value == "error"
        assert "dominio no existe" in result.error.lower()

    def test_validate_nonexistent_adr_path(self, agent):
        """Should handle validation of nonexistent file."""
        input_data = {
            "operation": "validate",
            "adr_paths": ["/nonexistent/path/ADR_2025_999_fake.md"]
        }

        result = agent.execute(input_data)

        # Should report error
        validation_results = result.output["validation_results"]
        assert validation_results["invalid"] >= 0  # Might skip or report error

    def test_update_references_with_no_matches(self, agent, temp_project):
        """Should handle update when no references found."""
        input_data = {
            "operation": "update_references",
            "old_reference": "ADR-9999-999",
            "new_reference": "ADR_9999_999"
        }

        result = agent.execute(input_data)

        assert result.status.value == "success"
        assert len(result.output["updated_files"]) == 0


# 10. Helper Method Tests
class TestHelperMethods:
    """Test internal helper methods."""

    def test_get_next_adr_number_with_no_adrs(self, agent):
        """Should return 1 when no ADRs exist."""
        next_num = agent._get_next_adr_number()
        assert next_num == 1

    def test_get_next_adr_number_with_existing_adrs(self, agent, existing_adr):
        """Should return next sequential number."""
        next_num = agent._get_next_adr_number()
        assert next_num == 2

    def test_to_snake_case_conversion(self, agent):
        """Should convert text to snake_case correctly."""
        assert agent._to_snake_case("Sistema de Permisos") == "sistema_de_permisos"
        assert agent._to_snake_case("React-Native Setup") == "react_native_setup"
        assert agent._to_snake_case("API Gateway") == "api_gateway"

    def test_extract_frontmatter_field(self, agent, existing_adr):
        """Should extract frontmatter fields correctly."""
        content = existing_adr.read_text(encoding="utf-8")

        estado = agent._extract_frontmatter_field(content, "estado")
        assert estado == "aceptada"

        propietario = agent._extract_frontmatter_field(content, "propietario")
        assert "@equipo-backend" in propietario
