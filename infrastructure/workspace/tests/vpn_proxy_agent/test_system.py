"""Tests for system diagnostics module."""

from __future__ import annotations

from types import SimpleNamespace


def test_system_diagnostics_collects_metrics(monkeypatch) -> None:
    from infrastructure.workspace.vpn_proxy_agent.system.services import SystemDiagnostics

    fake_psutil = SimpleNamespace(
        cpu_percent=lambda interval: 12.5,
        virtual_memory=lambda: SimpleNamespace(percent=43.2, total=16 * 1024**3, available=8 * 1024**3),
        disk_usage=lambda path: SimpleNamespace(percent=71.0, total=512 * 1024**3, free=256 * 1024**3),
        net_io_counters=lambda: SimpleNamespace(bytes_sent=1024, bytes_recv=2048),
        users=lambda: [SimpleNamespace(name="alice"), SimpleNamespace(name="bob")],
        pids=lambda: list(range(10)),
    )

    diagnostics = SystemDiagnostics(psutil_module=fake_psutil)
    report = diagnostics.collect()

    assert report.cpu_percent == 12.5
    assert report.memory.total_gb == 16
    assert report.disk.percent == 71.0
    assert report.active_users == ["alice", "bob"]
