"""Tests for VPN proxy Codex MCP playbooks."""

from __future__ import annotations


def test_playbooks_register_vpn_workflows() -> None:
    from infrastructure.workspace.codex_mcp import vpn_proxy_playbooks

    registry = vpn_proxy_playbooks.build_registry()
    assert "setup-dev-environment" in registry
    assert registry["setup-dev-environment"]["steps"][0]["tool"] == "setup_tunnel"
