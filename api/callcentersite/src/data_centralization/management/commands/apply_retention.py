"""
Management command to apply retention policies.

TASK-011: Data Centralization Layer
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    """Apply retention policies to data."""

    help = 'Apply retention policies to datos antiguos'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        """Execute command."""
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('Applying retention policies...'))
        self.stdout.write('')

        # Retention policies:
        # - Logs: 90 dias (automatico en Cassandra via TTL)
        # - Metrics: Permanente (NO delete)
        # - Health checks: 30 dias (future implementation)

        self.stdout.write('Retention policies configured:')
        self.stdout.write('  - DORA Metrics (MySQL): PERMANENT (no deletion)')
        self.stdout.write('  - Application Logs (Cassandra): 90 days TTL (automatic)')
        self.stdout.write('  - Health Checks: 30 days (pending implementation)')
        self.stdout.write('')

        # Future: Cleanup health checks older than 30 days
        # cutoff = timezone.now() - timedelta(days=30)
        # deleted = HealthCheck.objects.filter(created_at__lt=cutoff).delete()
        # self.stdout.write(f'Deleted {deleted[0]} old health checks')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No actual deletions performed'))
        else:
            self.stdout.write(self.style.SUCCESS('Retention policies applied successfully'))

        self.stdout.write('')
        self.stdout.write('Notes:')
        self.stdout.write('  - DORA metrics are never deleted (historical data)')
        self.stdout.write('  - Cassandra TTL handles log cleanup automatically')
        self.stdout.write('  - Health check cleanup pending implementation')
