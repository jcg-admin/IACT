"""Serializers para API REST de configuración."""

from rest_framework import serializers

from .models import AuditoriaConfiguracion, ConfiguracionSistema


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    """Serializer para configuraciones del sistema."""

    modificado_por_username = serializers.CharField(
        source='modificado_por.username',
        read_only=True
    )

    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id', 'clave', 'valor', 'tipo', 'descripcion',
            'valor_default', 'modificado_por', 'modificado_por_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'modificado_por']


class ModificarConfiguracionSerializer(serializers.Serializer):
    """Serializer para modificar una configuración."""

    nuevo_valor = serializers.CharField(
        help_text='Nuevo valor para la configuración'
    )

    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Razón del cambio (opcional)'
    )


class ImportarConfiguracionSerializer(serializers.Serializer):
    """Serializer para importar configuraciones."""

    json_data = serializers.CharField(
        help_text='JSON con array de configuraciones'
    )


class AuditoriaConfiguracionSerializer(serializers.ModelSerializer):
    """Serializer para auditoría de configuraciones."""

    configuracion_clave = serializers.CharField(
        source='configuracion.clave',
        read_only=True
    )

    modificado_por_username = serializers.CharField(
        source='modificado_por.username',
        read_only=True
    )

    class Meta:
        model = AuditoriaConfiguracion
        fields = [
            'id', 'configuracion', 'configuracion_clave',
            'valor_anterior', 'valor_nuevo', 'modificado_por',
            'modificado_por_username', 'timestamp', 'motivo'
        ]
        read_only_fields = fields
