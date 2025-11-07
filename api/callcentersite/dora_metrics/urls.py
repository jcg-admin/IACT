from django.urls import path
from . import views

urlpatterns = [
    path('metrics/', views.dora_metrics_summary, name='dora-metrics-summary'),
    path('metrics/create/', views.dora_metrics_create, name='dora-metrics-create'),
]
