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
