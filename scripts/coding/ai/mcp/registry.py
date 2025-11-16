"""Declarative registry for Model Context Protocol servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple


@dataclass(frozen=True)
class RemoteMCPServer:
    """Metadata to connect to a remote MCP server exposed over HTTP(S)."""

    name: str
    url: str
    mode: str = "readonly"
    headers: Mapping[str, str] = field(default_factory=dict)

    def as_cli_entry(self) -> Dict[str, object]:
        payload: Dict[str, object] = {"url": self.url, "mode": self.mode}
        if self.headers:
            payload["headers"] = dict(self.headers)
        return payload


@dataclass(frozen=True)
class LocalMCPServer:
    """Metadata for spawning a local MCP server via CLI (e.g., Playwright)."""

    name: str
    command: str
    args: Tuple[str, ...]
    allowed_origins: Tuple[str, ...]
    output_dir: str
    viewport_size: Tuple[int, int]
    env: Mapping[str, str] = field(default_factory=dict)

    def as_cli_entry(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "command": self.command,
            "args": list(self.args),
            "metadata": {
                "allowed_origins": list(self.allowed_origins),
                "output_dir": self.output_dir,
                "viewport_size": self.viewport_size,
            },
        }
        if self.env:
            payload["env"] = dict(self.env)
        return payload


@dataclass(frozen=True)
class MCPRegistry:
    """Collection of remote and local MCP server definitions."""

    remote_servers: Tuple[RemoteMCPServer, ...]
    local_servers: Tuple[LocalMCPServer, ...]

    def as_cli_config(self) -> Dict[str, Dict[str, object]]:
        """Serialize registry so CLI tooling can consume it directly."""

        remote = {server.name: server.as_cli_entry() for server in self.remote_servers}
        local = {server.name: server.as_cli_entry() for server in self.local_servers}
        return {"remote": remote, "local": local}


def build_default_registry() -> MCPRegistry:
    """Build the registry that mirrors the Copilot CLI log shared by the user."""

    remote_servers = (
        RemoteMCPServer(
            name="blackbird-mcp-server",
            url="https://api.githubcopilot.com/mcp/readonly",
            mode="readonly",
        ),
        RemoteMCPServer(
            name="github-mcp-server",
            url="https://api.githubcopilot.com/mcp/readonly",
            mode="readonly",
        ),
    )

    allowed_origins = ("localhost", "localhost:*", "127.0.0.1", "127.0.0.1:*")
    allowed_origins_flag = ";".join(allowed_origins)
    viewport_size = (1280, 720)

    local_servers = (
        LocalMCPServer(
            name="playwright",
            command="npx",
            args=(
                "@playwright/mcp@0.0.40",
                "--viewport-size",
                f"{viewport_size[0]}, {viewport_size[1]}",
                "--output-dir",
                "/tmp/playwright-logs",
                "--allowed-origins",
                allowed_origins_flag,
            ),
            allowed_origins=allowed_origins,
            output_dir="/tmp/playwright-logs",
            viewport_size=viewport_size,
        ),
    )

    return MCPRegistry(remote_servers=remote_servers, local_servers=local_servers)
