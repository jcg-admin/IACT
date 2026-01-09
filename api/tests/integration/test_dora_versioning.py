"""Routing tests for DORA API versioning."""

from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class DoraVersioningRoutingTest(SimpleTestCase):
    """Validate DORA endpoints follow documented versioned scheme."""

    def test_versioned_endpoint_is_available(self):
        match = resolve("/api/v1/dora/metrics/")

        self.assertEqual(match.func.__name__, "dora_metrics_summary")

    def test_unversioned_endpoint_is_not_routed(self):
        with self.assertRaises(Resolver404):
            resolve("/api/dora/metrics/")
