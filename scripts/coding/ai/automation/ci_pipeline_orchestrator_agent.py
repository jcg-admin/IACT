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
ADR: docs/adr/ADR-045-ci-pipeline-orchestrator-agent.md

Author: Claude Code Agent
Date: 2025-11-13
"""

import argparse
import asyncio
import json
import logging
import re
import subprocess
import sys
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


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
    description: str = ""
    continue_on_error: bool = False
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
            logging.warning(f"Invalid pattern: {pattern}")
            return True  # Run by default if pattern is invalid


@dataclass
class Stage:
    """Represents a CI stage."""
    name: str
    jobs: List[Job] = field(default_factory=list)
    description: str = ""
    parallel: bool = False
    depends_on: List[str] = field(default_factory=list)


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    version: str
    pipeline_name: str
    fail_fast: bool = False
    parallel: bool = False
    timeout: int = 600
    stages: List[Stage] = field(default_factory=list)
    smart_detection_enabled: bool = False
    smart_detection_strategy: str = "git_diff"
    base_branch: str = "main"


@dataclass
class JobResult:
    """Result of job execution."""
    job_name: str
    status: str  # success, failure, timeout, skipped
    duration: float
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    continue_on_error: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class StageResult:
    """Result of stage execution."""
    stage_name: str
    status: str  # success, failure, timeout, skipped
    job_results: List[JobResult] = field(default_factory=list)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stage_name': self.stage_name,
            'status': self.status,
            'job_results': [jr.to_dict() for jr in self.job_results],
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    status: str  # success, failure, timeout, dry_run
    stage_results: List[StageResult] = field(default_factory=list)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'status': self.status,
            'stage_results': [sr.to_dict() for sr in self.stage_results],
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'dry_run': self.dry_run
        }


# ============================================================================
# SMART DETECTOR
# ============================================================================

class SmartDetector:
    """Detects changes in codebase to optimize CI execution."""

    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch

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

    def parse_git_diff(self, diff_output: str) -> List[str]:
        """
        Parse git diff output to extract changed files.

        Args:
            diff_output: Output from git diff

        Returns:
            List of changed file paths
        """
        files = []
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path from: diff --git a/path/to/file b/path/to/file
                # Use the 'b/' version which is the new file path
                parts = line.split(' ')
                if len(parts) >= 4:
                    filepath = parts[3].lstrip('b/')
                    files.append(filepath)

        return files


# ============================================================================
# JOB EXECUTOR
# ============================================================================

class JobExecutor:
    """Executes jobs using asyncio subprocess."""

    def __init__(self, parallel: bool = True, max_concurrent: int = 10):
        self.parallel = parallel
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

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
                    stderr=stderr.decode('utf-8', errors='replace'),
                    continue_on_error=job.continue_on_error
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
                    stderr=f"Job timed out after {job.timeout}s",
                    continue_on_error=job.continue_on_error
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            return JobResult(
                job_name=job.name,
                status="failure",
                duration=duration,
                exit_code=-1,
                stderr=str(e),
                continue_on_error=job.continue_on_error
            )

    async def execute_parallel(self, jobs: List[Job]) -> List[JobResult]:
        """
        Execute jobs in parallel with concurrency limit.

        Args:
            jobs: List of jobs to execute

        Returns:
            List of job results
        """
        async def execute_with_semaphore(job: Job) -> JobResult:
            async with self.semaphore:
                return await self.execute_job(job)

        tasks = [execute_with_semaphore(job) for job in jobs]
        return await asyncio.gather(*tasks)

    async def execute_sequential(self, jobs: List[Job]) -> List[JobResult]:
        """
        Execute jobs sequentially.

        Args:
            jobs: List of jobs to execute

        Returns:
            List of job results
        """
        results = []
        for job in jobs:
            result = await self.execute_job(job)
            results.append(result)

        return results


# ============================================================================
# DEPENDENCY RESOLVER
# ============================================================================

class DependencyResolver:
    """Resolves stage dependencies using topological sort."""

    def resolve(self, stages: List[Stage]) -> List[str]:
        """
        Resolve stage execution order.

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
        # in_degree tracks how many dependencies each stage has
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

    def get_parallel_groups(self, stages: List[Stage]) -> List[List[str]]:
        """
        Get groups of stages that can run in parallel.

        Args:
            stages: List of stages

        Returns:
            List of groups (each group can run in parallel)
        """
        graph = {stage.name: set(stage.depends_on) for stage in stages}
        stage_names = {stage.name for stage in stages}

        groups = []
        processed = set()

        while len(processed) < len(stages):
            # Find stages with all dependencies satisfied
            current_group = []
            for stage_name in stage_names:
                if stage_name in processed:
                    continue

                deps = graph[stage_name]
                if all(dep in processed for dep in deps):
                    current_group.append(stage_name)

            if not current_group:
                raise ValueError("Circular dependency detected")

            groups.append(sorted(current_group))
            processed.update(current_group)

        return groups


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

    def aggregate_stages(self, stage_results: List[StageResult]) -> Dict[str, Any]:
        """Aggregate stage results."""
        total = len(stage_results)
        successful = sum(1 for sr in stage_results if sr.status == "success")
        failed = sum(1 for sr in stage_results if sr.status == "failure")

        return {
            "total_stages": total,
            "successful_stages": successful,
            "failed_stages": failed
        }

    def calculate_success_rate(self, job_results: List[JobResult]) -> float:
        """Calculate success rate percentage."""
        if not job_results:
            return 0.0

        successful = sum(1 for jr in job_results if jr.status == "success")
        return (successful / len(job_results)) * 100.0

    def generate_statistics(self, pipeline_result: PipelineResult) -> Dict[str, Any]:
        """Generate comprehensive statistics."""
        all_job_results = []
        for stage_result in pipeline_result.stage_results:
            all_job_results.extend(stage_result.job_results)

        job_stats = self.aggregate_jobs(all_job_results)
        stage_stats = self.aggregate_stages(pipeline_result.stage_results)

        return {
            **job_stats,
            **stage_stats,
            "success_rate": self.calculate_success_rate(all_job_results),
            "total_duration": pipeline_result.duration,
            "pipeline_status": pipeline_result.status
        }


# ============================================================================
# CI PIPELINE ORCHESTRATOR AGENT
# ============================================================================

class CIPipelineOrchestratorAgent:
    """
    Main orchestrator for CI pipeline execution.

    Handles:
    - Configuration parsing
    - Smart detection
    - Job execution
    - Dependency resolution
    - Result aggregation
    """

    def __init__(
        self,
        config_file: str = ".ci-local.yaml",
        dry_run: bool = False,
        stage_filter: Optional[str] = None,
        job_filter: Optional[str] = None,
        output: Optional[str] = None,
        git_context: Optional[Dict[str, Any]] = None
    ):
        self.config_file = config_file
        self.dry_run = dry_run
        self.stage_filter = stage_filter
        self.job_filter = job_filter
        self.output = output
        self.git_context = git_context or {}
        self.warnings: List[str] = []

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def parse_config(self) -> PipelineConfig:
        """
        Parse .ci-local.yaml configuration.

        Returns:
            PipelineConfig object

        Raises:
            ValueError: If configuration is invalid
            yaml.YAMLError: If YAML syntax is invalid
        """
        config_path = Path(self.config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Validate required fields
        if "pipeline" not in data:
            raise ValueError("Missing required field: pipeline")

        if "stages" not in data:
            raise ValueError("Missing required field: stages")

        pipeline = data["pipeline"]
        smart_detection = data.get("smart_detection", {})

        # Parse stages
        stages = []
        for stage_data in data.get("stages", []):
            # Parse jobs
            jobs = []
            for job_data in stage_data.get("jobs", []):
                if "command" not in job_data:
                    raise ValueError(f"Job {job_data.get('name', 'unknown')} missing command")

                job = Job(
                    name=job_data["name"],
                    command=job_data["command"],
                    timeout=job_data.get("timeout", 60),
                    working_dir=job_data.get("working_dir", "."),
                    description=job_data.get("description", ""),
                    continue_on_error=job_data.get("continue_on_error", False),
                    condition=job_data.get("condition")
                )
                jobs.append(job)

            stage = Stage(
                name=stage_data["name"],
                jobs=jobs,
                description=stage_data.get("description", ""),
                parallel=stage_data.get("parallel", False),
                depends_on=stage_data.get("depends_on", [])
            )
            stages.append(stage)

        config = PipelineConfig(
            version=data.get("version", "1.0"),
            pipeline_name=pipeline.get("name", "CI Pipeline"),
            fail_fast=pipeline.get("fail_fast", False),
            parallel=pipeline.get("parallel", False),
            timeout=pipeline.get("timeout", 600),
            stages=stages,
            smart_detection_enabled=smart_detection.get("enabled", False),
            smart_detection_strategy=smart_detection.get("strategy", "git_diff"),
            base_branch=smart_detection.get("base_branch", "main")
        )

        return config

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration.

        Returns:
            Validation result with errors/warnings
        """
        errors = []
        warnings = []

        try:
            config = self.parse_config()

            # Check for empty stages
            if not config.stages:
                warnings.append("No stages defined")

            # Check for jobs without commands
            for stage in config.stages:
                for job in stage.jobs:
                    if not job.command:
                        errors.append(f"Job {job.name} has empty command")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }

    async def get_execution_plan(self) -> Dict[str, Any]:
        """
        Get execution plan without running.

        Returns:
            Execution plan with stages and jobs
        """
        config = self.parse_config()
        resolver = DependencyResolver()

        execution_order = resolver.resolve(config.stages)
        parallel_groups = resolver.get_parallel_groups(config.stages)

        stages_info = []
        jobs_info = []

        for stage in config.stages:
            stages_info.append({
                "name": stage.name,
                "description": stage.description,
                "depends_on": stage.depends_on,
                "job_count": len(stage.jobs)
            })

            for job in stage.jobs:
                jobs_info.append({
                    "name": job.name,
                    "stage": stage.name,
                    "command": job.command,
                    "timeout": job.timeout
                })

        return {
            "stages": stages_info,
            "jobs": jobs_info,
            "execution_order": execution_order,
            "parallel_groups": parallel_groups
        }

    async def run_pipeline(self) -> PipelineResult:
        """
        Run the complete pipeline.

        Returns:
            PipelineResult with all results
        """
        start_time = datetime.now()

        try:
            config = self.parse_config()

            # Dry run mode
            if self.dry_run:
                return await self._run_dry_run(config)

            # Smart detection
            changed_files = []
            if config.smart_detection_enabled and self.git_context:
                detector = SmartDetector(base_branch=config.base_branch)
                changes = detector.detect_changes(self.git_context)
                changed_files = changes.get("changed_files", [])

            # Resolve execution order
            resolver = DependencyResolver()
            execution_order = resolver.resolve(config.stages)

            # Execute stages
            executor = JobExecutor(parallel=config.parallel)
            stage_results = []

            for stage_name in execution_order:
                # Apply stage filter
                if self.stage_filter and stage_name != self.stage_filter:
                    continue

                stage = next((s for s in config.stages if s.name == stage_name), None)
                if not stage:
                    continue

                # Execute stage
                stage_result = await self._execute_stage(
                    stage,
                    executor,
                    changed_files
                )
                stage_results.append(stage_result)

                # Fail-fast check
                if config.fail_fast and stage_result.status == "failure":
                    self.logger.warning(f"Fail-fast triggered at stage {stage_name}")
                    break

            duration = (datetime.now() - start_time).total_seconds()

            # Determine overall status
            status = self._determine_pipeline_status(stage_results)

            return PipelineResult(
                status=status,
                stage_results=stage_results,
                duration=duration,
                timestamp=datetime.now()
            )

        except asyncio.TimeoutError:
            duration = (datetime.now() - start_time).total_seconds()
            return PipelineResult(
                status="timeout",
                stage_results=[],
                duration=duration,
                timestamp=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise

    async def _run_dry_run(self, config: PipelineConfig) -> PipelineResult:
        """Execute dry run."""
        stage_results = []

        for stage in config.stages:
            job_results = []
            for job in stage.jobs:
                job_results.append(JobResult(
                    job_name=job.name,
                    status="skipped",
                    duration=0.0,
                    exit_code=0
                ))

            stage_results.append(StageResult(
                stage_name=stage.name,
                status="skipped",
                job_results=job_results,
                duration=0.0
            ))

        return PipelineResult(
            status="dry_run",
            stage_results=stage_results,
            duration=0.0,
            timestamp=datetime.now(),
            dry_run=True
        )

    async def _execute_stage(
        self,
        stage: Stage,
        executor: JobExecutor,
        changed_files: List[str]
    ) -> StageResult:
        """Execute a single stage."""
        start_time = datetime.now()

        # Filter jobs
        jobs_to_run = []
        for job in stage.jobs:
            # Apply job filter
            if self.job_filter and job.name != self.job_filter:
                continue

            # Check conditions
            if changed_files and not job.should_run(changed_files):
                self.logger.info(f"Skipping job {job.name} (condition not met)")
                continue

            jobs_to_run.append(job)

        # Execute jobs
        if stage.parallel:
            job_results = await executor.execute_parallel(jobs_to_run)
        else:
            job_results = await executor.execute_sequential(jobs_to_run)

        duration = (datetime.now() - start_time).total_seconds()

        # Determine stage status
        has_failure = any(
            jr.status == "failure" and not jr.continue_on_error
            for jr in job_results
        )
        status = "failure" if has_failure else "success"

        return StageResult(
            stage_name=stage.name,
            status=status,
            job_results=job_results,
            duration=duration,
            timestamp=datetime.now()
        )

    def _determine_pipeline_status(self, stage_results: List[StageResult]) -> str:
        """Determine overall pipeline status."""
        if not stage_results:
            return "success"

        has_failure = any(sr.status == "failure" for sr in stage_results)
        has_timeout = any(sr.status == "timeout" for sr in stage_results)

        if has_failure:
            return "failure"
        if has_timeout:
            return "timeout"

        return "success"

    def generate_json_report(self, pipeline_result: PipelineResult) -> str:
        """
        Generate JSON report.

        Args:
            pipeline_result: Pipeline execution result

        Returns:
            JSON string
        """
        report = pipeline_result.to_dict()

        # Add statistics
        aggregator = ResultAggregator()
        report["statistics"] = aggregator.generate_statistics(pipeline_result)

        return json.dumps(report, indent=2)

    def save_json_report(self, pipeline_result: PipelineResult) -> None:
        """Save JSON report to file."""
        if not self.output:
            return

        report_json = self.generate_json_report(pipeline_result)

        output_path = Path(self.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(report_json)

        self.logger.info(f"Report saved to {self.output}")

    async def run(self) -> int:
        """
        Run pipeline and return exit code.

        Returns:
            Exit code (0=success, 1=failure, 2=warnings)
        """
        result = await self.run_pipeline()

        # Save report
        if self.output:
            self.save_json_report(result)

        # Determine exit code
        if result.status == "failure":
            return 1
        elif self.warnings:
            return 2
        else:
            return 0

    @classmethod
    def from_cli_args(cls, args: List[str]) -> 'CIPipelineOrchestratorAgent':
        """
        Create agent from CLI arguments.

        Args:
            args: Command line arguments

        Returns:
            CIPipelineOrchestratorAgent instance
        """
        parser = argparse.ArgumentParser(
            description="CI Pipeline Orchestrator Agent",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            '--config',
            type=str,
            default='.ci-local.yaml',
            help='Path to CI configuration file (default: .ci-local.yaml)'
        )

        parser.add_argument(
            '--stage',
            type=str,
            help='Run specific stage only'
        )

        parser.add_argument(
            '--job',
            type=str,
            help='Run specific job only'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show execution plan without running'
        )

        parser.add_argument(
            '--output',
            type=str,
            help='Output file for JSON report'
        )

        parsed_args = parser.parse_args(args)

        return cls(
            config_file=parsed_args.config,
            dry_run=parsed_args.dry_run,
            stage_filter=parsed_args.stage,
            job_filter=parsed_args.job,
            output=parsed_args.output
        )


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Main entry point."""
    agent = CIPipelineOrchestratorAgent.from_cli_args(sys.argv[1:])
    exit_code = await agent.run()
    return exit_code


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
