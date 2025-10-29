"""Configuración mínima para ejecutar pytest sin dependencias externas."""
from __future__ import annotations

import pytest


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
