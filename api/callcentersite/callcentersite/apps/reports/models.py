"""Modelos de reportes."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class ReportTemplate(TimeStampedModel):
    """Plantilla de reporte configurable."""

    FORMAT_CHOICES = [
        ("csv", "CSV"),
        ("excel", "Excel"),
        ("pdf", "PDF"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    query_config = models.JSONField(default=dict)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="report_templates")

    class Meta:
        verbose_name = "plantilla de reporte"
        verbose_name_plural = "plantillas de reporte"
        ordering = ("name",)


class GeneratedReport(TimeStampedModel):
    """Reporte generado listo para descarga."""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ]

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="generated_reports")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="generated_reports")
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to="reports/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    parameters = models.JSONField(default=dict)
    file_size = models.BigIntegerField(default=0)
    record_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "reporte generado"
        verbose_name_plural = "reportes generados"
        ordering = ("-generated_at",)
