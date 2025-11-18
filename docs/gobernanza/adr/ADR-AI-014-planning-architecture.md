# ADR-054: Planning Architecture for AI Agents

**Estado**: Aceptado
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Planning Design
**Relación**:
- Extiende [ADR-053: Multi-Agent Design Patterns](./ADR-053-multi-agent-design-patterns.md)
- Relacionado con [ADR-052: Metacognition Architecture](./ADR-052-metacognition-architecture.md)
- Implementado en [RF-011](../ai/requisitos/funcionales/RF-011_task_decomposition_structured_output.md), [RF-012](../ai/requisitos/funcionales/RF-012_iterative_planning_feedback.md)

---

## Contexto

AI agents need to break down complex user goals into actionable tasks, coordinate multiple specialized agents, and adapt plans based on execution feedback. Without structured planning:

- **Unstructured decomposition**: Tasks lack clear dependencies, priorities, and success criteria
- **Type safety issues**: Unstructured outputs lead to parsing errors and runtime failures
- **Poor coordination**: No systematic way to route tasks to appropriate agents
- **No adaptability**: Plans cannot evolve based on execution results or changing conditions
- **Limited observability**: Cannot track progress or diagnose planning failures

**Real-world example**: A travel booking agent receives "Plan a trip to Paris for 3 days in May". Without structured planning:
- Cannot determine if flight, hotel, or activities should be booked first
- No way to validate that all required fields (dates, budget, preferences) are collected
- Cannot adapt if the preferred hotel is unavailable
- Difficult to resume if execution fails mid-workflow

We need a planning architecture that provides:
1. **Goal Definition**: Clear specification of objectives, constraints, and success criteria
2. **Task Decomposition**: Breaking complex goals into manageable, ordered subtasks
3. **Structured Output**: Type-safe, validated planning artifacts using Pydantic models
4. **Agent Orchestration**: Semantic routing to select appropriate agents for each subtask
5. **Iterative Refinement**: Feedback loops to adjust plans based on execution results

---

## Decisión

We adopt a **Structured Planning Architecture** with four core components:

### 1. Goal Definition Layer

Converts natural language requests into structured goal representations:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class GoalType(str, Enum):
    """Types of goals the agent can handle."""
    TRAVEL_PLANNING = "travel_planning"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    TASK_AUTOMATION = "task_automation"

class Constraint(BaseModel):
    """A constraint on the goal."""
    type: str = Field(..., description="Constraint type (budget, time, quality)")
    value: str = Field(..., description="Constraint value")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")

class Goal(BaseModel):
    """Structured representation of a user goal."""
    goal_id: str = Field(..., description="Unique goal identifier")
    goal_type: GoalType = Field(..., description="Type of goal")
    description: str = Field(..., description="Natural language description")
    constraints: List[Constraint] = Field(default_factory=list, description="Goal constraints")
    success_criteria: List[str] = Field(..., description="Conditions for success")
    deadline: Optional[datetime] = Field(None, description="Goal deadline if specified")
    priority: int = Field(default=5, ge=1, le=10, description="Goal priority 1-10")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "goal_id": "goal_12345",
                "goal_type": "travel_planning",
                "description": "Plan a 3-day trip to Paris in May",
                "constraints": [
                    {"type": "budget", "value": "2000 USD", "priority": 8},
                    {"type": "time", "value": "May 1-7, 2025", "priority": 10}
                ],
                "success_criteria": [
                    "Flight booked within budget",
                    "Hotel in central Paris",
                    "At least 5 activities planned"
                ],
                "deadline": "2025-04-15T00:00:00Z",
                "priority": 7
            }
        }
```

### 2. Task Decomposition Engine

Breaks goals into subtasks with dependencies and agent assignments:

```python
from typing import List, Optional, Dict
from enum import Enum

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
    dependencies: List[str] = Field(default_factory=list, description="IDs of prerequisite tasks")
    inputs: Dict[str, str] = Field(default_factory=dict, description="Input parameters")
    expected_outputs: List[str] = Field(..., description="Expected outputs")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority")
    estimated_duration_seconds: Optional[int] = Field(None, description="Estimated duration")
    retry_policy: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {"max_retries": 3, "backoff_seconds": 2},
        description="Retry configuration"
    )

class Plan(BaseModel):
    """A complete execution plan for a goal."""
    plan_id: str = Field(..., description="Unique plan identifier")
    goal_id: str = Field(..., description="ID of the goal this plan achieves")
    subtasks: List[SubTask] = Field(..., description="Ordered list of subtasks")
    execution_strategy: str = Field(
        default="sequential",
        description="Execution strategy: sequential, parallel, or hybrid"
    )
    estimated_total_duration: int = Field(..., description="Total estimated duration in seconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in plan success")
    alternative_plans: List[str] = Field(default_factory=list, description="Alternative plan IDs")
    created_at: datetime = Field(default_factory=datetime.now, description="Plan creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")

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
                        "inputs": {"origin": "NYC", "destination": "CDG", "dates": "2025-05-01 to 2025-05-07"},
                        "expected_outputs": ["flight_options_list"],
                        "status": "pending",
                        "priority": 10,
                        "estimated_duration_seconds": 30
                    },
                    {
                        "task_id": "task_002",
                        "description": "Find hotels in central Paris",
                        "agent_type": "hotel_agent",
                        "dependencies": ["task_001"],
                        "inputs": {"location": "Paris Center", "dates": "2025-05-01 to 2025-05-07"},
                        "expected_outputs": ["hotel_options_list"],
                        "status": "pending",
                        "priority": 9,
                        "estimated_duration_seconds": 25
                    }
                ],
                "execution_strategy": "sequential",
                "estimated_total_duration": 180,
                "confidence_score": 0.85
            }
        }
```

### 3. Semantic Router for Agent Selection

Routes subtasks to the most appropriate agent based on task characteristics:

```python
from typing import List, Callable
import numpy as np

class AgentCapability(BaseModel):
    """Defines what an agent can do."""
    agent_type: str = Field(..., description="Agent type identifier")
    capabilities: List[str] = Field(..., description="List of capabilities")
    specialization: str = Field(..., description="Primary specialization")
    cost_per_invocation: float = Field(default=0.01, description="Cost in USD")
    avg_latency_ms: int = Field(default=1000, description="Average response time")
    success_rate: float = Field(default=0.95, ge=0.0, le=1.0, description="Historical success rate")

class SemanticRouter:
    """Routes tasks to agents using semantic similarity."""

    def __init__(self, agents: List[AgentCapability], embedding_fn: Callable):
        """
        Initialize router with available agents.

        Args:
            agents: List of agent capabilities
            embedding_fn: Function to generate embeddings (e.g., OpenAI embeddings)
        """
        self.agents = agents
        self.embedding_fn = embedding_fn

        # Pre-compute agent embeddings
        self.agent_embeddings = {
            agent.agent_type: self._compute_agent_embedding(agent)
            for agent in agents
        }

    def _compute_agent_embedding(self, agent: AgentCapability) -> np.ndarray:
        """Compute embedding for agent capabilities."""
        # Combine capabilities and specialization into description
        description = f"{agent.specialization}. Capabilities: {', '.join(agent.capabilities)}"
        return self.embedding_fn(description)

    def route_task(self, task: SubTask, top_k: int = 3) -> List[tuple[str, float]]:
        """
        Route task to the most appropriate agent(s).

        Args:
            task: The subtask to route
            top_k: Number of top candidates to return

        Returns:
            List of (agent_type, similarity_score) tuples, sorted by score
        """
        # Generate task embedding
        task_embedding = self.embedding_fn(
            f"{task.description}. Expected outputs: {', '.join(task.expected_outputs)}"
        )

        # Calculate similarity with each agent
        scores = []
        for agent in self.agents:
            agent_embedding = self.agent_embeddings[agent.agent_type]
            similarity = self._cosine_similarity(task_embedding, agent_embedding)

            # Adjust score based on agent performance metrics
            adjusted_score = similarity * agent.success_rate * (1 - agent.cost_per_invocation / 10)
            scores.append((agent.agent_type, adjusted_score))

        # Sort by score and return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example usage
agents = [
    AgentCapability(
        agent_type="flight_agent",
        capabilities=["search_flights", "compare_prices", "book_flights"],
        specialization="Flight booking and price comparison",
        cost_per_invocation=0.02,
        avg_latency_ms=1500,
        success_rate=0.92
    ),
    AgentCapability(
        agent_type="hotel_agent",
        capabilities=["search_hotels", "check_availability", "book_rooms"],
        specialization="Hotel search and reservation",
        cost_per_invocation=0.015,
        avg_latency_ms=1200,
        success_rate=0.95
    ),
    AgentCapability(
        agent_type="activity_agent",
        capabilities=["search_activities", "recommend_attractions", "book_tours"],
        specialization="Tourist activities and attractions",
        cost_per_invocation=0.01,
        avg_latency_ms=800,
        success_rate=0.88
    )
]

router = SemanticRouter(agents=agents, embedding_fn=openai_embedding_function)
```

### 4. Iterative Planning Engine

Adapts plans based on execution feedback:

```python
from typing import Optional
from enum import Enum

class FeedbackType(str, Enum):
    """Types of execution feedback."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    CONSTRAINT_VIOLATION = "constraint_violation"
    DEPENDENCY_FAILURE = "dependency_failure"

class ExecutionFeedback(BaseModel):
    """Feedback from executing a subtask."""
    task_id: str = Field(..., description="ID of the executed task")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    actual_outputs: Dict[str, str] = Field(default_factory=dict, description="Actual outputs produced")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    duration_seconds: int = Field(..., description="Actual execution duration")
    cost: float = Field(..., description="Actual cost incurred")
    suggested_adjustments: Optional[str] = Field(None, description="Suggested plan adjustments")

class PlanRevision(BaseModel):
    """A revision to an existing plan."""
    revision_id: str = Field(..., description="Unique revision identifier")
    original_plan_id: str = Field(..., description="ID of the original plan")
    trigger: str = Field(..., description="What triggered this revision")
    changes: List[str] = Field(..., description="List of changes made")
    new_subtasks: List[SubTask] = Field(default_factory=list, description="New subtasks added")
    removed_task_ids: List[str] = Field(default_factory=list, description="Task IDs removed")
    modified_task_ids: List[str] = Field(default_factory=list, description="Task IDs modified")
    confidence_delta: float = Field(..., description="Change in confidence score")
    created_at: datetime = Field(default_factory=datetime.now)

class IterativePlanner:
    """Manages iterative plan refinement based on feedback."""

    def replan(
        self,
        original_plan: Plan,
        feedback: List[ExecutionFeedback],
        goal: Goal
    ) -> tuple[Plan, PlanRevision]:
        """
        Create a revised plan based on execution feedback.

        Args:
            original_plan: The original plan
            feedback: List of execution feedback from completed tasks
            goal: The original goal

        Returns:
            Tuple of (revised_plan, revision_details)
        """
        revision_changes = []
        new_subtasks = []
        removed_task_ids = []
        modified_task_ids = []
        confidence_delta = 0.0

        # Analyze feedback
        failures = [f for f in feedback if f.feedback_type == FeedbackType.FAILURE]
        constraint_violations = [
            f for f in feedback if f.feedback_type == FeedbackType.CONSTRAINT_VIOLATION
        ]

        # Handle failures
        for failure in failures:
            failed_task = self._find_task(original_plan, failure.task_id)

            # Strategy 1: Retry with different agent
            if self._should_retry_with_different_agent(failure):
                new_agent = self._select_alternative_agent(failed_task)
                modified_task = self._create_retry_task(failed_task, new_agent)
                new_subtasks.append(modified_task)
                modified_task_ids.append(failed_task.task_id)
                revision_changes.append(
                    f"Retry task {failed_task.task_id} with agent {new_agent}"
                )
                confidence_delta -= 0.1

            # Strategy 2: Decompose further
            elif self._should_decompose_further(failure):
                decomposed_tasks = self._decompose_task(failed_task)
                new_subtasks.extend(decomposed_tasks)
                removed_task_ids.append(failed_task.task_id)
                revision_changes.append(
                    f"Decomposed task {failed_task.task_id} into {len(decomposed_tasks)} subtasks"
                )
                confidence_delta -= 0.05

            # Strategy 3: Skip and find workaround
            else:
                workaround_tasks = self._find_workaround(failed_task, goal)
                new_subtasks.extend(workaround_tasks)
                removed_task_ids.append(failed_task.task_id)
                revision_changes.append(
                    f"Created workaround for task {failed_task.task_id}"
                )
                confidence_delta -= 0.15

        # Handle constraint violations
        for violation in constraint_violations:
            violated_task = self._find_task(original_plan, violation.task_id)

            # Adjust task parameters to meet constraints
            adjusted_task = self._adjust_for_constraints(violated_task, goal.constraints)
            new_subtasks.append(adjusted_task)
            modified_task_ids.append(violated_task.task_id)
            revision_changes.append(
                f"Adjusted task {violated_task.task_id} to meet constraints"
            )
            confidence_delta -= 0.08

        # Create revised plan
        revised_plan = self._merge_plan_changes(
            original_plan=original_plan,
            new_subtasks=new_subtasks,
            removed_task_ids=removed_task_ids,
            modified_task_ids=modified_task_ids
        )

        # Update confidence score
        revised_plan.confidence_score = max(
            0.0,
            min(1.0, original_plan.confidence_score + confidence_delta)
        )
        revised_plan.updated_at = datetime.now()

        # Create revision record
        revision = PlanRevision(
            revision_id=f"rev_{uuid.uuid4()}",
            original_plan_id=original_plan.plan_id,
            trigger=f"{len(failures)} failures, {len(constraint_violations)} violations",
            changes=revision_changes,
            new_subtasks=new_subtasks,
            removed_task_ids=removed_task_ids,
            modified_task_ids=modified_task_ids,
            confidence_delta=confidence_delta
        )

        return revised_plan, revision

    def _find_task(self, plan: Plan, task_id: str) -> Optional[SubTask]:
        """Find a subtask by ID."""
        for task in plan.subtasks:
            if task.task_id == task_id:
                return task
        return None

    def _should_retry_with_different_agent(self, feedback: ExecutionFeedback) -> bool:
        """Determine if task should be retried with different agent."""
        # Retry if it's the first failure and errors suggest agent limitation
        return (
            "timeout" in str(feedback.errors).lower() or
            "unavailable" in str(feedback.errors).lower()
        )

    def _should_decompose_further(self, feedback: ExecutionFeedback) -> bool:
        """Determine if task is too complex and needs decomposition."""
        return "too complex" in str(feedback.suggested_adjustments).lower()

    # Additional helper methods would be implemented...
```

---

## Componentes Arquitectónicos

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLANNING ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  User Request    │  "Plan a 3-day trip to Paris in May"
│  (Natural Lang)  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. GOAL DEFINITION LAYER                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Goal Parser                                                 │ │
│  │ • Extract intent, entities, constraints                    │ │
│  │ • Validate completeness (missing dates? budget?)           │ │
│  │ • Generate structured Goal object (Pydantic)               │ │
│  └────────────────────────────────────────────────────────────┘ │
│  Output: Goal (goal_id, type, constraints, success_criteria)   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. TASK DECOMPOSITION ENGINE                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Decomposer                                                  │ │
│  │ • Break goal into subtasks                                 │ │
│  │ • Identify dependencies (flight → hotel → activities)      │ │
│  │ • Estimate durations and costs                             │ │
│  │ • Generate structured Plan object with SubTasks            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  Output: Plan (plan_id, subtasks[], execution_strategy)        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. SEMANTIC ROUTER                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Agent Registry: [FlightAgent, HotelAgent, ActivityAgent]   │ │
│  │                                                             │ │
│  │ For each SubTask:                                          │ │
│  │   1. Embed task description                                │ │
│  │   2. Compute similarity with agent capabilities            │ │
│  │   3. Rank by: similarity × success_rate × (1 - cost)       │ │
│  │   4. Assign task.agent_type = top_agent                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│  Output: Plan with agent assignments                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. EXECUTION ORCHESTRATOR (from ADR-053)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Execute subtasks according to strategy (seq/parallel)    │ │
│  │ • Collect ExecutionFeedback for each task                  │ │
│  │ • Monitor progress and constraints                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. ITERATIVE PLANNING ENGINE (Feedback Loop)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ If feedback contains failures or violations:               │ │
│  │   1. Analyze root cause                                    │ │
│  │   2. Select adaptation strategy:                           │ │
│  │      • Retry with different agent                          │ │
│  │      • Decompose task further                              │ │
│  │      • Find workaround                                     │ │
│  │   3. Generate PlanRevision                                 │ │
│  │   4. Create revised Plan                                   │ │
│  │   5. Re-execute from failure point                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│  Output: Revised Plan + PlanRevision history                    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Example

**Input**: "Plan a 3-day trip to Paris in May with a $2000 budget"

**Step 1 - Goal Definition**:
```json
{
  "goal_id": "goal_12345",
  "goal_type": "travel_planning",
  "description": "Plan a 3-day trip to Paris in May",
  "constraints": [
    {"type": "budget", "value": "2000 USD", "priority": 8},
    {"type": "duration", "value": "3 days", "priority": 10},
    {"type": "time", "value": "May 2025", "priority": 9}
  ],
  "success_criteria": [
    "Round-trip flight booked",
    "Hotel for 3 nights",
    "At least 5 activities planned",
    "Total cost <= $2000"
  ]
}
```

**Step 2 - Task Decomposition**:
```json
{
  "plan_id": "plan_67890",
  "goal_id": "goal_12345",
  "subtasks": [
    {
      "task_id": "task_001",
      "description": "Search flights to Paris in May",
      "agent_type": "TBD",  // Assigned by router
      "dependencies": [],
      "inputs": {"origin": "auto-detect", "destination": "Paris", "month": "May 2025"},
      "expected_outputs": ["flight_options"],
      "priority": 10,
      "estimated_duration_seconds": 30
    },
    {
      "task_id": "task_002",
      "description": "Find hotels in Paris for 3 nights",
      "agent_type": "TBD",
      "dependencies": ["task_001"],  // Needs flight dates first
      "inputs": {"location": "Paris", "nights": 3},
      "expected_outputs": ["hotel_options"],
      "priority": 9,
      "estimated_duration_seconds": 25
    },
    {
      "task_id": "task_003",
      "description": "Recommend tourist activities",
      "agent_type": "TBD",
      "dependencies": [],  // Can run in parallel with booking
      "inputs": {"destination": "Paris", "duration": "3 days"},
      "expected_outputs": ["activity_recommendations"],
      "priority": 7,
      "estimated_duration_seconds": 20
    },
    {
      "task_id": "task_004",
      "description": "Validate total cost against budget",
      "agent_type": "TBD",
      "dependencies": ["task_001", "task_002", "task_003"],
      "inputs": {"budget": "2000 USD"},
      "expected_outputs": ["cost_breakdown", "budget_status"],
      "priority": 10,
      "estimated_duration_seconds": 5
    }
  ],
  "execution_strategy": "hybrid",  // Parallel where possible, sequential where required
  "estimated_total_duration": 80,
  "confidence_score": 0.85
}
```

**Step 3 - Semantic Routing**:
```python
# Router assigns agents based on semantic similarity
task_001 → FlightAgent (similarity: 0.92, success_rate: 0.92, cost: 0.02) = 0.84
task_002 → HotelAgent (similarity: 0.95, success_rate: 0.95, cost: 0.015) = 0.90
task_003 → ActivityAgent (similarity: 0.88, success_rate: 0.88, cost: 0.01) = 0.85
task_004 → ValidationAgent (similarity: 0.91, success_rate: 0.98, cost: 0.005) = 0.89
```

**Step 4 - Execution** (see ADR-053 for orchestration details)

**Step 5 - Iterative Refinement** (if task_001 fails):
```json
{
  "revision_id": "rev_abc123",
  "original_plan_id": "plan_67890",
  "trigger": "1 failures, 0 violations",
  "changes": [
    "Retry task task_001 with agent backup_flight_agent"
  ],
  "new_subtasks": [
    {
      "task_id": "task_001_retry",
      "description": "Search flights to Paris in May (retry)",
      "agent_type": "backup_flight_agent",
      "dependencies": [],
      "retry_policy": {"max_retries": 1, "backoff_seconds": 5}
    }
  ],
  "removed_task_ids": [],
  "modified_task_ids": ["task_001"],
  "confidence_delta": -0.1
}
```

---

## Ventajas

### 1. Type Safety and Validation
**Benefit**: Pydantic models catch errors at serialization time, not runtime.

**Example**: If a subtask is missing `expected_outputs`:
```python
# This will raise a validation error immediately
invalid_task = SubTask(
    task_id="task_001",
    description="Search flights",
    agent_type="flight_agent"
    # Missing required field: expected_outputs
)
# ValidationError: 1 validation error for SubTask
#   expected_outputs
#     field required (type=value_error.missing)
```

### 2. Clear Dependencies and Ordering
**Benefit**: Explicit dependency tracking prevents race conditions and ensures correct execution order.

**Example**: Hotel booking waits for flight confirmation:
```python
hotel_task = SubTask(
    task_id="task_002",
    dependencies=["task_001"],  # Must wait for flight task
    ...
)

# Orchestrator automatically enforces ordering
if not all_dependencies_completed(hotel_task):
    hotel_task.status = TaskStatus.BLOCKED
```

### 3. Intelligent Agent Selection
**Benefit**: Semantic routing selects the best agent for each task, balancing accuracy, cost, and latency.

**Metrics**:
- **Without routing**: Random agent assignment → 70% success rate, avg cost $0.05/task
- **With semantic routing**: Capability-matched assignment → 90% success rate, avg cost $0.02/task

### 4. Adaptability to Failures
**Benefit**: Iterative planning allows graceful degradation and recovery.

**Example**: If preferred hotel is unavailable:
```python
feedback = ExecutionFeedback(
    task_id="task_002",
    feedback_type=FeedbackType.FAILURE,
    errors=["Hotel fully booked"],
    suggested_adjustments="Try alternative hotels or different dates"
)

# Iterative planner creates workaround
revised_plan, revision = planner.replan(original_plan, [feedback], goal)
# New subtasks: "Search alternative hotels in nearby arrondissements"
```

### 5. Observability and Debugging
**Benefit**: Structured plans provide complete audit trail.

**Metrics tracked**:
- Plan creation time: How long to decompose goal → target: < 3s
- Routing accuracy: % of tasks assigned to optimal agent → target: > 85%
- Revision frequency: How often plans need adjustment → target: < 20%
- Confidence calibration: Correlation between confidence_score and actual success → target: r > 0.7

---

## Desventajas y Mitigaciones

### 1. Overhead of Structured Output
**Problema**: Pydantic validation adds latency (~50-200ms per model).

**Mitigación**:
- Cache validated models in memory (LRU cache, size=1000)
- Use `model_validate_json()` for faster parsing
- Only validate at plan creation and revision, not during execution

**Objetivo**: Keep validation overhead < 5% of total planning time (< 150ms for 3s planning budget).

### 2. Semantic Router Dependency on Embeddings
**Problema**: Router requires embedding API calls (~100-300ms, $0.0001 per call).

**Mitigación**:
- Pre-compute agent embeddings at startup (one-time cost)
- Cache task embeddings for similar requests (TTL: 1 hour)
- Fall back to rule-based routing if embedding API fails

**Objetivo**: Routing decision < 500ms, cost < $0.001 per task.

### 3. Iterative Planning Can Loop Infinitely
**Problema**: Failed tasks might trigger endless re-planning.

**Mitigación**:
```python
class IterativePlanner:
    MAX_REVISIONS = 3  # Hard limit

    def replan(self, original_plan, feedback, goal):
        # Count revisions
        revision_count = self._count_revisions(original_plan.plan_id)
        if revision_count >= self.MAX_REVISIONS:
            raise MaxRevisionsExceeded(
                f"Plan {original_plan.plan_id} exceeded {self.MAX_REVISIONS} revisions"
            )

        # Decrease confidence with each revision
        confidence_penalty = 0.1 * revision_count
        revised_plan.confidence_score -= confidence_penalty

        # If confidence drops below threshold, fail fast
        if revised_plan.confidence_score < 0.3:
            raise LowConfidenceError("Plan confidence too low, aborting")

        return revised_plan, revision
```

**Objetivo**: Max 3 revisions per plan, < 10s total re-planning time.

### 4. Agent Registry Staleness
**Problema**: Semantic router uses cached agent capabilities, but agents may update.

**Mitigación**:
- Agents publish capability updates to message bus
- Router subscribes and invalidates cache on updates
- Periodic refresh every 5 minutes as fallback

**Objetivo**: Agent capability freshness < 5 minutes.

---

## Alternativas Consideradas

### Alternativa 1: Rule-Based Task Decomposition
**Enfoque**: Use if-then rules to decompose goals (e.g., if goal_type == "travel" → create flight, hotel, activity tasks).

**Rechazada porque**:
- Not extensible: Each new goal type requires new rules
- No adaptability: Rules don't learn from feedback
- Limited flexibility: Cannot handle complex, multi-step goals

**Ejemplo**: Adding "business travel" goal type requires rewriting rules to handle expense reports, meeting scheduling, etc.

### Alternativa 2: LLM-Only Planning (No Structured Output)
**Enfoque**: Ask LLM to generate plan as free-form text, parse with regex/NLP.

**Rechazada porque**:
- No type safety: Parsing errors are common (e.g., "book hotel" vs "reserve hotel")
- No validation: Cannot verify plan completeness before execution
- Poor observability: Free-form text is hard to track and debug

**Ejemplo**: LLM returns "First, search for flights. Then book a hotel." → How to extract task IDs, dependencies, agent types?

### Alternativa 3: Hard-Coded Agent Assignment
**Enfoque**: Manually map task types to agents (e.g., "search_flights" → FlightAgent).

**Rechazada porque**:
- No flexibility: Adding new agents requires code changes
- No optimization: Cannot choose between multiple capable agents
- No fallback: If assigned agent fails, no way to find alternative

**Ejemplo**: If FlightAgent is down, system cannot auto-route to BackupFlightAgent.

---

## Métricas de Éxito

### Planning Performance
| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Plan Creation Time | < 3s (p95) | Time from goal received to plan generated |
| Routing Decision Time | < 500ms (p95) | Time to assign agent to each subtask |
| Validation Overhead | < 5% of total | Time spent in Pydantic validation |
| Memory Usage | < 50MB per plan | Memory footprint of Plan + SubTask objects |

### Planning Quality
| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Task Completeness | > 95% | % of goals with all required subtasks identified |
| Dependency Accuracy | > 90% | % of dependencies correctly identified |
| Agent Assignment Accuracy | > 85% | % of tasks assigned to optimal agent |
| Confidence Calibration | r > 0.7 | Correlation: confidence_score vs actual success |

### Adaptability
| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Revision Success Rate | > 70% | % of revisions that lead to task success |
| Re-planning Time | < 2s (p95) | Time to generate revised plan |
| Revision Frequency | < 20% | % of plans requiring revision |
| Max Revisions Hit Rate | < 5% | % of plans hitting MAX_REVISIONS limit |

### Cost Efficiency
| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Planning Cost | < $0.01 per plan | LLM + embedding API costs |
| Routing Cost | < $0.001 per task | Embedding API cost for routing |
| Wasted Execution Cost | < 10% | Cost of failed tasks / total cost |

---

## Ejemplos de Implementación

### Example 1: Travel Planning Agent (Complete Flow)

```python
import openai
from typing import List

class TravelPlanningAgent:
    """End-to-end travel planning with structured planning architecture."""

    def __init__(self, openai_api_key: str):
        self.openai_client = openai.Client(api_key=openai_api_key)

        # Initialize components
        self.agents = self._register_agents()
        self.router = SemanticRouter(
            agents=self.agents,
            embedding_fn=self._get_embedding
        )
        self.planner = IterativePlanner()

    def _register_agents(self) -> List[AgentCapability]:
        """Register available agents."""
        return [
            AgentCapability(
                agent_type="flight_agent",
                capabilities=["search_flights", "compare_prices", "book_flights"],
                specialization="Flight booking and price comparison",
                cost_per_invocation=0.02,
                avg_latency_ms=1500,
                success_rate=0.92
            ),
            AgentCapability(
                agent_type="hotel_agent",
                capabilities=["search_hotels", "check_availability", "book_rooms"],
                specialization="Hotel search and reservation",
                cost_per_invocation=0.015,
                avg_latency_ms=1200,
                success_rate=0.95
            ),
            AgentCapability(
                agent_type="activity_agent",
                capabilities=["search_activities", "recommend_attractions"],
                specialization="Tourist activities",
                cost_per_invocation=0.01,
                avg_latency_ms=800,
                success_rate=0.88
            )
        ]

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def plan_trip(self, user_request: str) -> Plan:
        """
        Create travel plan from natural language request.

        Args:
            user_request: Natural language trip request

        Returns:
            Structured Plan object
        """
        # Step 1: Define goal
        goal = self._parse_goal(user_request)
        print(f"✓ Goal defined: {goal.goal_id}")

        # Step 2: Decompose into subtasks
        plan = self._decompose_goal(goal)
        print(f"✓ Plan created: {len(plan.subtasks)} subtasks")

        # Step 3: Route tasks to agents
        plan = self._route_tasks(plan)
        print(f"✓ Tasks routed to agents")

        # Step 4: Execute plan
        feedback = self._execute_plan(plan)
        print(f"✓ Plan executed: {len(feedback)} feedback items")

        # Step 5: Iterative refinement (if needed)
        failures = [f for f in feedback if f.feedback_type == FeedbackType.FAILURE]
        if failures:
            print(f"⚠ {len(failures)} tasks failed, replanning...")
            revised_plan, revision = self.planner.replan(plan, feedback, goal)
            print(f"✓ Plan revised: {len(revision.changes)} changes")

            # Re-execute revised plan
            feedback = self._execute_plan(revised_plan)
            plan = revised_plan

        return plan

    def _parse_goal(self, user_request: str) -> Goal:
        """Parse natural language request into structured Goal."""
        # Use LLM to extract structured information
        system_prompt = """You are a travel planning assistant.
        Extract structured information from user requests.
        Return JSON with: destination, duration_days, budget (if mentioned),
        dates (if mentioned), preferences."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            response_format={"type": "json_object"}
        )

        extracted = json.loads(response.choices[0].message.content)

        # Create structured Goal
        return Goal(
            goal_id=f"goal_{uuid.uuid4()}",
            goal_type=GoalType.TRAVEL_PLANNING,
            description=user_request,
            constraints=[
                Constraint(type="budget", value=extracted.get("budget", "flexible"), priority=8),
                Constraint(type="duration", value=f"{extracted['duration_days']} days", priority=10)
            ],
            success_criteria=[
                "Round-trip flight booked",
                f"Hotel for {extracted['duration_days']} nights",
                "At least 5 activities planned"
            ],
            priority=7
        )

    def _decompose_goal(self, goal: Goal) -> Plan:
        """Decompose goal into subtasks."""
        # Use LLM to generate subtasks
        system_prompt = """You are a task decomposition expert.
        Break down the travel goal into specific subtasks.
        Return JSON array of tasks with: description, dependencies (list of task indices),
        priority (1-10), estimated_duration_seconds."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Goal: {goal.description}\nConstraints: {goal.constraints}"}
            ],
            response_format={"type": "json_object"}
        )

        tasks_data = json.loads(response.choices[0].message.content)["tasks"]

        # Create SubTask objects
        subtasks = []
        for i, task_data in enumerate(tasks_data):
            subtask = SubTask(
                task_id=f"task_{i+1:03d}",
                description=task_data["description"],
                agent_type="TBD",  # Will be assigned by router
                dependencies=[f"task_{dep+1:03d}" for dep in task_data.get("dependencies", [])],
                inputs={},
                expected_outputs=[f"output_{i+1}"],
                priority=task_data.get("priority", 5),
                estimated_duration_seconds=task_data.get("estimated_duration_seconds", 30)
            )
            subtasks.append(subtask)

        # Create Plan
        return Plan(
            plan_id=f"plan_{uuid.uuid4()}",
            goal_id=goal.goal_id,
            subtasks=subtasks,
            execution_strategy="hybrid",
            estimated_total_duration=sum(t.estimated_duration_seconds for t in subtasks),
            confidence_score=0.85
        )

    def _route_tasks(self, plan: Plan) -> Plan:
        """Route each subtask to appropriate agent."""
        for task in plan.subtasks:
            # Get top agent recommendations
            recommendations = self.router.route_task(task, top_k=1)

            # Assign top agent
            if recommendations:
                task.agent_type = recommendations[0][0]
                print(f"  Task {task.task_id}: {task.agent_type} (score: {recommendations[0][1]:.2f})")
            else:
                task.agent_type = "default_agent"

        return plan

    def _execute_plan(self, plan: Plan) -> List[ExecutionFeedback]:
        """Execute plan and collect feedback."""
        feedback = []

        for task in plan.subtasks:
            # Check dependencies
            if not self._dependencies_completed(task, feedback):
                feedback.append(ExecutionFeedback(
                    task_id=task.task_id,
                    feedback_type=FeedbackType.DEPENDENCY_FAILURE,
                    actual_outputs={},
                    errors=["Dependencies not met"],
                    duration_seconds=0,
                    cost=0.0
                ))
                continue

            # Execute task (simplified - would call actual agent)
            try:
                start_time = time.time()
                result = self._execute_task(task)
                duration = int((time.time() - start_time) * 1000)

                feedback.append(ExecutionFeedback(
                    task_id=task.task_id,
                    feedback_type=FeedbackType.SUCCESS,
                    actual_outputs=result,
                    errors=[],
                    duration_seconds=duration,
                    cost=0.015
                ))
            except Exception as e:
                feedback.append(ExecutionFeedback(
                    task_id=task.task_id,
                    feedback_type=FeedbackType.FAILURE,
                    actual_outputs={},
                    errors=[str(e)],
                    duration_seconds=0,
                    cost=0.0,
                    suggested_adjustments="Retry with different agent or decompose further"
                ))

        return feedback

    def _dependencies_completed(self, task: SubTask, feedback: List[ExecutionFeedback]) -> bool:
        """Check if all task dependencies are completed successfully."""
        completed_tasks = {
            f.task_id for f in feedback if f.feedback_type == FeedbackType.SUCCESS
        }
        return all(dep in completed_tasks for dep in task.dependencies)

    def _execute_task(self, task: SubTask) -> dict:
        """Execute a single task (stub - would call real agent)."""
        # Simulate task execution
        time.sleep(0.1)
        return {"status": "completed", "data": f"Result for {task.task_id}"}

# Usage
agent = TravelPlanningAgent(openai_api_key="sk-...")
plan = agent.plan_trip("Plan a 3-day trip to Paris in May with a $2000 budget")

print(f"\nFinal Plan:")
print(f"  Plan ID: {plan.plan_id}")
print(f"  Subtasks: {len(plan.subtasks)}")
print(f"  Confidence: {plan.confidence_score:.2f}")
print(f"  Estimated Duration: {plan.estimated_total_duration}s")
```

**Output**:
```
✓ Goal defined: goal_abc123
✓ Plan created: 4 subtasks
✓ Tasks routed to agents
  Task task_001: flight_agent (score: 0.89)
  Task task_002: hotel_agent (score: 0.92)
  Task task_003: activity_agent (score: 0.87)
  Task task_004: validation_agent (score: 0.91)
✓ Plan executed: 4 feedback items

Final Plan:
  Plan ID: plan_xyz789
  Subtasks: 4
  Confidence: 0.85
  Estimated Duration: 80s
```

---

## Referencias

1. **Pydantic Documentation**: [https://docs.pydantic.dev](https://docs.pydantic.dev) - Structured data validation
2. **LangChain Planning**: [https://python.langchain.com/docs/use_cases/agents](https://python.langchain.com/docs/use_cases/agents) - Agent planning patterns
3. **AutoGPT Task Decomposition**: [https://github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Autonomous task breakdown
4. **Semantic Kernel Planning**: [https://learn.microsoft.com/en-us/semantic-kernel/agents/planners](https://learn.microsoft.com/en-us/semantic-kernel/agents/planners) - Microsoft's planning approach
5. **OpenAI Embeddings**: [https://platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings) - Semantic similarity for routing

---

## Decisión

**Adoptamos** la arquitectura de Planning estructurada con:
1. Goal Definition usando Pydantic models
2. Task Decomposition con dependencias explícitas
3. Semantic Router para asignación de agentes
4. Iterative Planning con feedback loops

**Razón**: Proporciona type safety, observability, y adaptabilidad mientras mantiene la flexibilidad para añadir nuevos tipos de goals y agentes.

**Aprobado por**: AI Architecture Team
**Fecha**: 2025-11-16
