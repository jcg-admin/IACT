"""
Tests de integración para sistema de compilación de CPython.

Referencia: SPEC_INFRA_001
Propósito: Validar infraestructura de compilación (Fase 1)
"""

import os
import re
import subprocess
from pathlib import Path

import pytest


# Paths del proyecto
BASE_DIR = Path(__file__).parent.parent.parent.parent
VAGRANT_DIR = BASE_DIR / "infrastructure" / "cpython"
SCRIPTS_INFRA_DIR = VAGRANT_DIR / "scripts"
ARTIFACTS_DIR = VAGRANT_DIR / "artifacts"


@pytest.mark.critical
def test_vagrant_directory_exists():
    """Verifica que directorio de Vagrant existe."""
    assert VAGRANT_DIR.exists(), f"Directorio Vagrant no encontrado: {VAGRANT_DIR}"
    assert VAGRANT_DIR.is_dir(), f"Vagrant path no es directorio: {VAGRANT_DIR}"


@pytest.mark.critical
def test_vagrantfile_exists():
    """Verifica que Vagrantfile existe y tiene contenido válido."""
    vagrantfile = VAGRANT_DIR / "Vagrantfile"
    assert vagrantfile.exists(), "Vagrantfile no encontrado"

    content = vagrantfile.read_text()
    assert "Vagrant.configure" in content, "Vagrantfile no tiene configuración válida"
    assert "ubuntu/focal64" in content, "Vagrantfile no usa Ubuntu 20.04"
    assert "vb.memory" in content, "Vagrantfile no configura RAM"


@pytest.mark.critical
def test_build_script_exists_and_executable():
    """Verifica que script de build existe y es ejecutable."""
    build_script = VAGRANT_DIR / "scripts" / "build_cpython.sh"
    assert build_script.exists(), "build_cpython.sh no encontrado"

    # Verificar que es ejecutable
    assert os.access(build_script, os.X_OK), "build_cpython.sh no es ejecutable"

    # Verificar contenido básico
    content = build_script.read_text()
    assert "#!/bin/bash" in content, "build_cpython.sh no tiene shebang"
    assert "PYTHON_VERSION" in content, "build_cpython.sh no maneja versión"
    assert "--enable-optimizations" in content, "build_cpython.sh no tiene PGO"


@pytest.mark.critical
def test_validate_script_exists_and_executable():
    """Verifica que script de validación existe y es ejecutable."""
    validate_script = VAGRANT_DIR / "scripts" / "validate_build.sh"
    assert validate_script.exists(), "validate_build.sh no encontrado"

    assert os.access(validate_script, os.X_OK), "validate_build.sh no es ejecutable"

    content = validate_script.read_text()
    assert "#!/bin/bash" in content, "validate_build.sh no tiene shebang"
    assert "sha256sum" in content, "validate_build.sh no valida checksum"


def test_wrapper_scripts_exist():
    """Verifica que scripts wrapper en scripts/infra/ existen."""
    build_wrapper = SCRIPTS_INFRA_DIR / "build_cpython.sh"
    validate_wrapper = SCRIPTS_INFRA_DIR / "validate-cpython.sh"

    assert build_wrapper.exists(), "Wrapper de build no encontrado"
    assert validate_wrapper.exists(), "Wrapper de validación no encontrado"

    assert os.access(build_wrapper, os.X_OK), "Wrapper de build no es ejecutable"
    assert os.access(validate_wrapper, os.X_OK), "Wrapper de validación no es ejecutable"


def test_artifacts_directory_structure():
    """Verifica estructura de directorio de artefactos."""
    assert ARTIFACTS_DIR.exists(), f"Directorio de artefactos no existe: {ARTIFACTS_DIR}"
    assert ARTIFACTS_DIR.is_dir(), "Artifacts path no es directorio"

    artifacts_md = BASE_DIR / "infrastructure" / "artifacts" / "ARTIFACTS.md"
    assert artifacts_md.exists(), "ARTIFACTS.md no encontrado"

    content = artifacts_md.read_text()
    assert "Versión" in content, "ARTIFACTS.md no tiene tabla de versiones"
    assert "SHA256" in content, "ARTIFACTS.md no documenta checksums"


def test_vagrant_readme_exists():
    """Verifica que README de Vagrant existe y tiene contenido."""
    readme = VAGRANT_DIR / "README.md"
    assert readme.exists(), "README.md de Vagrant no encontrado"

    content = readme.read_text()
    assert "CPython Builder" in content, "README no documenta propósito"
    assert "SPEC_INFRA_001" in content, "README no referencia spec"
    assert "vagrant up" in content, "README no documenta uso de Vagrant"


@pytest.mark.critical
def test_build_script_no_emojis():
    """Verifica que scripts no contienen emojis."""
    scripts_to_check = [
        VAGRANT_DIR / "scripts" / "build_cpython.sh",
        VAGRANT_DIR / "scripts" / "validate_build.sh",
        SCRIPTS_INFRA_DIR / "build_cpython.sh",
        SCRIPTS_INFRA_DIR / "validate-cpython.sh",
    ]

    for script in scripts_to_check:
        if script.exists():
            content = script.read_text()
            # Verificar caracteres ASCII extendidos comunes en emojis
            emoji_chars = ['✅', '❌', '🚀', '⚠️', '📦', '🔧']
            for emoji in emoji_chars:
                assert emoji not in content, f"Emoji {emoji} encontrado en {script.name}"


def test_makefile_has_cpython_targets():
    """Verifica que Makefile tiene targets de CPython."""
    makefile = BASE_DIR / "Makefile"
    assert makefile.exists(), "Makefile no encontrado"

    content = makefile.read_text()
    assert "build_cpython" in content, "Makefile no tiene target build_cpython"
    assert "validate-cpython" in content, "Makefile no tiene target validate-cpython"
    assert "list-artifacts" in content, "Makefile no tiene target list-artifacts"


def test_vagrant_config_resources():
    """Verifica que Vagrantfile configura recursos adecuados."""
    vagrantfile = VAGRANT_DIR / "Vagrantfile"
    content = vagrantfile.read_text()

    # Verificar RAM (debe ser al menos 2GB)
    assert "vb.memory" in content, "Vagrantfile no configura memoria"
    # Extraer valor de memoria (simple check)
    if '"4096"' in content or "'4096'" in content or "4096" in content:
        pass  # 4GB configurado correctamente
    else:
        pytest.fail("Vagrantfile no configura memoria suficiente (esperado: 4096)")

    # Verificar CPUs
    assert "vb.cpus" in content, "Vagrantfile no configura CPUs"


def test_scripts_have_error_handling():
    """Verifica que scripts tienen manejo de errores básico."""
    build_script = VAGRANT_DIR / "build_cpython.sh"
    content = build_script.read_text()

    # set -e hace que el script falle en cualquier error
    assert "set -e" in content or "set -euo pipefail" in content, \
        "build_cpython.sh no tiene manejo de errores con set -e"


def test_validate_script_checks_sha256():
    """Verifica que script de validación verifica SHA256."""
    validate_script = VAGRANT_DIR / "validate_build.sh"
    content = validate_script.read_text()

    assert "sha256sum" in content, "validate_build.sh no usa sha256sum"
    assert "-c" in content or "check" in content.lower(), \
        "validate_build.sh no verifica checksum"


def test_scripts_reference_spec():
    """Verifica que scripts referencian SPEC_INFRA_001."""
    scripts_to_check = [
        VAGRANT_DIR / "scripts" / "build_cpython.sh",
        VAGRANT_DIR / "scripts" / "validate_build.sh",
        VAGRANT_DIR / "README.md",
    ]

    for script in scripts_to_check:
        if script.exists():
            content = script.read_text()
            assert "SPEC_INFRA_001" in content, \
                f"{script.name} no referencia SPEC_INFRA_001"


def test_gitkeep_in_artifacts():
    """Verifica que .gitkeep existe en artifacts/cpython/ para versionar directorio."""
    gitkeep = ARTIFACTS_DIR / ".gitkeep"
    assert gitkeep.exists(), ".gitkeep no encontrado en artifacts/cpython/"


@pytest.mark.critical
def test_directory_structure_complete():
    """Verifica que estructura completa de directorios existe."""
    required_dirs = [
        VAGRANT_DIR,
        SCRIPTS_INFRA_DIR,
        ARTIFACTS_DIR,
        BASE_DIR / "infrastructure" / "tests",
    ]

    for dir_path in required_dirs:
        assert dir_path.exists(), f"Directorio requerido no existe: {dir_path}"


def test_devcontainer_references_checksum_artifact():
    """Verifica que el devcontainer referencia el checksum generado por el builder."""
    versions_conf = (VAGRANT_DIR / "config" / "versions.conf").read_text()

    version = re.search(r'DEFAULT_PYTHON_VERSION="([^"]+)"', versions_conf)
    build = re.search(r'DEFAULT_BUILD_NUMBER="([^"]+)"', versions_conf)
    distro = re.search(r'DISTRO="([^"]+)"', versions_conf)

    assert version, "DEFAULT_PYTHON_VERSION no definido en versions.conf"
    assert build, "DEFAULT_BUILD_NUMBER no definido en versions.conf"
    assert distro, "DISTRO no definido en versions.conf"

    python_version = version.group(1)
    build_number = build.group(1)
    distro_name = distro.group(1)

    devcontainer_contents = (BASE_DIR / ".devcontainer" / "devcontainer.json").read_text()

    expected_local_checksum = (
        f"infrastructure/cpython/artifacts/cpython-{python_version}-{distro_name}-build{build_number}.tgz.sha256"
    )
    assert (
        expected_local_checksum in devcontainer_contents
    ), "Devcontainer no referencia el checksum local generado por el builder"

    expected_release_checksum = (
        "https://github.com/2-Coatl/IACT---project/releases/download/"
        f"cpython-{python_version}-build{build_number}/cpython-{python_version}-{distro_name}-build{build_number}.tgz.sha256"
    )
    assert (
        expected_release_checksum in devcontainer_contents
    ), "Devcontainer no referencia el checksum publicado en GitHub Releases"


def test_no_compiled_artifacts_in_git():
    """Verifica que no hay artefactos compilados (.tgz) versionados en git."""
    # Verificar que .gitignore existe y excluye .tgz
    gitignore = BASE_DIR / ".gitignore"

    if gitignore.exists():
        content = gitignore.read_text()
        # Debería ignorar archivos .tgz en artifacts/
        assert "*.tgz" in content or "artifacts/" in content or "*.tar.gz" in content, \
            ".gitignore no excluye artefactos compilados"


def test_bootstrap_summary_handles_missing_toolchain_gracefully():
    """El resumen de bootstrap debe tolerar toolchain ausente."""

    bootstrap = (VAGRANT_DIR / "bootstrap.sh").read_text()

    signature = "display_summary() {"
    assert signature in bootstrap, "display_summary no definido en bootstrap.sh"

    start = bootstrap.index(signature) + len(signature)

    depth = 1
    idx = start
    while idx < len(bootstrap) and depth > 0:
        char = bootstrap[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        idx += 1

    assert depth == 0, "No se pudo extraer el cuerpo de display_summary"

    body = bootstrap[start:idx - 1]

    assert "command -v gcc" in body or 'validate_command_exists "gcc"' in body, (
        "display_summary debe verificar la disponibilidad de gcc antes de imprimir la versión"
    )
    assert "command -v make" in body or 'validate_command_exists "make"' in body, (
        "display_summary debe verificar la disponibilidad de make antes de imprimir la versión"
    )

    assert "reset_operation_state bootstrap_complete" in body, (
        "display_summary debe guiar al usuario para reejecutar bootstrap cuando falten herramientas"
    )
