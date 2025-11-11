"""Rutas para API REST de configuración."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConfiguracionViewSet

app_name = "configuracion"

# Router para ConfiguracionViewSet
router = DefaultRouter()
router.register(r'', ConfiguracionViewSet, basename='configuracion')

urlpatterns = [
    path("", include(router.urls)),
]
