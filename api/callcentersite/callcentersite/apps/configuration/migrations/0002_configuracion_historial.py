"""
Migracion para tabla de historial de configuraciones.

Crea tabla configuracion_historial para auditoria de cambios.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 7)
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Tabla: configuracion_historial
        migrations.CreateModel(
            name='ConfiguracionHistorial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('configuracion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='configuration.configuracion',
                    related_name='historial',
                    help_text='Configuracion modificada',
                )),
                ('clave', models.CharField(
                    max_length=100,
                    db_index=True,
                    help_text='Clave de la configuracion (desnormalizado para historico)',
                )),
                ('valor_anterior', models.TextField(
                    help_text='Valor antes del cambio',
                )),
                ('valor_nuevo', models.TextField(
                    help_text='Valor despues del cambio',
                )),
                ('modificado_por', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    null=True,
                    blank=True,
                    related_name='modificaciones_configuracion',
                    help_text='Usuario que realizo el cambio',
                )),
                ('timestamp', models.DateTimeField(
                    auto_now_add=True,
                    db_index=True,
                    help_text='Fecha y hora del cambio',
                )),
                ('ip_address', models.GenericIPAddressField(
                    null=True,
                    blank=True,
                    help_text='Direccion IP desde donde se realizo el cambio',
                )),
                ('user_agent', models.CharField(
                    max_length=255,
                    blank=True,
                    help_text='User agent del navegador',
                )),
            ],
            options={
                'db_table': 'configuracion_historial',
                'verbose_name': 'Historial de Configuracion',
                'verbose_name_plural': 'Historial de Configuraciones',
                'ordering': ['-timestamp'],
            },
        ),

        # Indices adicionales
        migrations.AddIndex(
            model_name='configuracionhistorial',
            index=models.Index(fields=['clave', '-timestamp'], name='config_hist_clave_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='configuracionhistorial',
            index=models.Index(fields=['modificado_por', '-timestamp'], name='config_hist_user_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='configuracionhistorial',
            index=models.Index(fields=['-timestamp'], name='config_hist_ts_idx'),
        ),
    ]
