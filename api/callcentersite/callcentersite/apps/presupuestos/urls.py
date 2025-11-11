from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PresupuestoViewSet

app_name = "presupuestos"

router = DefaultRouter()
router.register(r'', PresupuestoViewSet, basename='presupuesto')

urlpatterns = [
    path("", include(router.urls)),
]
