#!/usr/bin/env python3
"""
DORA Metrics Calculator para el proyecto IACT.

Calcula y reporta las 4 métricas clave de DORA:
1. Deployment Frequency
2. Lead Time for Changes
3. Change Failure Rate
4. Mean Time to Recovery (MTTR)

Uso:
    python scripts/dora_metrics.py --days 30
    python scripts/dora_metrics.py --start 2025-01-01 --end 2025-01-31 --format json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install: pip install requests")
    sys.exit(1)


class DORAMetricsCalculator:
    """Calculadora de DORA metrics usando GitHub API."""

    def __init__(
        self,
        repo: str,
        github_token: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """
        Inicializa el calculador.

        Args:
            repo: Repositorio en formato 'owner/repo'
            github_token: GitHub personal access token
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
        """
        self.repo = repo
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.github_token:
            raise ValueError("GITHUB_TOKEN requerido (env var o parámetro)")

        self.end_date = end_date or datetime.now()
        self.start_date = start_date or (self.end_date - timedelta(days=30))

        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get_deployments(self) -> List[Dict]:
        """
        Obtiene deployments del período.

        Returns:
            Lista de deployments con timestamps
        """
        url = f"{self.api_base}/repos/{self.repo}/deployments"
        params = {
            "environment": "production",
            "per_page": 100
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        deployments = []
        for deployment in response.json():
            created_at = datetime.fromisoformat(deployment['created_at'].replace('Z', '+00:00'))

            if self.start_date <= created_at <= self.end_date:
                # Get commit info
                sha = deployment['sha']
                commit = self._get_commit(sha)

                deployments.append({
                    'id': deployment['id'],
                    'sha': sha,
                    'commit_timestamp': commit['commit_timestamp'],
                    'deployment_timestamp': created_at,
                    'environment': deployment['environment']
                })

        return deployments

    def _get_commit(self, sha: str) -> Dict:
        """Obtiene información de un commit."""
        url = f"{self.api_base}/repos/{self.repo}/commits/{sha}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        commit_data = response.json()
        commit_timestamp = datetime.fromisoformat(
            commit_data['commit']['author']['date'].replace('Z', '+00:00')
        )

        return {
            'sha': sha,
            'message': commit_data['commit']['message'],
            'commit_timestamp': commit_timestamp
        }

    def _get_incidents(self) -> List[Dict]:
        """
        Obtiene incidents del período (issues con label 'incident').

        Returns:
            Lista de incidents con timestamps
        """
        url = f"{self.api_base}/repos/{self.repo}/issues"
        params = {
            "labels": "incident",
            "state": "all",
            "since": self.start_date.isoformat(),
            "per_page": 100
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        incidents = []
        for issue in response.json():
            created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))

            if created_at > self.end_date:
                continue

            resolved_at = None
            if issue['closed_at']:
                resolved_at = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))

            incidents.append({
                'number': issue['number'],
                'title': issue['title'],
                'created_at': created_at,
                'resolved_at': resolved_at,
                'labels': [label['name'] for label in issue['labels']]
            })

        return incidents

    def calculate_deployment_frequency(self) -> float:
        """
        Calcula deployments por día.

        Returns:
            Número promedio de deployments por día
        """
        deployments = self._get_deployments()
        days = (self.end_date - self.start_date).days

        if days == 0:
            days = 1

        return len(deployments) / days

    def calculate_lead_time(self) -> timedelta:
        """
        Calcula lead time promedio (commit → production).

        Returns:
            Timedelta promedio
        """
        deployments = self._get_deployments()

        if not deployments:
            return timedelta(0)

        lead_times = []
        for deployment in deployments:
            lead_time = deployment['deployment_timestamp'] - deployment['commit_timestamp']
            lead_times.append(lead_time)

        avg_seconds = sum(lt.total_seconds() for lt in lead_times) / len(lead_times)
        return timedelta(seconds=avg_seconds)

    def calculate_change_failure_rate(self) -> float:
        """
        Calcula % de deployments que causaron incidentes.

        Returns:
            Porcentaje (0.0 - 1.0)
        """
        deployments = self._get_deployments()
        incidents = self._get_incidents()

        if not deployments:
            return 0.0

        failed_deployments = 0
        for deployment in deployments:
            deploy_time = deployment['deployment_timestamp']

            # Check si hubo incident en las siguientes 24h
            for incident in incidents:
                incident_time = incident['created_at']
                if deploy_time <= incident_time <= deploy_time + timedelta(hours=24):
                    failed_deployments += 1
                    break

        return failed_deployments / len(deployments)

    def calculate_mttr(self) -> timedelta:
        """
        Calcula MTTR promedio.

        Returns:
            Timedelta promedio de recuperación
        """
        incidents = self._get_incidents()

        recovery_times = []
        for incident in incidents:
            if incident['resolved_at']:
                recovery_time = incident['resolved_at'] - incident['created_at']
                recovery_times.append(recovery_time)

        if not recovery_times:
            return timedelta(0)

        avg_seconds = sum(rt.total_seconds() for rt in recovery_times) / len(recovery_times)
        return timedelta(seconds=avg_seconds)

    def classify_performance(self, metric: str, value: float) -> str:
        """
        Clasifica performance según DORA research.

        Args:
            metric: Nombre de la métrica
            value: Valor de la métrica

        Returns:
            Clasificación: Elite, High, Medium, Low
        """
        thresholds = {
            'deployment_frequency': {
                'elite': 1,      # >= 1 deployment/día
                'high': 0.14,    # >= 1 deployment/semana
                'medium': 0.03   # >= 1 deployment/mes
            },
            'lead_time': {
                'elite': 1,      # <= 1 día
                'high': 7,       # <= 1 semana
                'medium': 30     # <= 1 mes
            },
            'change_failure_rate': {
                'elite': 0.15,   # <= 15%
                'high': 0.30,    # <= 30%
                'medium': 0.45   # <= 45%
            },
            'mttr': {
                'elite': 1,      # <= 1 hora
                'high': 24,      # <= 1 día
                'medium': 168    # <= 1 semana
            }
        }

        t = thresholds[metric]

        if metric == 'deployment_frequency':
            # Mayor es mejor
            if value >= t['elite']:
                return 'Elite'
            elif value >= t['high']:
                return 'High'
            elif value >= t['medium']:
                return 'Medium'
            else:
                return 'Low'
        else:
            # Menor es mejor
            if value <= t['elite']:
                return 'Elite'
            elif value <= t['high']:
                return 'High'
            elif value <= t['medium']:
                return 'Medium'
            else:
                return 'Low'

    def generate_report(self) -> Dict:
        """
        Genera reporte completo de DORA metrics.

        Returns:
            Diccionario con todas las métricas y clasificaciones
        """
        print(f"Calculando DORA metrics para {self.repo}...")
        print(f"Período: {self.start_date.date()} → {self.end_date.date()}\n")

        deployment_freq = self.calculate_deployment_frequency()
        lead_time = self.calculate_lead_time()
        cfr = self.calculate_change_failure_rate()
        mttr = self.calculate_mttr()

        return {
            'repository': self.repo,
            'period': {
                'start': self.start_date.isoformat(),
                'end': self.end_date.isoformat(),
                'days': (self.end_date - self.start_date).days
            },
            'metrics': {
                'deployment_frequency': {
                    'value': round(deployment_freq, 2),
                    'unit': 'deployments/day',
                    'classification': self.classify_performance('deployment_frequency', deployment_freq),
                    'description': 'Cuántas veces desplegamos a producción'
                },
                'lead_time_for_changes': {
                    'value': round(lead_time.total_seconds() / 3600, 2),
                    'unit': 'hours',
                    'classification': self.classify_performance('lead_time', lead_time.days),
                    'description': 'Tiempo desde commit hasta producción'
                },
                'change_failure_rate': {
                    'value': round(cfr * 100, 2),
                    'unit': '%',
                    'classification': self.classify_performance('change_failure_rate', cfr),
                    'description': 'Porcentaje de deployments que causan incidentes'
                },
                'mean_time_to_recovery': {
                    'value': round(mttr.total_seconds() / 3600, 2),
                    'unit': 'hours',
                    'classification': self.classify_performance('mttr', mttr.total_seconds() / 3600),
                    'description': 'Tiempo promedio para recuperar de incidente'
                }
            },
            'overall_classification': self._calculate_overall_classification({
                'deployment_frequency': self.classify_performance('deployment_frequency', deployment_freq),
                'lead_time': self.classify_performance('lead_time', lead_time.days),
                'change_failure_rate': self.classify_performance('change_failure_rate', cfr),
                'mttr': self.classify_performance('mttr', mttr.total_seconds() / 3600)
            })
        }

    def _calculate_overall_classification(self, classifications: Dict[str, str]) -> str:
        """Calcula clasificación general basada en todas las métricas."""
        scores = {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        avg_score = sum(scores[c] for c in classifications.values()) / len(classifications)

        if avg_score >= 3.5:
            return 'Elite'
        elif avg_score >= 2.5:
            return 'High'
        elif avg_score >= 1.5:
            return 'Medium'
        else:
            return 'Low'


def print_report(report: Dict, format: str = 'text') -> None:
    """
    Imprime reporte en formato especificado.

    Args:
        report: Diccionario con el reporte
        format: Formato (text, json, markdown)
    """
    if format == 'json':
        print(json.dumps(report, indent=2))
        return

    if format == 'markdown':
        print_markdown_report(report)
        return

    # Formato text
    print("=" * 80)
    print("DORA METRICS REPORT")
    print("=" * 80)
    print(f"\nRepositorio: {report['repository']}")
    print(f"Período: {report['period']['start'][:10]} → {report['period']['end'][:10]}")
    print(f"Duración: {report['period']['days']} días")

    print(f"\n{'Métrica':<30} {'Valor':>15} {'Clasificación':>15}")
    print("-" * 80)

    for metric_key, metric_data in report['metrics'].items():
        name = metric_key.replace('_', ' ').title()
        value = f"{metric_data['value']} {metric_data['unit']}"
        classification = metric_data['classification']

        # Symbol based on classification
        symbol = {
            'Elite': '[ELITE]',
            'High': '[HIGH]',
            'Medium': '[MEDIUM]',
            'Low': '[LOW]'
        }.get(classification, '')

        print(f"{name:<30} {value:>15} {symbol:>10} {classification:>12}")

    print("\n" + "-" * 80)
    print(f"Clasificación General: {report['overall_classification']}")
    print("=" * 80)


def print_markdown_report(report: Dict) -> None:
    """Imprime reporte en formato Markdown."""
    print(f"""# DORA Metrics Report

**Repositorio**: {report['repository']}
**Período**: {report['period']['start'][:10]} → {report['period']['end'][:10]} ({report['period']['days']} días)
**Clasificación General**: **{report['overall_classification']}**

## Métricas

| Métrica | Valor | Clasificación | Descripción |
|---------|-------|---------------|-------------|
""")

    for metric_key, metric_data in report['metrics'].items():
        name = metric_key.replace('_', ' ').title()
        value = f"{metric_data['value']} {metric_data['unit']}"
        classification = metric_data['classification']
        description = metric_data['description']

        symbol = {
            'Elite': '[ELITE]',
            'High': '[HIGH]',
            'Medium': '[MEDIUM]',
            'Low': '[LOW]'
        }.get(classification, '')

        print(f"| {name} | {value} | {symbol} {classification} | {description} |")

    print(f"""
## Interpretación

### Deployment Frequency
- **Elite**: >= 1 deployment/día
- **High**: >= 1 deployment/semana
- **Medium**: >= 1 deployment/mes
- **Low**: < 1 deployment/mes

### Lead Time for Changes
- **Elite**: <= 1 día
- **High**: <= 1 semana
- **Medium**: <= 1 mes
- **Low**: > 1 mes

### Change Failure Rate
- **Elite**: <= 15%
- **High**: <= 30%
- **Medium**: <= 45%
- **Low**: > 45%

### Mean Time to Recovery
- **Elite**: <= 1 hora
- **High**: <= 1 día
- **Medium**: <= 1 semana
- **Low**: > 1 semana

---

*Generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Basado en [DORA Research](https://dora.dev/)*
""")


class DocumentationMetricsCalculator:
    """Calculadora de métricas de documentación."""

    def __init__(self, project_root: Path):
        """
        Inicializa el calculador.

        Args:
            project_root: Raíz del proyecto
        """
        self.project_root = project_root
        self.guides_dir = project_root / "docs" / "guias"

    def calculate_documentation_coverage(self) -> Dict:
        """
        Calcula coverage de documentación.

        Returns:
            Diccionario con métricas de coverage
        """
        # Contar guías actuales
        if not self.guides_dir.exists():
            return {
                "total_guides_planned": 147,
                "total_guides_actual": 0,
                "coverage_percent": 0.0,
                "by_priority": {
                    "P0": {"planned": 20, "actual": 0, "percent": 0.0},
                    "P1": {"planned": 40, "actual": 0, "percent": 0.0},
                    "P2": {"planned": 50, "actual": 0, "percent": 0.0},
                    "P3": {"planned": 37, "actual": 0, "percent": 0.0}
                }
            }

        # Contar archivos .md (excluyendo README y METRICS)
        guide_files = []
        for md_file in self.guides_dir.rglob("*.md"):
            if md_file.name not in ["README.md", "METRICS.md"]:
                guide_files.append(md_file)

        total_actual = len(guide_files)

        # Contar por categoría
        by_category = {}
        for guide_file in guide_files:
            category = guide_file.parent.name
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_guides_planned": 147,
            "total_guides_actual": total_actual,
            "coverage_percent": round((total_actual / 147) * 100, 2),
            "by_category": by_category,
            "by_priority": {
                "P0": {
                    "planned": 20,
                    "actual": total_actual if total_actual <= 20 else 20,
                    "percent": round((min(total_actual, 20) / 20) * 100, 2)
                },
                "P1": {
                    "planned": 40,
                    "actual": max(0, total_actual - 20) if total_actual > 20 else 0,
                    "percent": 0.0
                },
                "P2": {
                    "planned": 50,
                    "actual": 0,
                    "percent": 0.0
                },
                "P3": {
                    "planned": 37,
                    "actual": 0,
                    "percent": 0.0
                }
            }
        }

    def calculate_onboarding_time(self) -> Dict:
        """
        Calcula tiempo estimado de onboarding.

        Returns:
            Diccionario con tiempos de onboarding
        """
        onboarding_dir = self.guides_dir / "onboarding"

        if not onboarding_dir.exists():
            return {
                "estimated_time_minutes": 0,
                "target_time_minutes": 30,
                "guides_count": 0,
                "status": "Not started"
            }

        # Contar guías de onboarding
        onboarding_guides = list(onboarding_dir.glob("*.md"))

        # Estimar tiempo (promedio 8 min por guía)
        # Basado en metadata de las guías generadas
        estimated_time = len(onboarding_guides) * 8

        return {
            "estimated_time_minutes": estimated_time,
            "target_time_minutes": 30,
            "guides_count": len(onboarding_guides),
            "status": "On track" if estimated_time <= 60 else "Needs optimization",
            "reduction_needed_minutes": max(0, estimated_time - 30)
        }


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Calculador de DORA metrics para el proyecto IACT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:

  # Últimos 30 días
  python scripts/dora_metrics.py --repo owner/repo

  # Período específico
  python scripts/dora_metrics.py --repo owner/repo \\
    --start 2025-01-01 --end 2025-01-31

  # Output en JSON
  python scripts/dora_metrics.py --repo owner/repo --format json

  # Output en Markdown
  python scripts/dora_metrics.py --repo owner/repo --format markdown > report.md

  # Solo métricas de documentación
  python scripts/dora_metrics.py --docs-only
        """
    )

    parser.add_argument(
        '--repo',
        type=str,
        default='2-Coatl/IACT---project',
        help='Repositorio en formato owner/repo (default: 2-Coatl/IACT---project)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Número de días hacia atrás (default: 30)'
    )

    parser.add_argument(
        '--start',
        type=str,
        help='Fecha inicio (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='Fecha fin (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json', 'markdown'],
        default='text',
        help='Formato de output (default: text)'
    )

    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub personal access token (o usar env GITHUB_TOKEN)'
    )

    parser.add_argument(
        '--docs-only',
        action='store_true',
        help='Solo calcular métricas de documentación (no requiere GITHUB_TOKEN)'
    )

    args = parser.parse_args()

    # Si es docs-only, solo calcular métricas de documentación
    if args.docs_only:
        try:
            project_root = Path(__file__).parent.parent
            doc_calc = DocumentationMetricsCalculator(project_root)

            coverage = doc_calc.calculate_documentation_coverage()
            onboarding = doc_calc.calculate_onboarding_time()

            report = {
                "documentation_metrics": {
                    "coverage": coverage,
                    "onboarding": onboarding,
                    "timestamp": datetime.now().isoformat()
                }
            }

            if args.format == 'json':
                print(json.dumps(report, indent=2))
            else:
                print("=" * 80)
                print("DOCUMENTATION METRICS REPORT")
                print("=" * 80)
                print(f"\nCoverage: {coverage['coverage_percent']}% ({coverage['total_guides_actual']}/{coverage['total_guides_planned']} guías)")
                print(f"\nPor categoría:")
                for cat, count in coverage['by_category'].items():
                    print(f"  - {cat}: {count} guías")
                print(f"\nOnboarding time: {onboarding['estimated_time_minutes']} min (target: {onboarding['target_time_minutes']} min)")
                print(f"Status: {onboarding['status']}")
                print("=" * 80)

            return 0

        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1

    # Parse dates
    end_date = datetime.now()
    if args.end:
        end_date = datetime.strptime(args.end, '%Y-%m-%d')

    if args.start:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=args.days)

    try:
        calculator = DORAMetricsCalculator(
            repo=args.repo,
            github_token=args.github_token,
            start_date=start_date,
            end_date=end_date
        )

        report = calculator.generate_report()
        print_report(report, args.format)

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
