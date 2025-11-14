import os
import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_cpython.sh"
DELEGATE_PATH = REPO_ROOT / "infrastructure" / "cpython" / "scripts" / "build_cpython.sh"
DELEGATE_RELATIVE = str(DELEGATE_PATH.relative_to(REPO_ROOT))


def require_script_text() -> str:
    if not SCRIPT_PATH.exists():
        raise AssertionError("Expected top-level build_cpython.sh entrypoint in scripts/")
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_build_script_entrypoint_exists_and_is_executable():
    assert SCRIPT_PATH.exists(), "scripts/build_cpython.sh should exist to match provisioning instructions"
    assert os.access(SCRIPT_PATH, os.X_OK), "scripts/build_cpython.sh must be executable"


def test_build_script_delegates_to_infrastructure_script():
    script_text = require_script_text()

    assert DELEGATE_RELATIVE in script_text, (
        "Top-level build script should reference the infrastructure delegate"
    )
    assert 'exec "$DELEGATE" "$@"' in script_text, "Top-level build script should exec into the delegate"


def test_build_script_validates_delegate_exists():
    script_text = require_script_text()

    assert '[[ ! -x "$DELEGATE" ]]' in script_text, "Script should guard against missing delegate"
    assert "exit 1" in script_text, "Script must exit non-zero when delegate is unavailable"
