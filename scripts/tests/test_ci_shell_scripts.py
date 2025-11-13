import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ALL_CHECKS = REPO_ROOT / "scripts" / "ci" / "run-all-checks.sh"
HEALTH_CHECK = REPO_ROOT / "scripts" / "ci" / "infrastructure" / "health-check.sh"


def _run_script(script_path, *args):
    return subprocess.run(
        ["bash", str(script_path), *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_run_all_checks_reports_summary_with_skips():
    result = _run_script(RUN_ALL_CHECKS)

    assert result.returncode == 0, "Aggregated checks should degrade to success with skips locally"
    combined_output = f"{result.stdout}\\n{result.stderr}"
    assert "FINAL CI/CD REPORT" in combined_output
    assert "Skipped:" in combined_output
    assert "[SKIP]" in combined_output or "Skipped: 0" in combined_output


def test_health_check_degrades_gracefully_when_django_missing():
    result = _run_script(HEALTH_CHECK)

    assert result.returncode in (0, 2), "Health check should pass or skip when Django is unavailable"
    combined_output = f"{result.stdout}\\n{result.stderr}"
    assert "Skipping Django checks" in combined_output


def test_run_all_checks_sets_strict_shell_flags():
    contents = RUN_ALL_CHECKS.read_text()

    assert "set -euo pipefail" in contents, "run-all-checks.sh must opt into strict shell error handling"
