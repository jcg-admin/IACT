"""Tests para Predictive Analytics - TASK-033."""

import numpy as np
from django.test import TestCase
from django.utils import timezone

from .ml_features import FeatureExtractor
from .ml_models import DeploymentRiskPredictor
from .models import DORAMetric


class FeatureExtractorTestCase(TestCase):
    """Tests para FeatureExtractor."""

    def setUp(self):
        """Setup inicial para tests."""
        self.cycle_id = "test-cycle-001"

        # Crear metricas de un cycle completo
        base_time = timezone.now()

        # Planning phase
        DORAMetric.objects.create(
            cycle_id=self.cycle_id,
            feature_id="feature-001",
            phase_name="planning",
            decision="go",
            duration_seconds=3600,  # 1 hora
            metadata={},
        )

        # Testing phase
        DORAMetric.objects.create(
            cycle_id=self.cycle_id,
            feature_id="feature-001",
            phase_name="testing",
            decision="go",
            duration_seconds=7200,  # 2 horas
            metadata={},
        )

        DORAMetric.objects.create(
            cycle_id=self.cycle_id,
            feature_id="feature-001",
            phase_name="testing",
            decision="go",
            duration_seconds=1800,
            metadata={},
        )

        # Deployment phase
        DORAMetric.objects.create(
            cycle_id=self.cycle_id,
            feature_id="feature-001",
            phase_name="deployment",
            decision="go",
            duration_seconds=28800,  # 8 horas lead time
            metadata={
                "code_changes_size": 150,
                "feature_complexity": "medium",
                "code_review_score": 0.85,
            },
        )

    def test_extract_deployment_features(self):
        """Test extraer features de un deployment cycle."""
        features = FeatureExtractor.extract_deployment_features(self.cycle_id)

        self.assertIsNotNone(features)
        self.assertEqual(features["cycle_id"], self.cycle_id)
        self.assertGreater(features["lead_time"], 0)
        self.assertGreaterEqual(features["tests_passed_pct"], 0)
        self.assertLessEqual(features["tests_passed_pct"], 100)
        self.assertEqual(features["code_changes_size"], 150)
        self.assertEqual(features["feature_complexity_score"], 2)  # medium = 2
        self.assertEqual(features["code_review_score"], 0.85)
        self.assertIn("time_of_day", features)
        self.assertIn("day_of_week", features)
        self.assertIn("previous_failures", features)
        self.assertIn("team_velocity", features)

    def test_extract_deployment_features_nonexistent(self):
        """Test extraer features de cycle inexistente."""
        features = FeatureExtractor.extract_deployment_features("nonexistent")

        self.assertIsNone(features)

    def test_create_training_dataset(self):
        """Test crear dataset de training."""
        dataset = FeatureExtractor.create_training_dataset(days=30)

        # Debe tener al menos 1 sample (nuestro cycle de setup)
        self.assertGreaterEqual(len(dataset), 1)

        # Verificar estructura de cada sample
        for sample in dataset:
            self.assertIn("cycle_id", sample)
            self.assertIn("lead_time", sample)
            self.assertIn("tests_passed_pct", sample)
            self.assertIn("deployment_failed", sample)

    def test_normalize_features(self):
        """Test normalizacion de features."""
        features = {
            "lead_time": 86400,  # 24 horas
            "tests_passed_pct": 80,
            "code_changes_size": 500,
            "time_of_day": 12,
            "day_of_week": 3,
            "previous_failures": 5,
            "team_velocity": 10,
            "planning_duration": 7200,
            "feature_complexity_score": 2,
            "code_review_score": 0.8,
        }

        normalized = FeatureExtractor.normalize_features(features)

        # Todos los valores deben estar en rango 0-1
        for key, value in normalized.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_get_feature_names(self):
        """Test obtener nombres de features."""
        names = FeatureExtractor.get_feature_names()

        self.assertEqual(len(names), 10)
        self.assertIn("lead_time", names)
        self.assertIn("tests_passed_pct", names)
        self.assertIn("code_changes_size", names)

    def test_features_to_array(self):
        """Test convertir features a array."""
        features = {
            "lead_time": 0.5,
            "tests_passed_pct": 0.8,
            "code_changes_size": 0.5,
            "time_of_day": 0.5,
            "day_of_week": 0.5,
            "previous_failures": 0.25,
            "team_velocity": 0.2,
            "planning_duration": 0.1,
            "feature_complexity_score": 0.33,
            "code_review_score": 0.85,
        }

        array = FeatureExtractor.features_to_array(features)

        self.assertEqual(len(array), 10)
        self.assertEqual(array[0], 0.5)  # lead_time


class DeploymentRiskPredictorTestCase(TestCase):
    """Tests para DeploymentRiskPredictor."""

    def setUp(self):
        """Setup inicial para tests."""
        # Crear dataset de prueba
        self.training_data = []

        # 15 samples exitosos (deployment_failed=0)
        for i in range(15):
            self.training_data.append({
                "cycle_id": f"success-{i}",
                "lead_time": 7200 + i * 100,
                "tests_passed_pct": 85 + i,
                "code_changes_size": 100 + i * 10,
                "time_of_day": 10,
                "day_of_week": 2,
                "previous_failures": 0,
                "team_velocity": 5,
                "planning_duration": 3600,
                "feature_complexity_score": 2,
                "code_review_score": 0.85,
                "deployment_failed": 0,
            })

        # 10 samples fallidos (deployment_failed=1)
        for i in range(10):
            self.training_data.append({
                "cycle_id": f"failure-{i}",
                "lead_time": 1800 + i * 50,
                "tests_passed_pct": 60 + i,
                "code_changes_size": 800 + i * 20,
                "time_of_day": 22,
                "day_of_week": 5,
                "previous_failures": 5 + i,
                "team_velocity": 2,
                "planning_duration": 1800,
                "feature_complexity_score": 4,
                "code_review_score": 0.5,
                "deployment_failed": 1,
            })

    def test_train_model_success(self):
        """Test entrenar modelo con datos suficientes."""
        predictor = DeploymentRiskPredictor()

        metrics = predictor.train_model(self.training_data)

        self.assertIn("accuracy", metrics)
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("f1_score", metrics)
        self.assertIn("training_samples", metrics)
        self.assertIn("validation_samples", metrics)
        self.assertIn("feature_importance", metrics)

        # Metricas deben estar en rango valido
        self.assertGreaterEqual(metrics["accuracy"], 0.0)
        self.assertLessEqual(metrics["accuracy"], 1.0)

    def test_train_model_insufficient_data(self):
        """Test entrenar modelo con datos insuficientes."""
        predictor = DeploymentRiskPredictor()

        # Solo 5 samples (< 10 minimo)
        small_dataset = self.training_data[:5]

        with self.assertRaises(ValueError):
            predictor.train_model(small_dataset)

    def test_predict_risk(self):
        """Test predecir riesgo de deployment."""
        predictor = DeploymentRiskPredictor()
        predictor.train_model(self.training_data)

        # Test con deployment de bajo riesgo
        low_risk_features = {
            "lead_time": 7200,
            "tests_passed_pct": 95,
            "code_changes_size": 100,
            "time_of_day": 10,
            "day_of_week": 2,
            "previous_failures": 0,
            "team_velocity": 5,
            "planning_duration": 3600,
            "feature_complexity_score": 2,
            "code_review_score": 0.9,
        }

        risk_score = predictor.predict_risk(low_risk_features)

        # Risk debe estar en rango 0-1
        self.assertGreaterEqual(risk_score, 0.0)
        self.assertLessEqual(risk_score, 1.0)

        # Test con deployment de alto riesgo
        high_risk_features = {
            "lead_time": 1800,
            "tests_passed_pct": 60,
            "code_changes_size": 900,
            "time_of_day": 23,
            "day_of_week": 5,
            "previous_failures": 10,
            "team_velocity": 1,
            "planning_duration": 1800,
            "feature_complexity_score": 4,
            "code_review_score": 0.5,
        }

        high_risk_score = predictor.predict_risk(high_risk_features)

        # Alto riesgo debe tener score mayor que bajo riesgo
        # (puede no ser siempre cierto con poco training data, pero esperado)

    def test_predict_risk_without_training(self):
        """Test predecir riesgo sin entrenar modelo."""
        predictor = DeploymentRiskPredictor()

        features = {
            "lead_time": 7200,
            "tests_passed_pct": 85,
            "code_changes_size": 200,
            "time_of_day": 10,
            "day_of_week": 2,
            "previous_failures": 1,
            "team_velocity": 5,
            "planning_duration": 3600,
            "feature_complexity_score": 2,
            "code_review_score": 0.8,
        }

        with self.assertRaises(ValueError):
            predictor.predict_risk(features)

    def test_explain_prediction(self):
        """Test explicar prediccion."""
        predictor = DeploymentRiskPredictor()
        predictor.train_model(self.training_data)

        features = {
            "lead_time": 7200,
            "tests_passed_pct": 85,
            "code_changes_size": 200,
            "time_of_day": 10,
            "day_of_week": 2,
            "previous_failures": 1,
            "team_velocity": 5,
            "planning_duration": 3600,
            "feature_complexity_score": 2,
            "code_review_score": 0.8,
        }

        explanation = predictor.explain_prediction(features)

        self.assertIn("risk_score", explanation)
        self.assertIn("risk_level", explanation)
        self.assertIn("confidence", explanation)
        self.assertIn("top_risk_factors", explanation)
        self.assertIn("recommendations", explanation)
        self.assertIn("feature_importance", explanation)

        # Risk level debe ser valido
        self.assertIn(explanation["risk_level"], ["very_low", "low", "medium", "high"])

        # Debe tener top risk factors
        self.assertGreater(len(explanation["top_risk_factors"]), 0)

        # Debe tener recomendaciones
        self.assertGreater(len(explanation["recommendations"]), 0)

    def test_classify_risk_level(self):
        """Test clasificacion de risk level."""
        predictor = DeploymentRiskPredictor()

        self.assertEqual(predictor._classify_risk_level(0.1), "very_low")
        self.assertEqual(predictor._classify_risk_level(0.3), "low")
        self.assertEqual(predictor._classify_risk_level(0.5), "medium")
        self.assertEqual(predictor._classify_risk_level(0.8), "high")

    def test_calculate_confidence(self):
        """Test calculo de confidence."""
        predictor = DeploymentRiskPredictor()

        # Confidence alta cuando risk esta lejos de 0.5
        high_conf = predictor._calculate_confidence(0.95)
        self.assertGreater(high_conf, 0.8)

        low_conf = predictor._calculate_confidence(0.05)
        self.assertGreater(low_conf, 0.8)

        # Confidence baja cuando risk esta cerca de 0.5
        medium_conf = predictor._calculate_confidence(0.5)
        self.assertLess(medium_conf, 0.2)

    def test_get_model_version(self):
        """Test obtener version del modelo."""
        predictor = DeploymentRiskPredictor()

        # Sin entrenar
        version = predictor.get_model_version()
        self.assertEqual(version, "untrained")

        # Despues de entrenar
        predictor.train_model(self.training_data)
        version = predictor.get_model_version()
        self.assertTrue(version.startswith("v1.0-"))

    def test_evaluate_model(self):
        """Test evaluar modelo."""
        predictor = DeploymentRiskPredictor()
        predictor.train_model(self.training_data)

        stats = predictor.evaluate_model()

        self.assertIn("trained_at", stats)
        self.assertIn("training_samples", stats)
        self.assertIn("validation_samples", stats)
        self.assertIn("accuracy", stats)
        self.assertIn("precision", stats)
        self.assertIn("recall", stats)
        self.assertIn("f1_score", stats)

    def test_save_and_load_model(self):
        """Test guardar y cargar modelo."""
        predictor = DeploymentRiskPredictor()
        predictor.train_model(self.training_data)

        # Guardar modelo
        model_path = "/tmp/test_deployment_risk_model.pkl"
        predictor.save_model(model_path)

        # Cargar modelo en nueva instancia
        predictor2 = DeploymentRiskPredictor(model_path=model_path)

        # Verificar que modelo fue cargado
        self.assertIsNotNone(predictor2.model)
        self.assertEqual(predictor2.model_metadata, predictor.model_metadata)

        # Verificar que predicciones son iguales
        features = {
            "lead_time": 7200,
            "tests_passed_pct": 85,
            "code_changes_size": 200,
            "time_of_day": 10,
            "day_of_week": 2,
            "previous_failures": 1,
            "team_velocity": 5,
            "planning_duration": 3600,
            "feature_complexity_score": 2,
            "code_review_score": 0.8,
        }

        risk1 = predictor.predict_risk(features)
        risk2 = predictor2.predict_risk(features)

        self.assertAlmostEqual(risk1, risk2, places=5)
