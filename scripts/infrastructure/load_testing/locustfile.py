"""
Locust load testing file for IACT DORA Metrics API.

Usage:
    # Install locust first
    pip install locust

    # Run load test
    locust -f locustfile.py --host=http://localhost:8000

    # Or run headless
    locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
"""

from locust import HttpUser, task, between, constant
import random
import json


class DORAMetricsAPIUser(HttpUser):
    """
    Simulated user for DORA Metrics API load testing.

    Simulates typical API usage patterns:
    - Reading metrics
    - Querying dashboard data
    - Accessing data catalog
    - Checking ecosystem health
    - Running analytics
    """

    # Wait time between requests (seconds)
    wait_time = between(1, 3)  # Random wait 1-3 seconds

    # Authentication (if required)
    # headers = {"Authorization": "Token YOUR_TOKEN_HERE"}

    def on_start(self):
        """Called when a simulated user starts."""
        self.client.verify = False  # Disable SSL verification for local testing

    @task(10)
    def get_dora_summary(self):
        """
        Most common task: Get DORA metrics summary.
        Weight: 10 (10% of requests)
        """
        params = {"days": random.choice([7, 30, 90])}
        response = self.client.get(
            "/api/dora/metrics/",
            params=params,
            name="/api/dora/metrics/ [summary]"
        )

        if response.status_code == 200:
            data = response.json()
            # Validate response
            assert "metrics" in data or "period_days" in data

    @task(5)
    def get_dashboard(self):
        """
        Load DORA dashboard page.
        Weight: 5 (5% of requests)
        """
        params = {"days": random.choice([7, 30])}
        self.client.get(
            "/api/dora/dashboard/",
            params=params,
            name="/api/dora/dashboard/"
        )

    @task(3)
    def get_deployment_frequency_chart(self):
        """
        Get deployment frequency chart data.
        Weight: 3 (3% of requests)
        """
        params = {"days": random.choice([30, 90])}
        self.client.get(
            "/api/dora/charts/deployment-frequency/",
            params=params,
            name="/api/dora/charts/deployment-frequency/"
        )

    @task(3)
    def get_lead_time_chart(self):
        """
        Get lead time trends chart data.
        Weight: 3 (3% of requests)
        """
        params = {"days": random.choice([30, 90])}
        self.client.get(
            "/api/dora/charts/lead-time-trends/",
            params=params,
            name="/api/dora/charts/lead-time-trends/"
        )

    @task(2)
    def get_data_catalog(self):
        """
        Access data catalog (AI Capability 6).
        Weight: 2 (2% of requests)
        """
        response = self.client.get(
            "/api/dora/data-catalog/",
            name="/api/dora/data-catalog/"
        )

        if response.status_code == 200:
            data = response.json()
            assert "catalog_version" in data
            assert "datasets" in data

    @task(2)
    def query_dora_metrics_catalog(self):
        """
        Query DORA metrics via data catalog.
        Weight: 2 (2% of requests)
        """
        params = {
            "days": random.choice([7, 30]),
            "phase_name": random.choice(["deployment", "testing", None])
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        self.client.get(
            "/api/dora/data-catalog/dora-metrics/",
            params=params,
            name="/api/dora/data-catalog/dora-metrics/"
        )

    @task(1)
    def check_ecosystem_health(self):
        """
        Check ecosystem health (AI Capability 7).
        Weight: 1 (1% of requests)
        """
        response = self.client.get(
            "/api/dora/ecosystem/health/",
            name="/api/dora/ecosystem/health/"
        )

        if response.status_code == 200:
            data = response.json()
            assert "overall_health_score" in data
            assert "status" in data

    @task(1)
    def get_data_quality(self):
        """
        Get data quality assessment.
        Weight: 1 (1% of requests)
        """
        params = {"days": random.choice([30, 90])}
        response = self.client.get(
            "/api/dora/ecosystem/quality/",
            params=params,
            name="/api/dora/ecosystem/quality/"
        )

        if response.status_code == 200:
            data = response.json()
            assert "overall_score" in data
            assert "quality_dimensions" in data

    @task(2)
    def get_trend_analysis(self):
        """
        Get trend analysis (Advanced Analytics).
        Weight: 2 (2% of requests)
        """
        endpoint = random.choice([
            "/api/dora/analytics/trends/deployment-frequency/",
            "/api/dora/analytics/trends/lead-time/"
        ])
        params = {"days": random.choice([60, 90])}

        self.client.get(
            endpoint,
            params=params,
            name=endpoint
        )

    @task(1)
    def get_comparative_analytics(self):
        """
        Get period-over-period comparison.
        Weight: 1 (1% of requests)
        """
        params = {
            "current_days": 30,
            "previous_days": 30
        }
        self.client.get(
            "/api/dora/analytics/comparative/period-over-period/",
            params=params,
            name="/api/dora/analytics/comparative/period-over-period/"
        )

    @task(1)
    def get_anomaly_detection(self):
        """
        Get anomaly detection results.
        Weight: 1 (1% of requests)
        """
        params = {"days": random.choice([30, 60])}
        self.client.get(
            "/api/dora/analytics/anomalies/",
            params=params,
            name="/api/dora/analytics/anomalies/"
        )


class HighVolumeUser(HttpUser):
    """
    High volume user simulating intensive API usage.

    Use for stress testing.
    """

    wait_time = constant(0.5)  # Only 0.5s wait time

    def on_start(self):
        self.client.verify = False

    @task
    def rapid_fire_requests(self):
        """Make rapid requests to test system under heavy load."""
        endpoints = [
            "/api/dora/metrics/",
            "/api/dora/charts/deployment-frequency/",
            "/api/dora/data-catalog/",
            "/api/dora/ecosystem/health/",
        ]

        endpoint = random.choice(endpoints)
        self.client.get(endpoint, params={"days": 30})


class WriteOperationUser(HttpUser):
    """
    User performing write operations.

    Tests POST endpoints (metric creation).
    """

    wait_time = between(5, 10)  # Slower, as writes are less frequent

    def on_start(self):
        self.client.verify = False

    @task
    def create_metric(self):
        """Create a new DORA metric."""
        data = {
            "cycle_id": f"load-test-{random.randint(1, 1000)}",
            "feature_id": f"FEAT-{random.randint(100, 999)}",
            "phase_name": random.choice(["development", "testing", "deployment"]),
            "decision": random.choice(["approved", "rejected"]),
            "duration_seconds": random.randint(300, 7200),
            "metadata": {
                "test": "load_test",
                "timestamp": "2025-11-07"
            }
        }

        self.client.post(
            "/api/dora/metrics/create/",
            json=data,
            name="/api/dora/metrics/create/"
        )
