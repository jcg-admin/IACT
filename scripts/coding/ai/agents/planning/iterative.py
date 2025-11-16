"""
Iterative Planner with Failure Transparency.

Implements RF-012: Iterative Planning and Feedback with Failure Transparency.
Key principle: IMMEDIATE transparency on failures - never hide errors.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .models import Plan, PlanRevision, RevisionStrategy, SubTask, TaskStatus


class FeedbackType(str, Enum):
    """Type of execution feedback."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    TIMEOUT = "timeout"
    RETRY_NEEDED = "retry_needed"


class FailureType(str, Enum):
    """Classification of failures for strategy selection."""

    AGENT_TIMEOUT = "agent_timeout"
    AGENT_ERROR = "agent_error"
    INVALID_INPUT = "invalid_input"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"


@dataclass
class ExecutionFeedback:
    """Feedback from task execution."""

    task_id: str
    feedback_type: FeedbackType
    actual_outputs: Dict
    errors: List[str]
    duration_seconds: float
    cost: float
    suggested_adjustments: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UserNotification:
    """Notification to user about plan execution."""

    severity: str  # ERROR, WARNING, INFO
    task_id: str
    error_summary: str
    recovery_strategy: str
    estimated_delay: str
    logs_url: str
    timestamp: datetime

    def __post_init__(self):
        if not hasattr(self, 'timestamp') or self.timestamp is None:
            self.timestamp = datetime.now()


class NotificationService:
    """Service to send notifications to users."""

    def send(self, notification: Dict) -> None:
        """Send notification (mock implementation for testing)."""
        print(f"[NOTIFICATION] {notification['severity']}: {notification['error_summary']}")


class IterativePlanner:
    """Planner that adapts based on execution feedback."""

    def __init__(self, max_revisions: int = 3):
        """
        Initialize iterative planner.

        Args:
            max_revisions: Maximum number of plan revisions allowed
        """
        self.max_revisions = max_revisions
        self.revisions: List[PlanRevision] = []

    def handle_feedback(
        self, plan: Plan, feedback: ExecutionFeedback
    ) -> Optional[PlanRevision]:
        """
        Handle execution feedback and potentially revise plan.

        Args:
            plan: Current plan
            feedback: Execution feedback

        Returns:
            PlanRevision if plan was revised, None otherwise
        """
        # Check if revision is needed
        if feedback.feedback_type == FeedbackType.SUCCESS:
            # Update confidence upward on success
            plan.confidence_score = min(1.0, plan.confidence_score + 0.05)
            return None

        # Check max revisions
        if len(self.revisions) >= self.max_revisions:
            # Escalate to human
            return self._create_revision(
                plan,
                feedback,
                RevisionStrategy.ESCALATE_TO_HUMAN,
                "Max revisions reached"
            )

        # Classify failure type
        failure_type = self._classify_failure(feedback)

        # Select revision strategy
        strategy = self._select_strategy(failure_type, feedback)

        # Create revision
        revision = self._create_revision(plan, feedback, strategy, feedback.errors[0] if feedback.errors else "Unknown error")

        # Adjust confidence
        plan.confidence_score = max(0.0, plan.confidence_score - 0.15)

        self.revisions.append(revision)
        return revision

    def _classify_failure(self, feedback: ExecutionFeedback) -> FailureType:
        """Classify failure type based on error messages."""
        error_text = " ".join(feedback.errors).lower()

        if "timeout" in error_text:
            return FailureType.AGENT_TIMEOUT
        elif "rate limit" in error_text or "429" in error_text:
            return FailureType.RATE_LIMIT
        elif "invalid" in error_text or "validation" in error_text:
            return FailureType.INVALID_INPUT
        elif "context" in error_text or "information" in error_text:
            return FailureType.INSUFFICIENT_CONTEXT
        elif "error" in error_text:
            return FailureType.AGENT_ERROR
        else:
            return FailureType.UNKNOWN

    def _select_strategy(
        self, failure_type: FailureType, feedback: ExecutionFeedback
    ) -> RevisionStrategy:
        """Select appropriate revision strategy based on failure type."""
        if failure_type == FailureType.AGENT_TIMEOUT:
            return RevisionStrategy.RETRY_DIFFERENT_AGENT
        elif failure_type == FailureType.RATE_LIMIT:
            return RevisionStrategy.ADD_FALLBACK
        elif failure_type == FailureType.INSUFFICIENT_CONTEXT:
            return RevisionStrategy.DECOMPOSE_FURTHER
        elif failure_type == FailureType.INVALID_INPUT:
            return RevisionStrategy.ADJUST_PARAMETERS
        else:
            return RevisionStrategy.RETRY_DIFFERENT_AGENT

    def _create_revision(
        self,
        plan: Plan,
        feedback: ExecutionFeedback,
        strategy: RevisionStrategy,
        reason: str
    ) -> PlanRevision:
        """Create a plan revision."""
        revision_id = f"revision_{int(time.time() * 1000)}"
        new_plan_id = f"{plan.plan_id}_rev{len(self.revisions) + 1}"

        changes_made = self._apply_strategy(plan, feedback, strategy)

        # Calculate confidence delta
        confidence_delta = -0.15 if strategy != RevisionStrategy.ESCALATE_TO_HUMAN else -0.25

        return PlanRevision(
            revision_id=revision_id,
            original_plan_id=plan.plan_id,
            new_plan_id=new_plan_id,
            reason=reason,
            strategy=strategy,
            failed_task_id=feedback.task_id,
            changes_made=changes_made,
            confidence_delta=confidence_delta
        )

    def _apply_strategy(
        self, plan: Plan, feedback: ExecutionFeedback, strategy: RevisionStrategy
    ) -> List[str]:
        """Apply revision strategy and return list of changes."""
        changes = []

        if strategy == RevisionStrategy.RETRY_DIFFERENT_AGENT:
            changes.append(f"Retry task {feedback.task_id} with backup agent")
            # In real implementation, would modify plan.subtasks

        elif strategy == RevisionStrategy.DECOMPOSE_FURTHER:
            changes.append(f"Decompose task {feedback.task_id} into smaller subtasks")

        elif strategy == RevisionStrategy.ADJUST_PARAMETERS:
            changes.append(f"Adjust parameters for task {feedback.task_id}")

        elif strategy == RevisionStrategy.ADD_FALLBACK:
            changes.append(f"Add fallback task after {feedback.task_id}")

        elif strategy == RevisionStrategy.ESCALATE_TO_HUMAN:
            changes.append("Escalate to human for manual intervention")

        return changes


class ExecutionOrchestrator:
    """Orchestrates plan execution with failure handling."""

    def __init__(self):
        """Initialize orchestrator."""
        self.notification_service = NotificationService()
        self.planner = IterativePlanner()

    def handle_task_completion(self, feedback: ExecutionFeedback) -> None:
        """
        Handle task completion (success or failure).

        Args:
            feedback: Execution feedback
        """
        # Detect failure immediately
        start_time = time.time()

        if feedback.feedback_type == FeedbackType.FAILURE:
            # IMMEDIATE TRANSPARENCY: Notify user < 500ms
            self._send_immediate_notification(feedback)

        detection_time = time.time() - start_time

        # Update task status
        # (In real implementation, would update actual plan)

        # Log detection time for monitoring
        if detection_time > 0.1:
            print(f"Warning: Failure detection took {detection_time:.3f}s (target < 100ms)")

    def _send_immediate_notification(self, feedback: ExecutionFeedback) -> None:
        """Send immediate notification to user about failure."""
        # Select recovery strategy
        failure_type = self.planner._classify_failure(feedback)
        strategy = self.planner._select_strategy(failure_type, feedback)

        # Estimate delay
        estimated_delay = self._estimate_recovery_delay(strategy)

        # Create notification
        notification = {
            "severity": "ERROR",
            "task_id": feedback.task_id,
            "error_summary": f"Task failed: {feedback.errors[0] if feedback.errors else 'Unknown error'}",
            "recovery_strategy": self._strategy_to_message(strategy),
            "estimated_delay": estimated_delay,
            "logs_url": f"/logs/task/{feedback.task_id}"
        }

        # Send immediately (< 500ms total)
        self.notification_service.send(notification)

    def _estimate_recovery_delay(self, strategy: RevisionStrategy) -> str:
        """Estimate delay for recovery strategy."""
        if strategy == RevisionStrategy.RETRY_DIFFERENT_AGENT:
            return "2-3 seconds"
        elif strategy == RevisionStrategy.DECOMPOSE_FURTHER:
            return "5-10 seconds"
        elif strategy == RevisionStrategy.ADJUST_PARAMETERS:
            return "1-2 seconds"
        elif strategy == RevisionStrategy.ADD_FALLBACK:
            return "3-5 seconds"
        elif strategy == RevisionStrategy.ESCALATE_TO_HUMAN:
            return "Manual intervention required"
        else:
            return "Unknown"

    def _strategy_to_message(self, strategy: RevisionStrategy) -> str:
        """Convert strategy to user-friendly message."""
        messages = {
            RevisionStrategy.RETRY_DIFFERENT_AGENT: "Retrying with backup agent",
            RevisionStrategy.DECOMPOSE_FURTHER: "Breaking task into smaller steps",
            RevisionStrategy.ADJUST_PARAMETERS: "Adjusting task parameters",
            RevisionStrategy.ADD_FALLBACK: "Trying alternative approach",
            RevisionStrategy.ESCALATE_TO_HUMAN: "Requesting human assistance"
        }
        return messages.get(strategy, "Attempting recovery")
