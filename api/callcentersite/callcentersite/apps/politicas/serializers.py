from rest_framework import serializers
from .models import Politica


class PoliticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Politica
        fields = '__all__'
        read_only_fields = ['creado_por', 'publicado_por', 'created_at', 'updated_at', 'version']
