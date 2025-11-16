"""Tests for the MCP registry builder mirroring the Copilot log."""

import importlib.machinery
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
CODING_ROOT = SCRIPTS_ROOT / "coding"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_ROOT))
sys.path.insert(0, str(CODING_ROOT))

namespace_paths = [str(SCRIPTS_ROOT), str(CODING_ROOT)]
scripts_pkg = ModuleType("scripts")
scripts_pkg.__package__ = "scripts"
scripts_pkg.__path__ = namespace_paths
scripts_pkg.__spec__ = importlib.machinery.ModuleSpec(
    name="scripts",
    loader=None,
    is_package=True,
)
sys.modules.setdefault("scripts", scripts_pkg)


@pytest.fixture(name="registry_module")
def _registry_module():
    return __import__("scripts.coding.ai.mcp.registry", fromlist=["*"])


def test_default_registry_declares_remote_servers(registry_module):
    registry = registry_module.build_default_registry()

    remote_names = [server.name for server in registry.remote_servers]
    assert remote_names == ["blackbird-mcp-server", "github-mcp-server"]
    assert {server.url for server in registry.remote_servers} == {
        "https://api.githubcopilot.com/mcp/readonly"
    }
    assert all(server.mode == "readonly" for server in registry.remote_servers)


def test_playwright_server_configuration_matches_reference_log(registry_module):
    registry = registry_module.build_default_registry()
    local_servers = {server.name: server for server in registry.local_servers}
    playwright = local_servers["playwright"]

    assert playwright.command == "npx"
    assert playwright.viewport_size == (1280, 720)
    assert playwright.output_dir == "/tmp/playwright-logs"
    assert "@playwright/mcp@0.0.40" in playwright.args
    assert "--allowed-origins" in playwright.args
    assert "localhost;localhost:*;127.0.0.1;127.0.0.1:*" in playwright.args


def test_registry_cli_config_serializes_servers(registry_module):
    registry = registry_module.build_default_registry()
    cli_config = registry.as_cli_config()

    assert "remote" in cli_config and "local" in cli_config
    assert cli_config["remote"]["github-mcp-server"]["url"].startswith("https://")
    assert cli_config["local"]["playwright"]["command"] == "npx"
    assert cli_config["local"]["playwright"]["args"][0] == "@playwright/mcp@0.0.40"
    assert "memory_profiles" in cli_config
    assert "github-mcp-server" in cli_config["memory_profiles"]
