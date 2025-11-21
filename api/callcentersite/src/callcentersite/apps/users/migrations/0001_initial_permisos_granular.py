"""
Migracion inicial del sistema de permisos granular.

Crea 8 tablas base:
1. funciones - Recursos del sistema
2. capacidades - Acciones granulares
3. funcion_capacidades - Relacion N:M funciones-capacidades
4. grupos_permisos - Grupos funcionales sin jerarquia
5. grupo_capacidades - Relacion N:M grupos-capacidades
6. usuarios_grupos - Relacion N:M usuarios-grupos
7. permisos_excepcionales - Permisos temporales o permanentes
8. auditoria_permisos - Log de accesos

Referencia: docs/backend/requisitos/prioridad_01_estructura_base_datos.md
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Tabla 1: funciones
        migrations.CreateModel(
            name='Funcion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, help_text='Nombre corto: dashboards, usuarios')),
                ('nombre_completo', models.CharField(max_length=200, unique=True, help_text='Nombre completo: sistema.vistas.dashboards')),
                ('dominio', models.CharField(max_length=100, help_text='Dominio: vistas, administracion, operaciones')),
                ('categoria', models.CharField(max_length=50, help_text='Categoria funcional')),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('icono', models.CharField(max_length=50, blank=True, null=True)),
                ('orden_menu', models.IntegerField(default=999)),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'funciones',
                'verbose_name': 'Funcion',
                'verbose_name_plural': 'Funciones',
                'ordering': ['orden_menu', 'nombre'],
            },
        ),

        # Tabla 2: capacidades
        migrations.CreateModel(
            name='Capacidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=200, unique=True, help_text='Codigo completo: sistema.administracion.usuarios.crear')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('requiere_aprobacion', models.BooleanField(default=False)),
                ('nivel_riesgo', models.CharField(
                    max_length=20,
                    choices=[
                        ('bajo', 'Bajo'),
                        ('medio', 'Medio'),
                        ('alto', 'Alto'),
                        ('critico', 'Critico'),
                    ],
                    default='bajo',
                )),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'capacidades',
                'verbose_name': 'Capacidad',
                'verbose_name_plural': 'Capacidades',
                'ordering': ['codigo'],
            },
        ),

        # Tabla 3: funcion_capacidades (relacion N:M)
        migrations.CreateModel(
            name='FuncionCapacidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('funcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.funcion', related_name='funciones_capacidades')),
                ('capacidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.capacidad', related_name='capacidades_funciones')),
                ('es_requerida', models.BooleanField(default=True, help_text='Si es requerida para acceder a la funcion')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'funcion_capacidades',
                'verbose_name': 'Funcion-Capacidad',
                'verbose_name_plural': 'Funciones-Capacidades',
                'unique_together': {('funcion', 'capacidad')},
            },
        ),

        # Tabla 4: grupos_permisos
        migrations.CreateModel(
            name='GrupoPermiso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=100, unique=True, help_text='Codigo: administracion_usuarios, atencion_cliente')),
                ('nombre', models.CharField(max_length=150)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('categoria', models.CharField(max_length=50, help_text='tecnico, operativo, gestion')),
                ('requiere_aprobacion', models.BooleanField(default=False)),
                ('nivel_riesgo', models.CharField(
                    max_length=20,
                    choices=[
                        ('bajo', 'Bajo'),
                        ('medio', 'Medio'),
                        ('alto', 'Alto'),
                        ('critico', 'Critico'),
                    ],
                    default='bajo',
                )),
                ('activo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'grupos_permisos',
                'verbose_name': 'Grupo de Permisos',
                'verbose_name_plural': 'Grupos de Permisos',
                'ordering': ['categoria', 'nombre'],
            },
        ),

        # Tabla 5: grupo_capacidades (relacion N:M)
        migrations.CreateModel(
            name='GrupoCapacidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.grupopermiso', related_name='grupos_capacidades')),
                ('capacidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.capacidad', related_name='capacidades_grupos')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'grupo_capacidades',
                'verbose_name': 'Grupo-Capacidad',
                'verbose_name_plural': 'Grupos-Capacidades',
                'unique_together': {('grupo', 'capacidad')},
            },
        ),

        # Tabla 6: usuarios_grupos (relacion N:M usuarios-grupos)
        migrations.CreateModel(
            name='UsuarioGrupo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, related_name='usuario_grupos')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.grupopermiso', related_name='grupo_usuarios')),
                ('asignado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, related_name='asignaciones_realizadas')),
                ('fecha_asignacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_expiracion', models.DateTimeField(null=True, blank=True, help_text='NULL = permanente')),
                ('activo', models.BooleanField(default=True)),
                ('motivo', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'usuarios_grupos',
                'verbose_name': 'Usuario-Grupo',
                'verbose_name_plural': 'Usuarios-Grupos',
                'unique_together': {('usuario', 'grupo')},
                'indexes': [
                    models.Index(fields=['usuario', 'activo'], name='idx_usuario_activo'),
                ],
            },
        ),

        # Tabla 7: permisos_excepcionales
        migrations.CreateModel(
            name='PermisoExcepcional',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, related_name='permisos_excepcionales')),
                ('capacidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.capacidad')),
                ('tipo', models.CharField(
                    max_length=20,
                    choices=[
                        ('temporal', 'Temporal'),
                        ('permanente', 'Permanente'),
                    ],
                    default='temporal',
                )),
                ('otorgado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, related_name='permisos_otorgados')),
                ('fecha_inicio', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_expiracion', models.DateTimeField(null=True, blank=True)),
                ('motivo', models.TextField()),
                ('activo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'permisos_excepcionales',
                'verbose_name': 'Permiso Excepcional',
                'verbose_name_plural': 'Permisos Excepcionales',
                'indexes': [
                    models.Index(fields=['usuario', 'activo'], name='idx_permiso_exc_usuario'),
                ],
            },
        ),

        # Tabla 8: auditoria_permisos
        migrations.CreateModel(
            name='AuditoriaPermiso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('capacidad_codigo', models.CharField(max_length=200)),
                ('accion', models.CharField(
                    max_length=50,
                    choices=[
                        ('acceso_permitido', 'Acceso Permitido'),
                        ('acceso_denegado', 'Acceso Denegado'),
                        ('asignacion_grupo', 'Asignacion de Grupo'),
                        ('revocacion_grupo', 'Revocacion de Grupo'),
                        ('permiso_excepcional', 'Permiso Excepcional'),
                    ],
                )),
                ('resultado', models.CharField(max_length=20, choices=[('exito', 'Exito'), ('fallo', 'Fallo')])),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('user_agent', models.CharField(max_length=255, blank=True, null=True)),
                ('contexto_adicional', models.JSONField(default=dict, blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'auditoria_permisos',
                'verbose_name': 'Auditoria de Permiso',
                'verbose_name_plural': 'Auditorias de Permisos',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['usuario', 'timestamp'], name='idx_auditoria_usuario_time'),
                    models.Index(fields=['capacidad_codigo', 'timestamp'], name='idx_auditoria_cap_time'),
                ],
            },
        ),

        # Agregar relaciones ManyToMany en modelos
        migrations.AddField(
            model_name='funcion',
            name='capacidades',
            field=models.ManyToManyField(
                to='users.Capacidad',
                through='users.FuncionCapacidad',
                related_name='funciones',
            ),
        ),

        migrations.AddField(
            model_name='grupopermiso',
            name='capacidades',
            field=models.ManyToManyField(
                to='users.Capacidad',
                through='users.GrupoCapacidad',
                related_name='grupos',
            ),
        ),
    ]
