"""
Migracion para tabla de configuracion de dashboards.

Crea tabla dashboard_configuracion para personalizacion por usuario.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 31)
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
        # Tabla: dashboard_configuracion
        migrations.CreateModel(
            name='DashboardConfiguracion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                    related_name='dashboard_configuracion',
                    help_text='Usuario dueno de la configuracion',
                )),
                ('configuracion', models.JSONField(
                    default=dict,
                    help_text='Configuracion de widgets y layout en formato JSON',
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    help_text='Fecha de ultima actualizacion',
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    help_text='Fecha de creacion',
                )),
            ],
            options={
                'db_table': 'dashboard_configuracion',
                'verbose_name': 'Configuracion de Dashboard',
                'verbose_name_plural': 'Configuraciones de Dashboards',
                'ordering': ['-updated_at'],
            },
        ),
    ]
