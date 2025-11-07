"""Views para metricas DORA."""

from __future__ import annotations

import json
from datetime import timedelta

from django.db.models import Avg
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import DORAMetric


@require_http_methods(["GET"])
def dora_metrics_summary(request):
    """GET /api/dora/metrics - Summary ultimos 30 dias."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    metrics = DORAMetric.objects.filter(created_at__gte=cutoff)

    # Calcular Lead Time promedio
    deployment_metrics = metrics.filter(phase_name="deployment")
    avg_lead_time = deployment_metrics.aggregate(avg=Avg("duration_seconds"))["avg"] or 0

    # Calcular Deployment Frequency
    deployment_count = deployment_metrics.count()

    # Calcular Change Failure Rate
    testing_metrics = metrics.filter(phase_name="testing")
    failed_tests = testing_metrics.filter(decision="no-go").count()
    total_tests = testing_metrics.count()
    cfr = (failed_tests / total_tests * 100) if total_tests > 0 else 0

    return JsonResponse(
        {
            "period_days": days,
            "metrics": {
                "lead_time_hours": avg_lead_time / 3600,
                "deployment_frequency": deployment_count,
                "change_failure_rate": cfr,
                "mttr_hours": 0,  # TODO: implementar
            },
            "total_cycles": metrics.values("cycle_id").distinct().count(),
        }
    )


@require_http_methods(["POST"])
def dora_metrics_create(request):
    """POST /api/dora/metrics - Crear metrica."""
    data = json.loads(request.body)

    metric = DORAMetric.objects.create(
        cycle_id=data["cycle_id"],
        feature_id=data["feature_id"],
        phase_name=data["phase_name"],
        decision=data["decision"],
        duration_seconds=data["duration_seconds"],
        metadata=data.get("metadata", {}),
    )

    return JsonResponse(
        {
            "id": metric.id,
            "cycle_id": metric.cycle_id,
            "created_at": metric.created_at.isoformat(),
        },
        status=201,
    )
