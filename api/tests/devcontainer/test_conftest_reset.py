"""Pruebas para el restablecimiento del registro en memoria en pytest."""

from __future__ import annotations

import importlib
import types
from typing import List

import pytest

from api.callcentersite.tests import conftest


def test_safe_reset_ignora_modulo_faltante(monkeypatch: pytest.MonkeyPatch) -> None:
    """No debe lanzar excepción si el paquete de usuarios no está disponible."""

    def fake_import(name: str) -> types.ModuleType:
        raise ModuleNotFoundError(name=name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    conftest.safe_reset_in_memory_registry()


def test_safe_reset_tolera_dependencias_de_django_faltantes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Debe ignorar la falta de dependencias básicas como Django."""

    def fake_import(name: str) -> types.ModuleType:
        raise ModuleNotFoundError(name="django")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    conftest.safe_reset_in_memory_registry()


def test_reset_fixture_invoca_reset_en_ambas_fases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """El fixture debe ejecutar el restablecimiento antes y después de la prueba."""
    llamadas: List[str] = []

    def registrar_llamada() -> None:
        llamadas.append("reset")

    monkeypatch.setattr(conftest, "safe_reset_in_memory_registry", registrar_llamada)

    fixture = conftest.reset_in_memory_db.__wrapped__()

    assert next(fixture) is None
    assert llamadas == ["reset"]

    with pytest.raises(StopIteration):
        next(fixture)

    assert llamadas == ["reset", "reset"]
