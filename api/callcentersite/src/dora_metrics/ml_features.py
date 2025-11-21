"""Feature Engineering para Predictive Analytics - TASK-033."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count, Avg
from django.utils import timezone

from .models import DORAMetric


class FeatureExtractor:
    """Extractor de features para modelos ML de prediccion de riesgo."""

    @staticmethod
    def extract_deployment_features(cycle_id: str) -> dict[str, Any] | None:
        """
        Extraer features de un deployment cycle para prediccion.

        Args:
            cycle_id: ID del deployment cycle

        Returns:
            Dict con features extraidos, o None si no existe
        """
        try:
            # Obtener metricas del cycle
            cycle_metrics = DORAMetric.objects.filter(cycle_id=cycle_id)

            if not cycle_metrics.exists():
                return None

            # Feature 1: Lead Time (seconds)
            deployment_metric = cycle_metrics.filter(phase_name="deployment").first()
            if not deployment_metric:
                return None

            lead_time = float(deployment_metric.duration_seconds)

            # Feature 2: Tests Passed (%)
            testing_metrics = cycle_metrics.filter(phase_name="testing")
            total_tests = testing_metrics.count()
            passed_tests = testing_metrics.filter(decision="go").count()
            tests_passed_pct = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            # Feature 3: Code Changes Size (estimado por metadata)
            code_changes_size = deployment_metric.metadata.get("code_changes_size", 100)

            # Feature 4: Time of Day (hour 0-23)
            time_of_day = deployment_metric.created_at.hour

            # Feature 5: Day of Week (0=Monday, 6=Sunday)
            day_of_week = deployment_metric.created_at.weekday()

            # Feature 6: Previous Failures (ultimos 7 dias)
            seven_days_ago = deployment_metric.created_at - timedelta(days=7)
            previous_failures = DORAMetric.objects.filter(
                phase_name="testing",
                decision="no-go",
                created_at__gte=seven_days_ago,
                created_at__lt=deployment_metric.created_at,
            ).count()

            # Feature 7: Team Velocity (deployments en ultimos 7 dias)
            team_velocity = DORAMetric.objects.filter(
                phase_name="deployment",
                created_at__gte=seven_days_ago,
                created_at__lt=deployment_metric.created_at,
            ).count()

            # Feature 8: Planning Duration (si existe fase planning)
            planning_metric = cycle_metrics.filter(phase_name="planning").first()
            planning_duration = float(planning_metric.duration_seconds) if planning_metric else 0

            # Feature 9: Feature Complexity (de metadata)
            feature_complexity = deployment_metric.metadata.get("feature_complexity", "medium")
            feature_complexity_score = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "critical": 4,
            }.get(feature_complexity, 2)

            # Feature 10: Code Review Score (de metadata)
            code_review_score = deployment_metric.metadata.get("code_review_score", 0.8)

            # Target: Deployment Failed (basado en metadata o metricas posteriores)
            # Si existe fase maintenance con decision='blocked', el deployment fallo
            maintenance_failed = cycle_metrics.filter(
                phase_name="maintenance",
                decision="blocked",
            ).exists()

            return {
                "cycle_id": cycle_id,
                "lead_time": lead_time,
                "tests_passed_pct": tests_passed_pct,
                "code_changes_size": code_changes_size,
                "time_of_day": time_of_day,
                "day_of_week": day_of_week,
                "previous_failures": previous_failures,
                "team_velocity": team_velocity,
                "planning_duration": planning_duration,
                "feature_complexity_score": feature_complexity_score,
                "code_review_score": code_review_score,
                "deployment_failed": 1 if maintenance_failed else 0,
            }

        except Exception as e:
            print(f"Error extracting features for {cycle_id}: {e}")
            return None

    @staticmethod
    def create_training_dataset(days: int = 90) -> list[dict[str, Any]]:
        """
        Crear dataset de training con features de deployments recientes.

        Args:
            days: Numero de dias de historia a usar

        Returns:
            Lista de dicts con features para training
        """
        cutoff = timezone.now() - timedelta(days=days)

        # Obtener todos los cycle_ids en el periodo
        deployment_metrics = DORAMetric.objects.filter(
            phase_name="deployment",
            created_at__gte=cutoff,
        ).values_list("cycle_id", flat=True)

        # Extraer features para cada cycle
        dataset = []
        for cycle_id in deployment_metrics:
            features = FeatureExtractor.extract_deployment_features(cycle_id)
            if features:
                dataset.append(features)

        return dataset

    @staticmethod
    def normalize_features(features: dict[str, Any]) -> dict[str, float]:
        """
        Normalizar features para uso en ML.

        Args:
            features: Features raw

        Returns:
            Features normalizados (valores 0.0-1.0)
        """
        # Lead time: normalizar a horas (max 48 horas = 172800 segundos)
        lead_time_normalized = min(features["lead_time"] / 172800.0, 1.0)

        # Tests passed: ya esta en 0-100, convertir a 0-1
        tests_passed_normalized = features["tests_passed_pct"] / 100.0

        # Code changes size: normalizar (max 1000 lineas)
        code_changes_normalized = min(features["code_changes_size"] / 1000.0, 1.0)

        # Time of day: normalizar (0-23 -> 0-1)
        time_of_day_normalized = features["time_of_day"] / 23.0

        # Day of week: normalizar (0-6 -> 0-1)
        day_of_week_normalized = features["day_of_week"] / 6.0

        # Previous failures: normalizar (max 20 failures)
        previous_failures_normalized = min(features["previous_failures"] / 20.0, 1.0)

        # Team velocity: normalizar (max 50 deployments/week)
        team_velocity_normalized = min(features["team_velocity"] / 50.0, 1.0)

        # Planning duration: normalizar a horas (max 24 horas = 86400 segundos)
        planning_duration_normalized = min(features["planning_duration"] / 86400.0, 1.0)

        # Feature complexity: normalizar (1-4 -> 0-1)
        feature_complexity_normalized = (features["feature_complexity_score"] - 1) / 3.0

        # Code review score: ya esta en 0-1
        code_review_score_normalized = features["code_review_score"]

        return {
            "lead_time": lead_time_normalized,
            "tests_passed_pct": tests_passed_normalized,
            "code_changes_size": code_changes_normalized,
            "time_of_day": time_of_day_normalized,
            "day_of_week": day_of_week_normalized,
            "previous_failures": previous_failures_normalized,
            "team_velocity": team_velocity_normalized,
            "planning_duration": planning_duration_normalized,
            "feature_complexity_score": feature_complexity_normalized,
            "code_review_score": code_review_score_normalized,
        }

    @staticmethod
    def get_feature_names() -> list[str]:
        """
        Obtener nombres de features en orden.

        Returns:
            Lista de nombres de features
        """
        return [
            "lead_time",
            "tests_passed_pct",
            "code_changes_size",
            "time_of_day",
            "day_of_week",
            "previous_failures",
            "team_velocity",
            "planning_duration",
            "feature_complexity_score",
            "code_review_score",
        ]

    @staticmethod
    def features_to_array(features: dict[str, Any]) -> list[float]:
        """
        Convertir features dict a array para ML.

        Args:
            features: Features normalizados

        Returns:
            Array de floats en orden consistente
        """
        feature_names = FeatureExtractor.get_feature_names()
        return [features[name] for name in feature_names]
