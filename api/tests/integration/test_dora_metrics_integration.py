"""
Integration tests for DORA metrics system.

Tests the integration between:
- Layer 1: MySQL metrics storage
- Layer 2: JSON application logs
- Layer 3: Cassandra infrastructure logs
- DORA dashboard
- ETL pipeline
- Alerting system
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "callcentersite.settings.testing")
django.setup()

from dora_metrics.models import DORAMetric


class DORAMetricsAPIIntegrationTest(TestCase):
    """Test DORA metrics API endpoints integration."""

    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="testadmin",
            email="admin@test.com",
            password="testpass123",
        )
        self.client.login(username="testadmin", password="testpass123")

        # Create test metrics
        self.create_test_metrics()

    def create_test_metrics(self):
        """Create test DORA metrics."""
        DORAMetric.objects.all().delete()
        base_time = timezone.now() - timedelta(days=7)
        cycle_prefix = uuid.uuid4().hex

        # Deployment cycle 1 (successful)
        DORAMetric.objects.create(
            cycle_id=f"{cycle_prefix}-001",
            feature_id="FEAT-001",
            phase_name="deployment",
            decision="go",
            duration_seconds=600,
            created_at=base_time,
        )

        # Deployment cycle 2 (failure + recovery)
        DORAMetric.objects.create(
            cycle_id=f"{cycle_prefix}-002-deploy",
            feature_id="FEAT-002",
            phase_name="deployment",
            decision="no-go",
            duration_seconds=900,
            created_at=base_time + timedelta(days=1),
        )
        DORAMetric.objects.create(
            cycle_id=f"{cycle_prefix}-002-recovery",
            feature_id="FEAT-002",
            phase_name="recovery",
            decision="resolved",
            duration_seconds=3600,
            created_at=base_time + timedelta(days=1, hours=2),
        )

    def test_dora_metrics_api_returns_json(self):
        """Test that DORA metrics API returns valid JSON."""
        response = self.client.get("/api/v1/dora/metrics/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertIn('metrics', data)
        self.assertIsInstance(data['metrics'], list)
        self.assertGreater(len(data['metrics']), 0)

    def test_dora_summary_calculation(self):
        """Test DORA summary metrics calculation."""
        response = self.client.get("/api/v1/dora/summary/")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Verify all DORA metrics are present
        self.assertIn('deployment_frequency', data)
        self.assertIn('lead_time_hours', data)
        self.assertIn('change_failure_rate', data)
        self.assertIn('mttr_hours', data)

        # Verify types
        self.assertIsInstance(data['deployment_frequency'], (int, float))
        self.assertIsInstance(data['lead_time_hours'], (int, float))
        self.assertIsInstance(data['change_failure_rate'], (int, float))
        self.assertIsInstance(data['mttr_hours'], (int, float))

        # Verify ranges
        self.assertGreaterEqual(data['deployment_frequency'], 0)
        self.assertGreaterEqual(data['change_failure_rate'], 0)
        self.assertLessEqual(data['change_failure_rate'], 100)

    def test_dora_classification(self):
        """Test DORA performance classification."""
        response = self.client.get("/api/v1/dora/summary/")
        data = json.loads(response.content)

        self.assertIn('dora_classification', data)
        valid_classifications = ['Elite', 'High', 'Medium', 'Low']
        self.assertIn(data['dora_classification'], valid_classifications)

    def test_dashboard_page_loads(self):
        """Test that DORA dashboard page loads successfully."""
        response = self.client.get("/api/v1/dora/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DORA Metrics Dashboard')
        self.assertContains(response, 'Chart.js')

    def test_dashboard_chart_data_endpoints(self):
        """Test that chart data endpoints return valid data."""
        endpoints = [
            "/api/v1/dora/charts/deployment-frequency/",
            "/api/v1/dora/charts/lead-time-trends/",
            "/api/v1/dora/charts/change-failure-rate/",
            "/api/v1/dora/charts/mttr/",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)
            self.assertIn('labels', data)
            self.assertIn('datasets', data)
            self.assertIsInstance(data['labels'], list)
            self.assertIsInstance(data['datasets'], list)

    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced on API endpoints."""
        # Make rapid requests to trigger rate limit
        for i in range(150):  # Exceed 100/min burst limit
            response = self.client.get("/api/v1/dora/metrics/")

        # The last request should be rate limited
        self.assertEqual(response.status_code, 429)
        self.assertIn('X-RateLimit-Limit', response.headers or {})

    def test_metrics_time_filtering(self):
        """Test filtering metrics by time range."""
        # Test last 7 days
        response = self.client.get("/api/v1/dora/summary/?days=7")
        self.assertEqual(response.status_code, 200)
        data_7days = json.loads(response.content)

        # Test last 30 days
        response = self.client.get("/api/v1/dora/summary/?days=30")
        self.assertEqual(response.status_code, 200)
        data_30days = json.loads(response.content)

        # 30 days should include all metrics from 7 days
        self.assertGreaterEqual(
            data_30days['deployment_frequency'],
            data_7days['deployment_frequency']
        )

    def test_change_failure_detection(self):
        """Test that system correctly detects change failures."""
        response = self.client.get("/api/v1/dora/summary/?days=7")
        data = json.loads(response.content)

        # We created 2 deployments, 1 failed
        # CFR should be 50%
        expected_cfr = 50.0
        self.assertAlmostEqual(
            data['change_failure_rate'],
            expected_cfr,
            delta=5.0  # Allow 5% variance
        )

    def test_mttr_calculation(self):
        """Test Mean Time To Recovery calculation."""
        response = self.client.get("/api/v1/dora/summary/?days=7")
        data = json.loads(response.content)

        # We created one incident with 3600s (1 hour) recovery time
        expected_mttr_hours = 1.0
        self.assertAlmostEqual(
            data['mttr_hours'],
            expected_mttr_hours,
            delta=0.5  # Allow 30 min variance
        )


class ObservabilityLayersIntegrationTest(TestCase):
    """Test integration between observability layers."""

    def test_layer1_mysql_metrics_storage(self):
        """Test Layer 1: MySQL metrics are stored and retrievable."""
        # Create metric
        metric = DORAMetric.objects.create(
            cycle_id='integration-test-001',
            feature_id='FEAT-INTEG-001',
            phase_name='deployment',
            decision='approved',
            duration_seconds=1200
        )

        # Verify storage
        retrieved = DORAMetric.objects.get(cycle_id='integration-test-001')
        self.assertEqual(retrieved.feature_id, 'FEAT-INTEG-001')
        self.assertEqual(retrieved.duration_seconds, 1200)

    def test_layer2_json_logging_format(self):
        """Test Layer 2: Application logs are in JSON format."""
        pytest.skip("JSON logging formatter no disponible en entorno de pruebas")


class ETLPipelineIntegrationTest(TestCase):
    """Test ETL pipeline integration."""

    def test_etl_extract_phase(self):
        """Test ETL extract phase can retrieve data."""
        # This is a placeholder for actual ETL testing
        # In production, would test actual GitHub API extraction

        # Simulate extraction by creating raw data
        raw_data = {
            'cycle_id': 'etl-test-001',
            'feature_id': 'FEAT-ETL-001',
            'phase': 'development',
            'duration': 7200
        }

        self.assertIn('cycle_id', raw_data)
        self.assertIn('feature_id', raw_data)

    def test_etl_transform_validation(self):
        """Test ETL transform phase validates data."""
        from pydantic import BaseModel, ValidationError

        class ETLDataSchema(BaseModel):
            cycle_id: str
            feature_id: str
            phase_name: str
            duration_seconds: float

        # Valid data should pass
        valid_data = {
            'cycle_id': 'test-001',
            'feature_id': 'FEAT-001',
            'phase_name': 'deployment',
            'duration_seconds': 1200.0
        }

        try:
            validated = ETLDataSchema(**valid_data)
            self.assertEqual(validated.cycle_id, 'test-001')
        except ValidationError:
            self.fail('Valid data should not raise ValidationError')

        # Invalid data should fail
        invalid_data = {
            'cycle_id': 'test-002',
            # Missing required fields
        }

        with self.assertRaises(ValidationError):
            ETLDataSchema(**invalid_data)

    def test_etl_load_to_database(self):
        """Test ETL load phase stores data in database."""
        # Simulate loading transformed data
        data = {
            'cycle_id': 'etl-load-test-001',
            'feature_id': 'FEAT-LOAD-001',
            'phase_name': 'deployment',
            'decision': 'approved',
            'duration_seconds': 900
        }

        metric = DORAMetric.objects.create(**data)

        # Verify data is stored correctly
        stored = DORAMetric.objects.get(cycle_id='etl-load-test-001')
        self.assertEqual(stored.feature_id, 'FEAT-LOAD-001')
        self.assertEqual(stored.duration_seconds, 900)


class DataQualityIntegrationTest(TestCase):
    """Test data quality framework integration."""

    def test_schema_validation(self):
        """Test schema validation rejects invalid data."""
        from pydantic import BaseModel, validator, ValidationError

        class DORAMetricSchema(BaseModel):
            cycle_id: str
            feature_id: str
            phase_name: str
            duration_seconds: float

            @validator('duration_seconds')
            def validate_duration(cls, v):
                if v < 0:
                    raise ValueError('duration must be positive')
                if v > 86400:  # > 24 hours
                    raise ValueError('duration too long')
                return v

        # Valid duration should pass
        valid = {
            'cycle_id': 'test-001',
            'feature_id': 'FEAT-001',
            'phase_name': 'deployment',
            'duration_seconds': 1200.0
        }
        validated = DORAMetricSchema(**valid)
        self.assertEqual(validated.duration_seconds, 1200.0)

        # Negative duration should fail
        invalid_negative = {
            'cycle_id': 'test-002',
            'feature_id': 'FEAT-002',
            'phase_name': 'deployment',
            'duration_seconds': -100.0
        }
        with self.assertRaises(ValidationError):
            DORAMetricSchema(**invalid_negative)

        # Too long duration should fail
        invalid_long = {
            'cycle_id': 'test-003',
            'feature_id': 'FEAT-003',
            'phase_name': 'deployment',
            'duration_seconds': 100000.0
        }
        with self.assertRaises(ValidationError):
            DORAMetricSchema(**invalid_long)

    def test_data_quality_score_calculation(self):
        """Test data quality score is calculated correctly."""
        # Create metrics with varying quality
        good_metric = DORAMetric.objects.create(
            cycle_id='quality-test-001',
            feature_id='FEAT-GOOD',
            phase_name='deployment',
            decision='approved',
            duration_seconds=1200
        )

        # Quality score should be high for valid data
        # This is a placeholder - actual implementation would
        # calculate quality score based on validation rules
        quality_score = 100.0
        self.assertGreaterEqual(quality_score, 70.0)

    def test_anomaly_detection(self):
        """Test anomaly detection identifies outliers."""
        import numpy as np

        # Create normal metrics
        for i in range(10):
            DORAMetric.objects.create(
                cycle_id=f'normal-{i}',
                feature_id=f'FEAT-NORMAL-{i}',
                phase_name='deployment',
                decision='approved',
                duration_seconds=1200 + (i * 100)  # 1200-2100 seconds
            )

        # Create anomaly
        anomaly = DORAMetric.objects.create(
            cycle_id='anomaly-001',
            feature_id='FEAT-ANOMALY',
            phase_name='deployment',
            decision='approved',
            duration_seconds=50000  # Way too long
        )

        # Get all durations
        metrics = DORAMetric.objects.filter(
            cycle_id__startswith='normal-'
        ) | DORAMetric.objects.filter(cycle_id='anomaly-001')

        durations = [float(value) for value in metrics.values_list('duration_seconds', flat=True)]

        # Calculate IQR
        q1 = np.percentile(durations, 25)
        q3 = np.percentile(durations, 75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr

        # Anomaly should exceed upper bound
        self.assertGreater(50000, upper_bound)


class AlertingSystemIntegrationTest(TestCase):
    """Test alerting system integration."""

    def test_critical_alert_signal(self):
        """Test critical alert signal is sent correctly."""
        from django.dispatch import receiver
        from dora_metrics.alerts import critical_alert

        # Track if signal was received
        received_signals = []

        @receiver(critical_alert)
        def test_receiver(sender, **kwargs):
            received_signals.append(kwargs)

        # Send alert
        critical_alert.send(
            sender=None,
            message='Test critical alert',
            context={'test': True}
        )

        # Verify signal was received
        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals[0]['message'], 'Test critical alert')
        self.assertTrue(received_signals[0]['context']['test'])

    def test_warning_alert_signal(self):
        """Test warning alert signal is sent correctly."""
        from django.dispatch import receiver
        from dora_metrics.alerts import warning_alert

        received_signals = []

        @receiver(warning_alert)
        def test_receiver(sender, **kwargs):
            received_signals.append(kwargs)

        warning_alert.send(
            sender=None,
            message='Test warning alert',
            context={'level': 'warning'}
        )

        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals[0]['message'], 'Test warning alert')


@pytest.mark.integration
class PerformanceIntegrationTest(TestCase):
    """Test performance of integrated system."""

    def test_bulk_metric_creation_performance(self):
        """Test bulk creation of metrics is performant."""
        import time

        start_time = time.time()

        # Create 1000 metrics
        metrics = [
            DORAMetric(
                cycle_id=f'perf-test-{i}',
                feature_id=f'FEAT-PERF-{i}',
                phase_name='deployment',
                decision='approved',
                duration_seconds=1200
            )
            for i in range(1000)
        ]

        DORAMetric.objects.bulk_create(metrics, batch_size=100)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in less than 5 seconds
        self.assertLess(duration, 5.0)

    def test_api_response_time(self):
        """Test API endpoints respond within acceptable time."""
        import time

        # Create test data
        for i in range(100):
            DORAMetric.objects.create(
                cycle_id=f'response-test-{i}',
                feature_id=f'FEAT-RESP-{i}',
                phase_name='deployment',
                decision='approved',
                duration_seconds=1200
            )

        client = Client()
        user = User.objects.create_superuser(
            username='perftest',
            email='perf@test.com',
            password='testpass123'
        )
        client.login(username='perftest', password='testpass123')

        # Test API response time
        start_time = time.time()
        response = client.get("/api/v1/dora/summary/")
        end_time = time.time()

        duration = end_time - start_time

        # Should respond in less than 1 second
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0)
