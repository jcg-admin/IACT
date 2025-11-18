#!/usr/bin/env python3
"""
Tests for TDD Execution Logger module.

Validates:
- Logger initialization
- Phase logging
- Artifact logging with SHA256 hashing
- Test execution logging
- Metrics logging
- Finalization and report generation
- JSON and Markdown report formats

Reference: scripts/ai/agents/tdd_execution_logger.py
"""

from __future__ import annotations

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict

import sys
from pathlib import Path as PathLib

# Add scripts to path for imports
scripts_path = PathLib(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

from scripts.ai.tdd.execution_logger import TDDExecutionLogger


class TestLoggerInitialization:
    """Tests for TDDExecutionLogger initialization."""

    def test_initialize_logger_creates_output_directory(self):
        """Initialize logger creates output directory if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "logs"

            logger = TDDExecutionLogger(
                feature_name="test_feature",
                output_dir=output_dir,
            )

            assert output_dir.exists()
            assert output_dir.is_dir()

    def test_initialize_logger_sets_feature_name(self):
        """Initialize logger stores feature name correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger(
                feature_name="user_authentication",
                output_dir=Path(tmpdir),
            )

            assert logger.feature_name == "user_authentication"
            assert logger.log["feature_name"] == "user_authentication"

    def test_initialize_logger_sets_start_timestamp(self):
        """Initialize logger sets start timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            before = datetime.now()

            logger = TDDExecutionLogger(
                feature_name="test_feature",
                output_dir=Path(tmpdir),
            )

            after = datetime.now()

            start_ts = datetime.fromisoformat(logger.log["start_timestamp"])
            assert before <= start_ts <= after

    def test_initialize_logger_creates_empty_structure(self):
        """Initialize logger creates correct empty log structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger(
                feature_name="test_feature",
                output_dir=Path(tmpdir),
            )

            assert logger.log["end_timestamp"] is None
            assert logger.log["duration_seconds"] is None
            assert logger.log["phases"] == {}
            assert logger.log["artifacts"] == []
            assert logger.log["test_executions"] == []
            assert logger.log["metrics"] == {}
            assert logger.log["constitution_result"] == {}


class TestPhaseLogging:
    """Tests for log_phase method."""

    def test_log_phase_started_creates_phase_entry(self):
        """Log phase with started status creates phase entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_phase(
                "red_phase",
                {
                    "status": "started",
                    "timestamp": "2025-01-15T10:00:00",
                },
            )

            assert "red_phase" in logger.log["phases"]
            phase = logger.log["phases"]["red_phase"]
            assert phase["start_timestamp"] == "2025-01-15T10:00:00"
            assert phase["status"] == "in_progress"
            assert phase["end_timestamp"] is None

    def test_log_phase_completed_updates_phase_entry(self):
        """Log phase with completed status updates existing entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            # Start phase
            logger.log_phase("green_phase", {"status": "started", "timestamp": "2025-01-15T10:00:00"})

            # Complete phase
            logger.log_phase(
                "green_phase",
                {"status": "completed", "timestamp": "2025-01-15T10:05:00"},
            )

            phase = logger.log["phases"]["green_phase"]
            assert phase["end_timestamp"] == "2025-01-15T10:05:00"
            assert phase["status"] == "completed"

    def test_log_phase_calculates_duration(self):
        """Log phase completion calculates duration correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_phase("refactor_phase", {"status": "started", "timestamp": "2025-01-15T10:00:00"})

            logger.log_phase(
                "refactor_phase",
                {"status": "completed", "timestamp": "2025-01-15T10:03:30"},
            )

            phase = logger.log["phases"]["refactor_phase"]
            # Duration should be 3 minutes 30 seconds = 210 seconds
            assert phase["duration_seconds"] == 210.0

    def test_log_phase_with_details_stores_details(self):
        """Log phase with details stores them in phase entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_phase(
                "red_phase",
                {
                    "status": "started",
                    "details": {
                        "test_file": "tests/test_auth.py",
                        "test_count": 5,
                    },
                },
            )

            phase = logger.log["phases"]["red_phase"]
            assert phase["details"]["test_file"] == "tests/test_auth.py"
            assert phase["details"]["test_count"] == 5

    def test_log_phase_failed_status_marks_as_failed(self):
        """Log phase with failed status marks phase as failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_phase("green_phase", {"status": "started"})
            logger.log_phase("green_phase", {"status": "failed"})

            phase = logger.log["phases"]["green_phase"]
            assert phase["status"] == "failed"

    def test_log_multiple_phases_keeps_all(self):
        """Log multiple phases stores all of them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_phase("red_phase", {"status": "started"})
            logger.log_phase("green_phase", {"status": "started"})
            logger.log_phase("refactor_phase", {"status": "started"})

            assert "red_phase" in logger.log["phases"]
            assert "green_phase" in logger.log["phases"]
            assert "refactor_phase" in logger.log["phases"]


class TestArtifactLogging:
    """Tests for log_artifact method."""

    def test_log_artifact_calculates_sha256_hash(self):
        """Log artifact calculates SHA256 hash correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            # Create test file
            test_file = Path(tmpdir) / "test_artifact.py"
            test_file.write_text("def test_function():\n    pass\n")

            logger.log_artifact(test_file, "unit_test")

            artifacts = logger.log["artifacts"]
            assert len(artifacts) == 1
            assert artifacts[0]["sha256_hash"] is not None
            assert len(artifacts[0]["sha256_hash"]) == 64  # SHA256 is 64 hex chars

    def test_log_artifact_stores_file_path(self):
        """Log artifact stores file path correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            test_file = Path(tmpdir) / "feature.py"
            test_file.write_text("# implementation")

            logger.log_artifact(test_file, "service")

            artifacts = logger.log["artifacts"]
            assert artifacts[0]["file_path"] == str(test_file)

    def test_log_artifact_stores_artifact_type(self):
        """Log artifact stores artifact type correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            test_file = Path(tmpdir) / "model.py"
            test_file.write_text("class User: pass")

            logger.log_artifact(test_file, "model")

            artifacts = logger.log["artifacts"]
            assert artifacts[0]["artifact_type"] == "model"

    def test_log_artifact_stores_timestamp(self):
        """Log artifact stores timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("pass")

            before = datetime.now()
            logger.log_artifact(test_file, "unit_test")
            after = datetime.now()

            artifacts = logger.log["artifacts"]
            artifact_ts = datetime.fromisoformat(artifacts[0]["timestamp"])
            assert before <= artifact_ts <= after

    def test_log_artifact_stores_file_size(self):
        """Log artifact stores file size in bytes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            test_file = Path(tmpdir) / "test.py"
            content = "def test():\n    assert True\n"
            test_file.write_text(content)

            logger.log_artifact(test_file, "unit_test")

            artifacts = logger.log["artifacts"]
            assert artifacts[0]["size_bytes"] == len(content.encode('utf-8'))

    def test_log_multiple_artifacts_keeps_all(self):
        """Log multiple artifacts stores all of them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            # Create multiple files
            for i in range(3):
                test_file = Path(tmpdir) / f"file_{i}.py"
                test_file.write_text(f"# file {i}")
                logger.log_artifact(test_file, f"type_{i}")

            artifacts = logger.log["artifacts"]
            assert len(artifacts) == 3

    def test_log_artifact_hash_changes_with_content(self):
        """Log artifact produces different hashes for different content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            file1 = Path(tmpdir) / "file1.py"
            file1.write_text("content A")
            logger.log_artifact(file1, "test")

            file2 = Path(tmpdir) / "file2.py"
            file2.write_text("content B")
            logger.log_artifact(file2, "test")

            artifacts = logger.log["artifacts"]
            assert artifacts[0]["sha256_hash"] != artifacts[1]["sha256_hash"]


class TestTestExecutionLogging:
    """Tests for log_test_execution method."""

    def test_log_test_execution_stores_phase(self):
        """Log test execution stores phase correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_test_execution(
                "red_phase",
                {"total": 5, "passed": 0, "failed": 5},
            )

            executions = logger.log["test_executions"]
            assert len(executions) == 1
            assert executions[0]["phase"] == "red_phase"

    def test_log_test_execution_stores_result(self):
        """Log test execution stores test results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            test_result = {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "skipped": 0,
                "duration_seconds": 1.5,
            }

            logger.log_test_execution("green_phase", test_result)

            executions = logger.log["test_executions"]
            assert executions[0]["result"]["total"] == 10
            assert executions[0]["result"]["passed"] == 8
            assert executions[0]["result"]["failed"] == 2
            assert executions[0]["result"]["duration_seconds"] == 1.5

    def test_log_test_execution_stores_timestamp(self):
        """Log test execution stores timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            before = datetime.now()
            logger.log_test_execution("refactor_phase", {"total": 5, "passed": 5})
            after = datetime.now()

            executions = logger.log["test_executions"]
            exec_ts = datetime.fromisoformat(executions[0]["timestamp"])
            assert before <= exec_ts <= after

    def test_log_multiple_test_executions_keeps_all(self):
        """Log multiple test executions stores all of them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_test_execution("red_phase", {"total": 5, "failed": 5})
            logger.log_test_execution("green_phase", {"total": 5, "passed": 5})
            logger.log_test_execution("refactor_phase", {"total": 5, "passed": 5})

            executions = logger.log["test_executions"]
            assert len(executions) == 3


class TestMetricsLogging:
    """Tests for log_metrics method."""

    def test_log_metrics_stores_coverage_data(self):
        """Log metrics stores coverage data correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            metrics = {
                "coverage": {
                    "percent": 95.5,
                    "total_lines": 100,
                    "covered_lines": 95,
                }
            }

            logger.log_metrics(metrics)

            assert logger.log["metrics"]["coverage"]["percent"] == 95.5
            assert logger.log["metrics"]["coverage"]["total_lines"] == 100

    def test_log_metrics_stores_quality_data(self):
        """Log metrics stores quality data correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            metrics = {
                "quality": {
                    "linting_passed": True,
                    "issues_count": 0,
                }
            }

            logger.log_metrics(metrics)

            assert logger.log["metrics"]["quality"]["linting_passed"] is True
            assert logger.log["metrics"]["quality"]["issues_count"] == 0

    def test_log_metrics_stores_security_data(self):
        """Log metrics stores security data correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            metrics = {
                "security": {
                    "issues_count": 0,
                    "issues": [],
                }
            }

            logger.log_metrics(metrics)

            assert logger.log["metrics"]["security"]["issues_count"] == 0
            assert logger.log["metrics"]["security"]["issues"] == []

    def test_log_metrics_updates_existing_metrics(self):
        """Log metrics updates rather than replaces existing metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            logger.log_metrics({"coverage": {"percent": 90.0}})
            logger.log_metrics({"quality": {"linting_passed": True}})

            # Both should be present
            assert "coverage" in logger.log["metrics"]
            assert "quality" in logger.log["metrics"]


class TestFinalization:
    """Tests for finalize method and report generation."""

    def test_finalize_sets_end_timestamp(self):
        """Finalize sets end timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            before = datetime.now()
            logger.finalize({"compliant": True, "score": 100.0})
            after = datetime.now()

            end_ts = datetime.fromisoformat(logger.log["end_timestamp"])
            assert before <= end_ts <= after

    def test_finalize_calculates_total_duration(self):
        """Finalize calculates total execution duration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            # Manually set start timestamp to known value
            logger.log["start_timestamp"] = "2025-01-15T10:00:00"

            # Manually set end timestamp via finalize
            import unittest.mock as mock
            with mock.patch('scripts.ai.tdd.execution_logger.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2025, 1, 15, 10, 5, 30)
                mock_datetime.fromisoformat = datetime.fromisoformat

                logger.finalize({"compliant": True})

                # Duration should be 5 minutes 30 seconds = 330 seconds
                assert logger.log["duration_seconds"] == 330.0

    def test_finalize_stores_constitution_result(self):
        """Finalize stores constitution validation result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            constitution_result = {
                "compliant": True,
                "score": 100.0,
                "violations": [],
            }

            logger.finalize(constitution_result)

            assert logger.log["constitution_result"]["compliant"] is True
            assert logger.log["constitution_result"]["score"] == 100.0

    def test_finalize_generates_json_report(self):
        """Finalize generates JSON report file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test_feature", Path(tmpdir))

            json_path = logger.finalize({"compliant": True})

            assert json_path.exists()
            assert json_path.suffix == ".json"
            assert "test_feature" in json_path.name
            assert "tdd_execution" in json_path.name

    def test_finalize_json_report_is_valid_json(self):
        """Finalize generates valid JSON that can be parsed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            # Add some data
            logger.log_phase("red_phase", {"status": "started"})
            logger.log_metrics({"coverage": {"percent": 95.0}})

            json_path = logger.finalize({"compliant": True})

            # Should be able to load as JSON
            with open(json_path, "r") as f:
                data = json.load(f)

            assert data["feature_name"] == "test"
            assert "red_phase" in data["phases"]
            assert data["metrics"]["coverage"]["percent"] == 95.0

    def test_finalize_generates_markdown_report(self):
        """Finalize generates Markdown report file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test_feature", Path(tmpdir))

            logger.finalize({"compliant": True})

            # Find markdown file
            markdown_files = list(Path(tmpdir).glob("*.md"))
            assert len(markdown_files) == 1
            assert "test_feature" in markdown_files[0].name
            assert "tdd_execution" in markdown_files[0].name

    def test_finalize_markdown_report_has_content(self):
        """Finalize generates Markdown with actual content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test_feature", Path(tmpdir))

            # Add some data
            logger.log_phase("red_phase", {"status": "started"})
            logger.log_phase("red_phase", {"status": "completed"})

            logger.finalize({"compliant": True, "score": 100.0})

            # Read markdown
            markdown_files = list(Path(tmpdir).glob("*.md"))
            content = markdown_files[0].read_text()

            # Should contain key sections
            assert "TDD Execution Report" in content or "test_feature" in content
            # Markdown should have some structure
            assert len(content) > 100

    def test_finalize_returns_json_path(self):
        """Finalize returns path to JSON report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            result = logger.finalize({"compliant": True})

            assert isinstance(result, Path)
            assert result.exists()
            assert result.suffix == ".json"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_log_artifact_for_nonexistent_file_handles_gracefully(self):
        """Log artifact for missing file handles gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            nonexistent = Path(tmpdir) / "nonexistent.py"

            # Should handle gracefully, not crash
            # Note: Implementation might vary - this tests robustness
            try:
                logger.log_artifact(nonexistent, "test")
                # If it doesn't raise, check it logged something
                artifacts = logger.log["artifacts"]
                if len(artifacts) > 0:
                    assert artifacts[0]["size_bytes"] == 0
            except FileNotFoundError:
                # Also acceptable to raise FileNotFoundError
                pass

    def test_finalize_with_empty_log_succeeds(self):
        """Finalize with minimal data succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("minimal", Path(tmpdir))

            # Finalize immediately without logging anything
            json_path = logger.finalize({"compliant": False})

            assert json_path.exists()

            # Should be valid JSON
            with open(json_path, "r") as f:
                data = json.load(f)

            assert data["feature_name"] == "minimal"

    def test_multiple_finalize_calls_generate_different_files(self):
        """Multiple finalize calls generate different timestamped files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("test", Path(tmpdir))

            path1 = logger.finalize({"compliant": True})

            # Small delay to ensure different timestamp
            import time
            time.sleep(1.1)

            # Create new logger
            logger2 = TDDExecutionLogger("test", Path(tmpdir))
            path2 = logger2.finalize({"compliant": True})

            # Should be different files
            assert path1 != path2
            assert path1.exists()
            assert path2.exists()


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_complete_tdd_workflow_logging(self):
        """Complete TDD workflow logging end-to-end."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TDDExecutionLogger("user_authentication", Path(tmpdir))

            # RED Phase
            logger.log_phase(
                "red_phase",
                {
                    "status": "started",
                    "timestamp": "2025-01-15T10:00:00",
                    "details": {"test_file": "tests/test_auth.py"},
                },
            )

            test_file = Path(tmpdir) / "test_auth.py"
            test_file.write_text("def test_login(): assert False")
            logger.log_artifact(test_file, "unit_test")

            logger.log_test_execution(
                "red_phase",
                {"total": 5, "passed": 0, "failed": 5, "duration_seconds": 0.5},
            )

            logger.log_phase(
                "red_phase",
                {"status": "completed", "timestamp": "2025-01-15T10:05:00"},
            )

            # GREEN Phase
            logger.log_phase("green_phase", {"status": "started", "timestamp": "2025-01-15T10:06:00"})

            impl_file = Path(tmpdir) / "auth.py"
            impl_file.write_text("def login(user, pwd): return True")
            logger.log_artifact(impl_file, "service")

            logger.log_test_execution(
                "green_phase",
                {"total": 5, "passed": 5, "failed": 0, "duration_seconds": 0.6},
            )

            logger.log_phase(
                "green_phase",
                {"status": "completed", "timestamp": "2025-01-15T10:15:00"},
            )

            # REFACTOR Phase
            logger.log_phase(
                "refactor_phase",
                {"status": "started", "timestamp": "2025-01-15T10:16:00"},
            )

            logger.log_test_execution(
                "refactor_phase",
                {"total": 5, "passed": 5, "failed": 0, "duration_seconds": 0.5},
            )

            logger.log_phase(
                "refactor_phase",
                {"status": "completed", "timestamp": "2025-01-15T10:20:00"},
            )

            # Metrics
            logger.log_metrics(
                {
                    "coverage": {"percent": 95.5},
                    "quality": {"linting_passed": True},
                    "security": {"issues_count": 0},
                }
            )

            # Finalize
            constitution_result = {
                "compliant": True,
                "score": 100.0,
                "violations": [],
            }

            json_path = logger.finalize(constitution_result)

            # Verify complete log
            with open(json_path, "r") as f:
                log = json.load(f)

            assert log["feature_name"] == "user_authentication"
            assert len(log["phases"]) == 3
            assert len(log["artifacts"]) == 2
            assert len(log["test_executions"]) == 3
            assert log["metrics"]["coverage"]["percent"] == 95.5
            assert log["constitution_result"]["compliant"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
