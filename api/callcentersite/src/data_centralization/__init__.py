"""
Data Centralization Layer - TASK-011

Capa de centralizacion de datos para unified query API.
Integra metrics (MySQL), logs (Cassandra future), y health checks.
"""

default_app_config = 'data_centralization.apps.DataCentralizationConfig'
