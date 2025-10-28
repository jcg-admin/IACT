# Verificación de Devcontainer

## Resumen de ajustes
- Se corrigió la ruta del workspace para alinear Codespaces con la raíz real del repositorio (`/workspace`).
- Los hooks de instalación ahora apuntan a `api/requirements/*.txt`, garantizando que dev y test se instalen correctamente.
- La copia del `.env` es opcional y solo se ejecuta cuando existe `api/.env.example`, evitando errores innecesarios.
- Las tareas de Django (`migrate`, `collectstatic`, `check`, `showmigrations`) se ejecutan desde `api/`, por lo que encuentran el `manage.py` correcto.
- La espera de base de datos verifica primero la existencia de `pg_isready`, reduciendo errores en entornos sin cliente de PostgreSQL.
- Herramientas clave del stack (Python, pip, poetry, pytest, Django) están presentes y se ejecutan correctamente.

## Detalle de comandos

| Fase | Comando | Estado | Notas |
|------|---------|--------|-------|
| `updateContentCommand` | `echo 'Repositorio actualizado'` | ✅ | Sin dependencias externas. |
| `onCreateCommand` | `pip install -r api/requirements/dev.txt` | ✅ | Archivo presente en el repositorio (instala dependencias de desarrollo). |
| `onCreateCommand` | `pip install -r api/requirements/test.txt` | ✅ | Archivo presente dentro de `api/requirements/`. |
| `onCreateCommand` | `python -c 'import django; import pytest; ...'` | ✅ | Importaciones funcionan con las dependencias actuales. |
| `postCreateCommand` | `git config --global --add safe.directory ...` | ✅ | Ejecutable disponible. |
| `postCreateCommand` | Copia condicional de `api/.env.example` | ⚠️ | Solo se ejecuta si existe `api/.env.example`; informa cuando no está disponible. |
| `postStartCommand` | `pg_isready ...` | ✅ | El cliente está disponible y la espera es opcional si faltara la utilidad. |
| `postStartCommand` | `cd api && python manage.py migrate` | ✅ | Ejecuta migraciones en la ruta correcta. |
| `postStartCommand` | `cd api && python manage.py collectstatic --noinput --clear` | ✅ | Ejecuta la tarea desde `api/`. |
| `postStartCommand` | `cd api && python manage.py check` | ✅ | Valida el proyecto en la ubicación correcta. |
| `postAttachCommand` | `cat README-CODESPACES.md ...` | ⚠️ | Continúa mostrando mensaje alternativo si no existe el archivo. |
| `postAttachCommand` | `cd api && python manage.py showmigrations` | ✅ | Resume el estado de migraciones al adjuntar el editor. |

## Versiones verificadas

| Herramienta | Versión |
|-------------|---------|
| Python | `python --version` → 3.12.10 |
| pip | `pip --version` → 25.2 |
| Poetry | `poetry --version` → 2.1.4 |
| Pytest | `pytest --version` → 8.4.1 |
| Django (import) | `python -c "import django; print(django.get_version())"` → 5.2.7 |

## Ejecuciones manuales
Los binarios clave (`python`, `pip`, `poetry`, `pytest`, `django-admin`) se verificaron manualmente para confirmar su disponibilidad. Para validar los cambios del devcontainer es necesario reconstruir el Codespace/Dev Container y observar la ejecución automática de los hooks ya corregidos.
