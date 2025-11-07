#!/usr/bin/env python
"""
Script para re-entrenar modelo de prediccion de riesgo de deployments.

Uso:
    python retrain_deployment_risk_model.py [--days DAYS] [--dry-run]

Opciones:
    --days DAYS     Numero de dias de datos historicos (default: 90)
    --dry-run       Ejecutar sin guardar modelo

Este script debe ejecutarse mensualmente via cron job.
"""

import argparse
import sys
from pathlib import Path

# Add Django app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api" / "callcentersite"))

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "callcentersite.settings")
django.setup()

from dora_metrics.ml_features import FeatureExtractor
from dora_metrics.ml_models import DeploymentRiskPredictor


def main():
    """Main function para re-entrenar modelo."""
    parser = argparse.ArgumentParser(
        description="Re-entrenar modelo de prediccion de riesgo de deployments"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Numero de dias de datos historicos (default: 90)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar sin guardar modelo",
    )

    args = parser.parse_args()

    print(f"Iniciando re-training con {args.days} dias de datos...")

    # Crear training dataset
    print(f"Extrayendo features de ultimos {args.days} dias...")
    training_data = FeatureExtractor.create_training_dataset(days=args.days)

    print(f"Dataset creado: {len(training_data)} samples")

    if len(training_data) < 10:
        print(f"ERROR: Insuficientes datos para training (encontrado {len(training_data)}, necesita >= 10)")
        sys.exit(1)

    # Contar clase balance
    failures = sum(1 for sample in training_data if sample["deployment_failed"] == 1)
    successes = len(training_data) - failures

    print(f"Balance de clases:")
    print(f"  - Deployments exitosos: {successes} ({successes/len(training_data)*100:.1f}%)")
    print(f"  - Deployments fallidos: {failures} ({failures/len(training_data)*100:.1f}%)")

    if failures < 5:
        print(f"WARNING: Pocos ejemplos de failures ({failures}). Modelo puede tener baja precision.")

    # Entrenar modelo
    print("\nEntrenando Random Forest Classifier...")
    predictor = DeploymentRiskPredictor()

    try:
        metrics = predictor.train_model(training_data)

        print("\n=== Training Metrics ===")
        print(f"Accuracy:  {metrics['accuracy']:.3f}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall:    {metrics['recall']:.3f}")
        print(f"F1 Score:  {metrics['f1_score']:.3f}")
        print(f"\nTraining samples:   {metrics['training_samples']}")
        print(f"Validation samples: {metrics['validation_samples']}")

        print("\n=== Top 5 Feature Importance ===")
        sorted_features = sorted(
            metrics['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for feature, importance in sorted_features[:5]:
            print(f"{feature:25s} {importance:.4f}")

        if args.dry_run:
            print("\n[DRY RUN] Modelo NO guardado.")
        else:
            model_path = predictor.model_path
            print(f"\nModelo guardado en: {model_path}")
            print(f"Model version: {predictor.get_model_version()}")

        # Validation checks
        print("\n=== Validation Checks ===")
        if metrics['accuracy'] < 0.7:
            print("WARNING: Accuracy menor a 0.7. Considerar mas datos o feature engineering.")
        else:
            print(f"✓ Accuracy OK ({metrics['accuracy']:.3f} >= 0.70)")

        if metrics['f1_score'] < 0.6:
            print("WARNING: F1 Score menor a 0.6. Balance de precision/recall suboptimo.")
        else:
            print(f"✓ F1 Score OK ({metrics['f1_score']:.3f} >= 0.60)")

        if metrics['training_samples'] < 50:
            print("WARNING: Pocos training samples. Considerar aumentar periodo de datos.")
        else:
            print(f"✓ Training samples OK ({metrics['training_samples']} >= 50)")

        print("\n=== Training Completed Successfully ===")
        return 0

    except Exception as e:
        print(f"\nERROR durante training: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
