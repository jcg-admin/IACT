"""Hamilton nodes composing the VPN/Proxy workflows."""

from __future__ import annotations

from typing import List, Mapping, Sequence

from .network.connectivity import EndpointStatus
from .system.services import SystemDiagnostics
from .tunnel.status import TunnelStatus


def tunnel_status(status: TunnelStatus | None = None):
    if status is None:
        raise ValueError("Status payload is required")
    if isinstance(status, TunnelStatus):
        return status
    if hasattr(status, "is_active") and hasattr(status, "local_port"):
        return TunnelStatus(
            is_active=status.is_active,
            local_port=status.local_port,
            pid=getattr(status, "pid", None),
            details=getattr(status, "details", {}),
        )
    raise TypeError("Unsupported status payload")


def system_health_summary(report) -> Mapping[str, float]:
    return {
        "cpu_percent": float(report.cpu_percent),
        "memory_percent": float(report.memory.percent),
        "disk_percent": float(report.disk.percent),
    }


def connectivity_matrix(statuses: Sequence[EndpointStatus]) -> List[Mapping[str, object]]:
    matrix = []
    for status in statuses:
        matrix.append(
                {
                    "url": status.url,
                    "reachable": status.reachable,
                    "status_code": status.status_code,
                    "error": getattr(status, "error", None),
                }
            )
    return matrix


__all__ = ["tunnel_status", "system_health_summary", "connectivity_matrix"]
