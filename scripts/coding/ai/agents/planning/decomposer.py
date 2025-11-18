"""
Task Decomposer: Breaks goals into executable subtasks.

Implements RF-011 scenarios 6-10 (Task Decomposition).
"""

import time
from typing import List

from .models import Goal, GoalType, Plan, SubTask, TaskStatus


class TaskDecomposer:
    """Decompose goals into structured plans with subtasks."""

    def __init__(self, openai_client=None):
        """Initialize decomposer with optional LLM client."""
        self.client = openai_client

    def decompose(self, goal: Goal) -> Plan:
        """
        Decompose goal into executable plan.

        Args:
            goal: Structured goal object

        Returns:
            Plan: Complete execution plan with subtasks
        """
        # Generate subtasks based on goal type
        if goal.goal_type == GoalType.TRAVEL_PLANNING:
            subtasks = self._decompose_travel_goal(goal)
        elif goal.goal_type == GoalType.DATA_ANALYSIS:
            subtasks = self._decompose_data_analysis_goal(goal)
        elif goal.goal_type == GoalType.RESEARCH:
            subtasks = self._decompose_research_goal(goal)
        else:
            subtasks = self._decompose_generic_goal(goal)

        # Calculate total duration
        total_duration = sum(t.estimated_duration_seconds for t in subtasks)

        # Calculate confidence score
        confidence = self._calculate_confidence(goal, subtasks)

        # Generate plan ID
        plan_id = f"plan_{int(time.time() * 1000)}"

        return Plan(
            plan_id=plan_id,
            goal_id=goal.goal_id,
            subtasks=subtasks,
            execution_strategy="sequential",
            estimated_total_duration=total_duration,
            confidence_score=confidence
        )

    def _decompose_travel_goal(self, goal: Goal) -> List[SubTask]:
        """Decompose travel planning goal."""
        subtasks = [
            SubTask(
                task_id="task_001",
                description="Search for flights",
                agent_type="flight_agent",
                dependencies=[],
                inputs={},
                expected_outputs=["flight_options", "flight_dates", "flight_price"],
                status=TaskStatus.PENDING,
                priority=10,
                estimated_duration_seconds=30
            ),
            SubTask(
                task_id="task_002",
                description="Find hotels",
                agent_type="hotel_agent",
                dependencies=["task_001"],  # Needs flight dates
                inputs={"dates": "from flight_dates"},
                expected_outputs=["hotel_options"],
                status=TaskStatus.PENDING,
                priority=9,
                estimated_duration_seconds=25
            ),
            SubTask(
                task_id="task_003",
                description="Plan activities",
                agent_type="activity_agent",
                dependencies=["task_001"],  # Needs dates
                inputs={},
                expected_outputs=["activity_list"],
                status=TaskStatus.PENDING,
                priority=7,
                estimated_duration_seconds=20
            ),
            SubTask(
                task_id="task_004",
                description="Validate budget",
                agent_type="validator_agent",
                dependencies=["task_001", "task_002"],  # Needs costs
                inputs={},
                expected_outputs=["budget_report"],
                status=TaskStatus.PENDING,
                priority=8,
                estimated_duration_seconds=10
            )
        ]

        return subtasks

    def _decompose_data_analysis_goal(self, goal: Goal) -> List[SubTask]:
        """Decompose data analysis goal."""
        subtasks = [
            SubTask(
                task_id="task_001",
                description="Load sales data",
                agent_type="data_loader",
                dependencies=[],
                inputs={},
                expected_outputs=["raw_data"],
                status=TaskStatus.PENDING,
                priority=10,
                estimated_duration_seconds=15
            ),
            SubTask(
                task_id="task_002",
                description="Clean data",
                agent_type="data_cleaner",
                dependencies=["task_001"],
                inputs={},
                expected_outputs=["clean_data"],
                status=TaskStatus.PENDING,
                priority=9,
                estimated_duration_seconds=20
            ),
            SubTask(
                task_id="task_003",
                description="Analyze trends",
                agent_type="analyzer",
                dependencies=["task_002"],
                inputs={},
                expected_outputs=["trends"],
                status=TaskStatus.PENDING,
                priority=8,
                estimated_duration_seconds=30
            ),
            SubTask(
                task_id="task_004",
                description="Create visualizations",
                agent_type="visualizer",
                dependencies=["task_003"],
                inputs={},
                expected_outputs=["charts"],
                status=TaskStatus.PENDING,
                priority=7,
                estimated_duration_seconds=25
            ),
            SubTask(
                task_id="task_005",
                description="Generate executive report",
                agent_type="reporter",
                dependencies=["task_003", "task_004"],
                inputs={},
                expected_outputs=["report"],
                status=TaskStatus.PENDING,
                priority=6,
                estimated_duration_seconds=20
            )
        ]

        return subtasks

    def _decompose_research_goal(self, goal: Goal) -> List[SubTask]:
        """Decompose research goal."""
        subtasks = [
            SubTask(
                task_id="task_001",
                description="Gather sources",
                agent_type="research_agent",
                dependencies=[],
                inputs={},
                expected_outputs=["sources"],
                status=TaskStatus.PENDING,
                priority=10,
                estimated_duration_seconds=40
            ),
            SubTask(
                task_id="task_002",
                description="Analyze findings",
                agent_type="analyzer",
                dependencies=["task_001"],
                inputs={},
                expected_outputs=["analysis"],
                status=TaskStatus.PENDING,
                priority=9,
                estimated_duration_seconds=50
            ),
            SubTask(
                task_id="task_003",
                description="Synthesize report",
                agent_type="writer",
                dependencies=["task_002"],
                inputs={},
                expected_outputs=["report"],
                status=TaskStatus.PENDING,
                priority=8,
                estimated_duration_seconds=30
            )
        ]

        return subtasks

    def _decompose_generic_goal(self, goal: Goal) -> List[SubTask]:
        """Decompose generic goal."""
        subtasks = [
            SubTask(
                task_id="task_001",
                description=f"Execute: {goal.description}",
                agent_type="general_agent",
                dependencies=[],
                inputs={},
                expected_outputs=["result"],
                status=TaskStatus.PENDING,
                priority=10,
                estimated_duration_seconds=30
            ),
            SubTask(
                task_id="task_002",
                description="Validate results",
                agent_type="validator",
                dependencies=["task_001"],
                inputs={},
                expected_outputs=["validation_report"],
                status=TaskStatus.PENDING,
                priority=8,
                estimated_duration_seconds=10
            )
        ]

        return subtasks

    def _calculate_confidence(self, goal: Goal, subtasks: List[SubTask]) -> float:
        """Calculate confidence score for plan."""
        # Base confidence
        confidence = 0.85

        # Reduce if goal is ambiguous
        if goal.metadata.get("requires_clarification"):
            confidence -= 0.15

        # Increase if constraints are well-defined
        if len(goal.constraints) >= 2:
            confidence += 0.05

        # Reduce for complex plans
        if len(subtasks) > 8:
            confidence -= 0.10

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
