"""Stub de utilidades de autenticación."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - sólo para tipo estático
    from callcentersite.apps.users.models import User


def get_user_model():
    """Retorna la clase de usuario del dominio."""

    from callcentersite.apps.users import models

    return models.User


def logout(request) -> None:
    """Marca al usuario como no autenticado."""

    user = getattr(request, "user", None)
    if user is not None:
        try:
            user.set_authenticated(False)
        except AttributeError:  # pragma: no cover - compatibilidad defensiva
            user.is_authenticated = False
