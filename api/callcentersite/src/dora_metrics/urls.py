"""URLs para dora_metrics."""

from django.urls import path

from . import views

urlpatterns = [
    # API endpoints
    path("metrics/", views.dora_metrics_summary, name="dora-metrics-summary"),
    path("metrics/create/", views.dora_metrics_create, name="dora-metrics-create"),
    path("summary/", views.dora_summary, name="dora-summary"),
    path("export/csv/", views.export_csv, name="dora-export-csv"),
    path("export/excel/", views.export_excel, name="dora-export-excel"),
    path("export/pdf/", views.export_pdf, name="dora-export-pdf"),
    # Dashboard views
    path("dashboard/", views.dora_dashboard, name="dora-dashboard"),
    # Chart data API endpoints
    path("charts/deployment-frequency/", views.deployment_frequency_chart_data, name="deployment-frequency-chart"),
    path("charts/lead-time-trends/", views.lead_time_trends_chart_data, name="lead-time-trends-chart"),
    path("charts/change-failure-rate/", views.change_failure_rate_chart_data, name="change-failure-rate-chart"),
    path("charts/mttr/", views.mttr_chart_data, name="mttr-chart"),
    # AI-accessible Data Catalog (DORA 2025 AI Capability 6)
    path("data-catalog/", views.data_catalog_index, name="data-catalog-index"),
    path("data-catalog/dora-metrics/", views.data_catalog_dora_metrics, name="data-catalog-dora-metrics"),
    path("data-catalog/deployment-cycles/", views.data_catalog_deployment_cycles, name="data-catalog-deployment-cycles"),
    path("data-catalog/aggregated-stats/", views.data_catalog_aggregated_stats, name="data-catalog-aggregated-stats"),
    # Healthy Data Ecosystems (DORA 2025 AI Capability 7)
    path("ecosystem/quality/", views.data_quality_assessment, name="ecosystem-quality"),
    path("ecosystem/governance/", views.data_governance_status, name="ecosystem-governance"),
    path("ecosystem/lineage/", views.data_lineage_map, name="ecosystem-lineage"),
    path("ecosystem/health/", views.ecosystem_health_status, name="ecosystem-health"),
    path("ecosystem/metadata/", views.metadata_registry, name="ecosystem-metadata"),
    # Advanced Analytics
    path("analytics/trends/deployment-frequency/", views.trend_analysis_deployment_frequency, name="analytics-trend-deployment-frequency"),
    path("analytics/trends/lead-time/", views.trend_analysis_lead_time, name="analytics-trend-lead-time"),
    path("analytics/comparative/period-over-period/", views.comparative_period_over_period, name="analytics-comparative-pop"),
    path("analytics/historical/monthly/", views.historical_monthly_report, name="analytics-historical-monthly"),
    path("analytics/anomalies/", views.anomaly_detection, name="analytics-anomalies"),
    path("analytics/forecast/", views.performance_forecast, name="analytics-forecast"),
    # AI Telemetry System (TASK-024)
    path("ai-telemetry/record/", views.ai_telemetry_record, name="ai-telemetry-record"),
    path("ai-telemetry/<int:telemetry_id>/feedback/", views.ai_telemetry_feedback, name="ai-telemetry-feedback"),
    path("ai-telemetry/stats/", views.ai_telemetry_stats, name="ai-telemetry-stats"),
    path("ai-telemetry/agent/<str:agent_id>/", views.ai_telemetry_agent_stats, name="ai-telemetry-agent-stats"),
    path("ai-telemetry/accuracy/", views.ai_telemetry_accuracy, name="ai-telemetry-accuracy"),
    # Predictive Analytics (TASK-033)
    path("predict/deployment-risk/", views.predict_deployment_risk, name="predict-deployment-risk"),
    path("predict/model-stats/", views.predict_model_stats, name="predict-model-stats"),
    path("predict/retrain/", views.predict_retrain_model, name="predict-retrain"),
    path("predict/feature-importance/", views.predict_feature_importance, name="predict-feature-importance"),
    # Auto-remediation (TASK-034)
    path("remediation/problems/", views.remediation_problems, name="remediation-problems"),
    path("remediation/propose-fix/", views.remediation_propose_fix, name="remediation-propose-fix"),
    path("remediation/execute/", views.remediation_execute, name="remediation-execute"),
    path("remediation/rollback/<str:execution_id>/", views.remediation_rollback, name="remediation-rollback"),
]
