"""Vistas del dashboard."""

from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from .services import DashboardService


class DashboardOverviewView(APIView):
    """Devuelve información general del dashboard."""

    def get(self, request):  # type: ignore[override]
        return Response(DashboardService.overview())
