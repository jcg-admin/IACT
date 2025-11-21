"""
Migracion inicial del sistema de permisos granular.

Sistema de Permisos Granular - Prioridad 1
REF: ADR-012-sistema-permisos-sin-roles-jerarquicos.md

Crea 8 tablas:
1. permissions_funciones
2. permissions_capacidades
3. permissions_funcion_capacidades
4. permissions_grupos_permisos
5. permissions_grupo_capacidades
6. permissions_usuarios_grupos
7. permissions_permisos_excepcionales
8. permissions_auditoria_permisos
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Tabla: funciones
        migrations.CreateModel(
            name='Funcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, help_text='Nombre corto del recurso')),
                ('nombre_completo', models.CharField(max_length=200, unique=True, help_text='Nombre completo: sistema.dominio.recurso')),
                ('descripcion', models.TextField(blank=True, help_text='Descripcion de la funcionalidad')),
                ('dominio', models.CharField(max_length=100, help_text='Dominio al que pertenece (operaciones, finanzas, etc)')),
                ('categoria', models.CharField(max_length=50, blank=True, help_text='Categoria para agrupar en menu')),
                ('icono', models.CharField(max_length=50, blank=True, help_text='Icono para UI')),
                ('orden_menu', models.IntegerField(default=0, help_text='Orden en menu (menor = primero)')),
                ('activa', models.BooleanField(default=True, help_text='Si esta activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Funcion del Sistema',
                'verbose_name_plural': 'Funciones del Sistema',
                'db_table': 'permissions_funciones',
                'ordering': ['orden_menu', 'nombre'],
                'indexes': [
                    models.Index(fields=['dominio'], name='perm_func_dominio_idx'),
                    models.Index(fields=['activa'], name='perm_func_activa_idx'),
                    models.Index(fields=['categoria'], name='perm_func_categoria_idx'),
                ],
            },
        ),

        # 2. Tabla: capacidades
        migrations.CreateModel(
            name='Capacidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_completo', models.CharField(max_length=200, unique=True, help_text='Formato: sistema.dominio.recurso.accion')),
                ('descripcion', models.TextField(blank=True, help_text='Descripcion de la capacidad')),
                ('accion', models.CharField(max_length=50, help_text='Accion (ver, crear, editar, eliminar, aprobar, etc)')),
                ('recurso', models.CharField(max_length=100, help_text='Recurso sobre el que actua')),
                ('dominio', models.CharField(max_length=100, help_text='Dominio del sistema')),
                ('nivel_sensibilidad', models.CharField(
                    max_length=20,
                    default='normal',
                    choices=[
                        ('bajo', 'Bajo'),
                        ('normal', 'Normal'),
                        ('alto', 'Alto'),
                        ('critico', 'Critico')
                    ],
                    help_text='Nivel de sensibilidad de la capacidad'
                )),
                ('requiere_auditoria', models.BooleanField(default=False, help_text='Si accesos deben auditarse')),
                ('activa', models.BooleanField(default=True, help_text='Si esta activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Capacidad',
                'verbose_name_plural': 'Capacidades',
                'db_table': 'permissions_capacidades',
                'ordering': ['dominio', 'recurso', 'accion'],
                'indexes': [
                    models.Index(fields=['accion'], name='perm_cap_accion_idx'),
                    models.Index(fields=['recurso'], name='perm_cap_recurso_idx'),
                    models.Index(fields=['nivel_sensibilidad'], name='perm_cap_sensib_idx'),
                ],
            },
        ),

        # 3. Tabla: grupos_permisos
        migrations.CreateModel(
            name='GrupoPermisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=100, unique=True, help_text='Codigo unico del grupo (snake_case)')),
                ('nombre_display', models.CharField(max_length=200, help_text='Nombre legible para UI')),
                ('descripcion', models.TextField(blank=True, help_text='Descripcion del grupo')),
                ('tipo_acceso', models.CharField(
                    max_length=50,
                    blank=True,
                    choices=[
                        ('operativo', 'Operativo'),
                        ('gestion', 'Gestion'),
                        ('analisis', 'Analisis'),
                        ('estrategico', 'Estrategico'),
                        ('tecnico', 'Tecnico'),
                        ('finanzas', 'Finanzas'),
                        ('calidad', 'Calidad')
                    ],
                    help_text='Tipo de acceso del grupo'
                )),
                ('activo', models.BooleanField(default=True, help_text='Si esta activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Grupo de Permisos',
                'verbose_name_plural': 'Grupos de Permisos',
                'db_table': 'permissions_grupos_permisos',
                'ordering': ['nombre_display'],
            },
        ),

        # 4. Tabla: funcion_capacidades (N:M entre Funcion y Capacidad)
        migrations.CreateModel(
            name='FuncionCapacidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requerida', models.BooleanField(default=False, help_text='Si capacidad es requerida para la funcion')),
                ('visible_en_ui', models.BooleanField(default=True, help_text='Si mostrar en UI')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('funcion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.funcion',
                    related_name='funcion_capacidades'
                )),
                ('capacidad', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.capacidad',
                    related_name='capacidad_funciones'
                )),
            ],
            options={
                'verbose_name': 'Funcion-Capacidad',
                'verbose_name_plural': 'Funciones-Capacidades',
                'db_table': 'permissions_funcion_capacidades',
                'unique_together': {('funcion', 'capacidad')},
            },
        ),

        # 5. Tabla: grupo_capacidades (N:M entre GrupoPermisos y Capacidad)
        migrations.CreateModel(
            name='GrupoCapacidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('grupo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.grupopermisos',
                    related_name='grupo_capacidades'
                )),
                ('capacidad', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.capacidad',
                    related_name='capacidad_grupos'
                )),
            ],
            options={
                'verbose_name': 'Grupo-Capacidad',
                'verbose_name_plural': 'Grupos-Capacidades',
                'db_table': 'permissions_grupo_capacidades',
                'unique_together': {('grupo', 'capacidad')},
            },
        ),

        # 6. Tabla: usuarios_grupos (N:M entre User y GrupoPermisos)
        migrations.CreateModel(
            name='UsuarioGrupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField(null=True, blank=True, help_text='Fecha de expiracion (opcional)')),
                ('activo', models.BooleanField(default=True, help_text='Si asignacion esta activa')),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                    related_name='usuario_grupos'
                )),
                ('grupo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.grupopermisos',
                    related_name='grupo_usuarios'
                )),
                ('asignado_por', models.ForeignKey(
                    null=True,
                    blank=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    related_name='asignaciones_realizadas'
                )),
            ],
            options={
                'verbose_name': 'Usuario-Grupo',
                'verbose_name_plural': 'Usuarios-Grupos',
                'db_table': 'permissions_usuarios_grupos',
                'unique_together': {('usuario', 'grupo')},
            },
        ),

        # 7. Tabla: permisos_excepcionales
        migrations.CreateModel(
            name='PermisoExcepcional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    max_length=20,
                    choices=[
                        ('conceder', 'Conceder'),
                        ('revocar', 'Revocar')
                    ],
                    help_text='Tipo de permiso excepcional'
                )),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True)),
                ('fecha_fin', models.DateTimeField(null=True, blank=True, help_text='Fecha de fin (opcional)')),
                ('motivo', models.TextField(help_text='Razon del permiso excepcional')),
                ('activo', models.BooleanField(default=True, help_text='Si esta activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                    related_name='permisos_excepcionales'
                )),
                ('capacidad', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='permissions.capacidad',
                    related_name='excepciones'
                )),
                ('autorizado_por', models.ForeignKey(
                    null=True,
                    blank=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    related_name='autorizaciones_excepcionales'
                )),
            ],
            options={
                'verbose_name': 'Permiso Excepcional',
                'verbose_name_plural': 'Permisos Excepcionales',
                'db_table': 'permissions_permisos_excepcionales',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['usuario', 'activo'], name='perm_exc_usr_activo_idx'),
                ],
            },
        ),

        # 8. Tabla: auditoria_permisos
        migrations.CreateModel(
            name='AuditoriaPermiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capacidad', models.CharField(max_length=200, help_text='Capacidad utilizada')),
                ('accion_realizada', models.CharField(max_length=100, help_text='Accion realizada')),
                ('recurso_accedido', models.CharField(max_length=200, blank=True, null=True, help_text='ID del recurso accedido')),
                ('ip_address', models.CharField(max_length=50, blank=True, null=True, help_text='IP del usuario')),
                ('user_agent', models.TextField(blank=True, null=True, help_text='User agent del navegador')),
                ('metadata', models.JSONField(default=dict, blank=True, help_text='Metadatos adicionales')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    related_name='auditorias_permisos'
                )),
            ],
            options={
                'verbose_name': 'Auditoria de Permiso',
                'verbose_name_plural': 'Auditorias de Permisos',
                'db_table': 'permissions_auditoria_permisos',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['usuario'], name='perm_aud_usuario_idx'),
                    models.Index(fields=['timestamp'], name='perm_aud_timestamp_idx'),
                    models.Index(fields=['accion_realizada'], name='perm_aud_accion_idx'),
                ],
            },
        ),
    ]
