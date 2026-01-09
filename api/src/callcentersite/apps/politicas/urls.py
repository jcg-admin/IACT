from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PoliticaViewSet

app_name = "politicas"

router = DefaultRouter()
router.register(r'', PoliticaViewSet, basename='politica')

urlpatterns = [
    path("", include(router.urls)),
]
