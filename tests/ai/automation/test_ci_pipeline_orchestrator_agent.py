#!/usr/bin/env python3
"""
TDD Tests for CIPipelineOrchestratorAgent

Comprehensive test suite for CI Pipeline Orchestrator Agent following TDD approach.
Tests cover all critical functionality:
- Configuration parsing (.ci-local.yaml)
- Smart detection (git diff analysis)
- Parallel job execution (asyncio)
- Stage dependency resolution
- Timeout handling
- Fail-fast behavior
- Result aggregation
- Dry-run mode
- JSON report generation
- CLI interface

Author: Claude Code Agent
Date: 2025-11-13
Related: AGENTS_ARCHITECTURE.md, ADR-045
"""

import asyncio
import json
import os
import pytest
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from typing import Dict, List

# Import will fail initially (TDD RED) - that's expected
try:
    from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import (
        CIPipelineOrchestratorAgent,
        PipelineConfig,
        Stage,
        Job,
        JobResult,
        StageResult,
        PipelineResult,
        SmartDetector,
        JobExecutor,
        DependencyResolver,
        ResultAggregator
    )
except ImportError:
    # Expected to fail initially in TDD RED phase
    pass


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_ci_config():
    """Sample .ci-local.yaml configuration."""
    return {
        "version": "1.0",
        "pipeline": {
            "name": "IACT Local CI",
            "fail_fast": True,
            "parallel": True,
            "timeout": 600
        },
        "smart_detection": {
            "enabled": True,
            "strategy": "git_diff",
            "base_branch": "main"
        },
        "stages": [
            {
                "name": "lint",
                "description": "Linting stage",
                "parallel": True,
                "depends_on": [],
                "jobs": [
                    {
                        "name": "lint_ui",
                        "description": "ESLint UI",
                        "working_dir": "ui/",
                        "command": "npm run lint",
                        "timeout": 60,
                        "continue_on_error": False,
                        "condition": {
                            "type": "files_changed",
                            "pattern": "ui/**/*.{js,jsx,ts,tsx}"
                        }
                    },
                    {
                        "name": "lint_api",
                        "description": "Ruff API",
                        "working_dir": "api/",
                        "command": "ruff check .",
                        "timeout": 60,
                        "continue_on_error": False,
                        "condition": {
                            "type": "files_changed",
                            "pattern": "api/**/*.py"
                        }
                    }
                ]
            },
            {
                "name": "test",
                "description": "Testing stage",
                "parallel": True,
                "depends_on": ["lint"],
                "jobs": [
                    {
                        "name": "test_ui",
                        "description": "Jest tests",
                        "working_dir": "ui/",
                        "command": "npm run test:coverage",
                        "timeout": 120,
                        "continue_on_error": False,
                        "condition": {
                            "type": "files_changed",
                            "pattern": "ui/**/*.{js,jsx,ts,tsx}"
                        }
                    }
                ]
            }
        ],
        "reporting": {
            "format": "json",
            "verbosity": "normal",
            "save_artifacts": True,
            "artifacts_dir": ".ci-artifacts"
        }
    }


@pytest.fixture
def sample_git_diff():
    """Sample git diff output."""
    return """
diff --git a/ui/src/components/Dashboard.jsx b/ui/src/components/Dashboard.jsx
index 1234567..89abcde 100644
--- a/ui/src/components/Dashboard.jsx
+++ b/ui/src/components/Dashboard.jsx
@@ -10,6 +10,7 @@ export const Dashboard = () => {
+  const [data, setData] = useState([]);
diff --git a/api/views.py b/api/views.py
index abcd123..xyz789 100644
--- a/api/views.py
+++ b/api/views.py
@@ -5,3 +5,5 @@ class DashboardView(APIView):
+    def get(self, request):
+        return Response({"status": "ok"})
"""


@pytest.fixture
def temp_ci_config_file(sample_ci_config):
    """Temporary .ci-local.yaml file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_ci_config, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def mock_git_context():
    """Mock git context."""
    return {
        "branch": "feature/test-branch",
        "base_branch": "main",
        "changed_files": [
            "ui/src/components/Dashboard.jsx",
            "api/views.py",
            "docs/README.md"
        ],
        "diff": "mock diff content"
    }


# ============================================================================
# 1. CONFIGURATION PARSING TESTS
# ============================================================================

class TestConfigurationParsing:
    """Test .ci-local.yaml configuration parsing."""

    def test_parse_valid_yaml_config(self, temp_ci_config_file):
        """Should parse valid YAML configuration."""
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        config = agent.parse_config()

        assert config is not None
        assert config.version == "1.0"
        assert config.pipeline_name == "IACT Local CI"
        assert config.fail_fast is True
        assert config.parallel is True
        assert len(config.stages) == 2

    def test_parse_invalid_yaml_syntax(self):
        """Should handle invalid YAML syntax gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: syntax: [")
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            with pytest.raises(yaml.YAMLError):
                agent.parse_config()
        finally:
            os.unlink(temp_path)

    def test_parse_missing_required_fields(self):
        """Should validate required configuration fields."""
        invalid_config = {"version": "1.0"}  # Missing pipeline, stages

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            with pytest.raises(ValueError, match="Missing required field"):
                agent.parse_config()
        finally:
            os.unlink(temp_path)

    def test_parse_stage_dependencies(self, temp_ci_config_file):
        """Should parse stage dependencies correctly."""
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        config = agent.parse_config()

        test_stage = [s for s in config.stages if s.name == "test"][0]
        assert "lint" in test_stage.depends_on

    def test_parse_job_conditions(self, temp_ci_config_file):
        """Should parse job execution conditions."""
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        config = agent.parse_config()

        lint_stage = config.stages[0]
        lint_ui_job = lint_stage.jobs[0]

        assert lint_ui_job.condition is not None
        assert lint_ui_job.condition["type"] == "files_changed"
        assert "ui/**/*.{js,jsx,ts,tsx}" in lint_ui_job.condition["pattern"]

    def test_parse_timeout_settings(self, temp_ci_config_file):
        """Should parse timeout settings for pipeline and jobs."""
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        config = agent.parse_config()

        assert config.timeout == 600
        assert config.stages[0].jobs[0].timeout == 60

    def test_default_config_values(self):
        """Should apply default values for optional fields."""
        minimal_config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(minimal_config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            config = agent.parse_config()

            # Check defaults
            assert config.fail_fast is False  # Default
            assert config.parallel is False  # Default
            assert config.timeout == 600  # Default
        finally:
            os.unlink(temp_path)


# ============================================================================
# 2. SMART DETECTION TESTS
# ============================================================================

class TestSmartDetection:
    """Test smart detection of changed components."""

    def test_detect_ui_changes(self, mock_git_context):
        """Should detect UI changes from git diff."""
        detector = SmartDetector(base_branch="main")
        changes = detector.detect_changes(mock_git_context)

        assert changes["ui_changed"] is True
        assert "ui/src/components/Dashboard.jsx" in changes["ui_files"]

    def test_detect_api_changes(self, mock_git_context):
        """Should detect API changes from git diff."""
        detector = SmartDetector(base_branch="main")
        changes = detector.detect_changes(mock_git_context)

        assert changes["api_changed"] is True
        assert "api/views.py" in changes["api_files"]

    def test_detect_docs_changes(self, mock_git_context):
        """Should detect documentation changes."""
        detector = SmartDetector(base_branch="main")
        changes = detector.detect_changes(mock_git_context)

        assert changes["docs_changed"] is True
        assert "docs/README.md" in changes["docs_files"]

    def test_detect_no_changes(self):
        """Should handle no changes scenario."""
        git_context = {
            "branch": "test",
            "base_branch": "main",
            "changed_files": [],
            "diff": ""
        }

        detector = SmartDetector(base_branch="main")
        changes = detector.detect_changes(git_context)

        assert changes["ui_changed"] is False
        assert changes["api_changed"] is False

    def test_pattern_matching_ui_extensions(self):
        """Should match UI file extensions correctly."""
        git_context = {
            "changed_files": [
                "ui/src/App.jsx",
                "ui/src/utils.ts",
                "ui/src/styles.css"
            ]
        }

        detector = SmartDetector()
        changes = detector.detect_changes(git_context)

        assert changes["ui_changed"] is True
        assert len(changes["ui_files"]) == 3

    def test_pattern_matching_api_extensions(self):
        """Should match API file extensions correctly."""
        git_context = {
            "changed_files": [
                "api/models.py",
                "api/serializers.py",
                "api/tests/test_views.py"
            ]
        }

        detector = SmartDetector()
        changes = detector.detect_changes(git_context)

        assert changes["api_changed"] is True
        assert len(changes["api_files"]) == 3

    def test_git_diff_parsing(self, sample_git_diff):
        """Should parse git diff output correctly."""
        detector = SmartDetector()
        parsed_files = detector.parse_git_diff(sample_git_diff)

        assert "ui/src/components/Dashboard.jsx" in parsed_files
        assert "api/views.py" in parsed_files
        assert len(parsed_files) == 2


# ============================================================================
# 3. PARALLEL EXECUTION TESTS
# ============================================================================

class TestParallelExecution:
    """Test parallel job execution."""

    def test_parallel_job_execution(self):
        """Should execute multiple jobs in parallel."""
        async def run_test():
            jobs = [
                Job(name="job1", command="echo 'test1'", timeout=10),
                Job(name="job2", command="echo 'test2'", timeout=10),
                Job(name="job3", command="echo 'test3'", timeout=10)
            ]

            executor = JobExecutor()
            start_time = datetime.now()
            results = await executor.execute_parallel(jobs)
            duration = (datetime.now() - start_time).total_seconds()

            assert len(results) == 3
            # Should complete in parallel (< 3 seconds for 3 sequential jobs)
            assert duration < 5

        asyncio.run(run_test())

    def test_sequential_job_execution(self):
        """Should execute jobs sequentially when parallel=False."""
        async def run_test():
            jobs = [
                Job(name="job1", command="echo 'test1'", timeout=10),
                Job(name="job2", command="echo 'test2'", timeout=10)
            ]

            executor = JobExecutor(parallel=False)
            results = await executor.execute_sequential(jobs)

            assert len(results) == 2
            assert results[0].job_name == "job1"
            assert results[1].job_name == "job2"

        asyncio.run(run_test())

    def test_asyncio_subprocess_management(self):
        """Should manage subprocess execution via asyncio."""
        async def run_test():
            job = Job(name="test_job", command="sleep 0.1 && echo 'done'", timeout=5)

            executor = JobExecutor()
            result = await executor.execute_job(job)

            assert result.status == "success"
            assert "done" in result.stdout

        asyncio.run(run_test())

    def test_parallel_execution_with_failures(self):
        """Should handle failures in parallel execution."""
        async def run_test():
            jobs = [
                Job(name="success_job", command="echo 'ok'", timeout=10),
                Job(name="fail_job", command="exit 1", timeout=10),
                Job(name="another_success", command="echo 'ok2'", timeout=10)
            ]

            executor = JobExecutor()
            results = await executor.execute_parallel(jobs)

            assert len(results) == 3
            success_count = sum(1 for r in results if r.status == "success")
            failure_count = sum(1 for r in results if r.status == "failure")

            assert success_count == 2
            assert failure_count == 1

        asyncio.run(run_test())


# ============================================================================
# 4. DEPENDENCY RESOLUTION TESTS
# ============================================================================

class TestDependencyResolution:
    """Test stage dependency resolution."""

    def test_resolve_linear_dependencies(self):
        """Should resolve linear stage dependencies."""
        stages = [
            Stage(name="build", depends_on=["test"]),
            Stage(name="test", depends_on=["lint"]),
            Stage(name="lint", depends_on=[])
        ]

        resolver = DependencyResolver()
        execution_order = resolver.resolve(stages)

        assert execution_order == ["lint", "test", "build"]

    def test_resolve_parallel_stages(self):
        """Should identify stages that can run in parallel."""
        stages = [
            Stage(name="lint_ui", depends_on=[]),
            Stage(name="lint_api", depends_on=[]),
            Stage(name="test", depends_on=["lint_ui", "lint_api"])
        ]

        resolver = DependencyResolver()
        parallel_groups = resolver.get_parallel_groups(stages)

        assert len(parallel_groups) == 2
        assert set(parallel_groups[0]) == {"lint_ui", "lint_api"}
        assert parallel_groups[1] == ["test"]

    def test_detect_circular_dependencies(self):
        """Should detect circular dependencies."""
        stages = [
            Stage(name="a", depends_on=["b"]),
            Stage(name="b", depends_on=["c"]),
            Stage(name="c", depends_on=["a"])
        ]

        resolver = DependencyResolver()
        with pytest.raises(ValueError, match="Circular dependency"):
            resolver.resolve(stages)

    def test_validate_dependency_exists(self):
        """Should validate that dependencies reference existing stages."""
        stages = [
            Stage(name="test", depends_on=["nonexistent_stage"])
        ]

        resolver = DependencyResolver()
        with pytest.raises(ValueError, match="Unknown dependency"):
            resolver.resolve(stages)

    def test_topological_sort(self):
        """Should perform topological sort correctly."""
        stages = [
            Stage(name="deploy", depends_on=["test", "build"]),
            Stage(name="test", depends_on=["lint"]),
            Stage(name="build", depends_on=["lint"]),
            Stage(name="lint", depends_on=[])
        ]

        resolver = DependencyResolver()
        order = resolver.resolve(stages)

        # lint must be first
        assert order[0] == "lint"
        # deploy must be last
        assert order[-1] == "deploy"
        # test and build can be in any order but after lint
        assert order.index("test") > order.index("lint")
        assert order.index("build") > order.index("lint")


# ============================================================================
# 5. TIMEOUT HANDLING TESTS
# ============================================================================

class TestTimeoutHandling:
    """Test timeout handling for jobs and pipeline."""

    def async def (test_job_timeout):
self"""        """
        async def run_test():
        job = Job(name="long_job", command="sleep 10", timeout=1)

        executor = JobExecutor()
        result = await executor.execute_job(job)

        assert result.status == "timeout"
        assert result.duration < 2  # Should timeout around 1 second

    def async def (test_pipeline_timeout):
self, temp_ci_config_file"""        """
        async def run_test():
        config_with_short_timeout = {
            "version": "1.0",
            "pipeline": {
                "name": "Test",
                "timeout": 2  # 2 seconds
            },
            "stages": [
                {
                    "name": "slow_stage",
                    "jobs": [
                        {
                            "name": "slow_job",
                            "command": "sleep 10",
                            "timeout": 60
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_with_short_timeout, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            result = await agent.run_pipeline()

            assert result.status == "timeout"
            assert result.duration < 5
        finally:
            os.unlink(temp_path)

    def async def (test_timeout_cleanup):
self"""        """
        async def run_test():
        job = Job(name="test", command="sleep 100", timeout=1)

        executor = JobExecutor()
        result = await executor.execute_job(job)

        # Verify process was terminated
        assert result.status == "timeout"
        # No zombie processes should remain
        # (In real implementation, check process cleanup)

    def async def (test_configurable_timeout_per_job):
self"""        """
        async def run_test():
        jobs = [
            Job(name="fast", command="echo 'fast'", timeout=1),
            Job(name="slow", command="sleep 5", timeout=2)
        ]

        executor = JobExecutor()
        results = await executor.execute_parallel(jobs)

        fast_result = [r for r in results if r.job_name == "fast"][0]
        slow_result = [r for r in results if r.job_name == "slow"][0]

        assert fast_result.status == "success"
        assert slow_result.status == "timeout"


# ============================================================================
# 6. FAIL-FAST BEHAVIOR TESTS
# ============================================================================

class TestFailFastBehavior:
    """Test fail-fast pipeline behavior."""

    def async def (test_fail_fast_enabled):
self"""        """
        async def run_test():
        config = {
            "version": "1.0",
            "pipeline": {
                "name": "Test",
                "fail_fast": True
            },
            "stages": [
                {
                    "name": "stage1",
                    "jobs": [{"name": "job1", "command": "exit 1"}]
                },
                {
                    "name": "stage2",
                    "jobs": [{"name": "job2", "command": "echo 'should not run'"}]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            result = await agent.run_pipeline()

            assert result.status == "failure"
            assert len(result.stage_results) == 1  # Only stage1 ran
            assert result.stage_results[0].stage_name == "stage1"
        finally:
            os.unlink(temp_path)

    def async def (test_fail_fast_disabled):
self"""        """
        async def run_test():
        config = {
            "version": "1.0",
            "pipeline": {
                "name": "Test",
                "fail_fast": False
            },
            "stages": [
                {
                    "name": "stage1",
                    "depends_on": [],
                    "jobs": [{"name": "job1", "command": "exit 1"}]
                },
                {
                    "name": "stage2",
                    "depends_on": [],
                    "jobs": [{"name": "job2", "command": "echo 'ok'"}]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            result = await agent.run_pipeline()

            # Both stages should run
            assert len(result.stage_results) == 2
            assert result.stage_results[0].status == "failure"
            assert result.stage_results[1].status == "success"
        finally:
            os.unlink(temp_path)

    def async def (test_continue_on_error_per_job):
self"""        """
        async def run_test():
        job1 = Job(name="job1", command="exit 1", continue_on_error=True)
        job2 = Job(name="job2", command="echo 'ok'", continue_on_error=False)

        executor = JobExecutor()
        result1 = await executor.execute_job(job1)
        result2 = await executor.execute_job(job2)

        # Job1 fails but continues
        assert result1.status == "failure"
        assert result1.continue_on_error is True

        # Job2 succeeds
        assert result2.status == "success"


# ============================================================================
# 7. RESULT AGGREGATION TESTS
# ============================================================================

class TestResultAggregation:
    """Test result aggregation and reporting."""

    def test_aggregate_job_results(self):
        """Should aggregate multiple job results."""
        job_results = [
            JobResult(job_name="job1", status="success", duration=1.5, exit_code=0),
            JobResult(job_name="job2", status="failure", duration=2.0, exit_code=1),
            JobResult(job_name="job3", status="success", duration=0.8, exit_code=0)
        ]

        aggregator = ResultAggregator()
        summary = aggregator.aggregate_jobs(job_results)

        assert summary["total_jobs"] == 3
        assert summary["successful_jobs"] == 2
        assert summary["failed_jobs"] == 1
        assert summary["total_duration"] == pytest.approx(4.3, rel=0.1)

    def test_aggregate_stage_results(self):
        """Should aggregate stage results."""
        stage_results = [
            StageResult(stage_name="lint", status="success", job_results=[]),
            StageResult(stage_name="test", status="failure", job_results=[]),
            StageResult(stage_name="build", status="success", job_results=[])
        ]

        aggregator = ResultAggregator()
        summary = aggregator.aggregate_stages(stage_results)

        assert summary["total_stages"] == 3
        assert summary["successful_stages"] == 2
        assert summary["failed_stages"] == 1

    def test_calculate_success_rate(self):
        """Should calculate pipeline success rate."""
        job_results = [
            JobResult(job_name="j1", status="success", duration=1.0, exit_code=0),
            JobResult(job_name="j2", status="success", duration=1.0, exit_code=0),
            JobResult(job_name="j3", status="failure", duration=1.0, exit_code=1),
            JobResult(job_name="j4", status="success", duration=1.0, exit_code=0)
        ]

        aggregator = ResultAggregator()
        success_rate = aggregator.calculate_success_rate(job_results)

        assert success_rate == 75.0  # 3 out of 4 succeeded

    def test_generate_summary_statistics(self):
        """Should generate comprehensive summary statistics."""
        pipeline_result = PipelineResult(
            status="success",
            stage_results=[
                StageResult(
                    stage_name="test",
                    status="success",
                    job_results=[
                        JobResult(job_name="j1", status="success", duration=1.5, exit_code=0),
                        JobResult(job_name="j2", status="success", duration=2.5, exit_code=0)
                    ]
                )
            ],
            duration=5.0,
            timestamp=datetime.now()
        )

        aggregator = ResultAggregator()
        stats = aggregator.generate_statistics(pipeline_result)

        assert "total_jobs" in stats
        assert "total_stages" in stats
        assert "success_rate" in stats
        assert "total_duration" in stats


# ============================================================================
# 8. DRY-RUN MODE TESTS
# ============================================================================

class TestDryRunMode:
    """Test dry-run mode functionality."""

    def async def (test_dry_run_no_execution):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(
            config_file=temp_ci_config_file,
            dry_run=True
        )

        result = await agent.run_pipeline()

        assert result.status == "dry_run"
        assert result.dry_run is True
        # No actual job execution
        for stage_result in result.stage_results:
            for job_result in stage_result.job_results:
                assert job_result.status == "skipped"

    def async def (test_dry_run_shows_execution_plan):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(
            config_file=temp_ci_config_file,
            dry_run=True
        )

        plan = await agent.get_execution_plan()

        assert "stages" in plan
        assert "jobs" in plan
        assert len(plan["stages"]) > 0

    def async def (test_dry_run_validates_config):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(
            config_file=temp_ci_config_file,
            dry_run=True
        )

        validation_result = agent.validate_config()

        assert validation_result["valid"] is True
        assert "errors" in validation_result
        assert len(validation_result["errors"]) == 0


# ============================================================================
# 9. JSON REPORT GENERATION TESTS
# ============================================================================

class TestJSONReportGeneration:
    """Test JSON pipeline report generation."""

    def test_generate_json_report(self):
        """Should generate valid JSON report."""
        pipeline_result = PipelineResult(
            status="success",
            stage_results=[],
            duration=10.5,
            timestamp=datetime.now()
        )

        agent = CIPipelineOrchestratorAgent()
        report_json = agent.generate_json_report(pipeline_result)

        report = json.loads(report_json)
        assert report["status"] == "success"
        assert report["duration"] == 10.5
        assert "timestamp" in report

    def test_json_report_includes_all_results(self):
        """Should include all job and stage results in JSON."""
        pipeline_result = PipelineResult(
            status="success",
            stage_results=[
                StageResult(
                    stage_name="test",
                    status="success",
                    job_results=[
                        JobResult(
                            job_name="test_job",
                            status="success",
                            duration=2.0,
                            exit_code=0,
                            stdout="Test output",
                            stderr=""
                        )
                    ]
                )
            ],
            duration=3.0,
            timestamp=datetime.now()
        )

        agent = CIPipelineOrchestratorAgent()
        report_json = agent.generate_json_report(pipeline_result)

        report = json.loads(report_json)
        assert len(report["stage_results"]) == 1
        assert len(report["stage_results"][0]["job_results"]) == 1
        assert report["stage_results"][0]["job_results"][0]["stdout"] == "Test output"

    def test_save_json_report_to_file(self, tmp_path):
        """Should save JSON report to file."""
        pipeline_result = PipelineResult(
            status="success",
            stage_results=[],
            duration=5.0,
            timestamp=datetime.now()
        )

        output_file = tmp_path / "pipeline_report.json"
        agent = CIPipelineOrchestratorAgent(output=str(output_file))
        agent.save_json_report(pipeline_result)

        assert output_file.exists()
        with open(output_file) as f:
            report = json.load(f)

        assert report["status"] == "success"

    def test_json_report_schema_validation(self):
        """Should generate JSON report matching expected schema."""
        pipeline_result = PipelineResult(
            status="success",
            stage_results=[],
            duration=1.0,
            timestamp=datetime.now()
        )

        agent = CIPipelineOrchestratorAgent()
        report_json = agent.generate_json_report(pipeline_result)
        report = json.loads(report_json)

        # Validate schema
        required_fields = ["status", "stage_results", "duration", "timestamp"]
        for field in required_fields:
            assert field in report


# ============================================================================
# 10. CLI INTERFACE TESTS
# ============================================================================

class TestCLIInterface:
    """Test CLI argument parsing and handling."""

    def test_cli_config_argument(self):
        """Should accept --config argument."""
        args = ["--config", ".ci-local.yaml"]
        agent = CIPipelineOrchestratorAgent.from_cli_args(args)

        assert agent.config_file == ".ci-local.yaml"

    def test_cli_stage_filter(self):
        """Should accept --stage argument to run specific stage."""
        args = ["--config", ".ci-local.yaml", "--stage", "test"]
        agent = CIPipelineOrchestratorAgent.from_cli_args(args)

        assert agent.stage_filter == "test"

    def test_cli_job_filter(self):
        """Should accept --job argument to run specific job."""
        args = ["--config", ".ci-local.yaml", "--job", "test_ui"]
        agent = CIPipelineOrchestratorAgent.from_cli_args(args)

        assert agent.job_filter == "test_ui"

    def test_cli_dry_run_flag(self):
        """Should accept --dry-run flag."""
        args = ["--config", ".ci-local.yaml", "--dry-run"]
        agent = CIPipelineOrchestratorAgent.from_cli_args(args)

        assert agent.dry_run is True

    def test_cli_output_argument(self):
        """Should accept --output argument for JSON report."""
        args = ["--config", ".ci-local.yaml", "--output", "report.json"]
        agent = CIPipelineOrchestratorAgent.from_cli_args(args)

        assert agent.output == "report.json"

    def test_cli_help_message(self):
        """Should display help message with --help."""
        with pytest.raises(SystemExit):
            CIPipelineOrchestratorAgent.from_cli_args(["--help"])


# ============================================================================
# 11. EXIT CODE TESTS
# ============================================================================

class TestExitCodes:
    """Test exit code handling."""

    def async def (test_exit_code_success):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        exit_code = await agent.run()

        assert exit_code == 0

    def async def (test_exit_code_failure):
self"""        """
        async def run_test():
        config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": [
                {
                    "name": "fail_stage",
                    "jobs": [{"name": "fail", "command": "exit 1"}]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            exit_code = await agent.run()

            assert exit_code == 1
        finally:
            os.unlink(temp_path)

    def async def (test_exit_code_warnings):
self"""        """
        async def run_test():
        config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": [
                {
                    "name": "warn_stage",
                    "jobs": [
                        {
                            "name": "warn_job",
                            "command": "echo 'Warning: something' && exit 0",
                            "continue_on_error": True
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            # Simulate warnings
            agent.warnings.append("Test warning")
            exit_code = await agent.run()

            assert exit_code == 2
        finally:
            os.unlink(temp_path)


# ============================================================================
# 12. INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete pipeline execution."""

    def async def (test_full_pipeline_execution):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)
        result = await agent.run_pipeline()

        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'stage_results')

    def async def (test_pipeline_with_smart_detection):
self, temp_ci_config_file, mock_git_context"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(
            config_file=temp_ci_config_file,
            git_context=mock_git_context
        )

        result = await agent.run_pipeline()

        # Should only run jobs for changed components
        assert result is not None

    def async def (test_error_recovery_and_logging):
self, temp_ci_config_file"""        """
        async def run_test():
        agent = CIPipelineOrchestratorAgent(config_file=temp_ci_config_file)

        with patch('logging.Logger.error') as mock_logger:
            # Force an error
            agent.config_file = "nonexistent.yaml"

            try:
                await agent.run_pipeline()
            except Exception:
                pass

            # Should have logged error
            assert mock_logger.called


# ============================================================================
# 13. EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_stages_list(self):
        """Should handle empty stages list."""
        config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            # Should not crash
            assert len(agent.parse_config().stages) == 0
        finally:
            os.unlink(temp_path)

    def test_missing_job_command(self):
        """Should validate that jobs have commands."""
        config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": [
                {
                    "name": "test",
                    "jobs": [{"name": "job1"}]  # Missing command
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            with pytest.raises(ValueError, match="Job.*missing command"):
                agent.parse_config()
        finally:
            os.unlink(temp_path)

    def async def (test_concurrent_job_limit):
self"""        """
        async def run_test():
        jobs = [Job(name=f"job{i}", command="sleep 0.1", timeout=5) for i in range(20)]

        executor = JobExecutor(max_concurrent=5)
        results = await executor.execute_parallel(jobs)

        assert len(results) == 20
        # All should complete successfully despite concurrency limit

    def test_malformed_condition_pattern(self):
        """Should handle malformed condition patterns."""
        config = {
            "version": "1.0",
            "pipeline": {"name": "Test"},
            "stages": [
                {
                    "name": "test",
                    "jobs": [
                        {
                            "name": "job1",
                            "command": "echo test",
                            "condition": {
                                "type": "files_changed",
                                "pattern": "[invalid regex("
                            }
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            agent = CIPipelineOrchestratorAgent(config_file=temp_path)
            # Should handle gracefully
            config_obj = agent.parse_config()
            assert config_obj is not None
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
