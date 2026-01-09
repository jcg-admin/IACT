"""Pruebas de consolidación para endpoints de configuración.

Estas pruebas aseguran que la ruta en español (`/api/v1/configuracion/`)
utiliza la implementación moderna del módulo `configuration` y que la app
legacy `configuracion` ya no está habilitada en `INSTALLED_APPS`.
"""

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import resolve

from callcentersite.apps.configuration.views import ConfiguracionListView


class TestConfiguracionConsolidation(SimpleTestCase):
    """Valida que exista una única implementación de configuraciones."""

    def test_ruta_espanol_resuelve_a_configuration(self):
        """La ruta legacy debe usar las vistas de `configuration`."""

        resolver = resolve("/api/v1/configuracion/")

        self.assertIs(resolver.func.view_class, ConfiguracionListView)

    def test_app_configuracion_no_esta_instalada(self):
        """La app duplicada `configuracion` no debe estar instalada."""

        self.assertNotIn("callcentersite.apps.configuracion", settings.INSTALLED_APPS)
