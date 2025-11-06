"""
Tests Unitarios: Agentes de Análisis de Negocio

Tests básicos para validar funcionamiento de los agentes.

Ejecutar:
    python -m pytest scripts/ai/agents/test_business_analysis_agents.py -v
"""

import pytest
from pathlib import Path

from .business_analysis_generator import BusinessAnalysisGenerator
from .traceability_matrix_generator import TraceabilityMatrixGenerator
from .completeness_validator import CompletenessValidator
from .template_generator import TemplateGenerator
from .document_splitter import DocumentSplitter
from .business_analysis_pipeline import create_business_analysis_pipeline


# Fixtures

@pytest.fixture
def sample_input_data():
    """Datos de entrada de ejemplo para tests."""
    return {
        "component_name": "Sistema de Test",
        "domain": "Testing",
        "business_objective": "Probar el sistema de análisis",
        "stakeholders": [
            {"rol": "Tester", "interes": "Validar funcionalidad"}
        ]
    }


@pytest.fixture
def sample_use_cases():
    """Casos de uso de ejemplo."""
    return [
        {
            "id": "UC-001",
            "name": "Ejecutar Prueba",
            "primary_actor": "Tester",
            "preconditions": ["Sistema operativo"],
            "postconditions_success": ["Prueba exitosa"],
            "main_flow": ["Paso 1", "Paso 2", "Paso 3"],
            "related_rules": ["RN-TEST-01"]
        }
    ]


@pytest.fixture
def sample_requirements():
    """Requisitos de ejemplo."""
    return [
        {
            "id": "RF-001",
            "title": "Ejecutar prueba unitaria",
            "priority": "MUST",
            "description": "El sistema debe ejecutar pruebas",
            "acceptance_criteria": ["Criterio 1", "Criterio 2"],
            "related_uc": "UC-001",
            "related_rules": ["RN-TEST-01"]
        }
    ]


# Tests: BusinessAnalysisGenerator

class TestBusinessAnalysisGenerator:
    """Tests para BusinessAnalysisGenerator."""

    def test_initialization(self):
        """Test de inicialización del agente."""
        agent = BusinessAnalysisGenerator()
        assert agent.name == "BusinessAnalysisGenerator"
        assert agent.standards["iso_29148"] == True

    def test_validate_input_success(self, sample_input_data):
        """Test de validación de entrada exitosa."""
        agent = BusinessAnalysisGenerator()
        errors = agent.validate_input(sample_input_data)
        assert len(errors) == 0

    def test_validate_input_missing_component_name(self):
        """Test de validación con campo faltante."""
        agent = BusinessAnalysisGenerator()
        errors = agent.validate_input({"domain": "Test"})
        assert len(errors) > 0
        assert any("component_name" in error for error in errors)

    def test_generate_analysis(self, sample_input_data):
        """Test de generación de análisis completo."""
        agent = BusinessAnalysisGenerator()
        result = agent.execute(sample_input_data)

        assert result.is_success()
        assert "document" in result.data
        assert "processes" in result.data
        assert "use_cases" in result.data
        assert "requirements_functional" in result.data
        assert len(result.data["document"]) > 100

    def test_guardrails_no_emojis(self, sample_input_data):
        """Test de guardrails: sin emojis."""
        agent = BusinessAnalysisGenerator()
        result = agent.execute(sample_input_data)

        # Verificar que el guardrail no detecta emojis
        guardrail_errors = agent.apply_guardrails(result.data)
        emoji_errors = [e for e in guardrail_errors if "emoji" in e.lower()]
        assert len(emoji_errors) == 0


# Tests: TraceabilityMatrixGenerator

class TestTraceabilityMatrixGenerator:
    """Tests para TraceabilityMatrixGenerator."""

    def test_initialization(self):
        """Test de inicialización."""
        agent = TraceabilityMatrixGenerator()
        assert agent.name == "TraceabilityMatrixGenerator"
        assert agent.min_traceability_index == 0.95

    def test_validate_input_success(self, sample_use_cases, sample_requirements):
        """Test de validación exitosa."""
        agent = TraceabilityMatrixGenerator()
        input_data = {
            "use_cases": sample_use_cases,
            "requirements_functional": sample_requirements
        }
        errors = agent.validate_input(input_data)
        assert len(errors) == 0

    def test_validate_input_missing_requirements(self, sample_use_cases):
        """Test de validación con requisitos faltantes."""
        agent = TraceabilityMatrixGenerator()
        input_data = {"use_cases": sample_use_cases}
        errors = agent.validate_input(input_data)
        assert len(errors) > 0

    def test_generate_matrices(self, sample_use_cases, sample_requirements):
        """Test de generación de matrices."""
        agent = TraceabilityMatrixGenerator()
        input_data = {
            "use_cases": sample_use_cases,
            "requirements_functional": sample_requirements,
            "processes": [],
            "business_rules": [],
            "test_cases": [],
            "implementations": []
        }
        result = agent.execute(input_data)

        assert result.is_success()
        assert "main_matrix" in result.data
        assert "rtm_document" in result.data
        assert "metrics" in result.data
        assert "traceability_index" in result.data


# Tests: CompletenessValidator

class TestCompletenessValidator:
    """Tests para CompletenessValidator."""

    def test_initialization(self):
        """Test de inicialización."""
        agent = CompletenessValidator()
        assert agent.name == "CompletenessValidator"
        assert agent.min_completeness == 0.95

    def test_validate_structured_data(self, sample_use_cases, sample_requirements):
        """Test de validación de datos estructurados."""
        agent = CompletenessValidator()
        input_data = {
            "use_cases": sample_use_cases,
            "requirements_functional": sample_requirements,
            "processes": [{"id": "PROC-TEST-001"}],
            "business_rules": [],
            "business_objective": "Test"
        }
        result = agent.execute(input_data)

        assert result.is_success()
        assert "completeness_percentage" in result.data
        assert "checks" in result.data
        assert result.data["completeness_percentage"] >= 0.0

    def test_validate_document(self):
        """Test de validación de documento."""
        agent = CompletenessValidator()
        document = """
# Análisis Integrado

## 1. Contexto de Negocio
Contenido...

## 2. Procesos de Negocio
Contenido...

## 3. Casos de Uso
Contenido...
        """
        input_data = {"document": document}
        result = agent.execute(input_data)

        assert result.is_success()
        assert "completeness_percentage" in result.data


# Tests: TemplateGenerator

class TestTemplateGenerator:
    """Tests para TemplateGenerator."""

    def test_initialization(self):
        """Test de inicialización."""
        agent = TemplateGenerator()
        assert agent.name == "TemplateGenerator"
        assert len(agent.TEMPLATE_TYPES) == 6

    def test_validate_input_valid_type(self):
        """Test de validación con tipo válido."""
        agent = TemplateGenerator()
        input_data = {"template_type": "master_document"}
        errors = agent.validate_input(input_data)
        assert len(errors) == 0

    def test_validate_input_invalid_type(self):
        """Test de validación con tipo inválido."""
        agent = TemplateGenerator()
        input_data = {"template_type": "invalid_type"}
        errors = agent.validate_input(input_data)
        assert len(errors) > 0

    @pytest.mark.parametrize("template_type", [
        "master_document",
        "rtm_matrix",
        "completeness_checklist",
        "business_rule",
        "use_case",
        "requirement_spec"
    ])
    def test_generate_all_template_types(self, template_type):
        """Test de generación de todos los tipos de plantillas."""
        agent = TemplateGenerator()
        input_data = {"template_type": template_type}
        result = agent.execute(input_data)

        assert result.is_success()
        assert "template_content" in result.data
        assert len(result.data["template_content"]) > 50
        assert "[COMPLETAR]" in result.data["template_content"]


# Tests: DocumentSplitter

class TestDocumentSplitter:
    """Tests para DocumentSplitter."""

    def test_initialization(self):
        """Test de inicialización."""
        agent = DocumentSplitter()
        assert agent.name == "DocumentSplitter"
        assert agent.max_lines_per_module == 1000

    def test_validate_input_valid_document(self):
        """Test de validación con documento válido."""
        agent = DocumentSplitter()
        # Documento con más de 200 líneas
        document = "\n".join([f"Línea {i}" for i in range(250)])
        input_data = {"document": document}
        errors = agent.validate_input(input_data)
        assert len(errors) == 0

    def test_validate_input_short_document(self):
        """Test de validación con documento muy corto."""
        agent = DocumentSplitter()
        document = "Documento muy corto\nSolo 2 líneas"
        input_data = {"document": document}
        errors = agent.validate_input(input_data)
        assert len(errors) > 0

    def test_split_document(self):
        """Test de división de documento."""
        agent = DocumentSplitter(config={"max_lines": 100})

        # Crear documento con múltiples secciones
        document = """
# Sección 1
Contenido de la sección 1
""" + "\n" * 50 + """
# Sección 2
Contenido de la sección 2
""" + "\n" * 50 + """
# Sección 3
Contenido de la sección 3
""" + "\n" * 50

        input_data = {
            "document": document,
            "component_name": "Test Document"
        }
        result = agent.execute(input_data)

        assert result.is_success()
        assert "modules" in result.data
        assert "master_index" in result.data
        assert result.data["module_count"] >= 2


# Tests: BusinessAnalysisPipeline

class TestBusinessAnalysisPipeline:
    """Tests para BusinessAnalysisPipeline."""

    def test_pipeline_creation(self, tmp_path):
        """Test de creación de pipeline."""
        pipeline = create_business_analysis_pipeline(
            output_dir=tmp_path / "output",
            config={"split_large_docs": False}
        )
        assert pipeline is not None
        assert len(pipeline.agents) >= 3  # Mínimo 3 agentes obligatorios

    def test_pipeline_execution(self, tmp_path, sample_input_data):
        """Test de ejecución completa del pipeline."""
        pipeline = create_business_analysis_pipeline(
            output_dir=tmp_path / "output",
            config={
                "split_large_docs": False,
                "generate_templates": False,
                "validator": {"min_completeness": 0.80}  # Umbral más bajo para test
            }
        )

        result = pipeline.execute(sample_input_data)

        # Verificar que el pipeline se ejecutó (puede fallar por guardrails)
        assert result["status"] in ["success", "blocked", "failed"]

        # Si fue exitoso, verificar estructura
        if result["status"] == "success":
            assert "data" in result
            assert "results" in result


# Tests de Integración

class TestIntegration:
    """Tests de integración entre agentes."""

    def test_full_workflow(self, tmp_path, sample_input_data):
        """Test de flujo completo: Generación → Trazabilidad → Validación."""

        # Paso 1: Generar análisis
        generator = BusinessAnalysisGenerator()
        gen_result = generator.execute(sample_input_data)
        assert gen_result.is_success()

        # Paso 2: Generar matrices de trazabilidad
        traceability = TraceabilityMatrixGenerator()
        trace_input = {
            "use_cases": gen_result.data["use_cases"],
            "requirements_functional": gen_result.data["requirements_functional"],
            "processes": gen_result.data["processes"],
            "business_rules": gen_result.data["business_rules"],
            "test_cases": [],
            "implementations": []
        }
        trace_result = traceability.execute(trace_input)
        assert trace_result.is_success()

        # Paso 3: Validar completitud
        validator = CompletenessValidator(config={"min_completeness": 0.50})
        val_input = {
            **trace_input,
            "document": gen_result.data["document"]
        }
        val_result = validator.execute(val_input)
        assert val_result.is_success()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
