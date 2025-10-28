"""Decoradores de auditoría."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from .services import AuditService


def audit_action(action: str, resource: str | None = None) -> Callable:
    """Decora vistas o métodos para registrar auditoría."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                response = func(self, request, *args, **kwargs)
                AuditService.log(
                    user=getattr(request, "user", None),
                    action=action,
                    resource=resource or getattr(self, "basename", "resource"),
                    resource_id=kwargs.get("pk"),
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    result="success",
                    metadata={"method": request.method},
                )
                return response
            except Exception as error:  # pragma: no cover - re lanza
                AuditService.log(
                    user=getattr(request, "user", None),
                    action=action,
                    resource=resource or "system",
                    resource_id=kwargs.get("pk"),
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    result="failure",
                    error_message=str(error),
                )
                raise

        return wrapper

    return decorator
