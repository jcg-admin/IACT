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
    path("", ConfiguracionListView.as_view(), name="list"),
    path("<str:clave>/", ConfiguracionEditarView.as_view(), name="editar"),
    path("exportar/", ConfiguracionExportarView.as_view(), name="exportar"),
    path("importar/", ConfiguracionImportarView.as_view(), name="importar"),
    path("<str:clave>/restaurar/", ConfiguracionRestaurarView.as_view(), name="restaurar"),
]
