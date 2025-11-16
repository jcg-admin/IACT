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


def test_empty_registry_serializes_correctly(registry_module):
    """Test that an empty registry with no servers serializes to empty dicts."""
    empty_registry = registry_module.MCPRegistry(remote_servers=(), local_servers=())
    config = empty_registry.as_cli_config()
    assert config == {"remote": {}, "local": {}}


def test_remote_server_with_custom_headers(registry_module):
    """Test that RemoteMCPServer correctly serializes custom headers."""
    server = registry_module.RemoteMCPServer(
        name="test",
        url="https://test.com",
        headers={"Authorization": "Bearer token", "X-Custom-Header": "value"}
    )
    entry = server.as_cli_entry()
    assert "headers" in entry
    assert entry["headers"]["Authorization"] == "Bearer token"
    assert entry["headers"]["X-Custom-Header"] == "value"
    assert entry["url"] == "https://test.com"
    assert entry["mode"] == "readonly"


def test_remote_server_without_custom_headers(registry_module):
    """Test that RemoteMCPServer without headers doesn't include headers field."""
    server = registry_module.RemoteMCPServer(
        name="test",
        url="https://test.com"
    )
    entry = server.as_cli_entry()
    assert "headers" not in entry
    assert entry["url"] == "https://test.com"
    assert entry["mode"] == "readonly"


def test_local_server_with_custom_env_variables(registry_module):
    """Test that LocalMCPServer correctly serializes custom environment variables."""
    server = registry_module.LocalMCPServer(
        name="test-server",
        command="node",
        args=("server.js", "--port", "3000"),
        allowed_origins=("localhost",),
        output_dir="/tmp/test-logs",
        viewport_size=(1920, 1080),
        env={"NODE_ENV": "production", "DEBUG": "true"}
    )
    entry = server.as_cli_entry()
    assert "env" in entry
    assert entry["env"]["NODE_ENV"] == "production"
    assert entry["env"]["DEBUG"] == "true"
    assert entry["command"] == "node"
    assert entry["args"] == ["server.js", "--port", "3000"]


def test_local_server_without_custom_env_variables(registry_module):
    """Test that LocalMCPServer without env variables doesn't include env field."""
    server = registry_module.LocalMCPServer(
        name="test-server",
        command="node",
        args=("server.js",),
        allowed_origins=("localhost",),
        output_dir="/tmp/test-logs",
        viewport_size=(1920, 1080)
    )
    entry = server.as_cli_entry()
    assert "env" not in entry
    assert entry["command"] == "node"


def test_registry_with_mixed_empty_collections(registry_module):
    """Test registry with only remote servers (no local servers)."""
    remote_only_registry = registry_module.MCPRegistry(
        remote_servers=(
            registry_module.RemoteMCPServer(
                name="remote-test",
                url="https://example.com"
            ),
        ),
        local_servers=()
    )
    config = remote_only_registry.as_cli_config()
    assert len(config["remote"]) == 1
    assert "remote-test" in config["remote"]
    assert config["local"] == {}


def test_registry_with_only_local_servers(registry_module):
    """Test registry with only local servers (no remote servers)."""
    local_only_registry = registry_module.MCPRegistry(
        remote_servers=(),
        local_servers=(
            registry_module.LocalMCPServer(
                name="local-test",
                command="node",
                args=("test.js",),
                allowed_origins=("localhost",),
                output_dir="/tmp/test",
                viewport_size=(800, 600)
            ),
        )
    )
    config = local_only_registry.as_cli_config()
    assert config["remote"] == {}
    assert len(config["local"]) == 1
    assert "local-test" in config["local"]
