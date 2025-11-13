"""
Data Ecosystem Health Management.

Implements DORA 2025 AI Capability 7: Healthy Data Ecosystems.

Provides:
- Data quality monitoring
- Data governance
- Data lineage tracking
- Metadata management
- Ecosystem health metrics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min, Q
from .models import DORAMetric


class DataQualityMonitor:
    """
    Monitor and assess data quality across the ecosystem.

    Tracks:
    - Completeness
    - Accuracy
    - Consistency
    - Timeliness
    - Validity
    """

    @staticmethod
    def assess_data_quality(days: int = 30) -> Dict[str, Any]:
        """
        Comprehensive data quality assessment.

        Args:
            days: Number of days to assess

        Returns:
            Dict with quality metrics and scores
        """
        start_date = timezone.now() - timedelta(days=days)
        metrics = DORAMetric.objects.filter(created_at__gte=start_date)
        total_count = metrics.count()

        if total_count == 0:
            return {
                "overall_score": 0,
                "assessment_date": timezone.now().isoformat(),
                "period_days": days,
                "total_records": 0,
                "quality_dimensions": {},
                "issues": ["No data available for assessment"]
            }

        # 1. Completeness Score (0-100)
        required_fields = ['cycle_id', 'feature_id', 'phase_name', 'decision']
        null_counts = {}
        for field in required_fields:
            null_count = metrics.filter(**{f'{field}__isnull': True}).count()
            null_counts[field] = null_count

        total_nulls = sum(null_counts.values())
        max_nulls = len(required_fields) * total_count
        completeness_score = ((max_nulls - total_nulls) / max_nulls * 100) if max_nulls > 0 else 100

        # 2. Validity Score (0-100)
        # Check for invalid duration values
        invalid_duration = metrics.filter(
            Q(duration_seconds__lt=0) | Q(duration_seconds__gt=86400)
        ).count()
        validity_score = ((total_count - invalid_duration) / total_count * 100) if total_count > 0 else 100

        # 3. Consistency Score (0-100)
        # Check for inconsistent cycle data
        inconsistencies = 0
        cycle_ids = metrics.values_list('cycle_id', flat=True).distinct()

        for cycle_id in cycle_ids:
            cycle_metrics = metrics.filter(cycle_id=cycle_id)
            feature_ids = cycle_metrics.values_list('feature_id', flat=True).distinct()

            # Each cycle should have consistent feature_id
            if len(feature_ids) > 1:
                inconsistencies += 1

        consistency_score = ((len(cycle_ids) - inconsistencies) / len(cycle_ids) * 100) if len(cycle_ids) > 0 else 100

        # 4. Timeliness Score (0-100)
        # Check data freshness (data should be recent)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_count = metrics.filter(created_at__gte=recent_cutoff).count()
        timeliness_score = (recent_count / total_count * 100) if total_count > 0 else 0

        # 5. Accuracy Score (0-100)
        # Check for reasonable duration values (heuristic)
        reasonable_duration = metrics.filter(
            duration_seconds__gte=60,  # At least 1 minute
            duration_seconds__lte=7200  # At most 2 hours
        ).count()
        accuracy_score = (reasonable_duration / total_count * 100) if total_count > 0 else 100

        # Overall Score (weighted average)
        overall_score = (
            completeness_score * 0.25 +
            validity_score * 0.25 +
            consistency_score * 0.20 +
            timeliness_score * 0.15 +
            accuracy_score * 0.15
        )

        # Identify issues
        issues = []
        if completeness_score < 95:
            issues.append(f"Completeness below threshold: {completeness_score:.1f}% (target: 95%)")
        if validity_score < 95:
            issues.append(f"Validity issues detected: {invalid_duration} invalid records")
        if consistency_score < 90:
            issues.append(f"Consistency issues: {inconsistencies} inconsistent cycles")
        if timeliness_score < 50:
            issues.append("Data not fresh: Less than 50% records in last 24 hours")

        return {
            "overall_score": round(overall_score, 2),
            "assessment_date": timezone.now().isoformat(),
            "period_days": days,
            "total_records": total_count,
            "quality_dimensions": {
                "completeness": {
                    "score": round(completeness_score, 2),
                    "null_counts": null_counts,
                    "status": "healthy" if completeness_score >= 95 else "attention_needed"
                },
                "validity": {
                    "score": round(validity_score, 2),
                    "invalid_records": invalid_duration,
                    "status": "healthy" if validity_score >= 95 else "attention_needed"
                },
                "consistency": {
                    "score": round(consistency_score, 2),
                    "inconsistent_cycles": inconsistencies,
                    "status": "healthy" if consistency_score >= 90 else "attention_needed"
                },
                "timeliness": {
                    "score": round(timeliness_score, 2),
                    "recent_records": recent_count,
                    "status": "healthy" if timeliness_score >= 50 else "attention_needed"
                },
                "accuracy": {
                    "score": round(accuracy_score, 2),
                    "reasonable_durations": reasonable_duration,
                    "status": "healthy" if accuracy_score >= 90 else "attention_needed"
                }
            },
            "issues": issues if issues else ["No issues detected"],
            "recommendation": DataQualityMonitor._get_recommendation(overall_score)
        }

    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Get recommendation based on overall score."""
        if score >= 95:
            return "Excellent data quality. Maintain current practices."
        elif score >= 85:
            return "Good data quality. Monitor trends and address minor issues."
        elif score >= 70:
            return "Fair data quality. Review data collection processes and implement improvements."
        else:
            return "Poor data quality. Immediate action required. Review data pipeline and validation rules."


class DataGovernance:
    """
    Data governance policies and compliance tracking.

    Manages:
    - Data retention policies
    - Access controls
    - Compliance rules
    - Data ownership
    """

    @staticmethod
    def get_governance_status() -> Dict[str, Any]:
        """Get current governance status and compliance."""
        return {
            "governance_framework": {
                "version": "1.0.0",
                "last_updated": "2025-11-07",
                "owner": "data-governance-team"
            },
            "data_retention": {
                "dora_metrics_mysql": {
                    "policy": "permanent",
                    "reasoning": "Historical analysis and trending",
                    "compliance": "compliant"
                },
                "application_logs_json": {
                    "policy": "90_days",
                    "rotation": "100MB",
                    "compliance": "compliant"
                },
                "infrastructure_logs_cassandra": {
                    "policy": "90_days_ttl",
                    "auto_expire": True,
                    "compliance": "compliant"
                }
            },
            "access_controls": {
                "api_endpoints": {
                    "authentication": "required",
                    "rate_limiting": "enabled",
                    "audit_logging": "enabled"
                },
                "database_access": {
                    "role_based": True,
                    "principle": "least_privilege"
                }
            },
            "compliance_rules": [
                {
                    "rule_id": "RNF-002",
                    "description": "Technology restrictions compliance",
                    "status": "compliant",
                    "last_audit": "2025-11-07"
                },
                {
                    "rule_id": "DATA-001",
                    "description": "No PII in metrics",
                    "status": "compliant",
                    "enforcement": "schema_validation"
                },
                {
                    "rule_id": "DATA-002",
                    "description": "Data quality >= 80%",
                    "status": "monitored",
                    "current_score": DataQualityMonitor.assess_data_quality(30)["overall_score"]
                }
            ],
            "data_ownership": {
                "dora_metrics": {
                    "owner": "backend-team",
                    "steward": "data-team",
                    "contact": "backend-lead@iact.com"
                },
                "deployment_cycles": {
                    "owner": "devops-team",
                    "steward": "data-team",
                    "contact": "devops-lead@iact.com"
                }
            }
        }


class DataLineage:
    """
    Track data lineage and transformations.

    Tracks:
    - Data sources
    - Transformations
    - Data flow
    - Dependencies
    """

    @staticmethod
    def get_lineage_map() -> Dict[str, Any]:
        """Get complete data lineage map."""
        return {
            "lineage_version": "1.0.0",
            "generated_at": timezone.now().isoformat(),
            "data_flows": [
                {
                    "flow_id": "flow_001",
                    "name": "DORA Metrics Collection",
                    "description": "Collection of DORA metrics from application events",
                    "stages": [
                        {
                            "stage": "source",
                            "component": "Application Events",
                            "type": "event_stream",
                            "format": "python_objects"
                        },
                        {
                            "stage": "ingestion",
                            "component": "Django ORM",
                            "operations": ["validation", "serialization"],
                            "transformations": [
                                "Convert timestamps to UTC",
                                "Validate duration_seconds range",
                                "Generate unique IDs"
                            ]
                        },
                        {
                            "stage": "storage",
                            "component": "MySQL Database",
                            "table": "dora_metrics_dorametric",
                            "indexes": ["cycle_id", "feature_id", "created_at"]
                        },
                        {
                            "stage": "access",
                            "component": "REST APIs",
                            "endpoints": [
                                "/api/dora/metrics/",
                                "/api/dora/data-catalog/dora-metrics/"
                            ]
                        }
                    ]
                },
                {
                    "flow_id": "flow_002",
                    "name": "Application Logs Pipeline",
                    "description": "Structured JSON logging for application events",
                    "stages": [
                        {
                            "stage": "source",
                            "component": "Django Application",
                            "type": "log_events"
                        },
                        {
                            "stage": "formatting",
                            "component": "JSONFormatter",
                            "operations": ["structure", "enrich"],
                            "transformations": [
                                "Convert to JSON",
                                "Add timestamp",
                                "Add log level",
                                "Add context"
                            ]
                        },
                        {
                            "stage": "storage",
                            "component": "File System",
                            "location": "/var/log/iact/app.json.log",
                            "rotation": "100MB"
                        }
                    ]
                },
                {
                    "flow_id": "flow_003",
                    "name": "Infrastructure Logs Pipeline",
                    "description": "Collection of infraestructura logs to Cassandra",
                    "stages": [
                        {
                            "stage": "source",
                            "component": "System Logs",
                            "sources": ["syslog", "auth.log", "kern.log", "systemd"]
                        },
                        {
                            "stage": "collection",
                            "component": "Log Collector Daemon",
                            "operations": ["parse", "normalize", "batch"],
                            "batch_size": 1000
                        },
                        {
                            "stage": "storage",
                            "component": "Cassandra Cluster",
                            "keyspace": "logging",
                            "table": "infrastructure_logs",
                            "ttl": "90_days"
                        }
                    ]
                }
            ],
            "data_dependencies": [
                {
                    "dependent": "DORA Dashboard",
                    "depends_on": ["dora_metrics"],
                    "relationship": "reads_from",
                    "frequency": "real_time"
                },
                {
                    "dependent": "Data Catalog API",
                    "depends_on": ["dora_metrics", "deployment_cycles"],
                    "relationship": "aggregates",
                    "frequency": "on_demand"
                },
                {
                    "dependent": "Quality Monitoring",
                    "depends_on": ["dora_metrics"],
                    "relationship": "validates",
                    "frequency": "daily"
                }
            ]
        }


class EcosystemHealth:
    """
    Monitor overall data ecosystem health.

    Tracks:
    - System health metrics
    - Data pipeline status
    - Error rates
    - Performance metrics
    """

    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get comprehensive ecosystem health status."""
        quality_assessment = DataQualityMonitor.assess_data_quality(30)

        # Check data freshness
        recent_count = DORAMetric.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()

        # Calculate error indicators
        total_recent = DORAMetric.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        failed_deployments = DORAMetric.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7),
            phase_name='incident'
        ).count()

        error_rate = (failed_deployments / total_recent * 100) if total_recent > 0 else 0

        # Overall health score
        health_components = {
            "data_quality": quality_assessment["overall_score"],
            "data_freshness": min((recent_count / 10) * 100, 100),  # Expect at least 10 records/hour
            "error_rate_health": max(100 - (error_rate * 2), 0),  # Lower error rate = higher health
        }

        overall_health = sum(health_components.values()) / len(health_components)

        # Determine status
        if overall_health >= 90:
            status = "healthy"
            status_color = "green"
        elif overall_health >= 75:
            status = "warning"
            status_color = "yellow"
        else:
            status = "critical"
            status_color = "red"

        return {
            "overall_health_score": round(overall_health, 2),
            "status": status,
            "status_color": status_color,
            "assessed_at": timezone.now().isoformat(),
            "components": {
                "data_quality": {
                    "score": round(health_components["data_quality"], 2),
                    "status": "healthy" if health_components["data_quality"] >= 85 else "degraded",
                    "details": quality_assessment
                },
                "data_freshness": {
                    "score": round(health_components["data_freshness"], 2),
                    "recent_records_1h": recent_count,
                    "status": "healthy" if health_components["data_freshness"] >= 80 else "degraded"
                },
                "error_rate": {
                    "score": round(health_components["error_rate_health"], 2),
                    "incident_count_7d": failed_deployments,
                    "error_rate_percent": round(error_rate, 2),
                    "status": "healthy" if error_rate < 10 else "degraded"
                }
            },
            "data_pipelines": {
                "dora_metrics_collection": {
                    "status": "operational",
                    "last_data": DataLineage._get_last_metric_time(),
                    "throughput_24h": DORAMetric.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).count()
                },
                "application_logs": {
                    "status": "operational",
                    "location": "/var/log/iact/app.json.log"
                },
                "infrastructure_logs": {
                    "status": "operational",
                    "backend": "cassandra",
                    "ttl": "90_days"
                }
            },
            "recommendations": EcosystemHealth._get_health_recommendations(overall_health, health_components)
        }

    @staticmethod
    def _get_health_recommendations(overall_health: float, components: Dict[str, float]) -> List[str]:
        """Generate health recommendations."""
        recommendations = []

        if overall_health < 75:
            recommendations.append("URGENT: Ecosystem health below acceptable threshold. Investigate immediately.")

        if components["data_quality"] < 85:
            recommendations.append("Improve data quality: Review validation rules and data collection processes.")

        if components["data_freshness"] < 80:
            recommendations.append("Data freshness issue: Check data collection pipeline for delays or failures.")

        if components["error_rate_health"] < 70:
            recommendations.append("High error rate detected: Review recent deployments and incident patterns.")

        if not recommendations:
            recommendations.append("Ecosystem healthy. Continue monitoring and maintain current practices.")

        return recommendations


class MetadataManagement:
    """
    Manage metadata for all datasets.

    Tracks:
    - Schema versions
    - Field descriptions
    - Data types
    - Update history
    """

    @staticmethod
    def get_metadata_registry() -> Dict[str, Any]:
        """Get complete metadata registry."""
        return {
            "registry_version": "1.0.0",
            "last_updated": timezone.now().isoformat(),
            "datasets": [
                {
                    "dataset_id": "dora_metrics",
                    "schema_version": "1.0.0",
                    "table": "dora_metrics_dorametric",
                    "record_count": DORAMetric.objects.count(),
                    "size_estimate_mb": DORAMetric.objects.count() * 0.001,  # Rough estimate
                    "last_updated": DataLineage._get_last_metric_time(),
                    "fields": [
                        {
                            "name": "id",
                            "type": "AutoField",
                            "description": "Primary key",
                            "nullable": False,
                            "indexed": True
                        },
                        {
                            "name": "cycle_id",
                            "type": "CharField",
                            "max_length": 255,
                            "description": "Unique deployment cycle identifier",
                            "nullable": False,
                            "indexed": True,
                            "example": "cycle-2025-001"
                        },
                        {
                            "name": "feature_id",
                            "type": "CharField",
                            "max_length": 255,
                            "description": "Feature identifier",
                            "nullable": False,
                            "indexed": True,
                            "example": "FEAT-123"
                        },
                        {
                            "name": "phase_name",
                            "type": "CharField",
                            "max_length": 100,
                            "description": "SDLC phase name",
                            "nullable": False,
                            "indexed": True,
                            "enum": ["development", "testing", "deployment", "incident", "recovery"],
                            "example": "deployment"
                        },
                        {
                            "name": "decision",
                            "type": "CharField",
                            "max_length": 100,
                            "description": "Phase decision outcome",
                            "nullable": False,
                            "enum": ["approved", "rejected", "rollback", "resolved"],
                            "example": "approved"
                        },
                        {
                            "name": "duration_seconds",
                            "type": "FloatField",
                            "description": "Phase duration in seconds",
                            "nullable": False,
                            "min": 0,
                            "max": 86400,
                            "example": 1200.5
                        },
                        {
                            "name": "metadata",
                            "type": "JSONField",
                            "description": "Additional metadata",
                            "nullable": True,
                            "example": {"environment": "production"}
                        },
                        {
                            "name": "created_at",
                            "type": "DateTimeField",
                            "description": "Record creation timestamp",
                            "nullable": False,
                            "indexed": True,
                            "auto_now_add": True
                        }
                    ],
                    "indexes": [
                        {
                            "fields": ["cycle_id"],
                            "unique": False
                        },
                        {
                            "fields": ["feature_id"],
                            "unique": False
                        },
                        {
                            "fields": ["phase_name"],
                            "unique": False
                        },
                        {
                            "fields": ["created_at"],
                            "unique": False
                        }
                    ]
                }
            ]
        }


# Helper method for DataLineage class
def _get_last_metric_time():
    """Get timestamp of last metric."""
    last_metric = DORAMetric.objects.order_by('-created_at').first()
    return last_metric.created_at.isoformat() if last_metric else "never"

DataLineage._get_last_metric_time = staticmethod(_get_last_metric_time)
