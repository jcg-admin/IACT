"""TDD tests for the SSH tunnel manager abstractions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FakeTunnelStatus:
    is_active: bool
    local_port: int
    pid: int | None
    details: dict[str, Any]


class DummySSHClient:
    def __init__(self) -> None:
        self.open_calls: list[dict[str, Any]] = []
        self.close_calls: list[dict[str, Any]] = []

    async def open_tunnel(self, *, host: str, username: str, key_path: Path, local_port: int) -> FakeTunnelStatus:
        self.open_calls.append({
            "host": host,
            "username": username,
            "key_path": str(key_path),
            "local_port": local_port,
        })
        return FakeTunnelStatus(is_active=True, local_port=local_port, pid=1234, details={"host": host})

    async def close_tunnel(self) -> FakeTunnelStatus:
        self.close_calls.append({})
        return FakeTunnelStatus(is_active=False, local_port=0, pid=None, details={})


def build_manager(tmp_path: Path):
    from infrastructure.workspace.vpn_proxy_agent.state.manager import StateManager
    from infrastructure.workspace.vpn_proxy_agent.tunnel.manager import TunnelManager

    state = StateManager(base_dir=tmp_path)
    ssh_client = DummySSHClient()
    manager = TunnelManager(ssh_client=ssh_client, state_manager=state)
    return manager, ssh_client, state


def test_start_tunnel_records_state(tmp_path: Path) -> None:
    manager, ssh_client, state = build_manager(tmp_path)

    status = asyncio.run(
        manager.start_tunnel(
            host="vpn.example.com",
            username="alice",
            key_path=tmp_path / "id_ed25519",
            local_port=1080,
        )
    )

    assert status.is_active is True
    assert ssh_client.open_calls[-1]["host"] == "vpn.example.com"
    data = state.load_state("tunnel")
    assert data["is_active"] is True
    assert data["local_port"] == 1080


def test_stop_tunnel_updates_state(tmp_path: Path) -> None:
    manager, ssh_client, state = build_manager(tmp_path)

    asyncio.run(
        manager.start_tunnel(
            host="vpn.example.com",
            username="alice",
            key_path=tmp_path / "id_ed25519",
            local_port=1080,
        )
    )
    status = asyncio.run(manager.stop_tunnel())

    assert status.is_active is False
    assert len(ssh_client.close_calls) == 1
    assert state.load_state("tunnel")["is_active"] is False


def test_status_reads_from_state(tmp_path: Path) -> None:
    manager, _, state = build_manager(tmp_path)

    manager.state_manager.save_state("tunnel", {"is_active": True, "local_port": 8080, "pid": 100})
    status = asyncio.run(manager.status())

    assert status.is_active is True
    assert status.local_port == 8080
