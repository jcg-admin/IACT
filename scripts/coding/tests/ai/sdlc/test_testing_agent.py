#!/usr/bin/env python3
"""
TDD Tests for SDLCTestingAgent

Tests the SDLCTestingAgent implementation which generates test plans,
test cases, and testing strategies for features.

Tests cover both LLM-enhanced and heuristic fallback methods.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from scripts.ai.sdlc.testing_agent import (
    SDLCTestingAgent,
    TESTING_METHOD_LLM,
    TESTING_METHOD_HEURISTIC
)


# Fixtures
@pytest.fixture
def sample_issue():
    """Sample issue for testing."""
    return {
        "issue_title": "Implement User Profile Management",
        "issue_number": "IACT-789",
        "priority": "P1",
        "story_points": 5,
        "technical_requirements": [
            "Create user profile model",
            "Implement profile update endpoint",
            "Add profile validation",
            "Create profile view component"
        ],
        "acceptance_criteria": [
            "User can view their profile",
            "User can update profile information",
            "Profile validation works correctly",
            "Changes are persisted to database"
        ]
    }


@pytest.fixture
def sample_design_result():
    """Sample design result from SDLCDesignAgent."""
    return {
        "hld": "# High-Level Design\nProfile management system...",
        "lld": "# Low-Level Design\nDetailed implementation...",
        "diagrams": {
            "architecture": "```mermaid\ngraph TB...",
            "sequence": "```mermaid\nsequenceDiagram..."
        }
    }


@pytest.fixture
def sample_input_data(sample_issue, sample_design_result):
    """Sample input data for agent run."""
    return {
        "issue": sample_issue,
        "design_result": sample_design_result,
        "implementation_status": "pending"
    }


@pytest.fixture
def complex_issue():
    """Complex issue with many requirements."""
    return {
        "issue_title": "Implement Advanced Analytics Dashboard",
        "issue_number": "IACT-999",
        "priority": "P0",
        "story_points": 13,
        "technical_requirements": [
            "Create analytics models",
            "Implement data aggregation service",
            "Build real-time data processing",
            "Create dashboard UI components",
            "Add export functionality",
            "Implement caching layer"
        ],
        "acceptance_criteria": [
            "Dashboard displays real-time data",
            "Data can be filtered by date range",
            "Export to CSV/PDF works",
            "Performance < 2s for all queries"
        ]
    }


# 1. Initialization Tests
class TestTestingAgentInitialization:
    """Test SDLCTestingAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = SDLCTestingAgent()

        assert agent.name == "SDLCTestingAgent"
        assert agent.phase == "testing"

    def test_initialization_with_config(self):
        """Should initialize with config parameter."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929"
        }
        agent = SDLCTestingAgent(config=config)

        assert agent.name == "SDLCTestingAgent"
        assert agent.phase == "testing"

    def test_initialization_without_config(self):
        """Should initialize without config (heuristic mode)."""
        agent = SDLCTestingAgent(config=None)

        assert agent.name == "SDLCTestingAgent"
        assert agent.llm_generator is None


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation."""

    def test_validate_valid_input(self, sample_input_data):
        """Should accept valid input data."""
        agent = SDLCTestingAgent()

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_design_result(self, sample_issue):
        """Should reject input without design_result."""
        agent = SDLCTestingAgent()
        input_data = {"issue": sample_issue}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("design_result" in err.lower() for err in errors)

    def test_validate_missing_issue(self, sample_design_result):
        """Should reject input without issue."""
        agent = SDLCTestingAgent()
        input_data = {"design_result": sample_design_result}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("issue" in err.lower() for err in errors)

    def test_validate_missing_both(self):
        """Should reject input without issue and design_result."""
        agent = SDLCTestingAgent()
        input_data = {"implementation_status": "pending"}

        errors = agent.validate_input(input_data)

        assert len(errors) >= 2


# 3. Heuristic Test Plan Generation Tests
class TestTestPlanGenerationHeuristic:
    """Test heuristic test plan generation."""

    def test_generate_test_plan_structure(self, sample_issue, sample_design_result):
        """Should generate test plan with correct structure."""
        agent = SDLCTestingAgent()

        test_plan = agent._generate_test_plan(sample_issue, sample_design_result)

        assert "Test Plan" in test_plan
        assert "Objectives" in test_plan
        assert "Test Strategy" in test_plan
        assert "Test Pyramid" in test_plan
        assert sample_issue["issue_title"] in test_plan

    def test_generate_test_plan_includes_acceptance_criteria(self, sample_issue, sample_design_result):
        """Should include acceptance criteria in test plan."""
        agent = SDLCTestingAgent()

        test_plan = agent._generate_test_plan(sample_issue, sample_design_result)

        for criterion in sample_issue["acceptance_criteria"]:
            # Acceptance criteria should be referenced in some form
            assert len(test_plan) > 0

    def test_generate_test_plan_includes_coverage_target(self, sample_issue, sample_design_result):
        """Should include coverage target in test plan."""
        agent = SDLCTestingAgent()

        test_plan = agent._generate_test_plan(sample_issue, sample_design_result)

        assert "80%" in test_plan or "coverage" in test_plan.lower()


# 4. Heuristic Test Cases Generation Tests
class TestTestCasesGenerationHeuristic:
    """Test heuristic test cases generation."""

    def test_generate_test_cases_returns_list(self, sample_issue, sample_design_result):
        """Should return list of test cases."""
        agent = SDLCTestingAgent()

        test_cases = agent._generate_test_cases(sample_issue, sample_design_result)

        assert isinstance(test_cases, list)
        assert len(test_cases) > 0

    def test_generate_unit_test_cases(self):
        """Should generate unit test cases."""
        agent = SDLCTestingAgent()
        acceptance_criteria = ["User can create profile", "User can update profile"]

        unit_tests = agent._generate_unit_test_cases(acceptance_criteria)

        assert isinstance(unit_tests, list)
        assert len(unit_tests) > 0
        assert all(tc["type"] == "unit" for tc in unit_tests)

    def test_generate_integration_test_cases(self):
        """Should generate integration test cases."""
        agent = SDLCTestingAgent()
        acceptance_criteria = ["API endpoint works", "Database is updated"]

        integration_tests = agent._generate_integration_test_cases(acceptance_criteria)

        assert isinstance(integration_tests, list)
        assert len(integration_tests) > 0
        assert all(tc["type"] == "integration" for tc in integration_tests)

    def test_generate_e2e_test_cases(self):
        """Should generate E2E test cases."""
        agent = SDLCTestingAgent()
        acceptance_criteria = ["User flow works end-to-end"]

        e2e_tests = agent._generate_e2e_test_cases(acceptance_criteria)

        assert isinstance(e2e_tests, list)
        assert len(e2e_tests) > 0
        assert all(tc["type"] == "e2e" for tc in e2e_tests)

    def test_test_cases_have_required_fields(self, sample_issue, sample_design_result):
        """Should generate test cases with all required fields."""
        agent = SDLCTestingAgent()

        test_cases = agent._generate_test_cases(sample_issue, sample_design_result)

        for tc in test_cases:
            assert "id" in tc
            assert "type" in tc
            assert "name" in tc
            assert "description" in tc
            assert "priority" in tc


# 5. Test Pyramid Strategy Tests
class TestTestPyramidStrategy:
    """Test test pyramid strategy generation."""

    def test_generate_test_pyramid_calculates_percentages(self):
        """Should calculate test pyramid percentages correctly."""
        agent = SDLCTestingAgent()
        test_cases = [
            {"type": "unit", "id": "UT-001"},
            {"type": "unit", "id": "UT-002"},
            {"type": "unit", "id": "UT-003"},
            {"type": "unit", "id": "UT-004"},
            {"type": "unit", "id": "UT-005"},
            {"type": "unit", "id": "UT-006"},
            {"type": "integration", "id": "IT-001"},
            {"type": "integration", "id": "IT-002"},
            {"type": "integration", "id": "IT-003"},
            {"type": "e2e", "id": "E2E-001"}
        ]

        pyramid = agent._generate_test_pyramid_strategy(test_cases)

        assert pyramid["total_tests"] == 10
        assert pyramid["unit_tests"]["count"] == 6
        assert pyramid["integration_tests"]["count"] == 3
        assert pyramid["e2e_tests"]["count"] == 1
        assert pyramid["unit_tests"]["percentage"] == 60.0

    def test_test_pyramid_status_on_target(self):
        """Should identify when test pyramid is on target."""
        agent = SDLCTestingAgent()
        # 60% unit, 30% integration, 10% e2e
        test_cases = (
            [{"type": "unit", "id": f"UT-{i}"} for i in range(6)] +
            [{"type": "integration", "id": f"IT-{i}"} for i in range(3)] +
            [{"type": "e2e", "id": "E2E-001"}]
        )

        pyramid = agent._generate_test_pyramid_strategy(test_cases)

        assert pyramid["unit_tests"]["status"] == "on_target"

    def test_test_pyramid_needs_more_unit_tests(self):
        """Should identify when more unit tests are needed."""
        agent = SDLCTestingAgent()
        # Only 20% unit tests
        test_cases = (
            [{"type": "unit", "id": "UT-001"}] +
            [{"type": "integration", "id": f"IT-{i}"} for i in range(3)] +
            [{"type": "e2e", "id": "E2E-001"}]
        )

        pyramid = agent._generate_test_pyramid_strategy(test_cases)

        assert pyramid["unit_tests"]["status"] == "needs_more"


# 6. Coverage Requirements Tests
class TestCoverageRequirements:
    """Test coverage requirements generation."""

    def test_coverage_requirements_for_simple_feature(self, sample_issue):
        """Should set 80% coverage for simple features."""
        agent = SDLCTestingAgent()

        coverage = agent._generate_coverage_requirements(sample_issue)

        assert coverage["overall_target"] == 80

    def test_coverage_requirements_for_complex_feature(self, complex_issue):
        """Should set higher coverage for complex features."""
        agent = SDLCTestingAgent()

        coverage = agent._generate_coverage_requirements(complex_issue)

        assert coverage["overall_target"] >= 80
        assert coverage["critical_paths"] == 100

    def test_coverage_requirements_structure(self, sample_issue):
        """Should include all coverage categories."""
        agent = SDLCTestingAgent()

        coverage = agent._generate_coverage_requirements(sample_issue)

        assert "overall_target" in coverage
        assert "critical_paths" in coverage
        assert "models" in coverage
        assert "services" in coverage
        assert "views" in coverage


# 7. LLM Integration Tests
class TestLLMIntegration:
    """Test LLM integration for enhanced test strategy."""

    @patch('scripts.ai.sdlc.testing_agent.LLMGenerator')
    def test_generate_test_strategy_with_llm(self, mock_llm_gen, sample_issue, sample_design_result):
        """Should use LLM for test strategy generation."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "test_strategy": {
                "focus_areas": ["API endpoints", "Data validation", "User flows"],
                "critical_paths": ["User login -> Profile update"],
                "risk_areas": ["Database transactions", "Concurrent updates"],
                "recommended_test_count": {
                    "unit": 15,
                    "integration": 8,
                    "e2e": 3
                }
            }
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCTestingAgent(config={"llm_provider": "anthropic"})
        agent.llm_generator = mock_llm_instance

        strategy = agent._generate_test_strategy_with_llm(sample_issue, sample_design_result)

        assert "focus_areas" in strategy
        assert "critical_paths" in strategy
        assert "risk_areas" in strategy
        mock_llm_instance._call_llm.assert_called_once()

    @patch('scripts.ai.sdlc.testing_agent.LLMGenerator')
    def test_generate_test_cases_with_llm(self, mock_llm_gen, sample_issue, sample_design_result):
        """Should use LLM for enhanced test case generation."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "test_cases": [
                {
                    "id": "UT-001",
                    "type": "unit",
                    "name": "Test profile model validation",
                    "description": "Verify profile model validates required fields",
                    "priority": "high",
                    "steps": ["Create profile with missing fields", "Verify ValidationError"],
                    "expected_result": "ValidationError raised"
                }
            ]
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCTestingAgent(config={"llm_provider": "anthropic"})
        agent.llm_generator = mock_llm_instance

        test_cases = agent._generate_test_cases_with_llm(sample_issue, sample_design_result)

        assert len(test_cases) > 0
        assert test_cases[0]["type"] == "unit"
        assert test_cases[0]["name"]
        mock_llm_instance._call_llm.assert_called_once()

    @patch('scripts.ai.sdlc.testing_agent.LLMGenerator')
    def test_identify_critical_paths_with_llm(self, mock_llm_gen, sample_issue, sample_design_result):
        """Should use LLM to identify critical test paths."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "critical_paths": [
                {
                    "path": "User authentication -> Profile access -> Update -> Save",
                    "priority": "critical",
                    "rationale": "Core user functionality"
                }
            ]
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCTestingAgent(config={"llm_provider": "anthropic"})
        agent.llm_generator = mock_llm_instance

        paths = agent._identify_critical_paths_with_llm(sample_issue, sample_design_result)

        assert len(paths) > 0
        assert "path" in paths[0]
        mock_llm_instance._call_llm.assert_called_once()

    def test_llm_fallback_on_error_test_strategy(self, sample_issue, sample_design_result):
        """Should fallback to heuristics if LLM fails for test strategy."""
        config = {"llm_provider": "anthropic"}
        agent = SDLCTestingAgent(config=config)

        # Mock LLM to raise exception
        if agent.llm_generator:
            agent.llm_generator._call_llm = MagicMock(side_effect=Exception("LLM error"))

        # Should not crash, should fallback
        strategy = agent._generate_test_strategy_with_llm(sample_issue, sample_design_result)

        # Should return some default structure
        assert isinstance(strategy, dict)

    def test_llm_fallback_on_error_test_cases(self, sample_issue, sample_design_result):
        """Should fallback to heuristics if LLM fails for test cases."""
        config = {"llm_provider": "anthropic"}
        agent = SDLCTestingAgent(config=config)

        # Mock LLM to raise exception
        if agent.llm_generator:
            agent.llm_generator._call_llm = MagicMock(side_effect=Exception("LLM error"))

        # Should not crash, should use heuristics
        test_cases = agent._generate_test_cases(sample_issue, sample_design_result)

        assert isinstance(test_cases, list)
        assert len(test_cases) > 0

    def test_parse_llm_test_strategy_from_json(self, sample_issue, sample_design_result):
        """Should parse LLM JSON response for test strategy."""
        agent = SDLCTestingAgent()

        llm_response = json.dumps({
            "test_strategy": {
                "focus_areas": ["Authentication", "Authorization"],
                "critical_paths": ["Login flow"],
                "risk_areas": ["Session management"],
                "recommended_test_count": {"unit": 10, "integration": 5, "e2e": 2}
            }
        })

        strategy = agent._parse_llm_test_strategy(llm_response)

        assert "focus_areas" in strategy
        assert len(strategy["focus_areas"]) == 2
        assert "critical_paths" in strategy

    def test_parse_llm_test_cases_from_json(self):
        """Should parse LLM JSON response for test cases."""
        agent = SDLCTestingAgent()

        llm_response = json.dumps({
            "test_cases": [
                {
                    "id": "UT-001",
                    "type": "unit",
                    "name": "Test model validation",
                    "description": "Verify validation works",
                    "priority": "high",
                    "steps": ["Step 1", "Step 2"],
                    "expected_result": "Validation passes"
                }
            ]
        })

        test_cases = agent._parse_llm_test_cases(llm_response)

        assert len(test_cases) == 1
        assert test_cases[0]["id"] == "UT-001"
        assert test_cases[0]["type"] == "unit"


# 8. Full Pipeline Tests
class TestFullPipeline:
    """Test complete testing phase pipeline."""

    def test_run_generates_all_artifacts(self, sample_input_data):
        """Should generate all required artifacts."""
        agent = SDLCTestingAgent()

        result = agent.run(sample_input_data)

        assert "test_plan" in result
        assert "test_cases" in result
        assert "test_pyramid" in result
        assert "coverage_requirements" in result
        assert "testing_checklist" in result
        assert "artifacts" in result

    def test_run_saves_artifacts(self, sample_input_data):
        """Should save artifacts to files."""
        agent = SDLCTestingAgent()

        result = agent.run(sample_input_data)

        assert "test_plan_path" in result
        assert "test_cases_path" in result
        assert "test_pyramid_path" in result
        assert "checklist_path" in result
        assert len(result["artifacts"]) >= 4

    def test_run_creates_phase_result(self, sample_input_data):
        """Should create phase result with decision."""
        agent = SDLCTestingAgent()

        result = agent.run(sample_input_data)

        assert "phase_result" in result
        phase_result = result["phase_result"]
        # phase_result is a SDLCPhaseResult object, not a dict
        assert hasattr(phase_result, "decision")
        assert phase_result.decision == "go"
        assert phase_result.confidence > 0

    def test_run_with_llm_tracks_method(self, sample_input_data):
        """Should track testing method when using LLM."""
        config = {"llm_provider": "anthropic"}
        agent = SDLCTestingAgent(config=config)

        result = agent.run(sample_input_data)

        assert "testing_method" in result
        assert result["testing_method"] in [TESTING_METHOD_LLM, TESTING_METHOD_HEURISTIC]

    def test_run_without_llm_uses_heuristic(self, sample_input_data):
        """Should use heuristic method when LLM not available."""
        agent = SDLCTestingAgent(config=None)

        result = agent.run(sample_input_data)

        assert "testing_method" in result
        assert result["testing_method"] == TESTING_METHOD_HEURISTIC


# 9. Edge Cases Tests
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_acceptance_criteria(self, sample_design_result):
        """Should handle empty acceptance criteria."""
        agent = SDLCTestingAgent()
        issue = {
            "issue_title": "Test Feature",
            "story_points": 3,
            "acceptance_criteria": []
        }

        test_plan = agent._generate_test_plan(issue, sample_design_result)

        assert test_plan
        assert len(test_plan) > 0

    def test_zero_story_points(self, sample_design_result):
        """Should handle zero story points."""
        agent = SDLCTestingAgent()
        issue = {
            "issue_title": "Test Feature",
            "story_points": 0,
            "acceptance_criteria": ["Test works"]
        }

        coverage = agent._generate_coverage_requirements(issue)

        assert coverage["overall_target"] >= 80

    def test_missing_optional_fields(self):
        """Should handle missing optional fields in input."""
        agent = SDLCTestingAgent()
        input_data = {
            "issue": {
                "issue_title": "Test",
                "acceptance_criteria": ["Criteria"]
            },
            "design_result": {"hld": "test"}
            # implementation_status is optional
        }

        result = agent.run(input_data)

        assert "test_plan" in result

    def test_very_large_feature(self, sample_design_result):
        """Should handle very large features with many test cases."""
        agent = SDLCTestingAgent()
        issue = {
            "issue_title": "Huge Feature",
            "story_points": 21,
            "acceptance_criteria": [f"Criterion {i}" for i in range(20)]
        }

        test_cases = agent._generate_test_cases(issue, sample_design_result)

        assert len(test_cases) > 0
        # Should still generate reasonable number of test cases

    def test_invalid_llm_response(self):
        """Should handle invalid LLM response gracefully."""
        agent = SDLCTestingAgent()

        # Test with invalid JSON
        invalid_response = "This is not JSON at all!"

        strategy = agent._parse_llm_test_strategy(invalid_response)

        # Should return default structure
        assert isinstance(strategy, dict)


# 10. Guardrails Tests
class TestGuardrails:
    """Test custom guardrails for testing phase."""

    def test_guardrails_pass_for_valid_output(self):
        """Should pass guardrails for valid output with proper test pyramid."""
        agent = SDLCTestingAgent()

        # Create valid output data with proper test pyramid ratio
        output_data = {
            "test_plan": "Test plan content",
            "test_cases": [
                {"type": "unit", "id": "UT-001"},
                {"type": "unit", "id": "UT-002"},
                {"type": "unit", "id": "UT-003"},
                {"type": "unit", "id": "UT-004"},
                {"type": "unit", "id": "UT-005"},
                {"type": "unit", "id": "UT-006"},
                {"type": "integration", "id": "IT-001"},
                {"type": "integration", "id": "IT-002"},
                {"type": "integration", "id": "IT-003"},
                {"type": "e2e", "id": "E2E-001"}
            ],
            "test_pyramid": {
                "unit_tests": {"percentage": 60.0},
                "integration_tests": {"percentage": 30.0},
                "e2e_tests": {"percentage": 10.0}
            },
            "coverage_requirements": {"overall_target": 80}
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) == 0

    def test_guardrails_fail_for_missing_test_plan(self):
        """Should fail guardrails if test plan is missing."""
        agent = SDLCTestingAgent()
        output_data = {
            "test_cases": [],
            "test_pyramid": {},
            "coverage_requirements": {}
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("test plan" in err.lower() for err in errors)

    def test_guardrails_fail_for_missing_test_cases(self):
        """Should fail guardrails if test cases are missing."""
        agent = SDLCTestingAgent()
        output_data = {
            "test_plan": "test plan",
            "test_pyramid": {},
            "coverage_requirements": {}
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("test case" in err.lower() for err in errors)

    def test_guardrails_fail_for_insufficient_unit_tests(self):
        """Should fail guardrails if unit test percentage is too low."""
        agent = SDLCTestingAgent()
        output_data = {
            "test_plan": "test plan",
            "test_cases": [{"type": "unit"}],
            "test_pyramid": {
                "unit_tests": {"percentage": 30.0}  # < 50%
            },
            "coverage_requirements": {"overall_target": 80}
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("unit test" in err.lower() for err in errors)

    def test_guardrails_fail_for_low_coverage_target(self):
        """Should fail guardrails if coverage target is too low."""
        agent = SDLCTestingAgent()
        output_data = {
            "test_plan": "test plan",
            "test_cases": [{"type": "unit"}],
            "test_pyramid": {
                "unit_tests": {"percentage": 60.0}
            },
            "coverage_requirements": {"overall_target": 70}  # < 80%
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("coverage" in err.lower() for err in errors)
