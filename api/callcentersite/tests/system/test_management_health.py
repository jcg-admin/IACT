"""Smoke tests for Django management health commands."""

from django.core.management import call_command
from django.test import SimpleTestCase


class ManagementHealthTests(SimpleTestCase):
    """Ensure critical management commands run without raising errors."""

    def test_system_check_succeeds(self) -> None:
        """Running ``manage.py check`` should complete without issues."""
        call_command("check")
