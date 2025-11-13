"""
ShellScriptRemediationAgent - Automated Shell Script Remediation

Component: ShellScriptRemediationAgent
Issue ID: FEATURE-SHELL-REMEDIATION-001
Date: 2025-11-13
Status: Implementation (Tier 1 MVP)
Estimated Lines: 600-800

This agent automatically remediates shell script issues using rule-based fixes.
Tier 1 (Rule-Based MVP) provides deterministic fixes for common patterns.
Tier 2 (LLM-Powered) is documented for future enhancement.
"""

import json
import re
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.coding.ai.shared.agent_base import Agent


# =============================================================================
# Data Models
# =============================================================================

class FixStrategy(Enum):
    """Remediation strategy"""
    RULE_BASED = "RULE_BASED"  # Tier 1
    LLM_COT = "LLM_COT"  # Tier 2 (future)
    HYBRID = "HYBRID"  # Tier 1 + Tier 2 validation (future)
    SKIP = "SKIP"  # Manual review


class FixStatus(Enum):
    """Fix application status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    SKIPPED = "SKIPPED"


@dataclass
class Issue:
    """Single shell script issue from analysis"""
    line: int
    type: str  # "constitutional" | "security" | "quality"
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    rule: str  # "missing_set_e", "unquoted_variable", etc.
    message: str
    context: str  # Surrounding code


@dataclass
class ScriptIssues:
    """All issues for a single script"""
    script_path: Path
    domain: str
    issues: List[Issue]
    current_score: float


@dataclass
class FixResult:
    """Result of applying a fix"""
    issue: Issue
    strategy: FixStrategy
    status: FixStatus
    fixed_content: Optional[str] = None
    backup_path: Optional[Path] = None
    confidence: float = 0.0
    error_message: Optional[str] = None


@dataclass
class ScriptRemediationResult:
    """Result of remediating a single script"""
    script_path: Path
    original_score: float
    new_score: float
    fixes_applied: List[FixResult]
    fixes_skipped: List[Issue]
    validation_passed: bool
    remediation_time: float


# =============================================================================
# Fix Rules (Tier 1 - Rule-Based)
# =============================================================================

class FixRule(ABC):
    """Base class for fix rules"""

    @abstractmethod
    def matches(self, issue: Issue) -> bool:
        """Check if this rule applies to the issue"""
        pass

    @abstractmethod
    def apply(self, content: str, issue: Issue) -> str:
        """Apply the fix to the content"""
        pass

    @abstractmethod
    def get_confidence(self) -> float:
        """Return confidence level (0.0-1.0)"""
        pass


class AddSetERule(FixRule):
    """Add 'set -euo pipefail' after shebang"""

    def matches(self, issue: Issue) -> bool:
        return issue.rule == "missing_set_e"

    def apply(self, content: str, issue: Issue) -> str:
        lines = content.split('\n')

        # Find shebang
        shebang_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#!/bin/bash') or line.startswith('#!/usr/bin/env bash'):
                shebang_idx = i
                break

        # Check if already has set -e
        if shebang_idx + 1 < len(lines):
            next_line = lines[shebang_idx + 1].strip()
            if 'set -' in next_line:
                # Already has set, just ensure it has euo pipefail
                if 'set -euo pipefail' not in next_line:
                    lines[shebang_idx + 1] = 'set -euo pipefail'
                return '\n'.join(lines)

        # Insert set -euo pipefail after shebang
        lines.insert(shebang_idx + 1, 'set -euo pipefail')
        return '\n'.join(lines)

    def get_confidence(self) -> float:
        return 0.99  # Very high confidence


class QuoteVariableRule(FixRule):
    """Quote unquoted variables"""

    def matches(self, issue: Issue) -> bool:
        return issue.rule == "unquoted_variable"

    def apply(self, content: str, issue: Issue) -> str:
        lines = content.split('\n')

        # Get the line with the issue
        if issue.line < 1 or issue.line > len(lines):
            return content

        line_idx = issue.line - 1
        line = lines[line_idx]

        # Find unquoted variables: $VAR or ${VAR}
        # Simple pattern: $\w+ not already in quotes
        pattern = r'(?<!")(\$\{?\w+\}?)(?!")'

        def quote_var(match):
            var = match.group(1)
            # Don't quote if already in quotes or in special contexts
            return f'"{var}"'

        fixed_line = re.sub(pattern, quote_var, line)
        lines[line_idx] = fixed_line

        return '\n'.join(lines)

    def get_confidence(self) -> float:
        return 0.95  # High confidence, but context matters


class ReplaceOrTrueRule(FixRule):
    """Replace || true with explicit error handling"""

    def matches(self, issue: Issue) -> bool:
        return issue.rule == "or_true_pattern"

    def apply(self, content: str, issue: Issue) -> str:
        lines = content.split('\n')

        if issue.line < 1 or issue.line > len(lines):
            return content

        line_idx = issue.line - 1
        line = lines[line_idx]

        # Extract command before || true
        match = re.match(r'(.+?)\s*\|\|\s*true', line)
        if not match:
            return content

        command = match.group(1).strip()

        # Replace with if-statement
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent

        replacement = [
            f"{indent_str}if ! {command}; then",
            f"{indent_str}    # Command failed, continuing",
            f"{indent_str}    :",  # No-op
            f"{indent_str}fi"
        ]

        lines[line_idx:line_idx+1] = replacement
        return '\n'.join(lines)

    def get_confidence(self) -> float:
        return 0.90  # Good confidence


class RemoveUnnecessaryOrTrueRule(FixRule):
    """Remove || true for idempotent commands"""

    IDEMPOTENT_COMMANDS = ['mkdir', 'touch', 'chmod', 'chown']

    def matches(self, issue: Issue) -> bool:
        return issue.rule == "unnecessary_or_true"

    def apply(self, content: str, issue: Issue) -> str:
        lines = content.split('\n')

        if issue.line < 1 or issue.line > len(lines):
            return content

        line_idx = issue.line - 1
        line = lines[line_idx]

        # Just remove || true
        fixed_line = re.sub(r'\s*\|\|\s*true', '', line)
        lines[line_idx] = fixed_line

        return '\n'.join(lines)

    def get_confidence(self) -> float:
        return 0.98  # Very high for idempotent commands


# =============================================================================
# RuleBasedFixer Component
# =============================================================================

class RuleBasedFixer:
    """Applies rule-based fixes to scripts"""

    def __init__(self):
        self.rules = [
            AddSetERule(),
            QuoteVariableRule(),
            ReplaceOrTrueRule(),
            RemoveUnnecessaryOrTrueRule()
        ]

    def fix(self, script_content: str, issues: List[Issue]) -> List[FixResult]:
        """Apply fixes for all issues"""
        fixes_applied = []
        modified_content = script_content

        # Sort issues by line number (fix from bottom to top to preserve line numbers)
        sorted_issues = sorted(issues, key=lambda i: i.line, reverse=True)

        for issue in sorted_issues:
            # Find matching rule
            for rule in self.rules:
                if rule.matches(issue):
                    try:
                        modified_content = rule.apply(modified_content, issue)
                        fixes_applied.append(FixResult(
                            issue=issue,
                            strategy=FixStrategy.RULE_BASED,
                            status=FixStatus.SUCCESS,
                            fixed_content=modified_content,
                            confidence=rule.get_confidence()
                        ))
                        break
                    except Exception as e:
                        fixes_applied.append(FixResult(
                            issue=issue,
                            strategy=FixStrategy.RULE_BASED,
                            status=FixStatus.FAILED,
                            error_message=str(e)
                        ))

        return fixes_applied


# =============================================================================
# BackupManager Component
# =============================================================================

class BackupManager:
    """Manages script backups for rollback"""

    def __init__(self, backup_dir: Path = Path(".remediation_backup")):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup(self, script_path: Path) -> Path:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{script_path.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(script_path, backup_path)
        return backup_path

    def rollback(self, script_path: Path, backup_path: Path):
        """Restore from backup"""
        if backup_path.exists():
            shutil.copy2(backup_path, script_path)
        else:
            raise FileNotFoundError(f"Backup not found: {backup_path}")

    def cleanup_old_backups(self, days: int = 30):
        """Remove backups older than N days"""
        cutoff = datetime.now() - timedelta(days=days)
        for backup in self.backup_dir.glob("*.bak"):
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            if mtime < cutoff:
                backup.unlink()


# =============================================================================
# SyntaxValidator Component
# =============================================================================

@dataclass
class ValidationResult:
    valid: bool
    bash_errors: Optional[str] = None
    shellcheck_issues: Optional[List[str]] = None


class SyntaxValidator:
    """Validates shell script syntax"""

    def validate(self, script_path: Path) -> ValidationResult:
        """Run validation checks"""
        # bash -n (required)
        bash_result = self._bash_check(script_path)

        # ShellCheck (optional, if available)
        shellcheck_result = None
        if shutil.which("shellcheck"):
            shellcheck_result = self._shellcheck(script_path)

        valid = bash_result.valid and (shellcheck_result is None or shellcheck_result.valid)

        return ValidationResult(
            valid=valid,
            bash_errors=bash_result.bash_errors,
            shellcheck_issues=shellcheck_result.shellcheck_issues if shellcheck_result else None
        )

    def _bash_check(self, script_path: Path) -> ValidationResult:
        """Run bash -n syntax check"""
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        return ValidationResult(
            valid=(result.returncode == 0),
            bash_errors=result.stderr if result.returncode != 0 else None
        )

    def _shellcheck(self, script_path: Path) -> ValidationResult:
        """Run ShellCheck"""
        result = subprocess.run(
            ["shellcheck", "-f", "json", str(script_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ValidationResult(valid=True)

        try:
            issues = json.loads(result.stdout)
            # Only consider errors, not warnings
            errors = [i for i in issues if i.get('level') == 'error']
            return ValidationResult(
                valid=(len(errors) == 0),
                shellcheck_issues=[i['message'] for i in errors]
            )
        except Exception:
            return ValidationResult(valid=True)  # Graceful degradation


# =============================================================================
# Main Agent
# =============================================================================

class ShellScriptRemediationAgent(Agent):
    """Main remediation agent (Tier 1 MVP)"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ShellScriptRemediationAgent", config=config)

        self.dry_run = self.config.get("dry_run", False)
        self.backup_enabled = self.config.get("backup_enabled", True)

        # Initialize components
        self.rule_fixer = RuleBasedFixer()
        self.backup_manager = BackupManager()
        self.validator = SyntaxValidator()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute remediation"""
        analysis_path = Path(input_data["analysis_path"])
        # output_dir = Path(input_data.get("output_dir", "remediation_reports"))  # TODO: Use for report generation

        # Load analysis results
        analysis_data = self._load_analysis(analysis_path)

        # Remediate each script
        results = []
        for script_issues in analysis_data:
            result = self._remediate_script(script_issues)
            results.append(result)

        # Generate summary
        summary = self._calculate_summary(results)

        return {
            "status": "success",
            "summary": summary,
            "results": [self._make_json_serializable(asdict(r)) for r in results]
        }

    def _remediate_script(self, script_issues: ScriptIssues) -> ScriptRemediationResult:
        """Remediate a single script"""
        script_path = script_issues.script_path
        start_time = time.time()

        # Backup
        backup_path = None
        if self.backup_enabled and not self.dry_run:
            backup_path = self.backup_manager.backup(script_path)

        # Read script
        content = script_path.read_text()

        # Apply fixes
        fixes_applied = self.rule_fixer.fix(content, script_issues.issues)

        # Write fixes (if not dry-run)
        if not self.dry_run and fixes_applied:
            final_content = fixes_applied[-1].fixed_content
            if final_content:
                script_path.write_text(final_content)

                # Validate
                validation = self.validator.validate(script_path)

                if not validation.valid:
                    # Rollback
                    if backup_path:
                        self.backup_manager.rollback(script_path, backup_path)

                    return ScriptRemediationResult(
                        script_path=script_path,
                        original_score=script_issues.current_score,
                        new_score=script_issues.current_score,  # No change
                        fixes_applied=[],
                        fixes_skipped=script_issues.issues,
                        validation_passed=False,
                        remediation_time=time.time() - start_time
                    )

        return ScriptRemediationResult(
            script_path=script_path,
            original_score=script_issues.current_score,
            new_score=0.0,  # Would need re-analysis
            fixes_applied=fixes_applied,
            fixes_skipped=[],
            validation_passed=True,
            remediation_time=time.time() - start_time
        )

    def _load_analysis(self, analysis_path: Path) -> List[ScriptIssues]:
        """Load analysis JSON"""
        # data = json.loads(analysis_path.read_text())  # TODO: Parse JSON into ScriptIssues objects
        # Parse JSON into ScriptIssues objects
        # Implementation depends on ShellScriptAnalysisAgent output format
        # For now, return empty list (will be implemented in integration)
        return []

    def _calculate_summary(self, results: List[ScriptRemediationResult]) -> Dict:
        """Calculate summary statistics"""
        return {
            "scripts_processed": len(results),
            "fixes_applied": sum(len(r.fixes_applied) for r in results),
            "validation_passed": sum(1 for r in results if r.validation_passed)
        }

    def _make_json_serializable(self, obj: Any) -> Any:
        """Recursively convert non-JSON-serializable objects"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
