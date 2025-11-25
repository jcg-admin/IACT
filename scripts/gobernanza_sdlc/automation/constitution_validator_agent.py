#!/usr/bin/env python3
"""
ConstitutionValidatorAgent - TDD Implementation.

This file is being rebuilt using strict TDD methodology.
Each feature is implemented following RED-GREEN-REFACTOR cycles.
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional


# ============================================================================
# CICLO 1: Estructuras básicas (Enums y Dataclasses)
# TDD: GREEN - Código mínimo para pasar tests de importación
# ============================================================================

class ValidationMode(Enum):
    """Validation modes for different contexts."""
    PRE_COMMIT = "pre-commit"
    PRE_PUSH = "pre-push"
    DEVCONTAINER_INIT = "devcontainer-init"
    CI_LOCAL = "ci-local"
    MANUAL = "manual"


class ViolationSeverity(Enum):
    """Severity levels for violations."""
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Violation:
    """Represents a constitution rule violation."""
    rule_id: str
    severity: ViolationSeverity
    message: str
    file: str
    line: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "file": self.file,
            "line": self.line,
        }


@dataclass
class RuleValidationResult:
    """Result of a single rule validation."""
    rule_id: str
    passed: bool
    violations: List[Violation] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Overall validation result."""
    passed: bool
    violations: List[Violation]
    rules_evaluated: List[str]
    summary: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate summary after initialization."""
        if not self.summary:
            self.summary = self._calculate_summary()

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate validation summary."""
        rules_failed = len(set(v.rule_id for v in self.violations if v.severity == ViolationSeverity.ERROR))
        rules_passed = len(self.rules_evaluated) - rules_failed
        has_blocking = any(v.severity == ViolationSeverity.ERROR for v in self.violations)

        return {
            "rules_evaluated": len(self.rules_evaluated),
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "blocking": has_blocking,
        }


class ConstitutionValidatorAgent:
    """Agent for validating constitution rules R1-R6."""

    # Emoji detection regex (Unicode ranges for emojis and symbols)
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric shapes
        "\U0001F800-\U0001F8FF"  # Supplemental arrows
        "\U0001F900-\U0001F9FF"  # Supplemental symbols
        "\U0001FA00-\U0001FA6F"  # Chess symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and pictographs extended
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\u2600-\u26FF"          # Miscellaneous symbols
        "\u2700-\u27BF"          # Dingbats
        "\u2300-\u23FF"          # Miscellaneous technical
        "\u2190-\u21FF"          # Arrows (partial - common ones like checkmarks)
        "]+",
        flags=re.UNICODE
    )

    # ========================================================================
    # CICLO 2: Inicialización
    # TDD: GREEN - Código mínimo para pasar tests de init
    # ========================================================================

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ConstitutionValidatorAgent."""
        self.name = "ConstitutionValidator"
        self.config = config or {}
        self.logger = self._setup_logger()
        self.project_root = Path(self.config.get("project_root", Path.cwd()))

    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the agent."""
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    # ========================================================================
    # CICLO 3: R1 - Branch Protection
    # TDD: GREEN - Código mínimo para validar branch protection
    # ========================================================================

    def validate_r1_branch_protection(self) -> RuleValidationResult:
        """
        Validate R1: No direct push to main/master.

        Returns:
            RuleValidationResult
        """
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()

            # Check if on protected branch
            protected_branches = ["main", "master"]
            if current_branch in protected_branches:
                return RuleValidationResult(
                    rule_id="R1",
                    passed=False,
                    violations=[
                        Violation(
                            rule_id="R1",
                            severity=ViolationSeverity.ERROR,
                            message=f"Direct push to protected branch '{current_branch}' is not allowed",
                            file="",
                        )
                    ],
                )

            return RuleValidationResult(rule_id="R1", passed=True, violations=[])

        except Exception as e:
            return RuleValidationResult(
                rule_id="R1",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R1",
                        severity=ViolationSeverity.ERROR,
                        message=f"Validation error: {str(e)}",
                        file="",
                    )
                ],
            )

    # ========================================================================
    # CICLO 4: R2 - Emoji Detection
    # TDD: GREEN - Código mínimo para detectar emojis
    # ========================================================================

    def validate_r2_no_emojis(self, changed_files: List[str]) -> RuleValidationResult:
        """
        Validate R2: No emojis in any files.

        Args:
            changed_files: List of files to check

        Returns:
            RuleValidationResult
        """
        all_violations = []

        for file_path in changed_files:
            try:
                violations = self.detect_emojis_in_content_from_file(file_path)
                all_violations.extend(violations)
            except Exception as e:
                self.logger.warning(f"Error scanning {file_path}: {e}")

        passed = len(all_violations) == 0

        return RuleValidationResult(
            rule_id="R2",
            passed=passed,
            violations=all_violations,
        )

    def detect_emojis_in_content_from_file(self, file_path: str) -> List[Violation]:
        """
        Detect emojis in a file.

        Args:
            file_path: Path to file

        Returns:
            List of violations
        """
        try:
            path = Path(file_path)

            # Skip if file doesn't exist
            if not path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                return []

            # Skip binary files
            if self._is_binary_file(path):
                return []

            # Read file content
            content = path.read_text(encoding='utf-8', errors='ignore')

            return self.detect_emojis_in_content(content, file_path)

        except Exception as e:
            self.logger.warning(f"Error reading {file_path}: {e}")
            return []

    def detect_emojis_in_content(self, content: str, file_path: str) -> List[Violation]:
        """
        Detect emojis in content.

        Args:
            content: Text content to scan
            file_path: File path for reporting

        Returns:
            List of Violation objects
        """
        violations = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            matches = self.EMOJI_PATTERN.finditer(line)
            for match in matches:
                emoji = match.group()
                violations.append(
                    Violation(
                        rule_id="R2",
                        severity=ViolationSeverity.ERROR,
                        message=f"Emoji detected: {repr(emoji)}",
                        file=file_path,
                        line=line_num,
                    )
                )

        return violations

    def _is_binary_file(self, path: Path) -> bool:
        """
        Check if file is binary.

        Args:
            path: Path to file

        Returns:
            True if binary, False otherwise
        """
        try:
            # Read first 8192 bytes
            with open(path, 'rb') as f:
                chunk = f.read(8192)

            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True

            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True

        except Exception:
            return True

    # ========================================================================
    # CICLO 5: R3 - UI/API Coherence
    # TDD: GREEN - Código mínimo para validar coherencia UI/API
    # ========================================================================

    def validate_r3_ui_api_coherence(self, changed_files: List[str]) -> RuleValidationResult:
        """
        Validate R3: UI/API coherence.

        Args:
            changed_files: List of changed files

        Returns:
            RuleValidationResult
        """
        # Check if any API files changed
        api_patterns = [
            "views.py", "serializers.py", "urls.py", "api.py",
            "/api/", "/backend/", "router.ts", "routes.ts"
        ]

        has_api_changes = any(
            any(pattern in str(f) for pattern in api_patterns)
            for f in changed_files
        )

        if not has_api_changes:
            return RuleValidationResult(rule_id="R3", passed=True, violations=[])

        # Call CoherenceAnalyzerAgent (integration)
        try:
            coherence_result = self._call_coherence_analyzer(changed_files)

            if coherence_result.get("coherent", True):
                return RuleValidationResult(rule_id="R3", passed=True, violations=[])

            # Convert gaps to violations
            violations = []
            for gap in coherence_result.get("gaps", []):
                violations.append(
                    Violation(
                        rule_id="R3",
                        severity=ViolationSeverity.WARNING,
                        message=f"Coherence gap: {gap.get('type', 'unknown')} - {gap.get('file', 'N/A')}",
                        file=gap.get("file", ""),
                    )
                )

            return RuleValidationResult(
                rule_id="R3",
                passed=False,
                violations=violations,
            )

        except Exception as e:
            self.logger.error(f"Error calling CoherenceAnalyzerAgent: {e}")
            return RuleValidationResult(
                rule_id="R3",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R3",
                        severity=ViolationSeverity.ERROR,
                        message=f"Coherence analysis error: {str(e)}",
                        file="",
                    )
                ],
            )

    def _call_coherence_analyzer(self, changed_files: List[str]) -> Dict[str, Any]:
        """Call CoherenceAnalyzerAgent for analysis."""
        # Placeholder for actual integration
        return {"coherent": True, "gaps": []}

    # ========================================================================
    # CICLO 6: R4 - Database Router
    # TDD: GREEN - Código mínimo para validar database router
    # ========================================================================

    def validate_r4_database_router(
        self,
        settings_file: Optional[str] = None,
        project_root: Optional[str] = None,
    ) -> RuleValidationResult:
        """
        Validate R4: Database router configuration.

        Args:
            settings_file: Path to Django settings file
            project_root: Project root directory

        Returns:
            RuleValidationResult
        """
        # Find settings file
        if not settings_file:
            settings_candidates = [
                self.project_root / "backend" / "settings.py",
                self.project_root / "config" / "settings.py",
                self.project_root / "settings.py",
            ]
            for candidate in settings_candidates:
                if candidate.exists():
                    settings_file = str(candidate)
                    break

        if not settings_file or not Path(settings_file).exists():
            self.logger.warning("Django settings file not found, skipping R4")
            return RuleValidationResult(rule_id="R4", passed=True, violations=[])

        try:
            # Read settings file
            content = Path(settings_file).read_text(encoding='utf-8')

            # Check for DATABASE_ROUTERS
            if "DATABASE_ROUTERS" not in content:
                return RuleValidationResult(
                    rule_id="R4",
                    passed=False,
                    violations=[
                        Violation(
                            rule_id="R4",
                            severity=ViolationSeverity.ERROR,
                            message="DATABASE_ROUTERS not configured in settings",
                            file=settings_file,
                        )
                    ],
                )

            # Extract router class names
            router_pattern = r"DATABASE_ROUTERS\s*=\s*\[(.*?)\]"
            match = re.search(router_pattern, content, re.DOTALL)

            if not match:
                return RuleValidationResult(
                    rule_id="R4",
                    passed=False,
                    violations=[
                        Violation(
                            rule_id="R4",
                            severity=ViolationSeverity.ERROR,
                            message="DATABASE_ROUTERS is empty or malformed",
                            file=settings_file,
                        )
                    ],
                )

            return RuleValidationResult(rule_id="R4", passed=True, violations=[])

        except Exception as e:
            self.logger.error(f"Error validating database router: {e}")
            return RuleValidationResult(
                rule_id="R4",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R4",
                        severity=ViolationSeverity.ERROR,
                        message=f"Database router validation error: {str(e)}",
                        file=settings_file or "",
                    )
                ],
            )

    # ========================================================================
    # CICLO 7: R5 - Tests Pass
    # TDD: GREEN - Código mínimo para ejecutar tests
    # ========================================================================

    def validate_r5_tests_pass(self) -> RuleValidationResult:
        """
        Validate R5: All tests must pass.

        Returns:
            RuleValidationResult
        """
        try:
            # Run tests
            result = subprocess.run(
                ["pytest", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                return RuleValidationResult(rule_id="R5", passed=True, violations=[])

            # Parse test failures
            return RuleValidationResult(
                rule_id="R5",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R5",
                        severity=ViolationSeverity.ERROR,
                        message=f"Tests failed with exit code {result.returncode}",
                        file="",
                    )
                ],
            )

        except subprocess.TimeoutExpired:
            return RuleValidationResult(
                rule_id="R5",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R5",
                        severity=ViolationSeverity.ERROR,
                        message="Test execution timed out (5 minutes)",
                        file="",
                    )
                ],
            )
        except FileNotFoundError:
            self.logger.warning("pytest not found, skipping R5")
            return RuleValidationResult(rule_id="R5", passed=True, violations=[])
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            return RuleValidationResult(
                rule_id="R5",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R5",
                        severity=ViolationSeverity.ERROR,
                        message=f"Test execution error: {str(e)}",
                        file="",
                    )
                ],
            )

    # ========================================================================
    # CICLO 8: R6 - DevContainer
    # TDD: GREEN - Código mínimo para validar DevContainer
    # ========================================================================

    def validate_r6_devcontainer_compatibility(self) -> RuleValidationResult:
        """
        Validate R6: DevContainer compatibility.

        Returns:
            RuleValidationResult
        """
        try:
            # Call DevContainerValidatorAgent (integration)
            devcontainer_result = self._call_devcontainer_validator()

            if devcontainer_result.get("valid", True):
                return RuleValidationResult(rule_id="R6", passed=True, violations=[])

            # Convert checks to violations
            violations = []
            for check in devcontainer_result.get("checks", []):
                if check.get("status") == "failed":
                    violations.append(
                        Violation(
                            rule_id="R6",
                            severity=ViolationSeverity.ERROR,
                            message=f"DevContainer check failed: {check.get('check', 'unknown')} - {check.get('message', '')}",
                            file="",
                        )
                    )

            return RuleValidationResult(
                rule_id="R6",
                passed=False,
                violations=violations,
            )

        except Exception as e:
            self.logger.error(f"Error calling DevContainerValidatorAgent: {e}")
            return RuleValidationResult(
                rule_id="R6",
                passed=False,
                violations=[
                    Violation(
                        rule_id="R6",
                        severity=ViolationSeverity.ERROR,
                        message=f"DevContainer validation error: {str(e)}",
                        file="",
                    )
                ],
            )

    def _call_devcontainer_validator(self) -> Dict[str, Any]:
        """Call DevContainerValidatorAgent for validation."""
        # Placeholder for actual integration
        return {"valid": True, "checks": []}

    # ========================================================================
    # CICLO 9: Modos de validación
    # TDD: GREEN - Código mínimo para soportar diferentes modos
    # ========================================================================

    def validate(
        self,
        mode: ValidationMode,
        changed_files: Optional[List[str]] = None,
        rules: Optional[List[str]] = None,
    ) -> ValidationResult:
        """
        Validate constitution rules based on mode.

        Args:
            mode: Validation mode
            changed_files: List of changed files
            rules: Optional specific rules to validate (for manual mode)

        Returns:
            ValidationResult with all violations
        """
        self.logger.info(f"Starting validation in mode: {mode.value}")

        # Rule mappings for different modes
        mode_rules = {
            ValidationMode.PRE_COMMIT: ["R2"],
            ValidationMode.PRE_PUSH: ["R1", "R3", "R4", "R5"],
            ValidationMode.DEVCONTAINER_INIT: ["R6"],
            ValidationMode.CI_LOCAL: ["R1", "R2", "R3", "R4", "R5", "R6"],
            ValidationMode.MANUAL: [],
        }

        # Determine which rules to validate
        rules_to_validate = rules if rules else mode_rules.get(mode, [])

        all_violations = []
        rules_evaluated = []

        # Validate each rule
        for rule_id in rules_to_validate:
            self.logger.info(f"Validating {rule_id}...")
            result = self._validate_rule(rule_id, changed_files or [])
            rules_evaluated.append(rule_id)

            if not result.passed:
                all_violations.extend(result.violations)
                self.logger.warning(f"{rule_id} validation failed: {len(result.violations)} violations")
            else:
                self.logger.info(f"{rule_id} validation passed")

        # Determine overall pass/fail
        passed = len(all_violations) == 0

        validation_result = ValidationResult(
            passed=passed,
            violations=all_violations,
            rules_evaluated=rules_evaluated,
        )

        self.logger.info(
            f"Validation complete: {len(rules_evaluated)} rules evaluated, "
            f"{len(all_violations)} violations found"
        )

        return validation_result

    def _validate_rule(self, rule_id: str, changed_files: List[str]) -> RuleValidationResult:
        """
        Validate a specific rule.

        Args:
            rule_id: Rule identifier (R1-R6)
            changed_files: List of changed files

        Returns:
            RuleValidationResult
        """
        validators = {
            "R1": lambda: self.validate_r1_branch_protection(),
            "R2": lambda: self.validate_r2_no_emojis(changed_files),
            "R3": lambda: self.validate_r3_ui_api_coherence(changed_files),
            "R4": lambda: self.validate_r4_database_router(),
            "R5": lambda: self.validate_r5_tests_pass(),
            "R6": lambda: self.validate_r6_devcontainer_compatibility(),
        }

        validator = validators.get(rule_id)
        if not validator:
            return RuleValidationResult(
                rule_id=rule_id,
                passed=False,
                violations=[
                    Violation(
                        rule_id=rule_id,
                        severity=ViolationSeverity.ERROR,
                        message=f"Unknown rule: {rule_id}",
                        file="",
                    )
                ],
            )

        try:
            return validator()
        except Exception as e:
            self.logger.exception(f"Error validating {rule_id}: {e}")
            return RuleValidationResult(
                rule_id=rule_id,
                passed=False,
                violations=[
                    Violation(
                        rule_id=rule_id,
                        severity=ViolationSeverity.ERROR,
                        message=f"Validation error: {str(e)}",
                        file="",
                    )
                ],
            )

    # ========================================================================
    # CICLO 10: Exit codes y JSON output
    # TDD: GREEN - Código mínimo para generar JSON y exit codes
    # ========================================================================

    def to_json(self, result: ValidationResult) -> str:
        """
        Convert validation result to JSON.

        Args:
            result: ValidationResult to convert

        Returns:
            JSON string
        """
        status = "success" if result.passed else "failure"

        # Check if only warnings
        has_errors = any(v.severity == ViolationSeverity.ERROR for v in result.violations)
        if not has_errors and result.violations:
            status = "warning"

        output = {
            "status": status,
            "violations": [v.to_dict() for v in result.violations],
            "summary": result.summary,
        }

        return json.dumps(output, indent=2)

    def get_exit_code(self, result: ValidationResult) -> int:
        """
        Determine exit code based on validation result.

        Args:
            result: ValidationResult

        Returns:
            Exit code (0, 1, 2, or 3)
        """
        # 0: Success
        if result.passed and not result.violations:
            return 0

        # Check for errors vs warnings
        has_errors = any(v.severity == ViolationSeverity.ERROR for v in result.violations)

        if has_errors:
            # 1: Blocking errors
            return 1
        else:
            # 2: Warnings only
            return 2

    # ========================================================================
    # CICLO 11: CLI
    # TDD: GREEN - Código mínimo para soportar CLI
    # ========================================================================

    def parse_cli_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse CLI arguments.

        Args:
            args: Optional argument list (for testing)

        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description="ConstitutionValidatorAgent - Validate constitution rules R1-R6"
        )

        parser.add_argument(
            "--mode",
            type=str,
            required=True,
            choices=["pre-commit", "pre-push", "devcontainer-init", "ci-local", "manual"],
            help="Validation mode",
        )

        parser.add_argument(
            "--config",
            type=str,
            default=".constitucion.yaml",
            help="Path to constitution config file",
        )

        parser.add_argument(
            "--changed-files",
            type=str,
            default="",
            help="Comma-separated list of changed files",
        )

        parser.add_argument(
            "--output",
            type=str,
            help="Path to output JSON report",
        )

        parser.add_argument(
            "--rules",
            type=str,
            help="Comma-separated list of specific rules to validate (for manual mode)",
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output",
        )

        return parser.parse_args(args)

    def main(self, cli_args: Optional[List[str]] = None) -> int:
        """
        Main entry point for CLI execution.

        Args:
            cli_args: Optional CLI arguments (for testing)

        Returns:
            Exit code
        """
        try:
            # Parse arguments
            args = self.parse_cli_args(cli_args)

            # Set verbosity
            if args.verbose:
                self.logger.setLevel(logging.DEBUG)

            # Parse mode
            mode = ValidationMode(args.mode)

            # Parse changed files
            changed_files = []
            if args.changed_files:
                changed_files = [f.strip() for f in args.changed_files.split(',') if f.strip()]

            # Parse specific rules (for manual mode)
            rules = None
            if args.rules:
                rules = [r.strip() for r in args.rules.split(',') if r.strip()]

            # Run validation
            result = self.validate(mode=mode, changed_files=changed_files, rules=rules)

            # Generate JSON output
            json_output = self.to_json(result)

            # Save to file if specified
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json_output, encoding='utf-8')
                self.logger.info(f"Report saved to {args.output}")

            # Print to stdout
            print(json_output)

            # Return exit code
            return self.get_exit_code(result)

        except Exception as e:
            self.logger.exception(f"Configuration error: {e}")
            error_output = {
                "status": "config_error",
                "error": str(e),
                "violations": [],
                "summary": {
                    "rules_evaluated": 0,
                    "rules_passed": 0,
                    "rules_failed": 0,
                    "blocking": True,
                }
            }
            print(json.dumps(error_output, indent=2))
            return 3  # Configuration error


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """CLI entry point."""
    agent = ConstitutionValidatorAgent()
    exit_code = agent.main()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
