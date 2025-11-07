"""
Views para unified query API.

TASK-011: Data Centralization Layer
Query unificada para metrics (MySQL), logs (Cassandra future), health checks.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def unified_query(request):
    """
    GET /api/data/query - Query unificada para metrics, logs, health.

    Query parameters:
    - type: metrics|logs|health (required)
    - days: number of days to query (default: 7)
    - limit: max results (default: 1000)

    Returns:
        JsonResponse with data

    Examples:
        GET /api/data/query?type=metrics&days=30
        GET /api/data/query?type=logs&days=7&limit=500
        GET /api/data/query?type=health
    """
    query_type = request.GET.get('type')
    days = int(request.GET.get('days', 7))
    limit = int(request.GET.get('limit', 1000))

    if not query_type:
        return JsonResponse({
            'error': 'Missing required parameter: type',
            'valid_types': ['metrics', 'logs', 'health']
        }, status=400)

    if query_type == 'metrics':
        return _query_metrics(days, limit)
    elif query_type == 'logs':
        return _query_logs(days, limit)
    elif query_type == 'health':
        return _query_health()
    else:
        return JsonResponse({
            'error': f'Invalid query type: {query_type}',
            'valid_types': ['metrics', 'logs', 'health']
        }, status=400)


def _query_metrics(days: int, limit: int) -> JsonResponse:
    """
    Query DORA metrics from MySQL.

    Args:
        days: Number of days to query
        limit: Max results

    Returns:
        JsonResponse with metrics data
    """
    from dora_metrics.models import DORAMetric

    cutoff = timezone.now() - timedelta(days=days)
    metrics = DORAMetric.objects.filter(
        created_at__gte=cutoff
    ).order_by('-created_at')[:limit]

    data = []
    for metric in metrics:
        data.append({
            'id': metric.id,
            'cycle_id': metric.cycle_id,
            'feature_id': metric.feature_id,
            'phase_name': metric.phase_name,
            'decision': metric.decision,
            'duration_seconds': float(metric.duration_seconds),
            'metadata': metric.metadata,
            'created_at': metric.created_at.isoformat(),
        })

    return JsonResponse({
        'query_type': 'metrics',
        'source': 'MySQL (dora_metrics)',
        'days': days,
        'count': len(data),
        'data': data
    })


def _query_logs(days: int, limit: int) -> JsonResponse:
    """
    Query application logs.

    NOTE: Cassandra integration pending (Q1 2026).
    Currently reads from JSON log files.

    Args:
        days: Number of days to query
        limit: Max results

    Returns:
        JsonResponse with logs data
    """
    # Future: Query from Cassandra
    # from cassandra.cluster import Cluster
    # cluster = Cluster(['cassandra-1'])
    # session = cluster.connect('logging')
    # rows = session.execute(...)

    # Current: Read from JSON log file
    log_file = Path('/var/log/iact/app.json.log')

    if not log_file.exists():
        return JsonResponse({
            'query_type': 'logs',
            'source': 'JSON log file (Cassandra pending)',
            'days': days,
            'count': 0,
            'data': [],
            'note': 'Log file not found. Cassandra integration pending Q1 2026.'
        })

    data = []
    cutoff = datetime.utcnow() - timedelta(days=days)

    with log_file.open('r') as f:
        for line in f:
            if len(data) >= limit:
                break

            try:
                log_entry = json.loads(line.strip())

                # Parse timestamp
                timestamp_str = log_entry.get('timestamp', '')
                if timestamp_str:
                    log_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if log_timestamp.replace(tzinfo=None) >= cutoff:
                        data.append(log_entry)

            except (json.JSONDecodeError, ValueError):
                continue

    return JsonResponse({
        'query_type': 'logs',
        'source': 'JSON log file (Cassandra integration pending)',
        'days': days,
        'count': len(data),
        'data': data,
        'note': 'Currently reading from JSON log file. Cassandra integration planned for Q1 2026.'
    })


def _query_health() -> JsonResponse:
    """
    Query system health checks.

    Returns:
        JsonResponse with health data
    """
    health_script = Path('/home/user/IACT---project/scripts/health_check.sh')

    if not health_script.exists():
        return JsonResponse({
            'query_type': 'health',
            'source': 'health_check.sh',
            'error': 'Health check script not found'
        }, status=500)

    try:
        result = subprocess.run(
            [str(health_script), '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            try:
                health_data = json.loads(result.stdout)
                return JsonResponse({
                    'query_type': 'health',
                    'source': 'health_check.sh',
                    'data': health_data
                })
            except json.JSONDecodeError:
                # Fallback: return as text
                return JsonResponse({
                    'query_type': 'health',
                    'source': 'health_check.sh',
                    'data': {
                        'status': 'ok' if result.returncode == 0 else 'error',
                        'output': result.stdout
                    }
                })
        else:
            return JsonResponse({
                'query_type': 'health',
                'source': 'health_check.sh',
                'error': 'Health check failed',
                'exit_code': result.returncode,
                'stderr': result.stderr
            }, status=500)

    except subprocess.TimeoutExpired:
        return JsonResponse({
            'query_type': 'health',
            'source': 'health_check.sh',
            'error': 'Health check timeout (>30s)'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'query_type': 'health',
            'source': 'health_check.sh',
            'error': f'Unexpected error: {str(e)}'
        }, status=500)
