"""
Security: Threat Detection

Implements RF-017 Threat Detection scenarios.
"""

import re
from enum import Enum
from typing import List


class ThreatLevel(str, Enum):
    """Threat severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ThreatDetector:
    """Detects security threats in user input."""

    INJECTION_PATTERNS = [
        r"ignore (previous|above) instructions",
        r"disregard (all|previous) rules",
        r"new instructions?:",
        r"system.?prompt",
    ]

    def detect_task_injection(self, user_input: str) -> bool:
        """Detect prompt injection attempts."""
        user_input_lower = user_input.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, user_input_lower):
                return True
        return False

    def classify_threat(self, user_input: str) -> ThreatLevel:
        """Classify threat level."""
        if self.detect_task_injection(user_input):
            return ThreatLevel.HIGH
        return ThreatLevel.NONE
