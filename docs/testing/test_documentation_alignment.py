"""Tests de consistencia documental para proteger los ajustes de la revisión 2025-11-12."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_acknowledges_absence_of_root_makefile():
    readme = _read(REPO_ROOT / "README.md")
    assert "No existe un Makefile en la raíz" in readme
    assert "docs/operaciones/verificar_servicios.md" in readme
    assert "./scripts/verificar_servicios.sh" in readme
    assert "[IMPLEMENTADO]" in readme
    assert "make docs-serve" not in readme


def test_docs_index_and_stubs_are_canonical():
    index = _read(REPO_ROOT / "docs/index.md")
    assert "## [DOCS] Documentación activa" in index
    assert "## [LEGADO] Contenido legado" in index

    index_stub = _read(REPO_ROOT / "docs/INDEX.md")
    indice_stub = _read(REPO_ROOT / "docs/INDICE.md")
    expected = "Consulta el índice consolidado en [index.md](index.md)."
    assert expected in index_stub
    assert expected in indice_stub


def test_scripts_documentation_reflects_current_inventory():
    scripts_readme = _read(REPO_ROOT / "scripts/README.md")
    assert "Cualquier referencia anterior a `scripts/requisitos/`" in scripts_readme
    assert "validation/" in scripts_readme
    assert "validacion/" in scripts_readme

    docs_scripts = _read(REPO_ROOT / "docs/scripts/README.md")
    assert "No existen scripts como `scripts/sdlc_agent.py`" in docs_scripts
    assert "scripts/ci" in docs_scripts


def test_logs_and_analysis_documentation_are_updated():
    schema = _read(REPO_ROOT / "logs_data/SCHEMA.md")
    assert "Automatización parcial" in schema
    assert "scripts/dora_metrics.py" in schema

    analyzer = _read(REPO_ROOT / "scripts/analyze_backend.py")
    assert "logs_data/analysis/backend_analysis_results.json" in analyzer


def test_run_all_tests_targets_ui_directory():
    script = _read(REPO_ROOT / "scripts/run_all_tests.sh")
    assert "UI_DIR" in script
    assert "FRONTEND_DIR" not in script


def test_cpython_install_script_renamed():
    renamed_path = REPO_ROOT / "infrastructure/cpython/scripts/install_prebuilt_cpython.sh"
    assert renamed_path.exists()
