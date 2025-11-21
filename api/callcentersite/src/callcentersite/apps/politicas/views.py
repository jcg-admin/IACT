from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Politica
from .serializers import PoliticaSerializer
from .services import PoliticaService


class PoliticaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Politica.objects.all()
    serializer_class = PoliticaSerializer
    
    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        try:
            politica = PoliticaService.publicar_politica(pk, request.user.id)
            return Response(PoliticaSerializer(politica).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        try:
            politica = PoliticaService.archivar_politica(pk)
            return Response(PoliticaSerializer(politica).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def nueva_version(self, request, pk=None):
        try:
            politica = PoliticaService.nueva_version(
                pk, request.data.get('contenido', ''), request.user.id
            )
            return Response(PoliticaSerializer(politica).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
