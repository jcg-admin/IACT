#!/usr/bin/env python3
"""
MetricsCollectorAgent - Metrics Collection and Tracking

Collects and analyzes metrics for the automation system:
- Constitution violations tracking
- CI pipeline metrics (duration, success rate)
- Coverage trends and history
- Developer compliance metrics
- Trend analysis (increasing/decreasing)

Part of: AUTOMATION_ARCHITECTURE.md - Section 2.2.1 #6

Author: SDLC Agent
Date: 2025-11-13
TDD: Test-driven implementation - STRICT TDD APPLIED
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directories to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.coding.ai.sdlc.base_agent import SDLCAgent


class TrendDirection(Enum):
    """Direction of trend analysis."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    UNKNOWN = "unknown"


class ViolationMetrics:
    """Data class for violation metrics."""
    pass


class CIMetrics:
    """Data class for CI pipeline metrics."""
    pass


class CoverageMetrics:
    """Data class for coverage metrics."""
    pass


class MetricsCollectorAgent(SDLCAgent):
    """
    Agent for collecting and analyzing automation system metrics.

    Responsibilities:
    - Parse logs/constitucion_violations.log
    - Track violations by rule (R1-R6)
    - Aggregate CI pipeline metrics
    - Track coverage trends
    - Calculate developer compliance
    - Generate trend analysis
    - Produce JSON and markdown reports
    """

    def __init__(self, name: str = "MetricsCollectorAgent",
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize MetricsCollectorAgent.

        Args:
            name: Agent name
            config: Configuration dict with optional keys:
                - log_file: Path to violations log
                - metrics_type: Type of metrics to collect (all, violations, ci, coverage)
                - period_days: Number of days to analyze
                - output_format: json or markdown
                - output_file: Path to output file
        """
        super().__init__(name=name, phase="metrics", config=config)

        # Configuration with validation
        self.log_file = Path(config.get("log_file")) if config and config.get("log_file") else None
        self.metrics_type = config.get("metrics_type", "all") if config else "all"
        self.period_days = max(1, config.get("period_days", 30)) if config else 30  # Ensure positive
        self.output_format = config.get("output_format", "json") if config else "json"
        self.output_file = Path(config.get("output_file")) if config and config.get("output_file") else None

        # Violation log pattern
        self.violation_pattern = re.compile(
            r'\[(?P<timestamp>[\d\-: ]+)\] VIOLATION - '
            r'Rule: (?P<rule>\w+) - '
            r'Severity: (?P<severity>\w+) - '
            r'File: (?P<file>[^\s]+) - '
            r'Line: (?P<line>\d+)'
            r'(?: - Author: (?P<author>[^\s]+))?'
            r' - Message: (?P<message>.+)'
        )

    @classmethod
    def from_cli_args(cls, args: List[str]) -> "MetricsCollectorAgent":
        """
        Create agent from CLI arguments.

        Args:
            args: List of CLI arguments

        Returns:
            Configured MetricsCollectorAgent instance
        """
        parser = argparse.ArgumentParser(
            description="MetricsCollectorAgent - Collect and analyze automation metrics"
        )

        parser.add_argument(
            "--log-file",
            type=str,
            help="Path to violations log file"
        )

        parser.add_argument(
            "--metrics-type",
            type=str,
            choices=["all", "violations", "ci", "coverage"],
            default="all",
            help="Type of metrics to collect"
        )

        parser.add_argument(
            "--period",
            type=int,
            default=30,
            help="Number of days to analyze (default: 30)"
        )

        parser.add_argument(
            "--output",
            type=str,
            help="Output file path"
        )

        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "markdown"],
            default="json",
            help="Output format"
        )

        parsed_args = parser.parse_args(args)

        config = {
            "metrics_type": parsed_args.metrics_type,
            "period_days": parsed_args.period,
            "output_format": parsed_args.format
        }

        if parsed_args.log_file:
            config["log_file"] = parsed_args.log_file

        if parsed_args.output:
            config["output_file"] = parsed_args.output

        return cls(config=config)

    def parse_violations_log(self) -> List[Dict[str, Any]]:
        """
        Parse constitution violations log file.

        Returns:
            List of violation dictionaries

        Raises:
            FileNotFoundError: If log file doesn't exist
        """
        if not self.log_file:
            return []

        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file}")

        violations = []
        content = self.log_file.read_text()

        if not content.strip():
            return []

        for line in content.splitlines():
            match = self.violation_pattern.match(line)
            if match:
                violation = {
                    "timestamp": match.group("timestamp"),
                    "rule": match.group("rule"),
                    "severity": match.group("severity"),
                    "file": match.group("file"),
                    "line": int(match.group("line")),
                    "message": match.group("message")
                }

                # Optional author field
                if match.group("author"):
                    violation["author"] = match.group("author")

                violations.append(violation)

        return violations

    def count_by_rule(self, violations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count violations grouped by rule.

        Args:
            violations: List of violation dicts

        Returns:
            Dict mapping rule ID to count
        """
        counts = defaultdict(int)

        for violation in violations:
            counts[violation["rule"]] += 1

        return dict(counts)

    def count_by_severity(self, violations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count violations grouped by severity.

        Args:
            violations: List of violation dicts

        Returns:
            Dict mapping severity to count
        """
        counts = defaultdict(int)

        for violation in violations:
            counts[violation["severity"]] += 1

        return dict(counts)

    def count_by_file(self, violations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count violations grouped by file.

        Args:
            violations: List of violation dicts

        Returns:
            Dict mapping file path to count
        """
        counts = defaultdict(int)

        for violation in violations:
            counts[violation["file"]] += 1

        return dict(counts)

    def filter_by_period(self, violations: List[Dict[str, Any]],
                        days: int) -> List[Dict[str, Any]]:
        """
        Filter violations to specific time period.

        Args:
            violations: List of violation dicts
            days: Number of days to include

        Returns:
            Filtered list of violations
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []

        for violation in violations:
            timestamp_str = violation["timestamp"]
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                if timestamp >= cutoff_date:
                    filtered.append(violation)
            except ValueError:
                # Skip violations with invalid timestamps
                continue

        return filtered

    def analyze_trend(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trend of violations over time.

        Args:
            violations: List of violation dicts

        Returns:
            Dict with trend analysis:
                - direction: str (trend direction value)
                - change_percentage: float
                - description: str
        """
        if len(violations) < 2:
            return {
                "direction": TrendDirection.UNKNOWN.value,
                "change_percentage": 0.0,
                "description": "Insufficient data for trend analysis"
            }

        # Sort by timestamp
        sorted_violations = sorted(
            violations,
            key=lambda v: datetime.strptime(v["timestamp"], "%Y-%m-%d %H:%M:%S")
        )

        # Find time range
        first_timestamp = datetime.strptime(sorted_violations[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
        last_timestamp = datetime.strptime(sorted_violations[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")
        total_duration = last_timestamp - first_timestamp

        # Split by time, not count
        mid_timestamp = first_timestamp + (total_duration / 2)

        # Count violations in first and second time periods
        first_period_count = sum(
            1 for v in sorted_violations
            if datetime.strptime(v["timestamp"], "%Y-%m-%d %H:%M:%S") < mid_timestamp
        )
        second_period_count = sum(
            1 for v in sorted_violations
            if datetime.strptime(v["timestamp"], "%Y-%m-%d %H:%M:%S") >= mid_timestamp
        )

        # Calculate percentage change
        if first_period_count == 0:
            change_percentage = 100.0 if second_period_count > 0 else 0.0
        else:
            change_percentage = ((second_period_count - first_period_count) / first_period_count) * 100

        # Determine direction
        if abs(change_percentage) < 5.0:
            direction = TrendDirection.STABLE
            description = "Violations are stable"
        elif change_percentage < 0:
            direction = TrendDirection.DECREASING
            description = f"Violations decreasing (improvement of {abs(change_percentage):.1f}%)"
        else:
            direction = TrendDirection.INCREASING
            description = f"Violations increasing (regression of {change_percentage:.1f}%)"

        return {
            "direction": direction.value,  # Convert enum to string value
            "change_percentage": change_percentage,
            "description": description
        }

    def aggregate_ci_metrics(self, metrics_file: Path) -> Dict[str, Any]:
        """
        Aggregate CI pipeline metrics from history file.

        Args:
            metrics_file: Path to CI metrics history JSON

        Returns:
            Aggregated metrics dict

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not metrics_file.exists():
            raise FileNotFoundError(f"Metrics file not found: {metrics_file}")

        with open(metrics_file) as f:
            data = json.load(f)

        pipeline_runs = data.get("pipeline_runs", [])

        if not pipeline_runs:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "fastest_run": 0,
                "slowest_run": 0
            }

        total_runs = len(pipeline_runs)
        successful_runs = sum(1 for run in pipeline_runs if run["status"] == "success")
        success_rate = (successful_runs / total_runs) * 100

        durations = [run["duration_seconds"] for run in pipeline_runs]
        average_duration = sum(durations) / len(durations)
        fastest_run = min(durations)
        slowest_run = max(durations)

        return {
            "total_runs": total_runs,
            "success_rate": success_rate,
            "average_duration": average_duration,
            "fastest_run": fastest_run,
            "slowest_run": slowest_run
        }

    def load_coverage_history(self, history_file: Path) -> Dict[str, Any]:
        """
        Load coverage history from JSON file.

        Args:
            history_file: Path to coverage history JSON

        Returns:
            Coverage history data

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not history_file.exists():
            raise FileNotFoundError(f"Coverage history not found: {history_file}")

        with open(history_file) as f:
            return json.load(f)

    def analyze_coverage_trend(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze coverage trend over time.

        Args:
            coverage_data: Coverage history data

        Returns:
            Trend analysis dict
        """
        snapshots = coverage_data.get("coverage_snapshots", [])

        if len(snapshots) < 2:
            return {
                "direction": TrendDirection.UNKNOWN.value,
                "change_percentage": 0.0,
                "start_coverage": 0.0,
                "end_coverage": 0.0
            }

        start_coverage = snapshots[0]["overall_coverage"]
        end_coverage = snapshots[-1]["overall_coverage"]

        change_percentage = ((end_coverage - start_coverage) / start_coverage) * 100

        if abs(change_percentage) < 1.0:
            direction = TrendDirection.STABLE
        elif change_percentage > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        return {
            "direction": direction.value,  # Convert enum to string value
            "change_percentage": change_percentage,
            "start_coverage": start_coverage,
            "end_coverage": end_coverage
        }

    def calculate_developer_compliance(self,
                                      violations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate compliance metrics by developer.

        Args:
            violations: List of violation dicts (must have 'author' field)

        Returns:
            Dict mapping developer to compliance metrics
        """
        compliance = defaultdict(lambda: {
            "total_violations": 0,
            "by_rule": defaultdict(int),
            "by_severity": defaultdict(int)
        })

        for violation in violations:
            if "author" not in violation:
                continue

            author = violation["author"]
            compliance[author]["total_violations"] += 1
            compliance[author]["by_rule"][violation["rule"]] += 1
            compliance[author]["by_severity"][violation["severity"]] += 1

        # Convert defaultdicts to regular dicts
        result = {}
        for author, metrics in compliance.items():
            result[author] = {
                "total_violations": metrics["total_violations"],
                "by_rule": dict(metrics["by_rule"]),
                "by_severity": dict(metrics["by_severity"])
            }

        return result

    def generate_json_report(self, metrics_data: Dict[str, Any],
                            output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate JSON report from metrics data.

        Args:
            metrics_data: Complete metrics data dict
            output_file: Optional path to save report

        Returns:
            JSON report dict
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": self.period_days,
            "metrics_type": self.metrics_type,
            **metrics_data
        }

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

        return report

    def generate_markdown_summary(self, metrics_data: Dict[str, Any],
                                  output_file: Path) -> None:
        """
        Generate markdown summary report.

        Args:
            metrics_data: Complete metrics data dict
            output_file: Path to save markdown file
        """
        lines = [
            "# Metrics Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Period: Last {self.period_days} days",
            ""
        ]

        # Violations section
        if "violations" in metrics_data:
            violations = metrics_data["violations"]
            lines.extend([
                "## Violations",
                "",
                f"Total Violations: {violations.get('total', 0)}",
                ""
            ])

            if "by_rule" in violations:
                lines.append("### By Rule")
                lines.append("")
                for rule, count in violations["by_rule"].items():
                    lines.append(f"- {rule}: {count}")
                lines.append("")

            if "trend" in violations:
                trend = violations["trend"]
                lines.append(f"Trend: {trend.get('direction', 'unknown')}")
                lines.append("")

        # CI Metrics section
        if "ci_metrics" in metrics_data:
            ci = metrics_data["ci_metrics"]
            lines.extend([
                "## CI Metrics",
                "",
                f"Total Runs: {ci.get('total_runs', 0)}",
                f"Success Rate: {ci.get('success_rate', 0):.1f}%",
                f"Average Duration: {ci.get('average_duration', 0):.1f}s",
                ""
            ])

        # Coverage section
        if "coverage" in metrics_data:
            coverage = metrics_data["coverage"]
            lines.extend([
                "## Coverage",
                "",
                f"Overall Coverage: {coverage.get('overall_coverage', 0):.1f}%",
                ""
            ])

            if "trend" in coverage:
                trend = coverage["trend"]
                lines.append(f"Trend: {trend.get('direction', 'unknown')}")
                lines.append("")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(lines))

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute metrics collection and analysis.

        Args:
            input_data: Input configuration (can override instance config)

        Returns:
            Dict with collected metrics
        """
        self.logger.info(f"Starting metrics collection - Type: {self.metrics_type}")

        results = {}

        # Collect violations metrics
        if self.metrics_type in ["all", "violations"] and self.log_file:
            try:
                violations = self.parse_violations_log()
                filtered_violations = self.filter_by_period(violations, self.period_days)

                results["violations"] = {
                    "by_rule": self.count_by_rule(filtered_violations),
                    "by_severity": self.count_by_severity(filtered_violations),
                    "by_file": self.count_by_file(filtered_violations),
                    "total": len(filtered_violations),
                    "trend": self.analyze_trend(filtered_violations)
                }

                self.logger.info(f"Collected {len(filtered_violations)} violations")

            except FileNotFoundError as e:
                self.logger.warning(f"Could not parse violations log: {e}")

        # Generate report
        if self.output_file:
            if self.output_format == "json":
                self.generate_json_report(results, self.output_file)
                self.logger.info(f"JSON report saved to {self.output_file}")
            elif self.output_format == "markdown":
                self.generate_markdown_summary(results, self.output_file)
                self.logger.info(f"Markdown report saved to {self.output_file}")

        return results

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Apply custom guardrails for metrics data.

        Args:
            output_data: Output data to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Validate metrics structure
        if not isinstance(output_data, dict):
            errors.append("Output data must be a dictionary")

        return errors


def main():
    """Main entry point for CLI usage."""
    agent = MetricsCollectorAgent.from_cli_args(sys.argv[1:])

    try:
        result = agent.execute({})

        if result.is_success():
            print("[SUCCESS] Metrics collection completed")
            return 0
        else:
            print(f"[FAILED] {result.errors}")
            return 1

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
