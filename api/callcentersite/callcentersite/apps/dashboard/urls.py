"""Rutas del dashboard."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardOverviewView, DashboardViewSet

app_name = "dashboard"

# Router para DashboardViewSet
router = DefaultRouter()
router.register(r'', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path("overview/", DashboardOverviewView.as_view(), name="overview"),
    path("", include(router.urls)),
]
