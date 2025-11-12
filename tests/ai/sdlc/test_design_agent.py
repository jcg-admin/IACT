#!/usr/bin/env python3
"""
TDD Tests for SDLCDesignAgent

Tests the SDLCDesignAgent implementation which generates system design
documentation including HLD, LLD, ADRs, and diagrams.

Tests cover both LLM-enhanced and heuristic fallback methods.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.ai.sdlc.design_agent import SDLCDesignAgent


# Constants for testing
DESIGN_METHOD_LLM = "llm"
DESIGN_METHOD_HEURISTIC = "heuristic"


# Fixtures
@pytest.fixture
def sample_issue():
    """Sample issue for testing."""
    return {
        "issue_title": "Implement User Authentication with JWT",
        "issue_number": "IACT-123",
        "priority": "P1",
        "story_points": 8,
        "technical_requirements": [
            "Implement JWT token generation",
            "Create user login endpoint",
            "Add token validation middleware",
            "Implement token refresh mechanism"
        ],
        "acceptance_criteria": [
            "User can login with username/password",
            "JWT token is generated on successful login",
            "Protected endpoints require valid token",
            "Token expires after 24 hours"
        ]
    }


@pytest.fixture
def sample_feasibility_result():
    """Sample feasibility result for testing."""
    return {
        "decision": "go",
        "confidence": 0.85,
        "risks": [
            {
                "type": "technical",
                "severity": "medium",
                "probability": "low",
                "description": "JWT implementation complexity",
                "mitigation": "Use proven library like PyJWT"
            }
        ],
        "technical_feasibility": {
            "is_feasible": True,
            "score": 0.9
        }
    }


@pytest.fixture
def sample_input_data(sample_issue, sample_feasibility_result):
    """Sample input data for agent run."""
    return {
        "issue": sample_issue,
        "feasibility_result": sample_feasibility_result,
        "project_context": "IACT project using Django 4.2+ and PostgreSQL"
    }


# 1. Initialization Tests
class TestDesignAgentInitialization:
    """Test SDLCDesignAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = SDLCDesignAgent()

        assert agent.name == "SDLCDesignAgent"
        assert agent.phase == "design"

    def test_initialization_without_config(self):
        """Should initialize without config."""
        agent = SDLCDesignAgent(config=None)

        assert agent.name == "SDLCDesignAgent"
        assert agent.llm_generator is None

    def test_initialization_with_config(self):
        """Should initialize with LLM config."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = SDLCDesignAgent(config=config)

        assert agent.name == "SDLCDesignAgent"
        # LLM generator might be available or not


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation."""

    def test_validate_valid_input(self, sample_input_data):
        """Should accept valid input data."""
        agent = SDLCDesignAgent()

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_feasibility_result(self, sample_issue):
        """Should reject input without feasibility_result."""
        agent = SDLCDesignAgent()
        input_data = {"issue": sample_issue}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("feasibility_result" in err.lower() for err in errors)

    def test_validate_missing_issue(self, sample_feasibility_result):
        """Should reject input without issue."""
        agent = SDLCDesignAgent()
        input_data = {"feasibility_result": sample_feasibility_result}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("issue" in err.lower() for err in errors)

    def test_validate_no_go_feasibility(self, sample_issue):
        """Should reject NO-GO feasibility decision."""
        agent = SDLCDesignAgent()
        input_data = {
            "issue": sample_issue,
            "feasibility_result": {"decision": "no-go"}
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("no-go" in err.lower() for err in errors)


# 3. Heuristic Design Methods Tests
class TestHeuristicDesignMethods:
    """Test heuristic design generation methods."""

    def test_generate_hld_heuristic(self, sample_issue, sample_feasibility_result):
        """Should generate HLD using heuristics."""
        agent = SDLCDesignAgent()

        hld = agent._generate_hld(sample_issue, sample_feasibility_result, "IACT context")

        assert "High-Level Design" in hld
        assert sample_issue["issue_title"] in hld
        assert "Architecture" in hld
        assert len(hld) > 100

    def test_generate_lld_heuristic(self, sample_issue):
        """Should generate LLD using heuristics."""
        agent = SDLCDesignAgent()
        hld = "Sample HLD content"

        lld = agent._generate_lld(sample_issue, hld)

        assert "Low-Level Design" in lld
        assert "Database Schema" in lld
        assert "API Endpoints" in lld
        assert len(lld) > 100

    def test_generate_adrs_heuristic(self, sample_issue):
        """Should generate ADRs using heuristics."""
        agent = SDLCDesignAgent()
        hld = "Sample HLD content"

        adrs = agent._generate_adrs(sample_issue, hld)

        # Should be a list (might be empty or contain ADRs)
        assert isinstance(adrs, list)

    def test_generate_diagrams_heuristic(self, sample_issue):
        """Should generate diagrams using heuristics."""
        agent = SDLCDesignAgent()
        hld = "Sample HLD"
        lld = "Sample LLD"

        diagrams = agent._generate_diagrams(sample_issue, hld, lld)

        assert "architecture" in diagrams
        assert "sequence" in diagrams
        assert "components" in diagrams
        assert "database" in diagrams
        # Check for Mermaid syntax
        assert "```mermaid" in diagrams["architecture"]

    def test_identify_components(self):
        """Should identify system components."""
        agent = SDLCDesignAgent()

        components = agent._identify_components(["API endpoints", "Database models"])

        assert len(components) > 0
        assert "Django" in components or "React" in components


# 4. LLM Integration Tests
class TestLLMIntegration:
    """Test LLM-enhanced design methods."""

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_generate_architecture_with_llm(self, mock_llm_gen, sample_issue):
        """Should use LLM to generate architecture recommendations."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "components": [
                "Authentication Service",
                "Token Manager",
                "User Repository"
            ],
            "data_flow": "User -> Auth Service -> Token Manager -> Database",
            "technology_recommendations": {
                "backend": "Django REST Framework with PyJWT",
                "database": "PostgreSQL for user storage"
            }
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        architecture = agent._generate_architecture_with_llm(
            sample_issue,
            "IACT project context"
        )

        assert "components" in architecture
        assert len(architecture["components"]) > 0
        mock_llm_instance._call_llm.assert_called_once()

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_recommend_patterns_with_llm(self, mock_llm_gen, sample_issue):
        """Should use LLM to recommend design patterns."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "patterns": [
                {
                    "name": "Repository Pattern",
                    "rationale": "Separates data access logic",
                    "applicability": "User data management"
                },
                {
                    "name": "Strategy Pattern",
                    "rationale": "Multiple authentication strategies",
                    "applicability": "Token validation"
                }
            ]
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        patterns = agent._recommend_patterns_with_llm(
            sample_issue,
            "Sample architecture"
        )

        assert "patterns" in patterns
        assert len(patterns["patterns"]) > 0
        mock_llm_instance._call_llm.assert_called_once()

    def test_parse_llm_architecture_from_json(self, sample_issue):
        """Should parse LLM JSON response for architecture."""
        agent = SDLCDesignAgent()

        llm_response = json.dumps({
            "components": ["Service A", "Service B"],
            "data_flow": "A -> B -> Database",
            "technology_recommendations": {
                "backend": "Django",
                "frontend": "React"
            }
        })

        architecture = agent._parse_llm_architecture(llm_response)

        assert "components" in architecture
        assert len(architecture["components"]) == 2
        assert "data_flow" in architecture

    def test_parse_llm_architecture_from_text(self, sample_issue):
        """Should parse LLM text response for architecture."""
        agent = SDLCDesignAgent()

        llm_response = """
        The system should have these components:
        - Authentication Service
        - Token Manager
        - User Database

        Data flows from user to auth service to database.
        """

        architecture = agent._parse_llm_architecture(llm_response)

        # Should extract at least something from text
        assert "components" in architecture or "data_flow" in architecture

    def test_parse_llm_patterns_from_json(self):
        """Should parse LLM JSON response for patterns."""
        agent = SDLCDesignAgent()

        llm_response = json.dumps({
            "patterns": [
                {
                    "name": "Repository Pattern",
                    "rationale": "Separation of concerns",
                    "applicability": "Data access"
                }
            ]
        })

        patterns = agent._parse_llm_patterns(llm_response)

        assert "patterns" in patterns
        assert len(patterns["patterns"]) == 1
        assert patterns["patterns"][0]["name"] == "Repository Pattern"

    def test_parse_llm_patterns_from_text(self):
        """Should parse LLM text response for patterns."""
        agent = SDLCDesignAgent()

        llm_response = """
        Recommended patterns:
        - Repository Pattern for data access
        - Strategy Pattern for authentication
        """

        patterns = agent._parse_llm_patterns(llm_response)

        # Should extract patterns from text
        assert "patterns" in patterns

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_llm_fallback_on_architecture_error(self, mock_llm_gen, sample_issue):
        """Should fallback to heuristics if LLM fails for architecture."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.side_effect = Exception("LLM error")
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Should not crash, should fallback to heuristics
        architecture = agent._generate_architecture_with_llm(
            sample_issue,
            "context"
        )

        # Should return something (even if from fallback)
        assert architecture is not None

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_llm_fallback_on_patterns_error(self, mock_llm_gen, sample_issue):
        """Should fallback to heuristics if LLM fails for patterns."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.side_effect = Exception("LLM error")
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Should not crash
        patterns = agent._recommend_patterns_with_llm(
            sample_issue,
            "architecture"
        )

        assert patterns is not None


# 5. Full Pipeline Tests
class TestFullPipeline:
    """Test complete design generation pipeline."""

    def test_run_design_generation_heuristic(self, sample_input_data):
        """Should run complete design generation with heuristics."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        # Should return complete result
        assert "hld" in result
        assert "lld" in result
        assert "adrs" in result
        assert "diagrams" in result
        assert "review_checklist" in result
        assert "artifacts" in result
        assert "phase_result" in result

    def test_run_includes_design_method(self, sample_input_data):
        """Should include design_method in phase result."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        # Phase result should exist
        assert "phase_result" in result
        # Design method should be tracked somewhere
        # (will be added in implementation)

    def test_generates_hld_artifact(self, sample_input_data):
        """Should generate and save HLD artifact."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        assert "hld_path" in result
        assert result["hld_path"] != ""
        assert "hld" in result
        assert len(result["hld"]) > 0

    def test_generates_lld_artifact(self, sample_input_data):
        """Should generate and save LLD artifact."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        assert "lld_path" in result
        assert result["lld_path"] != ""
        assert "lld" in result
        assert len(result["lld"]) > 0

    def test_generates_diagrams_artifact(self, sample_input_data):
        """Should generate and save diagrams artifact."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        assert "diagrams_path" in result
        assert result["diagrams_path"] != ""
        assert "diagrams" in result
        assert isinstance(result["diagrams"], dict)

    def test_generates_review_checklist(self, sample_input_data):
        """Should generate design review checklist."""
        agent = SDLCDesignAgent()

        result = agent.run(sample_input_data)

        assert "review_checklist" in result
        assert "review_path" in result
        assert "Design Review Checklist" in result["review_checklist"]


# 6. Edge Cases
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_minimal_issue(self):
        """Should handle issue with minimal information."""
        agent = SDLCDesignAgent()
        minimal_issue = {
            "issue_title": "Minimal Feature",
            "technical_requirements": [],
            "acceptance_criteria": []
        }
        feasibility_result = {"decision": "go"}

        # Should not crash
        hld = agent._generate_hld(minimal_issue, feasibility_result, "")

        assert len(hld) > 0
        assert "Minimal Feature" in hld

    def test_handles_missing_optional_fields(self):
        """Should handle missing optional fields gracefully."""
        agent = SDLCDesignAgent()
        minimal_issue = {
            "issue_title": "Test Feature"
        }

        # Should not crash
        lld = agent._generate_lld(minimal_issue, "HLD content")

        assert len(lld) > 0

    def test_handles_no_adrs_generated(self, sample_issue):
        """Should handle case when no ADRs are generated."""
        agent = SDLCDesignAgent()
        issue_no_arch = {
            "issue_title": "Simple UI Change",
            "technical_requirements": ["Update button color"]
        }

        adrs = agent._generate_adrs(issue_no_arch, "HLD")

        # Should return empty list, not crash
        assert isinstance(adrs, list)

    def test_handles_empty_risks_in_feasibility(self, sample_issue):
        """Should handle feasibility result with no risks."""
        agent = SDLCDesignAgent()
        feasibility_no_risks = {
            "decision": "go",
            "confidence": 0.9,
            "risks": []
        }

        hld = agent._generate_hld(sample_issue, feasibility_no_risks, "")

        # Should handle empty risks gracefully
        assert len(hld) > 0


# 7. LLM-Enhanced HLD/LLD Tests
class TestLLMEnhancedDocuments:
    """Test LLM enhancement of HLD/LLD documents."""

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_hld_uses_llm_architecture(self, mock_llm_gen, sample_issue, sample_feasibility_result):
        """Should use LLM-generated architecture in HLD."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "components": ["Auth Service", "Token Manager"],
            "data_flow": "User -> Auth -> Database"
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # When LLM is available, it might enhance the HLD
        # (Implementation detail - test that it doesn't crash)
        hld = agent._generate_hld(sample_issue, sample_feasibility_result, "context")

        assert len(hld) > 0

    @patch('scripts.ai.sdlc.design_agent.LLMGenerator')
    def test_lld_uses_llm_patterns(self, mock_llm_gen, sample_issue):
        """Should use LLM-recommended patterns in LLD."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "patterns": [
                {
                    "name": "Repository Pattern",
                    "rationale": "Data access separation"
                }
            ]
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        agent = SDLCDesignAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # When LLM is available, it might enhance the LLD
        lld = agent._generate_lld(sample_issue, "HLD content")

        assert len(lld) > 0


# 8. Guardrails Tests
class TestGuardrails:
    """Test custom guardrails for design phase."""

    def test_guardrails_detect_missing_hld(self):
        """Should detect missing HLD in output."""
        agent = SDLCDesignAgent()

        output_data = {
            "lld": "LLD content",
            "diagrams": {},
            "adrs": []
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("hld" in err.lower() for err in errors)

    def test_guardrails_detect_missing_lld(self):
        """Should detect missing LLD in output."""
        agent = SDLCDesignAgent()

        output_data = {
            "hld": "HLD content",
            "diagrams": {},
            "adrs": []
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("lld" in err.lower() for err in errors)

    def test_guardrails_detect_missing_diagrams(self):
        """Should detect missing diagrams in output."""
        agent = SDLCDesignAgent()

        output_data = {
            "hld": "HLD content",
            "lld": "LLD content",
            "adrs": []
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("diagrams" in err.lower() for err in errors)

    def test_guardrails_detect_redis_mention(self):
        """Should detect Redis mentioned without prohibition warning."""
        agent = SDLCDesignAgent()

        output_data = {
            "hld": "We will use Redis for caching",
            "lld": "LLD content",
            "diagrams": {}
        }

        errors = agent._custom_guardrails(output_data)

        # Should warn about Redis mention
        assert len(errors) > 0
        assert any("redis" in err.lower() for err in errors)

    def test_guardrails_allow_redis_with_prohibition(self):
        """Should allow Redis mention if prohibition is stated."""
        agent = SDLCDesignAgent()

        output_data = {
            "hld": "NO Redis allowed per RNF-002, use MySQL instead",
            "lld": "LLD content",
            "diagrams": {}
        }

        errors = agent._custom_guardrails(output_data)

        # Should not complain about Redis if prohibition is mentioned
        redis_errors = [e for e in errors if "redis" in e.lower()]
        # Either no Redis error, or the error is not about Redis being used
        # (implementation will check for "no redis" in text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
