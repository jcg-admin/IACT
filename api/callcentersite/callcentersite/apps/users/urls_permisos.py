"""
URLs para API REST del sistema de permisos granular.

Endpoints registrados:
  - /api/permisos/funciones/               - CRUD funciones
  - /api/permisos/capacidades/             - CRUD capacidades
  - /api/permisos/grupos/                  - CRUD grupos de permisos
  - /api/permisos/excepcionales/           - Grant/Revoke permisos excepcionales
  - /api/permisos/auditoria/               - Read-only audit logs
  - /api/permisos/verificar/:id/...        - Endpoints de verificación

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_permisos import (
    FuncionViewSet,
    CapacidadViewSet,
    GrupoPermisoViewSet,
    PermisoExcepcionalViewSet,
    AuditoriaPermisoViewSet,
    VerificacionPermisoViewSet,
)

# Router principal para recursos CRUD estándar
router = DefaultRouter()
router.register(r'funciones', FuncionViewSet, basename='funcion')
router.register(r'capacidades', CapacidadViewSet, basename='capacidad')
router.register(r'grupos', GrupoPermisoViewSet, basename='grupo-permiso')
router.register(r'excepcionales', PermisoExcepcionalViewSet, basename='permiso-excepcional')
router.register(r'auditoria', AuditoriaPermisoViewSet, basename='auditoria-permiso')
router.register(r'verificar', VerificacionPermisoViewSet, basename='verificar-permiso')

urlpatterns = [
    path('', include(router.urls)),
]
