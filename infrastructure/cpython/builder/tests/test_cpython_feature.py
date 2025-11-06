"""
Integration tests for CPython Prebuilt Dev Container Feature

Reference: SPEC-INFRA-001
"""

import json
import os
import stat
from pathlib import Path

import pytest

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Feature directory (now within builder)
FEATURE_DIR = BASE_DIR / "infrastructure" / "cpython" / "builder" / "feature"


@pytest.mark.critical
def test_feature_directory_exists():
    """Verifica que el directorio de la feature existe."""
    assert FEATURE_DIR.exists(), f"Feature directory {FEATURE_DIR} does not exist"
    assert FEATURE_DIR.is_dir(), f"{FEATURE_DIR} is not a directory"


@pytest.mark.critical
def test_devcontainer_feature_json_exists():
    """Verifica que devcontainer-feature.json existe y es valido."""
    feature_json = FEATURE_DIR / "devcontainer-feature.json"

    assert feature_json.exists(), "devcontainer-feature.json not found"

    # Parse JSON
    with open(feature_json) as f:
        data = json.load(f)

    # Verify required fields
    assert "id" in data, "Missing 'id' field"
    assert data["id"] == "cpython-prebuilt", f"Invalid id: {data['id']}"

    assert "version" in data, "Missing 'version' field"
    assert data["version"] == "1.0.0", f"Invalid version: {data['version']}"

    assert "name" in data, "Missing 'name' field"
    assert "description" in data, "Missing 'description' field"

    assert "options" in data, "Missing 'options' field"
    options = data["options"]

    # Verify option structure
    assert "version" in options, "Missing 'version' option"
    assert "artifactUrl" in options, "Missing 'artifactUrl' option"
    assert "checksumUrl" in options, "Missing 'checksumUrl' option"
    assert "installPrefix" in options, "Missing 'installPrefix' option"
    assert "skipValidation" in options, "Missing 'skipValidation' option"

    # Verify defaults
    assert options["version"]["default"] == "3.12.6"
    assert options["installPrefix"]["default"] == "/opt/python"
    assert options["skipValidation"]["default"] is False


@pytest.mark.critical
def test_install_sh_exists_and_executable():
    """Verifica que install.sh existe y es ejecutable."""
    install_sh = FEATURE_DIR / "install.sh"

    assert install_sh.exists(), "install.sh not found"
    assert install_sh.is_file(), "install.sh is not a file"

    # Check if executable
    st = os.stat(install_sh)
    is_executable = bool(st.st_mode & stat.S_IXUSR)
    assert is_executable, "install.sh is not executable"


def test_readme_exists():
    """Verifica que README.md existe."""
    readme = FEATURE_DIR / "README.md"
    assert readme.exists(), "README.md not found"


@pytest.mark.critical
def test_install_sh_has_shebang():
    """Verifica que install.sh tiene shebang correcto."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        first_line = f.readline().strip()

    assert first_line == "#!/bin/bash", f"Invalid shebang: {first_line}"


@pytest.mark.critical
def test_install_sh_has_set_e():
    """Verifica que install.sh tiene 'set -e' para fail-fast."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "set -e" in content, "Missing 'set -e' in install.sh"


def test_install_sh_has_idempotency_check():
    """Verifica que install.sh tiene deteccion de idempotencia."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "check_if_installed" in content or "MARKER_FILE" in content, \
        "Missing idempotency check in install.sh"
    assert ".installed" in content, "Missing .installed marker file logic"


def test_install_sh_has_checksum_validation():
    """Verifica que install.sh valida checksums SHA256."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "sha256sum" in content or "SHA256" in content, \
        "Missing SHA256 validation in install.sh"
    assert "validate_checksum" in content or "CHECKSUM" in content, \
        "Missing checksum validation function"


def test_install_sh_has_module_validation():
    """Verifica que install.sh valida modulos nativos."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    # Check for critical modules
    modules = ["ssl", "sqlite3", "uuid", "lzma", "bz2", "zlib", "ctypes"]
    for module in modules:
        assert module in content, f"Missing validation for module '{module}'"


def test_install_sh_has_spec_reference():
    """Verifica que install.sh referencia SPEC-INFRA-001."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "SPEC-INFRA-001" in content, "Missing SPEC-INFRA-001 reference"


@pytest.mark.critical
def test_feature_files_no_emojis():
    """Verifica que archivos de feature no contienen emojis."""
    files_to_check = [
        FEATURE_DIR / "install.sh",
        FEATURE_DIR / "devcontainer-feature.json",
        FEATURE_DIR / "README.md",
    ]

    # Common emoji characters
    emoji_chars = [
        '\u2705',  # checkmark
        '\u274C',  # cross mark
        '\U0001F680',  # rocket
        '\u26A0',  # warning
        '\U0001F4E6',  # package
        '\U0001F527',  # wrench
    ]

    for file_path in files_to_check:
        if file_path.exists():
            content = file_path.read_text()
            for emoji in emoji_chars:
                assert emoji not in content, \
                    f"Emoji {emoji} found in {file_path.name}"


def test_install_sh_downloads_artifact():
    """Verifica que install.sh descarga artefactos."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    # Check for download commands
    assert ("wget" in content or "curl" in content), \
        "Missing download command (wget or curl)"
    assert "download" in content.lower(), \
        "Missing download functionality"


def test_install_sh_creates_symlinks():
    """Verifica que install.sh crea symlinks."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "ln -s" in content or "symlink" in content.lower(), \
        "Missing symlink creation"
    assert "/usr/local/bin" in content, \
        "Missing symlinks to /usr/local/bin"


def test_install_sh_configures_ld():
    """Verifica que install.sh configura shared libraries."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "ldconfig" in content, "Missing ldconfig command"
    assert "/etc/ld.so.conf.d" in content, \
        "Missing /etc/ld.so.conf.d configuration"


def test_readme_has_usage_examples():
    """Verifica que README tiene ejemplos de uso."""
    readme = FEATURE_DIR / "README.md"

    with open(readme) as f:
        content = f.read()

    assert "Usage" in content or "Uso" in content, "Missing usage section"
    assert "devcontainer.json" in content, "Missing devcontainer.json examples"
    assert "features" in content, "Missing features configuration example"


def test_readme_has_security_section():
    """Verifica que README documenta seguridad."""
    readme = FEATURE_DIR / "README.md"

    with open(readme) as f:
        content = f.read()

    assert "Security" in content or "Seguridad" in content, \
        "Missing security section"
    assert "SHA256" in content or "checksum" in content, \
        "Missing checksum documentation"


def test_readme_has_troubleshooting():
    """Verifica que README tiene troubleshooting."""
    readme = FEATURE_DIR / "README.md"

    with open(readme) as f:
        content = f.read()

    assert "Troubleshooting" in content or "Solución" in content, \
        "Missing troubleshooting section"


def test_feature_has_all_required_files():
    """Verifica que feature tiene todos los archivos requeridos."""
    required_files = [
        "devcontainer-feature.json",
        "install.sh",
        "README.md",
    ]

    for filename in required_files:
        file_path = FEATURE_DIR / filename
        assert file_path.exists(), f"Missing required file: {filename}"


def test_install_sh_logging_functions():
    """Verifica que install.sh tiene funciones de logging."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    logging_functions = ["log_info", "log_error", "log_success", "log_warning"]
    for func in logging_functions:
        assert func in content, f"Missing logging function: {func}"


def test_install_sh_cleanup_function():
    """Verifica que install.sh limpia archivos temporales."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    assert "cleanup" in content.lower(), "Missing cleanup function"
    assert "TEMP_DIR" in content or "/tmp" in content, \
        "Missing temporary directory handling"


def test_devcontainer_feature_json_vscode_extensions():
    """Verifica que feature recomienda extensiones de VS Code."""
    feature_json = FEATURE_DIR / "devcontainer-feature.json"

    with open(feature_json) as f:
        data = json.load(f)

    assert "customizations" in data, "Missing customizations"
    assert "vscode" in data["customizations"], "Missing vscode customizations"
    assert "extensions" in data["customizations"]["vscode"], \
        "Missing vscode extensions"

    extensions = data["customizations"]["vscode"]["extensions"]
    assert "ms-python.python" in extensions, \
        "Missing ms-python.python extension"


def test_install_sh_handles_local_and_remote_urls():
    """Verifica que install.sh maneja URLs locales y remotas."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    # Check for URL detection
    assert "https://" in content or "http://" in content, \
        "Missing HTTP URL handling"

    # Check for local path handling
    assert "cp " in content or "copy" in content.lower(), \
        "Missing local file copy"


@pytest.mark.critical
def test_install_sh_exit_codes():
    """Verifica que install.sh usa exit codes apropiados."""
    install_sh = FEATURE_DIR / "install.sh"

    with open(install_sh) as f:
        content = f.read()

    # Should exit with code 1 on errors
    assert "exit 1" in content, "Missing error exit codes"

    # Should exit with code 0 on success (implicit or explicit)
    assert "exit 0" in content or "idempotent" in content.lower(), \
        "Missing success path"


def test_readme_references_spec():
    """Verifica que README referencia SPEC-INFRA-001."""
    readme = FEATURE_DIR / "README.md"

    with open(readme) as f:
        content = f.read()

    assert "SPEC-INFRA-001" in content, "Missing SPEC-INFRA-001 reference"


def test_readme_license_info():
    """Verifica que README menciona licencia."""
    readme = FEATURE_DIR / "README.md"

    with open(readme) as f:
        content = f.read()

    assert "License" in content or "Licencia" in content, \
        "Missing license section"
    assert "Python Software Foundation" in content or "PSF" in content, \
        "Missing PSF license reference"
