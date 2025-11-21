"""
Data Catalog for AI-accessible Internal Data.

Implements DORA 2025 AI Capability 6: AI-accessible Internal Data.

Provides structured access to internal system data for AI agents.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min, Q
from .models import DORAMetric


class DataCatalog:
    """
    Catalog of all internal data sources accessible to AI systems.

    Provides:
    - Schema information
    - Data discovery
    - Query capabilities
    - Metadata about datasets
    """

    @staticmethod
    def get_catalog() -> Dict[str, Any]:
        """
        Get complete data catalog with all available datasets.

        Returns:
            Dict containing catalog metadata and dataset list
        """
        return {
            "catalog_version": "1.0.0",
            "generated_at": timezone.now().isoformat(),
            "total_datasets": 4,
            "datasets": [
                DataCatalog.get_dora_metrics_dataset(),
                DataCatalog.get_deployment_cycles_dataset(),
                DataCatalog.get_performance_metrics_dataset(),
                DataCatalog.get_quality_metrics_dataset(),
            ]
        }

    @staticmethod
    def get_dora_metrics_dataset() -> Dict[str, Any]:
        """Get DORA metrics dataset information."""
        return {
            "dataset_id": "dora_metrics",
            "name": "DORA Metrics",
            "description": "Core DORA performance metrics",
            "type": "time_series",
            "update_frequency": "real_time",
            "schema": {
                "fields": [
                    {
                        "name": "cycle_id",
                        "type": "string",
                        "description": "Unique deployment cycle identifier",
                        "required": True,
                        "example": "cycle-2025-001"
                    },
                    {
                        "name": "feature_id",
                        "type": "string",
                        "description": "Feature identifier",
                        "required": True,
                        "example": "FEAT-123"
                    },
                    {
                        "name": "phase_name",
                        "type": "string",
                        "description": "SDLC phase",
                        "required": True,
                        "enum": ["development", "testing", "deployment", "incident", "recovery"],
                        "example": "deployment"
                    },
                    {
                        "name": "decision",
                        "type": "string",
                        "description": "Phase decision outcome",
                        "required": True,
                        "enum": ["approved", "rejected", "rollback", "resolved"],
                        "example": "approved"
                    },
                    {
                        "name": "duration_seconds",
                        "type": "float",
                        "description": "Phase duration in seconds",
                        "required": True,
                        "min": 0,
                        "max": 86400,
                        "example": 1200.5
                    },
                    {
                        "name": "created_at",
                        "type": "datetime",
                        "description": "Timestamp of metric creation",
                        "required": True,
                        "format": "ISO8601",
                        "example": "2025-11-07T10:30:00Z"
                    }
                ]
            },
            "api_endpoint": "/api/v1/dora/data-catalog/dora-metrics/",
            "query_parameters": [
                {
                    "name": "days",
                    "type": "integer",
                    "description": "Number of days to query",
                    "default": 30,
                    "min": 1,
                    "max": 365
                },
                {
                    "name": "phase_name",
                    "type": "string",
                    "description": "Filter by phase",
                    "optional": True
                },
                {
                    "name": "feature_id",
                    "type": "string",
                    "description": "Filter by feature",
                    "optional": True
                }
            ],
            "example_queries": [
                {
                    "description": "Get last 7 days of deployment metrics",
                    "url": "/api/v1/dora/data-catalog/dora-metrics/?days=7&phase_name=deployment"
                },
                {
                    "description": "Get all metrics for specific feature",
                    "url": "/api/v1/dora/data-catalog/dora-metrics/?feature_id=FEAT-123"
                }
            ]
        }

    @staticmethod
    def get_deployment_cycles_dataset() -> Dict[str, Any]:
        """Get deployment cycles dataset information."""
        return {
            "dataset_id": "deployment_cycles",
            "name": "Deployment Cycles",
            "description": "Complete deployment cycle information",
            "type": "aggregated",
            "update_frequency": "real_time",
            "schema": {
                "fields": [
                    {
                        "name": "cycle_id",
                        "type": "string",
                        "description": "Deployment cycle ID"
                    },
                    {
                        "name": "feature_id",
                        "type": "string",
                        "description": "Associated feature"
                    },
                    {
                        "name": "start_time",
                        "type": "datetime",
                        "description": "Cycle start timestamp"
                    },
                    {
                        "name": "end_time",
                        "type": "datetime",
                        "description": "Cycle end timestamp"
                    },
                    {
                        "name": "total_duration_hours",
                        "type": "float",
                        "description": "Total cycle duration"
                    },
                    {
                        "name": "phases_count",
                        "type": "integer",
                        "description": "Number of phases in cycle"
                    },
                    {
                        "name": "failed",
                        "type": "boolean",
                        "description": "Whether deployment failed"
                    }
                ]
            },
            "api_endpoint": "/api/v1/dora/data-catalog/deployment-cycles/",
            "query_parameters": [
                {
                    "name": "days",
                    "type": "integer",
                    "default": 30
                },
                {
                    "name": "failed_only",
                    "type": "boolean",
                    "description": "Show only failed deployments",
                    "optional": True
                }
            ]
        }

    @staticmethod
    def get_performance_metrics_dataset() -> Dict[str, Any]:
        """Get performance metrics dataset information."""
        return {
            "dataset_id": "performance_metrics",
            "name": "Performance Metrics",
            "description": "System performance and health metrics",
            "type": "time_series",
            "update_frequency": "5_minutes",
            "schema": {
                "fields": [
                    {
                        "name": "metric_name",
                        "type": "string",
                        "description": "Name of performance metric",
                        "enum": [
                            "api_response_time_ms",
                            "database_query_time_ms",
                            "cache_hit_rate",
                            "error_rate",
                            "request_throughput"
                        ]
                    },
                    {
                        "name": "value",
                        "type": "float",
                        "description": "Metric value"
                    },
                    {
                        "name": "timestamp",
                        "type": "datetime",
                        "description": "Measurement timestamp"
                    }
                ]
            },
            "api_endpoint": "/api/v1/dora/data-catalog/performance-metrics/",
            "query_parameters": [
                {
                    "name": "metric_name",
                    "type": "string",
                    "description": "Specific metric to query"
                },
                {
                    "name": "hours",
                    "type": "integer",
                    "default": 24
                }
            ]
        }

    @staticmethod
    def get_quality_metrics_dataset() -> Dict[str, Any]:
        """Get data quality metrics dataset information."""
        return {
            "dataset_id": "quality_metrics",
            "name": "Data Quality Metrics",
            "description": "Data quality scores and validations",
            "type": "aggregated",
            "update_frequency": "daily",
            "schema": {
                "fields": [
                    {
                        "name": "dataset_name",
                        "type": "string",
                        "description": "Name of validated dataset"
                    },
                    {
                        "name": "quality_score",
                        "type": "float",
                        "description": "Overall quality score 0-100",
                        "min": 0,
                        "max": 100
                    },
                    {
                        "name": "null_rate",
                        "type": "float",
                        "description": "Percentage of null values"
                    },
                    {
                        "name": "anomaly_rate",
                        "type": "float",
                        "description": "Percentage of anomalies detected"
                    },
                    {
                        "name": "schema_violations",
                        "type": "integer",
                        "description": "Number of schema violations"
                    },
                    {
                        "name": "checked_at",
                        "type": "datetime",
                        "description": "Quality check timestamp"
                    }
                ]
            },
            "api_endpoint": "/api/v1/dora/data-catalog/quality-metrics/",
            "query_parameters": [
                {
                    "name": "dataset_name",
                    "type": "string",
                    "optional": True
                }
            ]
        }


class DataQueryEngine:
    """
    Query engine for AI-accessible data.

    Provides structured querying capabilities optimized for AI agents.
    """

    @staticmethod
    def query_dora_metrics(
        days: int = 30,
        phase_name: Optional[str] = None,
        feature_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query DORA metrics with filters.

        Args:
            days: Number of days to query
            phase_name: Optional filter by phase
            feature_id: Optional filter by feature

        Returns:
            Dict with metrics data and metadata
        """
        start_date = timezone.now() - timedelta(days=days)

        # Build query
        query = Q(created_at__gte=start_date)
        if phase_name:
            query &= Q(phase_name=phase_name)
        if feature_id:
            query &= Q(feature_id=feature_id)

        metrics = DORAMetric.objects.filter(query).order_by('-created_at')

        # Serialize data
        data = list(metrics.values(
            'cycle_id',
            'feature_id',
            'phase_name',
            'decision',
            'duration_seconds',
            'created_at'
        ))

        # Convert datetimes to ISO format for JSON
        for item in data:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].isoformat()

        return {
            "query": {
                "days": days,
                "phase_name": phase_name,
                "feature_id": feature_id,
                "executed_at": timezone.now().isoformat()
            },
            "metadata": {
                "total_records": len(data),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": timezone.now().isoformat()
                }
            },
            "data": data
        }

    @staticmethod
    def query_deployment_cycles(
        days: int = 30,
        failed_only: bool = False
    ) -> Dict[str, Any]:
        """
        Query deployment cycles.

        Args:
            days: Number of days to query
            failed_only: Only return failed deployments

        Returns:
            Dict with deployment cycle data
        """
        start_date = timezone.now() - timedelta(days=days)

        # Get all deployment metrics
        deployments = DORAMetric.objects.filter(
            phase_name='deployment',
            created_at__gte=start_date
        )

        # Group by cycle_id
        cycles = {}
        for metric in deployments:
            cycle_id = metric.cycle_id

            if cycle_id not in cycles:
                # Get all phases for this cycle
                cycle_metrics = DORAMetric.objects.filter(cycle_id=cycle_id)

                # Check if deployment failed
                has_incident = cycle_metrics.filter(phase_name='incident').exists()
                has_rollback = cycle_metrics.filter(decision='rollback').exists()
                failed = has_incident or has_rollback

                if failed_only and not failed:
                    continue

                # Calculate total duration
                first_metric = cycle_metrics.order_by('created_at').first()
                last_metric = cycle_metrics.order_by('-created_at').first()

                if first_metric and last_metric:
                    duration = (last_metric.created_at - first_metric.created_at).total_seconds() / 3600
                else:
                    duration = 0

                cycles[cycle_id] = {
                    "cycle_id": cycle_id,
                    "feature_id": metric.feature_id,
                    "start_time": first_metric.created_at.isoformat() if first_metric else None,
                    "end_time": last_metric.created_at.isoformat() if last_metric else None,
                    "total_duration_hours": round(duration, 2),
                    "phases_count": cycle_metrics.count(),
                    "failed": failed
                }

        return {
            "query": {
                "days": days,
                "failed_only": failed_only,
                "executed_at": timezone.now().isoformat()
            },
            "metadata": {
                "total_cycles": len(cycles),
                "failed_cycles": sum(1 for c in cycles.values() if c['failed'])
            },
            "data": list(cycles.values())
        }

    @staticmethod
    def get_aggregated_stats(days: int = 30) -> Dict[str, Any]:
        """
        Get aggregated statistics for AI analysis.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with aggregated statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        metrics = DORAMetric.objects.filter(created_at__gte=start_date)

        # Calculate statistics
        stats = {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": timezone.now().isoformat()
            },
            "total_metrics": metrics.count(),
            "by_phase": {},
            "by_decision": {},
            "duration_stats": {},
            "deployment_frequency": 0,
            "change_failure_rate": 0.0,
            "lead_time_hours": 0.0,
            "mttr_hours": 0.0
        }

        # Count by phase
        for phase in ['development', 'testing', 'deployment', 'incident', 'recovery']:
            count = metrics.filter(phase_name=phase).count()
            stats["by_phase"][phase] = count

        # Count by decision
        for decision in ['approved', 'rejected', 'rollback', 'resolved']:
            count = metrics.filter(decision=decision).count()
            stats["by_decision"][decision] = count

        # Duration statistics
        duration_stats = metrics.aggregate(
            avg_duration=Avg('duration_seconds'),
            min_duration=Min('duration_seconds'),
            max_duration=Max('duration_seconds')
        )

        stats["duration_stats"] = {
            "avg_seconds": round(duration_stats['avg_duration'] or 0, 2),
            "min_seconds": duration_stats['min_duration'] or 0,
            "max_seconds": duration_stats['max_duration'] or 0,
            "avg_hours": round((duration_stats['avg_duration'] or 0) / 3600, 2)
        }

        # DORA metrics
        deployments = metrics.filter(phase_name='deployment')
        stats["deployment_frequency"] = deployments.count()

        # Change failure rate
        total_deployments = deployments.count()
        failed_deployments = metrics.filter(
            Q(phase_name='incident') | Q(decision='rollback')
        ).values('cycle_id').distinct().count()

        if total_deployments > 0:
            stats["change_failure_rate"] = round(
                (failed_deployments / total_deployments) * 100, 2
            )

        # Lead time
        if deployments.exists():
            avg_lead_time = deployments.aggregate(Avg('duration_seconds'))['duration_seconds__avg']
            stats["lead_time_hours"] = round((avg_lead_time or 0) / 3600, 2)

        # MTTR
        recovery_phases = metrics.filter(phase_name='recovery')
        if recovery_phases.exists():
            avg_mttr = recovery_phases.aggregate(Avg('duration_seconds'))['duration_seconds__avg']
            stats["mttr_hours"] = round((avg_mttr or 0) / 3600, 2)

        return stats
