"""Modelos analíticos."""

from __future__ import annotations

from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class CallAnalytics(TimeStampedModel):
    """Registro de llamada procesado por ETL."""

    call_id = models.CharField(max_length=100, unique=True)
    client_id = models.CharField(max_length=100)
    call_date = models.DateTimeField()
    duration_seconds = models.IntegerField()
    call_type = models.CharField(max_length=50)
    result = models.CharField(max_length=50)
    center_id = models.IntegerField()
    service_id = models.IntegerField()
    agent_id = models.CharField(max_length=100, null=True, blank=True)
    queue_time_seconds = models.IntegerField(default=0)
    talk_time_seconds = models.IntegerField(default=0)
    hold_time_seconds = models.IntegerField(default=0)
    transfer_count = models.IntegerField(default=0)
    satisfaction_score = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "analítica de llamada"
        verbose_name_plural = "analíticas de llamadas"
        ordering = ("-call_date",)


class DailyMetrics(TimeStampedModel):
    """Métricas agregadas por día."""

    date = models.DateField()
    center_id = models.IntegerField()
    total_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    failed_calls = models.IntegerField(default=0)
    avg_duration = models.FloatField(default=0.0)
    avg_queue_time = models.FloatField(default=0.0)
    avg_talk_time = models.FloatField(default=0.0)
    max_queue_time = models.IntegerField(default=0)
    total_talk_time = models.IntegerField(default=0)

    class Meta:
        verbose_name = "métrica diaria"
        verbose_name_plural = "métricas diarias"
        unique_together = ("date", "center_id")
        ordering = ("-date",)
