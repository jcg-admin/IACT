"""
Serializers para API REST del sistema de permisos granular.

Incluye serializers para:
- Funciones
- Capacidades
- Grupos de Permisos
- Permisos Excepcionales
- Auditoría

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models_permisos_granular import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermiso,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)

User = get_user_model()


# =============================================================================
# FUNCION SERIALIZERS
# =============================================================================

class FuncionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de funciones."""

    capacidades_count = serializers.SerializerMethodField()

    class Meta:
        model = Funcion
        fields = [
            'id',
            'nombre',
            'nombre_completo',
            'dominio',
            'categoria',
            'orden_menu',
            'activa',
            'capacidades_count',
        ]
        read_only_fields = fields

    def get_capacidades_count(self, obj):
        """Cuenta capacidades asociadas."""
        return obj.capacidades.filter(activa=True).count()


class FuncionDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de función."""

    capacidades = serializers.SerializerMethodField()

    class Meta:
        model = Funcion
        fields = [
            'id',
            'nombre',
            'nombre_completo',
            'dominio',
            'categoria',
            'descripcion',
            'icono',
            'orden_menu',
            'activa',
            'capacidades',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_capacidades(self, obj):
        """Obtiene capacidades de la función."""
        capacidades = obj.capacidades.filter(activa=True)
        return CapacidadListSerializer(capacidades, many=True).data


class FuncionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar funciones."""

    class Meta:
        model = Funcion
        fields = [
            'nombre',
            'nombre_completo',
            'dominio',
            'categoria',
            'descripcion',
            'icono',
            'orden_menu',
            'activa',
        ]

    def validate_nombre_completo(self, value):
        """Valida que nombre_completo sea único."""
        instance = self.instance
        if instance:
            # Actualización: verificar que no exista otro con ese nombre
            if Funcion.objects.filter(nombre_completo=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError(
                    f'Ya existe una función con el nombre completo: {value}'
                )
        else:
            # Creación: verificar que no exista
            if Funcion.objects.filter(nombre_completo=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe una función con el nombre completo: {value}'
                )
        return value


# =============================================================================
# CAPACIDAD SERIALIZERS
# =============================================================================

class CapacidadListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de capacidades."""

    funciones_count = serializers.SerializerMethodField()

    class Meta:
        model = Capacidad
        fields = [
            'id',
            'codigo',
            'nombre',
            'nivel_riesgo',
            'requiere_aprobacion',
            'activa',
            'funciones_count',
        ]
        read_only_fields = fields

    def get_funciones_count(self, obj):
        """Cuenta funciones asociadas."""
        return obj.funciones.filter(activa=True).count()


class CapacidadDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de capacidad."""

    funciones = serializers.SerializerMethodField()
    grupos_count = serializers.SerializerMethodField()

    class Meta:
        model = Capacidad
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'requiere_aprobacion',
            'nivel_riesgo',
            'activa',
            'funciones',
            'grupos_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_funciones(self, obj):
        """Obtiene funciones que incluyen esta capacidad."""
        funciones = obj.funciones.filter(activa=True)
        return FuncionListSerializer(funciones, many=True).data

    def get_grupos_count(self, obj):
        """Cuenta grupos que tienen esta capacidad."""
        return obj.grupos.filter(activo=True).count()


class CapacidadCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar capacidades."""

    class Meta:
        model = Capacidad
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'requiere_aprobacion',
            'nivel_riesgo',
            'activa',
        ]

    def validate_codigo(self, value):
        """Valida que codigo sea único."""
        instance = self.instance
        if instance:
            # Actualización: verificar que no exista otro con ese código
            if Capacidad.objects.filter(codigo=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError(
                    f'Ya existe una capacidad con el código: {value}'
                )
        else:
            # Creación: verificar que no exista
            if Capacidad.objects.filter(codigo=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe una capacidad con el código: {value}'
                )
        return value

    def validate_nivel_riesgo(self, value):
        """Valida que nivel_riesgo sea válido."""
        valid_choices = [choice[0] for choice in Capacidad.NIVEL_RIESGO_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f'Nivel de riesgo inválido. Opciones: {", ".join(valid_choices)}'
            )
        return value


# =============================================================================
# GRUPO PERMISO SERIALIZERS
# =============================================================================

class GrupoPermisoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de grupos."""

    capacidades_count = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = GrupoPermiso
        fields = [
            'id',
            'codigo',
            'nombre',
            'categoria',
            'nivel_riesgo',
            'activo',
            'capacidades_count',
            'usuarios_count',
        ]
        read_only_fields = fields

    def get_capacidades_count(self, obj):
        """Cuenta capacidades del grupo."""
        return obj.capacidades.filter(activa=True).count()

    def get_usuarios_count(self, obj):
        """Cuenta usuarios activos en el grupo."""
        return UsuarioGrupo.objects.filter(grupo=obj, activo=True).count()


class GrupoPermisoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de grupo."""

    capacidades = serializers.SerializerMethodField()
    usuarios = serializers.SerializerMethodField()

    class Meta:
        model = GrupoPermiso
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'requiere_aprobacion',
            'nivel_riesgo',
            'activo',
            'capacidades',
            'usuarios',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_capacidades(self, obj):
        """Obtiene capacidades del grupo."""
        capacidades = obj.capacidades.filter(activa=True)
        return CapacidadListSerializer(capacidades, many=True).data

    def get_usuarios(self, obj):
        """Obtiene usuarios activos del grupo."""
        usuarios_grupos = UsuarioGrupo.objects.filter(
            grupo=obj,
            activo=True
        ).select_related('usuario')

        return [
            {
                'id': ug.usuario.id,
                'email': ug.usuario.email,
                'first_name': ug.usuario.first_name,
                'last_name': ug.usuario.last_name,
                'fecha_asignacion': ug.fecha_asignacion.isoformat(),
                'fecha_expiracion': ug.fecha_expiracion.isoformat() if ug.fecha_expiracion else None,
            }
            for ug in usuarios_grupos
        ]


class GrupoPermisoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar grupos."""

    capacidades_codigos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
        help_text='Lista de códigos de capacidades a asignar'
    )

    class Meta:
        model = GrupoPermiso
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'requiere_aprobacion',
            'nivel_riesgo',
            'activo',
            'capacidades_codigos',
        ]

    def validate_codigo(self, value):
        """Valida que codigo sea único."""
        instance = self.instance
        if instance:
            if GrupoPermiso.objects.filter(codigo=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError(
                    f'Ya existe un grupo con el código: {value}'
                )
        else:
            if GrupoPermiso.objects.filter(codigo=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe un grupo con el código: {value}'
                )
        return value

    def validate_capacidades_codigos(self, value):
        """Valida que todas las capacidades existan."""
        if value:
            for codigo in value:
                if not Capacidad.objects.filter(codigo=codigo, activa=True).exists():
                    raise serializers.ValidationError(
                        f'Capacidad no encontrada o inactiva: {codigo}'
                    )
        return value

    def create(self, validated_data):
        """Crea grupo y asigna capacidades."""
        capacidades_codigos = validated_data.pop('capacidades_codigos', [])
        grupo = GrupoPermiso.objects.create(**validated_data)

        # Asignar capacidades
        if capacidades_codigos:
            capacidades = Capacidad.objects.filter(codigo__in=capacidades_codigos)
            for capacidad in capacidades:
                GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad)

        return grupo

    def update(self, instance, validated_data):
        """Actualiza grupo y capacidades."""
        capacidades_codigos = validated_data.pop('capacidades_codigos', None)

        # Actualizar campos del grupo
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar capacidades si se proporcionaron
        if capacidades_codigos is not None:
            # Eliminar capacidades actuales
            GrupoCapacidad.objects.filter(grupo=instance).delete()

            # Asignar nuevas capacidades
            capacidades = Capacidad.objects.filter(codigo__in=capacidades_codigos)
            for capacidad in capacidades:
                GrupoCapacidad.objects.create(grupo=instance, capacidad=capacidad)

        return instance


# =============================================================================
# PERMISO EXCEPCIONAL SERIALIZERS
# =============================================================================

class PermisoExcepcionalListSerializer(serializers.ModelSerializer):
    """Serializer para listados de permisos excepcionales."""

    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    capacidad_codigo = serializers.CharField(source='capacidad.codigo', read_only=True)
    otorgado_por_email = serializers.CharField(source='otorgado_por.email', read_only=True)

    class Meta:
        model = PermisoExcepcional
        fields = [
            'id',
            'usuario_email',
            'capacidad_codigo',
            'tipo',
            'fecha_inicio',
            'fecha_expiracion',
            'activo',
            'otorgado_por_email',
            'created_at',
        ]
        read_only_fields = fields


class PermisoExcepcionalDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de permiso excepcional."""

    usuario = serializers.SerializerMethodField()
    capacidad = serializers.SerializerMethodField()
    otorgado_por = serializers.SerializerMethodField()

    class Meta:
        model = PermisoExcepcional
        fields = [
            'id',
            'usuario',
            'capacidad',
            'tipo',
            'fecha_inicio',
            'fecha_expiracion',
            'motivo',
            'activo',
            'otorgado_por',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_usuario(self, obj):
        return {
            'id': obj.usuario.id,
            'email': obj.usuario.email,
            'first_name': obj.usuario.first_name,
            'last_name': obj.usuario.last_name,
        }

    def get_capacidad(self, obj):
        return {
            'id': obj.capacidad.id,
            'codigo': obj.capacidad.codigo,
            'nombre': obj.capacidad.nombre,
            'nivel_riesgo': obj.capacidad.nivel_riesgo,
        }

    def get_otorgado_por(self, obj):
        if obj.otorgado_por:
            return {
                'id': obj.otorgado_por.id,
                'email': obj.otorgado_por.email,
            }
        return None


class PermisoExcepcionalCreateSerializer(serializers.Serializer):
    """Serializer para otorgar permiso excepcional."""

    usuario_id = serializers.IntegerField(required=True)
    capacidad_codigo = serializers.CharField(max_length=200, required=True)
    tipo = serializers.ChoiceField(
        choices=PermisoExcepcional.TIPO_CHOICES,
        default='temporal'
    )
    fecha_inicio = serializers.DateTimeField(required=False)
    fecha_expiracion = serializers.DateTimeField(required=False, allow_null=True)
    motivo = serializers.CharField(required=True)

    def validate_usuario_id(self, value):
        """Valida que el usuario exista."""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'Usuario no encontrado: {value}')
        return value

    def validate_capacidad_codigo(self, value):
        """Valida que la capacidad exista."""
        if not Capacidad.objects.filter(codigo=value, activa=True).exists():
            raise serializers.ValidationError(
                f'Capacidad no encontrada o inactiva: {value}'
            )
        return value

    def validate(self, data):
        """Validaciones cruzadas."""
        if data['tipo'] == 'temporal' and not data.get('fecha_expiracion'):
            raise serializers.ValidationError(
                'Los permisos temporales requieren fecha_expiracion'
            )
        return data


# =============================================================================
# AUDITORIA SERIALIZERS
# =============================================================================

class AuditoriaPermisoSerializer(serializers.ModelSerializer):
    """Serializer para auditoría de permisos (read-only)."""

    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = AuditoriaPermiso
        fields = [
            'id',
            'usuario_email',
            'capacidad_codigo',
            'accion',
            'resultado',
            'ip_address',
            'user_agent',
            'contexto_adicional',
            'timestamp',
        ]
        read_only_fields = fields


# =============================================================================
# VERIFICATION SERIALIZERS (Custom endpoints)
# =============================================================================

class UsuarioCapacidadesSerializer(serializers.Serializer):
    """Serializer para respuesta de capacidades de usuario."""

    usuario_id = serializers.IntegerField()
    capacidades = serializers.ListField(child=serializers.CharField())
    total = serializers.IntegerField()


class VerificarPermisoSerializer(serializers.Serializer):
    """Serializer para respuesta de verificación de permiso."""

    usuario_id = serializers.IntegerField()
    capacidad_codigo = serializers.CharField()
    tiene_permiso = serializers.BooleanField()
    origen = serializers.CharField(required=False)


class MenuUsuarioSerializer(serializers.Serializer):
    """Serializer para respuesta de menú dinámico."""

    usuario_id = serializers.IntegerField()
    menu = serializers.JSONField()
