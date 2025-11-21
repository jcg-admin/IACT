"""Migracion inicial para dora_metrics."""

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    """Migracion inicial."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DORAMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cycle_id", models.CharField(max_length=50, unique=True)),
                ("feature_id", models.CharField(max_length=50)),
                ("phase_name", models.CharField(max_length=50)),
                ("decision", models.CharField(max_length=20)),
                ("duration_seconds", models.DecimalField(decimal_places=2, max_digits=10)),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "dora_metrics",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="dorametric",
            index=models.Index(fields=["phase_name"], name="dora_metric_phase_n_idx"),
        ),
        migrations.AddIndex(
            model_name="dorametric",
            index=models.Index(fields=["feature_id"], name="dora_metric_feature_idx"),
        ),
        migrations.AddIndex(
            model_name="dorametric",
            index=models.Index(fields=["created_at"], name="dora_metric_created_idx"),
        ),
    ]
