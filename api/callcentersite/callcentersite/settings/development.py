"""Configuración de desarrollo."""

from importlib import util

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
