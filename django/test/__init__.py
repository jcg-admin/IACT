"""Implementación simplificada de RequestFactory."""

from __future__ import annotations

from typing import Any, Dict

from django.http import HttpRequest


class RequestFactory:
    """Crea solicitudes HTTP básicas para pruebas."""

    def _build_request(self, method: str, path: str, data: Dict[str, Any] | None = None, **extra: Any) -> HttpRequest:
        request = HttpRequest(method=method, path=path)
        request.META["REMOTE_ADDR"] = extra.pop("REMOTE_ADDR", "127.0.0.1")
        request.META["HTTP_USER_AGENT"] = extra.pop("HTTP_USER_AGENT", "")
        request.META.update(extra)
        request.data = data or {}
        return request

    def get(self, path: str = "/", data: Dict[str, Any] | None = None, **extra: Any) -> HttpRequest:
        return self._build_request("GET", path, data, **extra)
