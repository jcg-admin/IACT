import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "dora_metrics.py"


def _run_command(*args, env=None):
    result = subprocess.run(
        ["python", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return result


def test_generates_json_payload_with_expected_keys():
    result = _run_command("--days", "30", "--format", "json")
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)

    for key in [
        "analysis_window",
        "deployment_frequency",
        "change_failure_rate",
        "lead_time_for_changes",
        "mean_time_to_recover",
        "notes",
    ]:
        assert key in payload

    assert payload["analysis_window"]["days"] > 0
    assert payload["deployment_frequency"]["count"] >= 0


def test_supports_markdown_output():
    result = _run_command("--days", "7", "--format", "markdown")
    assert result.returncode == 0, result.stderr

    stdout = result.stdout.strip()
    assert "# DORA Metrics Report" in stdout
    assert "Deployment frequency" in stdout


def test_docs_only_scope_is_reflected_in_output():
    result = _run_command("--days", "90", "--format", "json", "--docs-only")
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    assert payload["scope"] == "docs"
