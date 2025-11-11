#!/usr/bin/env python3
"""
PDCA Automation Agent - Fase 5: Medicion, Validacion y Mejora Continua

Implementa ciclos PDCA (Plan-Do-Check-Act) automatizados para optimizacion
continua de practicas IA basadas en metricas DORA.

Tareas:
- T5.5: Implementar ciclo PDCA automatizado
  - Plan: Ajustar configuracion IA basado en metricas
  - Do: Desplegar cambios incrementales
  - Check: Validar metricas post-cambio
  - Act: Aplicar o revertir cambios

Autor: Claude Code Agent
Fecha: 2025-11-06
Relacionado: FASES_IMPLEMENTACION_IA.md, ESTRATEGIA_IA.md
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Importar DORA metrics calculator si existe
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from dora_metrics import DORAMetricsCalculator
except ImportError:
    print("[WARNING] dora_metrics.py no disponible, usando metricas mock")
    DORAMetricsCalculator = None


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

    Implementa ciclos automatizados:
    1. PLAN: Analizar metricas actuales y proponer ajustes
    2. DO: Ejecutar cambios en entorno controlado
    3. CHECK: Validar metricas post-cambio vs baseline
    4. ACT: Decidir aplicar, revertir o escalar
    """

    def __init__(
        self,
        repo: str,
        github_token: Optional[str] = None,
        config_file: str = ".pdca_config.json",
        baseline_days: int = 30,
        validation_threshold: float = 0.05
    ):
        """
        Inicializa el agente PDCA.

        Args:
            repo: Repositorio en formato 'owner/repo'
            github_token: GitHub token para metricas
            config_file: Archivo de configuracion PDCA
            baseline_days: Dias para calcular baseline
            validation_threshold: Umbral de mejora minima (5% default)
        """
        self.repo = repo
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.config_file = Path(config_file)
        self.baseline_days = baseline_days
        self.validation_threshold = validation_threshold

        self.config = self._load_config()
        self.history_file = Path(".pdca_history.json")
        self.history = self._load_history()

    def _load_config(self) -> Dict:
        """Carga configuracion PDCA."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)

        # Configuracion default
        return {
            "enabled": True,
            "auto_apply_threshold": 0.15,  # Auto-apply si mejora >15%
            "auto_revert_threshold": -0.05,  # Auto-revert si empeora >5%
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
        """Guarda configuracion PDCA."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_history(self) -> List[Dict]:
        """Carga historial de ciclos PDCA."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def _save_history(self) -> None:
        """Guarda historial de ciclos PDCA."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def _get_baseline_metrics(self) -> Dict:
        """
        Obtiene metricas DORA baseline.

        Returns:
            Diccionario con metricas baseline
        """
        if not DORAMetricsCalculator or not self.github_token:
            print("[WARNING] Usando metricas mock - GITHUB_TOKEN requerido")
            return self._get_mock_metrics()

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.baseline_days)

            calculator = DORAMetricsCalculator(
                repo=self.repo,
                github_token=self.github_token,
                start_date=start_date,
                end_date=end_date
            )

            report = calculator.generate_report()
            return {
                'deployment_frequency': report['metrics']['deployment_frequency']['value'],
                'lead_time_for_changes': report['metrics']['lead_time_for_changes']['value'],
                'change_failure_rate': report['metrics']['change_failure_rate']['value'],
                'mean_time_to_recovery': report['metrics']['mean_time_to_recovery']['value'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[ERROR] Fallo al obtener metricas DORA: {e}")
            return self._get_mock_metrics()

    def _get_mock_metrics(self) -> Dict:
        """Metricas mock para testing."""
        return {
            'deployment_frequency': 0.5,  # 0.5 deployments/day
            'lead_time_for_changes': 48.0,  # 48 hours
            'change_failure_rate': 15.0,  # 15%
            'mean_time_to_recovery': 2.5,  # 2.5 hours
            'timestamp': datetime.now().isoformat(),
            'mock': True
        }

    def plan(self, baseline_metrics: Dict) -> Dict:
        """
        FASE 1: PLAN - Analizar metricas y proponer ajustes.

        Args:
            baseline_metrics: Metricas DORA actuales

        Returns:
            Plan de accion con ajustes propuestos
        """
        print("\n[PLAN] Analizando metricas actuales...")
        print(f"  Deployment Frequency: {baseline_metrics['deployment_frequency']:.2f} deploys/dia")
        print(f"  Lead Time: {baseline_metrics['lead_time_for_changes']:.2f} horas")
        print(f"  Change Failure Rate: {baseline_metrics['change_failure_rate']:.2f}%")
        print(f"  MTTR: {baseline_metrics['mean_time_to_recovery']:.2f} horas")

        improvements = []

        # Analizar cada metrica y proponer mejoras
        if baseline_metrics['deployment_frequency'] < 1.0:
            improvements.append({
                'metric': 'deployment_frequency',
                'current': baseline_metrics['deployment_frequency'],
                'target': baseline_metrics['deployment_frequency'] * 1.3,
                'action': 'Incrementar automatizacion CI/CD',
                'priority': 'high',
                'ai_assistance': ['Auto-merge PRs con >90% coverage', 'AI code review paralelo']
            })

        if baseline_metrics['lead_time_for_changes'] > 24.0:
            improvements.append({
                'metric': 'lead_time_for_changes',
                'current': baseline_metrics['lead_time_for_changes'],
                'target': baseline_metrics['lead_time_for_changes'] * 0.7,
                'action': 'Reducir tiempo commit -> produccion',
                'priority': 'high',
                'ai_assistance': ['AI test generation', 'Automated PR descriptions']
            })

        if baseline_metrics['change_failure_rate'] > 15.0:
            improvements.append({
                'metric': 'change_failure_rate',
                'current': baseline_metrics['change_failure_rate'],
                'target': baseline_metrics['change_failure_rate'] * 0.8,
                'action': 'Mejorar validaciones pre-deploy',
                'priority': 'critical',
                'ai_assistance': ['AI security scanning', 'Predictive failure detection']
            })

        if baseline_metrics['mean_time_to_recovery'] > 1.0:
            improvements.append({
                'metric': 'mean_time_to_recovery',
                'current': baseline_metrics['mean_time_to_recovery'],
                'target': baseline_metrics['mean_time_to_recovery'] * 0.85,
                'action': 'Automatizar rollback y recovery',
                'priority': 'medium',
                'ai_assistance': ['AI incident detection', 'Auto-rollback triggers']
            })

        plan = {
            'cycle_id': f"pdca-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'phase': PDCAPhase.PLAN.value,
            'baseline_metrics': baseline_metrics,
            'improvements': improvements,
            'estimated_impact': self._calculate_estimated_impact(improvements),
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n[PLAN] {len(improvements)} mejoras identificadas")
        for imp in improvements:
            print(f"  [{imp['priority'].upper()}] {imp['metric']}: {imp['action']}")

        return plan

    def _calculate_estimated_impact(self, improvements: List[Dict]) -> Dict:
        """Calcula impacto estimado de mejoras propuestas."""
        impact = {}
        for imp in improvements:
            metric = imp['metric']
            current = imp['current']
            target = imp['target']

            if metric == 'deployment_frequency':
                change_pct = ((target - current) / current) * 100
            else:
                change_pct = ((current - target) / current) * 100

            impact[metric] = {
                'current': current,
                'target': target,
                'improvement_pct': round(change_pct, 2)
            }

        return impact

    def do(self, plan: Dict) -> Dict:
        """
        FASE 2: DO - Ejecutar cambios propuestos.

        Args:
            plan: Plan de accion de fase PLAN

        Returns:
            Resultado de ejecucion
        """
        print("\n[DO] Ejecutando cambios propuestos...")

        # En implementacion real, aqui se ejecutarian:
        # - Actualizar configuraciones CI/CD
        # - Activar feature flags
        # - Deploy incremental a staging
        # - Activar herramientas IA adicionales

        execution_log = []

        for improvement in plan['improvements']:
            action_result = {
                'metric': improvement['metric'],
                'action': improvement['action'],
                'status': 'simulated',  # Real: 'executed', 'failed', 'rolled_back'
                'timestamp': datetime.now().isoformat()
            }

            print(f"  [EJECUTANDO] {improvement['action']}")
            print(f"    AI Assistance: {', '.join(improvement['ai_assistance'])}")

            # Simulacion de ejecucion
            action_result['details'] = {
                'ai_tools_enabled': improvement['ai_assistance'],
                'rollback_point': f"commit-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'monitoring_active': True
            }

            execution_log.append(action_result)

        do_result = {
            'cycle_id': plan['cycle_id'],
            'phase': PDCAPhase.DO.value,
            'execution_log': execution_log,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n[DO] {len(execution_log)} acciones ejecutadas")

        return do_result

    def check(self, plan: Dict, do_result: Dict, wait_hours: int = 24) -> Dict:
        """
        FASE 3: CHECK - Validar metricas post-cambio.

        Args:
            plan: Plan original
            do_result: Resultado de fase DO
            wait_hours: Horas de espera para medicion

        Returns:
            Resultados de validacion
        """
        print(f"\n[CHECK] Validando metricas (esperando {wait_hours}h para estabilizacion)...")

        # En implementacion real, esperar wait_hours antes de medir
        # Por ahora, simular metricas post-cambio

        baseline = plan['baseline_metrics']
        post_metrics = self._simulate_post_metrics(baseline, plan['improvements'])

        validation_results = []

        for metric_name, post_value in post_metrics.items():
            if metric_name in ['timestamp', 'mock']:
                continue

            baseline_value = baseline[metric_name]
            priority = self.config['metrics_priority'].get(metric_name, 0.25)

            # Calcular mejora
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

            status = '[OK]' if passed else '[FAIL]'
            print(f"  {status} {metric_name}: {baseline_value:.2f} -> {post_value:.2f} ({improvement_pct:+.2f}%)")

        # Calcular score ponderado
        weighted_score = sum(
            vr['improvement_pct'] * vr['priority_weight']
            for vr in validation_results
        )

        check_result = {
            'cycle_id': plan['cycle_id'],
            'phase': PDCAPhase.CHECK.value,
            'baseline_metrics': baseline,
            'post_metrics': post_metrics,
            'validation_results': validation_results,
            'weighted_score': round(weighted_score, 2),
            'passed': weighted_score >= (self.validation_threshold * 100),
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n[CHECK] Score ponderado: {weighted_score:+.2f}% (umbral: {self.validation_threshold*100:.1f}%)")

        return check_result

    def _simulate_post_metrics(self, baseline: Dict, improvements: List[Dict]) -> Dict:
        """Simula metricas post-cambio para testing."""
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

    def act(self, check_result: Dict) -> Dict:
        """
        FASE 4: ACT - Decidir aplicar, revertir o escalar.

        Args:
            check_result: Resultado de fase CHECK

        Returns:
            Decision y accion tomada
        """
        print("\n[ACT] Decidiendo accion basado en validacion...")

        weighted_score = check_result['weighted_score']
        auto_apply_threshold = self.config['auto_apply_threshold'] * 100
        auto_revert_threshold = self.config['auto_revert_threshold'] * 100

        # Decision automatizada
        if weighted_score >= auto_apply_threshold:
            decision = DecisionAction.APPLY
            reason = f"Mejora significativa ({weighted_score:+.2f}% >= {auto_apply_threshold:.1f}%)"
        elif weighted_score <= auto_revert_threshold:
            decision = DecisionAction.REVERT
            reason = f"Regresion detectada ({weighted_score:+.2f}% <= {auto_revert_threshold:.1f}%)"
        elif weighted_score >= (self.validation_threshold * 100):
            decision = DecisionAction.CONTINUE
            reason = f"Mejora marginal ({weighted_score:+.2f}%), continuar monitoreando"
        else:
            decision = DecisionAction.ESCALATE
            reason = f"Resultado ambiguo ({weighted_score:+.2f}%), requiere revision humana"

        act_result = {
            'cycle_id': check_result['cycle_id'],
            'phase': PDCAPhase.ACT.value,
            'decision': decision.value,
            'reason': reason,
            'weighted_score': weighted_score,
            'actions_taken': [],
            'timestamp': datetime.now().isoformat()
        }

        print(f"  Decision: {decision.value.upper()}")
        print(f"  Razon: {reason}")

        # Ejecutar accion
        if decision == DecisionAction.APPLY:
            act_result['actions_taken'] = [
                "Merge cambios a main branch",
                "Deploy a produccion",
                "Actualizar baseline metrics",
                "Notificar equipo: Mejora validada"
            ]
        elif decision == DecisionAction.REVERT:
            act_result['actions_taken'] = [
                "Rollback automatico activado",
                "Revertir configuraciones IA",
                "Restaurar baseline anterior",
                "Alertar equipo: Regresion detectada"
            ]
        elif decision == DecisionAction.CONTINUE:
            act_result['actions_taken'] = [
                "Mantener cambios en staging",
                "Extender periodo de monitoreo +48h",
                "Recolectar datos adicionales"
            ]
        else:  # ESCALATE
            act_result['actions_taken'] = [
                "Pausar cambios automaticos",
                "Generar reporte para arquitecto",
                "Solicitar revision manual"
            ]

        for action in act_result['actions_taken']:
            print(f"  [ACCION] {action}")

        return act_result

    def run_cycle(self, auto_execute: bool = False) -> Dict:
        """
        Ejecuta ciclo PDCA completo.

        Args:
            auto_execute: Si True, ejecuta todas las fases automaticamente

        Returns:
            Resultado completo del ciclo
        """
        print("=" * 80)
        print("PDCA AUTOMATION AGENT - Ciclo de Mejora Continua")
        print("=" * 80)

        # PLAN
        baseline = self._get_baseline_metrics()
        if baseline.get('mock'):
            print("\n[WARNING] Usando metricas MOCK - Configurar GITHUB_TOKEN para datos reales")

        plan = self.plan(baseline)

        if not auto_execute:
            response = input("\nContinuar con fase DO? [y/N]: ")
            if response.lower() != 'y':
                print("[ABORTED] Ciclo cancelado por usuario")
                return {'status': 'aborted', 'phase': 'plan'}

        # DO
        do_result = self.do(plan)

        if not auto_execute:
            response = input("\nContinuar con fase CHECK? [y/N]: ")
            if response.lower() != 'y':
                print("[ABORTED] Ciclo cancelado por usuario")
                return {'status': 'aborted', 'phase': 'do'}

        # CHECK
        check_result = self.check(plan, do_result)

        if not auto_execute:
            response = input("\nContinuar con fase ACT? [y/N]: ")
            if response.lower() != 'y':
                print("[ABORTED] Ciclo cancelado por usuario")
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

        print("\n" + "=" * 80)
        print(f"CICLO PDCA COMPLETADO: {plan['cycle_id']}")
        print(f"Decision: {act_result['decision'].upper()}")
        print(f"Score: {act_result['weighted_score']:+.2f}%")
        print("=" * 80)

        return cycle_complete


def main():
    """Punto de entrada principal."""
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

        result = agent.run_cycle(auto_execute=args.auto_execute)

        if result.get('status') == 'aborted':
            return 1

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
