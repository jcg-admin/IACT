"""Middleware de sesión en memoria."""

from __future__ import annotations


class SessionStore(dict):
    """Implementación sencilla de almacenamiento de sesión."""

    def save(self) -> None:
        """Compatibilidad con API de Django; no hace nada."""

    def flush(self) -> None:
        """Limpia toda la sesión."""

        self.clear()


class SessionMiddleware:
    """Agrega una sesión en memoria a la solicitud."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):  # pragma: no cover - flujo no usado en tests
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request) -> None:
        if getattr(request, "session", None) is None:
            request.session = SessionStore()

    def process_response(self, request, response):  # pragma: no cover - compatibilidad
        return response
