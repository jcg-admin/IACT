import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ALL_CHECKS = REPO_ROOT / "scripts" / "ci" / "run-all-checks.sh"
HEALTH_CHECK = REPO_ROOT / "scripts" / "ci" / "infrastructure" / "health-check.sh"
BANDIT_SCAN = REPO_ROOT / "scripts" / "ci" / "security" / "bandit-scan.sh"
NPM_AUDIT = REPO_ROOT / "scripts" / "ci" / "security" / "npm-audit.sh"
TEST_EXECUTION_TIME = REPO_ROOT / "scripts" / "ci" / "testing" / "test-execution-time.sh"


def _run_script(script_path, *args, env=None, timeout=60):
    return subprocess.run(
        ["bash", str(script_path), *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        timeout=timeout,
    )


def test_run_all_checks_reports_summary_with_skips():
    result = _run_script(RUN_ALL_CHECKS)

    assert result.returncode == 0, "Aggregated checks should degrade to success with skips locally"
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "FINAL CI/CD REPORT" in combined_output
    assert "Skipped:" in combined_output
    assert "[SKIP]" in combined_output or "Skipped: 0" in combined_output


def test_health_check_degrades_gracefully_when_django_missing():
    result = _run_script(HEALTH_CHECK)

    assert result.returncode in (0, 2), "Health check should pass or skip when Django is unavailable"
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Skipping Django checks" in combined_output


def test_run_all_checks_sets_strict_shell_flags():
    contents = RUN_ALL_CHECKS.read_text()

    assert "set -euo pipefail" in contents, "run-all-checks.sh must opt into strict shell error handling"


def test_bandit_scan_skips_quickly_when_cli_missing():
    result = _run_script(BANDIT_SCAN, timeout=5)

    assert result.returncode == 2, "Bandit scan should degrade to SKIP without attempting long installations"
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Bandit CLI not detected" in combined_output or "Bandit not installed" in combined_output


def test_npm_audit_detects_ui_workspace_and_skips_without_npm():
    env = os.environ.copy()
    env["PATH"] = ":".join(
        [
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
        ]
    )

    result = _run_script(NPM_AUDIT, env=env, timeout=30)

    assert result.returncode == 2, "NPM audit should skip when npm CLI is not available"
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Found package.json in ui" in combined_output
    assert "npm CLI not available" in combined_output or "npm not installed" in combined_output


def test_test_execution_time_skips_without_django():
    result = _run_script(TEST_EXECUTION_TIME, timeout=20)

    assert result.returncode == 2, "Test execution validation should skip when Django is absent"
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Skipping test execution time validation" in combined_output
