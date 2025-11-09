#!/usr/bin/env python3
"""
DORA-SDLC Integration Module

Integra metricas DORA con agentes SDLC para rastrear performance
en tiempo real durante cada fase del ciclo de desarrollo.

Basado en:
- FASES_IMPLEMENTACION_IA.md (Fase 1: T1.2, Fase 5: T5.1)
- ESTRATEGIA_IA.md (Practica 3: AI-accessible Internal Data)

Autor: Claude Code Agent
Fecha: 2025-11-06
"""

import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .sdlc_base import SDLCAgent, SDLCPhaseResult

# Intentar importar DORA metrics
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dora_metrics import DORAMetricsCalculator
    DORA_AVAILABLE = True
except ImportError:
    DORA_AVAILABLE = False
    logging.warning("dora_metrics.py no disponible - metricas DORA deshabilitadas")


class DORAMetrics:
    """
    Metricas DORA en memoria para rastreo durante SDLC.

    Mapeo SDLC Phase -> DORA Metric:
    - planning -> Lead Time start (commit timestamp)
    - design -> Lead Time checkpoint
    - testing -> Change Failure Rate (test pass/fail)
    - deployment -> Deployment Frequency + Lead Time end
    - maintenance -> MTTR (incident resolution)
    """

    def __init__(self):
        """Inicializa almacenamiento de metricas."""
        self.cycles: List[Dict[str, Any]] = []
        self.current_cycle: Optional[Dict[str, Any]] = None
        self.metrics_file = Path(".dora_sdlc_metrics.json")
        self._load_metrics()

    def _load_metrics(self) -> None:
        """Carga metricas desde disco."""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                self.cycles = data.get('cycles', [])

    def _save_metrics(self) -> None:
        """Guarda metricas a disco."""
        with open(self.metrics_file, 'w') as f:
            json.dump({
                'cycles': self.cycles,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def start_cycle(self, feature_id: str, phase: str) -> None:
        """
        Inicia nuevo ciclo SDLC.

        Args:
            feature_id: Identificador del feature
            phase: Fase SDLC inicial
        """
        self.current_cycle = {
            'feature_id': feature_id,
            'cycle_id': f"cycle-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'start_phase': phase,
            'phases': [],
            'metrics': {
                'deployment_frequency': None,
                'lead_time': None,
                'change_failure_rate': None,
                'mttr': None
            },
            'status': 'in_progress'
        }

        logging.info(f"[DORA] Ciclo iniciado: {self.current_cycle['cycle_id']}")

    def record_phase(
        self,
        phase: str,
        decision: str,
        duration_seconds: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra completacion de fase SDLC.

        Args:
            phase: Nombre de la fase
            decision: Decision (go, no-go, review, blocked)
            duration_seconds: Duracion de la fase
            metadata: Metadatos adicionales
        """
        if not self.current_cycle:
            logging.warning("[DORA] No hay ciclo activo")
            return

        phase_record = {
            'phase': phase,
            'decision': decision,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration_seconds,
            'metadata': metadata or {}
        }

        self.current_cycle['phases'].append(phase_record)

        # Actualizar metricas basadas en fase
        if phase == 'testing':
            self._update_cfr(decision, metadata)
        elif phase == 'deployment':
            self._update_deployment_metrics()
        elif phase == 'maintenance':
            self._update_mttr(metadata)

        logging.info(f"[DORA] Fase registrada: {phase} ({duration_seconds:.2f}s)")

    def _update_cfr(self, decision: str, metadata: Optional[Dict]) -> None:
        """Actualiza Change Failure Rate basado en tests."""
        if not metadata:
            return

        tests_passed = metadata.get('tests_passed', 0)
        tests_failed = metadata.get('tests_failed', 0)
        total = tests_passed + tests_failed

        if total > 0:
            cfr = (tests_failed / total) * 100
            self.current_cycle['metrics']['change_failure_rate'] = round(cfr, 2)

    def _update_deployment_metrics(self) -> None:
        """Actualiza Deployment Frequency y Lead Time."""
        if not self.current_cycle:
            return

        # Lead Time: tiempo desde planning hasta deployment
        start_time = datetime.fromisoformat(self.current_cycle['start_time'])
        end_time = datetime.now()
        lead_time_hours = (end_time - start_time).total_seconds() / 3600

        self.current_cycle['metrics']['lead_time'] = round(lead_time_hours, 2)

        # Deployment Frequency: calcular desde ultimos ciclos
        recent_deployments = [
            c for c in self.cycles[-30:]  # Ultimos 30 ciclos
            if any(p['phase'] == 'deployment' for p in c.get('phases', []))
        ]

        if recent_deployments:
            days_span = 30  # Aproximacion
            df = len(recent_deployments) / days_span
            self.current_cycle['metrics']['deployment_frequency'] = round(df, 2)

    def _update_mttr(self, metadata: Optional[Dict]) -> None:
        """Actualiza Mean Time to Recovery."""
        if not metadata:
            return

        incident_duration = metadata.get('incident_duration_hours')
        if incident_duration:
            self.current_cycle['metrics']['mttr'] = round(incident_duration, 2)

    def complete_cycle(self, final_decision: str) -> Dict[str, Any]:
        """
        Completa ciclo actual y calcula metricas finales.

        Args:
            final_decision: Decision final del ciclo

        Returns:
            Resumen de metricas del ciclo
        """
        if not self.current_cycle:
            return {}

        self.current_cycle['end_time'] = datetime.now().isoformat()
        self.current_cycle['final_decision'] = final_decision
        self.current_cycle['status'] = 'completed'

        # Calcular duracion total
        start = datetime.fromisoformat(self.current_cycle['start_time'])
        end = datetime.fromisoformat(self.current_cycle['end_time'])
        total_duration = (end - start).total_seconds()
        self.current_cycle['total_duration_seconds'] = total_duration

        # Guardar ciclo completado
        self.cycles.append(self.current_cycle)
        self._save_metrics()

        summary = {
            'cycle_id': self.current_cycle['cycle_id'],
            'feature_id': self.current_cycle['feature_id'],
            'duration_hours': round(total_duration / 3600, 2),
            'phases_completed': len(self.current_cycle['phases']),
            'metrics': self.current_cycle['metrics']
        }

        logging.info(f"[DORA] Ciclo completado: {summary['cycle_id']}")
        logging.info(f"[DORA] Lead Time: {summary['metrics']['lead_time']}h")

        self.current_cycle = None
        return summary

    def get_summary(self, last_n_cycles: int = 30) -> Dict[str, Any]:
        """
        Genera resumen de metricas DORA.

        Args:
            last_n_cycles: Numero de ciclos a incluir

        Returns:
            Resumen agregado de metricas
        """
        recent_cycles = self.cycles[-last_n_cycles:]

        if not recent_cycles:
            return {'error': 'No hay ciclos registrados'}

        # Calcular promedios
        lead_times = [
            c['metrics'].get('lead_time', 0)
            for c in recent_cycles
            if c['metrics'].get('lead_time')
        ]

        cfrs = [
            c['metrics'].get('change_failure_rate', 0)
            for c in recent_cycles
            if c['metrics'].get('change_failure_rate') is not None
        ]

        mttrs = [
            c['metrics'].get('mttr', 0)
            for c in recent_cycles
            if c['metrics'].get('mttr')
        ]

        # Deployment frequency: ciclos con deployment / dias
        deployments = [
            c for c in recent_cycles
            if any(p['phase'] == 'deployment' for p in c.get('phases', []))
        ]

        days_span = 30 if len(recent_cycles) >= 30 else len(recent_cycles)
        df = len(deployments) / days_span if days_span > 0 else 0

        return {
            'period': {
                'cycles': len(recent_cycles),
                'days_approximate': days_span
            },
            'metrics': {
                'deployment_frequency': {
                    'value': round(df, 2),
                    'unit': 'deployments/day'
                },
                'lead_time_for_changes': {
                    'value': round(sum(lead_times) / len(lead_times), 2) if lead_times else 0,
                    'unit': 'hours',
                    'samples': len(lead_times)
                },
                'change_failure_rate': {
                    'value': round(sum(cfrs) / len(cfrs), 2) if cfrs else 0,
                    'unit': '%',
                    'samples': len(cfrs)
                },
                'mean_time_to_recovery': {
                    'value': round(sum(mttrs) / len(mttrs), 2) if mttrs else 0,
                    'unit': 'hours',
                    'samples': len(mttrs)
                }
            }
        }


class DORATrackedSDLCAgent(SDLCAgent):
    """
    SDLCAgent extendido con rastreo automatico de metricas DORA.

    Todos los agentes que hereden de esta clase registraran
    automaticamente sus metricas en el sistema DORA.
    """

    def __init__(
        self,
        name: str,
        phase: str,
        config: Optional[Dict[str, Any]] = None,
        dora_metrics: Optional[DORAMetrics] = None
    ):
        """
        Inicializa agente con rastreo DORA.

        Args:
            name: Nombre del agente
            phase: Fase SDLC
            config: Configuracion
            dora_metrics: Instancia de DORAMetrics (crea una nueva si None)
        """
        super().__init__(name, phase, config)
        self.dora_metrics = dora_metrics or DORAMetrics()

    def execute(self, input_data: Dict[str, Any]) -> Any:
        """
        Ejecuta agente con rastreo DORA automatico.

        Args:
            input_data: Datos de entrada

        Returns:
            Resultado de ejecucion
        """
        feature_id = input_data.get('feature_id', 'unknown')

        # Iniciar ciclo si es primera fase
        if self.phase == 'planning' and not self.dora_metrics.current_cycle:
            self.dora_metrics.start_cycle(feature_id, self.phase)

        # Medir duracion
        start_time = time.time()

        try:
            # Ejecutar logica del agente
            result = self.run(input_data)

            duration = time.time() - start_time

            # Extraer metadata para DORA
            metadata = {}
            if hasattr(result, 'metadata'):
                metadata = result.metadata
            elif isinstance(result, dict):
                metadata = result.get('metadata', {})

            # Registrar fase en DORA
            decision = getattr(result, 'decision', 'unknown') if hasattr(result, 'decision') else 'unknown'
            self.dora_metrics.record_phase(
                phase=self.phase,
                decision=decision,
                duration_seconds=duration,
                metadata=metadata
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            self.dora_metrics.record_phase(
                phase=self.phase,
                decision='failed',
                duration_seconds=duration,
                metadata={'error': str(e)}
            )
            raise


def dora_tracked(func: Callable) -> Callable:
    """
    Decorador para rastrear metricas DORA en funciones arbitrarias.

    Uso:
        @dora_tracked
        def deploy_to_production(feature_id: str) -> bool:
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        metrics = DORAMetrics()
        feature_id = kwargs.get('feature_id', args[0] if args else 'unknown')

        if not metrics.current_cycle:
            metrics.start_cycle(feature_id, func.__name__)

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            metrics.record_phase(
                phase=func.__name__,
                decision='success',
                duration_seconds=duration,
                metadata={'function': func.__name__}
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            metrics.record_phase(
                phase=func.__name__,
                decision='failed',
                duration_seconds=duration,
                metadata={'error': str(e)}
            )
            raise

    return wrapper


def integrate_dora_with_github(
    repo: str,
    github_token: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Integra metricas SDLC locales con GitHub para calculo DORA completo.

    Combina:
    - Metricas locales de ciclos SDLC
    - Datos de GitHub API (commits, PRs, deployments, issues)

    Args:
        repo: Repositorio en formato 'owner/repo'
        github_token: GitHub token
        days: Dias de historial

    Returns:
        Reporte DORA combinado
    """
    if not DORA_AVAILABLE:
        return {'error': 'DORA metrics module no disponible'}

    # Obtener metricas locales
    local_metrics = DORAMetrics()
    local_summary = local_metrics.get_summary(last_n_cycles=days)

    # Obtener metricas GitHub
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        calculator = DORAMetricsCalculator(
            repo=repo,
            github_token=github_token,
            start_date=start_date,
            end_date=end_date
        )

        github_report = calculator.generate_report()

        # Combinar metricas
        combined = {
            'source': 'combined',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'local_sdlc_metrics': local_summary,
            'github_metrics': github_report['metrics'],
            'overall_classification': github_report['overall_classification'],
            'timestamp': datetime.now().isoformat()
        }

        return combined

    except Exception as e:
        logging.error(f"Error integrando con GitHub: {e}")
        return {
            'source': 'local_only',
            'local_sdlc_metrics': local_summary,
            'github_error': str(e)
        }


def print_dora_summary(summary: Dict[str, Any]) -> None:
    """Imprime resumen de metricas DORA."""
    print("\n" + "=" * 80)
    print("DORA METRICS SUMMARY (SDLC Integration)")
    print("=" * 80)

    if 'error' in summary:
        print(f"\n[ERROR] {summary['error']}")
        return

    period = summary.get('period', {})
    print(f"\nPeriodo: {period.get('cycles', 0)} ciclos (~{period.get('days_approximate', 0)} dias)")

    metrics = summary.get('metrics', {})
    print("\nMetricas:")
    print(f"  Deployment Frequency: {metrics['deployment_frequency']['value']:.2f} {metrics['deployment_frequency']['unit']}")
    print(f"  Lead Time: {metrics['lead_time_for_changes']['value']:.2f} {metrics['lead_time_for_changes']['unit']}")
    print(f"    (basado en {metrics['lead_time_for_changes']['samples']} muestras)")
    print(f"  Change Failure Rate: {metrics['change_failure_rate']['value']:.2f}%")
    print(f"    (basado en {metrics['change_failure_rate']['samples']} muestras)")
    print(f"  MTTR: {metrics['mean_time_to_recovery']['value']:.2f} {metrics['mean_time_to_recovery']['unit']}")
    print(f"    (basado en {metrics['mean_time_to_recovery']['samples']} muestras)")

    print("\n" + "=" * 80)


# Ejemplo de uso
if __name__ == '__main__':
    # Demo de rastreo DORA
    metrics = DORAMetrics()

    # Simular ciclo SDLC
    metrics.start_cycle('FEAT-001', 'planning')
    metrics.record_phase('planning', 'go', 1800.0)
    metrics.record_phase('design', 'go', 3600.0)
    metrics.record_phase('testing', 'go', 7200.0, {'tests_passed': 95, 'tests_failed': 5})
    metrics.record_phase('deployment', 'go', 900.0)

    summary = metrics.complete_cycle('success')
    print_dora_summary(metrics.get_summary())
