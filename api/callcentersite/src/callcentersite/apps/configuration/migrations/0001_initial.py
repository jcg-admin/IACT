"""
Migracion inicial del sistema de configuracion.

Crea tabla configuracion con parametros del sistema.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 6)
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
        # Tabla: configuracion
        migrations.CreateModel(
            name='Configuracion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('categoria', models.CharField(
                    max_length=50,
                    db_index=True,
                    choices=[
                        ('general', 'General'),
                        ('seguridad', 'Seguridad'),
                        ('notificaciones', 'Notificaciones'),
                        ('integraciones', 'Integraciones'),
                        ('llamadas', 'Llamadas'),
                        ('tickets', 'Tickets'),
                        ('reportes', 'Reportes'),
                        ('sistema', 'Sistema'),
                    ],
                    help_text='Categoria de la configuracion',
                )),
                ('clave', models.CharField(
                    max_length=100,
                    unique=True,
                    db_index=True,
                    help_text='Clave unica de la configuracion',
                )),
                ('valor', models.TextField(
                    help_text='Valor actual de la configuracion',
                )),
                ('tipo_dato', models.CharField(
                    max_length=20,
                    choices=[
                        ('string', 'String'),
                        ('integer', 'Integer'),
                        ('boolean', 'Boolean'),
                        ('float', 'Float'),
                        ('json', 'JSON'),
                        ('email', 'Email'),
                        ('url', 'URL'),
                    ],
                    help_text='Tipo de dato del valor',
                )),
                ('valor_default', models.TextField(
                    help_text='Valor por defecto de la configuracion',
                )),
                ('descripcion', models.TextField(
                    blank=True,
                    help_text='Descripcion de la configuracion',
                )),
                ('activa', models.BooleanField(
                    default=True,
                    db_index=True,
                    help_text='Indica si la configuracion esta activa',
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    help_text='Fecha de ultima actualizacion',
                )),
                ('updated_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    null=True,
                    blank=True,
                    related_name='configuraciones_modificadas',
                    help_text='Usuario que realizo la ultima modificacion',
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    help_text='Fecha de creacion',
                )),
            ],
            options={
                'db_table': 'configuracion',
                'verbose_name': 'Configuracion',
                'verbose_name_plural': 'Configuraciones',
                'ordering': ['categoria', 'clave'],
            },
        ),

        # Indices adicionales
        migrations.AddIndex(
            model_name='configuracion',
            index=models.Index(fields=['categoria', 'activa'], name='config_cat_act_idx'),
        ),
        migrations.AddIndex(
            model_name='configuracion',
            index=models.Index(fields=['clave'], name='config_clave_idx'),
        ),
    ]
