"""Servicios de autenticación."""

from __future__ import annotations

from datetime import timedelta
from django.utils import timezone

from .models import LoginAttempt


class LoginAttemptService:
    """Gestiona intentos de inicio de sesión."""

    @staticmethod
    def register_attempt(
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        reason: str | None = None,
    ) -> None:
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            reason=reason,
        )

    @staticmethod
    def count_recent_failures(username: str, window: timedelta) -> int:
        threshold = timezone.now() - window
        return LoginAttempt.objects.filter(
            username=username, success=False, timestamp__gte=threshold
        ).count()
