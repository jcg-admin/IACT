"""Tests for the Hamilton driver integration with the VPN agent."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class DummyLLMClient:
    price_per_1k_tokens: float = 0.1

    def complete(self, prompt: str) -> str:
        return f"LLM response for: {prompt[:24]}"


class DummyTunnelManager:
    async def status(self):
        return type("Status", (), {"is_active": True, "local_port": 1080, "pid": 1234, "details": {}})()


class DummyDiagnostics:
    def collect(self):
        return type(
            "Report",
            (),
            {
                "cpu_percent": 12.0,
                "memory": type("Mem", (), {"percent": 45.0})(),
                "disk": type("Disk", (), {"percent": 70.0})(),
            },
        )()


async def dummy_connectivity(**kwargs):
    return [type("Status", (), {"url": "https://api", "reachable": True, "status_code": 200})()]


def test_execute_vpn_workflow_returns_expected_outputs(monkeypatch) -> None:
    from infrastructure.workspace.hamilton_llm.driver import execute_vpn_workflow

    async def run_workflow():
        return await execute_vpn_workflow(
            tunnel_manager=DummyTunnelManager(),
            diagnostics=DummyDiagnostics(),
            connectivity_tester=dummy_connectivity,
            llm_client=DummyLLMClient(),
            idea="Automate VPN health",
            domain_data={"business_process": "DevOps", "ui": "CLI", "data": "Logs"},
            edge_cases=["network outage"],
            pricing_policy={"price_per_1k_tokens": 0.2, "safety_multiplier": 1.5},
        )

    result = asyncio.run(run_workflow())

    assert "business_value" in result
    assert result["business_value"]["pace"]["traditional_ml"]
    assert result["connectivity_matrix"][0]["reachable"] is True
    assert result["cost_estimate"] > 0


def test_select_llm_client_supports_claude(monkeypatch) -> None:
    from infrastructure.workspace.hamilton_llm.llm_client import create_llm_client

    monkeypatch.setenv("LLM_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    client = create_llm_client(response_catalog={"__default__": "Claude says hi"})

    assert "claude" in client.model_id
    assert "Claude" in client.complete("Hello")
