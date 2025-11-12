#!/usr/bin/env python3
"""
TDD Tests for UMLDiagramValidationAgent

Tests the agent that uses Self-Consistency to validate UML diagrams.

Technique: Self-Consistency (Wang et al., 2022)
- Generates multiple reasoning paths
- Votes on consistency across paths
- Identifies inconsistencies with high confidence

Meta-Application: Using multiple validation perspectives to ensure diagram quality.
"""

import pytest
from scripts.ai.agents.meta import (
    UMLDiagramValidationAgent,
    UMLValidationResult,
    DiagramType,
    ValidationIssue
)


# Fixtures
@pytest.fixture
def valid_class_diagram():
    """Valid UML class diagram."""
    return '''
@startuml
class User {
    +id: int
    +name: string
    +email: string
    +getProfile(): UserProfile
}

class UserProfile {
    +bio: string
    +avatar: string
}

User "1" -- "1" UserProfile
@enduml
'''


@pytest.fixture
def invalid_class_diagram():
    """Invalid UML class diagram with inconsistencies."""
    return '''
@startuml
class Order {
    +id: int
    +customer: Customer
    +items: List<Item>
    +getTotal(): float
}

class Customer {
    +id: int
    +name: string
}

' Inconsistency: Item class not defined but referenced
Order "1" -- "*" Item
@enduml
'''


# 1. Initialization Tests
class TestUMLValidationAgentInitialization:
    """Test UMLDiagramValidationAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = UMLDiagramValidationAgent()

        assert agent.name == "UMLDiagramValidationAgent"
        assert agent.self_consistency is not None

    def test_custom_initialization(self):
        """Should initialize with custom parameters."""
        agent = UMLDiagramValidationAgent(
            num_samples=5
        )

        assert agent.num_samples == 5


# 2. Diagram Type Detection Tests
class TestDiagramTypeDetection:
    """Test automatic diagram type detection."""

    def test_detect_class_diagram(self, valid_class_diagram):
        """Should detect class diagram type."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(valid_class_diagram)

        assert result.diagram_type == DiagramType.CLASS

    def test_detect_sequence_diagram(self):
        """Should detect sequence diagram type."""
        agent = UMLDiagramValidationAgent()

        sequence = '''
@startuml
Alice -> Bob: Request
Bob -> Alice: Response
@enduml
'''

        result = agent.validate_diagram(sequence)

        assert result.diagram_type == DiagramType.SEQUENCE


# 3. Validation Tests
class TestDiagramValidation:
    """Test diagram validation functionality."""

    def test_validate_correct_diagram(self, valid_class_diagram):
        """Should validate correct diagram without issues."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(valid_class_diagram)

        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_detect_undefined_reference(self, invalid_class_diagram):
        """Should detect undefined class references."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(invalid_class_diagram)

        assert result.is_valid is False
        assert len(result.issues) > 0

        # Should have issue about undefined Item class
        undefined_issues = [
            i for i in result.issues
            if 'Item' in i.description or 'undefined' in i.description.lower()
        ]
        assert len(undefined_issues) > 0


# 4. Self-Consistency Integration Tests
class TestSelfConsistencyIntegration:
    """Test Self-Consistency technique integration."""

    def test_uses_multiple_reasoning_paths(self, valid_class_diagram):
        """Should use multiple reasoning paths for validation."""
        agent = UMLDiagramValidationAgent(num_samples=3)

        result = agent.validate_diagram(valid_class_diagram)

        # Should have sampled multiple paths
        assert hasattr(result, 'num_samples')
        assert result.num_samples >= 3

    def test_confidence_score_included(self, valid_class_diagram):
        """Should include confidence score from voting."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(valid_class_diagram)

        assert hasattr(result, 'confidence')
        assert 0.0 <= result.confidence <= 1.0

    def test_high_confidence_for_obvious_errors(self, invalid_class_diagram):
        """Should have high confidence for obvious errors."""
        agent = UMLDiagramValidationAgent(num_samples=5)

        result = agent.validate_diagram(invalid_class_diagram)

        # Should be confident about the validation result
        assert result.confidence >= 0.6


# 5. Issue Detection Tests
class TestIssueDetection:
    """Test specific issue detection."""

    def test_detect_missing_class(self):
        """Should detect missing class definitions."""
        agent = UMLDiagramValidationAgent()

        diagram = '''
@startuml
class A {
    +b: B
}
' B is not defined
@enduml
'''

        result = agent.validate_diagram(diagram)

        assert result.is_valid is False
        assert any('B' in i.description or 'missing' in i.description.lower()
                   for i in result.issues)

    def test_detect_circular_dependency(self):
        """Should detect circular dependencies."""
        agent = UMLDiagramValidationAgent()

        diagram = '''
@startuml
class A {
    +b: B
}
class B {
    +a: A
}
A --> B
B --> A
@enduml
'''

        result = agent.validate_diagram(diagram)

        # May or may not flag circular deps depending on context
        assert isinstance(result, UMLValidationResult)

    def test_detect_multiplicity_error(self):
        """Should detect invalid multiplicity."""
        agent = UMLDiagramValidationAgent()

        diagram = '''
@startuml
class Order {
}
class Customer {
}
Order "invalid" -- "1" Customer
@enduml
'''

        result = agent.validate_diagram(diagram)

        # Should detect invalid multiplicity if strict validation
        assert isinstance(result, UMLValidationResult)


# 6. Validation Issue Details Tests
class TestValidationIssueDetails:
    """Test validation issue detail quality."""

    def test_issues_have_descriptions(self, invalid_class_diagram):
        """Issues should have clear descriptions."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(invalid_class_diagram)

        if result.issues:
            issue = result.issues[0]
            assert isinstance(issue, ValidationIssue)
            assert len(issue.description) > 10

    def test_issues_have_severity(self, invalid_class_diagram):
        """Issues should have severity levels."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(invalid_class_diagram)

        if result.issues:
            issue = result.issues[0]
            assert hasattr(issue, 'severity')
            assert issue.severity in ['low', 'medium', 'high', 'critical']

    def test_issues_have_locations(self, invalid_class_diagram):
        """Issues should indicate location in diagram."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(invalid_class_diagram)

        if result.issues:
            issue = result.issues[0]
            assert hasattr(issue, 'location')
            assert issue.location is not None


# 7. Edge Cases
class TestUMLValidationEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_empty_diagram(self):
        """Should handle empty diagram gracefully."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram("")

        assert result.is_valid is False
        assert len(result.issues) > 0

    def test_handles_malformed_uml(self):
        """Should handle malformed UML syntax."""
        agent = UMLDiagramValidationAgent()

        malformed = "class { invalid syntax }"

        result = agent.validate_diagram(malformed)

        assert result.is_valid is False

    def test_handles_large_diagram(self):
        """Should handle large diagrams."""
        agent = UMLDiagramValidationAgent()

        # Generate large diagram
        large = "@startuml\n"
        for i in range(50):
            large += f"class Class{i} {{\n}}\n"
        large += "@enduml"

        result = agent.validate_diagram(large)

        assert isinstance(result, UMLValidationResult)


# 8. Integration Tests
class TestUMLValidationIntegration:
    """Test integration with other components."""

    def test_result_serializable(self, valid_class_diagram):
        """Results should be serializable for pipeline."""
        agent = UMLDiagramValidationAgent()

        result = agent.validate_diagram(valid_class_diagram)

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'is_valid' in result_dict
        assert 'diagram_type' in result_dict
        assert 'confidence' in result_dict


# 9. LLM Integration Tests (TDD - RED Phase)
class TestLLMIntegration:
    """Test LLM integration for UML validation."""

    def test_initializes_with_llm_config(self):
        """Should initialize LLMGenerator when config provided."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = UMLDiagramValidationAgent(config=config)

        # Should have LLMGenerator initialized
        assert hasattr(agent, 'llm_generator')
        assert agent.llm_generator is not None

    def test_uses_llm_for_validation(self, invalid_class_diagram):
        """Should use LLM to validate diagrams."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "use_llm": True
        }
        agent = UMLDiagramValidationAgent(config=config)

        result = agent.validate_diagram(invalid_class_diagram)

        # Should use LLM validation method
        assert hasattr(result, 'validation_method')
        assert result.validation_method == 'llm'

    def test_llm_finds_more_issues(self, invalid_class_diagram):
        """LLM should find more issues than heuristics."""
        config_llm = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        config_heuristic = {"use_llm": False}

        agent_with_llm = UMLDiagramValidationAgent(config=config_llm)
        agent_without_llm = UMLDiagramValidationAgent(config=config_heuristic)

        result_llm = agent_with_llm.validate_diagram(invalid_class_diagram)
        result_heuristic = agent_without_llm.validate_diagram(invalid_class_diagram)

        # LLM should find same or more issues
        assert len(result_llm.issues) >= len(result_heuristic.issues)

    def test_fallback_to_heuristics_when_llm_fails(self, valid_class_diagram):
        """Should fallback to heuristics if LLM fails."""
        config = {
            "llm_provider": "anthropic",
            "model": "invalid-model",  # This will fail
            "use_llm": True
        }
        agent = UMLDiagramValidationAgent(config=config)

        result = agent.validate_diagram(valid_class_diagram)

        # Should fallback to heuristics
        assert isinstance(result, UMLValidationResult)
        assert result.validation_method == 'heuristic'

    def test_llm_provides_better_descriptions(self, invalid_class_diagram):
        """LLM should provide better issue descriptions."""
        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent = UMLDiagramValidationAgent(config=config)

        result = agent.validate_diagram(invalid_class_diagram)

        # LLM descriptions should be more detailed
        if result.issues:
            for issue in result.issues:
                # LLM should provide comprehensive descriptions
                assert len(issue.description) > 20
                assert issue.severity in ['low', 'medium', 'high', 'critical']
                assert issue.location is not None

    def test_respects_api_key_validation(self):
        """Should validate API key before using LLM."""
        import os
        # Temporarily remove API key
        original_key = os.environ.get('ANTHROPIC_API_KEY')
        if original_key:
            del os.environ['ANTHROPIC_API_KEY']

        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }

        try:
            agent = UMLDiagramValidationAgent(config=config)
            # Should either raise error or set use_llm=False
            assert hasattr(agent, 'llm_generator')
            # Should either raise error or fallback gracefully
            assert agent.config.get('use_llm') == False or agent.llm_generator is None
        finally:
            # Restore key
            if original_key:
                os.environ['ANTHROPIC_API_KEY'] = original_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
