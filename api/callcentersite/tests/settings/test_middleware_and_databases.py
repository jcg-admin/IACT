"""Validaciones de seguridad para middleware y configuración de bases de datos."""

from __future__ import annotations

import importlib


def test_session_security_middleware_presente() -> None:
    """El middleware de seguridad de sesión debe estar configurado y después de auth."""

    base_settings = importlib.import_module("callcentersite.settings.base")

    middleware = list(base_settings.MIDDLEWARE)
    target = "callcentersite.middleware.session_security.SessionSecurityMiddleware"

    assert target in middleware
    assert middleware.index(target) > middleware.index(
        "django.contrib.auth.middleware.AuthenticationMiddleware"
    )


def test_bases_de_datos_principales_configuradas() -> None:
    """La configuración base define PostgreSQL y MySQL en lugar de SQLite."""

    base_settings = importlib.import_module("callcentersite.settings.base")

    assert base_settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert base_settings.DATABASES["ivr_readonly"]["ENGINE"] == "mysql.connector.django"

