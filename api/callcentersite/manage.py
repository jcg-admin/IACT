#!/usr/bin/env python
"""Herramienta CLI de Django."""

import os
import sys


def main() -> None:
    """Ejecuta tareas administrativas de Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "callcentersite.settings.development")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - error crítico
        raise ImportError(
            "No fue posible importar Django. Verifica tu entorno virtual y dependencias."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":  # pragma: no cover
    main()
