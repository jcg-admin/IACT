"""HTTP mínimo compatible con las pruebas."""

from __future__ import annotations

from typing import Any, Dict


class HttpResponse:
    """Respuesta HTTP extremadamente simple."""

    def __init__(self, content: Any = "", status: int = 200):
        self.content = content
        self.status_code = status
        self.headers: Dict[str, str] = {}

    def __setitem__(self, key: str, value: str) -> None:
        self.headers[key] = value

    def __getitem__(self, key: str) -> str:
        return self.headers[key]


class HttpRequest:
    """Solicitud HTTP simplificada para pruebas."""

    def __init__(self, method: str = "GET", path: str = "/") -> None:
        self.method = method.upper()
        self.path = path
        self.META: Dict[str, Any] = {}
        self.user: Any = None
        self.session: Any = None
