"""
Alerting System - Self-hosted
NO usa Prometheus/Alertmanager (RNF-002 compliant)

Sistema de alertas basado en Django signals y notificaciones.
"""

from django.dispatch import Signal, receiver
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SIGNALS
# ============================================================================

# Signal para alertas criticas
critical_alert = Signal()

# Signal para alertas de warning
warning_alert = Signal()

# ============================================================================
# ALERT HANDLERS
# ============================================================================

@receiver(critical_alert)
def handle_critical_alert(sender, **kwargs):
    """Handle CRITICAL alerts."""
    message = kwargs.get('message', 'Unknown critical alert')
    context = kwargs.get('context', {})

    logger.critical(f"CRITICAL ALERT: {message} - Context: {context}")

    # TODO: Send notification (email, slack, etc)
    # For now, just log
    # send_notification(level='CRITICAL', message=message, context=context)


@receiver(warning_alert)
def handle_warning_alert(sender, **kwargs):
    """Handle WARNING alerts."""
    message = kwargs.get('message', 'Unknown warning')
    context = kwargs.get('context', {})

    logger.warning(f"WARNING ALERT: {message} - Context: {context}")


# ============================================================================
# ALERT TRIGGERS
# ============================================================================

def check_dora_metrics_health():
    """Check DORA metrics and trigger alerts if needed."""
    from .models import DORAMetric
    from datetime import timedelta
    from django.utils import timezone

    cutoff = timezone.now() - timedelta(days=7)
    metrics = DORAMetric.objects.filter(created_at__gte=cutoff)

    # Check deployment frequency
    deployment_count = metrics.filter(phase_name='deployment').count()
    if deployment_count == 0:
        critical_alert.send(
            sender=None,
            message="No deployments in last 7 days",
            context={'deployment_count': 0}
        )

    # Check change failure rate
    testing = metrics.filter(phase_name='testing')
    failed = testing.filter(decision='no-go').count()
    total = testing.count()
    if total > 0:
        cfr = (failed / total) * 100
        if cfr > 20:  # >20% failure rate
            warning_alert.send(
                sender=None,
                message=f"High change failure rate: {cfr:.1f}%",
                context={'cfr': cfr, 'failed': failed, 'total': total}
            )


def check_system_health():
    """Check system health and trigger alerts."""
    from django.contrib.sessions.models import Session

    # Check session table size
    session_count = Session.objects.count()
    if session_count > 100000:
        critical_alert.send(
            sender=None,
            message=f"Session table too large: {session_count} sessions",
            context={'session_count': session_count}
        )
    elif session_count > 50000:
        warning_alert.send(
            sender=None,
            message=f"Session table growing: {session_count} sessions",
            context={'session_count': session_count}
        )
