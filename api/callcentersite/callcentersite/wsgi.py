"""Configuración WSGI para despliegue con Apache + mod_wsgi."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "callcentersite.settings.production")

application = get_wsgi_application()
