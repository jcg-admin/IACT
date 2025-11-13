"""System diagnostics built on top of :mod:`psutil`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


def _maybe_import_psutil():  # pragma: no cover - thin wrapper
    import psutil

    return psutil


@dataclass
class MemoryStats:
    percent: float
    total_gb: int
    available_gb: int


@dataclass
class DiskStats:
    percent: float
    total_gb: int
    free_gb: int


@dataclass
class NetworkStats:
    bytes_sent: int
    bytes_received: int


@dataclass
class SystemReport:
    cpu_percent: float
    memory: MemoryStats
    disk: DiskStats
    network: NetworkStats
    active_users: List[str]
    process_count: int


class SystemDiagnostics:
    """Collect and normalize system metrics."""

    def __init__(self, psutil_module=None) -> None:
        self._psutil = psutil_module or _maybe_import_psutil()

    def collect(self) -> SystemReport:
        psutil = self._psutil
        cpu_percent = float(psutil.cpu_percent(interval=0.1))
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        users = psutil.users()
        processes = psutil.pids()

        memory = MemoryStats(
            percent=float(vm.percent),
            total_gb=int(vm.total // 1024**3),
            available_gb=int(vm.available // 1024**3),
        )
        disk = DiskStats(
            percent=float(du.percent),
            total_gb=int(du.total // 1024**3),
            free_gb=int(du.free // 1024**3),
        )
        network = NetworkStats(bytes_sent=int(net.bytes_sent), bytes_received=int(net.bytes_recv))
        active_users = [user.name for user in users]
        process_count = len(processes)

        return SystemReport(
            cpu_percent=cpu_percent,
            memory=memory,
            disk=disk,
            network=network,
            active_users=active_users,
            process_count=process_count,
        )


__all__ = [
    "SystemDiagnostics",
    "SystemReport",
    "MemoryStats",
    "DiskStats",
    "NetworkStats",
]
