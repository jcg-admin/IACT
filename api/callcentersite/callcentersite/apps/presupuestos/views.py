from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Presupuesto
from .serializers import PresupuestoSerializer
from .services import PresupuestoService


class PresupuestoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Presupuesto.objects.all()
    serializer_class = PresupuestoSerializer
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        try:
            presupuesto = PresupuestoService.aprobar_presupuesto(pk, request.user.id)
            return Response(PresupuestoSerializer(presupuesto).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        try:
            presupuesto = PresupuestoService.rechazar_presupuesto(pk, request.user.id)
            return Response(PresupuestoSerializer(presupuesto).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def exportar(self, request):
        data = PresupuestoService.exportar_presupuestos()
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="presupuestos.json"'
        return response
