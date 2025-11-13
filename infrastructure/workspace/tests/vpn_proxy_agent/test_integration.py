"""Integration-level tests for MCP server wiring."""

from __future__ import annotations

import asyncio
import json


def test_mcp_server_lists_and_calls_tools(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent import mcp_server

    class DummyTools:
        async def setup_tunnel(self, **kwargs):
            return {"success": True, "details": kwargs}

        async def check_tunnel_status(self):
            return {"status": {"is_active": True}}

    monkeypatch.setattr(mcp_server, "tools", DummyTools())

    tools = asyncio.run(mcp_server.list_tools())
    names = {tool.name for tool in tools}
    assert "setup_tunnel" in names

    response = asyncio.run(
        mcp_server.call_tool("setup_tunnel", {"host": "vpn", "username": "alice", "key_path": "/tmp/key"})
    )
    payload = json.loads(response[0].text)
    assert payload["success"] is True
