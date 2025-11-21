"""
Advanced Analytics for DORA Metrics.

Provides:
- Trend analysis
- Comparative analytics
- Historical reporting
- Anomaly trend detection
- Performance forecasting
- Statistical insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min, Q, StdDev, Variance
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from .models import DORAMetric
import statistics


class TrendAnalyzer:
    """
    Analyze trends in DORA metrics over time.

    Provides:
    - Historical trends
    - Trend direction (improving/declining/stable)
    - Rate of change
    - Trend predictions
    """

    @staticmethod
    def analyze_deployment_frequency_trend(days: int = 90) -> Dict[str, Any]:
        """Analyze deployment frequency trends."""
        start_date = timezone.now() - timedelta(days=days)

        # Get weekly deployment counts
        weekly_data = (
            DORAMetric.objects.filter(
                created_at__gte=start_date,
                phase_name='deployment'
            )
            .annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )

        weeks = []
        counts = []
        for item in weekly_data:
            weeks.append(item['week'].strftime('%Y-%W'))
            counts.append(item['count'])

        # Calculate trend
        if len(counts) >= 2:
            trend_direction = TrendAnalyzer._calculate_trend_direction(counts)
            avg_change = TrendAnalyzer._calculate_average_change(counts)
        else:
            trend_direction = 'insufficient_data'
            avg_change = 0

        return {
            "metric": "deployment_frequency",
            "period_days": days,
            "data_points": len(counts),
            "weekly_data": {
                "weeks": weeks,
                "counts": counts
            },
            "trend_analysis": {
                "direction": trend_direction,
                "average_weekly_change": round(avg_change, 2),
                "current_week_count": counts[-1] if counts else 0,
                "previous_week_count": counts[-2] if len(counts) >= 2 else 0,
                "week_over_week_change": counts[-1] - counts[-2] if len(counts) >= 2 else 0
            },
            "statistics": {
                "mean": round(statistics.mean(counts), 2) if counts else 0,
                "median": statistics.median(counts) if counts else 0,
                "std_dev": round(statistics.stdev(counts), 2) if len(counts) >= 2 else 0,
                "min": min(counts) if counts else 0,
                "max": max(counts) if counts else 0
            }
        }

    @staticmethod
    def analyze_lead_time_trend(days: int = 90) -> Dict[str, Any]:
        """Analyze lead time trends."""
        start_date = timezone.now() - timedelta(days=days)

        # Get weekly average lead times
        weekly_data = (
            DORAMetric.objects.filter(
                created_at__gte=start_date,
                phase_name='deployment'
            )
            .annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(avg_duration=Avg('duration_seconds'))
            .order_by('week')
        )

        weeks = []
        avg_durations_hours = []
        for item in weekly_data:
            weeks.append(item['week'].strftime('%Y-%W'))
            avg_durations_hours.append(round(item['avg_duration'] / 3600, 2))

        # Calculate trend
        if len(avg_durations_hours) >= 2:
            trend_direction = TrendAnalyzer._calculate_trend_direction(avg_durations_hours, inverse=True)
            avg_change = TrendAnalyzer._calculate_average_change(avg_durations_hours)
        else:
            trend_direction = 'insufficient_data'
            avg_change = 0

        return {
            "metric": "lead_time",
            "period_days": days,
            "data_points": len(avg_durations_hours),
            "weekly_data": {
                "weeks": weeks,
                "avg_lead_time_hours": avg_durations_hours
            },
            "trend_analysis": {
                "direction": trend_direction,
                "average_weekly_change_hours": round(avg_change, 2),
                "current_week_avg": avg_durations_hours[-1] if avg_durations_hours else 0,
                "previous_week_avg": avg_durations_hours[-2] if len(avg_durations_hours) >= 2 else 0,
                "week_over_week_change": round(
                    avg_durations_hours[-1] - avg_durations_hours[-2], 2
                ) if len(avg_durations_hours) >= 2 else 0
            },
            "statistics": {
                "mean": round(statistics.mean(avg_durations_hours), 2) if avg_durations_hours else 0,
                "median": round(statistics.median(avg_durations_hours), 2) if avg_durations_hours else 0,
                "std_dev": round(statistics.stdev(avg_durations_hours), 2) if len(avg_durations_hours) >= 2 else 0,
                "min": min(avg_durations_hours) if avg_durations_hours else 0,
                "max": max(avg_durations_hours) if avg_durations_hours else 0
            }
        }

    @staticmethod
    def _calculate_trend_direction(values: List[float], inverse: bool = False) -> str:
        """
        Calculate trend direction from values.

        Args:
            values: List of numeric values
            inverse: If True, decreasing values indicate improvement

        Returns:
            'improving', 'declining', or 'stable'
        """
        if len(values) < 2:
            return 'insufficient_data'

        # Calculate simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 'stable'

        slope = numerator / denominator

        # Determine significance (>5% change over period)
        total_change = abs(slope * n)
        avg_value = y_mean
        percent_change = (total_change / avg_value * 100) if avg_value > 0 else 0

        if percent_change < 5:
            return 'stable'

        # Interpret slope
        if inverse:
            # For metrics where lower is better (e.g., lead time)
            return 'improving' if slope < 0 else 'declining'
        else:
            # For metrics where higher is better (e.g., deployment frequency)
            return 'improving' if slope > 0 else 'declining'

    @staticmethod
    def _calculate_average_change(values: List[float]) -> float:
        """Calculate average change between consecutive values."""
        if len(values) < 2:
            return 0

        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        return sum(changes) / len(changes)


class ComparativeAnalytics:
    """
    Comparative analytics across different dimensions.

    Compares:
    - Period over period
    - Feature performance
    - Phase efficiency
    - Team performance
    """

    @staticmethod
    def period_over_period_comparison(current_days: int = 30, previous_days: int = 30) -> Dict[str, Any]:
        """Compare current period vs previous period."""
        current_end = timezone.now()
        current_start = current_end - timedelta(days=current_days)
        previous_end = current_start
        previous_start = previous_end - timedelta(days=previous_days)

        # Current period metrics
        current_metrics = DORAMetric.objects.filter(
            created_at__gte=current_start,
            created_at__lt=current_end
        )

        # Previous period metrics
        previous_metrics = DORAMetric.objects.filter(
            created_at__gte=previous_start,
            created_at__lt=previous_end
        )

        # Calculate metrics for both periods
        current_stats = ComparativeAnalytics._calculate_period_stats(current_metrics)
        previous_stats = ComparativeAnalytics._calculate_period_stats(previous_metrics)

        # Calculate changes
        changes = {
            "deployment_frequency": {
                "current": current_stats['deployment_count'],
                "previous": previous_stats['deployment_count'],
                "change": current_stats['deployment_count'] - previous_stats['deployment_count'],
                "percent_change": ComparativeAnalytics._calculate_percent_change(
                    previous_stats['deployment_count'],
                    current_stats['deployment_count']
                )
            },
            "lead_time_hours": {
                "current": current_stats['avg_lead_time_hours'],
                "previous": previous_stats['avg_lead_time_hours'],
                "change": current_stats['avg_lead_time_hours'] - previous_stats['avg_lead_time_hours'],
                "percent_change": ComparativeAnalytics._calculate_percent_change(
                    previous_stats['avg_lead_time_hours'],
                    current_stats['avg_lead_time_hours']
                )
            },
            "change_failure_rate": {
                "current": current_stats['change_failure_rate'],
                "previous": previous_stats['change_failure_rate'],
                "change": current_stats['change_failure_rate'] - previous_stats['change_failure_rate'],
                "percent_change": ComparativeAnalytics._calculate_percent_change(
                    previous_stats['change_failure_rate'],
                    current_stats['change_failure_rate']
                )
            }
        }

        return {
            "comparison_type": "period_over_period",
            "current_period": {
                "start": current_start.isoformat(),
                "end": current_end.isoformat(),
                "days": current_days
            },
            "previous_period": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "days": previous_days
            },
            "metrics": changes,
            "summary": ComparativeAnalytics._generate_comparison_summary(changes)
        }

    @staticmethod
    def _calculate_period_stats(metrics_queryset) -> Dict[str, float]:
        """Calculate statistics for a period."""
        deployment_metrics = metrics_queryset.filter(phase_name='deployment')
        deployment_count = deployment_metrics.count()

        avg_lead_time = deployment_metrics.aggregate(Avg('duration_seconds'))['duration_seconds__avg'] or 0
        avg_lead_time_hours = avg_lead_time / 3600

        # Calculate CFR
        incident_cycles = metrics_queryset.filter(phase_name='incident').values_list('cycle_id', flat=True).distinct()
        deployment_cycles = deployment_metrics.values_list('cycle_id', flat=True).distinct()

        total_deployments = len(deployment_cycles)
        failed_deployments = len(set(incident_cycles))

        change_failure_rate = (failed_deployments / total_deployments * 100) if total_deployments > 0 else 0

        return {
            'deployment_count': deployment_count,
            'avg_lead_time_hours': round(avg_lead_time_hours, 2),
            'change_failure_rate': round(change_failure_rate, 2)
        }

    @staticmethod
    def _calculate_percent_change(old_value: float, new_value: float) -> float:
        """Calculate percent change."""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0

        return round(((new_value - old_value) / old_value) * 100, 2)

    @staticmethod
    def _generate_comparison_summary(changes: Dict) -> str:
        """Generate human-readable comparison summary."""
        summaries = []

        # Deployment frequency
        df_change = changes['deployment_frequency']['percent_change']
        if df_change > 10:
            summaries.append(f"Deployment frequency increased significantly ({df_change:+.1f}%)")
        elif df_change < -10:
            summaries.append(f"Deployment frequency decreased significantly ({df_change:+.1f}%)")

        # Lead time
        lt_change = changes['lead_time_hours']['percent_change']
        if lt_change < -10:
            summaries.append(f"Lead time improved ({lt_change:+.1f}%)")
        elif lt_change > 10:
            summaries.append(f"Lead time degraded ({lt_change:+.1f}%)")

        # CFR
        cfr_change = changes['change_failure_rate']['percent_change']
        if cfr_change < -10:
            summaries.append(f"Change failure rate improved ({cfr_change:+.1f}%)")
        elif cfr_change > 10:
            summaries.append(f"Change failure rate degraded ({cfr_change:+.1f}%)")

        if not summaries:
            return "No significant changes between periods"

        return "; ".join(summaries)


class HistoricalReporting:
    """
    Generate historical reports with various time granularities.

    Supports:
    - Daily reports
    - Weekly reports
    - Monthly reports
    - Custom date ranges
    """

    @staticmethod
    def generate_monthly_report(months: int = 6) -> Dict[str, Any]:
        """Generate monthly historical report."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months * 30)

        monthly_data = (
            DORAMetric.objects.filter(
                created_at__gte=start_date,
                phase_name='deployment'
            )
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(
                deployment_count=Count('id'),
                avg_duration=Avg('duration_seconds')
            )
            .order_by('month')
        )

        months_list = []
        deployment_counts = []
        avg_lead_times = []

        for item in monthly_data:
            months_list.append(item['month'].strftime('%Y-%m'))
            deployment_counts.append(item['deployment_count'])
            avg_lead_times.append(round(item['avg_duration'] / 3600, 2))

        return {
            "report_type": "monthly",
            "period_months": months,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": {
                "months": months_list,
                "deployment_frequency": deployment_counts,
                "avg_lead_time_hours": avg_lead_times
            },
            "summary": {
                "total_deployments": sum(deployment_counts),
                "avg_deployments_per_month": round(
                    sum(deployment_counts) / len(deployment_counts), 2
                ) if deployment_counts else 0,
                "best_month": {
                    "month": months_list[deployment_counts.index(max(deployment_counts))] if deployment_counts else None,
                    "deployments": max(deployment_counts) if deployment_counts else 0
                },
                "worst_month": {
                    "month": months_list[deployment_counts.index(min(deployment_counts))] if deployment_counts else None,
                    "deployments": min(deployment_counts) if deployment_counts else 0
                }
            }
        }


class AnomalyTrendDetector:
    """
    Detect anomaly trends and patterns.

    Identifies:
    - Recurring anomalies
    - Anomaly clusters
    - Seasonal patterns
    - Outlier trends
    """

    @staticmethod
    def detect_duration_anomalies(days: int = 30) -> Dict[str, Any]:
        """Detect anomalies in deployment durations."""
        start_date = timezone.now() - timedelta(days=days)

        deployments = DORAMetric.objects.filter(
            created_at__gte=start_date,
            phase_name='deployment'
        )

        durations = list(deployments.values_list('duration_seconds', flat=True))

        if len(durations) < 10:
            return {
                "status": "insufficient_data",
                "message": "Need at least 10 data points for anomaly detection"
            }

        # Calculate IQR for anomaly detection
        q1 = statistics.quantiles(durations, n=4)[0]
        q3 = statistics.quantiles(durations, n=4)[2]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find anomalies
        anomalies = deployments.filter(
            Q(duration_seconds__lt=lower_bound) | Q(duration_seconds__gt=upper_bound)
        )

        anomaly_list = []
        for anomaly in anomalies:
            anomaly_list.append({
                "cycle_id": anomaly.cycle_id,
                "feature_id": anomaly.feature_id,
                "duration_seconds": anomaly.duration_seconds,
                "duration_hours": round(anomaly.duration_seconds / 3600, 2),
                "created_at": anomaly.created_at.isoformat(),
                "type": "unusually_fast" if anomaly.duration_seconds < lower_bound else "unusually_slow"
            })

        return {
            "period_days": days,
            "total_deployments": len(durations),
            "anomalies_detected": len(anomaly_list),
            "anomaly_rate": round(len(anomaly_list) / len(durations) * 100, 2),
            "thresholds": {
                "lower_bound_seconds": round(lower_bound, 2),
                "upper_bound_seconds": round(upper_bound, 2),
                "lower_bound_hours": round(lower_bound / 3600, 2),
                "upper_bound_hours": round(upper_bound / 3600, 2)
            },
            "statistics": {
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "iqr": round(iqr, 2),
                "mean": round(statistics.mean(durations), 2),
                "median": round(statistics.median(durations), 2),
                "std_dev": round(statistics.stdev(durations), 2)
            },
            "anomalies": anomaly_list[:20]  # Limit to 20 most recent
        }


class PerformanceForecasting:
    """
    Simple performance forecasting based on historical trends.

    Provides:
    - Next period prediction
    - Trend-based forecasts
    - Confidence intervals
    """

    @staticmethod
    def forecast_next_month(historical_months: int = 6) -> Dict[str, Any]:
        """Forecast next month's metrics based on historical trend."""
        monthly_report = HistoricalReporting.generate_monthly_report(historical_months)

        deployment_counts = monthly_report['data']['deployment_frequency']
        lead_times = monthly_report['data']['avg_lead_time_hours']

        if len(deployment_counts) < 3:
            return {
                "status": "insufficient_data",
                "message": "Need at least 3 months of data for forecasting"
            }

        # Simple linear extrapolation
        df_forecast = PerformanceForecasting._linear_forecast(deployment_counts)
        lt_forecast = PerformanceForecasting._linear_forecast(lead_times)

        return {
            "forecast_period": "next_month",
            "based_on_months": historical_months,
            "forecasts": {
                "deployment_frequency": {
                    "predicted": round(df_forecast, 0),
                    "current_avg": round(statistics.mean(deployment_counts), 1),
                    "trend": "increasing" if df_forecast > deployment_counts[-1] else "decreasing"
                },
                "lead_time_hours": {
                    "predicted": round(lt_forecast, 2),
                    "current_avg": round(statistics.mean(lead_times), 2),
                    "trend": "increasing" if lt_forecast > lead_times[-1] else "decreasing"
                }
            },
            "confidence": "low" if historical_months < 6 else "medium",
            "note": "Forecasts based on simple linear trend extrapolation"
        }

    @staticmethod
    def _linear_forecast(values: List[float]) -> float:
        """Simple linear forecast for next value."""
        if len(values) < 2:
            return values[-1] if values else 0

        # Calculate average change
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)

        # Predict next value
        return values[-1] + avg_change
