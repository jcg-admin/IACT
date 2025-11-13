"""Tools exposed through the Model Context Protocol server."""

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, List, Sequence

from .network.connectivity import EndpointStatus
from .ssh.keys import GeneratedKeyPair, generate_keypair
from .system.services import SystemDiagnostics
from .tunnel.manager import TunnelManager, TunnelStatus


class VPNProxyTools:
    """High-level operations orchestrated via MCP."""

    def __init__(
        self,
        *,
        tunnel_manager: TunnelManager,
        diagnostics: SystemDiagnostics,
        connectivity_tester: Callable[..., Awaitable[List[EndpointStatus]]],
        key_generator: Callable[..., GeneratedKeyPair] | None = None,
    ) -> None:
        self.tunnel_manager = tunnel_manager
        self.diagnostics = diagnostics
        self.connectivity_tester = connectivity_tester
        self.key_generator = key_generator or generate_keypair

    @staticmethod
    def _status_to_dict(status: TunnelStatus) -> dict:
        return {
            "is_active": status.is_active,
            "local_port": status.local_port,
            "pid": status.pid,
            "details": status.details,
        }

    async def setup_tunnel(self, *, host: str, username: str, key_path: str, port: int = 1080) -> dict:
        status = await self.tunnel_manager.start_tunnel(
            host=host,
            username=username,
            key_path=Path(key_path),
            local_port=port,
        )
        return {"success": status.is_active, "status": self._status_to_dict(status)}

    async def check_tunnel_status(self) -> dict:
        status = await self.tunnel_manager.status()
        return {"status": self._status_to_dict(status)}

    async def stop_tunnel(self) -> dict:
        status = await self.tunnel_manager.stop_tunnel()
        return {"success": not status.is_active, "status": self._status_to_dict(status)}

    async def diagnose_system(self) -> dict:
        report = self.diagnostics.collect()
        return {
            "cpu_percent": report.cpu_percent,
            "memory_percent": report.memory.percent,
            "disk_percent": report.disk.percent,
            "active_users": list(getattr(report, "active_users", [])),
            "process_count": int(getattr(report, "process_count", 0)),
        }

    async def generate_ssh_key(self, *, key_name: str = "vpn_key", key_type: str = "ed25519", directory: str | None = None) -> dict:
        base_dir = Path(directory) if directory else Path.home() / ".ssh"
        pair = self.key_generator(base_dir=base_dir, key_name=key_name, key_type=key_type)
        return pair.as_dict()

    async def test_connectivity(self, *, proxy_url: str | None, api_urls: Sequence[str], timeout: float = 5.0) -> List[dict]:
        statuses = await self.connectivity_tester(proxy_url=proxy_url, api_urls=api_urls, timeout=timeout)
        return [
            {
                "url": status.url,
                "reachable": status.reachable,
                "status_code": status.status_code,
                "error": getattr(status, "error", None),
            }
            for status in statuses
        ]


__all__ = ["VPNProxyTools"]
