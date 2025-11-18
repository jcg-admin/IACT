from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("users", "0003_create_permission_functions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="permisoexcepcional",
            name="usuario",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="permisos_excepcionales_granular",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
