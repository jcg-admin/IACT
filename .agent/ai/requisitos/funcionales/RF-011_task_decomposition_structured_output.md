# RF-011: Task Decomposition and Structured Output

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Planning Design
**Relación**:
- Implementa [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
- Sigue [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
- Relacionado con [UC-SYS-006: Planning and Replanning Workflow](../casos_uso/UC-SYS-006_planning_replanning_workflow.md)

---

## Descripción

El sistema debe convertir user requests en natural language en structured plans con typed objects (Pydantic), desglosar objectives complejos en subtasks ejecutables, identificar dependencies automáticamente, y validar completeness antes de execution.

**Capacidades principales**:
1. **Goal Parsing**: Natural language → structured Goal object con constraints y success criteria
2. **Task Decomposition**: Goal → ordered SubTask list con dependencies
3. **Pydantic Validation**: Type-safe objects con automatic validation
4. **Dependency Analysis**: Automatic dependency detection y cycle prevention
5. **Completeness Validation**: Ensure all required task categories present

---

## Escenarios de Aceptación (Gherkin)

### Categoría: Goal Parsing

#### Escenario 1: Parse Simple Travel Goal
```gherkin
Given el usuario envía la solicitud "Plan a 3-day trip to Paris in May"
When el Goal Parser procesa la solicitud
Then debe crear un Goal object con:
  | Campo | Valor |
  | goal_type | TRAVEL_PLANNING |
  | description | "Plan a 3-day trip to Paris in May" |
  | constraints | [{"type": "duration", "value": "3 days"}, {"type": "time", "value": "May"}] |
And debe extraer destination = "Paris"
And debe extraer duration_days = 3
And debe completar en < 1s
And debe costar < $0.002
```

**Test Template**:
```python
def test_parse_simple_travel_goal():
    """RF-011: Escenario 1 - Parse Simple Travel Goal"""
    parser = GoalParser(openai_client=client)

    # Given
    user_request = "Plan a 3-day trip to Paris in May"

    # When
    start_time = time.time()
    goal = parser.parse(user_request)
    duration = time.time() - start_time

    # Then
    assert goal.goal_type == GoalType.TRAVEL_PLANNING
    assert goal.description == user_request
    assert any(c.type == "duration" and c.value == "3 days" for c in goal.constraints)
    assert any(c.type == "time" and "May" in c.value for c in goal.constraints)

    # Extracted fields
    assert "Paris" in goal.description
    extracted = goal.metadata.get("extracted", {})
    assert extracted.get("duration_days") == 3

    # Performance
    assert duration < 1.0, f"Parsing took {duration:.2f}s (limit: 1s)"

    # Cost (tracked separately via CostTracker)
    assert parser.last_call_cost < 0.002
```

---

#### Escenario 2: Parse Goal with Budget Constraint
```gherkin
Given el usuario envía "Plan a trip to Tokyo with a $3000 budget"
When el Goal Parser procesa la solicitud
Then debe crear un Goal con constraint:
  | type | value | priority |
  | budget | 3000 USD | 10 |
And debe incluir success_criteria "Total cost <= $3000"
And debe asignar prioridad más alta al constraint de budget (priority=10)
```

**Test Template**:
```python
def test_parse_goal_with_budget_constraint():
    """RF-011: Escenario 2 - Parse Goal with Budget Constraint"""
    parser = GoalParser(openai_client=client)

    # Given
    user_request = "Plan a trip to Tokyo with a $3000 budget"

    # When
    goal = parser.parse(user_request)

    # Then
    budget_constraint = next((c for c in goal.constraints if c.type == "budget"), None)
    assert budget_constraint is not None
    assert "3000" in budget_constraint.value
    assert budget_constraint.priority == 10  # Highest priority

    # Success criteria should include budget check
    assert any("cost" in sc.lower() and "3000" in sc for sc in goal.success_criteria)
```

---

#### Escenario 3: Parse Goal with Multiple Constraints
```gherkin
Given el usuario envía "Plan a 5-day trip to Barcelona in June, budget $2500, prefer boutique hotels"
When el Goal Parser procesa la solicitud
Then debe crear constraints para:
  | type | value | priority |
  | duration | 5 days | 9 |
  | time | June | 8 |
  | budget | 2500 USD | 10 |
And debe registrar preference "boutique hotels" en metadata
And debe generar success_criteria para cada constraint
```

**Test Template**:
```python
def test_parse_goal_with_multiple_constraints():
    """RF-011: Escenario 3 - Parse Goal with Multiple Constraints"""
    parser = GoalParser(openai_client=client)

    # Given
    user_request = "Plan a 5-day trip to Barcelona in June, budget $2500, prefer boutique hotels"

    # When
    goal = parser.parse(user_request)

    # Then - all constraints present
    constraint_types = {c.type for c in goal.constraints}
    assert "duration" in constraint_types
    assert "time" in constraint_types
    assert "budget" in constraint_types

    # Duration constraint
    duration_c = next(c for c in goal.constraints if c.type == "duration")
    assert "5" in duration_c.value

    # Preferences in metadata
    assert "boutique" in str(goal.metadata.get("preferences", [])).lower()

    # Success criteria generated
    assert len(goal.success_criteria) >= 3
```

---

#### Escenario 4: Handle Ambiguous Goal (Missing Information)
```gherkin
Given el usuario envía "Plan a trip to Paris"
When el Goal Parser procesa la solicitud
Then debe crear un Goal válido con:
  | Campo | Comportamiento |
  | constraints | Lista vacía o solo destination |
  | success_criteria | Criterios genéricos |
  | metadata.ambiguities | ["duration not specified", "budget not specified"] |
And debe marcar metadata.requires_clarification = True
And debe sugerir preguntas de clarification
```

**Test Template**:
```python
def test_handle_ambiguous_goal():
    """RF-011: Escenario 4 - Handle Ambiguous Goal"""
    parser = GoalParser(openai_client=client)

    # Given
    user_request = "Plan a trip to Paris"

    # When
    goal = parser.parse(user_request)

    # Then - valid but marked as ambiguous
    assert goal.goal_type == GoalType.TRAVEL_PLANNING

    # Ambiguities tracked
    assert goal.metadata.get("requires_clarification") == True
    ambiguities = goal.metadata.get("ambiguities", [])
    assert any("duration" in a.lower() for a in ambiguities)
    assert any("budget" in a.lower() for a in ambiguities)

    # Clarification questions suggested
    clarifications = goal.metadata.get("clarification_questions", [])
    assert len(clarifications) > 0
```

---

#### Escenario 5: Validate Pydantic Goal Object
```gherkin
Given se intenta crear un Goal sin campo requerido
When se instancia Goal(goal_id="test", description="Test")
Then debe lanzar ValidationError
And debe indicar campo faltante "goal_type"
And debe indicar campo faltante "success_criteria"
```

**Test Template**:
```python
def test_validate_pydantic_goal_object():
    """RF-011: Escenario 5 - Validate Pydantic Goal Object"""
    from pydantic import ValidationError

    # Given - missing required fields
    # When/Then - should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        invalid_goal = Goal(
            goal_id="test_goal",
            description="Test description"
            # Missing: goal_type, success_criteria
        )

    # Verify error details
    errors = exc_info.value.errors()
    error_fields = {e["loc"][0] for e in errors}

    assert "goal_type" in error_fields
    assert "success_criteria" in error_fields
```

---

### Categoría: Task Decomposition

#### Escenario 6: Decompose Simple Travel Goal
```gherkin
Given un Goal de tipo TRAVEL_PLANNING con destination="Paris", duration=3
When el Task Decomposer genera subtasks
Then debe crear al menos 4 subtasks:
  | Description Contains | Category |
  | flight | flight_booking |
  | hotel | hotel_booking |
  | activit | activity_planning |
  | budget | budget_validation |
And todas las subtasks deben tener task_id único
And debe completar en < 2s
```

**Test Template**:
```python
def test_decompose_simple_travel_goal():
    """RF-011: Escenario 6 - Decompose Simple Travel Goal"""
    decomposer = TaskDecomposer(openai_client=client)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Plan a 3-day trip to Paris",
        constraints=[],
        success_criteria=["Complete plan"]
    )

    # When
    start_time = time.time()
    plan = decomposer.decompose(goal)
    duration = time.time() - start_time

    # Then - at least 4 subtasks
    assert len(plan.subtasks) >= 4

    # Required categories
    descriptions = [t.description.lower() for t in plan.subtasks]
    assert any("flight" in d for d in descriptions)
    assert any("hotel" in d for d in descriptions)
    assert any("activ" in d for d in descriptions)
    assert any("budget" in d or "validat" in d for d in descriptions)

    # Unique IDs
    task_ids = [t.task_id for t in plan.subtasks]
    assert len(task_ids) == len(set(task_ids))

    # Performance
    assert duration < 2.0, f"Decomposition took {duration:.2f}s (limit: 2s)"
```

---

#### Escenario 7: Identify Task Dependencies Automatically
```gherkin
Given un Plan con subtasks: [search_flights, book_hotel, validate_budget]
When el sistema analiza dependencies
Then "book_hotel" debe depender de "search_flights" (necesita fechas)
And "validate_budget" debe depender de ambos "search_flights" y "book_hotel"
And "search_flights" no debe tener dependencies (puede ejecutarse inmediatamente)
```

**Test Template**:
```python
def test_identify_task_dependencies():
    """RF-011: Escenario 7 - Identify Task Dependencies Automatically"""
    decomposer = TaskDecomposer(openai_client=client)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Plan trip",
        constraints=[],
        success_criteria=[]
    )

    # When
    plan = decomposer.decompose(goal)

    # Then - find specific tasks
    flight_task = next((t for t in plan.subtasks if "flight" in t.description.lower()), None)
    hotel_task = next((t for t in plan.subtasks if "hotel" in t.description.lower()), None)
    budget_task = next((t for t in plan.subtasks if "budget" in t.description.lower() or "validat" in t.description.lower()), None)

    assert flight_task is not None
    assert hotel_task is not None
    assert budget_task is not None

    # Dependencies
    assert len(flight_task.dependencies) == 0, "Flight search should have no deps"
    assert flight_task.task_id in hotel_task.dependencies, "Hotel should depend on flight"
    assert flight_task.task_id in budget_task.dependencies, "Budget should depend on flight"
    assert hotel_task.task_id in budget_task.dependencies, "Budget should depend on hotel"
```

---

#### Escenario 8: Create Pydantic SubTask Objects
```gherkin
Given task data: {description: "Search flights", agent_type: "flight_agent"}
When se crea SubTask con Pydantic
Then debe validar campos requeridos
And debe generar task_id automático si no se provee
And debe inicializar status = PENDING
And debe validar que priority esté en rango 1-10
```

**Test Template**:
```python
def test_create_pydantic_subtask_objects():
    """RF-011: Escenario 8 - Create Pydantic SubTask Objects"""
    # Given - valid data
    task_data = {
        "task_id": "task_001",
        "description": "Search flights",
        "agent_type": "flight_agent",
        "dependencies": [],
        "expected_outputs": ["flight_options"]
    }

    # When
    task = SubTask(**task_data)

    # Then - defaults applied
    assert task.status == TaskStatus.PENDING
    assert 1 <= task.priority <= 10
    assert isinstance(task.inputs, dict)

    # Test validation - invalid priority
    with pytest.raises(ValidationError):
        invalid_task = SubTask(
            task_id="task_002",
            description="Test",
            agent_type="test",
            dependencies=[],
            expected_outputs=["out"],
            priority=15  # Invalid: > 10
        )
```

---

#### Escenario 9: Estimate Task Durations
```gherkin
Given subtasks para travel planning
When el decomposer estima durations
Then "search_flights" debe tener estimated_duration_seconds ~ 30
And "book_hotel" debe tener estimated_duration_seconds ~ 25
And "search_activities" debe tener estimated_duration_seconds ~ 20
And plan.estimated_total_duration debe ser suma de subtasks parallelizables
```

**Test Template**:
```python
def test_estimate_task_durations():
    """RF-011: Escenario 9 - Estimate Task Durations"""
    decomposer = TaskDecomposer(openai_client=client)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Plan trip",
        constraints=[],
        success_criteria=[]
    )

    # When
    plan = decomposer.decompose(goal)

    # Then - all tasks have duration estimates
    for task in plan.subtasks:
        assert task.estimated_duration_seconds is not None
        assert task.estimated_duration_seconds > 0

    # Specific estimates (within reasonable range)
    flight_task = next((t for t in plan.subtasks if "flight" in t.description.lower()), None)
    if flight_task:
        assert 20 <= flight_task.estimated_duration_seconds <= 60

    # Total duration reasonable
    assert plan.estimated_total_duration > 0
    assert plan.estimated_total_duration <= sum(t.estimated_duration_seconds for t in plan.subtasks)
```

---

#### Escenario 10: Handle Complex Multi-Step Goals
```gherkin
Given un Goal complejo: "Analyze sales data from Q3, identify trends, create visualizations, and generate executive report"
When el decomposer genera subtasks
Then debe crear subtasks para cada step:
  | Step | Category |
  | Load data | data_loading |
  | Clean data | data_cleaning |
  | Analyze trends | analysis |
  | Create visualizations | visualization |
  | Generate report | reporting |
And debe establecer dependencies secuenciales
And debe asignar priorities basadas en order
```

**Test Template**:
```python
def test_handle_complex_multistep_goals():
    """RF-011: Escenario 10 - Handle Complex Multi-Step Goals"""
    decomposer = TaskDecomposer(openai_client=client)

    # Given
    goal = Goal(
        goal_id="goal_456",
        goal_type=GoalType.DATA_ANALYSIS,
        description="Analyze sales data from Q3, identify trends, create visualizations, and generate executive report",
        constraints=[],
        success_criteria=["Complete analysis with visualizations and report"]
    )

    # When
    plan = decomposer.decompose(goal)

    # Then - multiple subtasks created
    assert len(plan.subtasks) >= 5

    # Check categories present
    descriptions_lower = [t.description.lower() for t in plan.subtasks]
    assert any("load" in d or "data" in d for d in descriptions_lower)
    assert any("clean" in d for d in descriptions_lower)
    assert any("analyz" in d or "trend" in d for d in descriptions_lower)
    assert any("visual" in d for d in descriptions_lower)
    assert any("report" in d for d in descriptions_lower)

    # Sequential dependencies
    # Later tasks should depend on earlier ones
    last_task = plan.subtasks[-1]
    assert len(last_task.dependencies) > 0, "Final task should have dependencies"
```

---

### Categoría: Dependency Validation

#### Escenario 11: Detect Circular Dependencies
```gherkin
Given un Plan con circular dependency: task_A → task_B → task_C → task_A
When el DependencyValidator valida dependencies
Then debe detectar el ciclo
And debe retornar is_valid = False
And debe incluir en errors: "Circular dependencies detected: ['task_A', 'task_B', 'task_C', 'task_A']"
```

**Test Template**:
```python
def test_detect_circular_dependencies():
    """RF-011: Escenario 11 - Detect Circular Dependencies"""
    validator = DependencyValidator()

    # Given - plan with circular dependency
    plan = Plan(
        plan_id="plan_cycle",
        goal_id="goal_123",
        subtasks=[
            SubTask(task_id="task_A", description="A", agent_type="test", dependencies=["task_C"], expected_outputs=["a"]),
            SubTask(task_id="task_B", description="B", agent_type="test", dependencies=["task_A"], expected_outputs=["b"]),
            SubTask(task_id="task_C", description="C", agent_type="test", dependencies=["task_B"], expected_outputs=["c"])
        ],
        execution_strategy="sequential",
        estimated_total_duration=100,
        confidence_score=0.8
    )

    # When
    result = validator.validate_dependencies(plan)

    # Then
    assert result.is_valid == False
    assert any("circular" in str(e).lower() for e in result.errors)

    # Cycle details
    assert "task_A" in str(result.errors)
    assert "task_B" in str(result.errors)
    assert "task_C" in str(result.errors)
```

---

#### Escenario 12: Detect Dangling Dependencies
```gherkin
Given un Plan con task_A que depende de "task_XYZ" (que no existe)
When el DependencyValidator valida
Then debe retornar is_valid = False
And debe incluir en errors: "Dependencies reference non-existent tasks: [('task_A', 'task_XYZ')]"
```

**Test Template**:
```python
def test_detect_dangling_dependencies():
    """RF-011: Escenario 12 - Detect Dangling Dependencies"""
    validator = DependencyValidator()

    # Given - plan with dangling dependency
    plan = Plan(
        plan_id="plan_dangling",
        goal_id="goal_123",
        subtasks=[
            SubTask(task_id="task_A", description="A", agent_type="test", dependencies=["task_XYZ"], expected_outputs=["a"]),
            SubTask(task_id="task_B", description="B", agent_type="test", dependencies=[], expected_outputs=["b"])
        ],
        execution_strategy="sequential",
        estimated_total_duration=100,
        confidence_score=0.8
    )

    # When
    result = validator.validate_dependencies(plan)

    # Then
    assert result.is_valid == False
    assert any("non-existent" in str(e).lower() for e in result.errors)
    assert "task_XYZ" in str(result.errors)
```

---

#### Escenario 13: Identify Unnecessary Dependencies (Transitive)
```gherkin
Given un Plan donde task_C depende de [task_A, task_B] y task_B ya depende de task_A
When el DependencyValidator identifica redundancias
Then debe sugerir en warnings: "Potentially unnecessary dependencies: [('task_C', 'task_A')]"
And la dependency task_C → task_A es transitiva via task_B
```

**Test Template**:
```python
def test_identify_unnecessary_dependencies():
    """RF-011: Escenario 13 - Identify Unnecessary Dependencies"""
    validator = DependencyValidator()

    # Given - plan with transitive dependency
    plan = Plan(
        plan_id="plan_transitive",
        goal_id="goal_123",
        subtasks=[
            SubTask(task_id="task_A", description="A", agent_type="test", dependencies=[], expected_outputs=["a"]),
            SubTask(task_id="task_B", description="B", agent_type="test", dependencies=["task_A"], expected_outputs=["b"]),
            SubTask(task_id="task_C", description="C", agent_type="test", dependencies=["task_A", "task_B"], expected_outputs=["c"])
        ],
        execution_strategy="sequential",
        estimated_total_duration=100,
        confidence_score=0.8
    )

    # When
    result = validator.validate_dependencies(plan)

    # Then - should warn about transitive dependency
    assert result.is_valid == True  # Not invalid, just suboptimal
    assert len(result.warnings) > 0
    assert any("unnecessary" in w.lower() for w in result.warnings)
    assert any("task_A" in w for w in result.warnings)
```

---

#### Escenario 14: Validate Dependency Completeness
```gherkin
Given un Plan con task_hotel que usa output de task_flight
When el validator analiza data flow
Then debe detectar missing dependency si task_hotel no lista task_flight en dependencies
And debe sugerir en warnings: "Potentially missing dependencies: [('task_hotel', 'task_flight')]"
```

**Test Template**:
```python
def test_validate_dependency_completeness():
    """RF-011: Escenario 14 - Validate Dependency Completeness"""
    validator = DependencyValidator()

    # Given - hotel task uses flight output but doesn't declare dependency
    plan = Plan(
        plan_id="plan_missing_dep",
        goal_id="goal_123",
        subtasks=[
            SubTask(
                task_id="task_flight",
                description="Search flights",
                agent_type="flight",
                dependencies=[],
                expected_outputs=["flight_dates", "flight_price"]
            ),
            SubTask(
                task_id="task_hotel",
                description="Book hotel",
                agent_type="hotel",
                dependencies=[],  # Missing: should depend on task_flight
                inputs={"dates": "from flight_dates"},  # Uses flight output!
                expected_outputs=["hotel_booking"]
            )
        ],
        execution_strategy="sequential",
        estimated_total_duration=100,
        confidence_score=0.8
    )

    # When
    result = validator.validate_dependencies(plan)

    # Then - should detect missing dependency
    assert len(result.warnings) > 0
    assert any("missing" in w.lower() for w in result.warnings)
    assert any("task_hotel" in w and "task_flight" in w for w in result.warnings)
```

---

### Categoría: Completeness Validation

#### Escenario 15: Validate Travel Plan Completeness
```gherkin
Given un Goal de TRAVEL_PLANNING
And required categories: [flight_booking, hotel_booking, activity_planning, budget_validation]
When el Plan solo incluye [flight_booking, hotel_booking]
Then CompletenessValidator debe retornar is_complete = False
And completeness_score debe ser 0.5 (2/4)
And missing_categories debe ser [activity_planning, budget_validation]
```

**Test Template**:
```python
def test_validate_travel_plan_completeness():
    """RF-011: Escenario 15 - Validate Travel Plan Completeness"""
    validator = CompletenessValidator(goal_templates=GOAL_TEMPLATES)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Plan trip",
        constraints=[],
        success_criteria=[]
    )

    incomplete_plan = Plan(
        plan_id="plan_incomplete",
        goal_id=goal.goal_id,
        subtasks=[
            SubTask(task_id="1", description="Search flights", agent_type="flight", dependencies=[], expected_outputs=["flights"]),
            SubTask(task_id="2", description="Book hotel", agent_type="hotel", dependencies=[], expected_outputs=["hotel"])
        ],
        execution_strategy="sequential",
        estimated_total_duration=50,
        confidence_score=0.7
    )

    # When
    result = validator.validate_completeness(incomplete_plan, goal)

    # Then
    assert result.is_complete == False
    assert result.completeness_score == 0.5  # 2 out of 4 categories

    # Missing categories
    missing = set(result.missing_categories)
    assert "activity_planning" in missing
    assert "budget_validation" in missing
```

---

#### Escenario 16: Complete Plan Passes Validation
```gherkin
Given un Plan con todas las categorías requeridas
When el CompletenessValidator valida
Then debe retornar is_complete = True
And completeness_score debe ser >= 0.95
And missing_categories debe ser []
```

**Test Template**:
```python
def test_complete_plan_passes_validation():
    """RF-011: Escenario 16 - Complete Plan Passes Validation"""
    validator = CompletenessValidator(goal_templates=GOAL_TEMPLATES)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Plan trip",
        constraints=[],
        success_criteria=[]
    )

    complete_plan = Plan(
        plan_id="plan_complete",
        goal_id=goal.goal_id,
        subtasks=[
            SubTask(task_id="1", description="Search flights", agent_type="flight", dependencies=[], expected_outputs=["f"]),
            SubTask(task_id="2", description="Book hotel", agent_type="hotel", dependencies=[], expected_outputs=["h"]),
            SubTask(task_id="3", description="Plan activities", agent_type="activity", dependencies=[], expected_outputs=["a"]),
            SubTask(task_id="4", description="Validate budget", agent_type="validator", dependencies=[], expected_outputs=["v"])
        ],
        execution_strategy="sequential",
        estimated_total_duration=100,
        confidence_score=0.9
    )

    # When
    result = validator.validate_completeness(complete_plan, goal)

    # Then
    assert result.is_complete == True
    assert result.completeness_score >= 0.95
    assert len(result.missing_categories) == 0
```

---

### Categoría: Performance and Cost

#### Escenario 17: Enforce Goal Parsing Latency
```gherkin
Given el Goal Parser con timeout=1s
When procesa una solicitud compleja
And la operación tarda 1.2s
Then debe lanzar PlanningTimeoutError
And debe incluir mensaje "parse_goal took 1.20s (limit: 1.0s)"
```

**Test Template**:
```python
def test_enforce_goal_parsing_latency():
    """RF-011: Escenario 17 - Enforce Goal Parsing Latency"""
    from unittest.mock import patch
    import time

    # Mock slow LLM call
    def slow_llm_call(*args, **kwargs):
        time.sleep(1.2)  # Exceeds 1s timeout
        return MockLLMResponse(content='{"destination": "Paris"}')

    parser = GoalParser(openai_client=client)

    # When - parsing with timeout enforcement
    with patch.object(parser.client.chat.completions, 'create', side_effect=slow_llm_call):
        with pytest.raises(PlanningTimeoutError) as exc_info:
            goal = parser.parse("Plan a complex multi-destination trip")

    # Then
    assert "parse_goal" in str(exc_info.value)
    assert "1.2" in str(exc_info.value) or "1s" in str(exc_info.value)
```

---

#### Escenario 18: Enforce Task Decomposition Latency
```gherkin
Given el Task Decomposer con timeout=2s
When descompone un goal
And completa en 1.8s
Then debe procesar exitosamente
And debe registrar latency metric = 1.8s
And status debe ser "success"
```

**Test Template**:
```python
def test_enforce_task_decomposition_latency():
    """RF-011: Escenario 18 - Enforce Task Decomposition Latency"""
    decomposer = TaskDecomposer(openai_client=client)

    # Given
    goal = Goal(
        goal_id="goal_123",
        goal_type=GoalType.TRAVEL_PLANNING,
        description="Simple trip",
        constraints=[],
        success_criteria=[]
    )

    # When
    start_time = time.time()
    plan = decomposer.decompose(goal)
    duration = time.time() - start_time

    # Then - should complete within timeout
    assert duration < 2.0, f"Decomposition took {duration:.2f}s (limit: 2s)"

    # Metrics should be recorded (check via Prometheus or tracker)
    # assert PLANNING_LATENCY.labels(operation="decompose_task", status="success").observe was called
```

---

#### Escenario 19: Track Goal Parsing Cost
```gherkin
Given el CostTracker monitorea LLM calls
When se parsea un goal con 200 prompt tokens y 100 completion tokens
Then debe calcular cost = (200/1000 * $0.03) + (100/1000 * $0.06) = $0.012
And debe comparar con budget de $0.002
And debe lanzar BudgetExceededError si excede
```

**Test Template**:
```python
def test_track_goal_parsing_cost():
    """RF-011: Escenario 19 - Track Goal Parsing Cost"""
    tracker = PlanningCostTracker()

    # Given - LLM call with specific token counts
    prompt_tokens = 200
    completion_tokens = 100

    # When
    tracking = tracker.track_llm_call(
        operation="parse_goal",
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )

    # Then - cost calculated correctly
    expected_cost = (200/1000 * 0.03) + (100/1000 * 0.06)
    assert abs(tracking.cost_usd - expected_cost) < 0.0001

    # Budget check
    assert tracking.budget_usd == 0.002

    # Since cost exceeds budget, should raise error
    # (In this test, the tracker already raised it during track_llm_call)
```

---

#### Escenario 20: Validate Plan Size Limit
```gherkin
Given un Plan con 100 subtasks grandes (description = 10,000 chars cada uno)
When se valida el tamaño del plan
Then el Plan serializado debe exceder 1MB
And debe lanzar PlanSizeError
And debe incluir mensaje con plan_id y tamaño actual
```

**Test Template**:
```python
def test_validate_plan_size_limit():
    """RF-011: Escenario 20 - Validate Plan Size Limit"""
    # Given - create very large plan
    large_subtasks = []
    for i in range(100):
        task = SubTask(
            task_id=f"task_{i}",
            description="x" * 10000,  # 10K chars
            agent_type="test_agent",
            dependencies=[],
            expected_outputs=["output"],
            inputs={"large_data": "y" * 5000}  # Add more bulk
        )
        large_subtasks.append(task)

    large_plan = Plan(
        plan_id="large_plan",
        goal_id="goal_123",
        subtasks=large_subtasks,
        execution_strategy="sequential",
        estimated_total_duration=10000,
        confidence_score=0.8
    )

    # When/Then - should raise PlanSizeError
    with pytest.raises(PlanSizeError) as exc_info:
        validate_plan_size(large_plan)

    # Error message includes plan ID and size
    assert "large_plan" in str(exc_info.value)
    assert "bytes" in str(exc_info.value).lower()
```

---

## Criterios de Validación

### Funcionales
- ✓ Goal Parser convierte natural language a structured Goal objects
- ✓ Task Decomposer genera SubTasks con dependencies correctas
- ✓ Pydantic valida tipos y campos requeridos automáticamente
- ✓ DependencyValidator detecta cycles, dangling deps, y transitive deps
- ✓ CompletenessValidator verifica que todos los task categories estén presentes

### No Funcionales
- ✓ Goal parsing < 1s (p95)
- ✓ Task decomposition < 2s (p95)
- ✓ Plan validation < 200ms
- ✓ Goal parsing cost < $0.002
- ✓ Task decomposition cost < $0.005
- ✓ Plan size < 1MB

### Calidad
- ✓ Task completeness > 95%
- ✓ Dependency accuracy > 90%
- ✓ Type safety: 100% (via Pydantic)
- ✓ Error messages descriptivos y actionables

---

## Notas de Implementación

### Pydantic Best Practices

```python
from pydantic import BaseModel, Field, validator

class SubTask(BaseModel):
    """Subtask with validation."""

    task_id: str = Field(..., min_length=1, description="Unique task ID")
    description: str = Field(..., min_length=10, description="Task description")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")

    @validator('priority')
    def validate_priority_range(cls, v):
        """Ensure priority is in valid range."""
        if not 1 <= v <= 10:
            raise ValueError(f"Priority must be 1-10, got {v}")
        return v

    @validator('description')
    def validate_description_not_empty(cls, v):
        """Ensure description is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")
        return v

    class Config:
        """Pydantic config."""
        validate_assignment = True  # Validate on attribute assignment
        json_schema_extra = {
            "example": {
                "task_id": "task_001",
                "description": "Search for flights to Paris",
                "priority": 8
            }
        }
```

### LLM Prompting for Decomposition

```python
DECOMPOSITION_PROMPT = """You are an expert task decomposition system.

Break down the following goal into specific, executable subtasks.

Goal: {goal_description}
Constraints: {constraints}

For each subtask, provide:
1. description: Clear, actionable description (verb + object)
2. dependencies: List of task indices this depends on (0-indexed)
3. priority: 1-10 (10 = highest)
4. estimated_duration_seconds: Realistic estimate

Guidelines:
- Create 4-8 subtasks for simple goals, 8-15 for complex goals
- Identify dependencies based on data flow (which tasks need outputs from others?)
- Assign higher priority to critical path tasks
- Include validation/verification as final task

Return JSON:
{
  "tasks": [
    {
      "description": "string",
      "dependencies": [0, 1],
      "priority": 8,
      "estimated_duration_seconds": 30
    }
  ]
}
"""
```

---

## Referencias

1. [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
2. [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
3. [UC-SYS-006: Planning and Replanning Workflow](../casos_uso/UC-SYS-006_planning_replanning_workflow.md)
4. [Pydantic Documentation](https://docs.pydantic.dev)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Total Escenarios**: 20
