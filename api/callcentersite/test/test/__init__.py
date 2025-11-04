"""Utilidades de testing simplificadas."""

from __future__ import annotations

from typing import Any, Dict, Optional

from django.http import HttpRequest


class RequestFactory:
    """Generador mínimo de ``HttpRequest`` para las pruebas."""

    def _base_request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None
    ) -> HttpRequest:
        return HttpRequest(method=method, path=path, data=data)

    def get(self, path: str, data: Optional[Dict[str, Any]] = None) -> HttpRequest:
        return self._base_request("GET", path, data)


__all__ = ["RequestFactory"]
