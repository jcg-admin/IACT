import os
import pathlib
import re


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "install_prebuilt_cpython.sh"


def require_script_text() -> str:
    if not SCRIPT_PATH.exists():
        raise AssertionError("install_prebuilt_cpython.sh is missing; expected by bootstrap symlink step")
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_install_script_exists_and_is_executable():
    assert SCRIPT_PATH.exists(), "install_prebuilt_cpython.sh must exist in scripts/"
    assert os.access(SCRIPT_PATH, os.X_OK), "install_prebuilt_cpython.sh should be executable"


def test_install_script_contains_expected_commands():
    script_text = require_script_text()

    assert "wget" in script_text and "cpython-3.12.6-ubuntu20.04-build1.tgz" in script_text
    assert 'tar -xzf "$TMP_ARTIFACT"' in script_text, "Script should extract the downloaded artifact"
    assert "--strip-components=1" in script_text, "Extraction should strip the top-level directory"
    assert re.search(r'bin/python3"?\s+--version', script_text), "Script must verify the installed Python version"


def test_install_script_defaults_are_configurable():
    script_text = require_script_text()

    version_match = re.search(r"PYTHON_VERSION_DEFAULT=\"([^\"]+)\"", script_text)
    build_match = re.search(r"BUILD_ID_DEFAULT=\"([^\"]+)\"", script_text)
    url_match = re.search(r"ARTIFACT_BASE_URL_DEFAULT=\"([^\"]+)\"", script_text)

    assert version_match, "Default Python version variable missing"
    assert build_match, "Default build id variable missing"
    assert url_match, "Default artifact base URL missing"

    assert version_match.group(1) == "3.12.6"
    assert build_match.group(1) == "build1"
    assert "github.com/2-Coatl/IACT---project/releases" in url_match.group(1)


def test_install_script_sources_shared_logging():
    script_text = require_script_text()

    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"' in script_text, "Script should resolve SCRIPT_DIR for sourcing utils"
    assert 'source "$SCRIPT_DIR/utils/logging.sh"' in script_text, "Script must reuse shared logging utilities"
    assert "log_info() {" not in script_text, "Script should rely on shared logging helpers instead of redefining them"
