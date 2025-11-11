"""Vistas del dashboard."""

from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .serializers import (
    CompartirDashboardSerializer,
    ExportarDashboardSerializer,
    PersonalizarDashboardSerializer,
)
from .services import DashboardService


class DashboardOverviewView(APIView):
    """Devuelve información general del dashboard (legacy)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):  # type: ignore[override]
        return Response(DashboardService.overview())


class DashboardViewSet(ViewSet):
    """
    ViewSet para gestión de dashboards personalizados.

    Endpoints:
    - GET /api/v1/dashboard/ - Ver dashboard personal
    - POST /api/v1/dashboard/personalizar/ - Personalizar widgets
    - POST /api/v1/dashboard/exportar/ - Exportar dashboard
    - POST /api/v1/dashboard/compartir/ - Compartir configuración
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/dashboard/ - Ver dashboard personal.

        Retorna el dashboard personalizado del usuario autenticado.
        """
        try:
            dashboard = DashboardService.ver_dashboard(usuario_id=request.user.id)
            return Response(dashboard, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def personalizar(self, request):
        """
        POST /api/v1/dashboard/personalizar/ - Personalizar widgets.

        Body:
        {
            "widgets": ["total_calls", "avg_duration"]
        }
        """
        serializer = PersonalizarDashboardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            config = DashboardService.personalizar_dashboard(
                usuario_id=request.user.id,
                widgets=serializer.validated_data['widgets']
            )
            return Response(
                {'message': 'Dashboard personalizado exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def exportar(self, request):
        """
        POST /api/v1/dashboard/exportar/ - Exportar dashboard.

        Body:
        {
            "formato": "csv"  // o "pdf"
        }
        """
        serializer = ExportarDashboardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            formato = serializer.validated_data['formato']
            data = DashboardService.exportar_dashboard(
                usuario_id=request.user.id,
                formato=formato
            )

            if formato == 'csv':
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="dashboard.csv"'
            else:  # pdf
                response = HttpResponse(data, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="dashboard.pdf"'

            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def compartir(self, request):
        """
        POST /api/v1/dashboard/compartir/ - Compartir configuración.

        Body:
        {
            "usuario_destino_id": 123
        }
        """
        serializer = CompartirDashboardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            config = DashboardService.compartir_dashboard(
                usuario_origen_id=request.user.id,
                usuario_destino_id=serializer.validated_data['usuario_destino_id']
            )
            return Response(
                {'message': 'Dashboard compartido exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
