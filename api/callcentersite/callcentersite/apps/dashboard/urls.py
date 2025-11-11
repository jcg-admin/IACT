"""Rutas del dashboard."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardCompartirView,
    DashboardExportarView,
    DashboardOverviewView,
    DashboardPersonalizarView,
)

app_name = "dashboard"

# Router para DashboardViewSet
router = DefaultRouter()
router.register(r'', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path("overview/", DashboardOverviewView.as_view(), name="overview"),
    path("exportar/", DashboardExportarView.as_view(), name="exportar"),
    path("personalizar/", DashboardPersonalizarView.as_view(), name="personalizar"),
    path("compartir/", DashboardCompartirView.as_view(), name="compartir"),
]
