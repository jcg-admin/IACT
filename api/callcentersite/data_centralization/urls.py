"""URL configuration for data_centralization app."""

from django.urls import path
from . import views

app_name = 'data_centralization'

urlpatterns = [
    path('query/', views.unified_query, name='unified-query'),
]
