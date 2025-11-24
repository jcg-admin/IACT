# RT-013: Planning Performance and Quality Standards

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Planning Design
**Relación**:
- Implementa [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
- Relacionado con [RT-009: Metacognition Performance Constraints](./RT-009_metacognition_performance_constraints.md)
- Relacionado con [RT-011: Multi-Agent Communication Coordination](./RT-011_multi_agent_communication_coordination.md)

---

## Propósito

Define performance constraints, quality standards, and cost budgets for the Planning Architecture to ensure:
- **Low latency**: Plans generated in < 3s (p95)
- **High quality**: > 95% task completeness, > 90% dependency accuracy
- **Cost efficiency**: < $0.01 per plan
- **Adaptability**: Revisions succeed > 70% of the time
- **Observability**: All planning operations tracked and measurable

---

## Performance Constraints

### 1. Latency Targets

All planning operations must meet these latency targets (p95):

| Operation | Target Latency | Enforcement |
|-----------|----------------|-------------|
| Goal Parsing | < 1s | Timeout decorator |
| Task Decomposition | < 2s | Timeout decorator |
| Agent Routing (per task) | < 500ms | Timeout decorator |
| Plan Validation | < 200ms | Sync validation only |
| Plan Execution Orchestration | < 100ms | Non-blocking dispatch |
| Re-planning | < 2s | Timeout decorator |
| Full Planning Cycle | < 3s | End-to-end monitoring |

**Enforcement mechanism**:

```python
import functools
import time
from typing import Callable, Any
from prometheus_client import Histogram

# Metrics
PLANNING_LATENCY = Histogram(
    'planning_operation_latency_seconds',
    'Latency of planning operations',
    ['operation', 'status'],
    buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

class PlanningTimeoutError(Exception):
    """Raised when planning operation exceeds timeout."""
    pass

def enforce_planning_latency(operation: str, timeout_seconds: float = None):
    """
    Decorator to enforce planning latency targets.

    Args:
        operation: Name of the planning operation
        timeout_seconds: Max allowed duration (optional, uses defaults if not provided)

    Raises:
        PlanningTimeoutError: If operation exceeds timeout
    """
    # Default timeouts from table above
    DEFAULT_TIMEOUTS = {
        "parse_goal": 1.0,
        "decompose_task": 2.0,
        "route_task": 0.5,
        "validate_plan": 0.2,
        "orchestrate_execution": 0.1,
        "replan": 2.0,
        "full_planning_cycle": 3.0
    }

    timeout = timeout_seconds or DEFAULT_TIMEOUTS.get(operation, 5.0)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"

            try:
                # Execute with timeout
                result = func(*args, **kwargs)

                duration = time.time() - start_time
                if duration > timeout:
                    status = "timeout_exceeded"
                    raise PlanningTimeoutError(
                        f"{operation} took {duration:.2f}s (limit: {timeout}s)"
                    )

                return result

            except Exception as e:
                status = "error"
                raise

            finally:
                duration = time.time() - start_time
                PLANNING_LATENCY.labels(operation=operation, status=status).observe(duration)

        return wrapper
    return decorator

# Usage
@enforce_planning_latency("decompose_task")
def decompose_goal(goal: Goal) -> Plan:
    """Decompose goal into subtasks."""
    # Implementation
    pass

@enforce_planning_latency("route_task", timeout_seconds=0.5)
def route_task(task: SubTask, router: SemanticRouter) -> str:
    """Route task to appropriate agent."""
    # Implementation
    pass
```

### 2. Throughput Targets

System must handle concurrent planning requests:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Concurrent Plans | ≥ 10 plans/second | Requests per second (RPS) |
| Max Queue Depth | ≤ 100 pending plans | Queue length monitoring |
| Queue Wait Time | < 500ms (p95) | Time from request to processing |

**Enforcement**:

```python
import asyncio
from asyncio import Queue, Semaphore
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PlanningRequest:
    """A planning request in the queue."""
    request_id: str
    goal: Goal
    submitted_at: datetime
    priority: int = 5

class PlanningQueue:
    """Manages concurrent planning requests with backpressure."""

    def __init__(self, max_concurrent: int = 10, max_queue_depth: int = 100):
        self.max_concurrent = max_concurrent
        self.max_queue_depth = max_queue_depth
        self.semaphore = Semaphore(max_concurrent)
        self.queue = Queue(maxsize=max_queue_depth)
        self.active_plans = 0

    async def submit_planning_request(self, request: PlanningRequest) -> Plan:
        """
        Submit a planning request.

        Args:
            request: The planning request

        Returns:
            The generated plan

        Raises:
            QueueFullError: If queue is at capacity
        """
        # Check queue depth
        if self.queue.qsize() >= self.max_queue_depth:
            raise QueueFullError(
                f"Planning queue full ({self.queue.qsize()}/{self.max_queue_depth})"
            )

        # Record queue entry time
        enqueued_at = datetime.now()

        # Add to queue
        await self.queue.put(request)

        # Wait for available slot
        async with self.semaphore:
            self.active_plans += 1

            try:
                # Measure queue wait time
                wait_time = (datetime.now() - enqueued_at).total_seconds()
                if wait_time > 0.5:  # p95 target
                    logger.warning(
                        f"Planning request {request.request_id} waited {wait_time:.2f}s in queue"
                    )

                # Execute planning
                plan = await self._execute_planning(request)
                return plan

            finally:
                self.active_plans -= 1

    async def _execute_planning(self, request: PlanningRequest) -> Plan:
        """Execute planning for a request."""
        # Implementation calls planning components
        pass
```

### 3. Memory Constraints

Planning operations must stay within memory bounds:

| Component | Memory Limit | Enforcement |
|-----------|--------------|-------------|
| Single Plan Object | < 1MB | Size validation |
| Plan Cache | < 100MB total | LRU eviction |
| Agent Registry | < 10MB | Fixed size |
| Embedding Cache | < 50MB | TTL-based eviction |

**Enforcement**:

```python
import sys
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional

class PlanSizeError(Exception):
    """Raised when plan exceeds size limit."""
    pass

MAX_PLAN_SIZE_BYTES = 1_048_576  # 1MB

def validate_plan_size(plan: Plan) -> None:
    """
    Validate that plan object doesn't exceed size limit.

    Args:
        plan: The plan to validate

    Raises:
        PlanSizeError: If plan exceeds 1MB
    """
    plan_json = plan.model_dump_json()
    size_bytes = sys.getsizeof(plan_json)

    if size_bytes > MAX_PLAN_SIZE_BYTES:
        raise PlanSizeError(
            f"Plan {plan.plan_id} is {size_bytes} bytes (limit: {MAX_PLAN_SIZE_BYTES})"
        )

class PlanCache:
    """LRU cache for plans with size limit."""

    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1_048_576
        self.cache = {}
        self.access_times = {}
        self.current_size = 0

    def get(self, plan_id: str) -> Optional[Plan]:
        """Get plan from cache."""
        if plan_id in self.cache:
            self.access_times[plan_id] = datetime.now()
            return self.cache[plan_id]
        return None

    def put(self, plan: Plan) -> None:
        """Add plan to cache, evicting LRU if needed."""
        plan_size = sys.getsizeof(plan.model_dump_json())

        # Evict until we have space
        while self.current_size + plan_size > self.max_size_bytes and self.cache:
            self._evict_lru()

        # Add to cache
        self.cache[plan.plan_id] = plan
        self.access_times[plan.plan_id] = datetime.now()
        self.current_size += plan_size

    def _evict_lru(self) -> None:
        """Evict least recently used plan."""
        if not self.cache:
            return

        lru_plan_id = min(self.access_times, key=self.access_times.get)
        evicted_plan = self.cache.pop(lru_plan_id)
        del self.access_times[lru_plan_id]

        evicted_size = sys.getsizeof(evicted_plan.model_dump_json())
        self.current_size -= evicted_size

class EmbeddingCache:
    """TTL-based cache for embeddings."""

    def __init__(self, max_size_mb: int = 50, ttl_seconds: int = 3600):
        self.max_size_bytes = max_size_mb * 1_048_576
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.timestamps = {}
        self.current_size = 0

    def get(self, key: str) -> Optional[List[float]]:
        """Get embedding from cache if not expired."""
        if key not in self.cache:
            return None

        # Check if expired
        age = (datetime.now() - self.timestamps[key]).total_seconds()
        if age > self.ttl_seconds:
            self._evict(key)
            return None

        return self.cache[key]

    def put(self, key: str, embedding: List[float]) -> None:
        """Add embedding to cache."""
        embedding_size = sys.getsizeof(embedding)

        # Evict expired entries
        self._evict_expired()

        # Evict oldest if still no space
        while self.current_size + embedding_size > self.max_size_bytes and self.cache:
            oldest_key = min(self.timestamps, key=self.timestamps.get)
            self._evict(oldest_key)

        # Add to cache
        self.cache[key] = embedding
        self.timestamps[key] = datetime.now()
        self.current_size += embedding_size

    def _evict(self, key: str) -> None:
        """Evict a specific key."""
        if key in self.cache:
            embedding = self.cache.pop(key)
            del self.timestamps[key]
            self.current_size -= sys.getsizeof(embedding)

    def _evict_expired(self) -> None:
        """Evict all expired entries."""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if (now - timestamp).total_seconds() > self.ttl_seconds
        ]
        for key in expired_keys:
            self._evict(key)
```

---

## Quality Standards

### 1. Task Completeness

Plans must include all necessary subtasks to achieve the goal.

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task Completeness | > 95% | % of goals with all required tasks identified |
| Missing Task Detection | < 5% false negatives | Manual review of 100 random plans |

**Validation**:

```python
from typing import List, Set

class CompletenessValidator:
    """Validates plan completeness against goal."""

    def __init__(self, goal_templates: dict):
        """
        Initialize with goal templates.

        Args:
            goal_templates: Dict mapping goal_type to required task categories
        """
        self.goal_templates = goal_templates

    def validate_completeness(self, plan: Plan, goal: Goal) -> CompletenessResult:
        """
        Validate that plan includes all necessary tasks.

        Args:
            plan: The plan to validate
            goal: The goal being achieved

        Returns:
            CompletenessResult with score and missing tasks
        """
        # Get required task categories for this goal type
        required_categories = self.goal_templates.get(goal.goal_type, [])

        # Extract task categories from plan
        plan_categories = self._extract_task_categories(plan.subtasks)

        # Find missing categories
        missing = set(required_categories) - plan_categories

        # Calculate completeness score
        completeness_score = (
            len(plan_categories & set(required_categories)) /
            len(required_categories)
        ) if required_categories else 1.0

        return CompletenessResult(
            is_complete=completeness_score >= 0.95,
            completeness_score=completeness_score,
            missing_categories=list(missing),
            covered_categories=list(plan_categories & set(required_categories))
        )

    def _extract_task_categories(self, subtasks: List[SubTask]) -> Set[str]:
        """Extract task categories from subtasks using LLM classification."""
        categories = set()

        for task in subtasks:
            # Classify task into category
            category = self._classify_task(task.description)
            if category:
                categories.add(category)

        return categories

    def _classify_task(self, description: str) -> Optional[str]:
        """Classify task description into category."""
        # Use keyword matching or LLM classification
        keywords = {
            "flight_booking": ["flight", "airplane", "airline", "fly"],
            "hotel_booking": ["hotel", "accommodation", "lodging", "room"],
            "activity_planning": ["activity", "tour", "attraction", "visit"],
            "budget_validation": ["budget", "cost", "price", "expense"],
            "date_validation": ["date", "schedule", "time", "when"]
        }

        description_lower = description.lower()
        for category, words in keywords.items():
            if any(word in description_lower for word in words):
                return category

        return None

# Example goal templates
GOAL_TEMPLATES = {
    GoalType.TRAVEL_PLANNING: [
        "flight_booking",
        "hotel_booking",
        "activity_planning",
        "budget_validation"
    ],
    GoalType.DATA_ANALYSIS: [
        "data_loading",
        "data_cleaning",
        "analysis",
        "visualization",
        "reporting"
    ]
}

validator = CompletenessValidator(goal_templates=GOAL_TEMPLATES)
result = validator.validate_completeness(plan, goal)

if not result.is_complete:
    logger.warning(
        f"Plan {plan.plan_id} incomplete (score: {result.completeness_score:.2f}). "
        f"Missing: {result.missing_categories}"
    )
```

### 2. Dependency Accuracy

Task dependencies must be correctly identified to prevent race conditions.

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dependency Accuracy | > 90% | % of dependencies correctly identified |
| Circular Dependency Detection | 100% | All cycles caught before execution |
| Unnecessary Dependencies | < 10% | % of dependencies that could be removed |

**Validation**:

```python
from typing import List, Set, Tuple

class DependencyValidator:
    """Validates task dependencies in a plan."""

    def validate_dependencies(self, plan: Plan) -> DependencyValidationResult:
        """
        Validate all task dependencies in plan.

        Args:
            plan: The plan to validate

        Returns:
            DependencyValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Build dependency graph
        graph = self._build_dependency_graph(plan.subtasks)

        # Check for circular dependencies
        cycles = self._detect_cycles(graph)
        if cycles:
            errors.append(
                f"Circular dependencies detected: {cycles}"
            )

        # Check for missing dependencies
        missing = self._find_missing_dependencies(plan.subtasks)
        if missing:
            warnings.append(
                f"Potentially missing dependencies: {missing}"
            )

        # Check for unnecessary dependencies
        unnecessary = self._find_unnecessary_dependencies(graph)
        if unnecessary:
            warnings.append(
                f"Potentially unnecessary dependencies: {unnecessary}"
            )

        # Check for dangling dependencies
        dangling = self._find_dangling_dependencies(plan.subtasks)
        if dangling:
            errors.append(
                f"Dependencies reference non-existent tasks: {dangling}"
            )

        is_valid = len(errors) == 0
        accuracy_score = 1.0 - (len(errors) + 0.5 * len(warnings)) / max(1, len(plan.subtasks))

        return DependencyValidationResult(
            is_valid=is_valid,
            accuracy_score=max(0.0, accuracy_score),
            errors=errors,
            warnings=warnings
        )

    def _build_dependency_graph(self, subtasks: List[SubTask]) -> dict:
        """Build adjacency list representation of dependencies."""
        graph = {task.task_id: task.dependencies for task in subtasks}
        return graph

    def _detect_cycles(self, graph: dict) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _find_missing_dependencies(self, subtasks: List[SubTask]) -> List[Tuple[str, str]]:
        """
        Find potentially missing dependencies using heuristics.

        Returns:
            List of (task_id, suggested_dependency) tuples
        """
        missing = []

        # Heuristic: Tasks that use outputs from other tasks should depend on them
        task_outputs = {task.task_id: task.expected_outputs for task in subtasks}

        for task in subtasks:
            # Check if task inputs match any other task's outputs
            for other_task in subtasks:
                if other_task.task_id == task.task_id:
                    continue

                # If other task produces output that this task might need
                for output in other_task.expected_outputs:
                    for input_key, input_value in task.inputs.items():
                        if output.lower() in input_value.lower():
                            # This task might depend on other_task
                            if other_task.task_id not in task.dependencies:
                                missing.append((task.task_id, other_task.task_id))

        return missing

    def _find_unnecessary_dependencies(self, graph: dict) -> List[Tuple[str, str]]:
        """
        Find dependencies that could be removed (transitive dependencies).

        Returns:
            List of (task_id, unnecessary_dependency) tuples
        """
        unnecessary = []

        for task_id, deps in graph.items():
            for dep in deps:
                # Check if there's a path to dep through other dependencies
                other_deps = [d for d in deps if d != dep]
                if self._has_path_through(dep, other_deps, graph):
                    unnecessary.append((task_id, dep))

        return unnecessary

    def _has_path_through(self, target: str, intermediates: List[str], graph: dict) -> bool:
        """Check if target is reachable through any intermediate node."""
        for intermediate in intermediates:
            if self._has_path(intermediate, target, graph):
                return True
        return False

    def _has_path(self, start: str, end: str, graph: dict) -> bool:
        """Check if there's a path from start to end."""
        visited = set()
        queue = [start]

        while queue:
            node = queue.pop(0)
            if node == end:
                return True

            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        return False

    def _find_dangling_dependencies(self, subtasks: List[SubTask]) -> List[Tuple[str, str]]:
        """Find dependencies that reference non-existent tasks."""
        task_ids = {task.task_id for task in subtasks}
        dangling = []

        for task in subtasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    dangling.append((task.task_id, dep))

        return dangling

# Usage
validator = DependencyValidator()
result = validator.validate_dependencies(plan)

if not result.is_valid:
    raise PlanValidationError(f"Plan has dependency errors: {result.errors}")

if result.warnings:
    logger.warning(f"Plan has dependency warnings: {result.warnings}")
```

### 3. Agent Assignment Accuracy

Tasks must be routed to agents capable of executing them.

| Metric | Target | Measurement |
|--------|--------|-------------|
| Assignment Accuracy | > 85% | % of tasks assigned to optimal agent |
| Assignment Failures | < 5% | % of tasks where assigned agent cannot execute |

**Validation**:

```python
class AssignmentValidator:
    """Validates agent assignments in a plan."""

    def __init__(self, agent_registry: List[AgentCapability]):
        self.agent_registry = {agent.agent_type: agent for agent in agent_registry}

    def validate_assignments(self, plan: Plan) -> AssignmentValidationResult:
        """
        Validate all agent assignments in plan.

        Args:
            plan: The plan to validate

        Returns:
            AssignmentValidationResult with validation details
        """
        errors = []
        warnings = []
        total_tasks = len(plan.subtasks)
        valid_assignments = 0

        for task in plan.subtasks:
            # Check if agent exists
            if task.agent_type not in self.agent_registry:
                errors.append(
                    f"Task {task.task_id} assigned to unknown agent: {task.agent_type}"
                )
                continue

            agent = self.agent_registry[task.agent_type]

            # Check if agent can handle task
            can_handle, confidence = self._agent_can_handle_task(agent, task)

            if not can_handle:
                errors.append(
                    f"Task {task.task_id} cannot be handled by {task.agent_type}"
                )
            elif confidence < 0.7:
                warnings.append(
                    f"Task {task.task_id} assigned to {task.agent_type} with low confidence: {confidence:.2f}"
                )
                valid_assignments += 1
            else:
                valid_assignments += 1

        accuracy_score = valid_assignments / total_tasks if total_tasks > 0 else 0.0

        return AssignmentValidationResult(
            is_valid=len(errors) == 0,
            accuracy_score=accuracy_score,
            errors=errors,
            warnings=warnings
        )

    def _agent_can_handle_task(self, agent: AgentCapability, task: SubTask) -> Tuple[bool, float]:
        """
        Check if agent can handle task.

        Returns:
            Tuple of (can_handle: bool, confidence: float)
        """
        # Extract required capabilities from task
        required_capabilities = self._extract_required_capabilities(task)

        # Check overlap with agent capabilities
        agent_caps_set = set(agent.capabilities)
        required_caps_set = set(required_capabilities)

        overlap = agent_caps_set & required_caps_set
        if not overlap:
            return False, 0.0

        # Calculate confidence based on coverage
        coverage = len(overlap) / len(required_caps_set) if required_caps_set else 0.0

        # Adjust for agent's historical success rate
        confidence = coverage * agent.success_rate

        can_handle = confidence >= 0.5
        return can_handle, confidence

    def _extract_required_capabilities(self, task: SubTask) -> List[str]:
        """Extract required capabilities from task description."""
        # Use keyword matching or LLM extraction
        capability_keywords = {
            "search_flights": ["search flight", "find flight", "flight option"],
            "book_flights": ["book flight", "reserve flight", "purchase flight"],
            "search_hotels": ["search hotel", "find hotel", "hotel option"],
            "book_rooms": ["book hotel", "reserve room", "book accommodation"],
            "search_activities": ["search activity", "find activity", "recommend attraction"],
            "validate_budget": ["validate budget", "check cost", "verify price"]
        }

        required = []
        desc_lower = task.description.lower()

        for capability, keywords in capability_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                required.append(capability)

        return required if required else ["general_execution"]

# Usage
validator = AssignmentValidator(agent_registry=agents)
result = validator.validate_assignments(plan)

if not result.is_valid:
    raise PlanValidationError(f"Plan has assignment errors: {result.errors}")
```

### 4. Confidence Calibration

Plan confidence scores must correlate with actual success rates.

| Metric | Target | Measurement |
|--------|--------|-------------|
| Confidence Calibration | r > 0.7 | Pearson correlation between confidence_score and success |
| Over-confidence Rate | < 15% | % of plans with confidence > 0.8 that fail |
| Under-confidence Rate | < 15% | % of plans with confidence < 0.5 that succeed |

**Measurement**:

```python
import numpy as np
from scipy.stats import pearsonr
from dataclasses import dataclass
from typing import List

@dataclass
class PlanOutcome:
    """Outcome of a plan execution."""
    plan_id: str
    confidence_score: float
    success: bool  # Did plan achieve goal?
    execution_time: float
    cost: float

class ConfidenceCalibrator:
    """Tracks and calibrates plan confidence scores."""

    def __init__(self):
        self.outcomes: List[PlanOutcome] = []

    def record_outcome(self, outcome: PlanOutcome) -> None:
        """Record a plan execution outcome."""
        self.outcomes.append(outcome)

    def calculate_calibration(self) -> CalibrationMetrics:
        """
        Calculate confidence calibration metrics.

        Returns:
            CalibrationMetrics with correlation and error rates
        """
        if len(self.outcomes) < 10:
            return CalibrationMetrics(
                correlation=0.0,
                over_confidence_rate=0.0,
                under_confidence_rate=0.0,
                sample_size=len(self.outcomes),
                message="Insufficient data (need >= 10 outcomes)"
            )

        # Extract confidence scores and success flags
        confidences = np.array([o.confidence_score for o in self.outcomes])
        successes = np.array([1.0 if o.success else 0.0 for o in self.outcomes])

        # Calculate Pearson correlation
        correlation, p_value = pearsonr(confidences, successes)

        # Calculate over-confidence rate
        high_confidence = [o for o in self.outcomes if o.confidence_score > 0.8]
        over_confident = sum(1 for o in high_confidence if not o.success)
        over_confidence_rate = (
            over_confident / len(high_confidence) if high_confidence else 0.0
        )

        # Calculate under-confidence rate
        low_confidence = [o for o in self.outcomes if o.confidence_score < 0.5]
        under_confident = sum(1 for o in low_confidence if o.success)
        under_confidence_rate = (
            under_confident / len(low_confidence) if low_confidence else 0.0
        )

        return CalibrationMetrics(
            correlation=correlation,
            over_confidence_rate=over_confidence_rate,
            under_confidence_rate=under_confidence_rate,
            sample_size=len(self.outcomes),
            p_value=p_value
        )

    def adjust_confidence(self, raw_confidence: float) -> float:
        """
        Adjust confidence score based on historical calibration.

        Args:
            raw_confidence: Raw confidence from planner

        Returns:
            Calibrated confidence score
        """
        metrics = self.calculate_calibration()

        if metrics.sample_size < 10:
            # Not enough data, return raw
            return raw_confidence

        # If over-confident, reduce high scores
        if metrics.over_confidence_rate > 0.15:
            if raw_confidence > 0.8:
                adjustment = -0.1 * metrics.over_confidence_rate
                return max(0.0, min(1.0, raw_confidence + adjustment))

        # If under-confident, increase low scores
        if metrics.under_confidence_rate > 0.15:
            if raw_confidence < 0.5:
                adjustment = 0.1 * metrics.under_confidence_rate
                return max(0.0, min(1.0, raw_confidence + adjustment))

        return raw_confidence

# Usage
calibrator = ConfidenceCalibrator()

# After each plan execution
outcome = PlanOutcome(
    plan_id=plan.plan_id,
    confidence_score=plan.confidence_score,
    success=True,  # or False
    execution_time=12.5,
    cost=0.08
)
calibrator.record_outcome(outcome)

# Check calibration metrics
metrics = calibrator.calculate_calibration()
if metrics.correlation < 0.7:
    logger.warning(
        f"Confidence poorly calibrated (r={metrics.correlation:.2f}). "
        f"Over-confidence: {metrics.over_confidence_rate:.1%}, "
        f"Under-confidence: {metrics.under_confidence_rate:.1%}"
    )

# Adjust future confidence scores
adjusted_confidence = calibrator.adjust_confidence(plan.confidence_score)
```

---

## Cost Budgets

### 1. LLM API Costs

Planning operations must stay within cost budgets:

| Operation | Cost Budget | Enforcement |
|-----------|-------------|-------------|
| Goal Parsing | < $0.002 | Token counting |
| Task Decomposition | < $0.005 | Token counting |
| Plan Revision | < $0.003 | Token counting |
| Full Planning Cycle | < $0.01 | Cumulative tracking |

**Enforcement**:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CostTracking:
    """Tracks costs for a planning operation."""
    operation: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    budget_usd: float
    timestamp: datetime

class PlanningCostTracker:
    """Tracks and enforces cost budgets for planning."""

    # Pricing (example for GPT-4)
    COST_PER_1K_PROMPT_TOKENS = 0.03  # $0.03 per 1K tokens
    COST_PER_1K_COMPLETION_TOKENS = 0.06  # $0.06 per 1K tokens

    # Budgets (from table above)
    BUDGETS = {
        "parse_goal": 0.002,
        "decompose_task": 0.005,
        "replan": 0.003,
        "full_planning_cycle": 0.01
    }

    def __init__(self):
        self.cost_history: List[CostTracking] = []
        self.current_cycle_cost = 0.0

    def track_llm_call(
        self,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> CostTracking:
        """
        Track cost of an LLM API call.

        Args:
            operation: Name of the planning operation
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            CostTracking record

        Raises:
            BudgetExceededError: If operation exceeds budget
        """
        # Calculate cost
        cost = (
            (prompt_tokens / 1000) * self.COST_PER_1K_PROMPT_TOKENS +
            (completion_tokens / 1000) * self.COST_PER_1K_COMPLETION_TOKENS
        )

        # Get budget for this operation
        budget = self.BUDGETS.get(operation, 0.01)

        # Check if budget exceeded
        if cost > budget:
            raise BudgetExceededError(
                f"{operation} cost ${cost:.4f} exceeds budget ${budget:.4f}"
            )

        # Record cost
        tracking = CostTracking(
            operation=operation,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            budget_usd=budget,
            timestamp=datetime.now()
        )
        self.cost_history.append(tracking)
        self.current_cycle_cost += cost

        return tracking

    def start_planning_cycle(self) -> None:
        """Start tracking a new planning cycle."""
        self.current_cycle_cost = 0.0

    def end_planning_cycle(self) -> float:
        """
        End planning cycle and return total cost.

        Returns:
            Total cost for the cycle

        Raises:
            BudgetExceededError: If cycle exceeds budget
        """
        cycle_budget = self.BUDGETS["full_planning_cycle"]

        if self.current_cycle_cost > cycle_budget:
            raise BudgetExceededError(
                f"Planning cycle cost ${self.current_cycle_cost:.4f} "
                f"exceeds budget ${cycle_budget:.4f}"
            )

        return self.current_cycle_cost

# Usage with LLM calls
cost_tracker = PlanningCostTracker()

cost_tracker.start_planning_cycle()

# Track goal parsing
response = openai_client.chat.completions.create(...)
cost_tracker.track_llm_call(
    operation="parse_goal",
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens
)

# Track task decomposition
response = openai_client.chat.completions.create(...)
cost_tracker.track_llm_call(
    operation="decompose_task",
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens
)

# End cycle
total_cost = cost_tracker.end_planning_cycle()
print(f"Planning cycle cost: ${total_cost:.4f}")
```

### 2. Embedding API Costs

Semantic routing requires embeddings:

| Operation | Cost Budget | Enforcement |
|-----------|-------------|-------------|
| Task Embedding | < $0.0001 per task | Token counting |
| Agent Embedding (cached) | $0.001 one-time | Pre-computed at startup |
| Routing per Task | < $0.001 | Cumulative tracking |

**Enforcement**:

```python
class EmbeddingCostTracker:
    """Tracks embedding API costs."""

    # Pricing (example for text-embedding-3-small)
    COST_PER_1K_TOKENS = 0.00002  # $0.00002 per 1K tokens

    def __init__(self):
        self.total_cost = 0.0
        self.call_count = 0

    def track_embedding_call(self, text: str, tokens: int) -> float:
        """
        Track cost of an embedding API call.

        Args:
            text: The text being embedded
            tokens: Number of tokens

        Returns:
            Cost of this call
        """
        cost = (tokens / 1000) * self.COST_PER_1K_TOKENS
        self.total_cost += cost
        self.call_count += 1

        return cost

# Usage
embedding_tracker = EmbeddingCostTracker()

# Embed task
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=task.description
)
tokens = response.usage.total_tokens
cost = embedding_tracker.track_embedding_call(task.description, tokens)

print(f"Embedding cost: ${cost:.6f}")
print(f"Total embedding cost: ${embedding_tracker.total_cost:.6f}")
```

---

## Testing and Validation

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch
import time

class TestPlanningPerformance:
    """Test planning performance constraints."""

    def test_goal_parsing_latency(self):
        """Goal parsing must complete in < 1s."""
        planner = TravelPlanningAgent(openai_api_key="test")

        start = time.time()
        goal = planner._parse_goal("Plan a trip to Paris for 3 days in May")
        duration = time.time() - start

        assert duration < 1.0, f"Goal parsing took {duration:.2f}s (limit: 1s)"
        assert goal.goal_type == GoalType.TRAVEL_PLANNING
        assert len(goal.constraints) > 0

    def test_task_decomposition_latency(self):
        """Task decomposition must complete in < 2s."""
        planner = TravelPlanningAgent(openai_api_key="test")
        goal = Goal(
            goal_id="test_goal",
            goal_type=GoalType.TRAVEL_PLANNING,
            description="Test travel goal",
            constraints=[],
            success_criteria=["Test criteria"]
        )

        start = time.time()
        plan = planner._decompose_goal(goal)
        duration = time.time() - start

        assert duration < 2.0, f"Decomposition took {duration:.2f}s (limit: 2s)"
        assert len(plan.subtasks) > 0

    def test_routing_latency(self):
        """Agent routing must complete in < 500ms per task."""
        router = SemanticRouter(agents=test_agents, embedding_fn=mock_embedding_fn)
        task = SubTask(
            task_id="test_task",
            description="Search for flights",
            agent_type="TBD",
            dependencies=[],
            expected_outputs=["flight_results"]
        )

        start = time.time()
        recommendations = router.route_task(task, top_k=3)
        duration = time.time() - start

        assert duration < 0.5, f"Routing took {duration:.2f}s (limit: 0.5s)"
        assert len(recommendations) > 0

    def test_plan_size_limit(self):
        """Plans must not exceed 1MB."""
        large_plan = Plan(
            plan_id="large_plan",
            goal_id="test_goal",
            subtasks=[
                SubTask(
                    task_id=f"task_{i}",
                    description="x" * 10000,  # Large description
                    agent_type="test_agent",
                    dependencies=[],
                    expected_outputs=["output"]
                )
                for i in range(100)  # 100 large tasks
            ],
            execution_strategy="sequential",
            estimated_total_duration=1000,
            confidence_score=0.8
        )

        with pytest.raises(PlanSizeError):
            validate_plan_size(large_plan)

class TestPlanningQuality:
    """Test planning quality standards."""

    def test_completeness_validation(self):
        """Plans must include all required tasks."""
        validator = CompletenessValidator(goal_templates=GOAL_TEMPLATES)

        # Complete plan
        complete_plan = Plan(
            plan_id="complete",
            goal_id="test_goal",
            subtasks=[
                SubTask(task_id="1", description="Search flights", agent_type="flight", dependencies=[], expected_outputs=["flights"]),
                SubTask(task_id="2", description="Search hotels", agent_type="hotel", dependencies=[], expected_outputs=["hotels"]),
                SubTask(task_id="3", description="Plan activities", agent_type="activity", dependencies=[], expected_outputs=["activities"]),
                SubTask(task_id="4", description="Validate budget", agent_type="validator", dependencies=[], expected_outputs=["validation"])
            ],
            execution_strategy="sequential",
            estimated_total_duration=100,
            confidence_score=0.9
        )

        goal = Goal(
            goal_id="test_goal",
            goal_type=GoalType.TRAVEL_PLANNING,
            description="Test goal",
            constraints=[],
            success_criteria=[]
        )

        result = validator.validate_completeness(complete_plan, goal)
        assert result.is_complete
        assert result.completeness_score >= 0.95

    def test_dependency_cycle_detection(self):
        """Must detect circular dependencies."""
        validator = DependencyValidator()

        # Plan with circular dependency: A -> B -> C -> A
        cyclic_plan = Plan(
            plan_id="cyclic",
            goal_id="test_goal",
            subtasks=[
                SubTask(task_id="A", description="Task A", agent_type="test", dependencies=["C"], expected_outputs=["a"]),
                SubTask(task_id="B", description="Task B", agent_type="test", dependencies=["A"], expected_outputs=["b"]),
                SubTask(task_id="C", description="Task C", agent_type="test", dependencies=["B"], expected_outputs=["c"])
            ],
            execution_strategy="sequential",
            estimated_total_duration=100,
            confidence_score=0.8
        )

        result = validator.validate_dependencies(cyclic_plan)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "circular" in str(result.errors).lower()

    def test_confidence_calibration(self):
        """Confidence scores must correlate with success."""
        calibrator = ConfidenceCalibrator()

        # Record outcomes
        outcomes = [
            PlanOutcome("1", 0.9, True, 10.0, 0.05),   # High confidence, success
            PlanOutcome("2", 0.8, True, 12.0, 0.06),   # High confidence, success
            PlanOutcome("3", 0.7, True, 11.0, 0.055),  # Medium confidence, success
            PlanOutcome("4", 0.5, False, 8.0, 0.04),   # Medium confidence, failure
            PlanOutcome("5", 0.3, False, 7.0, 0.03),   # Low confidence, failure
            PlanOutcome("6", 0.2, False, 6.0, 0.025),  # Low confidence, failure
            PlanOutcome("7", 0.85, True, 11.5, 0.055), # High confidence, success
            PlanOutcome("8", 0.75, True, 10.5, 0.05),  # Medium confidence, success
            PlanOutcome("9", 0.4, False, 7.5, 0.035),  # Low confidence, failure
            PlanOutcome("10", 0.6, True, 9.0, 0.045)   # Medium confidence, success
        ]

        for outcome in outcomes:
            calibrator.record_outcome(outcome)

        metrics = calibrator.calculate_calibration()
        assert metrics.correlation > 0.7, f"Correlation {metrics.correlation:.2f} < 0.7"
        assert metrics.over_confidence_rate < 0.15
        assert metrics.under_confidence_rate < 0.15

class TestPlanningCosts:
    """Test planning cost budgets."""

    def test_goal_parsing_cost(self):
        """Goal parsing must cost < $0.002."""
        tracker = PlanningCostTracker()

        # Typical goal parsing: ~200 prompt tokens, ~100 completion tokens
        tracking = tracker.track_llm_call(
            operation="parse_goal",
            prompt_tokens=200,
            completion_tokens=100
        )

        assert tracking.cost_usd < 0.002, f"Cost ${tracking.cost_usd:.4f} exceeds budget"

    def test_full_cycle_cost(self):
        """Full planning cycle must cost < $0.01."""
        tracker = PlanningCostTracker()
        tracker.start_planning_cycle()

        # Goal parsing
        tracker.track_llm_call("parse_goal", 200, 100)

        # Task decomposition
        tracker.track_llm_call("decompose_task", 400, 300)

        # End cycle
        total_cost = tracker.end_planning_cycle()
        assert total_cost < 0.01, f"Cycle cost ${total_cost:.4f} exceeds budget $0.01"
```

---

## Métricas de Monitoreo

### Dashboards

**Planning Performance Dashboard** (Grafana/Prometheus):

```yaml
panels:
  - title: "Planning Latency (p95)"
    query: histogram_quantile(0.95, planning_operation_latency_seconds)
    thresholds:
      - value: 1.0
        color: green
      - value: 2.0
        color: yellow
      - value: 3.0
        color: red

  - title: "Planning Success Rate"
    query: rate(planning_success_total) / rate(planning_attempts_total)
    thresholds:
      - value: 0.85
        color: red
      - value: 0.90
        color: yellow
      - value: 0.95
        color: green

  - title: "Planning Cost per Cycle"
    query: avg(planning_cost_usd)
    thresholds:
      - value: 0.01
        color: green
      - value: 0.015
        color: yellow
      - value: 0.02
        color: red

  - title: "Confidence Calibration"
    query: planning_confidence_correlation
    thresholds:
      - value: 0.5
        color: red
      - value: 0.7
        color: yellow
      - value: 0.8
        color: green
```

### Alerts

```yaml
alerts:
  - name: "High Planning Latency"
    condition: planning_operation_latency_seconds{quantile="0.95"} > 3.0
    severity: warning
    message: "Planning latency p95 exceeds 3s threshold"

  - name: "Low Planning Success Rate"
    condition: rate(planning_success_total) / rate(planning_attempts_total) < 0.85
    severity: critical
    message: "Planning success rate below 85%"

  - name: "Planning Cost Exceeded"
    condition: avg(planning_cost_usd) > 0.015
    severity: warning
    message: "Average planning cost exceeds $0.015 per cycle"

  - name: "Poor Confidence Calibration"
    condition: planning_confidence_correlation < 0.7
    severity: warning
    message: "Confidence calibration below 0.7"
```

---

## Referencias

1. [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
2. [RT-009: Metacognition Performance Constraints](./RT-009_metacognition_performance_constraints.md)
3. [RT-011: Multi-Agent Communication Coordination](./RT-011_multi_agent_communication_coordination.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
