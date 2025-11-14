"""Tests for network connectivity checks."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest


class FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class FakeClient:
    def __init__(self, responses: dict[str, int]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def get(self, url: str, *, timeout: float) -> FakeResponse:
        self.calls.append((url, {"timeout": timeout}))
        return FakeResponse(self.responses[url])

    async def aclose(self) -> None:
        return None


def test_connectivity_reports_status(monkeypatch: pytest.MonkeyPatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent.network.connectivity import test_endpoints

    responses = {
        "https://api.service-a.com": 200,
        "https://api.service-b.com": 503,
    }

    async def fake_client_factory(*, proxy: str | None) -> FakeClient:
        assert proxy == "socks5://localhost:1080"
        return FakeClient(responses)

    results = asyncio.run(
        test_endpoints(
            proxy_url="socks5://localhost:1080",
            api_urls=list(responses.keys()),
            client_factory=fake_client_factory,
            timeout=1.0,
        )
    )

    assert results[0].reachable is True
    assert results[1].reachable is False
