"""
Serializers para API REST de usuarios.

Validaciones incluidas:
- Formato de email
- Username unico
- Campos requeridos

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 42)
"""

from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models_permisos_granular import GrupoPermiso, UsuarioGrupo

User = get_user_model()


class GrupoPermisoSerializer(serializers.ModelSerializer):
    """Serializer basico para grupos de permisos."""

    class Meta:
        model = GrupoPermiso
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'categoria']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para modelo User con validaciones.

    Campos:
        - id: int (read-only)
        - email: str (requerido, unico, formato email)
        - first_name: str (requerido)
        - last_name: str (requerido)
        - is_active: bool
        - is_staff: bool
        - grupos: list (read-only, calculado desde UsuarioGrupo)
        - created_at: datetime (read-only)
        - last_login: datetime (read-only)
    """

    grupos = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        help_text='Password del usuario (requerido al crear)',
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'grupos',
            'password',
            'created_at',
            'last_login',
        ]
        read_only_fields = ['id', 'created_at', 'last_login', 'grupos']
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False,
            },
            'first_name': {
                'required': True,
                'allow_blank': False,
            },
            'last_name': {
                'required': True,
                'allow_blank': False,
            },
        }

    def get_grupos(self, obj: User) -> list:
        """Obtiene grupos activos del usuario."""
        grupos = UsuarioGrupo.objects.filter(
            usuario=obj,
            activo=True,
        ).select_related('grupo')

        return [
            {
                'codigo': ug.grupo.codigo,
                'nombre': ug.grupo.nombre,
                'asignado_en': ug.asignado_en.isoformat(),
            }
            for ug in grupos
        ]

    def validate_email(self, value: str) -> str:
        """Valida que el email tenga formato correcto y sea unico."""
        # El formato es validado automaticamente por EmailField
        # Solo validar unicidad si es creacion o si cambio el email
        request = self.context.get('request')
        if request and request.method == 'POST':
            # Creacion: validar que no exista
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe un usuario con el email: {value}'
                )
        elif self.instance:
            # Edicion: validar que no exista otro usuario con ese email
            if value != self.instance.email:
                if User.objects.filter(email=value).exists():
                    raise serializers.ValidationError(
                        f'Ya existe un usuario con el email: {value}'
                    )
        return value

    def validate_password(self, value: str) -> str:
        """Valida longitud minima del password."""
        if value and len(value) < 8:
            raise serializers.ValidationError(
                'El password debe tener al menos 8 caracteres'
            )
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Crea usuario con password hasheado."""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data,
        )
        return user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """Actualiza usuario, hasheando password si se proporciona."""
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de usuarios."""

    grupos_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'grupos_count',
            'last_login',
        ]
        read_only_fields = fields

    def get_grupos_count(self, obj: User) -> int:
        """Cuenta grupos activos del usuario."""
        return UsuarioGrupo.objects.filter(
            usuario=obj,
            activo=True,
        ).count()


class AsignarGruposSerializer(serializers.Serializer):
    """
    Serializer para asignar grupos a un usuario.

    Campos:
        - grupos_codigos: list[str] (requerido)
    """

    grupos_codigos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True,
        allow_empty=False,
        help_text='Lista de codigos de grupos a asignar',
    )

    def validate_grupos_codigos(self, value: list) -> list:
        """Valida que todos los grupos existan."""
        for codigo in value:
            if not GrupoPermiso.objects.filter(codigo=codigo).exists():
                raise serializers.ValidationError(
                    f'Grupo no encontrado: {codigo}'
                )
        return value


class SuspenderUsuarioSerializer(serializers.Serializer):
    """
    Serializer para suspender un usuario.

    Campos:
        - motivo: str (opcional)
    """

    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text='Motivo de la suspension',
    )
