"""REST views for centralized data access using DRF."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    DataQueryService,
    HealthQueryStrategy,
    InvalidQueryTypeError,
    LogsQueryStrategy,
    MetricsQueryStrategy,
    QueryExecutionError,
)

DEFAULT_LOG_PATH = Path("/var/log/iact/app.json.log")
DEFAULT_HEALTH_SCRIPT = Path("/home/user/IACT---project/scripts/health_check.sh")


def build_default_service() -> DataQueryService:
    """Create the service with default strategies."""

    return DataQueryService(
        strategies=[
            MetricsQueryStrategy(dataset=[]),
            LogsQueryStrategy(log_path=DEFAULT_LOG_PATH),
            HealthQueryStrategy(script_path=DEFAULT_HEALTH_SCRIPT),
        ]
    )


class DataQueryView(APIView):
    """Provides unified access to metrics, logs and health data."""

    permission_classes = [IsAuthenticated]

    def get(self, request):  # type: ignore[override]
        query_type = request.query_params.get("type")
        service = build_default_service()

        if not query_type:
            return Response(
                {
                    "error": "Missing required parameter: type",
                    "valid_types": service.valid_types,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            days = int(request.query_params.get("days", 7))
            limit = int(request.query_params.get("limit", 1000))
        except (TypeError, ValueError):
            return Response(
                {"error": "Parameters days and limit must be integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if days < 0 or limit < 1:
            return Response(
                {"error": "days must be >= 0 and limit must be >= 1"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload: Dict[str, Any] = service.run(query_type=query_type, days=days, limit=limit)
        except InvalidQueryTypeError:
            return Response(
                {
                    "error": f"Invalid query type: {query_type}",
                    "valid_types": service.valid_types,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except QueryExecutionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(payload)
