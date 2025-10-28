"""Configuración WSGI para el proyecto Call Center Analytics."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')

application = get_wsgi_application()
