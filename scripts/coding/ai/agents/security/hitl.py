"""
Security: Human-in-the-Loop

Implements RF-017 HITL scenarios.
"""

from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """Risk levels for actions."""
    CRITICAL = "critical"  # 2 approvers
    HIGH = "high"          # 1 approver
    MEDIUM = "medium"      # Quick confirmation
    LOW = "low"            # No approval needed


class HumanInTheLoop:
    """Human-in-the-Loop approval system."""

    HIGH_RISK_ACTIONS = ["transfer_money", "delete_data", "grant_access"]

    def classify_risk(self, action: Any) -> RiskLevel:
        """Classify action risk level."""
        action_type = getattr(action, "type", "unknown")

        if action_type in ["transfer_money", "delete_data"]:
            amount = getattr(action, "amount", 0)
            if amount > 10000:
                return RiskLevel.CRITICAL

        if action_type in self.HIGH_RISK_ACTIONS:
            return RiskLevel.HIGH

        return RiskLevel.LOW

    def requires_approval(self, action: Any) -> bool:
        """Check if action requires approval."""
        risk = self.classify_risk(action)
        return risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]
