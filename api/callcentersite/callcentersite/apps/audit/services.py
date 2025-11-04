"""Servicios relacionados con la auditoría."""

from __future__ import annotations

from typing import Any, Dict

from .models import AuditLog


class AuditService:
    """Servicio centralizado de auditoría."""

    @staticmethod
    def log(
        *,
        user,
        action: str,
        resource: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        result: str = "success",
        error_message: str | None = None,
        metadata: Dict[str, Any] | None = None,
        old_values: Dict[str, Any] | None = None,
        new_values: Dict[str, Any] | None = None,
    ) -> None:
        AuditLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            resource=resource or "system",
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            error_message=error_message,
            metadata=metadata or {},
            old_values=old_values,
            new_values=new_values,
        )
