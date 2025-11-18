"""Verifica el fallback a SQLite documentado para entornos locales."""

import importlib
import sys


def test_development_settings_activan_sqlite_con_bandera(monkeypatch) -> None:
    """Cuando USE_SQLITE_DEV=true ambas bases usan SQLite en desarrollo."""

    monkeypatch.setenv("USE_SQLITE_DEV", "true")

    if "callcentersite.settings.development" in list(sys.modules):
        sys.modules.pop("callcentersite.settings.development")

    settings_dev = importlib.import_module("callcentersite.settings.development")

    assert settings_dev.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
    assert settings_dev.DATABASES["ivr_readonly"]["ENGINE"] == "django.db.backends.sqlite3"
    assert settings_dev.DATABASES["default"]["NAME"].endswith("app.sqlite3")
    assert settings_dev.DATABASES["ivr_readonly"]["NAME"].endswith("ivr_readonly.sqlite3")

    monkeypatch.delenv("USE_SQLITE_DEV", raising=False)
