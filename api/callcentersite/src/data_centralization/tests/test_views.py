"""Tests for the data_centralization API view."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.urls import path
from django.utils import timezone
from rest_framework.test import APITestCase

from data_centralization.services import (
    DataQueryService,
    HealthQueryStrategy,
    LogsQueryStrategy,
    MetricsQueryStrategy,
)
from data_centralization.views import DataQueryView

urlpatterns = [
    path("api/v1/data/query/", DataQueryView.as_view(), name="data-query"),
]


class DataQueryViewTests(APITestCase):
    """Integration tests for the data query endpoint."""

    endpoint = "/api/v1/data/query/"

    @classmethod
    def setUpClass(cls) -> None:
        cls.override_urls = override_settings(ROOT_URLCONF=__name__)
        cls.override_urls.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.override_urls.disable()
        super().tearDownClass()

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="data-query-user",
            password="strong-pass-123",
            email="data.query@example.com",
        )
        self.client.force_authenticate(user=self.user)

    def _build_service(
        self,
        metrics_dataset: List[dict],
        log_file: Path | None = None,
        health_script: Path | None = None,
        clock=None,
    ) -> DataQueryService:
        """Helper to build a deterministic service for testing."""

        return DataQueryService(
            strategies=[
                MetricsQueryStrategy(dataset=metrics_dataset, clock=clock or timezone.now),
                LogsQueryStrategy(log_path=log_file or Path("/tmp/missing.log")),
                HealthQueryStrategy(
                    script_path=health_script or Path("/tmp/missing.sh"),
                ),
            ]
        )

    def test_returns_error_when_type_is_missing(self):
        """The endpoint should reject requests without a type parameter."""

        response = self.client.get(self.endpoint)

        assert response.status_code == 400
        assert response.data["error"] == "Missing required parameter: type"
        assert "metrics" in response.data["valid_types"]

    def test_returns_error_for_invalid_type(self):
        """The endpoint should return a 400 when query type is invalid."""

        response = self.client.get(self.endpoint, {"type": "unknown"})

        assert response.status_code == 400
        assert "Invalid query type" in response.data["error"]

    def test_requires_authentication(self):
        """Anonymous requests are rejected with 401 to protect sensitive data."""

        anonymous_client = self.client.__class__()
        response = anonymous_client.get(self.endpoint, {"type": "metrics"})

        assert response.status_code == 401

    def test_metrics_query_filters_by_days_and_limit(self):
        """Only recent metric samples are returned according to the filters."""

        fixed_now = timezone.now()
        dataset = [
            {
                "id": 1,
                "metric": "aht",
                "value": 120,
                "created_at": fixed_now - timedelta(days=2),
            },
            {
                "id": 2,
                "metric": "aht",
                "value": 130,
                "created_at": fixed_now - timedelta(days=10),
            },
        ]

        service = self._build_service(metrics_dataset=dataset, clock=lambda: fixed_now)

        with patch("data_centralization.views.build_default_service", return_value=service):
            response = self.client.get(
                self.endpoint,
                {"type": "metrics", "days": 5, "limit": 10},
            )

        assert response.status_code == 200
        assert response.data["query_type"] == "metrics"
        assert response.data["count"] == 1
        assert response.data["data"][0]["id"] == 1

    def test_logs_query_reads_from_json_lines_file(self):
        """Log strategy should parse JSON lines and apply limits."""

        fixed_now = datetime.utcnow()
        with NamedTemporaryFile(mode="w", delete=False) as log_file:
            log_path = Path(log_file.name)
            log_entry = {"message": "ok", "timestamp": fixed_now.isoformat()}
            older_entry = {
                "message": "old",
                "timestamp": (fixed_now - timedelta(days=30)).isoformat(),
            }
            log_file.write(json.dumps(log_entry) + "\n")
            log_file.write(json.dumps(older_entry) + "\n")

        dataset: list[dict] = []
        service = self._build_service(metrics_dataset=dataset, log_file=log_path)

        with patch("data_centralization.views.build_default_service", return_value=service):
            response = self.client.get(
                self.endpoint,
                {"type": "logs", "days": 7, "limit": 5},
            )

        log_path.unlink(missing_ok=True)

        assert response.status_code == 200
        assert response.data["query_type"] == "logs"
        assert response.data["count"] == 1
        assert response.data["data"][0]["message"] == "ok"

    def test_health_query_executes_script_and_returns_json(self):
        """Health strategy should execute the script and return its JSON output."""

        with NamedTemporaryFile(mode="w", delete=False) as script_file:
            script_path = Path(script_file.name)
            script_file.write('#!/bin/sh\nprintf "{\\\"status\\\": \\\"ok\\\"}"\n')

        script_path.chmod(0o755)

        dataset: list[dict] = []
        service = self._build_service(
            metrics_dataset=dataset,
            health_script=script_path,
        )

        with patch("data_centralization.views.build_default_service", return_value=service):
            response = self.client.get(self.endpoint, {"type": "health"})

        script_path.unlink(missing_ok=True)

        assert response.status_code == 200
        assert response.data["query_type"] == "health"
        assert response.data["data"]["status"] == "ok"
