"""Tests for state persistence manager."""

from __future__ import annotations

import json
from pathlib import Path


def test_state_manager_round_trip(tmp_path: Path) -> None:
    from infrastructure.workspace.vpn_proxy_agent.state.manager import StateManager

    manager = StateManager(base_dir=tmp_path)

    assert manager.load_state("tunnel") == {}

    payload = {"is_active": True, "local_port": 1080}
    manager.save_state("tunnel", payload)

    stored = json.loads((tmp_path / "tunnel.json").read_text())
    assert stored == payload
    assert manager.load_state("tunnel") == payload
