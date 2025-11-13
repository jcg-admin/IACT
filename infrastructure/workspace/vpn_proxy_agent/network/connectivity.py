"""Network connectivity tests using :mod:`httpx`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, List, Sequence


@dataclass
class EndpointStatus:
    url: str
    reachable: bool
    status_code: int | None
    error: str | None


async def _default_client_factory(*, proxy: str | None):  # pragma: no cover - thin wrapper
    import httpx

    return httpx.AsyncClient(proxies=proxy)


async def test_endpoints(
    *,
    proxy_url: str | None,
    api_urls: Sequence[str],
    client_factory: Callable[..., Awaitable[object]] | None = None,
    timeout: float = 5.0,
) -> List[EndpointStatus]:
    factory = client_factory or _default_client_factory
    client = await factory(proxy=proxy_url)
    results: List[EndpointStatus] = []
    try:
        for url in api_urls:
            try:
                response = await client.get(url, timeout=timeout)
                results.append(
                    EndpointStatus(
                        url=url,
                        reachable=200 <= int(getattr(response, "status_code", 0)) < 500,
                        status_code=int(getattr(response, "status_code", 0)),
                        error=None,
                    )
                )
            except Exception as exc:  # pragma: no cover - network errors not deterministic
                results.append(EndpointStatus(url=url, reachable=False, status_code=None, error=str(exc)))
        return results
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()


__all__ = ["EndpointStatus", "test_endpoints"]
