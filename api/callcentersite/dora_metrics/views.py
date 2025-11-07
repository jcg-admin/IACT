"""Views para metricas DORA."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import throttle_classes
from .throttling import BurstRateThrottle, SustainedRateThrottle

from .models import DORAMetric
from .data_catalog import DataCatalog, DataQueryEngine


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
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


# ============================================================================
# DJANGO ADMIN DASHBOARDS
# ============================================================================


@staff_member_required
def dora_dashboard(request):
    """Dashboard principal de metricas DORA para Django Admin."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    metrics = DORAMetric.objects.filter(created_at__gte=cutoff)

    # Calcular metricas principales
    deployment_metrics = metrics.filter(phase_name="deployment")
    avg_lead_time = deployment_metrics.aggregate(avg=Avg("duration_seconds"))["avg"] or 0
    deployment_count = deployment_metrics.count()

    testing_metrics = metrics.filter(phase_name="testing")
    failed_tests = testing_metrics.filter(decision="no-go").count()
    total_tests = testing_metrics.count()
    cfr = (failed_tests / total_tests * 100) if total_tests > 0 else 0

    # Calcular MTTR (Mean Time To Recovery)
    # Usar metricas de maintenance con decision='fixed'
    maintenance_metrics = metrics.filter(phase_name="maintenance", decision="fixed")
    avg_mttr = maintenance_metrics.aggregate(avg=Avg("duration_seconds"))["avg"] or 0

    # Calcular clasificacion DORA
    dora_classification = calculate_dora_classification(
        deployment_count, days, avg_lead_time / 3600, cfr, avg_mttr / 3600
    )

    context = {
        "days": days,
        "lead_time_hours": round(avg_lead_time / 3600, 2),
        "deployment_frequency": deployment_count,
        "deployment_frequency_per_week": round(deployment_count / (days / 7), 2),
        "change_failure_rate": round(cfr, 2),
        "mttr_hours": round(avg_mttr / 3600, 2),
        "total_cycles": metrics.values("cycle_id").distinct().count(),
        "dora_classification": dora_classification,
        "period_start": cutoff.strftime("%Y-%m-%d"),
        "period_end": timezone.now().strftime("%Y-%m-%d"),
    }

    return render(request, "dora_metrics/dashboard.html", context)


@staff_member_required
def deployment_frequency_chart_data(request):
    """API endpoint para datos de grafico de deployment frequency."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    # Agrupar deployments por dia
    deployments_by_day = (
        DORAMetric.objects.filter(
            created_at__gte=cutoff, phase_name="deployment"
        )
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    labels = []
    data = []
    for item in deployments_by_day:
        labels.append(item["date"].strftime("%Y-%m-%d"))
        data.append(item["count"])

    return JsonResponse({"labels": labels, "data": data})


@staff_member_required
def lead_time_trends_chart_data(request):
    """API endpoint para datos de grafico de lead time trends."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    # Agrupar lead time por semana
    deployments = (
        DORAMetric.objects.filter(
            created_at__gte=cutoff, phase_name="deployment"
        )
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(avg_duration=Avg("duration_seconds"))
        .order_by("date")
    )

    labels = []
    data = []
    for item in deployments:
        labels.append(item["date"].strftime("%Y-%m-%d"))
        # Convertir a horas
        data.append(round(item["avg_duration"] / 3600, 2))

    return JsonResponse({"labels": labels, "data": data})


@staff_member_required
def change_failure_rate_chart_data(request):
    """API endpoint para datos de grafico de change failure rate."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    # Agrupar tests por semana
    tests_by_week = (
        DORAMetric.objects.filter(
            created_at__gte=cutoff, phase_name="testing"
        )
        .annotate(date=TruncDate("created_at"))
        .values("date", "decision")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # Procesar datos para calcular CFR por dia
    data_dict = {}
    for item in tests_by_week:
        date = item["date"].strftime("%Y-%m-%d")
        if date not in data_dict:
            data_dict[date] = {"total": 0, "failed": 0}

        data_dict[date]["total"] += item["count"]
        if item["decision"] == "no-go":
            data_dict[date]["failed"] += item["count"]

    labels = []
    data = []
    for date in sorted(data_dict.keys()):
        labels.append(date)
        total = data_dict[date]["total"]
        failed = data_dict[date]["failed"]
        cfr = (failed / total * 100) if total > 0 else 0
        data.append(round(cfr, 2))

    return JsonResponse({"labels": labels, "data": data})


@staff_member_required
def mttr_chart_data(request):
    """API endpoint para datos de grafico de MTTR."""
    days = int(request.GET.get("days", 30))
    cutoff = timezone.now() - timedelta(days=days)

    # Agrupar MTTR por semana
    maintenance_by_week = (
        DORAMetric.objects.filter(
            created_at__gte=cutoff,
            phase_name="maintenance",
            decision="fixed"
        )
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(avg_duration=Avg("duration_seconds"))
        .order_by("date")
    )

    labels = []
    data = []
    for item in maintenance_by_week:
        labels.append(item["date"].strftime("%Y-%m-%d"))
        # Convertir a horas
        data.append(round(item["avg_duration"] / 3600, 2))

    return JsonResponse({"labels": labels, "data": data})


def calculate_dora_classification(deployment_count, days, lead_time_hours, cfr, mttr_hours):
    """Calcular clasificacion DORA (Elite, High, Medium, Low)."""
    # Normalizar a valores por semana/mes
    deployments_per_week = deployment_count / (days / 7)

    # Criterios DORA 2024
    # Elite: >1/dia, <1h lead time, <5% CFR, <1h MTTR
    # High: 1/sem-1/mes, 1dia-1sem lead time, 5-10% CFR, <1dia MTTR
    # Medium: 1/mes-1/6meses, 1sem-1mes lead time, 10-15% CFR, <1sem MTTR
    # Low: <1/6meses, >1mes lead time, >15% CFR, >1sem MTTR

    elite_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    # Deployment Frequency
    if deployments_per_week > 7:  # >1/dia
        elite_count += 1
    elif deployments_per_week >= 1:  # 1/sem-1/dia
        high_count += 1
    elif deployments_per_week >= 0.25:  # 1/mes-1/sem
        medium_count += 1
    else:
        low_count += 1

    # Lead Time
    if lead_time_hours < 1:
        elite_count += 1
    elif lead_time_hours < 24:  # <1 dia
        high_count += 1
    elif lead_time_hours < 168:  # <1 semana
        medium_count += 1
    else:
        low_count += 1

    # Change Failure Rate
    if cfr < 5:
        elite_count += 1
    elif cfr < 10:
        high_count += 1
    elif cfr < 15:
        medium_count += 1
    else:
        low_count += 1

    # MTTR
    if mttr_hours < 1:
        elite_count += 1
    elif mttr_hours < 24:  # <1 dia
        high_count += 1
    elif mttr_hours < 168:  # <1 semana
        medium_count += 1
    else:
        low_count += 1

    # Determinar clasificacion general
    if elite_count >= 3:
        return "Elite"
    elif high_count >= 2:
        return "High"
    elif medium_count >= 2:
        return "Medium"
    else:
        return "Low"


# ============================================================================
# AI-ACCESSIBLE DATA CATALOG (DORA 2025 AI Capability 6)
# ============================================================================


@require_http_methods(["GET"])
def data_catalog_index(request):
    """
    GET /api/dora/data-catalog/ - Complete data catalog.

    Returns structured metadata about all available datasets for AI access.
    Implements DORA 2025 AI Capability 6: AI-accessible Internal Data.
    """
    catalog = DataCatalog.get_catalog()
    return JsonResponse(catalog)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def data_catalog_dora_metrics(request):
    """
    GET /api/dora/data-catalog/dora-metrics/ - Query DORA metrics data.

    Query parameters:
        - days: Number of days to query (default: 30)
        - phase_name: Filter by phase (optional)
        - feature_id: Filter by feature (optional)

    Returns structured DORA metrics data for AI analysis.
    """
    days = int(request.GET.get('days', 30))
    phase_name = request.GET.get('phase_name')
    feature_id = request.GET.get('feature_id')

    result = DataQueryEngine.query_dora_metrics(
        days=days,
        phase_name=phase_name,
        feature_id=feature_id
    )

    return JsonResponse(result)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def data_catalog_deployment_cycles(request):
    """
    GET /api/dora/data-catalog/deployment-cycles/ - Query deployment cycles.

    Query parameters:
        - days: Number of days to query (default: 30)
        - failed_only: Show only failed deployments (default: false)

    Returns deployment cycle data for AI analysis.
    """
    days = int(request.GET.get('days', 30))
    failed_only = request.GET.get('failed_only', 'false').lower() == 'true'

    result = DataQueryEngine.query_deployment_cycles(
        days=days,
        failed_only=failed_only
    )

    return JsonResponse(result)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def data_catalog_aggregated_stats(request):
    """
    GET /api/dora/data-catalog/aggregated-stats/ - Get aggregated statistics.

    Query parameters:
        - days: Number of days to analyze (default: 30)

    Returns comprehensive aggregated statistics for AI analysis.
    """
    days = int(request.GET.get('days', 30))

    result = DataQueryEngine.get_aggregated_stats(days=days)

    return JsonResponse(result)
