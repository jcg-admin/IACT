#!/usr/bin/env python3
"""
TDD Tests for SDLCDeploymentAgent

Tests the SDLCDeploymentAgent implementation which generates deployment plans,
rollback plans, and deployment procedures for features.

Tests cover both LLM-enhanced and heuristic fallback methods.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, Mock
from scripts.ai.sdlc.deployment_agent import (
    SDLCDeploymentAgent,
    DEPLOYMENT_METHOD_LLM,
    DEPLOYMENT_METHOD_HEURISTIC
)


# Fixtures
@pytest.fixture
def sample_issue():
    """Sample issue for testing."""
    return {
        "issue_title": "Implement User Authentication System",
        "issue_number": "IACT-456",
        "priority": "P0",
        "story_points": 8,
        "technical_requirements": [
            "Create authentication models",
            "Implement JWT token generation",
            "Add login/logout endpoints",
            "Create password hashing"
        ],
        "acceptance_criteria": [
            "User can log in with credentials",
            "User can log out",
            "Tokens expire after configured time",
            "Passwords are securely hashed"
        ]
    }


@pytest.fixture
def sample_design_result():
    """Sample design result from SDLCDesignAgent."""
    return {
        "hld": "# High-Level Design\nAuthentication system...",
        "lld": "# Low-Level Design\nDetailed implementation...",
        "database_schema": """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            password_hash VARCHAR(255)
        );
        """,
        "diagrams": {
            "architecture": "```mermaid\ngraph TB...",
            "sequence": "```mermaid\nsequenceDiagram..."
        }
    }


@pytest.fixture
def sample_testing_result():
    """Sample testing result from SDLCTestingAgent."""
    from scripts.ai.sdlc.base_agent import SDLCPhaseResult

    phase_result = SDLCPhaseResult(
        phase="testing",
        decision="go",
        confidence=0.9,
        artifacts=[],
        recommendations=[],
        risks=[],
        next_steps=[]
    )

    return {
        "test_plan": "# Test Plan\nComprehensive testing...",
        "test_cases": [
            {"id": "UT-001", "type": "unit", "status": "passed"},
            {"id": "IT-001", "type": "integration", "status": "passed"}
        ],
        "coverage_requirements": {
            "overall_target": 85
        },
        "phase_result": phase_result
    }


@pytest.fixture
def sample_input_data(sample_issue, sample_design_result, sample_testing_result):
    """Sample input data for agent run."""
    return {
        "issue": sample_issue,
        "design_result": sample_design_result,
        "testing_result": sample_testing_result,
        "environment": "staging"
    }


@pytest.fixture
def complex_issue():
    """Complex issue with database migrations."""
    return {
        "issue_title": "Migrate Legacy Data and Add New Analytics",
        "issue_number": "IACT-999",
        "priority": "P1",
        "story_points": 13,
        "technical_requirements": [
            "Create new analytics models",
            "Migrate legacy data",
            "Add data aggregation service",
            "Update database schema"
        ],
        "acceptance_criteria": [
            "Legacy data migrated successfully",
            "Analytics dashboard shows correct data",
            "Performance within acceptable limits"
        ]
    }


# 1. Initialization Tests
class TestDeploymentAgentInitialization:
    """Test SDLCDeploymentAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = SDLCDeploymentAgent()

        assert agent.name == "SDLCDeploymentAgent"
        assert agent.phase == "deployment"

    def test_initialization_with_config(self):
        """Should initialize with config parameter for LLM."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929"
        }
        agent = SDLCDeploymentAgent(config=config)

        assert agent.name == "SDLCDeploymentAgent"
        assert agent.phase == "deployment"

    def test_initialization_without_config(self):
        """Should initialize without config (heuristic mode)."""
        agent = SDLCDeploymentAgent(config=None)

        assert agent.name == "SDLCDeploymentAgent"
        assert agent.llm_generator is None


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation."""

    def test_validate_valid_input(self, sample_input_data):
        """Should accept valid input data."""
        agent = SDLCDeploymentAgent()

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_testing_result(self, sample_issue, sample_design_result):
        """Should reject input without testing_result."""
        agent = SDLCDeploymentAgent()
        input_data = {
            "issue": sample_issue,
            "design_result": sample_design_result
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("testing_result" in err.lower() for err in errors)

    def test_validate_missing_design_result(self, sample_issue, sample_testing_result):
        """Should reject input without design_result."""
        agent = SDLCDeploymentAgent()
        input_data = {
            "issue": sample_issue,
            "testing_result": sample_testing_result
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("design_result" in err.lower() for err in errors)

    def test_validate_missing_issue(self, sample_design_result, sample_testing_result):
        """Should reject input without issue."""
        agent = SDLCDeploymentAgent()
        input_data = {
            "design_result": sample_design_result,
            "testing_result": sample_testing_result
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("issue" in err.lower() for err in errors)

    def test_validate_failed_tests(self, sample_issue, sample_design_result):
        """Should reject input when tests failed."""
        from scripts.ai.sdlc.base_agent import SDLCPhaseResult

        agent = SDLCDeploymentAgent()

        # Testing result with failed tests
        phase_result = SDLCPhaseResult(
            phase="testing",
            decision="no-go",
            confidence=0.3,
            artifacts=[],
            recommendations=[],
            risks=[],
            next_steps=[]
        )

        testing_result = {
            "test_plan": "Test plan",
            "phase_result": phase_result
        }

        input_data = {
            "issue": sample_issue,
            "design_result": sample_design_result,
            "testing_result": testing_result
        }

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("tests" in err.lower() or "no se puede deployar" in err.lower() for err in errors)

    def test_validate_missing_all_fields(self):
        """Should reject input without required fields."""
        agent = SDLCDeploymentAgent()
        input_data = {"environment": "staging"}

        errors = agent.validate_input(input_data)

        assert len(errors) >= 3  # Missing issue, design_result, testing_result


# 3. Heuristic Deployment Plan Generation Tests
class TestDeploymentPlanGenerationHeuristic:
    """Test heuristic deployment plan generation."""

    def test_generate_deployment_plan_structure(self, sample_issue, sample_design_result, sample_testing_result):
        """Should generate deployment plan with correct structure."""
        agent = SDLCDeploymentAgent()

        plan = agent._generate_deployment_plan(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "staging"
        )

        assert "Deployment Plan" in plan
        assert "Executive Summary" in plan
        assert "Prerequisites" in plan
        assert "Deployment Steps" in plan
        assert "Rollback Criteria" in plan
        assert sample_issue["issue_title"] in plan

    def test_generate_deployment_plan_includes_backup_steps(
        self, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should include backup steps in deployment plan."""
        agent = SDLCDeploymentAgent()

        plan = agent._generate_deployment_plan(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "production"
        )

        assert "backup" in plan.lower() or "mysqldump" in plan.lower()

    def test_generate_deployment_plan_includes_health_checks(
        self, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should include health checks in deployment plan."""
        agent = SDLCDeploymentAgent()

        plan = agent._generate_deployment_plan(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "staging"
        )

        assert "health check" in plan.lower() or "health_check" in plan.lower()

    def test_generate_deployment_plan_includes_environment(
        self, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should include target environment in deployment plan."""
        agent = SDLCDeploymentAgent()

        plan = agent._generate_deployment_plan(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "production"
        )

        assert "production" in plan.lower()


# 4. Heuristic Rollback Plan Generation Tests
class TestRollbackPlanGenerationHeuristic:
    """Test heuristic rollback plan generation."""

    def test_generate_rollback_plan_structure(self, sample_issue):
        """Should generate rollback plan with correct structure."""
        agent = SDLCDeploymentAgent()

        rollback_plan = agent._generate_rollback_plan(sample_issue, "staging")

        assert "Rollback Plan" in rollback_plan
        assert "Rollback Decision" in rollback_plan
        assert "Rollback Steps" in rollback_plan
        assert sample_issue["issue_title"] in rollback_plan

    def test_generate_rollback_plan_includes_restore_code(self, sample_issue):
        """Should include code restoration steps."""
        agent = SDLCDeploymentAgent()

        rollback_plan = agent._generate_rollback_plan(sample_issue, "production")

        assert "git checkout" in rollback_plan.lower() or "restore code" in rollback_plan.lower()

    def test_generate_rollback_plan_includes_database_rollback(self, sample_issue):
        """Should include database rollback considerations."""
        agent = SDLCDeploymentAgent()

        rollback_plan = agent._generate_rollback_plan(sample_issue, "production")

        assert "database" in rollback_plan.lower()
        assert "migration" in rollback_plan.lower() or "restore" in rollback_plan.lower()

    def test_generate_rollback_plan_includes_verification(self, sample_issue):
        """Should include verification steps."""
        agent = SDLCDeploymentAgent()

        rollback_plan = agent._generate_rollback_plan(sample_issue, "staging")

        assert "verify" in rollback_plan.lower() or "check" in rollback_plan.lower()


# 5. Checklist Generation Tests
class TestChecklistGeneration:
    """Test pre and post deployment checklist generation."""

    def test_generate_pre_deployment_checklist_structure(self, sample_issue, sample_testing_result):
        """Should generate pre-deployment checklist with correct structure."""
        agent = SDLCDeploymentAgent()

        checklist = agent._generate_pre_deployment_checklist(sample_issue, sample_testing_result)

        assert "Pre-Deployment Checklist" in checklist
        assert "Code Quality" in checklist
        assert "Testing" in checklist
        assert "Critical IACT Restrictions" in checklist

    def test_generate_pre_deployment_checklist_includes_iact_restrictions(
        self, sample_issue, sample_testing_result
    ):
        """Should include IACT-specific restrictions."""
        agent = SDLCDeploymentAgent()

        checklist = agent._generate_pre_deployment_checklist(sample_issue, sample_testing_result)

        assert "NO Redis" in checklist or "redis" in checklist.lower()
        assert "MySQL" in checklist or "mysql" in checklist.lower()

    def test_generate_post_deployment_checklist_structure(self, sample_issue):
        """Should generate post-deployment checklist with correct structure."""
        agent = SDLCDeploymentAgent()

        checklist = agent._generate_post_deployment_checklist(sample_issue)

        assert "Post-Deployment Checklist" in checklist
        assert "Immediate Verification" in checklist
        assert "Functional Verification" in checklist
        assert "Performance Verification" in checklist

    def test_generate_post_deployment_checklist_includes_rollback_decision(self, sample_issue):
        """Should include rollback decision point."""
        agent = SDLCDeploymentAgent()

        checklist = agent._generate_post_deployment_checklist(sample_issue)

        assert "rollback" in checklist.lower()
        assert "YES / NO" in checklist or "yes / no" in checklist.lower()


# 6. Monitoring Plan Generation Tests
class TestMonitoringPlanGeneration:
    """Test monitoring plan generation."""

    def test_generate_monitoring_plan_structure(self, sample_issue):
        """Should generate monitoring plan with correct structure."""
        agent = SDLCDeploymentAgent()

        monitoring_plan = agent._generate_monitoring_plan(sample_issue)

        assert "Monitoring Plan" in monitoring_plan
        assert "Key Metrics" in monitoring_plan
        assert "Monitoring Tools" in monitoring_plan
        assert "Alerting" in monitoring_plan

    def test_generate_monitoring_plan_includes_database_checks(self, sample_issue):
        """Should include database monitoring."""
        agent = SDLCDeploymentAgent()

        monitoring_plan = agent._generate_monitoring_plan(sample_issue)

        assert "database" in monitoring_plan.lower()
        assert "session" in monitoring_plan.lower() or "django_session" in monitoring_plan

    def test_generate_monitoring_plan_includes_response_time_metrics(self, sample_issue):
        """Should include response time metrics."""
        agent = SDLCDeploymentAgent()

        monitoring_plan = agent._generate_monitoring_plan(sample_issue)

        assert "response time" in monitoring_plan.lower()


# 7. LLM Integration Tests (with mocking)
class TestLLMIntegration:
    """Test LLM integration for deployment strategy generation."""

    @patch('scripts.ai.sdlc.deployment_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_initialization_with_llm_available(self, mock_llm_generator):
        """Should initialize LLM when config provided and available."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929"
        }

        agent = SDLCDeploymentAgent(config=config)

        # With LLM available and config provided, should initialize
        assert agent.llm_generator is not None or mock_llm_generator.called

    @patch('scripts.ai.sdlc.deployment_agent.LLM_AVAILABLE', False)
    def test_initialization_with_llm_unavailable(self):
        """Should fall back to heuristics when LLM unavailable."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929"
        }

        agent = SDLCDeploymentAgent(config=config)

        assert agent.llm_generator is None

    @patch('scripts.ai.sdlc.deployment_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_generate_deployment_strategy_with_llm_success(
        self, mock_llm_generator, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should use LLM to generate enhanced deployment strategy."""
        # Mock LLM response
        mock_instance = Mock()
        mock_instance._call_llm.return_value = json.dumps({
            "deployment_strategy": {
                "approach": "rolling",
                "phases": ["phase1", "phase2"],
                "risk_mitigation": ["backup", "gradual rollout"],
                "estimated_downtime": "0 minutes"
            }
        })
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)
        # Set llm_generator directly since mocking might not work as expected
        agent.llm_generator = mock_instance

        strategy = agent._generate_deployment_strategy_with_llm(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "production"
        )

        assert strategy is not None
        assert "deployment_strategy" in strategy
        assert strategy["deployment_strategy"]["approach"] == "rolling"

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_generate_deployment_strategy_with_llm_failure_fallback(
        self, mock_llm_generator, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should fall back to heuristics when LLM fails."""
        # Mock LLM to raise exception
        mock_instance = Mock()
        mock_instance._call_llm.side_effect = Exception("LLM API error")
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)

        strategy = agent._generate_deployment_strategy_with_llm(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "production"
        )

        # Should return fallback strategy
        assert strategy is not None

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_identify_deployment_risks_with_llm(
        self, mock_llm_generator, sample_issue, sample_design_result, sample_testing_result
    ):
        """Should use LLM to identify deployment risks."""
        # Mock LLM response
        mock_instance = Mock()
        mock_instance._call_llm.return_value = json.dumps({
            "risks": [
                {
                    "type": "technical",
                    "severity": "high",
                    "description": "Database migration may take longer than expected",
                    "mitigation": "Test migration on staging first"
                }
            ]
        })
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)

        risks = agent._identify_deployment_risks_with_llm(
            sample_issue,
            sample_design_result,
            sample_testing_result,
            "production"
        )

        assert isinstance(risks, list)
        if len(risks) > 0:
            assert "description" in risks[0] or "risk" in str(risks[0]).lower()

    @patch('scripts.ai.sdlc.deployment_agent.LLM_AVAILABLE', True)
    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_generate_rollback_strategy_with_llm(
        self, mock_llm_generator, sample_issue, sample_design_result
    ):
        """Should use LLM to generate rollback strategy."""
        # Mock LLM response
        mock_instance = Mock()
        mock_instance._call_llm.return_value = json.dumps({
            "rollback_strategy": {
                "triggers": ["health check fails", "critical errors"],
                "steps": ["stop services", "restore code", "restart"],
                "estimated_time": "5-10 minutes",
                "data_loss_risk": "low"
            }
        })
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)
        agent.llm_generator = mock_instance

        rollback_strategy = agent._generate_rollback_strategy_with_llm(
            sample_issue,
            sample_design_result,
            "production"
        )

        assert rollback_strategy is not None
        assert "rollback_strategy" in rollback_strategy
        assert "triggers" in rollback_strategy["rollback_strategy"]

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_generate_monitoring_strategy_with_llm(
        self, mock_llm_generator, sample_issue, sample_design_result
    ):
        """Should use LLM to generate monitoring strategy."""
        # Mock LLM response
        mock_instance = Mock()
        mock_instance._call_llm.return_value = json.dumps({
            "monitoring_strategy": {
                "key_metrics": ["response_time", "error_rate", "database_connections"],
                "alert_thresholds": {
                    "error_rate": "5%",
                    "response_time": "2s"
                },
                "monitoring_duration": "24 hours intensive"
            }
        })
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)

        monitoring_strategy = agent._generate_monitoring_strategy_with_llm(
            sample_issue,
            sample_design_result,
            "production"
        )

        assert monitoring_strategy is not None
        assert "key_metrics" in monitoring_strategy or "monitoring" in str(monitoring_strategy).lower()

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_parse_llm_deployment_strategy(self, mock_llm_generator):
        """Should parse LLM response for deployment strategy."""
        agent = SDLCDeploymentAgent()

        llm_response = json.dumps({
            "deployment_strategy": {
                "approach": "blue-green",
                "phases": ["deploy to blue", "switch traffic"],
                "risk_mitigation": ["keep green as backup"],
                "estimated_downtime": "0 minutes"
            }
        })

        strategy = agent._parse_llm_deployment_strategy(llm_response, {}, {}, {}, "production")

        assert strategy is not None
        assert "deployment_strategy" in strategy
        assert "approach" in strategy["deployment_strategy"]
        assert strategy["deployment_strategy"]["approach"] == "blue-green"

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_parse_llm_deployment_risks(self, mock_llm_generator):
        """Should parse LLM response for deployment risks."""
        agent = SDLCDeploymentAgent()

        llm_response = json.dumps({
            "risks": [
                {
                    "type": "technical",
                    "severity": "high",
                    "description": "Migration complexity",
                    "mitigation": "Test thoroughly"
                }
            ]
        })

        risks = agent._parse_llm_deployment_risks(llm_response, {}, {}, {})

        assert isinstance(risks, list)
        if len(risks) > 0:
            assert "description" in risks[0]


# 8. Full Pipeline Tests
class TestFullPipeline:
    """Test full deployment agent pipeline."""

    def test_run_with_heuristic_mode(self, sample_input_data, tmp_path):
        """Should run full pipeline in heuristic mode."""
        agent = SDLCDeploymentAgent(config=None)

        # Override artifacts_dir for testing
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert "deployment_plan" in result
        assert "rollback_plan" in result
        assert "pre_deployment_checklist" in result
        assert "post_deployment_checklist" in result
        assert "monitoring_plan" in result
        assert "phase_result" in result
        assert "deployment_method" in result
        assert result["deployment_method"] == DEPLOYMENT_METHOD_HEURISTIC

    @patch('scripts.ai.sdlc.deployment_agent.LLMGenerator')
    def test_run_with_llm_mode(self, mock_llm_generator, sample_input_data, tmp_path):
        """Should run full pipeline with LLM enhancement."""
        # Mock LLM responses
        mock_instance = Mock()
        mock_instance._call_llm.return_value = json.dumps({
            "deployment_strategy": {
                "approach": "rolling",
                "phases": ["phase1"],
                "risk_mitigation": ["backup"],
                "estimated_downtime": "0 minutes"
            }
        })
        mock_llm_generator.return_value = mock_instance

        config = {"llm_provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        agent = SDLCDeploymentAgent(config=config)
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert "deployment_plan" in result
        assert "deployment_method" in result

    def test_run_creates_artifacts(self, sample_input_data, tmp_path):
        """Should create all deployment artifacts."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert "artifacts" in result
        assert len(result["artifacts"]) == 5  # deployment, rollback, pre-check, post-check, monitoring

    def test_run_with_production_environment(self, sample_input_data, tmp_path):
        """Should handle production environment correctly."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        sample_input_data["environment"] = "production"

        result = agent.run(sample_input_data)

        assert result["environment"] == "production"
        assert "PRODUCTION" in result["deployment_plan"]

    def test_run_phase_result_decision_is_go(self, sample_input_data, tmp_path):
        """Should return 'go' decision for successful deployment plan."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert result["phase_result"].decision == "go"

    def test_run_phase_result_has_recommendations(self, sample_input_data, tmp_path):
        """Should include recommendations in phase result."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert len(result["phase_result"].recommendations) > 0

    def test_run_phase_result_has_next_steps(self, sample_input_data, tmp_path):
        """Should include next steps in phase result."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        assert len(result["phase_result"].next_steps) > 0


# 9. Edge Cases Tests
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_run_with_minimal_issue(self, sample_design_result, sample_testing_result, tmp_path):
        """Should handle issue with minimal information."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        minimal_issue = {
            "issue_title": "Minimal Feature",
            "issue_number": "IACT-001"
        }

        input_data = {
            "issue": minimal_issue,
            "design_result": sample_design_result,
            "testing_result": sample_testing_result
        }

        result = agent.run(input_data)

        assert result is not None
        assert "deployment_plan" in result

    def test_run_defaults_to_staging_environment(
        self, sample_issue, sample_design_result, sample_testing_result, tmp_path
    ):
        """Should default to staging environment if not specified."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        input_data = {
            "issue": sample_issue,
            "design_result": sample_design_result,
            "testing_result": sample_testing_result
            # No environment specified
        }

        result = agent.run(input_data)

        assert result["environment"] == "staging"

    def test_database_migrations_list_empty_by_default(self, sample_design_result):
        """Should handle missing database migrations."""
        agent = SDLCDeploymentAgent()

        migrations = agent._list_database_migrations(sample_design_result)

        assert migrations is not None
        assert isinstance(migrations, str)

    def test_data_migrations_list_empty_by_default(self, sample_design_result):
        """Should handle missing data migrations."""
        agent = SDLCDeploymentAgent()

        data_migrations = agent._list_data_migrations(sample_design_result)

        assert data_migrations is not None
        assert isinstance(data_migrations, str)


# 10. Guardrails Tests
class TestGuardrails:
    """Test custom guardrails for deployment phase."""

    def test_guardrails_valid_output(self, sample_input_data, tmp_path):
        """Should pass guardrails with valid output."""
        agent = SDLCDeploymentAgent()
        agent.artifacts_dir = tmp_path

        result = agent.run(sample_input_data)

        errors = agent._custom_guardrails(result)

        assert len(errors) == 0

    def test_guardrails_missing_deployment_plan(self):
        """Should fail guardrails when deployment plan missing."""
        agent = SDLCDeploymentAgent()

        output_data = {
            "rollback_plan": "some plan",
            "pre_deployment_checklist": "checklist",
            "post_deployment_checklist": "checklist"
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("deployment plan" in err.lower() for err in errors)

    def test_guardrails_missing_rollback_plan(self):
        """Should fail guardrails when rollback plan missing."""
        agent = SDLCDeploymentAgent()

        output_data = {
            "deployment_plan": "some plan",
            "pre_deployment_checklist": "checklist",
            "post_deployment_checklist": "checklist"
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("rollback plan" in err.lower() for err in errors)

    def test_guardrails_missing_checklists(self):
        """Should fail guardrails when checklists missing."""
        agent = SDLCDeploymentAgent()

        output_data = {
            "deployment_plan": "some plan",
            "rollback_plan": "rollback plan"
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) >= 2  # Missing pre and post checklists

    def test_guardrails_deployment_plan_without_backup(self):
        """Should fail guardrails when deployment plan doesn't mention backup."""
        agent = SDLCDeploymentAgent()

        output_data = {
            "deployment_plan": "Deploy without any precautions",
            "rollback_plan": "rollback",
            "pre_deployment_checklist": "checklist",
            "post_deployment_checklist": "checklist"
        }

        errors = agent._custom_guardrails(output_data)

        assert len(errors) > 0
        assert any("backup" in err.lower() for err in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
