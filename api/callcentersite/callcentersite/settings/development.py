"""Configuración de desarrollo."""

import os
from importlib import util
from pathlib import Path

from .base import *  # noqa: F401,F403

DEBUG = True

if util.find_spec("debug_toolbar"):
    if "debug_toolbar" not in INSTALLED_APPS:
        INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

INTERNAL_IPS = ["127.0.0.1"]

sqlite_dir: Path = BASE_DIR / "local_db"
sqlite_dir.mkdir(exist_ok=True)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(sqlite_dir / "app.sqlite3"),
    },
    "ivr_readonly": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(sqlite_dir / "ivr_readonly.sqlite3"),
    },
}
