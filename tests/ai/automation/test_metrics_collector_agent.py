"""
Tests for MetricsCollectorAgent - TDD approach

Tests metrics collection, tracking, trend analysis, and reporting.

Author: SDLC Agent
Date: 2025-11-13
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import will fail until we implement the agent (TDD RED phase)
try:
    from scripts.coding.ai.automation.metrics_collector_agent import (
        MetricsCollectorAgent,
        ViolationMetrics,
        CIMetrics,
        CoverageMetrics,
        TrendDirection
    )
except ImportError:
    pytest.skip("MetricsCollectorAgent not yet implemented", allow_module_level=True)


class TestMetricsCollectorAgentInit:
    """Test agent initialization and configuration."""

    def test_agent_initialization_default(self):
        """Test agent initializes with default configuration."""
        agent = MetricsCollectorAgent()

        assert agent.name == "MetricsCollectorAgent"
        assert agent.log_file is None
        assert agent.metrics_type == "all"
        assert agent.period_days == 30
        assert agent.output_format == "json"

    def test_agent_initialization_custom_config(self):
        """Test agent initializes with custom configuration."""
        config = {
            "log_file": "/tmp/test.log",
            "metrics_type": "violations",
            "period_days": 7,
            "output_format": "markdown"
        }
        agent = MetricsCollectorAgent(config=config)

        assert agent.log_file == Path("/tmp/test.log")
        assert agent.metrics_type == "violations"
        assert agent.period_days == 7
        assert agent.output_format == "markdown"


class TestViolationsLogParsing:
    """Test parsing of constitution violations log."""

    @pytest.fixture
    def sample_violations_log(self, tmp_path):
        """Create a sample violations log file."""
        log_file = tmp_path / "constitucion_violations.log"
        log_content = """[2025-11-10 14:23:45] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: docs/test.md - Line: 42 - Message: Emoji detected in markdown
[2025-11-10 15:30:12] VIOLATION - Rule: R1_protected_branches - Severity: error - File: .git/config - Line: 0 - Message: Direct push to main branch
[2025-11-11 09:15:33] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: warning - File: README.md - Line: 10 - Message: Emoji in documentation
[2025-11-11 10:45:00] VIOLATION - Rule: R3_ui_api_coherence - Severity: error - File: frontend/src/services/api.ts - Line: 55 - Message: API endpoint changed without UI update
[2025-11-12 11:20:15] VIOLATION - Rule: R4_database_routing - Severity: error - File: api/settings.py - Line: 120 - Message: Missing database router
[2025-11-13 08:00:00] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: src/components/Button.tsx - Line: 8 - Message: Emoji in code
"""
        log_file.write_text(log_content)
        return log_file

    def test_parse_violations_log(self, sample_violations_log):
        """Test parsing violations log file."""
        agent = MetricsCollectorAgent(config={"log_file": str(sample_violations_log)})
        violations = agent.parse_violations_log()

        assert len(violations) == 6
        assert all(isinstance(v, dict) for v in violations)
        assert all("rule" in v for v in violations)
        assert all("severity" in v for v in violations)
        assert all("timestamp" in v for v in violations)

    def test_parse_violations_log_empty_file(self, tmp_path):
        """Test parsing empty violations log."""
        empty_log = tmp_path / "empty.log"
        empty_log.write_text("")

        agent = MetricsCollectorAgent(config={"log_file": str(empty_log)})
        violations = agent.parse_violations_log()

        assert violations == []

    def test_parse_violations_log_malformed_entries(self, tmp_path):
        """Test parsing log with malformed entries."""
        log_file = tmp_path / "malformed.log"
        log_content = """[2025-11-10 14:23:45] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: docs/test.md - Line: 42 - Message: Valid entry
MALFORMED LINE WITHOUT TIMESTAMP
[INVALID] This is not a proper violation entry
[2025-11-11 10:00:00] VIOLATION - Rule: R1_protected_branches - Severity: error - File: .git/config - Line: 0 - Message: Another valid entry
"""
        log_file.write_text(log_content)

        agent = MetricsCollectorAgent(config={"log_file": str(log_file)})
        violations = agent.parse_violations_log()

        # Should only parse valid entries
        assert len(violations) == 2
        assert violations[0]["rule"] == "R2_no_emojis_anywhere"
        assert violations[1]["rule"] == "R1_protected_branches"


class TestViolationMetrics:
    """Test violation tracking and metrics."""

    @pytest.fixture
    def sample_violations_log(self, tmp_path):
        """Create sample violations log."""
        log_file = tmp_path / "violations.log"
        log_content = """[2025-11-10 14:23:45] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: docs/test.md - Line: 42 - Message: Emoji detected
[2025-11-10 15:30:12] VIOLATION - Rule: R1_protected_branches - Severity: error - File: .git/config - Line: 0 - Message: Push to main
[2025-11-11 09:15:33] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: warning - File: README.md - Line: 10 - Message: Emoji found
[2025-11-11 10:45:00] VIOLATION - Rule: R3_ui_api_coherence - Severity: error - File: frontend/api.ts - Line: 55 - Message: API mismatch
[2025-11-12 11:20:15] VIOLATION - Rule: R4_database_routing - Severity: error - File: settings.py - Line: 120 - Message: Router missing
[2025-11-13 08:00:00] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: Button.tsx - Line: 8 - Message: Emoji in code
"""
        log_file.write_text(log_content)
        return log_file

    def test_count_violations_by_rule(self, sample_violations_log):
        """Test counting violations grouped by rule."""
        agent = MetricsCollectorAgent(config={"log_file": str(sample_violations_log)})
        violations = agent.parse_violations_log()
        counts = agent.count_by_rule(violations)

        assert counts["R2_no_emojis_anywhere"] == 3
        assert counts["R1_protected_branches"] == 1
        assert counts["R3_ui_api_coherence"] == 1
        assert counts["R4_database_routing"] == 1
        assert counts.get("R5_tests_required", 0) == 0
        assert counts.get("R6_devcontainer_valid", 0) == 0

    def test_count_violations_by_severity(self, sample_violations_log):
        """Test counting violations by severity."""
        agent = MetricsCollectorAgent(config={"log_file": str(sample_violations_log)})
        violations = agent.parse_violations_log()
        counts = agent.count_by_severity(violations)

        assert counts["error"] == 5
        assert counts["warning"] == 1

    def test_count_violations_by_file(self, sample_violations_log):
        """Test counting violations by file."""
        agent = MetricsCollectorAgent(config={"log_file": str(sample_violations_log)})
        violations = agent.parse_violations_log()
        counts = agent.count_by_file(violations)

        assert "docs/test.md" in counts
        assert "README.md" in counts
        assert counts["docs/test.md"] == 1
        assert counts["README.md"] == 1


class TestTrendAnalysis:
    """Test trend analysis functionality."""

    @pytest.fixture
    def historical_violations_log(self, tmp_path):
        """Create violations log with 60 days of data."""
        log_file = tmp_path / "historical.log"
        violations = []

        # Generate violations over 60 days
        base_date = datetime.now() - timedelta(days=60)

        # Week 1-2: High violations (10 per day)
        for day in range(14):
            date = base_date + timedelta(days=day)
            for i in range(10):
                timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
                violations.append(
                    f"[{timestamp}] VIOLATION - Rule: R2_no_emojis_anywhere - "
                    f"Severity: error - File: test{i}.md - Line: 1 - Message: Violation"
                )

        # Week 3-4: Medium violations (5 per day) - improving trend
        for day in range(14, 28):
            date = base_date + timedelta(days=day)
            for i in range(5):
                timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
                violations.append(
                    f"[{timestamp}] VIOLATION - Rule: R2_no_emojis_anywhere - "
                    f"Severity: error - File: test{i}.md - Line: 1 - Message: Violation"
                )

        # Week 5-8: Low violations (2 per day) - continued improvement
        for day in range(28, 60):
            date = base_date + timedelta(days=day)
            for i in range(2):
                timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
                violations.append(
                    f"[{timestamp}] VIOLATION - Rule: R2_no_emojis_anywhere - "
                    f"Severity: error - File: test{i}.md - Line: 1 - Message: Violation"
                )

        log_file.write_text("\n".join(violations))
        return log_file

    def test_trend_analysis_decreasing(self, historical_violations_log):
        """Test trend analysis detects decreasing violations."""
        agent = MetricsCollectorAgent(config={
            "log_file": str(historical_violations_log),
            "period_days": 60
        })

        violations = agent.parse_violations_log()
        trend = agent.analyze_trend(violations)

        assert trend["direction"] == "decreasing"  # Check string value
        assert trend["change_percentage"] < 0  # Negative indicates decrease
        assert "improvement" in trend["description"].lower()

    def test_trend_analysis_with_period_filter(self, historical_violations_log):
        """Test trend analysis with specific time period."""
        agent = MetricsCollectorAgent(config={
            "log_file": str(historical_violations_log),
            "period_days": 30  # Last 30 days only
        })

        violations = agent.parse_violations_log()
        filtered_violations = agent.filter_by_period(violations, days=30)
        trend = agent.analyze_trend(filtered_violations)

        assert trend is not None
        assert "direction" in trend
        assert "change_percentage" in trend


class TestCIMetrics:
    """Test CI pipeline metrics collection."""

    @pytest.fixture
    def ci_metrics_history(self, tmp_path):
        """Create CI metrics history file."""
        history_file = tmp_path / "ci_metrics_history.json"
        history_data = {
            "pipeline_runs": [
                {
                    "timestamp": "2025-11-10T10:00:00",
                    "duration_seconds": 120,
                    "status": "success",
                    "jobs_passed": 10,
                    "jobs_failed": 0
                },
                {
                    "timestamp": "2025-11-10T14:30:00",
                    "duration_seconds": 135,
                    "status": "success",
                    "jobs_passed": 10,
                    "jobs_failed": 0
                },
                {
                    "timestamp": "2025-11-11T09:15:00",
                    "duration_seconds": 150,
                    "status": "failed",
                    "jobs_passed": 8,
                    "jobs_failed": 2
                },
                {
                    "timestamp": "2025-11-11T15:45:00",
                    "duration_seconds": 125,
                    "status": "success",
                    "jobs_passed": 10,
                    "jobs_failed": 0
                },
                {
                    "timestamp": "2025-11-12T11:20:00",
                    "duration_seconds": 118,
                    "status": "success",
                    "jobs_passed": 10,
                    "jobs_failed": 0
                }
            ]
        }
        history_file.write_text(json.dumps(history_data, indent=2))
        return history_file

    def test_ci_metrics_aggregation(self, ci_metrics_history):
        """Test aggregation of CI pipeline metrics."""
        agent = MetricsCollectorAgent()
        metrics = agent.aggregate_ci_metrics(ci_metrics_history)

        assert metrics["total_runs"] == 5
        assert metrics["success_rate"] == 80.0  # 4/5 = 80%
        assert metrics["average_duration"] == 129.6  # (120+135+150+125+118)/5
        assert metrics["fastest_run"] == 118
        assert metrics["slowest_run"] == 150

    def test_ci_metrics_success_rate_calculation(self, ci_metrics_history):
        """Test CI success rate calculation."""
        agent = MetricsCollectorAgent()
        metrics = agent.aggregate_ci_metrics(ci_metrics_history)

        # 4 successful runs out of 5 total
        expected_success_rate = (4 / 5) * 100
        assert metrics["success_rate"] == expected_success_rate


class TestCoverageMetrics:
    """Test code coverage metrics tracking."""

    @pytest.fixture
    def coverage_history(self, tmp_path):
        """Create coverage history file."""
        history_file = tmp_path / "coverage_history.json"
        history_data = {
            "coverage_snapshots": [
                {
                    "timestamp": "2025-11-01T10:00:00",
                    "overall_coverage": 75.5,
                    "backend_coverage": 80.0,
                    "frontend_coverage": 70.0
                },
                {
                    "timestamp": "2025-11-05T10:00:00",
                    "overall_coverage": 78.2,
                    "backend_coverage": 82.0,
                    "frontend_coverage": 73.0
                },
                {
                    "timestamp": "2025-11-10T10:00:00",
                    "overall_coverage": 81.0,
                    "backend_coverage": 85.0,
                    "frontend_coverage": 76.0
                },
                {
                    "timestamp": "2025-11-13T10:00:00",
                    "overall_coverage": 83.5,
                    "backend_coverage": 87.0,
                    "frontend_coverage": 79.0
                }
            ]
        }
        history_file.write_text(json.dumps(history_data, indent=2))
        return history_file

    def test_coverage_history_tracking(self, coverage_history):
        """Test tracking coverage over time."""
        agent = MetricsCollectorAgent()
        coverage_data = agent.load_coverage_history(coverage_history)

        assert len(coverage_data["coverage_snapshots"]) == 4
        assert coverage_data["coverage_snapshots"][0]["overall_coverage"] == 75.5
        assert coverage_data["coverage_snapshots"][-1]["overall_coverage"] == 83.5

    def test_coverage_trend_analysis(self, coverage_history):
        """Test coverage trend analysis."""
        agent = MetricsCollectorAgent()
        coverage_data = agent.load_coverage_history(coverage_history)
        trend = agent.analyze_coverage_trend(coverage_data)

        assert trend["direction"] == "increasing"  # Check string value
        assert trend["change_percentage"] > 0  # Coverage improving
        assert trend["start_coverage"] == 75.5
        assert trend["end_coverage"] == 83.5


class TestDeveloperComplianceMetrics:
    """Test developer compliance metrics."""

    @pytest.fixture
    def violations_by_author_log(self, tmp_path):
        """Create violations log with author information."""
        log_file = tmp_path / "violations_by_author.log"
        log_content = """[2025-11-10 14:23:45] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: docs/test.md - Line: 42 - Author: developer1 - Message: Emoji detected
[2025-11-10 15:30:12] VIOLATION - Rule: R1_protected_branches - Severity: error - File: .git/config - Line: 0 - Author: developer2 - Message: Push to main
[2025-11-11 09:15:33] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: warning - File: README.md - Line: 10 - Author: developer1 - Message: Emoji found
[2025-11-11 10:45:00] VIOLATION - Rule: R3_ui_api_coherence - Severity: error - File: frontend/api.ts - Line: 55 - Author: developer3 - Message: API mismatch
[2025-11-12 11:20:15] VIOLATION - Rule: R2_no_emojis_anywhere - Severity: error - File: Button.tsx - Line: 8 - Author: developer1 - Message: Emoji in code
"""
        log_file.write_text(log_content)
        return log_file

    def test_developer_compliance_metrics(self, violations_by_author_log):
        """Test tracking compliance by developer."""
        agent = MetricsCollectorAgent(config={"log_file": str(violations_by_author_log)})
        violations = agent.parse_violations_log()
        compliance = agent.calculate_developer_compliance(violations)

        assert "developer1" in compliance
        assert "developer2" in compliance
        assert "developer3" in compliance
        assert compliance["developer1"]["total_violations"] == 3
        assert compliance["developer2"]["total_violations"] == 1
        assert compliance["developer3"]["total_violations"] == 1


class TestReportGeneration:
    """Test JSON and markdown report generation."""

    @pytest.fixture
    def complete_metrics_data(self):
        """Create complete metrics data for reporting."""
        return {
            "violations": {
                "by_rule": {
                    "R2_no_emojis_anywhere": 10,
                    "R1_protected_branches": 2,
                    "R3_ui_api_coherence": 3
                },
                "by_severity": {
                    "error": 12,
                    "warning": 3
                },
                "total": 15,
                "trend": {
                    "direction": "decreasing",
                    "change_percentage": -25.5
                }
            },
            "ci_metrics": {
                "total_runs": 50,
                "success_rate": 85.0,
                "average_duration": 135.5
            },
            "coverage": {
                "overall_coverage": 83.5,
                "trend": {
                    "direction": "increasing",
                    "change_percentage": 8.2
                }
            }
        }

    def test_json_report_generation(self, complete_metrics_data, tmp_path):
        """Test JSON report generation."""
        agent = MetricsCollectorAgent()
        output_file = tmp_path / "metrics_report.json"

        agent.generate_json_report(complete_metrics_data, output_file)

        assert output_file.exists()

        with open(output_file) as f:
            report = json.load(f)

        assert "violations" in report
        assert "ci_metrics" in report
        assert "coverage" in report
        assert report["violations"]["total"] == 15
        assert report["ci_metrics"]["success_rate"] == 85.0

    def test_markdown_summary_generation(self, complete_metrics_data, tmp_path):
        """Test markdown summary generation."""
        agent = MetricsCollectorAgent()
        output_file = tmp_path / "metrics_summary.md"

        agent.generate_markdown_summary(complete_metrics_data, output_file)

        assert output_file.exists()

        content = output_file.read_text()

        assert "# Metrics Report" in content
        assert "## Violations" in content
        assert "## CI Metrics" in content
        assert "## Coverage" in content
        assert "85.0%" in content  # Success rate
        assert "83.5%" in content  # Coverage


class TestCLIArguments:
    """Test CLI argument parsing."""

    def test_cli_log_file_argument(self):
        """Test --log-file CLI argument."""
        agent = MetricsCollectorAgent.from_cli_args([
            "--log-file", "/tmp/violations.log"
        ])

        assert agent.log_file == Path("/tmp/violations.log")

    def test_cli_metrics_type_argument(self):
        """Test --metrics-type CLI argument."""
        agent = MetricsCollectorAgent.from_cli_args([
            "--metrics-type", "violations"
        ])

        assert agent.metrics_type == "violations"

    def test_cli_period_argument(self):
        """Test --period CLI argument."""
        agent = MetricsCollectorAgent.from_cli_args([
            "--period", "7"
        ])

        assert agent.period_days == 7

    def test_cli_output_argument(self):
        """Test --output CLI argument."""
        agent = MetricsCollectorAgent.from_cli_args([
            "--output", "/tmp/report.json"
        ])

        assert agent.output_file == Path("/tmp/report.json")

    def test_cli_all_arguments_combined(self):
        """Test all CLI arguments together."""
        agent = MetricsCollectorAgent.from_cli_args([
            "--log-file", "/tmp/violations.log",
            "--metrics-type", "ci",
            "--period", "14",
            "--output", "/tmp/metrics.json"
        ])

        assert agent.log_file == Path("/tmp/violations.log")
        assert agent.metrics_type == "ci"
        assert agent.period_days == 14
        assert agent.output_file == Path("/tmp/metrics.json")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nonexistent_log_file(self):
        """Test handling of nonexistent log file."""
        agent = MetricsCollectorAgent(config={"log_file": "/nonexistent/file.log"})

        with pytest.raises(FileNotFoundError):
            agent.parse_violations_log()

    def test_invalid_json_metrics_file(self, tmp_path):
        """Test handling of invalid JSON metrics file."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json content")

        agent = MetricsCollectorAgent()

        with pytest.raises(json.JSONDecodeError):
            agent.load_coverage_history(invalid_json)

    def test_empty_metrics_data(self):
        """Test report generation with empty metrics."""
        agent = MetricsCollectorAgent()
        empty_data = {
            "violations": {"total": 0},
            "ci_metrics": {},
            "coverage": {}
        }

        # Should not raise exception
        report = agent.generate_json_report(empty_data, None)
        assert report is not None
