"""URLs para API REST de usuarios."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_usuarios import UserViewSet

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]
