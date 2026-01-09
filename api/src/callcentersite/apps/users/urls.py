"""URLs para API REST de usuarios y permisos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_usuarios import UserRegistrationView, UserViewSet

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    # Registro publico de usuarios
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # Sistema de permisos granular
    path('permisos/', include('callcentersite.apps.users.urls_permisos')),
]
