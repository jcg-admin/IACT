"""Data models representing tunnel status."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TunnelStatus:
    is_active: bool
    local_port: int
    pid: int | None
    details: Dict[str, Any]


__all__ = ["TunnelStatus"]
