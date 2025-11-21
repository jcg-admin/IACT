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
            # CAMBIO: Añadido prefijo 'src.'
            "()": "src.callcentersite.logging.JSONStructuredFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console_debug": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("APP_LOG_FILE", "/var/log/iact/application.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("APP_ERROR_FILE", "/var/log/iact/error.log"),
            "formatter": "verbose",
            "level": "ERROR",
            "maxBytes": 1024 * 1024 * 20,  # 20 MB
            "backupCount": 3,
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("APP_JSON_LOG_FILE", "/var/log/iact/application_json.log"),
            "formatter": "json_structured",
            "maxBytes": 1024 * 1024 * 100,  # 100 MB
            "backupCount": 10,
        },
        "json_error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("APP_JSON_ERROR_FILE", "/var/log/iact/error_json.log"),
            "formatter": "json_structured",
            "level": "ERROR",
            "maxBytes": 1024 * 1024 * 30,  # 30 MB
            "backupCount": 5,
        },
        "security_audit": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("SECURITY_AUDIT_LOG", "/var/log/iact/security.log"),
            "formatter": "json_structured",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 2,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "error_file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "error_file"],
            "level": "INFO",
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
        # CAMBIO: Añadido prefijo 'src.' a todos los loggers internos
        "src.callcentersite": {
            "handlers": ["console", "file", "error_file", "json_file", "json_error_file"],
            "level": os.getenv("APP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "src.callcentersite.apps.etl": {
            "handlers": ["console", "file", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "src.callcentersite.apps.authentication": {
            "handlers": ["console", "file", "error_file", "json_file", "json_error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "src.callcentersite.apps.audit": {
            "handlers": ["console", "file", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "src.dora_metrics": {
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
    """Retorna la configuracion de logging completa."""
    return LOGGING_CONFIG