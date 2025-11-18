"""
Security: Audit logging

Implements RF-017 Audit scenarios.
"""

from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel


class AuditLog(BaseModel):
    """Audit log entry."""
    timestamp: datetime
    action: str
    agent_id: str
    user_id: str
    details: Dict[str, Any]


class AuditLogger:
    """Audit logging system."""

    def __init__(self):
        self.logs: List[AuditLog] = []

    def log_action(self, action: str, agent_id: str, user_id: str, details: Dict) -> None:
        """Log an action."""
        log_entry = AuditLog(
            timestamp=datetime.now(),
            action=action,
            agent_id=agent_id,
            user_id=user_id,
            details=details
        )
        self.logs.append(log_entry)

    def get_logs(self, filter_by: str = None) -> List[AuditLog]:
        """Retrieve logs."""
        if filter_by:
            return [log for log in self.logs if filter_by in log.action]
        return self.logs
