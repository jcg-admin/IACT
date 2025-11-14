"""Tests describing the expected Node.js tooling for the VPN/Proxy workspace.

These tests are written before the Node scaffolding exists to drive TDD.
"""

from __future__ import annotations

import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2] / "workspace"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise AssertionError(f"Expected file {path} to exist")
    return json.loads(path.read_text())


def test_package_json_contains_expected_scripts_and_dependencies() -> None:
    package_json = read_json(WORKSPACE_ROOT / "package.json")

    assert package_json["name"] == "mcp-workflows-infrastructure"
    assert package_json["type"] == "module"
    assert package_json["scripts"]["vpn:setup-dev"] == "codex mcp run setup-dev-environment"
    assert package_json["dependencies"]["codex-mcp"].startswith("^")
    assert "@modelcontextprotocol/sdk" in package_json["dependencies"]
    assert "lint:python" in package_json["scripts"]
    assert "typecheck:python" in package_json["scripts"]


def test_tsconfig_enables_esnext_modules() -> None:
    tsconfig = read_json(WORKSPACE_ROOT / "tsconfig.json")

    assert tsconfig["compilerOptions"]["module"] == "ESNext"
    assert "infrastructure/**/*.ts" in tsconfig["include"]
