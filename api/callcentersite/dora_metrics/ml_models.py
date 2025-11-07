"""ML Models para Predictive Analytics - TASK-033."""

from __future__ import annotations

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split

from .ml_features import FeatureExtractor


class DeploymentRiskPredictor:
    """Predictor de riesgo de fallos en deployments usando Random Forest."""

    def __init__(self, model_path: str | None = None):
        """
        Inicializar predictor.

        Args:
            model_path: Path al modelo pre-entrenado (opcional)
        """
        self.model: RandomForestClassifier | None = None
        self.feature_names = FeatureExtractor.get_feature_names()
        self.model_path = model_path or "/tmp/deployment_risk_model.pkl"
        self.model_metadata: dict[str, Any] = {}

        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def train_model(self, training_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Entrenar modelo con training data.

        Args:
            training_data: Lista de features + target

        Returns:
            Dict con metricas de training
        """
        if len(training_data) < 10:
            raise ValueError("Insuficientes datos para training (minimo 10 samples)")

        # Preparar X (features) y y (target)
        X = []
        y = []

        for sample in training_data:
            normalized = FeatureExtractor.normalize_features(sample)
            features_array = FeatureExtractor.features_to_array(normalized)
            X.append(features_array)
            y.append(sample["deployment_failed"])

        X = np.array(X)
        y = np.array(y)

        # Split train/validation (80/20)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

        # Entrenar Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced",  # Manejar clases desbalanceadas
        )

        self.model.fit(X_train, y_train)

        # Evaluar en validation set
        y_pred = self.model.predict(X_val)
        y_pred_proba = self.model.predict_proba(X_val)

        accuracy = accuracy_score(y_val, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_val, y_pred, average="binary", zero_division=0
        )

        # Guardar metadata del modelo
        self.model_metadata = {
            "trained_at": datetime.now().isoformat(),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "feature_names": self.feature_names,
        }

        # Guardar modelo
        self.save_model(self.model_path)

        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "feature_importance": self._get_feature_importance(),
        }

    def predict_risk(self, features: dict[str, Any]) -> float:
        """
        Predecir riesgo de fallo para un deployment.

        Args:
            features: Features del deployment

        Returns:
            Risk score 0.0-1.0 (probabilidad de fallo)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Ejecutar train_model() primero.")

        # Normalizar features
        normalized = FeatureExtractor.normalize_features(features)
        features_array = FeatureExtractor.features_to_array(normalized)

        # Reshape para sklearn
        X = np.array([features_array])

        # Predecir probabilidad de fallo (clase 1)
        risk_proba = self.model.predict_proba(X)[0][1]

        return float(risk_proba)

    def explain_prediction(self, features: dict[str, Any]) -> dict[str, Any]:
        """
        Explicar prediccion con feature importance y decision path.

        Args:
            features: Features del deployment

        Returns:
            Dict con explicacion de la prediccion
        """
        risk_score = self.predict_risk(features)

        # Feature importance del modelo
        global_importance = self._get_feature_importance()

        # Feature values normalizados
        normalized = FeatureExtractor.normalize_features(features)

        # Contribution de cada feature (feature_value * importance)
        feature_contributions = {}
        for feature_name in self.feature_names:
            contribution = normalized[feature_name] * global_importance[feature_name]
            feature_contributions[feature_name] = contribution

        # Ordenar por contribution absoluta
        sorted_contributions = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        # Top 5 features mas importantes
        top_features = sorted_contributions[:5]

        # Determinar recomendaciones basadas en top features
        recommendations = self._generate_recommendations(features, top_features, risk_score)

        return {
            "risk_score": risk_score,
            "risk_level": self._classify_risk_level(risk_score),
            "confidence": self._calculate_confidence(risk_score),
            "top_risk_factors": [
                {
                    "feature": feature,
                    "contribution": float(contribution),
                    "value": normalized[feature],
                }
                for feature, contribution in top_features
            ],
            "recommendations": recommendations,
            "feature_importance": global_importance,
        }

    def evaluate_model(self) -> dict[str, Any]:
        """
        Evaluar modelo con metricas completas.

        Returns:
            Dict con metricas de evaluacion
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado.")

        return self.model_metadata

    def _get_feature_importance(self) -> dict[str, float]:
        """Obtener feature importance del modelo."""
        if self.model is None:
            return {}

        importances = self.model.feature_importances_
        return {
            name: float(importance)
            for name, importance in zip(self.feature_names, importances)
        }

    def _classify_risk_level(self, risk_score: float) -> str:
        """Clasificar risk score en nivel."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score >= 0.2:
            return "low"
        else:
            return "very_low"

    def _calculate_confidence(self, risk_score: float) -> float:
        """
        Calcular confidence de la prediccion.

        Confidence es alta cuando risk_score esta lejos de 0.5 (decision boundary).
        """
        distance_from_boundary = abs(risk_score - 0.5)
        confidence = distance_from_boundary * 2  # Normalizar a 0-1
        return float(confidence)

    def _generate_recommendations(
        self,
        features: dict[str, Any],
        top_features: list[tuple[str, float]],
        risk_score: float,
    ) -> list[str]:
        """Generar recomendaciones basadas en features."""
        recommendations = []

        for feature_name, contribution in top_features:
            if feature_name == "tests_passed_pct" and features["tests_passed_pct"] < 80:
                recommendations.append("Aumentar cobertura de tests (actualmente bajo 80%)")
            elif feature_name == "code_changes_size" and features["code_changes_size"] > 500:
                recommendations.append("Considerar dividir deployment en cambios mas pequenos")
            elif feature_name == "previous_failures" and features["previous_failures"] > 3:
                recommendations.append("Revisar patrones de fallos recientes antes de deployment")
            elif feature_name == "time_of_day" and (features["time_of_day"] < 8 or features["time_of_day"] > 18):
                recommendations.append("Considerar deployment en horario laboral para mejor soporte")
            elif feature_name == "day_of_week" and features["day_of_week"] >= 4:
                recommendations.append("Evitar deployments viernes/fin de semana si es posible")
            elif feature_name == "lead_time" and features["lead_time"] < 3600:
                recommendations.append("Lead time muy corto, considerar mas tiempo de testing")
            elif feature_name == "code_review_score" and features["code_review_score"] < 0.7:
                recommendations.append("Mejorar calidad de code review antes de deployment")

        if risk_score >= 0.7:
            recommendations.append("ALTO RIESGO: Considerar posponer deployment o aumentar preparacion")
        elif risk_score >= 0.4:
            recommendations.append("RIESGO MEDIO: Preparar plan de rollback y monitoreo intensivo")
        else:
            recommendations.append("BAJO RIESGO: Proceder con deployment, monitoreo standard")

        return recommendations[:5]  # Maximo 5 recomendaciones

    def save_model(self, path: str) -> None:
        """Guardar modelo a disco."""
        if self.model is None:
            raise ValueError("No hay modelo para guardar.")

        model_data = {
            "model": self.model,
            "metadata": self.model_metadata,
            "feature_names": self.feature_names,
        }

        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    def load_model(self, path: str) -> None:
        """Cargar modelo desde disco."""
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        self.model = model_data["model"]
        self.model_metadata = model_data["metadata"]
        self.feature_names = model_data["feature_names"]

    def get_model_version(self) -> str:
        """Obtener version del modelo."""
        if not self.model_metadata:
            return "untrained"

        trained_at = self.model_metadata.get("trained_at", "unknown")
        return f"v1.0-{trained_at[:10]}"  # v1.0-YYYY-MM-DD
