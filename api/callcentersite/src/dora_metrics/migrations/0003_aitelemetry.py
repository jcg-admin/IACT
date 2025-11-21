"""Migracion para AITelemetry model - TASK-024."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Agregar modelo AITelemetry para telemetria de agentes IA."""

    dependencies = [
        ("dora_metrics", "0002_rename_dora_metric_phase_n_idx_dora_metric_phase_n_ea676d_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AITelemetry",
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
                ("agent_id", models.CharField(db_index=True, max_length=100)),
                ("task_type", models.CharField(db_index=True, max_length=50)),
                ("decision_made", models.JSONField()),
                ("confidence_score", models.DecimalField(decimal_places=4, max_digits=5)),
                ("human_feedback", models.CharField(blank=True, max_length=20, null=True)),
                ("accuracy", models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ("execution_time_ms", models.IntegerField()),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "ai_telemetry",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="aitelemetry",
            index=models.Index(fields=["agent_id"], name="ai_telemetr_agent_i_idx"),
        ),
        migrations.AddIndex(
            model_name="aitelemetry",
            index=models.Index(fields=["task_type"], name="ai_telemetr_task_ty_idx"),
        ),
        migrations.AddIndex(
            model_name="aitelemetry",
            index=models.Index(fields=["created_at"], name="ai_telemetr_created_idx"),
        ),
        migrations.AddIndex(
            model_name="aitelemetry",
            index=models.Index(fields=["human_feedback"], name="ai_telemetr_human_f_idx"),
        ),
    ]
