"""AI Telemetry Collector - Sistema de telemetria para agentes IA."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import AITelemetry


class AITelemetryCollector:
    """Collector para telemetria de decisiones IA."""

    @staticmethod
    def record_decision(
        agent_id: str,
        task_type: str,
        decision: dict[str, Any],
        confidence: float,
        execution_time_ms: int,
        metadata: dict[str, Any] | None = None,
    ) -> AITelemetry:
        """
        Registrar decision de agente IA.

        Args:
            agent_id: Identificador del agente IA
            task_type: Tipo de tarea (deployment_risk, code_review, etc)
            decision: Decision tomada (estructura JSON)
            confidence: Score de confianza 0.0-1.0
            execution_time_ms: Tiempo de ejecucion en ms
            metadata: Metadata adicional

        Returns:
            Instancia de AITelemetry creada
        """
        telemetry = AITelemetry.objects.create(
            agent_id=agent_id,
            task_type=task_type,
            decision_made=decision,
            confidence_score=Decimal(str(confidence)),
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )
        return telemetry

    @staticmethod
    def record_feedback(
        telemetry_id: int,
        feedback: str,
    ) -> AITelemetry:
        """
        Registrar feedback humano sobre decision IA.

        Args:
            telemetry_id: ID de telemetria
            feedback: Feedback humano (correct, incorrect, partially_correct)

        Returns:
            Instancia de AITelemetry actualizada
        """
        telemetry = AITelemetry.objects.get(id=telemetry_id)
        telemetry.human_feedback = feedback

        # Calcular accuracy basado en feedback
        if feedback == "correct":
            telemetry.accuracy = Decimal("1.0000")
        elif feedback == "incorrect":
            telemetry.accuracy = Decimal("0.0000")
        elif feedback == "partially_correct":
            telemetry.accuracy = Decimal("0.5000")

        telemetry.save()
        return telemetry

    @staticmethod
    def calculate_accuracy(
        agent_id: str | None = None,
        task_type: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Calcular accuracy general o por agente/tipo.

        Args:
            agent_id: ID agente (None para todos)
            task_type: Tipo tarea (None para todos)
            days: Dias a considerar

        Returns:
            Dict con metricas de accuracy
        """
        cutoff = timezone.now() - timedelta(days=days)
        queryset = AITelemetry.objects.filter(
            created_at__gte=cutoff,
            human_feedback__isnull=False,
        )

        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        total_feedback = queryset.count()
        if total_feedback == 0:
            return {
                "total_decisions": 0,
                "total_with_feedback": 0,
                "accuracy_avg": 0.0,
                "correct_count": 0,
                "incorrect_count": 0,
                "partially_correct_count": 0,
            }

        correct_count = queryset.filter(human_feedback="correct").count()
        incorrect_count = queryset.filter(human_feedback="incorrect").count()
        partially_correct_count = queryset.filter(human_feedback="partially_correct").count()

        avg_accuracy = queryset.aggregate(avg=Avg("accuracy"))["avg"] or Decimal("0.0")

        return {
            "total_decisions": AITelemetry.objects.filter(
                created_at__gte=cutoff,
                agent_id=agent_id if agent_id else Q(),
                task_type=task_type if task_type else Q(),
            ).count(),
            "total_with_feedback": total_feedback,
            "accuracy_avg": float(avg_accuracy),
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "partially_correct_count": partially_correct_count,
        }

    @staticmethod
    def get_agent_stats(agent_id: str, days: int = 30) -> dict[str, Any]:
        """
        Obtener estadisticas de un agente.

        Args:
            agent_id: ID del agente
            days: Dias a considerar

        Returns:
            Dict con estadisticas del agente
        """
        cutoff = timezone.now() - timedelta(days=days)
        decisions = AITelemetry.objects.filter(
            agent_id=agent_id,
            created_at__gte=cutoff,
        )

        total_decisions = decisions.count()
        if total_decisions == 0:
            return {
                "agent_id": agent_id,
                "total_decisions": 0,
                "avg_confidence": 0.0,
                "avg_execution_time_ms": 0.0,
                "task_types": [],
                "accuracy_metrics": {},
            }

        # Estadisticas basicas
        avg_confidence = decisions.aggregate(avg=Avg("confidence_score"))["avg"] or Decimal("0.0")
        avg_execution_time = decisions.aggregate(avg=Avg("execution_time_ms"))["avg"] or 0

        # Task types
        task_types_stats = (
            decisions.values("task_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Accuracy metrics
        accuracy_metrics = AITelemetryCollector.calculate_accuracy(
            agent_id=agent_id,
            days=days,
        )

        return {
            "agent_id": agent_id,
            "total_decisions": total_decisions,
            "avg_confidence": float(avg_confidence),
            "avg_execution_time_ms": float(avg_execution_time),
            "task_types": list(task_types_stats),
            "accuracy_metrics": accuracy_metrics,
        }

    @staticmethod
    def get_confidence_distribution(
        agent_id: str | None = None,
        task_type: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Obtener distribucion de confidence scores.

        Args:
            agent_id: ID agente (None para todos)
            task_type: Tipo tarea (None para todos)
            days: Dias a considerar

        Returns:
            Dict con distribucion de confidence
        """
        cutoff = timezone.now() - timedelta(days=days)
        queryset = AITelemetry.objects.filter(created_at__gte=cutoff)

        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        # Buckets de confidence: 0-0.5, 0.5-0.7, 0.7-0.85, 0.85-0.95, 0.95-1.0
        low_confidence = queryset.filter(confidence_score__lt=Decimal("0.5")).count()
        medium_confidence = queryset.filter(
            confidence_score__gte=Decimal("0.5"),
            confidence_score__lt=Decimal("0.7"),
        ).count()
        good_confidence = queryset.filter(
            confidence_score__gte=Decimal("0.7"),
            confidence_score__lt=Decimal("0.85"),
        ).count()
        high_confidence = queryset.filter(
            confidence_score__gte=Decimal("0.85"),
            confidence_score__lt=Decimal("0.95"),
        ).count()
        very_high_confidence = queryset.filter(
            confidence_score__gte=Decimal("0.95"),
        ).count()

        total = queryset.count()

        return {
            "total_decisions": total,
            "distribution": {
                "low_0_50": {"count": low_confidence, "percentage": (low_confidence / total * 100) if total > 0 else 0},
                "medium_50_70": {"count": medium_confidence, "percentage": (medium_confidence / total * 100) if total > 0 else 0},
                "good_70_85": {"count": good_confidence, "percentage": (good_confidence / total * 100) if total > 0 else 0},
                "high_85_95": {"count": high_confidence, "percentage": (high_confidence / total * 100) if total > 0 else 0},
                "very_high_95_100": {"count": very_high_confidence, "percentage": (very_high_confidence / total * 100) if total > 0 else 0},
            },
        }

    @staticmethod
    def get_execution_time_trends(
        agent_id: str | None = None,
        task_type: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Obtener trends de execution time.

        Args:
            agent_id: ID agente (None para todos)
            task_type: Tipo tarea (None para todos)
            days: Dias a considerar

        Returns:
            Dict con trends de execution time
        """
        cutoff = timezone.now() - timedelta(days=days)
        queryset = AITelemetry.objects.filter(created_at__gte=cutoff)

        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        if queryset.count() == 0:
            return {
                "avg_execution_time_ms": 0.0,
                "min_execution_time_ms": 0,
                "max_execution_time_ms": 0,
                "p50_execution_time_ms": 0,
                "p95_execution_time_ms": 0,
                "p99_execution_time_ms": 0,
            }

        # Calcular percentiles manualmente
        execution_times = list(queryset.order_by("execution_time_ms").values_list("execution_time_ms", flat=True))
        count = len(execution_times)

        p50_idx = int(count * 0.5)
        p95_idx = int(count * 0.95)
        p99_idx = int(count * 0.99)

        avg_time = queryset.aggregate(avg=Avg("execution_time_ms"))["avg"] or 0

        return {
            "avg_execution_time_ms": float(avg_time),
            "min_execution_time_ms": execution_times[0] if execution_times else 0,
            "max_execution_time_ms": execution_times[-1] if execution_times else 0,
            "p50_execution_time_ms": execution_times[p50_idx] if execution_times else 0,
            "p95_execution_time_ms": execution_times[p95_idx] if execution_times else 0,
            "p99_execution_time_ms": execution_times[p99_idx] if execution_times else 0,
        }
