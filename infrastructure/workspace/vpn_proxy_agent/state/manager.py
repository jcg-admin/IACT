"""Persistence helpers for VPN/Proxy agent state."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_STATE_DIR = Path(os.getenv("STATE_DIR", Path.home() / ".vpn-proxy-agent"))


class StateManager:
    """Store JSON documents describing tunnel state and diagnostics."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = Path(base_dir or DEFAULT_STATE_DIR).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        if not name:
            raise ValueError("State name must be a non-empty string")
        return self.base_dir / f"{name}.json"

    def load_state(self, name: str) -> Dict[str, Any]:
        path = self._path_for(name)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:  # pragma: no cover - defensive
            return {}

    def save_state(self, name: str, payload: Dict[str, Any]) -> None:
        path = self._path_for(name)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))


__all__ = ["StateManager", "DEFAULT_STATE_DIR"]
