"""Modelos para metricas DORA."""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class DORAMetric(models.Model):
    """Metricas DORA para rastreo de performance del equipo."""

    cycle_id = models.CharField(max_length=50, unique=True)
    feature_id = models.CharField(max_length=50)
    phase_name = models.CharField(max_length=50)  # planning, testing, deployment, maintenance
    decision = models.CharField(max_length=20)    # go, no-go, review, blocked
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "dora_metrics"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phase_name"]),
            models.Index(fields=["feature_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.cycle_id} - {self.phase_name}"


class AITelemetry(models.Model):
    """Telemetria para rastrear decisiones y performance de agentes IA."""

    agent_id = models.CharField(max_length=100, db_index=True)
    task_type = models.CharField(max_length=50, db_index=True)
    decision_made = models.JSONField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4)
    human_feedback = models.CharField(max_length=20, null=True, blank=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    execution_time_ms = models.IntegerField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_telemetry"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["agent_id"]),
            models.Index(fields=["task_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["human_feedback"]),
        ]

    def __str__(self):
        return f"{self.agent_id} - {self.task_type} - {self.created_at}"
