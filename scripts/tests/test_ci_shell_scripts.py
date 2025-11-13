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


def test_run_all_checks_reports_summary_even_on_failure():
    result = _run_script(RUN_ALL_CHECKS)

    assert result.returncode != 0, "Expected the aggregated checks to fail in the default dev environment"
    combined_output = f"{result.stdout}\\n{result.stderr}"
    assert "FINAL CI/CD REPORT" in combined_output


def test_health_check_surfaces_underlying_error_details():
    result = _run_script(HEALTH_CHECK)

    assert result.returncode != 0, "The health check should fail when dependencies are missing"
    combined_output = f"{result.stdout}\\n{result.stderr}"
    assert "ModuleNotFoundError" in combined_output or "No module named" in combined_output


def test_run_all_checks_sets_strict_shell_flags():
    contents = RUN_ALL_CHECKS.read_text()

    assert "set -euo pipefail" in contents, "run-all-checks.sh must opt into strict shell error handling"
