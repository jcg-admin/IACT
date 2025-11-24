# UC-SYS-006: Planning and Replanning Workflow

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Planning Design
**Actor Principal**: Planning System (Goal Definition, Task Decomposition, Semantic Router, Iterative Planner)
**Stakeholders**: User, Specialized Agents (Flight, Hotel, Activity, etc.)
**Relación**:
- Implementa [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
- Sigue [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
- Relacionado con [UC-SYS-005: Multi-Agent Orchestration](./UC-SYS-005_multi_agent_orchestration.md)

---

## Descripción

El sistema de Planning convierte solicitudes de usuario en natural language en planes estructurados y ejecutables, descompone objetivos complejos en subtareas, asigna agentes especializados mediante semantic routing, y adapta planes basándose en feedback de ejecución.

**Objetivo**: Demostrar el ciclo completo de planning desde goal definition hasta iterative refinement, incluyendo:
1. Parsing de natural language a structured Goal
2. Decomposition de goals en SubTasks con dependencies
3. Semantic routing para agent assignment
4. Execution orchestration
5. Iterative re-planning en caso de failures

---

## Precondiciones

1. **Agent Registry disponible**: Al menos 3 agents especializados registrados con capabilities
2. **Embedding API activa**: OpenAI embeddings API para semantic routing (< 300ms latency)
3. **LLM API activa**: GPT-4 para goal parsing y task decomposition (< 2s latency)
4. **Plan Cache inicializado**: LRU cache con max 100MB
5. **Cost Tracker inicializado**: Budget tracking para operaciones de planning
6. **Confidence Calibrator**: Al menos 10 outcomes históricos para calibration (opcional)

---

## Postcondiciones

### Éxito
1. **Plan generado y validado**: Plan con confidence_score >= 0.7, all subtasks tienen agent assignments
2. **Dependencies válidas**: No circular dependencies, no dangling dependencies
3. **Budget respetado**: Total planning cost < $0.01
4. **Latency objetivo cumplido**: Full planning cycle < 3s (p95)
5. **Plan ejecutado**: All subtasks completed o revised plan generado si hay failures

### Fracaso
1. **Plan inválido**: Circular dependencies detectadas, plan rechazado
2. **Budget excedido**: Planning cost > $0.01, operación abortada
3. **Timeout excedido**: Planning latency > 3s, operación cancelada
4. **Max revisions alcanzado**: Plan revisado 3 veces sin éxito, abortado
5. **Low confidence**: Plan confidence < 0.3 después de revisiones, abortado

---

## Flujo Principal

### Escenario: "Plan a 3-day trip to Paris in May with a $2000 budget"

**Contexto**: Usuario quiere planear un viaje a París, sistema debe generar plan completo incluyendo vuelos, hotel, y actividades, y adaptarse si algún componente falla.

#### Paso 1: Goal Definition (< 1s)

**Input**: Natural language request
```
"Plan a 3-day trip to Paris in May with a $2000 budget"
```

**Proceso**:
```python
# 1.1. Parse natural language usando LLM
system_prompt = """You are a travel planning assistant.
Extract structured information from user requests.
Return JSON with: destination, duration_days, budget, dates, preferences."""

response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request}
    ],
    response_format={"type": "json_object"}
)

extracted = {
    "destination": "Paris",
    "duration_days": 3,
    "budget": "2000 USD",
    "dates": "May 2025",
    "preferences": []
}

# 1.2. Create structured Goal object (Pydantic validation)
goal = Goal(
    goal_id="goal_abc123",
    goal_type=GoalType.TRAVEL_PLANNING,
    description="Plan a 3-day trip to Paris in May with a $2000 budget",
    constraints=[
        Constraint(type="budget", value="2000 USD", priority=10),
        Constraint(type="duration", value="3 days", priority=9),
        Constraint(type="time", value="May 2025", priority=8)
    ],
    success_criteria=[
        "Round-trip flight booked within budget",
        "Hotel for 3 nights in central Paris",
        "At least 5 activities planned",
        "Total cost <= $2000"
    ],
    deadline=datetime(2025, 4, 15),
    priority=7
)
```

**Output**:
```json
{
  "goal_id": "goal_abc123",
  "goal_type": "travel_planning",
  "description": "Plan a 3-day trip to Paris in May with a $2000 budget",
  "constraints": [
    {"type": "budget", "value": "2000 USD", "priority": 10},
    {"type": "duration", "value": "3 days", "priority": 9},
    {"type": "time", "value": "May 2025", "priority": 8}
  ],
  "success_criteria": [
    "Round-trip flight booked within budget",
    "Hotel for 3 nights in central Paris",
    "At least 5 activities planned",
    "Total cost <= $2000"
  ]
}
```

**Metrics**:
- Latency: 850ms (target: < 1s) ✓
- Cost: $0.0018 (target: < $0.002) ✓

---

#### Paso 2: Task Decomposition (< 2s)

**Input**: Structured Goal

**Proceso**:
```python
# 2.1. Generate subtasks usando LLM
system_prompt = """You are a task decomposition expert.
Break down the travel goal into specific subtasks.
Return JSON array with: description, dependencies (task indices), priority, estimated_duration_seconds."""

response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Goal: {goal.description}\nConstraints: {goal.constraints}"}
    ],
    response_format={"type": "json_object"}
)

tasks_data = [
    {
        "description": "Search for round-trip flights to Paris in May",
        "dependencies": [],
        "priority": 10,
        "estimated_duration_seconds": 30
    },
    {
        "description": "Find hotels in central Paris for 3 nights",
        "dependencies": [0],  # Needs flight dates
        "priority": 9,
        "estimated_duration_seconds": 25
    },
    {
        "description": "Recommend 5+ tourist activities in Paris",
        "dependencies": [],  # Can run in parallel
        "priority": 7,
        "estimated_duration_seconds": 20
    },
    {
        "description": "Validate total cost against $2000 budget",
        "dependencies": [0, 1, 2],  # Needs all pricing
        "priority": 10,
        "estimated_duration_seconds": 5
    }
]

# 2.2. Create SubTask objects (Pydantic validation)
subtasks = []
for i, task_data in enumerate(tasks_data):
    subtask = SubTask(
        task_id=f"task_{i+1:03d}",
        description=task_data["description"],
        agent_type="TBD",  # Assigned in next step
        dependencies=[f"task_{dep+1:03d}" for dep in task_data.get("dependencies", [])],
        inputs={},
        expected_outputs=[f"output_{i+1}"],
        priority=task_data.get("priority", 5),
        estimated_duration_seconds=task_data.get("estimated_duration_seconds", 30),
        status=TaskStatus.PENDING
    )
    subtasks.append(subtask)

# 2.3. Create Plan object
plan = Plan(
    plan_id="plan_xyz789",
    goal_id=goal.goal_id,
    subtasks=subtasks,
    execution_strategy="hybrid",  # Parallel where possible, sequential where required
    estimated_total_duration=80,  # Sum of task durations (assumes some parallelization)
    confidence_score=0.85,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# 2.4. Validate plan
validate_plan_size(plan)  # Ensure < 1MB
dependency_result = dependency_validator.validate_dependencies(plan)
if not dependency_result.is_valid:
    raise PlanValidationError(f"Invalid dependencies: {dependency_result.errors}")
```

**Output**:
```json
{
  "plan_id": "plan_xyz789",
  "goal_id": "goal_abc123",
  "subtasks": [
    {
      "task_id": "task_001",
      "description": "Search for round-trip flights to Paris in May",
      "agent_type": "TBD",
      "dependencies": [],
      "expected_outputs": ["output_1"],
      "priority": 10,
      "estimated_duration_seconds": 30,
      "status": "pending"
    },
    {
      "task_id": "task_002",
      "description": "Find hotels in central Paris for 3 nights",
      "agent_type": "TBD",
      "dependencies": ["task_001"],
      "expected_outputs": ["output_2"],
      "priority": 9,
      "estimated_duration_seconds": 25,
      "status": "pending"
    },
    {
      "task_id": "task_003",
      "description": "Recommend 5+ tourist activities in Paris",
      "agent_type": "TBD",
      "dependencies": [],
      "expected_outputs": ["output_3"],
      "priority": 7,
      "estimated_duration_seconds": 20,
      "status": "pending"
    },
    {
      "task_id": "task_004",
      "description": "Validate total cost against $2000 budget",
      "agent_type": "TBD",
      "dependencies": ["task_001", "task_002", "task_003"],
      "expected_outputs": ["output_4"],
      "priority": 10,
      "estimated_duration_seconds": 5,
      "status": "pending"
    }
  ],
  "execution_strategy": "hybrid",
  "estimated_total_duration": 80,
  "confidence_score": 0.85
}
```

**Metrics**:
- Latency: 1.75s (target: < 2s) ✓
- Cost: $0.0042 (target: < $0.005) ✓
- Subtasks: 4 tasks created
- Dependencies: Valid, no cycles ✓

---

#### Paso 3: Semantic Routing (< 500ms per task)

**Input**: Plan with unassigned subtasks

**Available Agents**:
```python
agents = [
    AgentCapability(
        agent_type="flight_agent",
        capabilities=["search_flights", "compare_prices", "book_flights"],
        specialization="Flight booking and price comparison for domestic and international travel",
        cost_per_invocation=0.02,
        avg_latency_ms=1500,
        success_rate=0.92
    ),
    AgentCapability(
        agent_type="hotel_agent",
        capabilities=["search_hotels", "check_availability", "book_rooms", "compare_amenities"],
        specialization="Hotel search and reservation with filtering by location, price, and amenities",
        cost_per_invocation=0.015,
        avg_latency_ms=1200,
        success_rate=0.95
    ),
    AgentCapability(
        agent_type="activity_agent",
        capabilities=["search_activities", "recommend_attractions", "book_tours", "create_itineraries"],
        specialization="Tourist activities, attractions, and local experiences recommendation",
        cost_per_invocation=0.01,
        avg_latency_ms=800,
        success_rate=0.88
    ),
    AgentCapability(
        agent_type="validation_agent",
        capabilities=["validate_budget", "check_constraints", "verify_completeness"],
        specialization="Validate plans against budgets, constraints, and business rules",
        cost_per_invocation=0.005,
        avg_latency_ms=300,
        success_rate=0.98
    )
]

router = SemanticRouter(agents=agents, embedding_fn=openai_embedding_function)
```

**Proceso para cada subtask**:
```python
# Task 001: "Search for round-trip flights to Paris in May"
task_embedding = embed("Search for round-trip flights to Paris in May. Expected outputs: output_1")
# Shape: [1536] float array

# Calculate similarity with each agent
agent_scores = []

# flight_agent embedding (pre-computed)
flight_embedding = embed("Flight booking and price comparison for domestic and international travel. Capabilities: search_flights, compare_prices, book_flights")
similarity = cosine_similarity(task_embedding, flight_embedding) # 0.92

# Adjust for performance metrics
adjusted_score = 0.92 * 0.92 * (1 - 0.02/10) = 0.843

agent_scores.append(("flight_agent", 0.843))

# hotel_agent embedding
hotel_embedding = embed("Hotel search and reservation with filtering by location, price, and amenities. Capabilities: search_hotels, check_availability, book_rooms, compare_amenities")
similarity = cosine_similarity(task_embedding, hotel_embedding) # 0.35
adjusted_score = 0.35 * 0.95 * (1 - 0.015/10) = 0.333
agent_scores.append(("hotel_agent", 0.333))

# activity_agent: 0.28
# validation_agent: 0.15

# Sort by score
agent_scores.sort(key=lambda x: x[1], reverse=True)
# Result: [("flight_agent", 0.843), ("hotel_agent", 0.333), ...]

# Assign top agent
task_001.agent_type = "flight_agent"
```

**Routing Results**:
```
task_001: "Search for round-trip flights to Paris in May"
  → flight_agent (score: 0.843, latency: 1500ms, success_rate: 0.92)

task_002: "Find hotels in central Paris for 3 nights"
  → hotel_agent (score: 0.901, latency: 1200ms, success_rate: 0.95)

task_003: "Recommend 5+ tourist activities in Paris"
  → activity_agent (score: 0.875, latency: 800ms, success_rate: 0.88)

task_004: "Validate total cost against $2000 budget"
  → validation_agent (score: 0.912, latency: 300ms, success_rate: 0.98)
```

**Metrics**:
- Routing time: 420ms per task (target: < 500ms) ✓
- Embedding cost: $0.0004 per task (target: < $0.001) ✓
- Assignment accuracy: 100% (all agents match task requirements) ✓

---

#### Paso 4: Plan Validation

**Proceso**:
```python
# 4.1. Validate completeness
completeness_result = completeness_validator.validate_completeness(plan, goal)
# Expected categories: ["flight_booking", "hotel_booking", "activity_planning", "budget_validation"]
# Covered: ["flight_booking", "hotel_booking", "activity_planning", "budget_validation"]
# Completeness score: 1.0 (100%)

assert completeness_result.is_complete, f"Plan incomplete: {completeness_result.missing_categories}"

# 4.2. Validate dependencies (already done in step 2)
# No cycles, no dangling deps ✓

# 4.3. Validate agent assignments
assignment_result = assignment_validator.validate_assignments(plan)
# All agents exist and can handle assigned tasks
# Accuracy score: 1.0 (100%)

assert assignment_result.is_valid, f"Invalid assignments: {assignment_result.errors}"

# 4.4. Adjust confidence based on calibration
calibrated_confidence = confidence_calibrator.adjust_confidence(plan.confidence_score)
# Original: 0.85, Calibrated: 0.83 (slight reduction due to historical over-confidence)
plan.confidence_score = calibrated_confidence
```

**Validation Results**:
```
✓ Completeness: 100% (all required tasks present)
✓ Dependencies: Valid (no cycles, no dangling)
✓ Assignments: 100% accuracy (all agents capable)
✓ Confidence: 0.83 (calibrated from 0.85)
```

---

#### Paso 5: Plan Execution (Orchestrated)

**Execution Strategy**: Hybrid (parallel where possible, sequential where required)

**Execution Graph**:
```
Start
  ├─→ task_001 (flight_agent) ──┐
  │                              ├─→ task_002 (hotel_agent) ──┐
  └─→ task_003 (activity_agent) ─┘                            ├─→ task_004 (validation_agent) → End
                                                               ┘
```

**Timeline**:
```
t=0s:   Start execution
t=0s:   Dispatch task_001 (flight_agent) [PARALLEL]
t=0s:   Dispatch task_003 (activity_agent) [PARALLEL]
t=1.5s: task_001 completes ✓ (flight options found)
t=1.5s: Dispatch task_002 (hotel_agent) [SEQUENTIAL, depends on task_001]
t=2.0s: task_003 completes ✓ (5 activities recommended)
t=2.7s: task_002 completes ✓ (hotel options found)
t=2.7s: Dispatch task_004 (validation_agent) [SEQUENTIAL, depends on all]
t=3.0s: task_004 completes ✓ (budget validated, total: $1850)
t=3.0s: Execution complete ✓
```

**Execution Results**:
```json
{
  "execution_id": "exec_123",
  "plan_id": "plan_xyz789",
  "start_time": "2025-11-16T10:00:00Z",
  "end_time": "2025-11-16T10:00:03Z",
  "total_duration_seconds": 3.0,
  "status": "SUCCESS",
  "feedback": [
    {
      "task_id": "task_001",
      "feedback_type": "SUCCESS",
      "actual_outputs": {
        "flight_options": [
          {"airline": "Air France", "price": 650, "departure": "2025-05-01", "return": "2025-05-04"},
          {"airline": "United", "price": 720, "departure": "2025-05-01", "return": "2025-05-04"}
        ]
      },
      "errors": [],
      "duration_seconds": 1.5,
      "cost": 0.02
    },
    {
      "task_id": "task_002",
      "feedback_type": "SUCCESS",
      "actual_outputs": {
        "hotel_options": [
          {"name": "Hotel Le Marais", "price_per_night": 180, "location": "4th arrondissement", "total": 540},
          {"name": "Hotel Louvre", "price_per_night": 220, "location": "1st arrondissement", "total": 660}
        ]
      },
      "errors": [],
      "duration_seconds": 1.2,
      "cost": 0.015
    },
    {
      "task_id": "task_003",
      "feedback_type": "SUCCESS",
      "actual_outputs": {
        "activities": [
          {"name": "Eiffel Tower", "price": 25},
          {"name": "Louvre Museum", "price": 20},
          {"name": "Arc de Triomphe", "price": 13},
          {"name": "Seine River Cruise", "price": 15},
          {"name": "Montmartre Walking Tour", "price": 30},
          {"name": "Notre-Dame (exterior)", "price": 0}
        ]
      },
      "errors": [],
      "duration_seconds": 2.0,
      "cost": 0.01
    },
    {
      "task_id": "task_004",
      "feedback_type": "SUCCESS",
      "actual_outputs": {
        "budget_status": "WITHIN_BUDGET",
        "total_cost": 1850,
        "breakdown": {
          "flight": 650,
          "hotel": 540,
          "activities": 103,
          "buffer": 150
        }
      },
      "errors": [],
      "duration_seconds": 0.3,
      "cost": 0.005
    }
  ]
}
```

**Metrics**:
- Total execution time: 3.0s (estimated: 80s, but parallelization helped) ✓
- Total cost: $0.05 (execution) + $0.0064 (planning) = $0.0564 ✓
- Success rate: 4/4 tasks (100%) ✓
- All constraints met: Budget ($1850 < $2000), Duration (3 days), Activities (6 > 5) ✓

---

## Flujos Alternos

### FA-1: Task Failure → Re-planning (Retry with Different Agent)

**Trigger**: Task execution fails due to agent timeout/unavailability

**Escenario**: task_001 (flight_agent) times out después de 10s

**Proceso**:
```python
# Feedback indicates failure
feedback = ExecutionFeedback(
    task_id="task_001",
    feedback_type=FeedbackType.FAILURE,
    actual_outputs={},
    errors=["Agent timeout after 10s"],
    duration_seconds=10,
    cost=0.0,
    suggested_adjustments="Retry with different agent or increase timeout"
)

# Iterative Planner analyzes failure
planner = IterativePlanner()
revised_plan, revision = planner.replan(
    original_plan=plan,
    feedback=[feedback],
    goal=goal
)

# Revision strategy: Retry with backup agent
# Router finds next best agent for flight search
backup_agent = router.route_task(task_001, top_k=2)[1]  # ("backup_flight_agent", 0.78)

# Create revised subtask
revised_task_001 = SubTask(
    task_id="task_001_retry",
    description="Search for round-trip flights to Paris in May (retry)",
    agent_type="backup_flight_agent",
    dependencies=[],
    inputs=task_001.inputs,
    expected_outputs=task_001.expected_outputs,
    priority=task_001.priority,
    status=TaskStatus.PENDING,
    retry_policy={"max_retries": 1, "backoff_seconds": 5}
)

# Update plan
revised_plan.subtasks[0] = revised_task_001
revised_plan.confidence_score -= 0.1  # Penalize for failure
revised_plan.updated_at = datetime.now()

# Re-execute
revised_feedback = execute_plan(revised_plan)

# Result: backup_flight_agent succeeds in 2.5s
```

**Metrics**:
- Re-planning time: 1.8s (target: < 2s) ✓
- Retry success: True ✓
- Confidence delta: -0.1 (from 0.83 to 0.73)

---

### FA-2: Constraint Violation → Re-planning (Adjust Parameters)

**Trigger**: task_004 (validation) fails because total cost ($2150) > budget ($2000)

**Escenario**: Selected options exceed budget

**Proceso**:
```python
# Validation feedback
feedback = ExecutionFeedback(
    task_id="task_004",
    feedback_type=FeedbackType.CONSTRAINT_VIOLATION,
    actual_outputs={
        "budget_status": "EXCEEDED",
        "total_cost": 2150,
        "overage": 150
    },
    errors=["Total cost $2150 exceeds budget $2000"],
    duration_seconds=0.3,
    cost=0.005,
    suggested_adjustments="Select cheaper flight or hotel options"
)

# Re-planning strategy: Adjust task parameters to find cheaper options
revised_plan, revision = planner.replan(
    original_plan=plan,
    feedback=[feedback],
    goal=goal
)

# Revision changes:
# 1. Add constraint to task_001: max_price = 600
# 2. Add constraint to task_002: max_price_per_night = 150

revised_task_001 = task_001.copy()
revised_task_001.inputs["max_price"] = 600

revised_task_002 = task_002.copy()
revised_task_002.inputs["max_price_per_night"] = 150

# Update plan
revised_plan.subtasks[0] = revised_task_001
revised_plan.subtasks[1] = revised_task_002
revised_plan.confidence_score -= 0.08  # Small penalty for constraint violation

# Re-execute tasks 001, 002, 004
# Result: Flight $580, Hotel $450, Activities $103, Total $1133 ✓
```

**Metrics**:
- Re-planning time: 1.5s ✓
- New total cost: $1133 (within budget) ✓
- Confidence delta: -0.08

---

### FA-3: Missing Task Detected → Add Subtask

**Trigger**: Completeness validator detects missing "transportation_booking" category

**Escenario**: Travel plan needs local transportation (Paris Metro pass)

**Proceso**:
```python
# Completeness validation finds missing category
completeness_result = completeness_validator.validate_completeness(plan, goal)
# Missing: ["transportation_booking"]
# Completeness score: 0.80 (below 0.95 threshold)

if not completeness_result.is_complete:
    # Add missing subtask
    new_task = SubTask(
        task_id="task_005",
        description="Book Paris Metro 3-day pass",
        agent_type="TBD",  # Will be routed
        dependencies=["task_001"],  # Needs arrival dates
        inputs={"duration": "3 days"},
        expected_outputs=["metro_pass"],
        priority=6,
        estimated_duration_seconds=15,
        status=TaskStatus.PENDING
    )

    # Route new task
    new_task.agent_type = router.route_task(new_task, top_k=1)[0][0]
    # Result: "transportation_agent"

    # Insert into plan (before validation task)
    plan.subtasks.insert(-1, new_task)

    # Update validation task dependencies
    plan.subtasks[-1].dependencies.append("task_005")

    # Re-validate
    new_completeness = completeness_validator.validate_completeness(plan, goal)
    # Completeness: 1.0 ✓
```

**Metrics**:
- New task added: task_005
- Completeness improved: 0.80 → 1.0
- Estimated duration increased: 80s → 95s

---

### FA-4: Circular Dependency Detected → Remove Dependency

**Trigger**: Dependency validator detects cycle during validation

**Escenario**: Accidental cycle introduced: task_002 → task_004 → task_002

**Proceso**:
```python
# Dependency validation finds cycle
dependency_result = dependency_validator.validate_dependencies(plan)
# Errors: ["Circular dependencies detected: ['task_002', 'task_004', 'task_002']"]

if not dependency_result.is_valid:
    # Analyze cycle
    cycles = dependency_result.cycles
    # [['task_002', 'task_004', 'task_002']]

    # Strategy: Remove unnecessary dependency
    # task_004 (validation) should NOT depend on task_002 (hotel)
    # It should depend on all pricing tasks being complete

    # Find unnecessary deps
    unnecessary = dependency_validator._find_unnecessary_dependencies(graph)
    # [("task_004", "task_002")]  # Transitive via task_001

    # Remove unnecessary dependency
    plan.subtasks[3].dependencies.remove("task_002")

    # Re-validate
    new_dependency_result = dependency_validator.validate_dependencies(plan)
    # is_valid: True ✓
```

**Metrics**:
- Cycle detection time: 50ms ✓
- Fix applied: Removed 1 dependency
- Validation success: True ✓

---

### FA-5: Max Revisions Reached → Abort Planning

**Trigger**: Plan revised 3 times without success

**Escenario**: Persistent failures (e.g., no flights available in May)

**Proceso**:
```python
# After 3rd revision attempt
revision_count = len(plan_revisions)  # 3

if revision_count >= IterativePlanner.MAX_REVISIONS:
    # Confidence has dropped significantly
    # Original: 0.85, After rev1: 0.75, After rev2: 0.65, After rev3: 0.55

    if plan.confidence_score < 0.3:
        raise LowConfidenceError(
            f"Plan {plan.plan_id} confidence {plan.confidence_score:.2f} too low after {revision_count} revisions. "
            f"Aborting planning. Suggest relaxing constraints or changing goal."
        )

    raise MaxRevisionsExceeded(
        f"Plan {plan.plan_id} exceeded {IterativePlanner.MAX_REVISIONS} revisions. "
        f"Latest errors: {latest_feedback.errors}"
    )

# User receives error and suggestion
# "Unable to complete plan. Suggestion: Consider alternative dates (June instead of May) or increase budget."
```

**Metrics**:
- Revisions attempted: 3
- Final confidence: 0.55
- Planning aborted: True
- User notified: True ✓

---

### FA-6: Low Confidence Plan → Request Human Approval

**Trigger**: Plan generated with confidence_score < 0.5

**Escenario**: Planner uncertain about decomposition or routing

**Proceso**:
```python
# Plan generated with low confidence
plan.confidence_score = 0.45  # Below 0.5 threshold

if plan.confidence_score < 0.5:
    # Flag for human review
    plan.metadata["requires_approval"] = True
    plan.metadata["low_confidence_reasons"] = [
        "Unusual goal type (not in training data)",
        "Ambiguous constraints (no specific dates)",
        "Low agent assignment confidence (avg 0.6)"
    ]

    # Request human approval
    approval_request = HumanApprovalRequest(
        plan_id=plan.plan_id,
        confidence_score=plan.confidence_score,
        reasons=plan.metadata["low_confidence_reasons"],
        plan_summary=_summarize_plan(plan),
        recommended_action="REVIEW_AND_ADJUST"
    )

    # Human reviews and either:
    # 1. Approves plan as-is → Execute
    # 2. Adjusts constraints/tasks → Re-plan
    # 3. Rejects plan → Abort

    human_decision = request_human_approval(approval_request)

    if human_decision.action == "APPROVE":
        # Proceed with execution despite low confidence
        execute_plan(plan)
    elif human_decision.action == "ADJUST":
        # Apply human adjustments
        adjusted_plan = apply_adjustments(plan, human_decision.adjustments)
        execute_plan(adjusted_plan)
    else:
        # Abort
        raise PlanRejectedError("Plan rejected by human reviewer")
```

**Metrics**:
- Human approval requested: True
- Approval time: 30s (human review)
- Final action: Approved with adjustments

---

### FA-7: Budget Exceeded During Planning → Abort Early

**Trigger**: Cumulative planning cost > $0.01 before completion

**Escenario**: Multiple LLM calls for complex decomposition

**Proceso**:
```python
# During planning
cost_tracker.start_planning_cycle()

# Goal parsing: $0.002
cost_tracker.track_llm_call("parse_goal", 200, 100)  # $0.002

# Task decomposition attempt 1: $0.005
cost_tracker.track_llm_call("decompose_task", 400, 300)  # $0.005

# Task decomposition attempt 2 (re-try): $0.005
cost_tracker.track_llm_call("decompose_task", 450, 320)  # $0.0055

# Current total: $0.0125 > $0.01 budget

try:
    cost_tracker.end_planning_cycle()
except BudgetExceededError as e:
    # Abort planning
    logger.error(f"Planning budget exceeded: {e}")

    # Return partial plan or error
    raise PlanningBudgetExceeded(
        f"Planning cost ${cost_tracker.current_cycle_cost:.4f} exceeds budget $0.01. "
        f"Consider simplifying goal or increasing budget."
    )
```

**Metrics**:
- Planning cost: $0.0125 (exceeds $0.01) ✗
- Planning aborted: True
- User notified: True ✓

---

## Métricas de Éxito

### Planning Performance
| Métrica | Objetivo | Resultado Ejemplo | Estado |
|---------|----------|-------------------|--------|
| Goal Parsing Time | < 1s (p95) | 850ms | ✓ |
| Task Decomposition Time | < 2s (p95) | 1.75s | ✓ |
| Agent Routing Time | < 500ms per task | 420ms avg | ✓ |
| Full Planning Cycle | < 3s (p95) | 2.6s | ✓ |
| Re-planning Time | < 2s (p95) | 1.8s | ✓ |

### Planning Quality
| Métrica | Objetivo | Resultado Ejemplo | Estado |
|---------|----------|-------------------|--------|
| Task Completeness | > 95% | 100% | ✓ |
| Dependency Accuracy | > 90% | 100% | ✓ |
| Agent Assignment Accuracy | > 85% | 100% | ✓ |
| Confidence Calibration | r > 0.7 | r = 0.82 | ✓ |

### Adaptability
| Métrica | Objetivo | Resultado Ejemplo | Estado |
|---------|----------|-------------------|--------|
| Revision Success Rate | > 70% | 85% | ✓ |
| Revisions per Plan | < 20% | 15% | ✓ |
| Max Revisions Hit Rate | < 5% | 2% | ✓ |

### Cost Efficiency
| Métrica | Objetivo | Resultado Ejemplo | Estado |
|---------|----------|-------------------|--------|
| Planning Cost | < $0.01 per plan | $0.0064 | ✓ |
| Routing Cost | < $0.001 per task | $0.0004 | ✓ |
| Total Cost (Planning + Execution) | Variable | $0.0564 | ✓ |

---

## Notas de Implementación

### 1. Pydantic Validation Benefits

**Type Safety**:
```python
# Invalid subtask (missing required field) caught immediately
try:
    invalid_task = SubTask(
        task_id="task_001",
        description="Search flights",
        agent_type="flight_agent"
        # Missing: expected_outputs
    )
except ValidationError as e:
    # ValidationError: 1 validation error for SubTask
    #   expected_outputs
    #     field required (type=value_error.missing)
    print(f"Validation error: {e}")
```

### 2. Semantic Router Caching

**Performance Optimization**:
```python
# Pre-compute agent embeddings at startup (one-time cost)
router = SemanticRouter(agents=agents, embedding_fn=embed_fn)
# Agent embeddings computed once: 4 agents × $0.0001 = $0.0004

# Cache task embeddings for similar requests
task_embedding_cache = EmbeddingCache(max_size_mb=50, ttl_seconds=3600)

# On routing
cache_key = hash(task.description)
embedding = task_embedding_cache.get(cache_key)
if embedding is None:
    embedding = embed_fn(task.description)  # $0.0001
    task_embedding_cache.put(cache_key, embedding)
else:
    # Cache hit, $0 cost
    pass
```

**Savings**: 80% cache hit rate → $0.0001 → $0.00002 avg cost per routing

### 3. Iterative Planning Strategies

**Strategy Selection**:
```python
class IterativePlanner:
    def _select_strategy(self, feedback: ExecutionFeedback) -> str:
        """Select re-planning strategy based on failure type."""

        if feedback.feedback_type == FeedbackType.FAILURE:
            # Check if timeout/unavailability → Retry different agent
            if any(err in ["timeout", "unavailable"] for err in feedback.errors):
                return "RETRY_DIFFERENT_AGENT"

            # Check if too complex → Decompose further
            if "too complex" in feedback.suggested_adjustments.lower():
                return "DECOMPOSE_FURTHER"

            # Default → Find workaround
            return "FIND_WORKAROUND"

        elif feedback.feedback_type == FeedbackType.CONSTRAINT_VIOLATION:
            # Adjust parameters to meet constraints
            return "ADJUST_PARAMETERS"

        elif feedback.feedback_type == FeedbackType.DEPENDENCY_FAILURE:
            # Re-sequence tasks or remove blocking dependency
            return "FIX_DEPENDENCIES"

        else:
            return "UNKNOWN"
```

### 4. Confidence Calibration

**Continuous Improvement**:
```python
# After each plan execution
outcome = PlanOutcome(
    plan_id=plan.plan_id,
    confidence_score=plan.confidence_score,
    success=execution_successful,
    execution_time=execution_duration,
    cost=execution_cost
)
calibrator.record_outcome(outcome)

# Periodically check calibration (every 100 plans)
if calibrator.outcomes_count % 100 == 0:
    metrics = calibrator.calculate_calibration()

    if metrics.correlation < 0.7:
        logger.warning(
            f"Confidence calibration degraded: r={metrics.correlation:.2f}. "
            f"Retraining confidence model recommended."
        )

        # Optionally: Retrain confidence prediction model
        retrain_confidence_model(calibrator.outcomes)
```

---

## Referencias

1. [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
2. [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
3. [UC-SYS-005: Multi-Agent Orchestration](./UC-SYS-005_multi_agent_orchestration.md)
4. [ADR-052: Metacognition Architecture](../../../gobernanza/adr/ADR-052-metacognition-architecture.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
