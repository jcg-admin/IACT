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
from .data_ecosystem import (
    DataQualityMonitor,
    DataGovernance,
    DataLineage,
    EcosystemHealth,
    MetadataManagement
)
from .advanced_analytics import (
    TrendAnalyzer,
    ComparativeAnalytics,
    HistoricalReporting,
    AnomalyTrendDetector,
    PerformanceForecasting
)


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


# ============================================================================
# HEALTHY DATA ECOSYSTEMS (DORA 2025 AI Capability 7)
# ============================================================================


@require_http_methods(["GET"])
def data_quality_assessment(request):
    """
    GET /api/dora/ecosystem/quality/ - Data quality assessment.

    Query parameters:
        - days: Number of days to assess (default: 30)

    Implements DORA 2025 AI Capability 7: Healthy Data Ecosystems.
    Returns comprehensive data quality metrics.
    """
    days = int(request.GET.get('days', 30))

    assessment = DataQualityMonitor.assess_data_quality(days=days)

    return JsonResponse(assessment)


@require_http_methods(["GET"])
def data_governance_status(request):
    """
    GET /api/dora/ecosystem/governance/ - Data governance status.

    Returns current data governance policies and compliance status.
    """
    governance = DataGovernance.get_governance_status()

    return JsonResponse(governance)


@require_http_methods(["GET"])
def data_lineage_map(request):
    """
    GET /api/dora/ecosystem/lineage/ - Data lineage map.

    Returns complete data lineage and flow information.
    """
    lineage = DataLineage.get_lineage_map()

    return JsonResponse(lineage)


@require_http_methods(["GET"])
def ecosystem_health_status(request):
    """
    GET /api/dora/ecosystem/health/ - Overall ecosystem health.

    Returns comprehensive ecosystem health status including:
    - Overall health score
    - Component health scores
    - Data pipeline status
    - Recommendations
    """
    health = EcosystemHealth.get_health_status()

    return JsonResponse(health)


@require_http_methods(["GET"])
def metadata_registry(request):
    """
    GET /api/dora/ecosystem/metadata/ - Metadata registry.

    Returns complete metadata registry for all datasets.
    """
    metadata = MetadataManagement.get_metadata_registry()

    return JsonResponse(metadata)


# ============================================================================
# ADVANCED ANALYTICS
# ============================================================================


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def trend_analysis_deployment_frequency(request):
    """
    GET /api/dora/analytics/trends/deployment-frequency/ - Deployment frequency trend.

    Query parameters:
        - days: Number of days to analyze (default: 90)

    Returns trend analysis for deployment frequency.
    """
    days = int(request.GET.get('days', 90))

    trend = TrendAnalyzer.analyze_deployment_frequency_trend(days=days)

    return JsonResponse(trend)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def trend_analysis_lead_time(request):
    """
    GET /api/dora/analytics/trends/lead-time/ - Lead time trend analysis.

    Query parameters:
        - days: Number of days to analyze (default: 90)

    Returns trend analysis for lead time.
    """
    days = int(request.GET.get('days', 90))

    trend = TrendAnalyzer.analyze_lead_time_trend(days=days)

    return JsonResponse(trend)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def comparative_period_over_period(request):
    """
    GET /api/dora/analytics/comparative/period-over-period/ - Period comparison.

    Query parameters:
        - current_days: Current period days (default: 30)
        - previous_days: Previous period days (default: 30)

    Returns comparative analysis between two periods.
    """
    current_days = int(request.GET.get('current_days', 30))
    previous_days = int(request.GET.get('previous_days', 30))

    comparison = ComparativeAnalytics.period_over_period_comparison(
        current_days=current_days,
        previous_days=previous_days
    )

    return JsonResponse(comparison)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def historical_monthly_report(request):
    """
    GET /api/dora/analytics/historical/monthly/ - Monthly historical report.

    Query parameters:
        - months: Number of months to include (default: 6)

    Returns monthly aggregated historical report.
    """
    months = int(request.GET.get('months', 6))

    report = HistoricalReporting.generate_monthly_report(months=months)

    return JsonResponse(report)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def anomaly_detection(request):
    """
    GET /api/dora/analytics/anomalies/ - Detect anomalies.

    Query parameters:
        - days: Number of days to analyze (default: 30)

    Returns detected anomalies in deployment durations.
    """
    days = int(request.GET.get('days', 30))

    anomalies = AnomalyTrendDetector.detect_duration_anomalies(days=days)

    return JsonResponse(anomalies)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def performance_forecast(request):
    """
    GET /api/dora/analytics/forecast/ - Performance forecast.

    Query parameters:
        - historical_months: Months of historical data to use (default: 6)

    Returns forecasted metrics for next period.
    """
    historical_months = int(request.GET.get('historical_months', 6))

    forecast = PerformanceForecasting.forecast_next_month(historical_months=historical_months)

    return JsonResponse(forecast)


# ============================================================================
# AI TELEMETRY SYSTEM (TASK-024)
# ============================================================================

from .ai_telemetry import AITelemetryCollector


@require_http_methods(["POST"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def ai_telemetry_record(request):
    """
    POST /api/dora/ai-telemetry/record/ - Registrar decision IA.

    Body:
        {
            "agent_id": "deployment-risk-predictor",
            "task_type": "deployment_risk",
            "decision": {"action": "approve", "risk_score": 0.15},
            "confidence": 0.92,
            "execution_time_ms": 150,
            "metadata": {}
        }
    """
    data = json.loads(request.body)

    telemetry = AITelemetryCollector.record_decision(
        agent_id=data["agent_id"],
        task_type=data["task_type"],
        decision=data["decision"],
        confidence=data["confidence"],
        execution_time_ms=data["execution_time_ms"],
        metadata=data.get("metadata", {}),
    )

    return JsonResponse(
        {
            "id": telemetry.id,
            "agent_id": telemetry.agent_id,
            "task_type": telemetry.task_type,
            "confidence_score": float(telemetry.confidence_score),
            "created_at": telemetry.created_at.isoformat(),
        },
        status=201,
    )


@require_http_methods(["POST"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def ai_telemetry_feedback(request, telemetry_id):
    """
    POST /api/dora/ai-telemetry/<id>/feedback/ - Registrar feedback humano.

    Body:
        {
            "feedback": "correct"  # correct, incorrect, partially_correct
        }
    """
    data = json.loads(request.body)

    telemetry = AITelemetryCollector.record_feedback(
        telemetry_id=telemetry_id,
        feedback=data["feedback"],
    )

    return JsonResponse(
        {
            "id": telemetry.id,
            "human_feedback": telemetry.human_feedback,
            "accuracy": float(telemetry.accuracy) if telemetry.accuracy else None,
        }
    )


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def ai_telemetry_stats(request):
    """
    GET /api/dora/ai-telemetry/stats/ - Estadisticas generales.

    Query parameters:
        - days: Number of days to analyze (default: 30)
    """
    days = int(request.GET.get("days", 30))

    accuracy_stats = AITelemetryCollector.calculate_accuracy(days=days)
    confidence_dist = AITelemetryCollector.get_confidence_distribution(days=days)
    execution_trends = AITelemetryCollector.get_execution_time_trends(days=days)

    return JsonResponse(
        {
            "period_days": days,
            "accuracy": accuracy_stats,
            "confidence_distribution": confidence_dist,
            "execution_time": execution_trends,
        }
    )


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def ai_telemetry_agent_stats(request, agent_id):
    """
    GET /api/dora/ai-telemetry/agent/<agent_id>/ - Stats por agente.

    Query parameters:
        - days: Number of days to analyze (default: 30)
    """
    days = int(request.GET.get("days", 30))

    stats = AITelemetryCollector.get_agent_stats(agent_id=agent_id, days=days)

    return JsonResponse(stats)


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def ai_telemetry_accuracy(request):
    """
    GET /api/dora/ai-telemetry/accuracy/ - Metricas accuracy.

    Query parameters:
        - agent_id: Filter by agent (optional)
        - task_type: Filter by task type (optional)
        - days: Number of days to analyze (default: 30)
    """
    agent_id = request.GET.get("agent_id")
    task_type = request.GET.get("task_type")
    days = int(request.GET.get("days", 30))

    accuracy_stats = AITelemetryCollector.calculate_accuracy(
        agent_id=agent_id,
        task_type=task_type,
        days=days,
    )

    confidence_dist = AITelemetryCollector.get_confidence_distribution(
        agent_id=agent_id,
        task_type=task_type,
        days=days,
    )

    return JsonResponse(
        {
            "period_days": days,
            "filters": {
                "agent_id": agent_id,
                "task_type": task_type,
            },
            "accuracy": accuracy_stats,
            "confidence_distribution": confidence_dist,
        }
    )


# ============================================================================
# PREDICTIVE ANALYTICS (TASK-033)
# ============================================================================

from .ml_features import FeatureExtractor
from .ml_models import DeploymentRiskPredictor


@require_http_methods(["POST"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def predict_deployment_risk(request):
    """
    POST /api/dora/predict/deployment-risk/ - Predecir riesgo de deployment.

    Body:
        {
            "cycle_id": "cycle-123" (opcional, extraer features automaticamente)
            O
            "features": {...} (proveer features manualmente)
        }
    """
    data = json.loads(request.body)

    # Cargar modelo
    predictor = DeploymentRiskPredictor()

    try:
        # Opcion 1: Usar cycle_id para extraer features
        if "cycle_id" in data:
            features = FeatureExtractor.extract_deployment_features(data["cycle_id"])
            if not features:
                return JsonResponse(
                    {"error": f"Cycle {data['cycle_id']} not found"},
                    status=404,
                )
        # Opcion 2: Proveer features manualmente
        elif "features" in data:
            features = data["features"]
        else:
            return JsonResponse(
                {"error": "Must provide either cycle_id or features"},
                status=400,
            )

        # Obtener prediccion con explicacion
        explanation = predictor.explain_prediction(features)

        return JsonResponse(
            {
                "cycle_id": data.get("cycle_id"),
                "prediction": explanation,
                "model_version": predictor.get_model_version(),
            }
        )

    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def predict_model_stats(request):
    """
    GET /api/dora/predict/model-stats/ - Estadisticas del modelo ML.
    """
    predictor = DeploymentRiskPredictor()

    try:
        stats = predictor.evaluate_model()

        return JsonResponse(
            {
                "model_version": predictor.get_model_version(),
                "statistics": stats,
            }
        )

    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )


@require_http_methods(["POST"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def predict_retrain_model(request):
    """
    POST /api/dora/predict/retrain/ - Re-entrenar modelo ML.

    Body:
        {
            "days": 90 (opcional, default 90)
        }
    """
    data = json.loads(request.body)
    days = data.get("days", 90)

    # Crear training dataset
    training_data = FeatureExtractor.create_training_dataset(days=days)

    if len(training_data) < 10:
        return JsonResponse(
            {"error": f"Insufficient data for training (found {len(training_data)}, need >= 10)"},
            status=400,
        )

    # Entrenar modelo
    predictor = DeploymentRiskPredictor()

    try:
        metrics = predictor.train_model(training_data)

        return JsonResponse(
            {
                "success": True,
                "model_version": predictor.get_model_version(),
                "training_metrics": metrics,
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


@require_http_methods(["GET"])
@throttle_classes([BurstRateThrottle, SustainedRateThrottle])
def predict_feature_importance(request):
    """
    GET /api/dora/predict/feature-importance/ - Feature importance del modelo.
    """
    predictor = DeploymentRiskPredictor()

    try:
        importance = predictor._get_feature_importance()

        # Ordenar por importance
        sorted_importance = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return JsonResponse(
            {
                "model_version": predictor.get_model_version(),
                "feature_importance": dict(sorted_importance),
                "top_features": [
                    {"feature": feature, "importance": float(imp)}
                    for feature, imp in sorted_importance[:5]
                ],
            }
        )

    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )
