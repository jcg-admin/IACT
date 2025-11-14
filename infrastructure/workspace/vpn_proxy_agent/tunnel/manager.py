"""SSH tunnel orchestration utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..state.manager import StateManager
from .status import TunnelStatus


def _coerce_status(raw: Any) -> TunnelStatus:
    if isinstance(raw, TunnelStatus):
        return raw
    if hasattr(raw, "is_active") and hasattr(raw, "local_port"):
        return TunnelStatus(
            is_active=bool(getattr(raw, "is_active")),
            local_port=int(getattr(raw, "local_port", 0)),
            pid=getattr(raw, "pid", None),
            details=dict(getattr(raw, "details", {})),
        )
    if isinstance(raw, dict):
        return TunnelStatus(
            is_active=bool(raw.get("is_active", False)),
            local_port=int(raw.get("local_port", 0)),
            pid=raw.get("pid"),
            details=dict(raw.get("details", {})),
        )
    raise TypeError(f"Unsupported tunnel status payload: {raw!r}")


class TunnelManager:
    """Manage tunnel lifecycle backed by a :class:`StateManager`."""

    def __init__(
        self,
        ssh_client: Any,
        state_manager: StateManager,
        *,
        state_key: str = "tunnel",
    ) -> None:
        self._ssh_client = ssh_client
        self.state_manager = state_manager
        self._state_key = state_key

    async def start_tunnel(
        self,
        *,
        host: str,
        username: str,
        key_path: Path,
        local_port: int,
        extra: Dict[str, Any] | None = None,
    ) -> TunnelStatus:
        kwargs = {
            "host": host,
            "username": username,
            "key_path": Path(key_path),
            "local_port": local_port,
        }
        if extra:
            kwargs["extra"] = extra
        raw_status = await self._ssh_client.open_tunnel(**kwargs)
        status = _coerce_status(raw_status)
        self.state_manager.save_state(
            self._state_key,
            {
                "is_active": status.is_active,
                "local_port": status.local_port,
                "pid": status.pid,
                "details": status.details,
            },
        )
        return status

    async def stop_tunnel(self) -> TunnelStatus:
        raw_status = await self._ssh_client.close_tunnel()
        status = _coerce_status(raw_status)
        self.state_manager.save_state(
            self._state_key,
            {
                "is_active": status.is_active,
                "local_port": status.local_port,
                "pid": status.pid,
                "details": status.details,
            },
        )
        return status

    async def status(self) -> TunnelStatus:
        stored = self.state_manager.load_state(self._state_key)
        if not stored:
            return TunnelStatus(is_active=False, local_port=0, pid=None, details={})
        return _coerce_status(stored)


__all__ = ["TunnelManager", "TunnelStatus"]
