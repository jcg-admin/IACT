"""
Settings para tests de infraestructura.

Este settings minimal permite tests de conectividad de base de datos
sin requerir migraciones ni modelos personalizados.

Usar con:
    pytest --ds=callcentersite.settings.infrastructure_test
"""

from callcentersite.settings.base import *

# Deshabilitar admin y apps que requieren migraciones
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # NO incluir: admin, auth (requieren User model)
]

# Usar modelo User por defecto (no personalizado)
AUTH_USER_MODEL = "auth.User"

# Mantener configuracion de bases de datos
# (ya esta definida en base.py)

# Deshabilitar migraciones
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()