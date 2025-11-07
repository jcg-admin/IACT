"""Django app configuration for data_centralization."""

from django.apps import AppConfig


class DataCentralizationConfig(AppConfig):
    """Configuration for data_centralization app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_centralization'
    verbose_name = 'Data Centralization'
