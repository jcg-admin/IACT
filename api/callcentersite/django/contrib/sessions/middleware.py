"""Middleware de sesión simplificado para pruebas."""

from __future__ import annotations

from typing import Any, Callable


class SessionStore(dict):
    """Almacén de sesión in-memory compatible con el uso de las pruebas."""

    def __init__(self) -> None:
        super().__init__()
        self.modified = False

    def __setitem__(self, key: Any, value: Any) -> None:
        self.modified = True
        super().__setitem__(key, value)

    def save(self) -> None:  # pragma: no cover - método trivial
        self.modified = False

    def flush(self) -> None:
        super().clear()
        self.modified = True


class SessionMiddleware:
    """Middleware que adjunta un ``SessionStore`` a cada request."""

    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:  # pragma: no cover - ruta no usada en tests
        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_request(self, request: Any) -> None:
        if getattr(request, "session", None) is None:
            request.session = SessionStore()

    def process_response(self, request: Any, response: Any) -> Any:  # pragma: no cover - trivial
        return response


__all__ = ["SessionMiddleware"]
