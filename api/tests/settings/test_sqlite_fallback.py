"""Verifica la configuración de SQLite para entornos locales."""

import os
import importlib
import sys
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "callcentersite.settings.development")
django.setup()


def _reload_dev_settings(monkeypatch) -> object:
    """Recarga el módulo de settings de desarrollo para aplicar cambios de entorno."""

    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "callcentersite.settings.development")
    for module in ["callcentersite.settings.development", "callcentersite.settings.base"]:
        sys.modules.pop(module, None)
    return importlib.import_module("callcentersite.settings.development")


def test_development_settings_usar_sqlite_por_defecto(monkeypatch) -> None:
    """El ambiente de desarrollo usa SQLite sin depender de variables de entorno."""

    monkeypatch.delenv("USE_SQLITE_DEV", raising=False)

    settings_dev = _reload_dev_settings(monkeypatch)

    assert settings_dev.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
    assert settings_dev.DATABASES["ivr_readonly"]["ENGINE"] == "django.db.backends.sqlite3"


def test_bases_sqlite_mantienen_nombres_diferenciados(monkeypatch) -> None:
    """Los archivos de base de datos mantienen nombres claros para cada conexión."""

    monkeypatch.delenv("USE_SQLITE_DEV", raising=False)

    settings_dev = _reload_dev_settings(monkeypatch)

    default_path = Path(settings_dev.DATABASES["default"]["NAME"])
    ivr_path = Path(settings_dev.DATABASES["ivr_readonly"]["NAME"])

    assert default_path.name == "app.sqlite3"
    assert ivr_path.name == "ivr_readonly.sqlite3"
    assert default_path.parent == ivr_path.parent
    assert default_path.parent.name == "local_db"
