"""
Tests for RF-012: Iterative Planning and Feedback with Failure Transparency

Key principle: IMMEDIATE transparency on failures (< 500ms)
"""

import time
from unittest.mock import Mock

from datetime import datetime
import pytest

from scripts.coding.ai.agents.planning.models import Goal, GoalType, Plan, SubTask, TaskStatus
from scripts.coding.ai.agents.planning.iterative import (
    ExecutionFeedback,
    ExecutionOrchestrator,
    FeedbackType,
    FailureType,
    IterativePlanner,
    RevisionStrategy,
)


def create_test_plan() -> Plan:
    """Create a test plan for testing."""
    return Plan(
        plan_id="test_plan_001",
        goal_id="test_goal_001",
        subtasks=[
            SubTask(
                task_id="task_001",
                description="Search flights",
                agent_type="flight_agent",
                dependencies=[],
                expected_outputs=["flights"],
                estimated_duration_seconds=30
            ),
            SubTask(
                task_id="task_002",
                description="Book hotel",
                agent_type="hotel_agent",
                dependencies=["task_001"],
                expected_outputs=["hotel"],
                estimated_duration_seconds=25
            )
        ],
        execution_strategy="sequential",
        estimated_total_duration=55,
        confidence_score=0.85
    )


# ==================================
# Failure Detection and Transparency
# ==================================


def test_detect_task_failure_immediately():
    """RF-012: Escenario 1 - Detect Task Failure Immediately"""
    orchestrator = ExecutionOrchestrator()
    plan = create_test_plan()

    # When - task fails
    start_failure_time = time.time()

    task_failure = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )

    # Trigger failure detection
    orchestrator.handle_task_completion(task_failure)
    detection_time = time.time() - start_failure_time

    # Then - immediate detection (< 100ms)
    assert detection_time < 0.1, f"Detection took {detection_time:.3f}s (should be < 100ms)"

    # Feedback created correctly
    assert task_failure.feedback_type == FeedbackType.FAILURE
    assert "timeout" in str(task_failure.errors).lower()


def test_immediate_user_notification_on_failure():
    """RF-012: Escenario 2 - Immediate User Notification on Failure"""
    orchestrator = ExecutionOrchestrator()
    notification_service = Mock()
    orchestrator.notification_service = notification_service

    # Given - task failure
    task_failure = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )

    # When - handle failure
    start_time = time.time()
    orchestrator.handle_task_completion(task_failure)
    notification_time = time.time() - start_time

    # Then - immediate notification (< 500ms)
    assert notification_time < 0.5, f"Notification took {notification_time:.3f}s"

    # Notification sent
    notification_service.send.assert_called_once()
    call_args = notification_service.send.call_args[0][0]

    assert call_args["severity"] == "ERROR"
    assert call_args["task_id"] == "task_001"
    assert "timeout" in call_args["error_summary"].lower()
    assert "retry" in call_args["recovery_strategy"].lower()


def test_classify_failure_type_for_strategy_selection():
    """RF-012: Escenario 3 - Classify Failure Type for Strategy Selection"""
    planner = IterativePlanner()

    # Test timeout classification
    timeout_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )
    assert planner._classify_failure(timeout_feedback) == FailureType.AGENT_TIMEOUT

    # Test rate limit classification
    rate_limit_feedback = ExecutionFeedback(
        task_id="task_002",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Rate limit exceeded (429)"],
        duration_seconds=5,
        cost=0.0
    )
    assert planner._classify_failure(rate_limit_feedback) == FailureType.RATE_LIMIT

    # Test invalid input classification
    invalid_feedback = ExecutionFeedback(
        task_id="task_003",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Invalid input parameters"],
        duration_seconds=2,
        cost=0.0
    )
    assert planner._classify_failure(invalid_feedback) == FailureType.INVALID_INPUT


# ==================================
# Re-planning Strategies
# ==================================


def test_retry_with_different_agent_strategy():
    """RF-012: Escenario 4 - Retry with Different Agent"""
    planner = IterativePlanner()
    plan = create_test_plan()

    timeout_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout"],
        duration_seconds=10,
        cost=0.0
    )

    # When
    revision = planner.handle_feedback(plan, timeout_feedback)

    # Then
    assert revision is not None
    assert revision.strategy == RevisionStrategy.RETRY_DIFFERENT_AGENT
    assert "backup agent" in " ".join(revision.changes_made).lower()


def test_decompose_further_strategy():
    """RF-012: Escenario 5 - Decompose Further"""
    planner = IterativePlanner()
    plan = create_test_plan()

    context_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Insufficient context to complete task"],
        duration_seconds=5,
        cost=0.0
    )

    # When
    revision = planner.handle_feedback(plan, context_feedback)

    # Then
    assert revision is not None
    assert revision.strategy == RevisionStrategy.DECOMPOSE_FURTHER
    assert "smaller subtasks" in " ".join(revision.changes_made).lower()


def test_adjust_parameters_strategy():
    """RF-012: Escenario 6 - Adjust Parameters"""
    planner = IterativePlanner()
    plan = create_test_plan()

    invalid_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Invalid parameter format"],
        duration_seconds=2,
        cost=0.0
    )

    # When
    revision = planner.handle_feedback(plan, invalid_feedback)

    # Then
    assert revision is not None
    assert revision.strategy == RevisionStrategy.ADJUST_PARAMETERS


# ==================================
# Confidence Adjustment
# ==================================


def test_increase_confidence_on_success():
    """RF-012: Escenario 7 - Increase Confidence on Success"""
    planner = IterativePlanner()
    plan = create_test_plan()
    initial_confidence = plan.confidence_score

    success_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.SUCCESS,
        actual_outputs={"flights": ["flight1", "flight2"]},
        errors=[],
        duration_seconds=25,
        cost=0.01
    )

    # When
    revision = planner.handle_feedback(plan, success_feedback)

    # Then - no revision needed
    assert revision is None
    # Confidence increased
    assert plan.confidence_score > initial_confidence


def test_decrease_confidence_on_failure():
    """RF-012: Escenario 8 - Decrease Confidence on Failure"""
    planner = IterativePlanner()
    plan = create_test_plan()
    initial_confidence = plan.confidence_score

    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Task failed"],
        duration_seconds=5,
        cost=0.0
    )

    # When
    planner.handle_feedback(plan, failure_feedback)

    # Then - confidence decreased
    assert plan.confidence_score < initial_confidence


def test_confidence_stays_in_valid_range():
    """RF-012: Escenario 9 - Confidence Stays in [0, 1]"""
    planner = IterativePlanner()
    plan = create_test_plan()
    plan.confidence_score = 0.95  # High confidence

    # Multiple successes
    for _ in range(10):
        success_feedback = ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.SUCCESS,
            actual_outputs={"result": "ok"},
            errors=[],
            duration_seconds=20,
            cost=0.01
        )
        planner.handle_feedback(plan, success_feedback)

    # Confidence should not exceed 1.0
    assert plan.confidence_score <= 1.0


# ==================================
# Max Revisions and Escalation
# ==================================


def test_enforce_max_revisions_limit():
    """RF-012: Escenario 10 - Enforce Max Revisions Limit"""
    planner = IterativePlanner(max_revisions=3)
    plan = create_test_plan()

    # Create 3 failures
    for i in range(3):
        failure_feedback = ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.FAILURE,
            actual_outputs={},
            errors=[f"Failure {i+1}"],
            duration_seconds=5,
            cost=0.0
        )
        planner.handle_feedback(plan, failure_feedback)

    # 4th failure should trigger escalation
    final_failure = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Failure 4"],
        duration_seconds=5,
        cost=0.0
    )

    revision = planner.handle_feedback(plan, final_failure)

    # Should escalate to human
    assert revision.strategy == RevisionStrategy.ESCALATE_TO_HUMAN
    assert "max revisions" in revision.reason.lower()


def test_escalate_to_human_after_max_revisions():
    """RF-012: Escenario 11 - Escalate to Human"""
    planner = IterativePlanner(max_revisions=2)
    plan = create_test_plan()

    # Exhaust max revisions
    for _ in range(2):
        planner.handle_feedback(plan, ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.FAILURE,
            actual_outputs={},
            errors=["Error"],
            duration_seconds=5,
            cost=0.0
        ))

    # Next failure triggers escalation
    revision = planner.handle_feedback(plan, ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Persistent error"],
        duration_seconds=5,
        cost=0.0
    ))

    assert revision.strategy == RevisionStrategy.ESCALATE_TO_HUMAN


# ==================================
# Performance Tests
# ==================================


def test_failure_notification_within_500ms():
    """RF-012: Escenario 12 - Notification within 500ms"""
    orchestrator = ExecutionOrchestrator()

    failure = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Error occurred"],
        duration_seconds=5,
        cost=0.0
    )

    start = time.time()
    orchestrator.handle_task_completion(failure)
    duration = time.time() - start

    assert duration < 0.5, f"Notification took {duration:.3f}s (limit: 500ms)"

# ==================================
# Additional RF-012 Tests (13-20)
# ==================================

def test_track_revision_history():
    """RF-012: Escenario 13 - Track Revision History"""
    planner = IterativePlanner(max_revisions=5)
    plan = create_test_plan()
    
    # Create multiple revisions
    for i in range(3):
        failure = ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.FAILURE,
            actual_outputs={},
            errors=[f"Error {i+1}"],
            duration_seconds=5,
            cost=0.0
        )
        planner.handle_feedback(plan, failure)
    
    # Check revision history
    assert len(planner.revisions) == 3
    assert all(isinstance(r.created_at, datetime) for r in planner.revisions)


def test_communicate_recovery_strategy():
    """RF-012: Escenario 14 - Communicate Recovery Strategy"""
    orchestrator = ExecutionOrchestrator()
    notification_service = Mock()
    orchestrator.notification_service = notification_service
    
    failure = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Task failed"],
        duration_seconds=5,
        cost=0.0
    )
    
    orchestrator.handle_task_completion(failure)
    
    # Verify strategy communicated
    call_args = notification_service.send.call_args[0][0]
    assert "recovery_strategy" in call_args
    assert len(call_args["recovery_strategy"]) > 0


def test_estimate_recovery_time():
    """RF-012: Escenario 15 - Estimate Recovery Time"""
    orchestrator = ExecutionOrchestrator()
    
    # Test different strategies have time estimates
    assert "second" in orchestrator._estimate_recovery_delay(RevisionStrategy.RETRY_DIFFERENT_AGENT)
    assert "second" in orchestrator._estimate_recovery_delay(RevisionStrategy.DECOMPOSE_FURTHER)
    assert "manual" in orchestrator._estimate_recovery_delay(RevisionStrategy.ESCALATE_TO_HUMAN).lower()


def test_batch_feedback_processing():
    """RF-012: Escenario 16 - Batch Feedback Processing"""
    planner = IterativePlanner()
    plan = create_test_plan()
    
    # Process multiple feedbacks
    feedbacks = [
        ExecutionFeedback(task_id="task_001", feedback_type=FeedbackType.SUCCESS, 
                         actual_outputs={}, errors=[], duration_seconds=20, cost=0.01),
        ExecutionFeedback(task_id="task_002", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={}, errors=[], duration_seconds=22, cost=0.01)
    ]
    
    for feedback in feedbacks:
        planner.handle_feedback(plan, feedback)
    
    # Confidence should increase
    assert plan.confidence_score > 0.85


def test_partial_success_handling():
    """RF-012: Escenario 17 - Partial Success Handling"""
    planner = IterativePlanner()
    plan = create_test_plan()
    
    partial_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.PARTIAL_SUCCESS,
        actual_outputs={"partial_data": "some_data"},
        errors=["Could not complete fully"],
        duration_seconds=15,
        cost=0.005
    )
    
    # Should still trigger revision
    revision = planner.handle_feedback(plan, partial_feedback)
    assert revision is not None


def test_timeout_specific_handling():
    """RF-012: Escenario 18 - Timeout Specific Handling"""
    planner = IterativePlanner()
    
    timeout_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.TIMEOUT,
        actual_outputs={},
        errors=["Operation timed out"],
        duration_seconds=30,
        cost=0.0
    )
    
    # Timeout should be classified correctly
    failure_type = planner._classify_failure(timeout_feedback)
    assert failure_type in [FailureType.AGENT_TIMEOUT, FailureType.UNKNOWN]


def test_confidence_calibration():
    """RF-012: Escenario 19 - Confidence Calibration"""
    planner = IterativePlanner()
    plan = create_test_plan()
    initial_confidence = plan.confidence_score
    
    # Multiple successes should increase confidence
    for _ in range(5):
        success = ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.SUCCESS,
            actual_outputs={},
            errors=[],
            duration_seconds=20,
            cost=0.01
        )
        planner.handle_feedback(plan, success)
    
    assert plan.confidence_score >= initial_confidence
    assert plan.confidence_score <= 1.0  # Never exceed 1.0


def test_revision_prevents_infinite_loop():
    """RF-012: Escenario 20 - Prevent Infinite Revision Loop"""
    planner = IterativePlanner(max_revisions=2)
    plan = create_test_plan()
    
    # Exhaust revisions
    for i in range(3):
        failure = ExecutionFeedback(
            task_id="task_001",
            feedback_type=FeedbackType.FAILURE,
            actual_outputs={},
            errors=[f"Persistent error {i}"],
            duration_seconds=5,
            cost=0.0
        )
        revision = planner.handle_feedback(plan, failure)
        
        # After max_revisions, should escalate
        if i >= 2:
            assert revision.strategy == RevisionStrategy.ESCALATE_TO_HUMAN
