"""Rutas principales del proyecto IACT."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(_request):
    """Retorna estado básico de la aplicación."""

    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/dashboard/", include("callcentersite.apps.dashboard.urls")),
    path("api/v1/permissions/", include("callcentersite.apps.permissions.urls")),
    path("api/dora/", include("dora_metrics.urls")),
    path("health/", health_check, name="health"),
]
