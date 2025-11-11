"""Serializers para API REST de dashboard."""

from rest_framework import serializers

from .models import DashboardConfiguration


class PersonalizarDashboardSerializer(serializers.Serializer):
    """Serializer para personalizar widgets del dashboard."""

    widgets = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text='Lista ordenada de tipos de widgets'
    )


class ExportarDashboardSerializer(serializers.Serializer):
    """Serializer para exportar dashboard."""

    formato = serializers.ChoiceField(
        choices=['csv', 'pdf'],
        default='csv',
        help_text='Formato de exportación'
    )


class CompartirDashboardSerializer(serializers.Serializer):
    """Serializer para compartir configuración de dashboard."""

    usuario_destino_id = serializers.IntegerField(
        help_text='ID del usuario que recibirá la configuración'
    )


class DashboardConfigurationSerializer(serializers.ModelSerializer):
    """Serializer para configuración de dashboard."""

    class Meta:
        model = DashboardConfiguration
        fields = ['id', 'widgets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
