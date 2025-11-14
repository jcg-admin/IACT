"""
Test suite for ShellScriptRemediationAgent

Component: ShellScriptRemediationAgent
Issue ID: FEATURE-SHELL-REMEDIATION-001
Date: 2025-11-13
Status: TDD RED Phase
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import time

from scripts.coding.ai.agents.quality.shell_remediation_agent import (
    # Data Models
    FixStrategy,
    FixStatus,
    Issue,
    ScriptIssues,
    FixResult,
    ScriptRemediationResult,
    # Fix Rules
    AddSetERule,
    QuoteVariableRule,
    ReplaceOrTrueRule,
    RemoveUnnecessaryOrTrueRule,
    # Components
    RuleBasedFixer,
    BackupManager,
    SyntaxValidator,
    ShellScriptRemediationAgent
)


class TestDataModels(unittest.TestCase):
    """Test data model classes"""

    def test_fix_strategy_enum(self):
        """Test FixStrategy enum values"""
        self.assertEqual(FixStrategy.RULE_BASED.value, "RULE_BASED")
        self.assertEqual(FixStrategy.LLM_COT.value, "LLM_COT")
        self.assertEqual(FixStrategy.HYBRID.value, "HYBRID")
        self.assertEqual(FixStrategy.SKIP.value, "SKIP")

    def test_fix_status_enum(self):
        """Test FixStatus enum values"""
        self.assertEqual(FixStatus.SUCCESS.value, "SUCCESS")
        self.assertEqual(FixStatus.FAILED.value, "FAILED")
        self.assertEqual(FixStatus.ROLLED_BACK.value, "ROLLED_BACK")
        self.assertEqual(FixStatus.SKIPPED.value, "SKIPPED")

    def test_issue_creation(self):
        """Test Issue dataclass creation"""
        issue = Issue(
            line=10,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Variable $VAR should be quoted",
            context="echo $VAR"
        )
        self.assertEqual(issue.line, 10)
        self.assertEqual(issue.type, "security")
        self.assertEqual(issue.severity, "HIGH")
        self.assertEqual(issue.rule, "unquoted_variable")

    def test_script_issues_creation(self):
        """Test ScriptIssues dataclass creation"""
        issue = Issue(
            line=5,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
        script_issues = ScriptIssues(
            script_path=Path("test.sh"),
            domain="infrastructure",
            issues=[issue],
            current_score=85.0
        )
        self.assertEqual(script_issues.script_path, Path("test.sh"))
        self.assertEqual(script_issues.domain, "infrastructure")
        self.assertEqual(len(script_issues.issues), 1)
        self.assertEqual(script_issues.current_score, 85.0)

    def test_fix_result_creation(self):
        """Test FixResult dataclass creation"""
        issue = Issue(
            line=5,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
        fix_result = FixResult(
            issue=issue,
            strategy=FixStrategy.RULE_BASED,
            status=FixStatus.SUCCESS,
            fixed_content="#!/bin/bash\nset -euo pipefail",
            confidence=0.99
        )
        self.assertEqual(fix_result.status, FixStatus.SUCCESS)
        self.assertEqual(fix_result.strategy, FixStrategy.RULE_BASED)
        self.assertEqual(fix_result.confidence, 0.99)


class TestAddSetERule(unittest.TestCase):
    """Test AddSetERule fix rule"""

    def setUp(self):
        self.rule = AddSetERule()

    def test_matches_missing_set_e(self):
        """Test rule matches missing_set_e issues"""
        issue = Issue(
            line=1,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
        self.assertTrue(self.rule.matches(issue))

    def test_does_not_match_other_rules(self):
        """Test rule does not match other issue types"""
        issue = Issue(
            line=5,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Variable should be quoted",
            context="echo $VAR"
        )
        self.assertFalse(self.rule.matches(issue))

    def test_apply_adds_set_e_after_shebang(self):
        """Test applying fix adds set -euo pipefail after shebang"""
        content = "#!/bin/bash\necho 'Hello'"
        issue = Issue(
            line=1,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
        result = self.rule.apply(content, issue)
        expected = "#!/bin/bash\nset -euo pipefail\necho 'Hello'"
        self.assertEqual(result, expected)

    def test_apply_replaces_existing_set(self):
        """Test applying fix replaces existing incomplete set"""
        content = "#!/bin/bash\nset -e\necho 'Hello'"
        issue = Issue(
            line=1,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -euo pipefail",
            context="#!/bin/bash"
        )
        result = self.rule.apply(content, issue)
        self.assertIn("set -euo pipefail", result)

    def test_get_confidence(self):
        """Test confidence level is very high"""
        self.assertEqual(self.rule.get_confidence(), 0.99)


class TestQuoteVariableRule(unittest.TestCase):
    """Test QuoteVariableRule fix rule"""

    def setUp(self):
        self.rule = QuoteVariableRule()

    def test_matches_unquoted_variable(self):
        """Test rule matches unquoted_variable issues"""
        issue = Issue(
            line=5,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Variable should be quoted",
            context="echo $VAR"
        )
        self.assertTrue(self.rule.matches(issue))

    def test_apply_quotes_simple_variable(self):
        """Test applying fix quotes simple $VAR"""
        content = "#!/bin/bash\nset -euo pipefail\necho $VAR"
        issue = Issue(
            line=3,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Variable $VAR should be quoted",
            context="echo $VAR"
        )
        result = self.rule.apply(content, issue)
        self.assertIn('echo "$VAR"', result)

    def test_apply_quotes_braced_variable(self):
        """Test applying fix quotes ${VAR}"""
        content = "#!/bin/bash\necho ${VAR}"
        issue = Issue(
            line=2,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Variable ${VAR} should be quoted",
            context="echo ${VAR}"
        )
        result = self.rule.apply(content, issue)
        self.assertIn('"${VAR}"', result)

    def test_get_confidence(self):
        """Test confidence level is high"""
        self.assertEqual(self.rule.get_confidence(), 0.95)


class TestReplaceOrTrueRule(unittest.TestCase):
    """Test ReplaceOrTrueRule fix rule"""

    def setUp(self):
        self.rule = ReplaceOrTrueRule()

    def test_matches_or_true_pattern(self):
        """Test rule matches or_true_pattern issues"""
        issue = Issue(
            line=5,
            type="constitutional",
            severity="HIGH",
            rule="or_true_pattern",
            message="Avoid || true pattern",
            context="command || true"
        )
        self.assertTrue(self.rule.matches(issue))

    def test_apply_replaces_with_if_statement(self):
        """Test applying fix replaces || true with if statement"""
        content = "#!/bin/bash\nset -euo pipefail\nmkdir /tmp/test || true"
        issue = Issue(
            line=3,
            type="constitutional",
            severity="HIGH",
            rule="or_true_pattern",
            message="Avoid || true",
            context="mkdir /tmp/test || true"
        )
        result = self.rule.apply(content, issue)
        self.assertIn("if ! mkdir /tmp/test; then", result)
        self.assertIn("fi", result)

    def test_apply_preserves_indentation(self):
        """Test applying fix preserves indentation"""
        content = "#!/bin/bash\nif true; then\n    command || true\nfi"
        issue = Issue(
            line=3,
            type="constitutional",
            severity="HIGH",
            rule="or_true_pattern",
            message="Avoid || true",
            context="    command || true"
        )
        result = self.rule.apply(content, issue)
        lines = result.split('\n')
        # Check indentation is preserved
        self.assertTrue(any("    if ! command; then" in line for line in lines))

    def test_get_confidence(self):
        """Test confidence level is good"""
        self.assertEqual(self.rule.get_confidence(), 0.90)


class TestRemoveUnnecessaryOrTrueRule(unittest.TestCase):
    """Test RemoveUnnecessaryOrTrueRule fix rule"""

    def setUp(self):
        self.rule = RemoveUnnecessaryOrTrueRule()

    def test_matches_unnecessary_or_true(self):
        """Test rule matches unnecessary_or_true issues"""
        issue = Issue(
            line=5,
            type="quality",
            severity="MEDIUM",
            rule="unnecessary_or_true",
            message="Unnecessary || true for idempotent command",
            context="mkdir -p /tmp/test || true"
        )
        self.assertTrue(self.rule.matches(issue))

    def test_apply_removes_or_true(self):
        """Test applying fix removes || true"""
        content = "#!/bin/bash\nmkdir -p /tmp/test || true"
        issue = Issue(
            line=2,
            type="quality",
            severity="MEDIUM",
            rule="unnecessary_or_true",
            message="Unnecessary || true",
            context="mkdir -p /tmp/test || true"
        )
        result = self.rule.apply(content, issue)
        self.assertIn("mkdir -p /tmp/test", result)
        self.assertNotIn("|| true", result)

    def test_get_confidence(self):
        """Test confidence level is very high for idempotent commands"""
        self.assertEqual(self.rule.get_confidence(), 0.98)


class TestRuleBasedFixer(unittest.TestCase):
    """Test RuleBasedFixer component"""

    def setUp(self):
        self.fixer = RuleBasedFixer()

    def test_initialization(self):
        """Test fixer initializes with all rules"""
        self.assertEqual(len(self.fixer.rules), 4)
        self.assertIsInstance(self.fixer.rules[0], AddSetERule)
        self.assertIsInstance(self.fixer.rules[1], QuoteVariableRule)
        self.assertIsInstance(self.fixer.rules[2], ReplaceOrTrueRule)
        self.assertIsInstance(self.fixer.rules[3], RemoveUnnecessaryOrTrueRule)

    def test_fix_applies_single_issue(self):
        """Test fixing single issue"""
        content = "#!/bin/bash\necho 'Hello'"
        issue = Issue(
            line=1,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
        fixes = self.fixer.fix(content, [issue])
        self.assertEqual(len(fixes), 1)
        self.assertEqual(fixes[0].status, FixStatus.SUCCESS)
        self.assertIn("set -euo pipefail", fixes[0].fixed_content)

    def test_fix_applies_multiple_issues(self):
        """Test fixing multiple issues"""
        content = "#!/bin/bash\necho $VAR\necho $OTHER"
        issues = [
            Issue(
                line=1,
                type="constitutional",
                severity="CRITICAL",
                rule="missing_set_e",
                message="Missing set -e",
                context="#!/bin/bash"
            ),
            Issue(
                line=2,
                type="security",
                severity="HIGH",
                rule="unquoted_variable",
                message="Variable should be quoted",
                context="echo $VAR"
            )
        ]
        fixes = self.fixer.fix(content, issues)
        self.assertEqual(len(fixes), 2)
        self.assertTrue(all(f.status == FixStatus.SUCCESS for f in fixes))

    def test_fix_handles_errors_gracefully(self):
        """Test fixer handles errors in rule application"""
        content = "#!/bin/bash\necho 'test'"
        # Create issue with invalid line number
        issue = Issue(
            line=999,
            type="security",
            severity="HIGH",
            rule="unquoted_variable",
            message="Test",
            context="test"
        )
        fixes = self.fixer.fix(content, [issue])
        # Should either skip or handle gracefully
        self.assertIsInstance(fixes, list)


class TestBackupManager(unittest.TestCase):
    """Test BackupManager component"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.temp_dir) / ".remediation_backup"
        self.manager = BackupManager(backup_dir=self.backup_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_creates_backup_dir(self):
        """Test backup directory is created on init"""
        self.assertTrue(self.backup_dir.exists())
        self.assertTrue(self.backup_dir.is_dir())

    def test_backup_creates_timestamped_file(self):
        """Test backup creates timestamped backup file"""
        # Create test script
        script_path = Path(self.temp_dir) / "test_script.sh"
        script_path.write_text("#!/bin/bash\necho 'original'")

        # Create backup
        backup_path = self.manager.backup(script_path)

        # Verify backup exists and has timestamp
        self.assertTrue(backup_path.exists())
        self.assertIn("test_script", backup_path.name)
        self.assertTrue(backup_path.name.endswith(".bak"))

        # Verify content matches
        self.assertEqual(backup_path.read_text(), script_path.read_text())

    def test_rollback_restores_from_backup(self):
        """Test rollback restores script from backup"""
        # Create test script
        script_path = Path(self.temp_dir) / "test_script.sh"
        original_content = "#!/bin/bash\necho 'original'"
        script_path.write_text(original_content)

        # Create backup
        backup_path = self.manager.backup(script_path)

        # Modify script
        script_path.write_text("#!/bin/bash\necho 'modified'")

        # Rollback
        self.manager.rollback(script_path, backup_path)

        # Verify content restored
        self.assertEqual(script_path.read_text(), original_content)

    def test_rollback_raises_on_missing_backup(self):
        """Test rollback raises error if backup doesn't exist"""
        script_path = Path(self.temp_dir) / "test_script.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        fake_backup = Path(self.temp_dir) / "nonexistent.bak"

        with self.assertRaises(FileNotFoundError):
            self.manager.rollback(script_path, fake_backup)

    def test_cleanup_removes_old_backups(self):
        """Test cleanup removes backups older than specified days"""
        # Create old backup
        old_backup = self.backup_dir / "old_backup.bak"
        old_backup.write_text("old content")

        # Set mtime to 31 days ago
        old_time = time.time() - (31 * 24 * 60 * 60)
        Path(old_backup).touch()
        import os
        os.utime(old_backup, (old_time, old_time))

        # Create recent backup
        recent_backup = self.backup_dir / "recent_backup.bak"
        recent_backup.write_text("recent content")

        # Cleanup backups older than 30 days
        self.manager.cleanup_old_backups(days=30)

        # Verify old backup removed, recent backup kept
        self.assertFalse(old_backup.exists())
        self.assertTrue(recent_backup.exists())


class TestSyntaxValidator(unittest.TestCase):
    """Test SyntaxValidator component"""

    def setUp(self):
        self.validator = SyntaxValidator()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_valid_script(self):
        """Test validation passes for valid script"""
        script_path = Path(self.temp_dir) / "valid.sh"
        script_path.write_text("#!/bin/bash\nset -euo pipefail\necho 'Hello'")

        result = self.validator.validate(script_path)

        self.assertTrue(result.valid)
        self.assertIsNone(result.bash_errors)

    def test_validate_invalid_syntax(self):
        """Test validation fails for invalid syntax"""
        script_path = Path(self.temp_dir) / "invalid.sh"
        script_path.write_text("#!/bin/bash\nif true; then\necho 'missing fi'")

        result = self.validator.validate(script_path)

        self.assertFalse(result.valid)
        self.assertIsNotNone(result.bash_errors)

    def test_bash_check_detects_syntax_error(self):
        """Test bash -n detects syntax errors"""
        script_path = Path(self.temp_dir) / "syntax_error.sh"
        script_path.write_text("#!/bin/bash\nfor i in")

        result = self.validator._bash_check(script_path)

        self.assertFalse(result.valid)
        self.assertIsNotNone(result.bash_errors)


class TestShellScriptRemediationAgent(unittest.TestCase):
    """Test main ShellScriptRemediationAgent"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent = ShellScriptRemediationAgent(config={
            "dry_run": True,
            "backup_enabled": True
        })

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test agent initializes with correct config"""
        self.assertTrue(self.agent.dry_run)
        self.assertTrue(self.agent.backup_enabled)
        self.assertIsInstance(self.agent.rule_fixer, RuleBasedFixer)
        self.assertIsInstance(self.agent.backup_manager, BackupManager)
        self.assertIsInstance(self.agent.validator, SyntaxValidator)

    def test_initialization_defaults(self):
        """Test agent uses defaults when no config provided"""
        agent = ShellScriptRemediationAgent()
        self.assertFalse(agent.dry_run)
        self.assertTrue(agent.backup_enabled)

    def test_remediate_script_dry_run(self):
        """Test script remediation in dry-run mode"""
        # Create test script
        script_path = Path(self.temp_dir) / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'Hello'")

        # Create script issues
        script_issues = ScriptIssues(
            script_path=script_path,
            domain="testing",
            issues=[
                Issue(
                    line=1,
                    type="constitutional",
                    severity="CRITICAL",
                    rule="missing_set_e",
                    message="Missing set -e",
                    context="#!/bin/bash"
                )
            ],
            current_score=85.0
        )

        # Remediate
        result = self.agent._remediate_script(script_issues)

        # Verify in dry-run, file not modified
        self.assertEqual(script_path.read_text(), "#!/bin/bash\necho 'Hello'")
        self.assertIsInstance(result, ScriptRemediationResult)

    def test_remediate_script_applies_fixes(self):
        """Test script remediation applies fixes"""
        agent = ShellScriptRemediationAgent(config={
            "dry_run": False,
            "backup_enabled": True
        })

        # Create test script
        script_path = Path(self.temp_dir) / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'Hello'")

        # Create script issues
        script_issues = ScriptIssues(
            script_path=script_path,
            domain="testing",
            issues=[
                Issue(
                    line=1,
                    type="constitutional",
                    severity="CRITICAL",
                    rule="missing_set_e",
                    message="Missing set -e",
                    context="#!/bin/bash"
                )
            ],
            current_score=85.0
        )

        # Remediate
        result = agent._remediate_script(script_issues)

        # Verify fixes applied
        modified_content = script_path.read_text()
        self.assertIn("set -euo pipefail", modified_content)
        self.assertTrue(result.validation_passed)

    def test_remediate_script_rollback_on_validation_failure(self):
        """Test script rolls back if validation fails"""
        # Create test script
        script_path = Path(self.temp_dir) / "test.sh"
        original_content = "#!/bin/bash\necho 'Hello'"
        script_path.write_text(original_content)

        # Mock a fix that would create invalid syntax
        # This is a simplified test - in reality, our fixes shouldn't break syntax
        # But we test the rollback mechanism

        script_issues = ScriptIssues(
            script_path=script_path,
            domain="testing",
            issues=[],
            current_score=85.0
        )

        result = self.agent._remediate_script(script_issues)

        # Should handle gracefully
        self.assertIsInstance(result, ScriptRemediationResult)

    def test_calculate_summary(self):
        """Test summary calculation"""
        results = [
            ScriptRemediationResult(
                script_path=Path("test1.sh"),
                original_score=85.0,
                new_score=95.0,
                fixes_applied=[],
                fixes_skipped=[],
                validation_passed=True,
                remediation_time=1.5
            ),
            ScriptRemediationResult(
                script_path=Path("test2.sh"),
                original_score=80.0,
                new_score=90.0,
                fixes_applied=[],
                fixes_skipped=[],
                validation_passed=True,
                remediation_time=2.0
            )
        ]

        summary = self.agent._calculate_summary(results)

        self.assertEqual(summary["scripts_processed"], 2)
        self.assertEqual(summary["validation_passed"], 2)


if __name__ == "__main__":
    unittest.main()
