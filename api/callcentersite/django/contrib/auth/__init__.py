"""Implementaciones mínimas del módulo django.contrib.auth."""

from __future__ import annotations

from typing import Any

try:
    from callcentersite.apps.users import models as user_models
except ModuleNotFoundError as exc:  # pragma: no cover - fallback en importación temprana
    raise RuntimeError("El paquete callcentersite debe estar disponible en sys.path") from exc


def get_user_model():
    """Retorna el modelo de usuarios en memoria."""

    return user_models.User


def logout(request: Any) -> None:
    """Marca al usuario como no autenticado y limpia la sesión."""

    user = getattr(request, "user", None)
    if user is not None:
        setter = getattr(user, "set_authenticated", None)
        if callable(setter):
            setter(False)
        else:  # pragma: no cover - ruta defensiva
            setattr(user, "is_authenticated", False)

    session = getattr(request, "session", None)
    if session is not None and hasattr(session, "flush"):
        session.flush()


__all__ = ["get_user_model", "logout"]
