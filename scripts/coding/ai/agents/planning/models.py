"""
Planning models for structured goal definition and task decomposition.

Implements ADR-054: Planning Architecture
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class GoalType(str, Enum):
    """Types of goals the agent can handle."""

    TRAVEL_PLANNING = "travel_planning"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    TASK_AUTOMATION = "task_automation"
    COMPLEX = "complex"
    SIMPLE = "simple"


class Constraint(BaseModel):
    """A constraint on the goal."""

    type: str = Field(..., description="Constraint type (budget, time, quality, duration)")
    value: str = Field(..., description="Constraint value")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")


class Goal(BaseModel):
    """Structured representation of a user goal."""

    goal_id: str = Field(..., description="Unique goal identifier")
    goal_type: GoalType = Field(..., description="Type of goal")
    description: str = Field(..., description="Natural language description")
    constraints: List[Constraint] = Field(
        default_factory=list, description="Goal constraints"
    )
    success_criteria: List[str] = Field(..., description="Conditions for success")
    deadline: Optional[datetime] = Field(None, description="Goal deadline if specified")
    priority: int = Field(default=5, ge=1, le=10, description="Goal priority 1-10")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "goal_id": "goal_12345",
                "goal_type": "travel_planning",
                "description": "Plan a 3-day trip to Paris in May",
                "constraints": [
                    {"type": "budget", "value": "2000 USD", "priority": 8},
                    {"type": "time", "value": "May 1-7, 2025", "priority": 10},
                ],
                "success_criteria": [
                    "Flight booked within budget",
                    "Hotel in central Paris",
                    "At least 5 activities planned",
                ],
                "deadline": "2025-04-15T00:00:00Z",
                "priority": 7,
            }
        }


class TaskStatus(str, Enum):
    """Status of a subtask."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class SubTask(BaseModel):
    """A decomposed subtask with structured fields."""

    task_id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")
    agent_type: str = Field(..., description="Agent type to execute this task")
    dependencies: List[str] = Field(
        default_factory=list, description="IDs of prerequisite tasks"
    )
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    expected_outputs: List[str] = Field(..., description="Expected outputs")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority")
    estimated_duration_seconds: Optional[int] = Field(
        None, description="Estimated duration"
    )
    retry_policy: Dict[str, int] = Field(
        default_factory=lambda: {"max_retries": 3, "backoff_seconds": 2},
        description="Retry configuration",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional task metadata"
    )


class Plan(BaseModel):
    """A complete execution plan for a goal."""

    plan_id: str = Field(..., description="Unique plan identifier")
    goal_id: str = Field(..., description="ID of the goal this plan achieves")
    subtasks: List[SubTask] = Field(..., description="Ordered list of subtasks")
    execution_strategy: str = Field(
        default="sequential",
        description="Execution strategy: sequential, parallel, or hybrid",
    )
    estimated_total_duration: int = Field(
        ..., description="Total estimated duration in seconds"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in plan success"
    )
    alternative_plans: List[str] = Field(
        default_factory=list, description="Alternative plan IDs"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Plan creation time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update time"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional plan metadata"
    )

    @field_validator("subtasks")
    @classmethod
    def validate_no_circular_dependencies(cls, v: List[SubTask]) -> List[SubTask]:
        """Validate that there are no circular dependencies in subtasks."""
        task_ids = {task.task_id for task in v}

        # Check all dependencies exist
        for task in v:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValueError(
                        f"Task {task.task_id} depends on non-existent task {dep_id}"
                    )

        # Check for circular dependencies using DFS
        def has_cycle(task_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            # Find task
            task = next((t for t in v if t.task_id == task_id), None)
            if task:
                for dep_id in task.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        visited: set = set()
        for task in v:
            if task.task_id not in visited:
                if has_cycle(task.task_id, visited, set()):
                    raise ValueError("Circular dependency detected in subtasks")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "plan_67890",
                "goal_id": "goal_12345",
                "subtasks": [
                    {
                        "task_id": "task_001",
                        "description": "Search for flights to Paris May 1-7",
                        "agent_type": "flight_agent",
                        "dependencies": [],
                        "inputs": {
                            "origin": "NYC",
                            "destination": "CDG",
                            "dates": "2025-05-01 to 2025-05-07",
                        },
                        "expected_outputs": ["flight_options_list"],
                        "status": "pending",
                        "priority": 10,
                        "estimated_duration_seconds": 30,
                    },
                    {
                        "task_id": "task_002",
                        "description": "Find hotels in central Paris",
                        "agent_type": "hotel_agent",
                        "dependencies": ["task_001"],
                        "inputs": {
                            "location": "Paris Center",
                            "dates": "2025-05-01 to 2025-05-07",
                        },
                        "expected_outputs": ["hotel_options_list"],
                        "status": "pending",
                        "priority": 9,
                        "estimated_duration_seconds": 25,
                    },
                ],
                "execution_strategy": "sequential",
                "estimated_total_duration": 180,
                "confidence_score": 0.85,
            }
        }


class RevisionStrategy(str, Enum):
    """Strategy for revising a failed plan."""

    RETRY_DIFFERENT_AGENT = "retry_different_agent"
    DECOMPOSE_FURTHER = "decompose_further"
    ADJUST_PARAMETERS = "adjust_parameters"
    ADD_FALLBACK = "add_fallback"
    ESCALATE_TO_HUMAN = "escalate_to_human"


class PlanRevision(BaseModel):
    """Records a revision to a plan based on execution feedback."""

    revision_id: str = Field(..., description="Unique revision identifier")
    original_plan_id: str = Field(..., description="ID of the original plan")
    new_plan_id: str = Field(..., description="ID of the revised plan")
    reason: str = Field(..., description="Why the revision was needed")
    strategy: RevisionStrategy = Field(..., description="Revision strategy used")
    failed_task_id: Optional[str] = Field(
        None, description="ID of the task that failed"
    )
    changes_made: List[str] = Field(..., description="List of changes applied")
    confidence_delta: float = Field(
        ..., description="Change in confidence score (-1.0 to 1.0)"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Revision creation time"
    )


class AgentCapability(BaseModel):
    """Defines what an agent can do."""

    agent_type: str = Field(..., description="Agent type identifier")
    capabilities: List[str] = Field(..., description="List of capabilities")
    specialization: str = Field(..., description="Primary specialization")
    cost_per_invocation: float = Field(default=0.01, description="Cost in USD")
    avg_latency_ms: int = Field(default=1000, description="Average response time")
    success_rate: float = Field(
        default=0.95, ge=0.0, le=1.0, description="Historical success rate"
    )
    max_concurrent_tasks: int = Field(
        default=5, description="Maximum concurrent tasks"
    )
