#!/usr/bin/env python3
"""
Tests for CI Pipeline Orchestrator Agent - TDD Approach

Each test follows Red-Green-Refactor cycle:
1. RED: Write failing test
2. GREEN: Minimal implementation
3. REFACTOR: Clean up code

Author: Claude Code Agent (TDD Process)
Date: 2025-11-14
"""

import unittest
from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import SmartDetector


# ============================================================================
# TDD CYCLE 1: Smart Detection - Git Diff Parsing
# ============================================================================

class TestSmartDetectorGitDiffParsing(unittest.TestCase):
    """Tests for git diff parsing functionality."""

    def test_parse_git_diff_single_file(self):
        """
        RED: Parse git diff with single file change.

        Given a git diff output with one file
        When parse_git_diff is called
        Then it should return list with that file path
        """
        detector = SmartDetector()
        diff_output = "diff --git a/api/models.py b/api/models.py"

        result = detector.parse_git_diff(diff_output)

        self.assertEqual(result, ["api/models.py"])

    def test_parse_git_diff_multiple_files(self):
        """
        RED: Parse git diff with multiple files.

        Given a git diff output with multiple files
        When parse_git_diff is called
        Then it should return list with all file paths
        """
        detector = SmartDetector()
        diff_output = """diff --git a/api/models.py b/api/models.py
diff --git a/ui/components/Button.tsx b/ui/components/Button.tsx
diff --git a/docs/README.md b/docs/README.md"""

        result = detector.parse_git_diff(diff_output)

        self.assertEqual(result, [
            "api/models.py",
            "ui/components/Button.tsx",
            "docs/README.md"
        ])

    def test_parse_git_diff_empty_output(self):
        """
        RED: Parse empty git diff output.

        Given empty git diff output
        When parse_git_diff is called
        Then it should return empty list
        """
        detector = SmartDetector()
        diff_output = ""

        result = detector.parse_git_diff(diff_output)

        self.assertEqual(result, [])




# ============================================================================
# TDD CYCLE 2: Smart Detection - File Type Classification
# ============================================================================

class TestSmartDetectorFileClassification(unittest.TestCase):
    """Tests for file type classification functionality."""

    def test_detect_changes_ui_files(self):
        """
        RED: Detect UI file changes.

        Given a git context with UI file changes
        When detect_changes is called
        Then it should mark ui_changed as True
        """
        detector = SmartDetector()
        git_context = {
            "changed_files": [
                "ui/components/Button.tsx",
                "ui/styles/main.css"
            ]
        }

        result = detector.detect_changes(git_context)

        self.assertTrue(result["ui_changed"])
        self.assertEqual(result["ui_files"], [
            "ui/components/Button.tsx",
            "ui/styles/main.css"
        ])

    def test_detect_changes_api_files(self):
        """
        RED: Detect API file changes.

        Given a git context with API file changes
        When detect_changes is called
        Then it should mark api_changed as True
        """
        detector = SmartDetector()
        git_context = {
            "changed_files": [
                "api/models.py",
                "api/views.py"
            ]
        }

        result = detector.detect_changes(git_context)

        self.assertTrue(result["api_changed"])
        self.assertEqual(result["api_files"], [
            "api/models.py",
            "api/views.py"
        ])

    def test_detect_changes_docs_files(self):
        """
        RED: Detect documentation file changes.

        Given a git context with docs file changes
        When detect_changes is called
        Then it should mark docs_changed as True
        """
        detector = SmartDetector()
        git_context = {
            "changed_files": [
                "docs/README.md",
                "docs/api/guide.md"
            ]
        }

        result = detector.detect_changes(git_context)

        self.assertTrue(result["docs_changed"])
        self.assertEqual(result["docs_files"], [
            "docs/README.md",
            "docs/api/guide.md"
        ])

    def test_detect_changes_mixed_files(self):
        """
        RED: Detect mixed file type changes.

        Given a git context with multiple file types
        When detect_changes is called
        Then it should detect all types correctly
        """
        detector = SmartDetector()
        git_context = {
            "changed_files": [
                "ui/App.tsx",
                "api/models.py",
                "docs/README.md",
                "scripts/test.sh"
            ]
        }

        result = detector.detect_changes(git_context)

        self.assertTrue(result["ui_changed"])
        self.assertTrue(result["api_changed"])
        self.assertTrue(result["docs_changed"])
        self.assertEqual(len(result["ui_files"]), 1)
        self.assertEqual(len(result["api_files"]), 1)
        self.assertEqual(len(result["docs_files"]), 1)

    def test_detect_changes_no_files(self):
        """
        RED: Detect changes with no files.

        Given an empty git context
        When detect_changes is called
        Then all flags should be False
        """
        detector = SmartDetector()
        git_context = {"changed_files": []}

        result = detector.detect_changes(git_context)

        self.assertFalse(result["ui_changed"])
        self.assertFalse(result["api_changed"])
        self.assertFalse(result["docs_changed"])




# ============================================================================
# TDD CYCLE 3: Dependency Resolution
# ============================================================================

class TestDependencyResolver(unittest.TestCase):
    """Tests for dependency resolution functionality."""

    def test_resolve_no_dependencies(self):
        """RED: Resolve stages with no dependencies."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import DependencyResolver, Stage

        resolver = DependencyResolver()
        stages = [
            Stage(name="test", jobs=[]),
            Stage(name="build", jobs=[]),
            Stage(name="lint", jobs=[])
        ]

        result = resolver.resolve(stages)

        self.assertEqual(sorted(result), ["build", "lint", "test"])

    def test_resolve_linear_dependencies(self):
        """RED: Resolve stages with linear dependencies."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import DependencyResolver, Stage

        resolver = DependencyResolver()
        stages = [
            Stage(name="deploy", jobs=[], depends_on=["test"]),
            Stage(name="test", jobs=[], depends_on=["build"]),
            Stage(name="build", jobs=[], depends_on=[])
        ]

        result = resolver.resolve(stages)

        self.assertEqual(result, ["build", "test", "deploy"])

    def test_resolve_parallel_dependencies(self):
        """RED: Resolve stages that can run in parallel."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import DependencyResolver, Stage

        resolver = DependencyResolver()
        stages = [
            Stage(name="deploy", jobs=[], depends_on=["test", "lint"]),
            Stage(name="test", jobs=[], depends_on=["build"]),
            Stage(name="lint", jobs=[], depends_on=["build"]),
            Stage(name="build", jobs=[], depends_on=[])
        ]

        result = resolver.resolve(stages)

        # build must be first, deploy must be last
        self.assertEqual(result[0], "build")
        self.assertEqual(result[-1], "deploy")
        # test and lint can be in any order
        self.assertIn("test", result)
        self.assertIn("lint", result)

    def test_resolve_circular_dependency_raises_error(self):
        """RED: Circular dependency should raise ValueError."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import DependencyResolver, Stage

        resolver = DependencyResolver()
        stages = [
            Stage(name="a", jobs=[], depends_on=["b"]),
            Stage(name="b", jobs=[], depends_on=["a"])
        ]

        with self.assertRaises(ValueError) as ctx:
            resolver.resolve(stages)

        self.assertIn("circular", str(ctx.exception).lower())

    def test_resolve_unknown_dependency_raises_error(self):
        """RED: Unknown dependency should raise ValueError."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import DependencyResolver, Stage

        resolver = DependencyResolver()
        stages = [
            Stage(name="test", jobs=[], depends_on=["unknown"])
        ]

        with self.assertRaises(ValueError) as ctx:
            resolver.resolve(stages)

        self.assertIn("unknown", str(ctx.exception).lower())




# ============================================================================
# TDD CYCLE 4: Result Aggregation
# ============================================================================

class TestResultAggregator(unittest.TestCase):
    """Tests for result aggregation functionality."""

    def test_aggregate_jobs_all_successful(self):
        """RED: Aggregate all successful jobs."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import ResultAggregator, JobResult

        aggregator = ResultAggregator()
        job_results = [
            JobResult(job_name="test1", status="success", duration=1.0, exit_code=0),
            JobResult(job_name="test2", status="success", duration=2.0, exit_code=0)
        ]

        result = aggregator.aggregate_jobs(job_results)

        self.assertEqual(result["total_jobs"], 2)
        self.assertEqual(result["successful_jobs"], 2)
        self.assertEqual(result["failed_jobs"], 0)
        self.assertEqual(result["total_duration"], 3.0)

    def test_aggregate_jobs_with_failures(self):
        """RED: Aggregate jobs with failures."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import ResultAggregator, JobResult

        aggregator = ResultAggregator()
        job_results = [
            JobResult(job_name="test1", status="success", duration=1.0, exit_code=0),
            JobResult(job_name="test2", status="failure", duration=2.0, exit_code=1),
            JobResult(job_name="test3", status="timeout", duration=3.0, exit_code=-1)
        ]

        result = aggregator.aggregate_jobs(job_results)

        self.assertEqual(result["total_jobs"], 3)
        self.assertEqual(result["successful_jobs"], 1)
        self.assertEqual(result["failed_jobs"], 1)
        self.assertEqual(result["timeout_jobs"], 1)

    def test_calculate_success_rate(self):
        """RED: Calculate success rate percentage."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import ResultAggregator, JobResult

        aggregator = ResultAggregator()
        job_results = [
            JobResult(job_name="test1", status="success", duration=1.0, exit_code=0),
            JobResult(job_name="test2", status="success", duration=2.0, exit_code=0),
            JobResult(job_name="test3", status="failure", duration=3.0, exit_code=1)
        ]

        result = aggregator.calculate_success_rate(job_results)

        self.assertAlmostEqual(result, 66.666, places=2)


# ============================================================================
# TDD CYCLE 5: Job Execution with Timeout
# ============================================================================

class TestJobExecutor(unittest.TestCase):
    """Tests for job execution functionality."""

    def test_execute_job_success(self):
        """RED: Execute successful job."""
        import asyncio
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import JobExecutor, Job

        async def test():
            executor = JobExecutor()
            job = Job(name="echo_test", command="echo 'hello'", timeout=5)

            result = await executor.execute_job(job)

            self.assertEqual(result.status, "success")
            self.assertEqual(result.exit_code, 0)
            self.assertIn("hello", result.stdout)

        asyncio.run(test())

    def test_execute_job_failure(self):
        """RED: Execute failing job."""
        import asyncio
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import JobExecutor, Job

        async def test():
            executor = JobExecutor()
            job = Job(name="fail_test", command="exit 1", timeout=5)

            result = await executor.execute_job(job)

            self.assertEqual(result.status, "failure")
            self.assertEqual(result.exit_code, 1)

        asyncio.run(test())

    def test_execute_job_timeout(self):
        """RED: Execute job that times out."""
        import asyncio
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import JobExecutor, Job

        async def test():
            executor = JobExecutor()
            job = Job(name="timeout_test", command="sleep 10", timeout=1)

            result = await executor.execute_job(job)

            self.assertEqual(result.status, "timeout")
            self.assertIn("timed out", result.stderr.lower())

        asyncio.run(test())


# ============================================================================
# TDD CYCLE 6: Job Condition Evaluation
# ============================================================================

class TestJobConditionEvaluation(unittest.TestCase):
    """Tests for job condition evaluation."""

    def test_job_should_run_no_condition(self):
        """RED: Job with no condition should always run."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import Job

        job = Job(name="test", command="echo test")

        result = job.should_run(["any/file.py"])

        self.assertTrue(result)

    def test_job_should_run_matching_pattern(self):
        """RED: Job should run when files match pattern."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import Job

        job = Job(
            name="test",
            command="echo test",
            condition={"type": "files_changed", "pattern": "**/*.py"}
        )

        result = job.should_run(["api/models.py", "ui/app.tsx"])

        self.assertTrue(result)

    def test_job_should_not_run_non_matching_pattern(self):
        """RED: Job should not run when files don't match pattern."""
        from scripts.coding.ai.automation.ci_pipeline_orchestrator_agent import Job

        job = Job(
            name="test",
            command="echo test",
            condition={"type": "files_changed", "pattern": "**/*.py"}
        )

        result = job.should_run(["ui/app.tsx", "docs/README.md"])

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
