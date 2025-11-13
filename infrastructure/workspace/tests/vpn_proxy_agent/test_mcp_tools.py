"""Tests for MCP tool wrapper."""

from __future__ import annotations

import asyncio


def test_tools_expose_expected_methods(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent import mcp_tools

    class DummyManager:
        async def start_tunnel(self, **kwargs):
            return type("Status", (), {"is_active": True, "local_port": 1080, "pid": 1234, "details": kwargs})()

        async def stop_tunnel(self):
            return type("Status", (), {"is_active": False, "local_port": 0, "pid": None, "details": {}})()

        async def status(self):
            return type("Status", (), {"is_active": True, "local_port": 1080, "pid": 4321, "details": {}})()

    class DummyDiagnostics:
        def collect(self):
            return type("Report", (), {"cpu_percent": 10.0, "memory": type("M", (), {"percent": 50.0})(), "disk": type("D", (), {"percent": 20.0})()})()

    async def fake_connectivity(**kwargs):
        return [type("Status", (), {"url": "https://api", "reachable": True, "status_code": 200})()]

    tools = mcp_tools.VPNProxyTools(
        tunnel_manager=DummyManager(),
        diagnostics=DummyDiagnostics(),
        connectivity_tester=fake_connectivity,
    )

    async def run_checks():
        setup_result = await tools.setup_tunnel(host="vpn", username="alice", key_path="/tmp/key", port=1080)
        status_result = await tools.check_tunnel_status()
        await tools.stop_tunnel()
        diag = await tools.diagnose_system()
        connectivity = await tools.test_connectivity(proxy_url="socks5://localhost:1080", api_urls=["https://api"])
        return setup_result, status_result, diag, connectivity

    setup_result, status_result, diag, connectivity = asyncio.run(run_checks())

    assert setup_result["success"] is True
    assert status_result["status"]["is_active"] is True
    assert diag["cpu_percent"] == 10.0
    assert connectivity[0]["reachable"] is True
