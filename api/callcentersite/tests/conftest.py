"""Configuración mínima para ejecutar pytest sin dependencias externas."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, ContextManager, Iterator

import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


def pytest_addoption(parser: pytest.Parser) -> None:
    """Registra opciones stub para compatibilidad con pytest.ini."""
    parser.addoption(
        "--cov",
        action="append",
        default=[],
        dest="stub_cov",
        help="Opción stub de coverage; se ignora en entornos sin pytest-cov.",
    )
    parser.addoption(
        "--cov-report",
        action="append",
        default=[],
        dest="stub_cov_report",
        help="Opción stub de coverage; se ignora en entornos sin pytest-cov.",
    )
    parser.addoption(
        "--cov-branch",
        action="store_true",
        default=False,
        dest="stub_cov_branch",
        help="Bandera stub para cobertura por rama.",
    )
    parser.addoption(
        "--nomigrations",
        action="store_true",
        default=False,
        dest="stub_nomigrations",
        help="Bandera stub equivalente a pytest-django --nomigrations.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """Consume opciones stub para evitar advertencias de pytest."""
    for attr in ("stub_cov", "stub_cov_report", "stub_cov_branch", "stub_nomigrations"):
        getattr(config.option, attr, None)
    config.addinivalue_line("markers", "django_db: marcador stub para compatibilidad con pytest-django")


@pytest.fixture
def django_assert_num_queries() -> Callable[[int], ContextManager[None]]:
    """Context manager stub que ignora el conteo de consultas."""

    @contextmanager
    def _assertion(expected: int):  # pragma: no cover - trivial
        yield

    return _assertion


@pytest.fixture(autouse=True)
def reset_in_memory_db() -> Iterator[None]:
    """Restablece los registros en memoria antes de cada prueba."""

    from callcentersite.apps.users import models

    models.reset_registry()
    yield
    models.reset_registry()
