"""URL configuration for data_centralization app."""

from django.urls import path

from .views import DataQueryView

app_name = "data_centralization"

urlpatterns = [
    path("query/", DataQueryView.as_view(), name="data-query"),
]
