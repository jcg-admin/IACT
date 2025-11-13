"""Structural tests ensuring workspace modules expose their test locations."""

from importlib import import_module
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def workspace_pkg():
    return import_module("infrastructure.workspace")


def test_workspace_exposes_hamilton_llm_suite(workspace_pkg):
    """The workspace package should document the canonical location of its tests."""
    suites = getattr(workspace_pkg, "TEST_SUITES")
    assert "hamilton_llm" in suites

    suite_path = Path(suites["hamilton_llm"])
    assert suite_path.parts[:3] == ("infrastructure", "workspace", "tests")
    assert suite_path.name == "hamilton_llm"


def test_workspace_exposes_language_server_suite(workspace_pkg):
    suites = getattr(workspace_pkg, "TEST_SUITES")
    key = "dev_tools_language_server"
    assert key in suites, "El registro de suites debe listar el workspace del lenguaje"

    suite_path = Path(suites[key])
    assert suite_path.parts[:4] == ("infrastructure", "workspace", "tests", "dev_tools")
    assert suite_path.exists()


def test_workspace_exposes_codex_mcp_suite(workspace_pkg):
    suites = getattr(workspace_pkg, "TEST_SUITES")
    key = "codex_mcp"
    assert key in suites, "El workspace Codex MCP debe registrarse en TEST_SUITES"

    suite_path = Path(suites[key])
    assert suite_path.parts[:3] == ("infrastructure", "workspace", "tests")
    assert suite_path.name == "codex_mcp"
    assert suite_path.exists()


def test_suite_path_points_to_existing_directory(workspace_pkg):
    suites = workspace_pkg.TEST_SUITES
    suite_path = Path(suites["hamilton_llm"])
    assert suite_path.exists(), "El workspace debe registrar un directorio real de pruebas"


def test_workspace_exports_documented_modules(workspace_pkg):
    """Ensure __all__ helps discovery tools locate available workspaces."""
    exported = set(getattr(workspace_pkg, "__all__", ()))
    assert "hamilton_llm" in exported, "El workspace Hamilton debe exponerse en __all__"
    assert "dev_tools" in exported, "Los dev tools deben estar disponibles en __all__"
    assert "codex_mcp" in exported, "El workspace Codex MCP debe exponerse en __all__"
