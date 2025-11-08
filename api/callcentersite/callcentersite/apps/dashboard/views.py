"""Vistas del dashboard."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from callcentersite.apps.users.services_permisos_granular import UserManagementService

from .services import DashboardService


class DashboardOverviewView(APIView):
    """Devuelve información general del dashboard.

    Requiere permiso: sistema.vistas.dashboards.ver

    Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 24)
    """

    def get(self, request):  # type: ignore[override]
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=request.user.id,
            capacidad_codigo='sistema.vistas.dashboards.ver',
        )

        if not tiene_permiso:
            raise PermissionDenied(
                'No tiene permiso para ver dashboards'
            )

        return Response(DashboardService.overview())
