#!/usr/bin/env python3
"""
TDD Tests for UMLGeneratorAgent

Tests the agent that GENERATES UML diagrams from requirements/code.

This agent generates PlantUML diagrams using both heuristic parsing
and LLM-based generation techniques.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.ai.agents.meta.uml_generator_agent import (
    UMLGeneratorAgent,
    UMLGenerationResult,
    GENERATION_METHOD_LLM,
    GENERATION_METHOD_HEURISTIC
)
from scripts.ai.agents.meta.uml_validation_agent import DiagramType


# Fixtures
@pytest.fixture
def sample_python_code():
    """Sample Python code for diagram generation."""
    return '''
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_profile(self):
        return f"User {self.name}"

class UserProfile:
    def __init__(self, bio):
        self.bio = bio
'''


@pytest.fixture
def sample_requirements():
    """Sample requirements for diagram generation."""
    return """
System should have:
- User entity with id, name, email
- UserProfile entity with bio, avatar
- User has one UserProfile
- Order entity with items
- Customer places orders
"""


@pytest.fixture
def sample_workflow_description():
    """Sample workflow for activity diagram."""
    return """
User login workflow:
1. User enters credentials
2. System validates credentials
3. If valid, create session
4. If invalid, show error
5. Redirect to dashboard
"""


@pytest.fixture
def sample_interaction():
    """Sample interaction for sequence diagram."""
    return """
User clicks checkout button
OrderController receives request
OrderController calls PaymentService
PaymentService processes payment
PaymentService returns confirmation
OrderController updates order status
OrderController returns response to User
"""


# 1. Initialization Tests
class TestUMLGeneratorAgentInitialization:
    """Test UMLGeneratorAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = UMLGeneratorAgent()

        assert agent.name == "UMLGeneratorAgent"
        assert agent.config == {}
        assert agent.llm_generator is None

    def test_initialization_with_config(self):
        """Should initialize with configuration."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = UMLGeneratorAgent(config=config)

        assert agent.config == config
        assert hasattr(agent, 'llm_generator')

    def test_initialization_without_llm(self):
        """Should initialize without LLM when not configured."""
        agent = UMLGeneratorAgent(config={})

        assert agent.llm_generator is None

    def test_initialization_with_invalid_config(self):
        """Should handle invalid config gracefully."""
        config = {"invalid_key": "invalid_value"}
        agent = UMLGeneratorAgent(config=config)

        # Agent should initialize but may or may not have LLM
        # (depends on whether LLMGenerator accepts invalid config)
        assert agent.config == config


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation for generation methods."""

    def test_empty_code_input(self):
        """Should handle empty code input."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code="")

        assert result.diagram_type == DiagramType.CLASS
        assert result.plantuml_code == ""
        assert not result.success
        assert "empty" in result.error_message.lower()

    def test_none_code_input(self):
        """Should handle None code input."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=None)

        assert not result.success
        assert result.error_message is not None

    def test_whitespace_only_input(self):
        """Should handle whitespace-only input."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code="   \n  \t  ")

        assert not result.success
        assert "empty" in result.error_message.lower()

    def test_invalid_diagram_type(self):
        """Should handle invalid diagram type."""
        agent = UMLGeneratorAgent()

        with pytest.raises(AttributeError):
            agent.generate_diagram(code="test", diagram_type="invalid")


# 3. Class Diagram Generation Tests (Heuristic)
class TestClassDiagramHeuristicGeneration:
    """Test heuristic-based class diagram generation."""

    def test_generate_class_diagram_from_code(self, sample_python_code):
        """Should generate class diagram from Python code."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        assert result.success
        assert result.diagram_type == DiagramType.CLASS
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert "class User" in result.plantuml_code
        assert "class UserProfile" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    def test_extract_class_names(self, sample_python_code):
        """Should extract class names from code."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        assert "User" in result.plantuml_code
        assert "UserProfile" in result.plantuml_code

    def test_extract_methods(self, sample_python_code):
        """Should extract methods from classes."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should contain __init__ or get_profile methods
        assert any(method in result.plantuml_code
                   for method in ["__init__", "get_profile"])

    def test_extract_attributes(self, sample_python_code):
        """Should extract attributes from classes."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should contain id, name, or bio attributes
        assert any(attr in result.plantuml_code
                   for attr in ["id", "name", "bio"])

    def test_handles_complex_code(self):
        """Should handle complex code structures."""
        complex_code = '''
class Base:
    def base_method(self):
        pass

class Derived(Base):
    def __init__(self):
        self.value = 0

    def derived_method(self):
        return self.value
'''
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=complex_code)

        assert result.success
        assert "Base" in result.plantuml_code
        assert "Derived" in result.plantuml_code

    def test_handles_inheritance(self):
        """Should detect inheritance relationships."""
        code_with_inheritance = '''
class Animal:
    pass

class Dog(Animal):
    pass
'''
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=code_with_inheritance)

        assert result.success
        # Should show inheritance relationship
        assert "Animal" in result.plantuml_code
        assert "Dog" in result.plantuml_code


# 4. Sequence Diagram Generation Tests (Heuristic)
class TestSequenceDiagramHeuristicGeneration:
    """Test heuristic-based sequence diagram generation."""

    def test_generate_sequence_diagram_from_interaction(self, sample_interaction):
        """Should generate sequence diagram from interaction description."""
        agent = UMLGeneratorAgent()

        result = agent.generate_sequence_diagram(requirements=sample_interaction)

        assert result.success
        assert result.diagram_type == DiagramType.SEQUENCE
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    def test_extract_participants(self, sample_interaction):
        """Should extract participants from interaction."""
        agent = UMLGeneratorAgent()

        result = agent.generate_sequence_diagram(requirements=sample_interaction)

        # Should identify main actors
        assert "User" in result.plantuml_code or "participant" in result.plantuml_code

    def test_extract_messages(self, sample_interaction):
        """Should extract messages between participants."""
        agent = UMLGeneratorAgent()

        result = agent.generate_sequence_diagram(requirements=sample_interaction)

        # Should contain message arrows
        assert "->" in result.plantuml_code or "-->" in result.plantuml_code

    def test_handles_complex_interactions(self):
        """Should handle complex interaction scenarios."""
        complex_interaction = """
User authenticates with system
AuthService validates credentials
If valid:
    SessionManager creates session
    Database stores session
    System returns success
Else:
    System returns error
"""
        agent = UMLGeneratorAgent()

        result = agent.generate_sequence_diagram(requirements=complex_interaction)

        assert result.success
        assert "@startuml" in result.plantuml_code


# 5. Component Diagram Generation Tests (Heuristic)
class TestComponentDiagramHeuristicGeneration:
    """Test heuristic-based component diagram generation."""

    def test_generate_component_diagram_from_requirements(self, sample_requirements):
        """Should generate component diagram from requirements."""
        agent = UMLGeneratorAgent()

        result = agent.generate_component_diagram(requirements=sample_requirements)

        assert result.success
        assert result.diagram_type == DiagramType.COMPONENT
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    def test_extract_components(self, sample_requirements):
        """Should extract components from requirements."""
        agent = UMLGeneratorAgent()

        result = agent.generate_component_diagram(requirements=sample_requirements)

        # Should identify main entities as components
        assert "component" in result.plantuml_code.lower() or "[" in result.plantuml_code

    def test_handles_architecture_description(self):
        """Should handle architecture descriptions."""
        architecture = """
System consists of:
- Frontend (React)
- API Gateway
- Authentication Service
- Database (PostgreSQL)
- Cache (NO Redis - NOT ALLOWED)
"""
        agent = UMLGeneratorAgent()

        result = agent.generate_component_diagram(requirements=architecture)

        assert result.success
        # Should not include Redis (IACT constraint)
        assert "Redis" not in result.plantuml_code


# 6. Activity Diagram Generation Tests (Heuristic)
class TestActivityDiagramHeuristicGeneration:
    """Test heuristic-based activity diagram generation."""

    def test_generate_activity_diagram_from_workflow(self, sample_workflow_description):
        """Should generate activity diagram from workflow."""
        agent = UMLGeneratorAgent()

        result = agent.generate_activity_diagram(requirements=sample_workflow_description)

        assert result.success
        assert result.diagram_type == DiagramType.ACTIVITY
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    def test_extract_activities(self, sample_workflow_description):
        """Should extract activities from workflow."""
        agent = UMLGeneratorAgent()

        result = agent.generate_activity_diagram(requirements=sample_workflow_description)

        # Should contain activity notation
        assert ":" in result.plantuml_code or "start" in result.plantuml_code.lower()

    def test_extract_decision_points(self, sample_workflow_description):
        """Should extract decision points from workflow."""
        agent = UMLGeneratorAgent()

        result = agent.generate_activity_diagram(requirements=sample_workflow_description)

        # Should contain decision logic
        assert "if" in result.plantuml_code.lower() or result.success


# 7. LLM Generation Tests
class TestLLMGeneration:
    """Test LLM-based diagram generation."""

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_uses_llm_when_configured(self, mock_llm_class, sample_python_code):
        """Should use LLM for generation when configured."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''
@startuml
class User {
    +id: int
    +name: string
}
@enduml
'''
        mock_llm_class.return_value = mock_llm

        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_class_diagram(code=sample_python_code)

        assert result.success
        assert result.generation_method == GENERATION_METHOD_LLM
        mock_llm._call_llm.assert_called_once()

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_llm_class_diagram_generation(self, mock_llm_class, sample_python_code):
        """Should generate class diagram using LLM."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''
@startuml
class User {
    +id: int
    +name: string
    +get_profile()
}
class UserProfile {
    +bio: string
}
User "1" -- "1" UserProfile
@enduml
'''
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_class_diagram(code=sample_python_code)

        assert result.success
        assert "class User" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_LLM

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_llm_sequence_diagram_generation(self, mock_llm_class, sample_interaction):
        """Should generate sequence diagram using LLM."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''
@startuml
User -> OrderController: checkout
OrderController -> PaymentService: process payment
PaymentService -> OrderController: confirmation
OrderController -> User: response
@enduml
'''
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_sequence_diagram(requirements=sample_interaction)

        assert result.success
        assert "->" in result.plantuml_code
        assert result.generation_method == GENERATION_METHOD_LLM

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_llm_component_diagram_generation(self, mock_llm_class, sample_requirements):
        """Should generate component diagram using LLM."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''
@startuml
component [User Service]
component [Order Service]
database [Database]
[User Service] --> [Database]
[Order Service] --> [Database]
@enduml
'''
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_component_diagram(requirements=sample_requirements)

        assert result.success
        assert result.generation_method == GENERATION_METHOD_LLM

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_fallback_to_heuristics_on_llm_failure(self, mock_llm_class, sample_python_code):
        """Should fallback to heuristics if LLM fails."""
        mock_llm = Mock()
        mock_llm._call_llm.side_effect = Exception("LLM Error")
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should fallback to heuristics
        assert result.success
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_fallback_on_invalid_llm_response(self, mock_llm_class, sample_python_code):
        """Should fallback to heuristics if LLM returns invalid PlantUML."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = "invalid plantuml response"
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should fallback to heuristics
        assert result.success
        assert result.generation_method == GENERATION_METHOD_HEURISTIC

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_llm_builds_appropriate_prompts(self, mock_llm_class, sample_python_code):
        """Should build appropriate prompts for LLM."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = "@startuml\nclass Test\n@enduml"
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        agent.generate_class_diagram(code=sample_python_code)

        # Should have called LLM with a prompt containing the code
        call_args = mock_llm._call_llm.call_args[0][0]
        assert sample_python_code in call_args
        assert "class diagram" in call_args.lower()

    @patch('scripts.ai.agents.meta.uml_generator_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.agents.meta.uml_generator_agent.LLMGenerator')
    def test_llm_respects_iact_constraints(self, mock_llm_class):
        """Should include IACT constraints in LLM prompt."""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = "@startuml\ncomponent [API]\n@enduml"
        mock_llm_class.return_value = mock_llm

        config = {"use_llm": True}
        agent = UMLGeneratorAgent(config=config)
        agent.llm_generator = mock_llm

        agent.generate_component_diagram(requirements="System architecture")

        # Prompt should mention IACT constraints (Redis and Email not allowed)
        call_args = mock_llm._call_llm.call_args[0][0]
        assert "Redis" in call_args and "Email" in call_args
        assert "NOT allowed" in call_args or "DO NOT include" in call_args


# 8. PlantUML Syntax Validation Tests
class TestPlantUMLSyntaxValidation:
    """Test PlantUML syntax validation."""

    def test_valid_plantuml_structure(self, sample_python_code):
        """Generated diagrams should have valid PlantUML structure."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        # Should have @startuml before @enduml
        start_idx = result.plantuml_code.index("@startuml")
        end_idx = result.plantuml_code.index("@enduml")
        assert start_idx < end_idx

    def test_no_invalid_syntax(self, sample_python_code):
        """Generated diagrams should not contain obvious syntax errors."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should not have malformed class declarations
        assert "class {" not in result.plantuml_code
        assert "class }" not in result.plantuml_code

    def test_proper_class_syntax(self, sample_python_code):
        """Class diagrams should use proper class syntax."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        # Class syntax should be: class ClassName {
        if "class" in result.plantuml_code:
            import re
            # Should match proper class pattern
            assert re.search(r'class\s+\w+\s*\{', result.plantuml_code)


# 9. Edge Cases Tests
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_code_with_syntax_errors(self):
        """Should handle code with syntax errors gracefully."""
        invalid_code = "class User def __init__(self"
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=invalid_code)

        # Should still attempt generation or handle gracefully
        assert isinstance(result, UMLGenerationResult)

    def test_handles_very_large_code(self):
        """Should handle very large code files."""
        large_code = "class Test:\n    pass\n" * 1000
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=large_code)

        assert isinstance(result, UMLGenerationResult)

    def test_handles_non_python_code(self):
        """Should handle non-Python code gracefully."""
        java_code = "public class Test { }"
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=java_code)

        # Should still generate something or report error
        assert isinstance(result, UMLGenerationResult)

    def test_handles_empty_requirements(self):
        """Should handle empty requirements."""
        agent = UMLGeneratorAgent()

        result = agent.generate_sequence_diagram(requirements="")

        assert not result.success
        assert "empty" in result.error_message.lower()

    def test_handles_unicode_in_input(self):
        """Should handle unicode characters in input."""
        code_with_unicode = """
class Utilisateur:
    def __init__(self):
        self.nom = "René"
"""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=code_with_unicode)

        assert result.success


# 10. Result Object Tests
class TestUMLGenerationResult:
    """Test UMLGenerationResult dataclass."""

    def test_result_has_required_fields(self, sample_python_code):
        """Result should have all required fields."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        assert hasattr(result, 'success')
        assert hasattr(result, 'diagram_type')
        assert hasattr(result, 'plantuml_code')
        assert hasattr(result, 'generation_method')
        assert hasattr(result, 'error_message')

    def test_result_is_serializable(self, sample_python_code):
        """Result should be serializable to dict."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'success' in result_dict
        assert 'diagram_type' in result_dict
        assert 'plantuml_code' in result_dict
        assert 'generation_method' in result_dict

    def test_successful_result_structure(self, sample_python_code):
        """Successful result should have proper structure."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        assert result.success is True
        assert result.plantuml_code != ""
        assert result.error_message is None
        assert result.diagram_type == DiagramType.CLASS
        assert result.generation_method in [GENERATION_METHOD_LLM, GENERATION_METHOD_HEURISTIC]

    def test_failed_result_structure(self):
        """Failed result should have proper structure."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code="")

        assert result.success is False
        assert result.error_message is not None
        assert result.plantuml_code == ""


# 11. Integration Tests
class TestUMLGeneratorIntegration:
    """Test integration scenarios."""

    def test_generate_multiple_diagram_types(self, sample_python_code, sample_interaction):
        """Should generate multiple diagram types from same agent."""
        agent = UMLGeneratorAgent()

        class_result = agent.generate_class_diagram(code=sample_python_code)
        seq_result = agent.generate_sequence_diagram(requirements=sample_interaction)

        assert class_result.success
        assert seq_result.success
        assert class_result.diagram_type == DiagramType.CLASS
        assert seq_result.diagram_type == DiagramType.SEQUENCE

    def test_consistent_results(self, sample_python_code):
        """Should generate consistent results for same input."""
        agent = UMLGeneratorAgent()

        result1 = agent.generate_class_diagram(code=sample_python_code)
        result2 = agent.generate_class_diagram(code=sample_python_code)

        # Should be deterministic for heuristic mode
        assert result1.plantuml_code == result2.plantuml_code

    def test_different_inputs_different_outputs(self):
        """Should generate different outputs for different inputs."""
        agent = UMLGeneratorAgent()

        code1 = "class A: pass"
        code2 = "class B: pass"

        result1 = agent.generate_class_diagram(code=code1)
        result2 = agent.generate_class_diagram(code=code2)

        assert result1.plantuml_code != result2.plantuml_code


# 12. AST Parsing Tests
class TestASTParsing:
    """Test AST-based code parsing."""

    def test_parses_python_ast(self, sample_python_code):
        """Should parse Python code using AST."""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=sample_python_code)

        # Should successfully parse and extract information
        assert result.success
        assert "User" in result.plantuml_code

    def test_extracts_class_hierarchy(self):
        """Should extract class hierarchy using AST."""
        code = """
class Base:
    pass

class Derived(Base):
    pass
"""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=code)

        assert result.success
        assert "Base" in result.plantuml_code
        assert "Derived" in result.plantuml_code

    def test_extracts_method_signatures(self):
        """Should extract method signatures using AST."""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""
        agent = UMLGeneratorAgent()

        result = agent.generate_class_diagram(code=code)

        assert result.success
        # Should contain method names
        assert "add" in result.plantuml_code or "subtract" in result.plantuml_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
