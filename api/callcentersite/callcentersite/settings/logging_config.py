"""
Configuración profesional de logging para Django.
Incluye soporte para múltiples handlers, formatters y niveles de log.

TASK-010: Logging Estructurado JSON
- Layer 2: Application logs to Cassandra (future)
- JSON format para AI-parseable logs
- Contexto enriquecido: request_id, user_id, session_id
"""

import os
from typing import Any

# Configuración de logging profesional
LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d %(request_id)s %(user_id)s %(session_id)s",
            "rename_fields": {
                "asctime": "timestamp",
                "name": "logger",
                "levelname": "level",
                "pathname": "file",
                "lineno": "line",
                "funcName": "function",
            },
        },
        "json_structured": {
            "()": "callcentersite.logging.JSONStructuredFormatter",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.getenv("LOG_DIR", "/tmp"), "django.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.getenv("LOG_DIR", "/tmp"), "django_debug.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.getenv("LOG_DIR", "/tmp"), "django_errors.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "json_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.getenv("LOG_DIR", "/var/log/iact"), "app.json.log"),
            "maxBytes": 1024 * 1024 * 100,  # 100MB
            "backupCount": 10,
            "formatter": "json_structured",
        },
        "json_error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.getenv("LOG_DIR", "/var/log/iact"), "app_errors.json.log"),
            "maxBytes": 1024 * 1024 * 100,  # 100MB
            "backupCount": 20,
            "formatter": "json_structured",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "error_file", "json_file", "json_error_file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "json_error_file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["error_file", "json_error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console_debug"],
            "level": "DEBUG",
            "propagate": False,
        },
        "callcentersite": {
            "handlers": ["console", "file", "error_file", "json_file", "json_error_file"],
            "level": os.getenv("APP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "callcentersite.apps.etl": {
            "handlers": ["console", "file", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "callcentersite.apps.authentication": {
            "handlers": ["console", "file", "error_file", "json_file", "json_error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "callcentersite.apps.audit": {
            "handlers": ["console", "file", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "dora_metrics": {
            "handlers": ["console", "file", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file", "error_file"],
        "level": "INFO",
    },
}


def get_logging_config() -> dict[str, Any]:
    """
    Retorna la configuración de logging.
    Permite personalización según el entorno.
    """
    return LOGGING_CONFIG
