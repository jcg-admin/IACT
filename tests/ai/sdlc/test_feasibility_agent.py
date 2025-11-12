#!/usr/bin/env python3
"""
TDD Tests for SDLCFeasibilityAgent

Tests the SDLCFeasibilityAgent implementation which analyzes feasibility
of features including technical viability, risk assessment, and effort estimation.

Tests cover both LLM-enhanced and heuristic fallback methods.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from scripts.ai.sdlc.feasibility_agent import (
    SDLCFeasibilityAgent,
    ANALYSIS_METHOD_LLM,
    ANALYSIS_METHOD_HEURISTIC
)


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
def sample_input_data(sample_issue):
    """Sample input data for agent run."""
    return {
        "issue": sample_issue,
        "project_context": "IACT project using Django 4.2+ and PostgreSQL",
        "technical_constraints": {
            "no_redis": True,
            "no_email": True
        }
    }


@pytest.fixture
def complex_issue():
    """Complex issue requiring Redis (blocker)."""
    return {
        "issue_title": "Implement Real-time Chat with Redis Pub/Sub",
        "issue_number": "IACT-456",
        "priority": "P0",
        "story_points": 13,
        "technical_requirements": [
            "Setup Redis for message brokering",
            "Implement pub/sub channels",
            "Create WebSocket handlers"
        ],
        "acceptance_criteria": [
            "Real-time message delivery"
        ]
    }


# 1. Initialization Tests
class TestFeasibilityAgentInitialization:
    """Test SDLCFeasibilityAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = SDLCFeasibilityAgent()

        assert agent.name == "SDLCFeasibilityAgent"
        assert agent.phase == "feasibility"
        assert agent.use_llm is True or agent.use_llm is False  # Depends on LLM_AVAILABLE

    def test_initialization_with_llm_disabled(self):
        """Should initialize with LLM disabled."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        assert agent.use_llm is False
        assert agent.llm is None

    def test_initialization_with_custom_model(self):
        """Should initialize with custom LLM model."""
        agent = SDLCFeasibilityAgent(
            use_llm=True,
            llm_provider="anthropic",
            model="claude-3-5-sonnet-20241022"
        )

        # Should not crash, LLM might be available or not
        assert agent.name == "SDLCFeasibilityAgent"


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation."""

    def test_validate_valid_input(self, sample_input_data):
        """Should accept valid input data."""
        agent = SDLCFeasibilityAgent()

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_issue(self):
        """Should reject input without issue."""
        agent = SDLCFeasibilityAgent()
        input_data = {"project_context": "test"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("issue" in err.lower() for err in errors)

    def test_validate_invalid_issue_format(self):
        """Should reject invalid issue format."""
        agent = SDLCFeasibilityAgent()
        input_data = {"issue": "not a dict"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0


# 3. Technical Feasibility Tests (Heuristic)
class TestTechnicalFeasibilityHeuristic:
    """Test heuristic technical feasibility analysis."""

    def test_analyze_feasible_feature(self, sample_issue):
        """Should analyze feasible feature correctly."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        feasibility = agent._analyze_technical_feasibility_heuristic(
            sample_issue,
            {"no_redis": True, "no_email": True}
        )

        assert feasibility["is_feasible"] is True
        assert feasibility["score"] > 0.5
        assert len(feasibility["blockers"]) == 0

    def test_detect_redis_blocker(self, complex_issue):
        """Should detect Redis blocker in requirements."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        feasibility = agent._analyze_technical_feasibility_heuristic(
            complex_issue,
            {"no_redis": True, "no_email": True}
        )

        assert feasibility["is_feasible"] is False
        assert len(feasibility["blockers"]) > 0
        assert any("redis" in blocker.lower() for blocker in feasibility["blockers"])

    def test_detect_architectural_concerns(self):
        """Should detect architectural complexity concerns."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        issue = {
            "issue_title": "Refactor entire arquitectura to microservices",
            "technical_requirements": []
        }

        feasibility = agent._analyze_technical_feasibility_heuristic(
            issue,
            {"no_redis": True}
        )

        assert len(feasibility["concerns"]) > 0


# 4. Risk Assessment Tests (Heuristic)
class TestRiskAssessmentHeuristic:
    """Test heuristic risk assessment."""

    def test_identify_complexity_risk(self, complex_issue):
        """Should identify high complexity risk."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        feasibility = {"is_feasible": True, "score": 0.8, "blockers": [], "concerns": []}

        risks = agent._assess_risks_heuristic(complex_issue, feasibility)

        # Should have risk for high story points (13)
        complexity_risks = [r for r in risks if "complejidad" in r["description"].lower()]
        assert len(complexity_risks) > 0
        assert complexity_risks[0]["severity"] == "high"

    def test_identify_blocker_risk(self, complex_issue):
        """Should identify critical risk from blockers."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        feasibility = {
            "is_feasible": False,
            "score": 0.2,
            "blockers": ["Redis is not allowed"],
            "concerns": []
        }

        risks = agent._assess_risks_heuristic(complex_issue, feasibility)

        # Should have critical risk
        critical_risks = [r for r in risks if r["severity"] == "critical"]
        assert len(critical_risks) > 0

    def test_identify_insufficient_criteria_risk(self):
        """Should identify risk from insufficient acceptance criteria."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        issue = {
            "issue_title": "Test Feature",
            "story_points": 5,
            "priority": "P2",
            "acceptance_criteria": ["One criteria only"]  # < 3
        }
        feasibility = {"is_feasible": True, "score": 0.8, "blockers": [], "concerns": []}

        risks = agent._assess_risks_heuristic(issue, feasibility)

        criteria_risks = [r for r in risks if "criteria" in r["description"].lower()]
        assert len(criteria_risks) > 0


# 5. Effort Analysis Tests (Heuristic)
class TestEffortAnalysisHeuristic:
    """Test heuristic effort analysis."""

    def test_basic_effort_estimation(self, sample_issue):
        """Should estimate effort based on story points."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        effort = agent._analyze_effort_heuristic(sample_issue)

        assert effort["story_points"] == 8
        assert effort["estimated_hours"] > 0
        assert effort["estimated_days"] > 0
        # 8 SP * 4 hours = 32 hours base
        assert effort["estimated_hours"] >= 32

    def test_complexity_multiplier_for_many_requirements(self):
        """Should apply complexity multiplier for many requirements."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        issue = {
            "issue_title": "Complex Feature",
            "story_points": 5,
            "technical_requirements": ["req" + str(i) for i in range(10)]  # > 5
        }

        effort = agent._analyze_effort_heuristic(issue)

        assert effort["complexity_multiplier"] > 1.0
        # Should be adjusted higher than base estimate
        assert effort["estimated_hours"] > 5 * 4

    def test_team_size_recommendation(self):
        """Should recommend team size based on story points."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        # Small feature
        small_issue = {"issue_title": "Small", "story_points": 3, "technical_requirements": []}
        effort_small = agent._analyze_effort_heuristic(small_issue)
        assert effort_small["team_size_recommended"] == 1

        # Large feature
        large_issue = {"issue_title": "Large", "story_points": 8, "technical_requirements": []}
        effort_large = agent._analyze_effort_heuristic(large_issue)
        assert effort_large["team_size_recommended"] == 2


# 6. Decision Making Tests
class TestDecisionMaking:
    """Test Go/No-Go decision making."""

    def test_go_decision_for_feasible_feature(self):
        """Should make GO decision for feasible feature."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        technical_feasibility = {"is_feasible": True, "score": 0.9, "blockers": [], "concerns": []}
        risks = []
        effort_analysis = {"estimated_days": 5}

        decision = agent._make_decision(technical_feasibility, risks, effort_analysis)

        assert decision["decision"] == "go"
        assert decision["confidence"] > 0.5

    def test_no_go_decision_for_critical_risks(self):
        """Should make NO-GO decision for critical risks."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        technical_feasibility = {"is_feasible": False, "score": 0.2, "blockers": ["BLOCKER"], "concerns": []}
        risks = [{"severity": "critical", "description": "Blocker"}]
        effort_analysis = {"estimated_days": 10}

        decision = agent._make_decision(technical_feasibility, risks, effort_analysis)

        assert decision["decision"] == "no-go"
        assert decision["confidence"] < 0.5

    def test_review_decision_for_high_risks(self):
        """Should make REVIEW decision for high risks."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        technical_feasibility = {"is_feasible": True, "score": 0.7, "blockers": [], "concerns": []}
        risks = [
            {"severity": "high", "description": "Risk 1"},
            {"severity": "high", "description": "Risk 2"},
            {"severity": "high", "description": "Risk 3"}
        ]
        effort_analysis = {"estimated_days": 10}

        decision = agent._make_decision(technical_feasibility, risks, effort_analysis)

        assert decision["decision"] == "review"


# 7. LLM Integration Tests
class TestLLMIntegration:
    """Test LLM-enhanced analysis methods."""

    @patch('scripts.ai.sdlc.feasibility_agent.LLMGenerator')
    def test_technical_feasibility_with_llm(self, mock_llm_gen, sample_issue):
        """Should use LLM for technical feasibility analysis."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "is_feasible": True,
            "score": 0.85,
            "blockers": [],
            "concerns": ["Consider security best practices"],
            "reasoning": "Feature is technically viable"
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCFeasibilityAgent(use_llm=True)
        agent.llm = mock_llm_instance

        feasibility = agent._analyze_technical_feasibility_with_llm(
            sample_issue,
            {"no_redis": True},
            "IACT project"
        )

        assert feasibility["is_feasible"] is True
        assert feasibility["score"] == 0.85
        assert len(feasibility["concerns"]) > 0
        mock_llm_instance._call_llm.assert_called_once()

    @patch('scripts.ai.sdlc.feasibility_agent.LLMGenerator')
    def test_risk_assessment_with_llm(self, mock_llm_gen, sample_issue):
        """Should use LLM for risk assessment."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "risks": [
                {
                    "type": "technical",
                    "severity": "medium",
                    "probability": "high",
                    "description": "JWT implementation complexity",
                    "mitigation": "Use proven library like PyJWT",
                    "impact": "Security vulnerabilities if not done correctly"
                }
            ]
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCFeasibilityAgent(use_llm=True)
        agent.llm = mock_llm_instance

        feasibility = {"is_feasible": True, "score": 0.8, "blockers": [], "concerns": []}
        risks = agent._assess_risks_with_llm(sample_issue, feasibility, "IACT project")

        assert len(risks) > 0
        assert risks[0]["type"] == "technical"
        assert risks[0]["severity"] == "medium"
        mock_llm_instance._call_llm.assert_called_once()

    @patch('scripts.ai.sdlc.feasibility_agent.LLMGenerator')
    def test_effort_analysis_with_llm(self, mock_llm_gen, sample_issue):
        """Should use LLM for effort analysis."""
        # Mock LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "story_points": 8,
            "estimated_hours": 40,
            "estimated_days": 5,
            "complexity_multiplier": 1.25,
            "team_size_recommended": 2,
            "reasoning": "Moderate complexity with security considerations"
        })
        mock_llm_gen.return_value = mock_llm_instance

        agent = SDLCFeasibilityAgent(use_llm=True)
        agent.llm = mock_llm_instance

        effort = agent._analyze_effort_with_llm(sample_issue, "IACT project")

        assert effort["story_points"] == 8
        assert effort["estimated_hours"] == 40
        assert effort["estimated_days"] == 5
        assert effort["complexity_multiplier"] == 1.25
        mock_llm_instance._call_llm.assert_called_once()

    def test_llm_fallback_on_error(self, sample_issue):
        """Should fallback to heuristics if LLM fails."""
        agent = SDLCFeasibilityAgent(use_llm=True)

        # Mock LLM to raise exception
        if agent.llm:
            agent.llm._call_llm = MagicMock(side_effect=Exception("LLM error"))

        # Should not crash, should fallback
        feasibility = agent._analyze_technical_feasibility(
            sample_issue,
            {"no_redis": True},
            "test context"
        )

        assert "is_feasible" in feasibility
        assert "score" in feasibility

    def test_parse_llm_technical_feasibility_from_json(self, sample_issue):
        """Should parse LLM JSON response for technical feasibility."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        llm_response = json.dumps({
            "is_feasible": True,
            "score": 0.9,
            "blockers": [],
            "concerns": ["Security review needed"],
            "reasoning": "Looks good"
        })

        feasibility = agent._parse_llm_technical_feasibility(
            llm_response,
            sample_issue,
            {"no_redis": True}
        )

        assert feasibility["is_feasible"] is True
        assert feasibility["score"] == 0.9
        assert len(feasibility["concerns"]) == 1

    def test_parse_llm_risks_from_json(self, sample_issue):
        """Should parse LLM JSON response for risks."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        llm_response = json.dumps({
            "risks": [
                {
                    "type": "technical",
                    "severity": "high",
                    "probability": "medium",
                    "description": "Complex integration",
                    "mitigation": "Phased approach",
                    "impact": "Delays possible"
                }
            ]
        })

        feasibility = {"is_feasible": True, "score": 0.8, "blockers": [], "concerns": []}
        risks = agent._parse_llm_risks(llm_response, sample_issue, feasibility)

        assert len(risks) == 1
        assert risks[0]["severity"] == "high"
        assert risks[0]["type"] == "technical"

    def test_parse_llm_effort_from_json(self, sample_issue):
        """Should parse LLM JSON response for effort."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        llm_response = json.dumps({
            "story_points": 8,
            "estimated_hours": 35,
            "estimated_days": 4.5,
            "complexity_multiplier": 1.1,
            "team_size_recommended": 2,
            "reasoning": "Standard complexity"
        })

        effort = agent._parse_llm_effort(llm_response, sample_issue)

        assert effort["story_points"] == 8
        assert effort["estimated_hours"] == 35
        assert effort["complexity_multiplier"] == 1.1


# 8. Full Pipeline Tests
class TestFullPipeline:
    """Test complete feasibility analysis pipeline."""

    def test_run_feasibility_analysis_heuristic(self, sample_input_data):
        """Should run complete feasibility analysis with heuristics."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        result = agent.run(sample_input_data)

        # Should return complete result
        assert "feasibility_report" in result
        assert "technical_feasibility" in result
        assert "risks" in result
        assert "effort_analysis" in result
        assert "decision" in result
        assert "confidence" in result
        assert "analysis_method" in result
        assert result["analysis_method"] == ANALYSIS_METHOD_HEURISTIC

    def test_run_includes_analysis_method(self, sample_input_data):
        """Should include analysis_method in result."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        result = agent.run(sample_input_data)

        assert "analysis_method" in result
        assert result["analysis_method"] in [ANALYSIS_METHOD_LLM, ANALYSIS_METHOD_HEURISTIC]

    def test_generates_report_artifact(self, sample_input_data):
        """Should generate and save feasibility report."""
        agent = SDLCFeasibilityAgent(use_llm=False)

        result = agent.run(sample_input_data)

        assert "report_path" in result
        assert result["report_path"] != ""
        assert "feasibility_report" in result
        assert len(result["feasibility_report"]) > 0


# 9. Edge Cases
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_zero_story_points(self):
        """Should handle issue with zero story points."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        issue = {
            "issue_title": "Test",
            "story_points": 0,
            "technical_requirements": [],
            "acceptance_criteria": ["Test"]
        }

        effort = agent._analyze_effort_heuristic(issue)

        assert effort["estimated_hours"] >= 0
        assert effort["estimated_days"] >= 0

    def test_handles_missing_optional_fields(self):
        """Should handle issue with missing optional fields."""
        agent = SDLCFeasibilityAgent(use_llm=False)
        minimal_issue = {
            "issue_title": "Minimal Feature"
        }

        # Should not crash
        feasibility = agent._analyze_technical_feasibility_heuristic(
            minimal_issue,
            {}
        )

        assert "is_feasible" in feasibility
        assert "score" in feasibility


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
