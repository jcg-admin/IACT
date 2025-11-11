"""URLs para API REST de configuraciones."""

from django.urls import path

from .views import (
    ConfiguracionEditarView,
    ConfiguracionExportarView,
    ConfiguracionImportarView,
    ConfiguracionListView,
    ConfiguracionRestaurarView,
)

app_name = "configuration"

urlpatterns = [
    path("configuracion/", ConfiguracionListView.as_view(), name="list"),
    path("configuracion/<str:clave>/", ConfiguracionEditarView.as_view(), name="editar"),
    path("configuracion/exportar/", ConfiguracionExportarView.as_view(), name="exportar"),
    path("configuracion/importar/", ConfiguracionImportarView.as_view(), name="importar"),
    path("configuracion/<str:clave>/restaurar/", ConfiguracionRestaurarView.as_view(), name="restaurar"),
]
