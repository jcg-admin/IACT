"""
Tests for ConstitutionValidatorAgent.

Test Coverage:
- R1: Branch protection validation (main/master)
- R2: Emoji detection with Unicode regex
- R3: UI/API coherence analysis (integration)
- R4: Database router validation (Django settings)
- R5: Test execution orchestration
- R6: DevContainer environment validation (integration)
- CLI modes: pre-commit, pre-push, ci-local, manual
- Exit codes: 0=success, 1=error, 2=warning, 3=config error
- JSON violations log
- Edge cases and error handling

TDD Approach: These tests are written FIRST before implementation.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.gobernanza_sdlc.automation.constitution_validator_agent import (
    ConstitutionValidatorAgent,
    ValidationMode,
    ValidationResult,
    ViolationSeverity,
    Violation,
)


class TestConstitutionValidatorAgentInit(unittest.TestCase):
    """Test agent initialization and configuration."""

    def test_agent_init_default_config(self):
        """Test agent initialization with default configuration."""
        agent = ConstitutionValidatorAgent()
        self.assertEqual(agent.name, "ConstitutionValidator")
        self.assertIsNotNone(agent.config)

    def test_agent_init_custom_config(self):
        """Test agent initialization with custom configuration."""
        config = {
            "project_root": "/tmp/test",
            "config_file": ".test.yaml",
        }
        agent = ConstitutionValidatorAgent(config=config)
        self.assertEqual(agent.config["project_root"], "/tmp/test")
        self.assertEqual(agent.config["config_file"], ".test.yaml")

    def test_agent_init_creates_logger(self):
        """Test that agent initialization creates a logger."""
        agent = ConstitutionValidatorAgent()
        self.assertIsNotNone(agent.logger)


class TestR1BranchProtection(unittest.TestCase):
    """Test R1: Branch protection validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_r1_detect_direct_push_to_main(self):
        """Test R1: Detect direct push to main branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="main\n",
            )
            result = self.agent.validate_r1_branch_protection()
            self.assertFalse(result.passed)
            self.assertEqual(len(result.violations), 1)
            self.assertIn("main", result.violations[0].message.lower())

    def test_r1_detect_direct_push_to_master(self):
        """Test R1: Detect direct push to master branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="master\n",
            )
            result = self.agent.validate_r1_branch_protection()
            self.assertFalse(result.passed)
            self.assertEqual(len(result.violations), 1)
            self.assertIn("master", result.violations[0].message.lower())

    def test_r1_allow_feature_branch(self):
        """Test R1: Allow push to feature branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="feature/test-branch\n",
            )
            result = self.agent.validate_r1_branch_protection()
            self.assertTrue(result.passed)
            self.assertEqual(len(result.violations), 0)

    def test_r1_allow_bugfix_branch(self):
        """Test R1: Allow push to bugfix branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="bugfix/issue-123\n",
            )
            result = self.agent.validate_r1_branch_protection()
            self.assertTrue(result.passed)

    def test_r1_git_command_failure(self):
        """Test R1: Handle git command failure gracefully."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Git command failed")
            result = self.agent.validate_r1_branch_protection()
            self.assertFalse(result.passed)
            self.assertTrue(any("error" in v.message.lower() for v in result.violations))


class TestR2EmojiDetection(unittest.TestCase):
    """Test R2: Emoji detection with Unicode regex."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_r2_detect_emoji_in_markdown(self):
        """Test R2: Detect emoji in markdown file."""
        test_content = "# Test Document\n\nThis has an emoji: ✓\n"
        violations = self.agent.detect_emojis_in_content(test_content, "test.md")
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0].severity, ViolationSeverity.ERROR)

    def test_r2_detect_unicode_emoji(self):
        """Test R2: Detect Unicode emoji characters."""
        test_content = "Great work! 🎉 👍"
        violations = self.agent.detect_emojis_in_content(test_content, "test.txt")
        self.assertGreater(len(violations), 0)

    def test_r2_detect_multiple_emojis(self):
        """Test R2: Detect multiple emojis in same file."""
        test_content = "Test ✓ Check ✗ Star ⭐"
        violations = self.agent.detect_emojis_in_content(test_content, "test.md")
        self.assertGreaterEqual(len(violations), 3)

    def test_r2_no_false_positives_ascii(self):
        """Test R2: No false positives for ASCII characters."""
        test_content = "Normal text with ASCII: !@#$%^&*()_+-=[]{}|;':,.<>?"
        violations = self.agent.detect_emojis_in_content(test_content, "test.txt")
        self.assertEqual(len(violations), 0)

    def test_r2_no_false_positives_numbers(self):
        """Test R2: No false positives for numbers and letters."""
        test_content = "Version 1.2.3 released on 2025-11-13"
        violations = self.agent.detect_emojis_in_content(test_content, "test.txt")
        self.assertEqual(len(violations), 0)

    def test_r2_no_false_positives_code_symbols(self):
        """Test R2: No false positives for programming symbols."""
        test_content = "if (x > 0) { return x * 2; }"
        violations = self.agent.detect_emojis_in_content(test_content, "test.js")
        self.assertEqual(len(violations), 0)

    def test_r2_scan_multiple_files(self):
        """Test R2: Scan multiple files for emojis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "file1.md").write_text("Clean content")
            (tmppath / "file2.md").write_text("Has emoji ✓")
            (tmppath / "file3.txt").write_text("Another emoji 🎉")

            changed_files = [
                str(tmppath / "file1.md"),
                str(tmppath / "file2.md"),
                str(tmppath / "file3.txt"),
            ]

            result = self.agent.validate_r2_no_emojis(changed_files)
            self.assertFalse(result.passed)
            self.assertEqual(len(result.violations), 2)

    def test_r2_line_number_reporting(self):
        """Test R2: Report correct line numbers for emoji violations."""
        test_content = "Line 1\nLine 2\nLine 3 with emoji ✓\nLine 4"
        violations = self.agent.detect_emojis_in_content(test_content, "test.md")
        self.assertEqual(violations[0].line, 3)


class TestR3CoherenceAnalysis(unittest.TestCase):
    """Test R3: UI/API coherence analysis integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_r3_calls_coherence_analyzer(self):
        """Test R3: Calls CoherenceAnalyzerAgent for analysis."""
        with patch.object(self.agent, "_call_coherence_analyzer") as mock_analyzer:
            mock_analyzer.return_value = {
                "coherent": True,
                "gaps": [],
            }

            changed_files = ["api/views.py", "ui/services.ts"]
            result = self.agent.validate_r3_ui_api_coherence(changed_files)

            mock_analyzer.assert_called_once_with(changed_files)
            self.assertTrue(result.passed)

    def test_r3_detects_incoherence(self):
        """Test R3: Detect UI/API incoherence."""
        with patch.object(self.agent, "_call_coherence_analyzer") as mock_analyzer:
            mock_analyzer.return_value = {
                "coherent": False,
                "gaps": [
                    {
                        "type": "missing_ui_test",
                        "endpoint": "/api/users",
                        "file": "ui/services/user.service.ts",
                    }
                ],
            }

            changed_files = ["api/views.py"]
            result = self.agent.validate_r3_ui_api_coherence(changed_files)

            self.assertFalse(result.passed)
            self.assertGreater(len(result.violations), 0)

    def test_r3_skips_if_no_api_changes(self):
        """Test R3: Skip coherence check if no API changes."""
        changed_files = ["docs/README.md", "tests/test_utils.py"]
        result = self.agent.validate_r3_ui_api_coherence(changed_files)
        self.assertTrue(result.passed)


class TestR4DatabaseRouter(unittest.TestCase):
    """Test R4: Database router validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_r4_validate_router_exists(self):
        """Test R4: Validate database router exists in settings."""
        settings_content = """
DATABASE_ROUTERS = ['myapp.routers.DatabaseRouter']

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.postgresql'},
    'mariadb': {'ENGINE': 'django.db.backends.mysql'},
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(settings_content)
            f.flush()

            result = self.agent.validate_r4_database_router(f.name)
            self.assertTrue(result.passed)

            Path(f.name).unlink()

    def test_r4_detect_missing_router(self):
        """Test R4: Detect missing database router."""
        settings_content = """
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.postgresql'},
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(settings_content)
            f.flush()

            result = self.agent.validate_r4_database_router(f.name)
            self.assertFalse(result.passed)

            Path(f.name).unlink()

    def test_r4_validate_router_class_exists(self):
        """Test R4: Validate router class file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create settings with router reference
            settings_file = tmppath / "settings.py"
            settings_file.write_text("DATABASE_ROUTERS = ['myapp.routers.DatabaseRouter']")

            # Create router file
            router_dir = tmppath / "myapp"
            router_dir.mkdir()
            (router_dir / "__init__.py").write_text("")
            (router_dir / "routers.py").write_text("class DatabaseRouter: pass")

            result = self.agent.validate_r4_database_router(
                str(settings_file),
                project_root=str(tmppath)
            )
            self.assertTrue(result.passed)


class TestR5TestOrchestration(unittest.TestCase):
    """Test R5: Test execution orchestration."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    @patch("subprocess.run")
    def test_r5_execute_tests_success(self, mock_run):
        """Test R5: Execute tests successfully."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="100 passed",
        )

        result = self.agent.validate_r5_tests_pass()
        self.assertTrue(result.passed)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_r5_execute_tests_failure(self, mock_run):
        """Test R5: Detect test failures."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="5 failed, 95 passed",
        )

        result = self.agent.validate_r5_tests_pass()
        self.assertFalse(result.passed)
        self.assertGreater(len(result.violations), 0)

    @patch("subprocess.run")
    def test_r5_handle_test_timeout(self, mock_run):
        """Test R5: Handle test execution timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=300)

        result = self.agent.validate_r5_tests_pass()
        self.assertFalse(result.passed)
        self.assertTrue(any("timed out" in v.message.lower() for v in result.violations))


class TestR6DevContainerValidation(unittest.TestCase):
    """Test R6: DevContainer environment validation integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_r6_calls_devcontainer_validator(self):
        """Test R6: Calls DevContainerValidatorAgent."""
        with patch.object(self.agent, "_call_devcontainer_validator") as mock_validator:
            mock_validator.return_value = {
                "valid": True,
                "checks": [],
            }

            result = self.agent.validate_r6_devcontainer_compatibility()

            mock_validator.assert_called_once()
            self.assertTrue(result.passed)

    def test_r6_detects_invalid_environment(self):
        """Test R6: Detect invalid DevContainer environment."""
        with patch.object(self.agent, "_call_devcontainer_validator") as mock_validator:
            mock_validator.return_value = {
                "valid": False,
                "checks": [
                    {
                        "check": "postgresql_service",
                        "status": "failed",
                        "message": "PostgreSQL service not running",
                    }
                ],
            }

            result = self.agent.validate_r6_devcontainer_compatibility()

            self.assertFalse(result.passed)
            self.assertGreater(len(result.violations), 0)


class TestValidationModes(unittest.TestCase):
    """Test different validation modes."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_mode_pre_commit_validates_r2_only(self):
        """Test pre-commit mode validates only R2 (emojis)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            test_file = tmppath / "test.md"
            test_file.write_text("Clean content")

            result = self.agent.validate(
                mode=ValidationMode.PRE_COMMIT,
                changed_files=[str(test_file)]
            )

            # Should only check R2
            self.assertIn("R2", result.rules_evaluated)
            self.assertNotIn("R5", result.rules_evaluated)

    def test_mode_pre_push_validates_multiple_rules(self):
        """Test pre-push mode validates R1, R3, R4, R5."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="feature/test\n")

            result = self.agent.validate(
                mode=ValidationMode.PRE_PUSH,
                changed_files=[]
            )

            # Should check R1, R3, R4, R5 (not R2, R6)
            self.assertIn("R1", result.rules_evaluated)
            self.assertNotIn("R2", result.rules_evaluated)

    def test_mode_ci_local_validates_all_rules(self):
        """Test ci-local mode validates all rules."""
        with patch.multiple(
            self.agent,
            validate_r1_branch_protection=Mock(return_value=Mock(passed=True, violations=[])),
            validate_r2_no_emojis=Mock(return_value=Mock(passed=True, violations=[])),
            validate_r3_ui_api_coherence=Mock(return_value=Mock(passed=True, violations=[])),
            validate_r4_database_router=Mock(return_value=Mock(passed=True, violations=[])),
            validate_r5_tests_pass=Mock(return_value=Mock(passed=True, violations=[])),
            validate_r6_devcontainer_compatibility=Mock(return_value=Mock(passed=True, violations=[])),
        ):
            result = self.agent.validate(
                mode=ValidationMode.CI_LOCAL,
                changed_files=[]
            )

            # Should check all rules
            self.assertEqual(len(result.rules_evaluated), 6)


class TestExitCodes(unittest.TestCase):
    """Test exit codes."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_exit_code_0_on_success(self):
        """Test exit code 0 on successful validation."""
        result = ValidationResult(
            passed=True,
            violations=[],
            rules_evaluated=["R1", "R2"],
        )
        exit_code = self.agent.get_exit_code(result)
        self.assertEqual(exit_code, 0)

    def test_exit_code_1_on_error(self):
        """Test exit code 1 on blocking errors."""
        result = ValidationResult(
            passed=False,
            violations=[
                Violation(
                    rule_id="R2",
                    severity=ViolationSeverity.ERROR,
                    message="Emoji detected",
                    file="test.md",
                    line=1,
                )
            ],
            rules_evaluated=["R2"],
        )
        exit_code = self.agent.get_exit_code(result)
        self.assertEqual(exit_code, 1)

    def test_exit_code_2_on_warning(self):
        """Test exit code 2 on warnings only."""
        result = ValidationResult(
            passed=True,
            violations=[
                Violation(
                    rule_id="R3",
                    severity=ViolationSeverity.WARNING,
                    message="Potential coherence issue",
                    file="api/views.py",
                    line=10,
                )
            ],
            rules_evaluated=["R3"],
        )
        exit_code = self.agent.get_exit_code(result)
        self.assertEqual(exit_code, 2)

    def test_exit_code_3_on_config_error(self):
        """Test exit code 3 on configuration error."""
        # Test the main() method which returns exit code 3 on config error
        with patch.object(self.agent, "parse_cli_args", side_effect=Exception("Config error")):
            exit_code = self.agent.main(["--mode", "manual"])
            self.assertEqual(exit_code, 3)


class TestJSONOutput(unittest.TestCase):
    """Test JSON output formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_json_output_structure(self):
        """Test JSON output has correct structure."""
        result = ValidationResult(
            passed=False,
            violations=[
                Violation(
                    rule_id="R2",
                    severity=ViolationSeverity.ERROR,
                    message="Emoji detected",
                    file="test.md",
                    line=5,
                )
            ],
            rules_evaluated=["R1", "R2"],
        )

        json_output = self.agent.to_json(result)
        data = json.loads(json_output)

        self.assertIn("status", data)
        self.assertIn("violations", data)
        self.assertIn("summary", data)
        self.assertEqual(data["status"], "failure")

    def test_json_violations_format(self):
        """Test JSON violations format."""
        result = ValidationResult(
            passed=False,
            violations=[
                Violation(
                    rule_id="R2",
                    severity=ViolationSeverity.ERROR,
                    message="Emoji detected: ✓",
                    file="docs/test.md",
                    line=42,
                )
            ],
            rules_evaluated=["R2"],
        )

        json_output = self.agent.to_json(result)
        data = json.loads(json_output)

        violation = data["violations"][0]
        self.assertEqual(violation["rule_id"], "R2")
        self.assertEqual(violation["severity"], "error")
        self.assertEqual(violation["file"], "docs/test.md")
        self.assertEqual(violation["line"], 42)

    def test_json_summary_calculations(self):
        """Test JSON summary calculations."""
        result = ValidationResult(
            passed=False,
            violations=[
                Violation("R1", ViolationSeverity.ERROR, "Error 1", "file1.py", 1),
                Violation("R2", ViolationSeverity.ERROR, "Error 2", "file2.md", 1),
            ],
            rules_evaluated=["R1", "R2", "R3"],
        )

        json_output = self.agent.to_json(result)
        data = json.loads(json_output)

        summary = data["summary"]
        self.assertEqual(summary["rules_evaluated"], 3)
        self.assertEqual(summary["rules_passed"], 1)
        self.assertEqual(summary["rules_failed"], 2)
        self.assertTrue(summary["blocking"])


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_parse_args_mode(self):
        """Test parsing --mode argument."""
        agent = ConstitutionValidatorAgent()
        args = agent.parse_cli_args([
            "--mode", "pre-commit",
        ])
        self.assertEqual(args.mode, "pre-commit")

    def test_parse_args_config_file(self):
        """Test parsing --config argument."""
        agent = ConstitutionValidatorAgent()
        args = agent.parse_cli_args([
            "--mode", "manual",
            "--config", "/path/to/.constitucion.yaml",
        ])
        self.assertEqual(args.config, "/path/to/.constitucion.yaml")

    def test_parse_args_output_file(self):
        """Test parsing --output argument."""
        agent = ConstitutionValidatorAgent()
        args = agent.parse_cli_args([
            "--mode", "pre-push",
            "--output", "/tmp/report.json",
        ])
        self.assertEqual(args.output, "/tmp/report.json")

    def test_parse_args_changed_files(self):
        """Test parsing --changed-files argument."""
        agent = ConstitutionValidatorAgent()
        args = agent.parse_cli_args([
            "--mode", "pre-commit",
            "--changed-files", "file1.py,file2.md,file3.txt",
        ])
        self.assertEqual(args.changed_files, "file1.py,file2.md,file3.txt")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ConstitutionValidatorAgent()

    def test_empty_changed_files(self):
        """Test validation with empty changed files list."""
        result = self.agent.validate(
            mode=ValidationMode.PRE_COMMIT,
            changed_files=[]
        )
        self.assertTrue(result.passed)

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        result = self.agent.validate_r2_no_emojis(["/nonexistent/file.md"])
        # Should handle gracefully without crashing
        self.assertIsNotNone(result)

    def test_binary_file_handling(self):
        """Test handling of binary files."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(b"\x00\x01\x02\x03")
            f.flush()

            # Should skip binary files
            violations = self.agent.detect_emojis_in_content_from_file(f.name)
            Path(f.name).unlink()

            # Binary files should be skipped or handled gracefully
            self.assertIsNotNone(violations)

    def test_large_file_handling(self):
        """Test handling of large files efficiently."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Write 10000 lines
            for i in range(10000):
                f.write(f"Line {i}\n")
            f.flush()

            violations = self.agent.detect_emojis_in_content_from_file(f.name)
            Path(f.name).unlink()

            self.assertEqual(len(violations), 0)

    def test_unicode_handling_in_paths(self):
        """Test handling of Unicode characters in file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with Unicode in path
            tmppath = Path(tmpdir)
            unicode_dir = tmppath / "测试"
            unicode_dir.mkdir()
            test_file = unicode_dir / "test.md"
            test_file.write_text("Normal content", encoding='utf-8')

            violations = self.agent.detect_emojis_in_content_from_file(str(test_file))
            self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
