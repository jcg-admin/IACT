"""URLs para dora_metrics."""

from django.urls import path

from . import views

urlpatterns = [
    # API endpoints
    path("metrics/", views.dora_metrics_summary, name="dora-metrics-summary"),
    path("metrics/create/", views.dora_metrics_create, name="dora-metrics-create"),
    # Dashboard views
    path("dashboard/", views.dora_dashboard, name="dora-dashboard"),
    # Chart data API endpoints
    path("charts/deployment-frequency/", views.deployment_frequency_chart_data, name="deployment-frequency-chart"),
    path("charts/lead-time-trends/", views.lead_time_trends_chart_data, name="lead-time-trends-chart"),
    path("charts/change-failure-rate/", views.change_failure_rate_chart_data, name="change-failure-rate-chart"),
    path("charts/mttr/", views.mttr_chart_data, name="mttr-chart"),
]
