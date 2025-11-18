"""
Modelos Django para el sistema de permisos granular.

Implementa el sistema basado en Grupos Funcionales sin jerarquias.

Referencia: docs/backend/requisitos/prioridad_01_estructura_base_datos.md

NOTA: Estos modelos usan Django ORM real y requieren base de datos PostgreSQL.
Los modelos in-memory existentes (models.py) se mantienen para compatibilidad.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Funcion(models.Model):
    """
    Funcion del sistema (recurso).

    Ejemplos: dashboards, usuarios, metricas, reportes.
    """

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=100,
        help_text='Nombre corto: dashboards, usuarios',
    )
    nombre_completo = models.CharField(
        max_length=200,
        unique=True,
        help_text='Nombre completo: sistema.vistas.dashboards',
    )
    dominio = models.CharField(
        max_length=100,
        help_text='Dominio: vistas, administracion, operaciones',
    )
    categoria = models.CharField(
        max_length=50,
        help_text='Categoria funcional',
    )
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    orden_menu = models.IntegerField(default=999)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relacion N:M con Capacidades (through FuncionCapacidad)
    capacidades = models.ManyToManyField(
        'Capacidad',
        through='FuncionCapacidad',
        related_name='funciones',
    )

    class Meta:
        db_table = 'funciones'
        verbose_name = 'Funcion'
        verbose_name_plural = 'Funciones'
        ordering = ['orden_menu', 'nombre']

    def __str__(self):
        return self.nombre_completo


class Capacidad(models.Model):
    """
    Capacidad granular (accion sobre recurso).

    Ejemplos:
    - sistema.administracion.usuarios.crear
    - sistema.vistas.dashboards.ver
    - sistema.operaciones.llamadas.realizar
    """

    NIVEL_RIESGO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('critico', 'Critico'),
    ]

    id = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=200,
        unique=True,
        help_text='Codigo completo: sistema.administracion.usuarios.crear',
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    requiere_aprobacion = models.BooleanField(default=False)
    nivel_riesgo = models.CharField(
        max_length=20,
        choices=NIVEL_RIESGO_CHOICES,
        default='bajo',
    )
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'capacidades'
        verbose_name = 'Capacidad'
        verbose_name_plural = 'Capacidades'
        ordering = ['codigo']

    def __str__(self):
        return self.codigo


class FuncionCapacidad(models.Model):
    """
    Relacion N:M entre Funciones y Capacidades.

    Define que capacidades pertenecen a cada funcion.
    """

    id = models.AutoField(primary_key=True)
    funcion = models.ForeignKey(
        Funcion,
        on_delete=models.CASCADE,
        related_name='funciones_capacidades',
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
        related_name='capacidades_funciones',
    )
    es_requerida = models.BooleanField(
        default=True,
        help_text='Si es requerida para acceder a la funcion',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'funcion_capacidades'
        verbose_name = 'Funcion-Capacidad'
        verbose_name_plural = 'Funciones-Capacidades'
        unique_together = [['funcion', 'capacidad']]

    def __str__(self):
        return f'{self.funcion.nombre} - {self.capacidad.codigo}'


class GrupoPermiso(models.Model):
    """
    Grupo funcional de permisos (sin jerarquia).

    Ejemplos:
    - administracion_usuarios
    - atencion_cliente
    - gestion_equipos
    """

    NIVEL_RIESGO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('critico', 'Critico'),
    ]

    id = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=100,
        unique=True,
        help_text='Codigo: administracion_usuarios, atencion_cliente',
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(
        max_length=50,
        help_text='tecnico, operativo, gestion',
    )
    requiere_aprobacion = models.BooleanField(default=False)
    nivel_riesgo = models.CharField(
        max_length=20,
        choices=NIVEL_RIESGO_CHOICES,
        default='bajo',
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relacion N:M con Capacidades (through GrupoCapacidad)
    capacidades = models.ManyToManyField(
        'Capacidad',
        through='GrupoCapacidad',
        related_name='grupos',
    )

    class Meta:
        db_table = 'grupos_permisos'
        verbose_name = 'Grupo de Permisos'
        verbose_name_plural = 'Grupos de Permisos'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return self.nombre


class GrupoCapacidad(models.Model):
    """
    Relacion N:M entre Grupos y Capacidades.

    Define que capacidades tiene cada grupo.
    """

    id = models.AutoField(primary_key=True)
    grupo = models.ForeignKey(
        GrupoPermiso,
        on_delete=models.CASCADE,
        related_name='grupos_capacidades',
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
        related_name='capacidades_grupos',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'grupo_capacidades'
        verbose_name = 'Grupo-Capacidad'
        verbose_name_plural = 'Grupos-Capacidades'
        unique_together = [['grupo', 'capacidad']]

    def __str__(self):
        return f'{self.grupo.codigo} - {self.capacidad.codigo}'


class UsuarioGrupo(models.Model):
    """
    Relacion N:M entre Usuarios y Grupos.

    Un usuario puede tener multiples grupos.
    Soporta asignaciones temporales con fecha_expiracion.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuario_grupos',
    )
    grupo = models.ForeignKey(
        GrupoPermiso,
        on_delete=models.CASCADE,
        related_name='grupo_usuarios',
    )
    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asignaciones_realizadas',
    )
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='NULL = permanente',
    )
    activo = models.BooleanField(default=True)
    motivo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'usuarios_grupos'
        verbose_name = 'Usuario-Grupo'
        verbose_name_plural = 'Usuarios-Grupos'
        unique_together = [['usuario', 'grupo']]
        indexes = [
            models.Index(fields=['usuario', 'activo'], name='idx_usuario_activo'),
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.grupo.codigo}'


class PermisoExcepcional(models.Model):
    """
    Permisos excepcionales (temporales o permanentes).

    Permite otorgar capacidades individuales a usuarios
    sin necesidad de asignar grupos completos.
    """

    TIPO_CHOICES = [
        ('temporal', 'Temporal'),
        ('permanente', 'Permanente'),
    ]

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permisos_excepcionales',
    )
    capacidad = models.ForeignKey(
        Capacidad,
        on_delete=models.CASCADE,
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='temporal',
    )
    otorgado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permisos_otorgados',
    )
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    motivo = models.TextField()
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'permisos_excepcionales'
        verbose_name = 'Permiso Excepcional'
        verbose_name_plural = 'Permisos Excepcionales'
        indexes = [
            models.Index(fields=['usuario', 'activo'], name='idx_permiso_exc_usuario'),
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.capacidad.codigo} ({self.tipo})'


class AuditoriaPermiso(models.Model):
    """
    Log de auditoria de accesos y cambios de permisos.

    Registra:
    - Accesos permitidos/denegados
    - Asignaciones de grupos
    - Permisos excepcionales
    """

    ACCION_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('asignacion_grupo', 'Asignacion de Grupo'),
        ('revocacion_grupo', 'Revocacion de Grupo'),
        ('permiso_excepcional', 'Permiso Excepcional'),
    ]

    RESULTADO_CHOICES = [
        ('exito', 'Exito'),
        ('fallo', 'Fallo'),
        ('permitido', 'Permitido'),
        ('denegado', 'Denegado'),
    ]

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    capacidad_codigo = models.CharField(max_length=200)
    recurso_tipo = models.CharField(max_length=100, default='', blank=True)
    recurso_id = models.CharField(max_length=100, null=True, blank=True)
    accion = models.CharField(max_length=50, choices=ACCION_CHOICES)
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES)
    razon = models.TextField(blank=True, default='')
    detalles = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    contexto_adicional = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'auditoria_permisos'
        verbose_name = 'Auditoria de Permiso'
        verbose_name_plural = 'Auditorias de Permisos'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp'], name='idx_auditoria_usuario_time'),
            models.Index(fields=['capacidad_codigo', 'timestamp'], name='idx_auditoria_cap_time'),
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.accion} - {self.capacidad_codigo}'
