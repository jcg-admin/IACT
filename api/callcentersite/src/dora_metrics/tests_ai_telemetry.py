"""Tests para AI Telemetry System - TASK-024."""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from .ai_telemetry import AITelemetryCollector
from .models import AITelemetry


class AITelemetryCollectorTestCase(TestCase):
    """Tests para AITelemetryCollector."""

    def setUp(self):
        """Setup inicial para tests."""
        self.agent_id = "deployment-risk-predictor"
        self.task_type = "deployment_risk"
        self.decision = {"action": "approve", "risk_score": 0.15}
        self.confidence = 0.92
        self.execution_time_ms = 150

    def test_record_decision(self):
        """Test registrar decision IA."""
        telemetry = AITelemetryCollector.record_decision(
            agent_id=self.agent_id,
            task_type=self.task_type,
            decision=self.decision,
            confidence=self.confidence,
            execution_time_ms=self.execution_time_ms,
        )

        self.assertIsNotNone(telemetry.id)
        self.assertEqual(telemetry.agent_id, self.agent_id)
        self.assertEqual(telemetry.task_type, self.task_type)
        self.assertEqual(telemetry.decision_made, self.decision)
        self.assertEqual(telemetry.confidence_score, Decimal("0.9200"))
        self.assertEqual(telemetry.execution_time_ms, self.execution_time_ms)
        self.assertIsNone(telemetry.human_feedback)
        self.assertIsNone(telemetry.accuracy)

    def test_record_decision_with_metadata(self):
        """Test registrar decision con metadata."""
        metadata = {"model_version": "v1.2.3", "features_used": 15}

        telemetry = AITelemetryCollector.record_decision(
            agent_id=self.agent_id,
            task_type=self.task_type,
            decision=self.decision,
            confidence=self.confidence,
            execution_time_ms=self.execution_time_ms,
            metadata=metadata,
        )

        self.assertEqual(telemetry.metadata, metadata)

    def test_record_feedback_correct(self):
        """Test registrar feedback correcto."""
        telemetry = AITelemetryCollector.record_decision(
            agent_id=self.agent_id,
            task_type=self.task_type,
            decision=self.decision,
            confidence=self.confidence,
            execution_time_ms=self.execution_time_ms,
        )

        updated = AITelemetryCollector.record_feedback(
            telemetry_id=telemetry.id,
            feedback="correct",
        )

        self.assertEqual(updated.human_feedback, "correct")
        self.assertEqual(updated.accuracy, Decimal("1.0000"))

    def test_record_feedback_incorrect(self):
        """Test registrar feedback incorrecto."""
        telemetry = AITelemetryCollector.record_decision(
            agent_id=self.agent_id,
            task_type=self.task_type,
            decision=self.decision,
            confidence=self.confidence,
            execution_time_ms=self.execution_time_ms,
        )

        updated = AITelemetryCollector.record_feedback(
            telemetry_id=telemetry.id,
            feedback="incorrect",
        )

        self.assertEqual(updated.human_feedback, "incorrect")
        self.assertEqual(updated.accuracy, Decimal("0.0000"))

    def test_record_feedback_partially_correct(self):
        """Test registrar feedback parcialmente correcto."""
        telemetry = AITelemetryCollector.record_decision(
            agent_id=self.agent_id,
            task_type=self.task_type,
            decision=self.decision,
            confidence=self.confidence,
            execution_time_ms=self.execution_time_ms,
        )

        updated = AITelemetryCollector.record_feedback(
            telemetry_id=telemetry.id,
            feedback="partially_correct",
        )

        self.assertEqual(updated.human_feedback, "partially_correct")
        self.assertEqual(updated.accuracy, Decimal("0.5000"))

    def test_calculate_accuracy_no_feedback(self):
        """Test calcular accuracy sin feedback."""
        # Crear decisiones sin feedback
        for i in range(5):
            AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )

        accuracy_stats = AITelemetryCollector.calculate_accuracy(days=30)

        self.assertEqual(accuracy_stats["total_decisions"], 5)
        self.assertEqual(accuracy_stats["total_with_feedback"], 0)
        self.assertEqual(accuracy_stats["accuracy_avg"], 0.0)

    def test_calculate_accuracy_with_feedback(self):
        """Test calcular accuracy con feedback."""
        # Crear 5 decisiones correctas
        for i in range(5):
            telemetry = AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )
            AITelemetryCollector.record_feedback(telemetry.id, "correct")

        # Crear 3 decisiones incorrectas
        for i in range(3):
            telemetry = AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )
            AITelemetryCollector.record_feedback(telemetry.id, "incorrect")

        # Crear 2 decisiones parcialmente correctas
        for i in range(2):
            telemetry = AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )
            AITelemetryCollector.record_feedback(telemetry.id, "partially_correct")

        accuracy_stats = AITelemetryCollector.calculate_accuracy(days=30)

        self.assertEqual(accuracy_stats["total_decisions"], 10)
        self.assertEqual(accuracy_stats["total_with_feedback"], 10)
        self.assertEqual(accuracy_stats["correct_count"], 5)
        self.assertEqual(accuracy_stats["incorrect_count"], 3)
        self.assertEqual(accuracy_stats["partially_correct_count"], 2)
        # (5*1.0 + 3*0.0 + 2*0.5) / 10 = 6.0 / 10 = 0.6
        self.assertEqual(accuracy_stats["accuracy_avg"], 0.6)

    def test_calculate_accuracy_by_agent(self):
        """Test calcular accuracy filtrado por agente."""
        # Crear decisiones para agent 1
        for i in range(3):
            telemetry = AITelemetryCollector.record_decision(
                agent_id="agent-1",
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )
            AITelemetryCollector.record_feedback(telemetry.id, "correct")

        # Crear decisiones para agent 2
        for i in range(2):
            telemetry = AITelemetryCollector.record_decision(
                agent_id="agent-2",
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=self.execution_time_ms,
            )
            AITelemetryCollector.record_feedback(telemetry.id, "incorrect")

        # Verificar accuracy de agent-1
        accuracy_stats = AITelemetryCollector.calculate_accuracy(agent_id="agent-1", days=30)
        self.assertEqual(accuracy_stats["total_with_feedback"], 3)
        self.assertEqual(accuracy_stats["correct_count"], 3)
        self.assertEqual(accuracy_stats["accuracy_avg"], 1.0)

        # Verificar accuracy de agent-2
        accuracy_stats = AITelemetryCollector.calculate_accuracy(agent_id="agent-2", days=30)
        self.assertEqual(accuracy_stats["total_with_feedback"], 2)
        self.assertEqual(accuracy_stats["incorrect_count"], 2)
        self.assertEqual(accuracy_stats["accuracy_avg"], 0.0)

    def test_get_agent_stats(self):
        """Test obtener estadisticas de agente."""
        # Crear decisiones para el agente
        for i in range(5):
            AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=0.8 + (i * 0.02),  # Variar confidence
                execution_time_ms=100 + (i * 10),  # Variar execution time
            )

        stats = AITelemetryCollector.get_agent_stats(self.agent_id, days=30)

        self.assertEqual(stats["agent_id"], self.agent_id)
        self.assertEqual(stats["total_decisions"], 5)
        self.assertGreater(stats["avg_confidence"], 0.8)
        self.assertGreater(stats["avg_execution_time_ms"], 100)
        self.assertEqual(len(stats["task_types"]), 1)
        self.assertEqual(stats["task_types"][0]["task_type"], self.task_type)
        self.assertEqual(stats["task_types"][0]["count"], 5)

    def test_get_confidence_distribution(self):
        """Test obtener distribucion de confidence scores."""
        # Crear decisiones con diferentes confidence levels
        AITelemetryCollector.record_decision(
            agent_id=self.agent_id, task_type=self.task_type,
            decision=self.decision, confidence=0.3, execution_time_ms=100
        )
        AITelemetryCollector.record_decision(
            agent_id=self.agent_id, task_type=self.task_type,
            decision=self.decision, confidence=0.6, execution_time_ms=100
        )
        AITelemetryCollector.record_decision(
            agent_id=self.agent_id, task_type=self.task_type,
            decision=self.decision, confidence=0.75, execution_time_ms=100
        )
        AITelemetryCollector.record_decision(
            agent_id=self.agent_id, task_type=self.task_type,
            decision=self.decision, confidence=0.9, execution_time_ms=100
        )
        AITelemetryCollector.record_decision(
            agent_id=self.agent_id, task_type=self.task_type,
            decision=self.decision, confidence=0.97, execution_time_ms=100
        )

        dist = AITelemetryCollector.get_confidence_distribution(days=30)

        self.assertEqual(dist["total_decisions"], 5)
        self.assertEqual(dist["distribution"]["low_0_50"]["count"], 1)
        self.assertEqual(dist["distribution"]["medium_50_70"]["count"], 1)
        self.assertEqual(dist["distribution"]["good_70_85"]["count"], 1)
        self.assertEqual(dist["distribution"]["high_85_95"]["count"], 1)
        self.assertEqual(dist["distribution"]["very_high_95_100"]["count"], 1)

    def test_get_execution_time_trends(self):
        """Test obtener trends de execution time."""
        execution_times = [100, 150, 200, 250, 300]

        for time_ms in execution_times:
            AITelemetryCollector.record_decision(
                agent_id=self.agent_id,
                task_type=self.task_type,
                decision=self.decision,
                confidence=self.confidence,
                execution_time_ms=time_ms,
            )

        trends = AITelemetryCollector.get_execution_time_trends(days=30)

        self.assertEqual(trends["min_execution_time_ms"], 100)
        self.assertEqual(trends["max_execution_time_ms"], 300)
        self.assertEqual(trends["avg_execution_time_ms"], 200.0)
        self.assertGreater(trends["p50_execution_time_ms"], 0)
        self.assertGreater(trends["p95_execution_time_ms"], 0)


class AITelemetryModelTestCase(TestCase):
    """Tests para modelo AITelemetry."""

    def test_create_telemetry(self):
        """Test crear instancia de AITelemetry."""
        telemetry = AITelemetry.objects.create(
            agent_id="test-agent",
            task_type="test_task",
            decision_made={"result": "success"},
            confidence_score=Decimal("0.8500"),
            execution_time_ms=120,
        )

        self.assertIsNotNone(telemetry.id)
        self.assertEqual(telemetry.agent_id, "test-agent")
        self.assertEqual(telemetry.task_type, "test_task")
        self.assertIsNone(telemetry.human_feedback)
        self.assertIsNone(telemetry.accuracy)
        self.assertIsNotNone(telemetry.created_at)

    def test_telemetry_ordering(self):
        """Test que telemetry se ordena por created_at descendente."""
        telemetry1 = AITelemetry.objects.create(
            agent_id="agent-1",
            task_type="task",
            decision_made={},
            confidence_score=Decimal("0.8"),
            execution_time_ms=100,
        )

        telemetry2 = AITelemetry.objects.create(
            agent_id="agent-2",
            task_type="task",
            decision_made={},
            confidence_score=Decimal("0.9"),
            execution_time_ms=150,
        )

        telemetries = list(AITelemetry.objects.all())

        # El mas reciente debe estar primero
        self.assertEqual(telemetries[0].id, telemetry2.id)
        self.assertEqual(telemetries[1].id, telemetry1.id)

    def test_telemetry_str_representation(self):
        """Test representacion string de AITelemetry."""
        telemetry = AITelemetry.objects.create(
            agent_id="test-agent",
            task_type="test_task",
            decision_made={},
            confidence_score=Decimal("0.85"),
            execution_time_ms=100,
        )

        str_repr = str(telemetry)
        self.assertIn("test-agent", str_repr)
        self.assertIn("test_task", str_repr)
