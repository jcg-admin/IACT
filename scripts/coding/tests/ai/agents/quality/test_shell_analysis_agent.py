#!/usr/bin/env python3
"""
TDD Tests for ShellScriptAnalysisAgent

Test-Driven Development: Tests written FIRST, implementation SECOND.

Trazabilidad:
- Issue: FEATURE-SHELL-ANALYSIS-001
- Design: docs/sdlc_outputs/design/lld_shell_script_analysis_agent.md
- Constitution: Principle 6 (Testing y Validación)

Coverage Target: >= 90%
"""

import pytest
from pathlib import Path
import tempfile
import json

# Import the agent (will fail initially - TDD RED phase)
from scripts.coding.ai.agents.quality.shell_analysis_agent import (
    ShellScriptAnalysisAgent,
    AnalysisMode,
    Severity,
    ConsolidatedResult,
    ConstitutionalResult,
    QualityResult,
    SecurityResult,
    Violation,
    RuleResult
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_script_good():
    """Sample shell script that follows all constitutional rules."""
    return '''#!/bin/bash
set -euo pipefail

# Script purpose: Example of good shell script
# Author: Test
# Date: 2025-11-13

main() {
    local name="$1"
    echo "Hello, ${name}"
}

# Main execution
main "$@"
'''


@pytest.fixture
def sample_script_bad():
    """Sample shell script with violations."""
    return '''#!/bin/bash
# Missing set -e
# Missing documentation

function do_something() {
    name=$1  # Unquoted variable
    eval $name  # Security issue: eval
    rm -rf $temp || true  # Silent error
}

do_something
'''


@pytest.fixture
def temp_script_file(tmp_path):
    """Create temporary script file."""
    script_path = tmp_path / "test_script.sh"
    script_path.write_text("#!/bin/bash\necho 'test'\n")
    return script_path


@pytest.fixture
def agent_default():
    """Agent with default configuration."""
    return ShellScriptAnalysisAgent()


@pytest.fixture
def agent_quick_mode():
    """Agent configured for quick mode."""
    return ShellScriptAnalysisAgent(config={"analysis_depth": "quick"})


# ============================================================================
# TEST 1: INITIALIZATION
# ============================================================================

class TestAgentInitialization:
    """Test agent initialization with different configurations."""

    def test_default_initialization(self, agent_default):
        """
        Test agent initializes with default configuration.

        Given: No configuration provided
        When: ShellScriptAnalysisAgent() is called
        Then:
            - Agent name is "ShellScriptAnalysisAgent"
            - Analysis mode is STANDARD
            - Constitutional rules are [1-8]
        """
        assert agent_default.name == "ShellScriptAnalysisAgent"
        assert agent_default.analysis_mode == AnalysisMode.STANDARD
        assert agent_default.constitutional_rules == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_quick_mode_initialization(self, agent_quick_mode):
        """
        Test agent initializes in quick mode.

        Given: Config with analysis_depth="quick"
        When: Agent is initialized
        Then: Analysis mode is QUICK
        """
        assert agent_quick_mode.analysis_mode == AnalysisMode.QUICK

    def test_custom_rules_initialization(self):
        """
        Test agent initializes with custom constitutional rules.

        Given: Config with constitutional_rules=[1,3,5]
        When: Agent is initialized
        Then: Only rules 1, 3, 5 are checked
        """
        agent = ShellScriptAnalysisAgent(config={"constitutional_rules": [1, 3, 5]})
        assert agent.constitutional_rules == [1, 3, 5]


# ============================================================================
# TEST 2: CONSTITUTIONAL ANALYSIS (Rule 3: Error Handling)
# ============================================================================

class TestConstitutionalRule3:
    """Test Rule 3: Explicit Error Handling validation."""

    def test_detects_missing_set_e(self, agent_default):
        """
        Test detection of missing 'set -e'.

        Given: Script without 'set -e'
        When: Constitutional analysis runs
        Then:
            - Rule 3 is NON-COMPLIANT
            - Violation: "Missing 'set -e'"
            - Severity: CRITICAL
        """
        script = "#!/bin/bash\necho 'test'\n"
        preprocessed = agent_default._preprocess(script, Path("test.sh"))
        result = agent_default._check_rule_3_error_handling(preprocessed)

        assert not result.compliant, "Should detect missing set -e"
        assert len(result.violations) > 0
        assert result.violations[0].severity == Severity.CRITICAL
        assert "set -e" in result.violations[0].description.lower()

    def test_detects_silent_errors(self, agent_default):
        """
        Test detection of silent error handling with '|| true'.

        Given: Script with '|| true' pattern
        When: Rule 3 checker runs
        Then:
            - Violation detected
            - Severity: HIGH
            - Location: specific line number
        """
        script = "#!/bin/bash\nset -e\nrm -rf /tmp/test || true\n"
        preprocessed = agent_default._preprocess(script, Path("test.sh"))
        result = agent_default._check_rule_3_error_handling(preprocessed)

        silent_error_violations = [
            v for v in result.violations
            if "|| true" in v.description
        ]
        assert len(silent_error_violations) > 0
        assert silent_error_violations[0].severity == Severity.HIGH

    def test_passes_good_error_handling(self, agent_default, sample_script_good):
        """
        Test script with proper error handling passes.

        Given: Script with 'set -euo pipefail'
        When: Rule 3 checker runs
        Then:
            - Rule 3 is COMPLIANT
            - No violations
            - Score = 100
        """
        preprocessed = agent_default._preprocess(sample_script_good, Path("good.sh"))
        result = agent_default._check_rule_3_error_handling(preprocessed)

        assert result.compliant, "Good script should pass Rule 3"
        assert result.score == 100.0
        assert len(result.violations) == 0


# ============================================================================
# TEST 3: SECURITY ANALYSIS
# ============================================================================

class TestSecurityAnalysis:
    """Test security vulnerability detection."""

    def test_detects_unquoted_variables(self, agent_default):
        """
        Test detection of unquoted variables (command injection risk).

        Given: Script with unquoted variable in command substitution
        When: Security analysis runs
        Then:
            - Issue type: "potential_command_injection"
            - CWE-78
            - Severity: HIGH
        """
        script = "#!/bin/bash\necho $(cat $file)\n"  # Unquoted $file
        preprocessed = agent_default._preprocess(script, Path("test.sh"))
        result = agent_default._analyze_security(preprocessed)

        assert len(result.issues) > 0
        cmd_injection_issues = [i for i in result.issues if i.type == "potential_command_injection"]
        assert len(cmd_injection_issues) > 0
        assert cmd_injection_issues[0].cwe_id == "CWE-78"
        assert cmd_injection_issues[0].severity == Severity.HIGH


# ============================================================================
# TEST 4: INTEGRATION (Full Analysis)
# ============================================================================

class TestFullAnalysis:
    """Test full end-to-end analysis."""

    def test_analyze_single_script(self, agent_default, temp_script_file):
        """
        Test analysis of a single script file.

        Given: Valid script file path
        When: Agent executes analysis
        Then:
            - Result is SUCCESS
            - ConsolidatedResult returned
            - All components analyzed (constitutional, quality, security)
        """
        result = agent_default.execute({
            "script_path": str(temp_script_file),
            "output_dir": tempfile.mkdtemp()
        })

        assert result.is_success(), f"Analysis failed: {result.errors}"
        assert "results" in result.data
        assert len(result.data["results"]) == 1

        analysis = result.data["results"][0]
        assert "constitutional" in analysis
        assert "quality" in analysis
        assert "security" in analysis
        assert "overall_score" in analysis

    def test_input_validation_missing_script(self, agent_default):
        """
        Test input validation for missing script path.

        Given: Input without script_path
        When: Agent validates input
        Then: Validation error returned
        """
        errors = agent_default.validate_input({})
        assert len(errors) > 0
        assert any("script_path" in error.lower() for error in errors)

    def test_input_validation_nonexistent_file(self, agent_default):
        """
        Test input validation for non-existent file.

        Given: Path to non-existent file
        When: Agent validates input
        Then: Validation error about file not found
        """
        errors = agent_default.validate_input({"script_path": "/tmp/nonexistent.sh"})
        assert len(errors) > 0
        assert any("not found" in error.lower() for error in errors)


# ============================================================================
# TEST 5: REPORT GENERATION
# ============================================================================

class TestReportGeneration:
    """Test report generation (markdown and JSON)."""

    def test_generates_individual_reports(self, agent_default, temp_script_file, tmp_path):
        """
        Test individual script report generation.

        Given: Analyzed script
        When: Report generator runs
        Then:
            - Markdown report created
            - JSON report created
            - Both contain analysis results
        """
        output_dir = tmp_path / "reports"
        result = agent_default.execute({
            "script_path": str(temp_script_file),
            "output_dir": str(output_dir)
        })

        assert result.is_success()

        # Check files were created
        script_name = temp_script_file.name
        md_report = output_dir / f"{script_name}_analysis.md"
        json_report = output_dir / f"{script_name}_analysis.json"

        assert md_report.exists(), "Markdown report should be created"
        assert json_report.exists(), "JSON report should be created"

        # Validate JSON structure
        with open(json_report) as f:
            data = json.load(f)
            assert "script_name" in data
            assert "overall_score" in data
            assert "constitutional" in data


# ============================================================================
# TEST 6: CONSTITUTION COMPLIANCE (Meta-test)
# ============================================================================

class TestConstitutionCompliance:
    """Test that agent itself follows constitution principles."""

    def test_no_emojis_in_output(self, agent_default, temp_script_file):
        """
        Test agent output contains no emojis (Constitution Principle 2).

        Given: Agent analysis execution
        When: Reports are generated
        Then: No emojis in any output
        """
        import re

        output_dir = Path(tempfile.mkdtemp())
        result = agent_default.execute({
            "script_path": str(temp_script_file),
            "output_dir": str(output_dir)
        })

        # Check markdown report
        script_name = temp_script_file.name
        md_report = output_dir / f"{script_name}_analysis.md"
        content = md_report.read_text()

        # Emoji regex
        emoji_pattern = re.compile("["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE)

        emojis = emoji_pattern.findall(content)
        assert len(emojis) == 0, f"Found emojis in output: {emojis}"

    def test_has_traceability(self):
        """
        Test agent module has traceability markers (Constitution Principle 3).

        Given: ShellScriptAnalysisAgent module
        When: Docstring is inspected
        Then: Contains traceability references (Issue, Planning, Design)
        """
        from scripts.coding.ai.agents.quality import shell_analysis_agent

        docstring = shell_analysis_agent.__doc__
        assert docstring is not None
        assert "FEATURE-SHELL-ANALYSIS-001" in docstring or "Trazabilidad" in docstring


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
