#!/usr/bin/env python3
"""
Alert on Errors - Detectar y alertar errores criticos en Cassandra logs

Consulta Cassandra cada 5 minutos (via cron) para detectar:
- >10 ERROR logs en ultimos 5 minutos
- >5 CRITICAL logs en ultimos 5 minutos
- >100 logs de un mismo logger (posible loop)

Notificaciones:
- Email (SMTP)
- Slack webhook
- Archivo alert.log

Usage:
    # Cron: Cada 5 minutos
    */5 * * * * python /app/scripts/logging/alert_on_errors.py \\
        --contact-points 127.0.0.1 \\
        --email alerts@iact.com \\
        --slack-webhook https://hooks.slack.com/...

Requirements:
    pip install cassandra-driver requests

Related:
    - ADR-2025-004: Centralized Log Storage en Cassandra
    - OBSERVABILITY_LAYERS.md: Capa 2 - Application Logs
"""

import argparse
import sys
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import json

try:
    from cassandra.cluster import Cluster
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AlertManager:
    """Gestor de alertas para logs de Cassandra."""

    def __init__(
        self,
        contact_points: List[str],
        keyspace: str = 'logging',
        port: int = 9042,
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        alert_log: str = '/var/log/iact/log_alerts.log'
    ):
        """
        Args:
            contact_points: Lista de IPs Cassandra
            keyspace: Keyspace (default: 'logging')
            port: Puerto Cassandra (default: 9042)
            email: Email para alertas (opcional)
            slack_webhook: Slack webhook URL (opcional)
            alert_log: Path a log file para alertas (default: /var/log/iact/log_alerts.log)
        """
        self.contact_points = contact_points
        self.keyspace = keyspace
        self.port = port
        self.email = email
        self.slack_webhook = slack_webhook
        self.alert_log = alert_log

        # Stats
        self.stats = {
            'errors_detected': 0,
            'criticals_detected': 0,
            'alerts_sent': 0
        }

        # Conectar a Cassandra
        self.cluster = None
        self.session = None

    def connect(self):
        """Conectar a Cassandra."""
        self.cluster = Cluster(
            contact_points=self.contact_points,
            port=self.port
        )
        self.session = self.cluster.connect(self.keyspace)

    def check_error_rate(self, minutes: int = 5) -> Dict:
        """
        Verificar tasa de errores en ultimos N minutos.

        Args:
            minutes: Ventana de tiempo (default: 5)

        Returns:
            Dict con counts por nivel
        """
        # Query: Contar errores por nivel
        # Cassandra requiere partition key (log_date)
        log_dates = [date.today()]  # Hoy

        cql = """
        SELECT level, COUNT(*) as count
        FROM application_logs
        WHERE log_date = ?
        AND timestamp >= ?
        GROUP BY level
        """

        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        counts = {'ERROR': 0, 'CRITICAL': 0, 'WARNING': 0}

        for log_date in log_dates:
            rows = self.session.execute(cql, (log_date, cutoff_time))
            for row in rows:
                if row.level in counts:
                    counts[row.level] += row.count

        return counts

    def check_logger_loops(self, minutes: int = 5, threshold: int = 100) -> List[Dict]:
        """
        Detectar loggers con >N logs (posible loop infinito).

        Args:
            minutes: Ventana de tiempo
            threshold: Logs maximos por logger (default: 100)

        Returns:
            Lista de loggers problemáticos
        """
        log_dates = [date.today()]
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        cql = """
        SELECT logger, COUNT(*) as count
        FROM application_logs
        WHERE log_date = ?
        AND timestamp >= ?
        GROUP BY logger
        """

        problem_loggers = []

        for log_date in log_dates:
            rows = self.session.execute(cql, (log_date, cutoff_time))
            for row in rows:
                if row.count > threshold:
                    problem_loggers.append({
                        'logger': row.logger,
                        'count': row.count,
                        'threshold': threshold
                    })

        return problem_loggers

    def send_alert(self, title: str, message: str, severity: str = 'ERROR'):
        """
        Enviar alerta via email, Slack, y log file.

        Args:
            title: Titulo de alerta
            message: Mensaje detallado
            severity: ERROR | CRITICAL
        """
        timestamp = datetime.now().isoformat()

        alert = {
            'timestamp': timestamp,
            'title': title,
            'message': message,
            'severity': severity
        }

        # 1. Log a archivo
        with open(self.alert_log, 'a') as f:
            f.write(f"[{timestamp}] [{severity}] {title}\n{message}\n\n")

        # 2. Slack webhook
        if self.slack_webhook and REQUESTS_AVAILABLE:
            self._send_slack(alert)

        # 3. Email (TODO: Implementar SMTP)
        if self.email:
            self._send_email(alert)

        self.stats['alerts_sent'] += 1

    def _send_slack(self, alert: Dict):
        """Enviar alerta a Slack."""
        try:
            payload = {
                "text": f"[{alert['severity']}] {alert['title']}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{alert['title']}*\n{alert['message']}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Timestamp: {alert['timestamp']}"
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=5
            )

            if response.status_code != 200:
                print(f"[WARNING] Slack webhook failed: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] Slack notification failed: {e}")

    def _send_email(self, alert: Dict):
        """Enviar alerta via email (TODO)."""
        # TODO: Implementar SMTP
        print(f"[TODO] Send email to {self.email}: {alert['title']}")

    def run_checks(self):
        """Ejecutar todos los checks y enviar alertas si necesario."""
        print(f"[{datetime.now()}] Running log checks...")

        # Check 1: Error rate
        error_counts = self.check_error_rate(minutes=5)
        self.stats['errors_detected'] = error_counts['ERROR']
        self.stats['criticals_detected'] = error_counts['CRITICAL']

        print(f"[INFO] Last 5 min: ERROR={error_counts['ERROR']}, CRITICAL={error_counts['CRITICAL']}, WARNING={error_counts['WARNING']}")

        # Alert si >10 ERROR
        if error_counts['ERROR'] > 10:
            self.send_alert(
                title=f"High ERROR rate: {error_counts['ERROR']} errors/5min",
                message=f"Detected {error_counts['ERROR']} ERROR logs in last 5 minutes.\n"
                        f"Threshold: 10 errors/5min.\n"
                        f"Check logs: cqlsh -e \"SELECT * FROM logging.application_logs WHERE level='ERROR' LIMIT 100;\"",
                severity='ERROR'
            )

        # Alert si >5 CRITICAL
        if error_counts['CRITICAL'] > 5:
            self.send_alert(
                title=f"CRITICAL errors detected: {error_counts['CRITICAL']} criticals/5min",
                message=f"Detected {error_counts['CRITICAL']} CRITICAL logs in last 5 minutes.\n"
                        f"Threshold: 5 criticals/5min.\n"
                        f"IMMEDIATE ACTION REQUIRED.",
                severity='CRITICAL'
            )

        # Check 2: Logger loops
        problem_loggers = self.check_logger_loops(minutes=5, threshold=100)
        if problem_loggers:
            loggers_str = '\n'.join([
                f"  - {l['logger']}: {l['count']} logs"
                for l in problem_loggers
            ])
            self.send_alert(
                title=f"Possible logging loop detected: {len(problem_loggers)} loggers",
                message=f"Detected loggers with >100 logs/5min:\n{loggers_str}\n"
                        f"Possible infinite loop or error storm.\n"
                        f"Check code: grep -r '{problem_loggers[0]['logger']}' .",
                severity='ERROR'
            )

        print(f"[INFO] Checks completed. Alerts sent: {self.stats['alerts_sent']}")

    def close(self):
        """Cerrar conexión."""
        if self.cluster:
            self.cluster.shutdown()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Alert on critical errors in Cassandra logs'
    )
    parser.add_argument(
        '--contact-points',
        type=str,
        default='127.0.0.1',
        help='Cassandra contact points (comma-separated)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9042,
        help='Cassandra port (default: 9042)'
    )
    parser.add_argument(
        '--keyspace',
        type=str,
        default='logging',
        help='Keyspace (default: logging)'
    )
    parser.add_argument(
        '--email',
        type=str,
        help='Email for alerts'
    )
    parser.add_argument(
        '--slack-webhook',
        type=str,
        help='Slack webhook URL'
    )
    parser.add_argument(
        '--alert-log',
        type=str,
        default='/var/log/iact/log_alerts.log',
        help='Path to alert log file'
    )

    args = parser.parse_args()

    if not CASSANDRA_AVAILABLE:
        print("[ERROR] cassandra-driver not installed")
        print("Install with: pip install cassandra-driver")
        return 1

    # Parse contact points
    contact_points = [ip.strip() for ip in args.contact_points.split(',')]

    # Alert manager
    manager = AlertManager(
        contact_points=contact_points,
        port=args.port,
        keyspace=args.keyspace,
        email=args.email,
        slack_webhook=args.slack_webhook,
        alert_log=args.alert_log
    )

    try:
        manager.connect()
        manager.run_checks()
        return 0
    except Exception as e:
        print(f"[ERROR] Alert check failed: {e}")
        return 1
    finally:
        manager.close()


if __name__ == '__main__':
    sys.exit(main())
