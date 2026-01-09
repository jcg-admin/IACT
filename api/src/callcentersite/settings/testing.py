"""Configuración específica para pruebas automatizadas."""

from .base import *  # noqa: F401,F403

# Usar modelo User custom (ahora es un modelo real de Django)
# AUTH_USER_MODEL ya está definido en base.py como "users.User"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ["rest_framework.permissions.AllowAny"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "ivr_readonly": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
