"""
Tests for PDCAAutomationAgent - TDD Strict Approach

Tests PDCA automation cycle: Plan-Do-Check-Act for continuous improvement.

Author: TDD Process
Date: 2025-11-14

TDD Cycles Applied:
- Cycle 1: Configuration management (load/save config)
- Cycle 2: History management (load/save history)
- Cycle 3: DORA metrics (baseline and mock)
- Cycle 4: PLAN phase (analysis and proposals)
- Cycle 5: DO phase (execution)
- Cycle 6: CHECK phase (validation)
- Cycle 7: ACT phase (decision)
- Cycle 8: Full cycle integration
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Import will fail until we implement the agent (TDD RED phase)
try:
    from scripts.gobernanza_sdlc.automation.pdca_agent import (
        PDCAAutomationAgent,
        PDCAPhase,
        DecisionAction
    )
except ImportError:
    pytest.skip("PDCAAutomationAgent not yet implemented", allow_module_level=True)


# ============================================================================
# TDD CYCLE 1: Configuration Management
# ============================================================================

class TestPDCAAgentConfiguration:
    """Test configuration loading and saving - TDD Cycle 1."""

    def test_agent_initialization_with_defaults(self):
        """RED: Test agent initializes with default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            assert agent.repo == "owner/repo"
            assert agent.config_file == config_file
            assert agent.baseline_days == 30
            assert agent.validation_threshold == 0.05
            assert agent.config is not None
            assert isinstance(agent.config, dict)

    def test_load_config_creates_default_when_missing(self):
        """RED: Test default config is created when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            config = agent.config
            assert config["enabled"] is True
            assert config["auto_apply_threshold"] == 0.15
            assert config["auto_revert_threshold"] == -0.05
            assert "metrics_priority" in config
            assert config["metrics_priority"]["deployment_frequency"] == 0.30

    def test_load_config_reads_existing_file(self):
        """RED: Test config is loaded from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            custom_config = {
                "enabled": False,
                "auto_apply_threshold": 0.20,
                "auto_revert_threshold": -0.10,
                "metrics_priority": {
                    "deployment_frequency": 0.40,
                    "lead_time_for_changes": 0.30,
                    "change_failure_rate": 0.20,
                    "mean_time_to_recovery": 0.10
                }
            }
            config_file.write_text(json.dumps(custom_config, indent=2))

            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            assert agent.config["enabled"] is False
            assert agent.config["auto_apply_threshold"] == 0.20
            assert agent.config["metrics_priority"]["deployment_frequency"] == 0.40

    def test_save_config_writes_to_file(self):
        """RED: Test config is saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            agent.config["enabled"] = False
            agent._save_config()

            assert config_file.exists()
            saved_config = json.loads(config_file.read_text())
            assert saved_config["enabled"] is False


# ============================================================================
# TDD CYCLE 2: History Management
# ============================================================================

class TestPDCAAgentHistory:
    """Test history loading and saving - TDD Cycle 2."""

    def test_load_history_returns_empty_when_missing(self):
        """RED: Test empty history when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            assert agent.history == []
            assert isinstance(agent.history, list)

    def test_load_history_reads_existing_file(self):
        """RED: Test history is loaded from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            history_file = Path(tmpdir) / ".pdca_history.json"

            sample_history = [
                {
                    "cycle_id": "pdca-20251114-120000",
                    "decision": "apply",
                    "score": 18.5
                }
            ]
            history_file.write_text(json.dumps(sample_history))

            # Create agent in same directory
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )
            # Manually set history file path to match tmpdir
            agent.history_file = history_file
            agent.history = agent._load_history()

            assert len(agent.history) == 1
            assert agent.history[0]["cycle_id"] == "pdca-20251114-120000"

    def test_save_history_writes_to_file(self):
        """RED: Test history is saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )
            agent.history_file = Path(tmpdir) / ".pdca_history.json"

            agent.history.append({
                "cycle_id": "pdca-20251114-130000",
                "decision": "revert"
            })
            agent._save_history()

            assert agent.history_file.exists()
            saved_history = json.loads(agent.history_file.read_text())
            assert len(saved_history) == 1
            assert saved_history[0]["cycle_id"] == "pdca-20251114-130000"


# ============================================================================
# TDD CYCLE 3: DORA Metrics
# ============================================================================

class TestPDCAAgentMetrics:
    """Test DORA metrics handling - TDD Cycle 3."""

    def test_get_mock_metrics_returns_valid_structure(self):
        """RED: Test mock metrics returns valid data structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            metrics = agent._get_mock_metrics()

            assert "deployment_frequency" in metrics
            assert "lead_time_for_changes" in metrics
            assert "change_failure_rate" in metrics
            assert "mean_time_to_recovery" in metrics
            assert "timestamp" in metrics
            assert metrics["mock"] is True

    def test_get_mock_metrics_returns_numeric_values(self):
        """RED: Test mock metrics returns numeric values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            metrics = agent._get_mock_metrics()

            assert isinstance(metrics["deployment_frequency"], (int, float))
            assert isinstance(metrics["lead_time_for_changes"], (int, float))
            assert isinstance(metrics["change_failure_rate"], (int, float))
            assert isinstance(metrics["mean_time_to_recovery"], (int, float))

    def test_get_baseline_metrics_uses_mock_without_token(self):
        """RED: Test baseline metrics uses mock when no GitHub token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                github_token=None,
                config_file=str(config_file)
            )

            metrics = agent._get_baseline_metrics()

            assert metrics.get("mock") is True
            assert "deployment_frequency" in metrics


# ============================================================================
# TDD CYCLE 4: PLAN Phase
# ============================================================================

class TestPDCAPlanPhase:
    """Test PLAN phase functionality - TDD Cycle 4."""

    def test_plan_returns_valid_structure(self):
        """RED: Test plan phase returns valid structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)

            assert "cycle_id" in plan
            assert "phase" in plan
            assert plan["phase"] == PDCAPhase.PLAN.value
            assert "baseline_metrics" in plan
            assert "improvements" in plan
            assert isinstance(plan["improvements"], list)

    def test_plan_identifies_improvements_for_low_deployment_frequency(self):
        """RED: Test plan identifies improvement for low deployment frequency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = {
                'deployment_frequency': 0.5,
                'lead_time_for_changes': 20.0,
                'change_failure_rate': 10.0,
                'mean_time_to_recovery': 0.5,
                'timestamp': datetime.now().isoformat()
            }
            plan = agent.plan(baseline)

            improvements = plan["improvements"]
            df_improvements = [i for i in improvements if i["metric"] == "deployment_frequency"]
            assert len(df_improvements) > 0
            assert df_improvements[0]["current"] == 0.5

    def test_plan_identifies_improvements_for_high_lead_time(self):
        """RED: Test plan identifies improvement for high lead time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = {
                'deployment_frequency': 2.0,
                'lead_time_for_changes': 48.0,
                'change_failure_rate': 10.0,
                'mean_time_to_recovery': 0.5,
                'timestamp': datetime.now().isoformat()
            }
            plan = agent.plan(baseline)

            improvements = plan["improvements"]
            lt_improvements = [i for i in improvements if i["metric"] == "lead_time_for_changes"]
            assert len(lt_improvements) > 0
            assert lt_improvements[0]["current"] == 48.0

    def test_plan_calculates_estimated_impact(self):
        """RED: Test plan calculates estimated impact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)

            assert "estimated_impact" in plan
            assert isinstance(plan["estimated_impact"], dict)


# ============================================================================
# TDD CYCLE 5: DO Phase
# ============================================================================

class TestPDCADoPhase:
    """Test DO phase functionality - TDD Cycle 5."""

    def test_do_returns_valid_structure(self):
        """RED: Test do phase returns valid structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)

            assert "cycle_id" in do_result
            assert do_result["cycle_id"] == plan["cycle_id"]
            assert "phase" in do_result
            assert do_result["phase"] == PDCAPhase.DO.value
            assert "execution_log" in do_result
            assert isinstance(do_result["execution_log"], list)

    def test_do_executes_all_improvements_from_plan(self):
        """RED: Test do phase executes all improvements from plan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)

            assert len(do_result["execution_log"]) == len(plan["improvements"])

    def test_do_logs_execution_details(self):
        """RED: Test do phase logs execution details."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)

            for log_entry in do_result["execution_log"]:
                assert "metric" in log_entry
                assert "action" in log_entry
                assert "status" in log_entry
                assert "timestamp" in log_entry


# ============================================================================
# TDD CYCLE 6: CHECK Phase
# ============================================================================

class TestPDCACheckPhase:
    """Test CHECK phase functionality - TDD Cycle 6."""

    def test_check_returns_valid_structure(self):
        """RED: Test check phase returns valid structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)
            check_result = agent.check(plan, do_result)

            assert "cycle_id" in check_result
            assert check_result["cycle_id"] == plan["cycle_id"]
            assert "phase" in check_result
            assert check_result["phase"] == PDCAPhase.CHECK.value
            assert "baseline_metrics" in check_result
            assert "post_metrics" in check_result
            assert "validation_results" in check_result

    def test_check_validates_all_metrics(self):
        """RED: Test check phase validates all metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)
            check_result = agent.check(plan, do_result)

            validation_results = check_result["validation_results"]
            assert len(validation_results) >= 4  # At least 4 DORA metrics

            for vr in validation_results:
                assert "metric" in vr
                assert "baseline" in vr
                assert "post_change" in vr
                assert "improvement_pct" in vr
                assert "passed" in vr

    def test_check_calculates_weighted_score(self):
        """RED: Test check phase calculates weighted score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)
            check_result = agent.check(plan, do_result)

            assert "weighted_score" in check_result
            assert isinstance(check_result["weighted_score"], (int, float))


# ============================================================================
# TDD CYCLE 7: ACT Phase
# ============================================================================

class TestPDCAActPhase:
    """Test ACT phase functionality - TDD Cycle 7."""

    def test_act_returns_valid_structure(self):
        """RED: Test act phase returns valid structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = agent._get_mock_metrics()
            plan = agent.plan(baseline)
            do_result = agent.do(plan)
            check_result = agent.check(plan, do_result)
            act_result = agent.act(check_result)

            assert "cycle_id" in act_result
            assert act_result["cycle_id"] == plan["cycle_id"]
            assert "phase" in act_result
            assert act_result["phase"] == PDCAPhase.ACT.value
            assert "decision" in act_result
            assert "reason" in act_result
            assert "actions_taken" in act_result

    def test_act_decides_apply_for_high_score(self):
        """RED: Test act phase decides APPLY for high weighted score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            # Create check result with high score
            check_result = {
                "cycle_id": "test-cycle",
                "phase": PDCAPhase.CHECK.value,
                "weighted_score": 20.0,  # Above auto_apply_threshold (15%)
                "passed": True
            }

            act_result = agent.act(check_result)
            assert act_result["decision"] == DecisionAction.APPLY.value

    def test_act_decides_revert_for_negative_score(self):
        """RED: Test act phase decides REVERT for negative score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            # Create check result with negative score
            check_result = {
                "cycle_id": "test-cycle",
                "phase": PDCAPhase.CHECK.value,
                "weighted_score": -8.0,  # Below auto_revert_threshold (-5%)
                "passed": False
            }

            act_result = agent.act(check_result)
            assert act_result["decision"] == DecisionAction.REVERT.value

    def test_act_decides_continue_for_marginal_score(self):
        """RED: Test act phase decides CONTINUE for marginal score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            # Create check result with marginal score
            check_result = {
                "cycle_id": "test-cycle",
                "phase": PDCAPhase.CHECK.value,
                "weighted_score": 8.0,  # Between validation_threshold (5%) and auto_apply (15%)
                "passed": True
            }

            act_result = agent.act(check_result)
            assert act_result["decision"] == DecisionAction.CONTINUE.value


# ============================================================================
# TDD CYCLE 8: Full Cycle Integration
# ============================================================================

class TestPDCAFullCycle:
    """Test full PDCA cycle integration - TDD Cycle 8."""

    @patch('builtins.input', return_value='y')
    def test_run_cycle_executes_all_phases(self, mock_input):
        """RED: Test run_cycle executes all 4 phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )
            agent.history_file = Path(tmpdir) / ".pdca_history.json"

            result = agent.run_cycle(auto_execute=True)

            assert "cycle_id" in result
            assert "plan" in result
            assert "do" in result
            assert "check" in result
            assert "act" in result
            assert "completed_at" in result

    @patch('builtins.input', return_value='y')
    def test_run_cycle_saves_to_history(self, mock_input):
        """RED: Test run_cycle saves result to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )
            agent.history_file = Path(tmpdir) / ".pdca_history.json"

            initial_count = len(agent.history)
            agent.run_cycle(auto_execute=True)

            assert len(agent.history) == initial_count + 1
            assert agent.history_file.exists()

    def test_run_cycle_can_be_aborted_at_plan(self):
        """RED: Test run_cycle can be aborted at plan phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            with patch('builtins.input', return_value='n'):
                result = agent.run_cycle(auto_execute=False)
                assert result["status"] == "aborted"
                assert result["phase"] == "plan"


# ============================================================================
# TDD CYCLE: Helper Methods
# ============================================================================

class TestPDCAHelperMethods:
    """Test helper methods."""

    def test_calculate_estimated_impact(self):
        """RED: Test impact calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            improvements = [
                {
                    "metric": "deployment_frequency",
                    "current": 0.5,
                    "target": 0.65
                },
                {
                    "metric": "lead_time_for_changes",
                    "current": 48.0,
                    "target": 33.6
                }
            ]

            impact = agent._calculate_estimated_impact(improvements)

            assert "deployment_frequency" in impact
            assert "lead_time_for_changes" in impact
            assert impact["deployment_frequency"]["current"] == 0.5
            assert impact["deployment_frequency"]["target"] == 0.65
            assert impact["deployment_frequency"]["improvement_pct"] == 30.0

    def test_simulate_post_metrics(self):
        """RED: Test post-metrics simulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pdca_config.json"
            agent = PDCAAutomationAgent(
                repo="owner/repo",
                config_file=str(config_file)
            )

            baseline = {
                'deployment_frequency': 0.5,
                'lead_time_for_changes': 48.0,
                'change_failure_rate': 15.0,
                'mean_time_to_recovery': 2.5,
                'timestamp': datetime.now().isoformat()
            }

            improvements = [
                {
                    "metric": "deployment_frequency",
                    "current": 0.5,
                    "target": 0.65
                }
            ]

            post_metrics = agent._simulate_post_metrics(baseline, improvements)

            assert "deployment_frequency" in post_metrics
            assert post_metrics["deployment_frequency"] != baseline["deployment_frequency"]
            assert "timestamp" in post_metrics
