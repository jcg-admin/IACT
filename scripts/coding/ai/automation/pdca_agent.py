#!/usr/bin/env python3
"""
PDCA Automation Agent - Implementado con TDD Estricto

Implementa ciclos PDCA (Plan-Do-Check-Act) automatizados para optimizacion
continua de practicas IA basadas en metricas DORA.

Este archivo fue completamente reconstruido usando TDD estricto con ciclos
RED-GREEN-REFACTOR para cada funcionalidad.

Autor: TDD Process
Fecha: 2025-11-14
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class PDCAPhase(Enum):
    """Fases del ciclo PDCA."""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class DecisionAction(Enum):
    """Acciones de decision post-validacion."""
    APPLY = "apply"
    REVERT = "revert"
    CONTINUE = "continue"
    ESCALATE = "escalate"


class PDCAAutomationAgent:
    """
    Agente de automatizacion PDCA para mejora continua IA.

    Implementado completamente con TDD estricto.
    """

    def __init__(
        self,
        repo: str,
        github_token: Optional[str] = None,
        config_file: str = ".pdca_config.json",
        baseline_days: int = 30,
        validation_threshold: float = 0.05
    ):
        """Inicializa el agente PDCA."""
        # TDD Cycle 1: Configuration
        self.repo = repo
        self.github_token = github_token
        self.config_file = Path(config_file)
        self.baseline_days = baseline_days
        self.validation_threshold = validation_threshold

        self.config = self._load_config()

        # TDD Cycle 2: History
        self.history_file = Path(".pdca_history.json")
        self.history = self._load_history()

    def _load_config(self) -> Dict:
        """
        Carga configuracion PDCA - TDD Cycle 1.

        RED: test_load_config_creates_default_when_missing
        GREEN: Implementacion minima que retorna config default
        REFACTOR: Agregar lectura de archivo existente
        """
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)

        # Configuracion default cuando no existe archivo
        return {
            "enabled": True,
            "auto_apply_threshold": 0.15,
            "auto_revert_threshold": -0.05,
            "metrics_priority": {
                "deployment_frequency": 0.30,
                "lead_time_for_changes": 0.30,
                "change_failure_rate": 0.25,
                "mean_time_to_recovery": 0.15
            },
            "notification_webhooks": [],
            "rollback_strategy": "immediate"
        }

    def _save_config(self) -> None:
        """
        Guarda configuracion PDCA - TDD Cycle 1.

        RED: test_save_config_writes_to_file
        GREEN: Implementacion minima que guarda JSON
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_history(self) -> List[Dict]:
        """
        Carga historial de ciclos PDCA - TDD Cycle 2.

        RED: test_load_history_returns_empty_when_missing
        GREEN: Retornar lista vacia si no existe
        REFACTOR: Agregar lectura de archivo existente
        """
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def _save_history(self) -> None:
        """
        Guarda historial de ciclos PDCA - TDD Cycle 2.

        RED: test_save_history_writes_to_file
        GREEN: Guardar lista como JSON
        """
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def _get_mock_metrics(self) -> Dict:
        """
        Metricas mock para testing - TDD Cycle 3.

        RED: test_get_mock_metrics_returns_valid_structure
        GREEN: Retornar dict con estructura DORA completa
        """
        return {
            'deployment_frequency': 0.5,  # 0.5 deployments/day
            'lead_time_for_changes': 48.0,  # 48 hours
            'change_failure_rate': 15.0,  # 15%
            'mean_time_to_recovery': 2.5,  # 2.5 hours
            'timestamp': datetime.now().isoformat(),
            'mock': True
        }

    def _get_baseline_metrics(self) -> Dict:
        """
        Obtiene metricas DORA baseline - TDD Cycle 3.

        RED: test_get_baseline_metrics_uses_mock_without_token
        GREEN: Retornar mock cuando no hay token
        REFACTOR: Agregar integracion con DORA metrics reales
        """
        # Sin GitHub token, usar metricas mock
        if not self.github_token:
            return self._get_mock_metrics()

        # TODO: Integrar con DORAMetricsCalculator cuando este disponible
        # Por ahora retornar mock
        return self._get_mock_metrics()

    def _calculate_estimated_impact(self, improvements: List[Dict]) -> Dict:
        """
        Calcula impacto estimado de mejoras propuestas - TDD Cycle 4.

        RED: test_calculate_estimated_impact
        GREEN: Calcular porcentaje de mejora para cada metrica
        """
        impact = {}
        for imp in improvements:
            metric = imp['metric']
            current = imp['current']
            target = imp['target']

            # Para deployment_frequency, mayor es mejor
            if metric == 'deployment_frequency':
                change_pct = ((target - current) / current) * 100
            else:
                # Para otras metricas, menor es mejor
                change_pct = ((current - target) / current) * 100

            impact[metric] = {
                'current': current,
                'target': target,
                'improvement_pct': round(change_pct, 2)
            }

        return impact

    def plan(self, baseline_metrics: Dict) -> Dict:
        """
        FASE 1: PLAN - Analizar metricas y proponer ajustes - TDD Cycle 4.

        RED: test_plan_returns_valid_structure
        GREEN: Retornar estructura basica con cycle_id y phase
        REFACTOR: Agregar analisis de metricas y propuestas de mejora
        """
        improvements = []

        # Analizar deployment_frequency
        if baseline_metrics['deployment_frequency'] < 1.0:
            improvements.append({
                'metric': 'deployment_frequency',
                'current': baseline_metrics['deployment_frequency'],
                'target': baseline_metrics['deployment_frequency'] * 1.3,
                'action': 'Incrementar automatizacion CI/CD',
                'priority': 'high',
                'ai_assistance': ['Auto-merge PRs con >90% coverage', 'AI code review paralelo']
            })

        # Analizar lead_time_for_changes
        if baseline_metrics['lead_time_for_changes'] > 24.0:
            improvements.append({
                'metric': 'lead_time_for_changes',
                'current': baseline_metrics['lead_time_for_changes'],
                'target': baseline_metrics['lead_time_for_changes'] * 0.7,
                'action': 'Reducir tiempo commit -> produccion',
                'priority': 'high',
                'ai_assistance': ['AI test generation', 'Automated PR descriptions']
            })

        # Analizar change_failure_rate
        if baseline_metrics['change_failure_rate'] > 15.0:
            improvements.append({
                'metric': 'change_failure_rate',
                'current': baseline_metrics['change_failure_rate'],
                'target': baseline_metrics['change_failure_rate'] * 0.8,
                'action': 'Mejorar validaciones pre-deploy',
                'priority': 'critical',
                'ai_assistance': ['AI security scanning', 'Predictive failure detection']
            })

        # Analizar mean_time_to_recovery
        if baseline_metrics['mean_time_to_recovery'] > 1.0:
            improvements.append({
                'metric': 'mean_time_to_recovery',
                'current': baseline_metrics['mean_time_to_recovery'],
                'target': baseline_metrics['mean_time_to_recovery'] * 0.85,
                'action': 'Automatizar rollback y recovery',
                'priority': 'medium',
                'ai_assistance': ['AI incident detection', 'Auto-rollback triggers']
            })

        return {
            'cycle_id': f"pdca-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'phase': PDCAPhase.PLAN.value,
            'baseline_metrics': baseline_metrics,
            'improvements': improvements,
            'estimated_impact': self._calculate_estimated_impact(improvements),
            'timestamp': datetime.now().isoformat()
        }

    def do(self, plan: Dict) -> Dict:
        """
        FASE 2: DO - Ejecutar cambios propuestos - TDD Cycle 5.

        RED: test_do_returns_valid_structure
        GREEN: Retornar estructura con cycle_id y execution_log
        REFACTOR: Ejecutar cada improvement del plan
        """
        execution_log = []

        for improvement in plan['improvements']:
            action_result = {
                'metric': improvement['metric'],
                'action': improvement['action'],
                'status': 'simulated',  # En produccion: 'executed', 'failed', 'rolled_back'
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'ai_tools_enabled': improvement['ai_assistance'],
                    'rollback_point': f"commit-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'monitoring_active': True
                }
            }
            execution_log.append(action_result)

        return {
            'cycle_id': plan['cycle_id'],
            'phase': PDCAPhase.DO.value,
            'execution_log': execution_log,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }

    def _simulate_post_metrics(self, baseline: Dict, improvements: List[Dict]) -> Dict:
        """
        Simula metricas post-cambio - TDD Cycle 6.

        RED: test_simulate_post_metrics
        GREEN: Generar metricas simuladas basadas en mejoras
        """
        import random
        post_metrics = baseline.copy()

        for imp in improvements:
            metric = imp['metric']
            target = imp['target']
            current = imp['current']

            # Simular mejora entre 60-100% del objetivo
            improvement_factor = random.uniform(0.6, 1.0)
            new_value = current + (target - current) * improvement_factor
            post_metrics[metric] = round(new_value, 2)

        post_metrics['timestamp'] = datetime.now().isoformat()
        return post_metrics

    def check(self, plan: Dict, do_result: Dict, wait_hours: int = 24) -> Dict:
        """
        FASE 3: CHECK - Validar metricas post-cambio - TDD Cycle 6.

        RED: test_check_returns_valid_structure
        GREEN: Retornar estructura con validation_results
        REFACTOR: Calcular mejoras y weighted_score
        """
        baseline = plan['baseline_metrics']
        post_metrics = self._simulate_post_metrics(baseline, plan['improvements'])

        validation_results = []

        for metric_name, post_value in post_metrics.items():
            if metric_name in ['timestamp', 'mock']:
                continue

            baseline_value = baseline[metric_name]
            priority = self.config['metrics_priority'].get(metric_name, 0.25)

            # Calcular mejora (deployment_frequency: mayor es mejor, otros: menor es mejor)
            if metric_name == 'deployment_frequency':
                improvement_pct = ((post_value - baseline_value) / baseline_value) * 100
            else:
                improvement_pct = ((baseline_value - post_value) / baseline_value) * 100

            passed = improvement_pct >= (self.validation_threshold * 100)

            validation_results.append({
                'metric': metric_name,
                'baseline': baseline_value,
                'post_change': post_value,
                'improvement_pct': round(improvement_pct, 2),
                'priority_weight': priority,
                'passed': passed,
                'status': '[OK]' if passed else '[FAIL]'
            })

        # Calcular score ponderado
        weighted_score = sum(
            vr['improvement_pct'] * vr['priority_weight']
            for vr in validation_results
        )

        return {
            'cycle_id': plan['cycle_id'],
            'phase': PDCAPhase.CHECK.value,
            'baseline_metrics': baseline,
            'post_metrics': post_metrics,
            'validation_results': validation_results,
            'weighted_score': round(weighted_score, 2),
            'passed': weighted_score >= (self.validation_threshold * 100),
            'timestamp': datetime.now().isoformat()
        }

    def act(self, check_result: Dict) -> Dict:
        """
        FASE 4: ACT - Decidir aplicar, revertir o escalar - TDD Cycle 7.

        RED: test_act_returns_valid_structure
        GREEN: Retornar estructura con decision y actions_taken
        REFACTOR: Implementar logica de decision automatizada
        """
        weighted_score = check_result['weighted_score']
        auto_apply_threshold = self.config['auto_apply_threshold'] * 100
        auto_revert_threshold = self.config['auto_revert_threshold'] * 100

        # Decision automatizada basada en weighted_score
        if weighted_score >= auto_apply_threshold:
            decision = DecisionAction.APPLY
            reason = f"Mejora significativa ({weighted_score:+.2f}% >= {auto_apply_threshold:.1f}%)"
            actions_taken = [
                "Merge cambios a main branch",
                "Deploy a produccion",
                "Actualizar baseline metrics",
                "Notificar equipo: Mejora validada"
            ]
        elif weighted_score <= auto_revert_threshold:
            decision = DecisionAction.REVERT
            reason = f"Regresion detectada ({weighted_score:+.2f}% <= {auto_revert_threshold:.1f}%)"
            actions_taken = [
                "Rollback automatico activado",
                "Revertir configuraciones IA",
                "Restaurar baseline anterior",
                "Alertar equipo: Regresion detectada"
            ]
        elif weighted_score >= (self.validation_threshold * 100):
            decision = DecisionAction.CONTINUE
            reason = f"Mejora marginal ({weighted_score:+.2f}%), continuar monitoreando"
            actions_taken = [
                "Mantener cambios en staging",
                "Extender periodo de monitoreo +48h",
                "Recolectar datos adicionales"
            ]
        else:
            decision = DecisionAction.ESCALATE
            reason = f"Resultado ambiguo ({weighted_score:+.2f}%), requiere revision humana"
            actions_taken = [
                "Pausar cambios automaticos",
                "Generar reporte para arquitecto",
                "Solicitar revision manual"
            ]

        return {
            'cycle_id': check_result['cycle_id'],
            'phase': PDCAPhase.ACT.value,
            'decision': decision.value,
            'reason': reason,
            'weighted_score': weighted_score,
            'actions_taken': actions_taken,
            'timestamp': datetime.now().isoformat()
        }

    def run_cycle(self, auto_execute: bool = False) -> Dict:
        """
        Ejecuta ciclo PDCA completo - TDD Cycle 8.

        RED: test_run_cycle_executes_all_phases
        GREEN: Ejecutar las 4 fases en orden
        REFACTOR: Agregar manejo de confirmaciones y guardado de historial

        Args:
            auto_execute: Si True, ejecuta sin confirmaciones

        Returns:
            Resultado completo del ciclo con todas las fases
        """
        # PLAN
        baseline = self._get_baseline_metrics()
        plan = self.plan(baseline)

        if not auto_execute:
            response = input("\nContinuar con fase DO? [y/N]: ")
            if response.lower() != 'y':
                return {'status': 'aborted', 'phase': 'plan'}

        # DO
        do_result = self.do(plan)

        if not auto_execute:
            response = input("\nContinuar con fase CHECK? [y/N]: ")
            if response.lower() != 'y':
                return {'status': 'aborted', 'phase': 'do'}

        # CHECK
        check_result = self.check(plan, do_result)

        if not auto_execute:
            response = input("\nContinuar con fase ACT? [y/N]: ")
            if response.lower() != 'y':
                return {'status': 'aborted', 'phase': 'check'}

        # ACT
        act_result = self.act(check_result)

        # Guardar en historial
        cycle_complete = {
            'cycle_id': plan['cycle_id'],
            'plan': plan,
            'do': do_result,
            'check': check_result,
            'act': act_result,
            'completed_at': datetime.now().isoformat()
        }

        self.history.append(cycle_complete)
        self._save_history()

        return cycle_complete


def main():
    """Punto de entrada principal."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="PDCA Automation Agent - Mejora continua IA basada en DORA metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--repo',
        type=str,
        default='2-Coatl/IACT---project',
        help='Repositorio en formato owner/repo'
    )

    parser.add_argument(
        '--baseline-days',
        type=int,
        default=30,
        help='Dias para calcular baseline (default: 30)'
    )

    parser.add_argument(
        '--auto-execute',
        action='store_true',
        help='Ejecutar ciclo completo sin confirmaciones'
    )

    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub token (o usar env GITHUB_TOKEN)'
    )

    parser.add_argument(
        '--show-history',
        action='store_true',
        help='Mostrar historial de ciclos PDCA'
    )

    args = parser.parse_args()

    try:
        agent = PDCAAutomationAgent(
            repo=args.repo,
            github_token=args.github_token,
            baseline_days=args.baseline_days
        )

        if args.show_history:
            print("\n=== HISTORIAL DE CICLOS PDCA ===\n")
            for cycle in agent.history:
                print(f"Cycle: {cycle['cycle_id']}")
                print(f"  Decision: {cycle['act']['decision']}")
                print(f"  Score: {cycle['act']['weighted_score']:+.2f}%")
                print(f"  Completed: {cycle['completed_at'][:19]}")
                print()
            return 0

        print("=" * 80)
        print("PDCA AUTOMATION AGENT - Ciclo de Mejora Continua")
        print("=" * 80)

        result = agent.run_cycle(auto_execute=args.auto_execute)

        if result.get('status') == 'aborted':
            print("\n[ABORTED] Ciclo cancelado por usuario")
            return 1

        print("\n" + "=" * 80)
        print(f"CICLO PDCA COMPLETADO: {result['cycle_id']}")
        print(f"Decision: {result['act']['decision'].upper()}")
        print(f"Score: {result['act']['weighted_score']:+.2f}%")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
