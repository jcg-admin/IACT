import pathlib


CPYTHON_ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD_SCRIPT = CPYTHON_ROOT / "scripts" / "build_cpython.sh"


def require_script_text() -> str:
    assert BUILD_SCRIPT.exists(), "Expected infrastructure build script to exist"
    return BUILD_SCRIPT.read_text(encoding="utf-8")


def test_build_script_defines_module_catalog():
    script_text = require_script_text()

    assert "MODULES_TO_CHECK" in script_text, (
        "build_cpython.sh should declare MODULES_TO_CHECK to avoid unbound variable errors"
    )
    assert 'MODULES_TO_CHECK=("${CRITICAL_MODULES[@]}" "${OPTIONAL_MODULES[@]}")' in script_text, (
        "MODULES_TO_CHECK should combine critical and optional module lists"
    )


def test_build_script_avoids_local_outside_functions():
    script_text = require_script_text()

    assert "local lib_dir=\"$INSTALL_PREFIX/lib\"" not in script_text, (
        "build_cpython.sh must not use 'local' outside of functions, which breaks execution with set -e"
    )
