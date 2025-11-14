"""Codex MCP playbooks for VPN/Proxy automation."""

from __future__ import annotations

from typing import Dict, List


def build_registry() -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    return {
        "setup-dev-environment": {
            "description": "Configure VPN tunnel and validate connectivity",
            "steps": [
                {"tool": "setup_tunnel", "description": "Establish SSH tunnel"},
                {"tool": "diagnose_system", "description": "Collect diagnostics"},
                {"tool": "test_connectivity", "description": "Verify API access"},
            ],
        },
        "health-check": {
            "description": "Inspect tunnel health and connectivity",
            "steps": [
                {"tool": "check_tunnel_status", "description": "Fetch tunnel status"},
                {"tool": "test_connectivity", "description": "Probe APIs"},
            ],
        },
        "stop-tunnel": {
            "description": "Terminate active tunnel",
            "steps": [{"tool": "stop_tunnel", "description": "Stop SSH tunnel"}],
        },
    }


__all__ = ["build_registry"]
