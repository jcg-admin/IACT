"""Servicios del dashboard."""

from __future__ import annotations

from typing import Dict, List

from django.utils import timezone

from .widgets import WIDGET_REGISTRY, Widget


class DashboardService:
    """Orquesta la construcción de respuestas para el dashboard."""

    @staticmethod
    def overview() -> Dict[str, object]:
        now = timezone.now()
        return {
            "last_update": now.isoformat(),
            "widgets": [widget.__dict__ for widget in DashboardService.available_widgets()],
        }

    @staticmethod
    def available_widgets() -> List[Widget]:
        return list(WIDGET_REGISTRY.values())
