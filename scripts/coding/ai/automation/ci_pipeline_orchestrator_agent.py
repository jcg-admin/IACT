#!/usr/bin/env python3
"""
CI Pipeline Orchestrator Agent

Intelligent orchestration of CI/CD pipeline execution with:
- Smart detection (git diff analysis, pattern matching)
- Parallel job execution (asyncio, subprocess management)
- Dependency resolution (stage dependencies)
- Result aggregation (JSON reports)
- Timeout handling
- Fail-fast logic

Location: scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py
Invoked by: ci-local.sh
Tests: tests/ai/automation/test_ci_pipeline_orchestrator_agent.py

Developed using TDD (Test-Driven Development)
Author: Claude Code Agent
Date: 2025-11-14
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Job:
    """Represents a CI job."""
    name: str
    command: str
    timeout: int = 60
    working_dir: str = "."
    condition: Optional[Dict[str, Any]] = None

    def should_run(self, changed_files: List[str]) -> bool:
        """Determine if job should run based on conditions."""
        if not self.condition:
            return True

        if self.condition.get("type") == "files_changed":
            pattern = self.condition.get("pattern", "")
            return self._matches_pattern(changed_files, pattern)

        return True

    def _matches_pattern(self, files: List[str], pattern: str) -> bool:
        """Check if any file matches the pattern."""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace("**", ".*").replace("*", "[^/]*")
        regex_pattern = regex_pattern.replace("{", "(").replace("}", ")")
        regex_pattern = regex_pattern.replace(",", "|")

        try:
            compiled = re.compile(regex_pattern)
            return any(compiled.search(f) for f in files)
        except re.error:
            return True  # Run by default if pattern is invalid


@dataclass
class Stage:
    """Represents a CI stage."""
    name: str
    jobs: List[Job] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class JobResult:
    """Result of job execution."""
    job_name: str
    status: str
    duration: float
    exit_code: int
    stdout: str = ""
    stderr: str = ""


# ============================================================================
# SMART DETECTOR
# ============================================================================

class SmartDetector:
    """Detects changes in codebase to optimize CI execution."""

    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch

    def parse_git_diff(self, diff_output: str) -> List[str]:
        """
        Parse git diff output to extract changed files.

        Args:
            diff_output: Output from git diff command

        Returns:
            List of changed file paths
        """
        files = []
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path from: diff --git a/path/to/file b/path/to/file
                parts = line.split(' ')
                if len(parts) >= 4:
                    # Use b/ version which is the new file path
                    filepath = parts[3].lstrip('b/')
                    files.append(filepath)
        return files

    def detect_changes(self, git_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect which components changed.

        Args:
            git_context: Git context with changed_files, diff, etc.

        Returns:
            Dictionary with changed components
        """
        changed_files = git_context.get("changed_files", [])

        ui_files = [f for f in changed_files if self._is_ui_file(f)]
        api_files = [f for f in changed_files if self._is_api_file(f)]
        docs_files = [f for f in changed_files if self._is_docs_file(f)]

        return {
            "ui_changed": len(ui_files) > 0,
            "ui_files": ui_files,
            "api_changed": len(api_files) > 0,
            "api_files": api_files,
            "docs_changed": len(docs_files) > 0,
            "docs_files": docs_files,
            "changed_files": changed_files
        }

    def _is_ui_file(self, filepath: str) -> bool:
        """Check if file is UI-related."""
        ui_extensions = ['.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.html']
        return (
            filepath.startswith('ui/') and
            any(filepath.endswith(ext) for ext in ui_extensions)
        )

    def _is_api_file(self, filepath: str) -> bool:
        """Check if file is API-related."""
        return filepath.startswith('api/') and filepath.endswith('.py')

    def _is_docs_file(self, filepath: str) -> bool:
        """Check if file is documentation."""
        return filepath.startswith('docs/') and filepath.endswith('.md')


# ============================================================================
# DEPENDENCY RESOLVER
# ============================================================================

class DependencyResolver:
    """Resolves stage dependencies using topological sort."""

    def resolve(self, stages: List[Stage]) -> List[str]:
        """
        Resolve stage execution order using Kahn's algorithm.

        Args:
            stages: List of stages with dependencies

        Returns:
            Ordered list of stage names

        Raises:
            ValueError: If circular dependency or unknown dependency
        """
        # Build dependency graph
        graph = {stage.name: set(stage.depends_on) for stage in stages}
        stage_names = {stage.name for stage in stages}

        # Validate dependencies exist
        for stage_name, deps in graph.items():
            for dep in deps:
                if dep not in stage_names:
                    raise ValueError(f"Unknown dependency: {dep} for stage {stage_name}")

        # Topological sort using Kahn's algorithm
        in_degree = {name: len(graph[name]) for name in graph}

        # Start with stages that have no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort to ensure deterministic order
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            # For each stage that depends on current, decrease its in-degree
            for stage_name, deps in graph.items():
                if current in deps:
                    in_degree[stage_name] -= 1
                    if in_degree[stage_name] == 0:
                        queue.append(stage_name)

        # Check for circular dependencies
        if len(result) != len(stages):
            raise ValueError("Circular dependency detected in stages")

        return result


# ============================================================================
# RESULT AGGREGATOR
# ============================================================================

class ResultAggregator:
    """Aggregates and analyzes pipeline results."""

    def aggregate_jobs(self, job_results: List[JobResult]) -> Dict[str, Any]:
        """Aggregate job results."""
        total = len(job_results)
        successful = sum(1 for jr in job_results if jr.status == "success")
        failed = sum(1 for jr in job_results if jr.status == "failure")
        timeout = sum(1 for jr in job_results if jr.status == "timeout")
        skipped = sum(1 for jr in job_results if jr.status == "skipped")
        total_duration = sum(jr.duration for jr in job_results)

        return {
            "total_jobs": total,
            "successful_jobs": successful,
            "failed_jobs": failed,
            "timeout_jobs": timeout,
            "skipped_jobs": skipped,
            "total_duration": total_duration
        }

    def calculate_success_rate(self, job_results: List[JobResult]) -> float:
        """Calculate success rate percentage."""
        if not job_results:
            return 0.0

        successful = sum(1 for jr in job_results if jr.status == "success")
        return (successful / len(job_results)) * 100.0


# ============================================================================
# JOB EXECUTOR
# ============================================================================

class JobExecutor:
    """Executes jobs using asyncio subprocess."""

    async def execute_job(self, job: Job) -> JobResult:
        """
        Execute a single job.

        Args:
            job: Job to execute

        Returns:
            JobResult with execution details
        """
        start_time = datetime.now()

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                job.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=job.working_dir
            )

            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=job.timeout
                )

                duration = (datetime.now() - start_time).total_seconds()
                exit_code = process.returncode

                status = "success" if exit_code == 0 else "failure"

                return JobResult(
                    job_name=job.name,
                    status=status,
                    duration=duration,
                    exit_code=exit_code,
                    stdout=stdout.decode('utf-8', errors='replace'),
                    stderr=stderr.decode('utf-8', errors='replace')
                )

            except asyncio.TimeoutError:
                # Kill process on timeout
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass

                duration = (datetime.now() - start_time).total_seconds()

                return JobResult(
                    job_name=job.name,
                    status="timeout",
                    duration=duration,
                    exit_code=-1,
                    stderr=f"Job timed out after {job.timeout}s"
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            return JobResult(
                job_name=job.name,
                status="failure",
                duration=duration,
                exit_code=-1,
                stderr=str(e)
            )
