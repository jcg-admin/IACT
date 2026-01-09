"""Pruebas de vistas de configuraciones consolidadas.

Validan que la app en inglés expone las rutas y comportamientos
antes disponibles en la versión en español (detalle e historial).
"""

from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from callcentersite.apps.configuration.models import Configuracion, ConfiguracionHistorial
from callcentersite.apps.configuration.views import (
    ConfiguracionEditarView,
    ConfiguracionAuditoriaView,
    ConfiguracionHistorialView,
)


class TestConfiguracionViewsEspanol(SimpleTestCase):
    """Valida que las vistas en inglés soporten las rutas legacy."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(id=1)

    def test_get_detalle_reutiliza_la_vista_de_edicion(self):
        """El GET al detalle debe devolver la configuración solicitada."""

        config = Configuracion(
            categoria="general",
            clave="timeout",
            valor="30",
            tipo_dato="integer",
            valor_default="30",
        )

        with mock.patch(
            "callcentersite.apps.configuration.views.ConfiguracionService.obtener_configuracion_detalle",
            return_value=config,
        ) as mock_service:
            request = self.factory.get("/api/v1/configuration/timeout/")
            request.user = self.user

            response = ConfiguracionEditarView.as_view()(request, clave="timeout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["clave"], "timeout")
        mock_service.assert_called_once_with(usuario_id=self.user.id, clave="timeout")

    def test_historial_view_serializa_cambios(self):
        """El historial expone los cambios registrados."""

        config = Configuracion(
            categoria="general",
            clave="timeout",
            valor="30",
            tipo_dato="integer",
            valor_default="30",
        )
        historial = [
            ConfiguracionHistorial(
                configuracion=config,
                clave="timeout",
                valor_anterior="30",
                valor_nuevo="60",
                timestamp=timezone.now(),
            )
        ]

        with mock.patch(
            "callcentersite.apps.configuration.views.ConfiguracionService.obtener_historial_configuracion",
            return_value=historial,
        ) as mock_service:
            request = self.factory.get("/api/v1/configuration/timeout/historial/")
            request.user = self.user

            response = ConfiguracionHistorialView.as_view()(request, clave="timeout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["valor_nuevo"], "60")
        mock_service.assert_called_once_with(usuario_id=self.user.id, clave="timeout")

    def test_auditoria_view_expone_historial_global(self):
        """La auditoría general retorna todas las modificaciones."""

        eventos = [
            ConfiguracionHistorial(
                configuracion=Configuracion(
                    categoria="general",
                    clave="timeout",
                    valor="30",
                    tipo_dato="integer",
                    valor_default="30",
                ),
                clave="timeout",
                valor_anterior="30",
                valor_nuevo="35",
                timestamp=timezone.now(),
            )
        ]

        with mock.patch(
            "callcentersite.apps.configuration.views.ConfiguracionService.obtener_historial_general",
            return_value=eventos,
        ) as mock_service:
            request = self.factory.get("/api/v1/configuration/auditar/")
            request.user = self.user

            response = ConfiguracionAuditoriaView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["clave"], "timeout")
        mock_service.assert_called_once_with(usuario_id=self.user.id)
