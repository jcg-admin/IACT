"""Tests for Hamilton node adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeStatus:
    is_active: bool
    local_port: int
    pid: int | None


def test_tunnel_status_node_accepts_status(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent import hamilton_nodes

    result = hamilton_nodes.tunnel_status(status=FakeStatus(is_active=True, local_port=1080, pid=1234))

    assert result.is_active is True
    assert result.local_port == 1080


def test_system_health_node_aggregates(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent import hamilton_nodes

    report = type(
        "Report",
        (),
        {
            "cpu_percent": 10.0,
            "memory": type("Mem", (), {"percent": 50.0})(),
            "disk": type("Disk", (), {"percent": 75.0})(),
        },
    )()

    summary = hamilton_nodes.system_health_summary(report=report)

    assert summary["cpu_percent"] == 10.0
    assert summary["memory_percent"] == 50.0


def test_connectivity_node_formats(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent import hamilton_nodes

    statuses = [type("S", (), {"url": "https://api", "reachable": True, "status_code": 200})()]
    matrix = hamilton_nodes.connectivity_matrix(statuses=statuses)

    assert matrix[0]["reachable"] is True
