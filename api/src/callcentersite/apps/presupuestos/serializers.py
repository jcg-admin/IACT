from rest_framework import serializers
from .models import Presupuesto


class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = '__all__'
        read_only_fields = ['creado_por', 'aprobado_por', 'created_at', 'updated_at']


class AprobarPresupuestoSerializer(serializers.Serializer):
    pass
