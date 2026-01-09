"""Funciones de hashing mínimas para pruebas unitarias."""

from __future__ import annotations

import hashlib
import secrets
from typing import Tuple

ALGORITHM = "stub_sha256"


def _encode(password: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{ALGORITHM}${salt}${digest}"


def make_password(password: str, salt: str | None = None) -> str:
    """Genera un hash determinista con SHA-256 y un salt aleatorio."""

    if salt is None:
        salt = secrets.token_hex(16)
    return _encode(password, salt)


def check_password(password: str, encoded: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""

    try:
        algorithm, salt, _hash = _split(encoded)
    except ValueError:  # pragma: no cover - entradas corruptas
        return False

    if algorithm != ALGORITHM:
        return False

    return _encode(password, salt) == encoded


def _split(encoded: str) -> Tuple[str, str, str]:
    parts = encoded.split("$", 2)
    if len(parts) != 3:
        raise ValueError("Encoded password must have three components")
    return parts[0], parts[1], parts[2]


__all__ = ["make_password", "check_password"]
