"""Stub de django.apps para pruebas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppConfig:
    """Config básica sin lógica adicional."""

    name: str
    verbose_name: str | None = None
