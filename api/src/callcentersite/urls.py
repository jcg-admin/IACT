"""Rutas principales del proyecto IACT."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
# Importamos RedirectView para redirigir la raíz (solución al 404)
from django.views.generic.base import RedirectView 

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(_request):
    """Retorna estado básico de la aplicación."""

    return JsonResponse({"status": "ok"})


urlpatterns = [
    # 1. REDIRECCIÓN DE LA RAÍZ (/) a la documentación
    # Redirige '/' a '/api/docs/' (Swagger UI) para evitar el 404 de Django.
    path(
        "", 
        RedirectView.as_view(url="api/docs/", permanent=False), 
        name="api-root-redirect"
    ),

    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    
    # **************** INCLUSIONES DE APPS DEL PROYECTO PRINCIPAL ****************
    path("api/v1/", include("callcentersite.apps.users.urls")),
    path("api/v1/configuration/", include("callcentersite.apps.configuration.urls")),
    path(
        "api/v1/configuracion/",
        include(
            (
                "callcentersite.apps.configuration.urls",
                "configuration",
            ),
            namespace="configuracion",
        ),
    ),
    path("api/v1/auth/", include("callcentersite.apps.authentication.urls")),
    path("api/v1/dashboard/", include("callcentersite.apps.dashboard.urls")),
    path("api/v1/presupuestos/", include("callcentersite.apps.presupuestos.urls")),
    path("api/v1/politicas/", include("callcentersite.apps.politicas.urls")),
    path("api/v1/excepciones/", include("callcentersite.apps.excepciones.urls")),
    path("api/v1/reportes/", include("callcentersite.apps.reportes.urls")),
    path("api/v1/notifications/", include("callcentersite.apps.notifications.urls")),
    path("api/v1/etl/", include("callcentersite.apps.etl.urls")),
    path("api/v1/permissions/", include("callcentersite.apps.permissions.urls")),
    path("api/v1/llamadas/", include("callcentersite.apps.llamadas.urls")),
    
    # **************** INCLUSIONES DE PAQUETES EXTERNOS ****************
    path("api/v1/dora/", include("dora_metrics.urls")),
    path("api/v1/data/", include("data_centralization.urls")),
    
    path("health/", health_check, name="health"),
]

# **************** CONFIGURACIÓN CONDICIONAL DE DESARROLLO ****************

# Django Debug Toolbar URLs (solo en desarrollo)
from django.conf import settings

# NOTA IMPORTANTE: Esta sección es condicional.
# No es necesario removerla en producción. Se ejecutará SOLAMENTE
# si settings.DEBUG es True (ambiente de desarrollo). 
# En producción, esta sección es ignorada automáticamente.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]