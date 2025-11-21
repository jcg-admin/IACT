"""Configuracion de app dora_metrics."""

from django.apps import AppConfig


class DoraMetricsConfig(AppConfig):
    """Configuracion para app de metricas DORA."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dora_metrics"
    verbose_name = "DORA Metrics"
