"""Serializers para la API de usuarios."""

from __future__ import annotations

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer completo de User para respuestas."""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'status',
            'segment',
            'is_locked',
            'locked_until',
            'lock_reason',
            'failed_login_attempts',
            'last_login_at',
            'last_login_ip',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_locked',
            'locked_until',
            'lock_reason',
            'failed_login_attempts',
            'last_login_at',
            'last_login_ip',
            'is_deleted',
            'created_at',
            'updated_at',
        ]


class CrearUsuarioSerializer(serializers.Serializer):
    """Serializer para UC-014: Crear usuario."""

    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text='Nombre de usuario único'
    )
    email = serializers.EmailField(
        required=True,
        help_text='Email único del usuario'
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text='Contraseña (mínimo 8 caracteres)'
    )
    segment = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default='',
        help_text='Segmento del usuario (GE, VIP, etc.)'
    )


class ActualizarUsuarioSerializer(serializers.Serializer):
    """Serializer para UC-015: Actualizar usuario."""

    email = serializers.EmailField(
        required=False,
        help_text='Nuevo email'
    )
    segment = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text='Nuevo segmento'
    )


class BloquearUsuarioSerializer(serializers.Serializer):
    """Serializer para UC-016: Bloquear usuario."""

    razon = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Razón del bloqueo'
    )


class CambiarContrasenaSerializer(serializers.Serializer):
    """Serializer para UC-019: Cambiar contraseña."""

    contrasena_actual = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Contraseña actual para validar'
    )
    contrasena_nueva = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text='Nueva contraseña (mínimo 8 caracteres)'
    )


class FiltrosUsuariosSerializer(serializers.Serializer):
    """Serializer para UC-018: Filtros de consulta."""

    segment = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Filtrar por segmento'
    )
    is_locked = serializers.BooleanField(
        required=False,
        help_text='Filtrar por estado de bloqueo'
    )
    incluir_eliminados = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Incluir usuarios eliminados'
    )
