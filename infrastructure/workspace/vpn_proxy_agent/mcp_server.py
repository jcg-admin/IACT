"""Model Context Protocol server entry point for the VPN/Proxy agent."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List

from .mcp_tools import VPNProxyTools


@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class TextContent:
    type: str
    text: str


class Server:
    """Minimal decorator-based stub compatible with the tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._list_tools_handler: Callable[[], Awaitable[List[Tool]]]
        self._call_tool_handler: Callable[[str, Dict[str, Any]], Awaitable[List[TextContent]]]

    def list_tools(self) -> Callable[[Callable[[], Awaitable[List[Tool]]]], Callable[[], Awaitable[List[Tool]]]]:
        def decorator(func):
            self._list_tools_handler = func
            return func

        return decorator

    def call_tool(self) -> Callable[[Callable[[str, Dict[str, Any]], Awaitable[List[TextContent]]]], Callable[[str, Dict[str, Any]], Awaitable[List[TextContent]]]]:
        def decorator(func):
            self._call_tool_handler = func
            return func

        return decorator

    async def run(self, *args, **kwargs):  # pragma: no cover - full server run not exercised in tests
        raise NotImplementedError("Full MCP server run is out of scope for tests")

    def create_initialization_options(self):  # pragma: no cover - placeholder
        return {}


class _UnconfiguredTools:
    async def __getattr__(self, item):  # pragma: no cover - guardrail
        raise RuntimeError("VPNProxyTools instance not configured")


server = Server("vpn-proxy-agent")
tools: VPNProxyTools | _UnconfiguredTools = _UnconfiguredTools()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="setup_tunnel",
            description="Setup SSH SOCKS5 tunnel for API access",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "default": 1080},
                    "username": {"type": "string"},
                    "key_path": {"type": "string"},
                },
                "required": ["host", "username", "key_path"],
            },
        ),
        Tool(
            name="check_tunnel_status",
            description="Check current tunnel status",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="stop_tunnel",
            description="Stop active SSH tunnel",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="diagnose_system",
            description="Run complete system diagnostics",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_ssh_key",
            description="Generate SSH key pair",
            inputSchema={
                "type": "object",
                "properties": {
                    "key_name": {"type": "string", "default": "vpn_key"},
                    "key_type": {"type": "string", "enum": ["ed25519", "rsa"], "default": "ed25519"},
                },
            },
        ),
        Tool(
            name="test_connectivity",
            description="Test API connectivity through tunnel",
            inputSchema={
                "type": "object",
                "properties": {
                    "proxy_url": {"type": "string"},
                    "api_urls": {"type": "array", "items": {"type": "string"}},
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if isinstance(tools, _UnconfiguredTools):
        raise RuntimeError("VPNProxyTools instance not configured")

    if name == "setup_tunnel":
        result = await tools.setup_tunnel(**arguments)
    elif name == "check_tunnel_status":
        result = await tools.check_tunnel_status()
    elif name == "stop_tunnel":
        result = await tools.stop_tunnel()
    elif name == "diagnose_system":
        result = await tools.diagnose_system()
    elif name == "generate_ssh_key":
        result = await tools.generate_ssh_key(**arguments)
    elif name == "test_connectivity":
        result = await tools.test_connectivity(**arguments)
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:  # pragma: no cover - CLI helper
    await server.run()


__all__ = ["server", "tools", "list_tools", "call_tool", "Tool", "TextContent", "main"]
