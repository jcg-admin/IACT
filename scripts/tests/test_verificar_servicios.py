import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "verificar_servicios.sh"


def _run_script(*args, extra_env=None):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    bash_path = os.environ.get("BASH", "/bin/bash")
    result = subprocess.run(
        [bash_path, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return result


def test_help_displays_usage_information():
    result = _run_script("--help")
    assert result.returncode == 0
    assert "Script: verificar servicios" in result.stdout
    assert "--dry-run" in result.stdout


def test_dry_run_succeeds_and_mentions_pending_checks():
    result = _run_script("--dry-run")
    assert result.returncode == 0
    stdout = result.stdout
    assert "[DRY-RUN]" in stdout
    assert "PostgreSQL" in stdout
    assert "MariaDB" in stdout


def test_handles_missing_clients_gracefully():
    result = _run_script("--postgres-host", "127.0.0.1", extra_env={"PATH": ""})
    assert result.returncode != 0
    assert "[ERROR] Cliente psql no encontrado" in result.stdout
    assert "[ERROR] Cliente mysql no encontrado" in result.stdout
