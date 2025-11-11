"""Vistas API REST para configuración del sistema."""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import (
    AuditoriaConfiguracionSerializer,
    ConfiguracionSistemaSerializer,
    ImportarConfiguracionSerializer,
    ModificarConfiguracionSerializer,
)
from .services import ConfigService


class ConfiguracionViewSet(ViewSet):
    """
    ViewSet para gestión de configuraciones del sistema.

    Endpoints:
    - GET /api/v1/configuracion/ - Listar todas las configuraciones
    - GET /api/v1/configuracion/{clave}/ - Ver configuración específica
    - PATCH /api/v1/configuracion/{clave}/modificar/ - Modificar configuración
    - POST /api/v1/configuracion/exportar/ - Exportar a JSON
    - POST /api/v1/configuracion/importar/ - Importar desde JSON
    - GET /api/v1/configuracion/{clave}/historial/ - Ver historial de cambios
    - GET /api/v1/configuracion/auditar/ - Ver historial completo
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/configuracion/ - Listar todas las configuraciones.

        Retorna lista completa de configuraciones del sistema.
        """
        try:
            configs = ConfigService.listar_configuraciones()
            serializer = ConfiguracionSistemaSerializer(configs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        GET /api/v1/configuracion/{clave}/ - Ver configuración específica.

        Args:
            pk: Clave de la configuración (no es ID numérico)
        """
        try:
            config = ConfigService.ver_configuracion(clave=pk)
            serializer = ConfiguracionSistemaSerializer(config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'])
    def modificar(self, request, pk=None):
        """
        PATCH /api/v1/configuracion/{clave}/modificar/ - Modificar configuración.

        Body:
        {
            "nuevo_valor": "valor",
            "motivo": "razón del cambio (opcional)"
        }
        """
        serializer = ModificarConfiguracionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            config = ConfigService.modificar_configuracion(
                clave=pk,
                nuevo_valor=serializer.validated_data['nuevo_valor'],
                usuario_id=request.user.id,
                motivo=serializer.validated_data.get('motivo', '')
            )
            return Response(
                {
                    'message': f'Configuración {pk} actualizada exitosamente',
                    'config': ConfiguracionSistemaSerializer(config).data
                },
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
        POST /api/v1/configuracion/exportar/ - Exportar todas las configuraciones.

        Retorna archivo JSON para descarga.
        """
        try:
            json_data = ConfigService.exportar_configuracion()
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="configuracion.json"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def importar(self, request):
        """
        POST /api/v1/configuracion/importar/ - Importar configuraciones.

        Body:
        {
            "json_data": "[{\"clave\": \"param1\", ...}]"
        }
        """
        serializer = ImportarConfiguracionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resultado = ConfigService.importar_configuracion(
                json_data=serializer.validated_data['json_data'],
                usuario_id=request.user.id
            )
            return Response(
                {
                    'message': 'Configuraciones importadas exitosamente',
                    'resultado': resultado
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """
        GET /api/v1/configuracion/{clave}/historial/ - Ver historial de configuración.

        Retorna historial de cambios de una configuración específica.
        """
        try:
            historial = ConfigService.ver_historial_configuracion(clave=pk)
            serializer = AuditoriaConfiguracionSerializer(historial, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def auditar(self, request):
        """
        GET /api/v1/configuracion/auditar/ - Ver historial completo.

        Retorna todo el historial de cambios de todas las configuraciones.
        """
        try:
            historial = ConfigService.ver_historial_completo()
            serializer = AuditoriaConfiguracionSerializer(historial, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
