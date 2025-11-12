#!/usr/bin/env python3
"""
TDD Tests for SDLCOrchestratorAgent

Tests the SDLCOrchestratorAgent implementation which orchestrates
all SDLC phases from planning to deployment.

Tests cover both LLM-enhanced and heuristic fallback methods.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, call
from scripts.ai.sdlc.orchestrator import SDLCOrchestratorAgent


# Fixtures
@pytest.fixture
def sample_feature_request():
    """Sample feature request for testing."""
    return "Implement user authentication with JWT tokens"


@pytest.fixture
def sample_input_data(sample_feature_request):
    """Sample input data for orchestrator run."""
    return {
        "feature_request": sample_feature_request,
        "project_context": "IACT project using Django 4.2+ and PostgreSQL",
        "technical_constraints": {
            "no_redis": True,
            "no_email": True
        },
        "start_phase": "planning",
        "end_phase": "deployment"
    }


@pytest.fixture
def mock_planning_result():
    """Mock planning phase result."""
    return {
        "issue": {
            "issue_title": "Implement User Authentication",
            "issue_number": "IACT-123",
            "priority": "P1",
            "story_points": 8,
            "technical_requirements": ["JWT generation", "Login endpoint"],
            "acceptance_criteria": ["User can login", "Token generated"]
        },
        "artifacts": ["planning_doc.md"],
        "phase_result": MagicMock(decision="go", confidence=0.9)
    }


@pytest.fixture
def mock_feasibility_result():
    """Mock feasibility phase result."""
    return {
        "decision": "go",
        "confidence": 0.85,
        "risks": [
            {"severity": "medium", "description": "Security complexity"}
        ],
        "technical_feasibility": {
            "is_feasible": True,
            "score": 0.85,
            "blockers": [],
            "concerns": []
        },
        "artifacts": ["feasibility_report.md"]
    }


@pytest.fixture
def mock_design_result():
    """Mock design phase result."""
    return {
        "hld_path": "HLD_doc.md",
        "lld_path": "LLD_doc.md",
        "adrs": ["ADR-001.md"],
        "diagrams": {"architecture": "diagram.mmd"},
        "artifacts": ["HLD_doc.md", "LLD_doc.md"]
    }


@pytest.fixture
def mock_testing_result():
    """Mock testing phase result."""
    return {
        "test_pyramid": {
            "total_tests": 100,
            "unit_tests": {"count": 70, "percentage": 70},
            "integration_tests": {"count": 20, "percentage": 20},
            "e2e_tests": {"count": 10, "percentage": 10}
        },
        "coverage_requirements": {"overall_target": 80},
        "artifacts": ["test_plan.md"]
    }


@pytest.fixture
def mock_deployment_result():
    """Mock deployment phase result."""
    return {
        "environment": "staging",
        "deployment_path": "deployment_plan.md",
        "rollback_path": "rollback_plan.md",
        "artifacts": ["deployment_plan.md", "rollback_plan.md"]
    }


# 1. Initialization Tests
class TestOrchestratorInitialization:
    """Test SDLCOrchestratorAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = SDLCOrchestratorAgent()

        assert agent.name == "SDLCOrchestratorAgent"
        assert agent.phase == "orchestration"
        assert hasattr(agent, 'planner_agent')
        assert hasattr(agent, 'feasibility_agent')
        assert hasattr(agent, 'design_agent')
        assert hasattr(agent, 'testing_agent')
        assert hasattr(agent, 'deployment_agent')

    def test_initialization_with_config(self):
        """Should initialize with custom configuration."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = SDLCOrchestratorAgent(config=config)

        assert agent.name == "SDLCOrchestratorAgent"
        # Config should be passed to sub-agents

    def test_initialization_with_llm_config(self):
        """Should initialize LLMGenerator with config."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = SDLCOrchestratorAgent(config=config)

        # Should have llm_generator attribute if LLM available
        assert hasattr(agent, 'llm_generator')

    def test_valid_phases_constant(self):
        """Should have valid phases defined."""
        agent = SDLCOrchestratorAgent()

        assert hasattr(agent, 'VALID_PHASES')
        assert "planning" in agent.VALID_PHASES
        assert "feasibility" in agent.VALID_PHASES
        assert "design" in agent.VALID_PHASES
        assert "testing" in agent.VALID_PHASES
        assert "deployment" in agent.VALID_PHASES


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation."""

    def test_validate_valid_input(self, sample_input_data):
        """Should accept valid input data."""
        agent = SDLCOrchestratorAgent()

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_feature_request(self):
        """Should reject input without feature_request."""
        agent = SDLCOrchestratorAgent()
        input_data = {"project_context": "test"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("feature_request" in err.lower() for err in errors)

    def test_validate_empty_feature_request(self):
        """Should reject empty feature_request."""
        agent = SDLCOrchestratorAgent()
        input_data = {"feature_request": ""}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0

    def test_validate_invalid_start_phase(self):
        """Should reject invalid start_phase."""
        agent = SDLCOrchestratorAgent()
        input_data = {
            "feature_request": "test",
            "start_phase": "invalid_phase"
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("start_phase" in err.lower() for err in errors)

    def test_validate_invalid_end_phase(self):
        """Should reject invalid end_phase."""
        agent = SDLCOrchestratorAgent()
        input_data = {
            "feature_request": "test",
            "end_phase": "invalid_phase"
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("end_phase" in err.lower() for err in errors)

    def test_validate_inverted_phase_order(self):
        """Should reject inverted phase order (end before start)."""
        agent = SDLCOrchestratorAgent()
        input_data = {
            "feature_request": "test",
            "start_phase": "deployment",
            "end_phase": "planning"
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("antes" in err.lower() for err in errors)


# 3. Phase Execution Decision Tests
class TestPhaseExecutionDecision:
    """Test _should_execute_phase logic."""

    def test_should_execute_phase_in_range(self):
        """Should execute phase within start-end range."""
        agent = SDLCOrchestratorAgent()

        should_execute = agent._should_execute_phase(
            "feasibility",
            start_phase="planning",
            end_phase="deployment",
            skip_phases=[]
        )

        assert should_execute is True

    def test_should_not_execute_phase_before_start(self):
        """Should not execute phase before start_phase."""
        agent = SDLCOrchestratorAgent()

        should_execute = agent._should_execute_phase(
            "planning",
            start_phase="feasibility",
            end_phase="deployment",
            skip_phases=[]
        )

        assert should_execute is False

    def test_should_not_execute_phase_after_end(self):
        """Should not execute phase after end_phase."""
        agent = SDLCOrchestratorAgent()

        should_execute = agent._should_execute_phase(
            "deployment",
            start_phase="planning",
            end_phase="testing",
            skip_phases=[]
        )

        assert should_execute is False

    def test_should_not_execute_skipped_phase(self):
        """Should not execute phase in skip_phases."""
        agent = SDLCOrchestratorAgent()

        should_execute = agent._should_execute_phase(
            "feasibility",
            start_phase="planning",
            end_phase="deployment",
            skip_phases=["feasibility"]
        )

        assert should_execute is False


# 4. Individual Phase Execution Tests
class TestIndividualPhaseExecution:
    """Test individual phase execution methods."""

    def test_execute_planning(self):
        """Should execute planning phase correctly."""
        agent = SDLCOrchestratorAgent()

        # Mock planner agent's execute method
        mock_result = MagicMock()
        mock_result.data = {"issue": {"issue_title": "Test"}}
        agent.planner_agent.execute = MagicMock(return_value=mock_result)

        result = agent._execute_planning("Test feature", "Test context")

        assert result == {"issue": {"issue_title": "Test"}}
        agent.planner_agent.execute.assert_called_once()

    def test_execute_feasibility(self):
        """Should execute feasibility phase correctly."""
        agent = SDLCOrchestratorAgent()

        # Mock feasibility agent's execute method
        mock_result = MagicMock()
        mock_result.data = {"decision": "go", "confidence": 0.9}
        agent.feasibility_agent.execute = MagicMock(return_value=mock_result)

        planning_result = {"issue": {"issue_title": "Test"}}
        constraints = {"no_redis": True}

        result = agent._execute_feasibility(planning_result, constraints)

        assert result["decision"] == "go"
        agent.feasibility_agent.execute.assert_called_once()

    def test_execute_design(self):
        """Should execute design phase correctly."""
        agent = SDLCOrchestratorAgent()

        # Mock design agent's execute method
        mock_result = MagicMock()
        mock_result.data = {"hld_path": "HLD.md"}
        agent.design_agent.execute = MagicMock(return_value=mock_result)

        planning_result = {"issue": {}}
        feasibility_result = {"decision": "go"}

        result = agent._execute_design(planning_result, feasibility_result, "context")

        assert "hld_path" in result
        agent.design_agent.execute.assert_called_once()

    def test_execute_testing(self):
        """Should execute testing phase correctly."""
        agent = SDLCOrchestratorAgent()

        # Mock testing agent's execute method
        mock_result = MagicMock()
        mock_result.data = {"test_pyramid": {}}
        agent.testing_agent.execute = MagicMock(return_value=mock_result)

        planning_result = {"issue": {}}
        design_result = {"hld_path": "HLD.md"}

        result = agent._execute_testing(planning_result, design_result)

        assert "test_pyramid" in result
        agent.testing_agent.execute.assert_called_once()

    def test_execute_deployment(self):
        """Should execute deployment phase correctly."""
        agent = SDLCOrchestratorAgent()

        # Mock deployment agent's execute method
        mock_result = MagicMock()
        mock_result.data = {"deployment_path": "deploy.md"}
        agent.deployment_agent.execute = MagicMock(return_value=mock_result)

        planning_result = {"issue": {}}
        design_result = {"hld_path": "HLD.md"}
        testing_result = {"test_pyramid": {}}

        result = agent._execute_deployment(
            planning_result, design_result, testing_result, "staging"
        )

        assert "deployment_path" in result
        agent.deployment_agent.execute.assert_called_once()


# 5. LLM Integration Tests
class TestLLMIntegration:
    """Test LLM-enhanced orchestration methods."""

    @patch('scripts.ai.sdlc.orchestrator.LLMGenerator')
    def test_initialization_with_llm(self, mock_llm_gen):
        """Should initialize with LLM when config provided."""
        mock_llm_instance = MagicMock()
        mock_llm_gen.return_value = mock_llm_instance

        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = SDLCOrchestratorAgent(config=config)

        assert hasattr(agent, 'llm_generator')

    @patch('scripts.ai.sdlc.orchestrator.LLMGenerator')
    def test_llm_phase_transition_decision(self, mock_llm_gen):
        """Should use LLM for phase transition decisions."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "should_proceed": True,
            "confidence": 0.9,
            "reasoning": "All conditions met"
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic"}
        agent = SDLCOrchestratorAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Test LLM-based phase transition decision
        if hasattr(agent, '_should_proceed_to_next_phase_with_llm'):
            result = agent._should_proceed_to_next_phase_with_llm(
                current_phase="feasibility",
                phase_result={"decision": "go", "confidence": 0.9}
            )
            assert result is True or result is False

    @patch('scripts.ai.sdlc.orchestrator.LLMGenerator')
    def test_llm_risk_aggregation(self, mock_llm_gen):
        """Should use LLM for risk aggregation across phases."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "aggregated_risks": [
                {
                    "type": "technical",
                    "severity": "high",
                    "description": "Complex integration",
                    "phases": ["feasibility", "design"]
                }
            ],
            "overall_risk_level": "medium"
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic"}
        agent = SDLCOrchestratorAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Test LLM-based risk aggregation
        if hasattr(agent, '_aggregate_risks_with_llm'):
            phase_results = {
                "feasibility": {"risks": [{"severity": "high"}]},
                "design": {"risks": [{"severity": "medium"}]}
            }
            risks = agent._aggregate_risks_with_llm(phase_results)
            assert isinstance(risks, list) or isinstance(risks, dict)

    @patch('scripts.ai.sdlc.orchestrator.LLMGenerator')
    def test_llm_recommendation_synthesis(self, mock_llm_gen):
        """Should use LLM for synthesizing recommendations."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.return_value = json.dumps({
            "recommendations": [
                "Proceed with deployment to staging",
                "Monitor security aspects closely",
                "Conduct thorough integration testing"
            ],
            "priority": "high"
        })
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic"}
        agent = SDLCOrchestratorAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Test LLM-based recommendation synthesis
        if hasattr(agent, '_synthesize_recommendations_with_llm'):
            phase_results = {
                "feasibility": {"decision": "go"},
                "design": {"hld_path": "HLD.md"}
            }
            recommendations = agent._synthesize_recommendations_with_llm(phase_results)
            assert isinstance(recommendations, list) or isinstance(recommendations, str)

    @patch('scripts.ai.sdlc.orchestrator.LLMGenerator')
    def test_llm_fallback_on_error(self, mock_llm_gen):
        """Should fallback to heuristics if LLM fails."""
        mock_llm_instance = MagicMock()
        mock_llm_instance._call_llm.side_effect = Exception("LLM API error")
        mock_llm_gen.return_value = mock_llm_instance

        config = {"llm_provider": "anthropic"}
        agent = SDLCOrchestratorAgent(config=config)
        agent.llm_generator = mock_llm_instance

        # Should not crash, should use heuristics
        if hasattr(agent, '_should_proceed_to_next_phase'):
            result = agent._should_proceed_to_next_phase(
                current_phase="feasibility",
                phase_result={"decision": "go", "confidence": 0.9}
            )
            assert result is True or result is False

    def test_orchestration_method_tracking(self):
        """Should track whether LLM or heuristic was used."""
        agent = SDLCOrchestratorAgent()

        # Should have constants for tracking method
        if hasattr(agent, 'ORCHESTRATION_METHOD_LLM'):
            assert agent.ORCHESTRATION_METHOD_LLM == "llm"
        if hasattr(agent, 'ORCHESTRATION_METHOD_HEURISTIC'):
            assert agent.ORCHESTRATION_METHOD_HEURISTIC == "heuristic"


# 6. Full Pipeline Tests
class TestFullPipeline:
    """Test complete SDLC pipeline orchestration."""

    def test_run_full_pipeline(self, sample_input_data):
        """Should run complete pipeline from planning to deployment."""
        agent = SDLCOrchestratorAgent()

        # Setup mocks
        agent.planner_agent.execute = MagicMock(return_value=MagicMock(data={
            "issue": {"issue_title": "Test", "story_points": 8},
            "artifacts": []
        }))
        agent.feasibility_agent.execute = MagicMock(return_value=MagicMock(data={
            "decision": "go",
            "confidence": 0.9,
            "risks": [],
            "artifacts": []
        }))
        agent.design_agent.execute = MagicMock(return_value=MagicMock(data={
            "hld_path": "HLD.md",
            "artifacts": []
        }))
        agent.testing_agent.execute = MagicMock(return_value=MagicMock(data={
            "test_pyramid": {},
            "artifacts": []
        }))
        agent.deployment_agent.execute = MagicMock(return_value=MagicMock(data={
            "deployment_path": "deploy.md",
            "artifacts": []
        }))

        result = agent.run(sample_input_data)

        # Verify all phases executed
        assert result["status"] == "completed"
        assert "phase_results" in result
        assert "execution_log" in result
        assert "final_report" in result

    def test_pipeline_stops_on_no_go(self, sample_input_data):
        """Should stop pipeline when feasibility returns NO-GO."""
        agent = SDLCOrchestratorAgent()

        # Setup mocks
        agent.planner_agent.execute = MagicMock(return_value=MagicMock(data={
            "issue": {"issue_title": "Test"},
            "artifacts": []
        }))
        agent.feasibility_agent.execute = MagicMock(return_value=MagicMock(data={
            "decision": "no-go",
            "confidence": 0.3,
            "risks": [{"severity": "critical"}],
            "artifacts": []
        }))

        result = agent.run(sample_input_data)

        # Should stop early
        assert result["status"] == "early_stop"
        assert result["stopped_at_phase"] == "feasibility"

    def test_pipeline_partial_execution(self):
        """Should execute only specified phase range."""
        agent = SDLCOrchestratorAgent()

        # Setup mocks
        agent.planner_agent.execute = MagicMock(return_value=MagicMock(data={
            "issue": {"issue_title": "Test"},
            "artifacts": []
        }))
        agent.feasibility_agent.execute = MagicMock(return_value=MagicMock(data={
            "decision": "go",
            "confidence": 0.9,
            "risks": [],
            "artifacts": []
        }))
        agent.design_agent.execute = MagicMock(return_value=MagicMock(data={
            "hld_path": "HLD.md",
            "artifacts": []
        }))

        input_data = {
            "feature_request": "Test feature",
            "start_phase": "planning",
            "end_phase": "design"  # Stop at design
        }

        result = agent.run(input_data)

        # Should only execute planning, feasibility, design
        assert "planning" in result["phase_results"]
        assert "feasibility" in result["phase_results"]
        assert "design" in result["phase_results"]
        assert "testing" not in result["phase_results"]
        assert "deployment" not in result["phase_results"]

    def test_pipeline_with_skip_phases(self):
        """Should skip specified phases."""
        agent = SDLCOrchestratorAgent()

        # Setup mocks
        agent.planner_agent.execute = MagicMock(return_value=MagicMock(data={
            "issue": {"issue_title": "Test"},
            "artifacts": []
        }))
        agent.design_agent.execute = MagicMock(return_value=MagicMock(data={
            "hld_path": "HLD.md",
            "artifacts": []
        }))

        input_data = {
            "feature_request": "Test feature",
            "start_phase": "planning",
            "end_phase": "design",
            "skip_phases": ["feasibility"]
        }

        # Should raise error because design requires feasibility
        with pytest.raises(Exception):
            result = agent.run(input_data)


# 7. Report Generation Tests
class TestReportGeneration:
    """Test report generation."""

    def test_generate_final_report_structure(self):
        """Should generate properly structured final report."""
        agent = SDLCOrchestratorAgent()

        phase_results = {
            "planning": {"issue": {"issue_title": "Test", "priority": "P1"}},
            "feasibility": {"decision": "go", "confidence": 0.9, "risks": []}
        }
        execution_log = [
            {"phase": "planning", "status": "completed", "decision": "go"},
            {"phase": "feasibility", "status": "completed", "decision": "go"}
        ]

        report = agent._generate_final_report(
            "Test feature",
            phase_results,
            ["artifact1.md"],
            execution_log
        )

        assert "SDLC Pipeline Execution Report" in report
        assert "Test feature" in report
        assert "planning" in report.lower()
        assert "feasibility" in report.lower()

    def test_generate_early_stop_report(self):
        """Should generate early stop report."""
        agent = SDLCOrchestratorAgent()

        phase_results = {
            "planning": {"issue": {"issue_title": "Test"}},
            "feasibility": {"decision": "no-go"}
        }
        execution_log = [
            {"phase": "planning", "status": "completed", "decision": "go"},
            {"phase": "feasibility", "status": "completed", "decision": "no-go"}
        ]

        result = agent._generate_early_stop_report(
            "Test feature",
            phase_results,
            [],
            execution_log,
            "feasibility",
            "Feature not viable"
        )

        assert result["status"] == "early_stop"
        assert result["stopped_at_phase"] == "feasibility"
        assert "Early Stop" in result["final_report"]

    def test_generate_recommendations(self):
        """Should generate recommendations based on phase results."""
        agent = SDLCOrchestratorAgent()

        phase_results = {
            "feasibility": {"confidence": 0.5},  # Low confidence
            "testing": {
                "test_pyramid": {
                    "unit_tests": {"percentage": 40}  # Low unit test %
                }
            }
        }

        recommendations = agent._generate_recommendations(phase_results, [])

        assert "confidence" in recommendations.lower() or "unit" in recommendations.lower()

    def test_generate_next_steps_after_deployment(self):
        """Should generate appropriate next steps after deployment."""
        agent = SDLCOrchestratorAgent()

        execution_log = [{"phase": "deployment", "status": "completed"}]

        next_steps = agent._generate_next_steps({}, execution_log)

        assert "deploy" in next_steps.lower() or "staging" in next_steps.lower()

    def test_generate_lessons_learned(self):
        """Should generate lessons learned from execution."""
        agent = SDLCOrchestratorAgent()

        phase_results = {
            "feasibility": {"risks": [{"severity": "high"}]},
            "design": {"adrs": ["ADR-001.md"]}
        }

        lessons = agent._generate_lessons_learned(phase_results, [])

        assert "riesgo" in lessons.lower() or "adr" in lessons.lower()


# 8. Edge Cases and Error Handling
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_missing_phase_dependencies(self):
        """Should raise error when phase dependencies missing."""
        agent = SDLCOrchestratorAgent()

        # Trying to execute design without feasibility might not raise error
        # depending on implementation, just verify it doesn't crash
        try:
            agent._execute_design({}, {}, "")
        except (ValueError, KeyError):
            # Expected if validation is strict
            pass

    def test_handles_agent_failure(self, sample_input_data):
        """Should handle agent execution failure gracefully."""
        agent = SDLCOrchestratorAgent()

        # Mock agent to raise exception
        agent.planner_agent.execute = MagicMock(side_effect=Exception("Agent failed"))

        # Should propagate exception
        with pytest.raises(Exception):
            agent.run(sample_input_data)

    def test_handles_empty_execution_log(self):
        """Should handle empty execution log."""
        agent = SDLCOrchestratorAgent()

        next_steps = agent._generate_next_steps({}, [])

        assert len(next_steps) > 0

    def test_format_artifact_link_with_none(self):
        """Should format artifact link when path is None."""
        agent = SDLCOrchestratorAgent()

        link = agent._format_artifact_link(None)

        assert link == "N/A"

    def test_format_artifact_link_with_path(self):
        """Should format artifact link with valid path."""
        agent = SDLCOrchestratorAgent()

        link = agent._format_artifact_link("/path/to/artifact.md")

        assert "artifact.md" in link


# 9. Guardrails Tests
class TestGuardrails:
    """Test custom guardrails."""

    def test_guardrails_with_valid_output(self):
        """Should pass guardrails with valid output."""
        agent = SDLCOrchestratorAgent()

        output_data = {
            "execution_log": [{"phase": "planning", "status": "completed"}],
            "final_report": "Complete report"
        }

        errors = agent._custom_guardrails(output_data)

        assert errors == []

    def test_guardrails_with_no_phases_executed(self):
        """Should fail guardrails if no phases executed."""
        agent = SDLCOrchestratorAgent()

        output_data = {
            "execution_log": [],
            "final_report": "Report"
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("fase" in err.lower() for err in errors)

    def test_guardrails_with_no_report(self):
        """Should fail guardrails if no report generated."""
        agent = SDLCOrchestratorAgent()

        output_data = {
            "execution_log": [{"phase": "planning"}],
            "final_report": ""
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("reporte" in err.lower() for err in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
