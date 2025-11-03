"""Objetos HTTP simplificados compatibles con las pruebas unitarias."""

from __future__ import annotations

from typing import Any, Dict, Optional


class HttpResponse:
    """Respuesta HTTP minimalista."""

    def __init__(self, content: Any = "", status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        self.content = content
        self.status_code = status
        self.headers: Dict[str, str] = dict(headers or {})

    def __setitem__(self, key: str, value: str) -> None:
        self.headers[key] = value

    def __getitem__(self, key: str) -> str:  # pragma: no cover - ruta auxiliar
        return self.headers[key]


class HttpRequest:
    """Request HTTP básico con los campos usados por las pruebas."""

    def __init__(self, method: str = "GET", path: str = "/", data: Optional[Dict[str, Any]] = None) -> None:
        self.method = method.upper()
        self.path = path
        payload = dict(data or {})
        self.GET: Dict[str, Any] = payload if self.method == "GET" else {}
        self.POST: Dict[str, Any] = payload if self.method in {"POST", "PUT", "PATCH"} else {}
        self.META: Dict[str, Any] = {}
        self.session: Any = None
        self.user: Any = type("AnonymousUser", (), {"is_authenticated": False})()


__all__ = ["HttpRequest", "HttpResponse"]
