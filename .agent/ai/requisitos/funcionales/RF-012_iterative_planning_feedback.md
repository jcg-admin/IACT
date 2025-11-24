# RF-012: Iterative Planning and Feedback with Failure Transparency

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Planning Design
**Relación**:
- Implementa [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
- Sigue [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
- Relacionado con [UC-SYS-006: Planning and Replanning Workflow](../casos_uso/UC-SYS-006_planning_replanning_workflow.md)

---

## Descripción

El sistema debe adaptar plans dinámicamente basándose en execution feedback, manejar failures con transparencia inmediata, seleccionar estrategias de re-planning apropiadas, y ajustar confidence scores para reflejar realidad. **Principio clave**: Transparencia inmediata ante fallos - nunca ocultar errores, siempre comunicar estado y estrategia de recuperación.

**Capacidades principales**:
1. **Failure Detection**: Detectar task failures inmediatamente y clasificar por tipo
2. **Immediate Transparency**: Comunicar fallos al usuario sin delay, con contexto y next steps
3. **Re-planning Strategies**: Retry con different agent, decompose further, o find workaround
4. **Feedback Loops**: Collect execution feedback y usar para adjust plans
5. **Confidence Adjustment**: Actualizar confidence_score basado en outcomes
6. **Human-in-the-Loop**: Solicitar aprobación humana para low-confidence plans o persistent failures

---

## Escenarios de Aceptación (Gherkin)

### Categoría: Failure Detection and Transparency

#### Escenario 1: Detect Task Failure Immediately
```gherkin
Given un plan en ejecución
When task_001 (flight_agent) falla después de 10s con error "Agent timeout"
Then el sistema debe detectar el failure inmediatamente (< 100ms después del timeout)
And debe crear ExecutionFeedback con:
  | Campo | Valor |
  | task_id | task_001 |
  | feedback_type | FAILURE |
  | errors | ["Agent timeout after 10s"] |
  | duration_seconds | 10 |
And debe marcar task_001.status = FAILED
And debe notificar al orchestrator inmediatamente
```

**Test Template**:
```python
def test_detect_task_failure_immediately():
    """RF-012: Escenario 1 - Detect Task Failure Immediately"""
    orchestrator = ExecutionOrchestrator()
    planner = IterativePlanner()

    # Given - plan in execution
    plan = create_test_plan()

    # When - task fails
    start_failure_time = time.time()

    # Simulate task failure
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

    # Then - immediate detection
    assert detection_time < 0.1, f"Detection took {detection_time:.3f}s (should be < 100ms)"

    # Feedback created correctly
    assert task_failure.feedback_type == FeedbackType.FAILURE
    assert "timeout" in str(task_failure.errors).lower()

    # Task marked as failed
    failed_task = next(t for t in plan.subtasks if t.task_id == "task_001")
    assert failed_task.status == TaskStatus.FAILED
```

---

#### Escenario 2: Immediate User Notification on Failure
```gherkin
Given task_001 falla
When el sistema detecta el failure
Then debe enviar notification al usuario en < 500ms con:
  | Campo | Contenido |
  | severity | ERROR |
  | task_id | task_001 |
  | error_summary | "Flight search failed: Agent timeout" |
  | recovery_strategy | "Retrying with backup agent" |
  | estimated_delay | "2-3 seconds" |
And debe incluir link a detailed logs
And NO debe ocultar el error o esperar a batch notifications
```

**Test Template**:
```python
def test_immediate_user_notification_on_failure():
    """RF-012: Escenario 2 - Immediate User Notification on Failure"""
    from unittest.mock import Mock

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
        cost=0.0,
        suggested_adjustments="Retry with different agent"
    )

    # When - handle failure
    start_time = time.time()
    orchestrator.handle_task_completion(task_failure)
    notification_time = time.time() - start_time

    # Then - immediate notification
    assert notification_time < 0.5, f"Notification took {notification_time:.3f}s"

    # Notification sent with correct details
    notification_service.send.assert_called_once()
    call_args = notification_service.send.call_args[0][0]

    assert call_args["severity"] == "ERROR"
    assert call_args["task_id"] == "task_001"
    assert "timeout" in call_args["error_summary"].lower()
    assert "retry" in call_args["recovery_strategy"].lower()
    assert call_args["estimated_delay"] is not None

    # Must include logs link
    assert "logs_url" in call_args or "log_link" in call_args
```

---

#### Escenario 3: Classify Failure Type for Strategy Selection
```gherkin
Given diferentes tipos de task failures
When el sistema analiza el error
Then debe clasificar correctamente:
  | Error Message | Feedback Type | Suggested Strategy |
  | "Agent timeout after 10s" | FAILURE | RETRY_DIFFERENT_AGENT |
  | "Task too complex to execute" | FAILURE | DECOMPOSE_FURTHER |
  | "Total cost $2150 exceeds budget $2000" | CONSTRAINT_VIOLATION | ADJUST_PARAMETERS |
  | "Dependency task_001 failed" | DEPENDENCY_FAILURE | FIX_DEPENDENCIES |
And debe seleccionar la estrategia apropiada en base a la classification
```

**Test Template**:
```python
def test_classify_failure_type():
    """RF-012: Escenario 3 - Classify Failure Type for Strategy Selection"""
    planner = IterativePlanner()

    # Test case 1: Timeout → Retry different agent
    timeout_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )
    strategy1 = planner._select_strategy(timeout_feedback)
    assert strategy1 == "RETRY_DIFFERENT_AGENT"

    # Test case 2: Too complex → Decompose
    complex_feedback = ExecutionFeedback(
        task_id="task_002",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Task too complex"],
        duration_seconds=5,
        cost=0.0,
        suggested_adjustments="Task too complex to execute in one step"
    )
    strategy2 = planner._select_strategy(complex_feedback)
    assert strategy2 == "DECOMPOSE_FURTHER"

    # Test case 3: Constraint violation → Adjust parameters
    violation_feedback = ExecutionFeedback(
        task_id="task_003",
        feedback_type=FeedbackType.CONSTRAINT_VIOLATION,
        actual_outputs={"total_cost": 2150, "budget": 2000},
        errors=["Total cost $2150 exceeds budget $2000"],
        duration_seconds=1,
        cost=0.0
    )
    strategy3 = planner._select_strategy(violation_feedback)
    assert strategy3 == "ADJUST_PARAMETERS"

    # Test case 4: Dependency failure → Fix dependencies
    dep_feedback = ExecutionFeedback(
        task_id="task_004",
        feedback_type=FeedbackType.DEPENDENCY_FAILURE,
        actual_outputs={},
        errors=["Dependency task_001 failed"],
        duration_seconds=0,
        cost=0.0
    )
    strategy4 = planner._select_strategy(dep_feedback)
    assert strategy4 == "FIX_DEPENDENCIES"
```

---

### Categoría: Re-planning Strategies

#### Escenario 4: Retry with Different Agent
```gherkin
Given task_001 (flight_agent) falló con timeout
When el IterativePlanner ejecuta estrategia RETRY_DIFFERENT_AGENT
Then debe:
  1. Consultar SemanticRouter para obtener backup agent (top_k=2, tomar segundo)
  2. Crear nuevo SubTask: task_001_retry con backup_flight_agent
  3. Copiar inputs y expected_outputs del original
  4. Configurar retry_policy = {max_retries: 1, backoff_seconds: 5}
  5. Reducir plan.confidence_score en -0.1
  6. Agregar a plan.subtasks en la posición del task original
And debe crear PlanRevision con changes = ["Retry task task_001 with agent backup_flight_agent"]
And debe notificar al usuario de la estrategia de retry
```

**Test Template**:
```python
def test_retry_with_different_agent():
    """RF-012: Escenario 4 - Retry with Different Agent"""
    planner = IterativePlanner()
    router = SemanticRouter(agents=test_agents, embedding_fn=mock_embed)

    # Given - failed task
    original_plan = create_test_plan()
    failed_task = original_plan.subtasks[0]  # task_001
    original_confidence = original_plan.confidence_score

    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )

    # When - replan with retry strategy
    revised_plan, revision = planner.replan(
        original_plan=original_plan,
        feedback=[failure_feedback],
        goal=test_goal
    )

    # Then - backup agent selected
    retry_task = revised_plan.subtasks[0]
    assert retry_task.task_id == "task_001_retry"
    assert retry_task.agent_type != failed_task.agent_type
    assert retry_task.agent_type in ["backup_flight_agent", "alternative_flight_agent"]

    # Inputs/outputs copied
    assert retry_task.inputs == failed_task.inputs
    assert retry_task.expected_outputs == failed_task.expected_outputs

    # Retry policy configured
    assert retry_task.retry_policy is not None
    assert retry_task.retry_policy["max_retries"] == 1
    assert retry_task.retry_policy["backoff_seconds"] >= 2

    # Confidence reduced
    assert revised_plan.confidence_score == original_confidence - 0.1

    # Revision details
    assert revision.trigger == "1 failures, 0 violations"
    assert any("retry" in c.lower() for c in revision.changes)
    assert "task_001" in str(revision.changes)
```

---

#### Escenario 5: Decompose Further on Complexity
```gherkin
Given task_002 falla con error "Task too complex to execute"
When el planner ejecuta estrategia DECOMPOSE_FURTHER
Then debe:
  1. Analizar task_002.description para identificar sub-steps
  2. Crear 2-4 nuevos SubTasks más granulares
  3. Establecer dependencies entre los nuevos tasks (secuencial si necesario)
  4. Remover task_002 del plan (añadir a removed_task_ids)
  5. Insertar nuevos tasks en la posición de task_002
  6. Reducir confidence en -0.05
And nuevos tasks deben tener estimated_duration_seconds < original task
And debe mantener el mismo expected_output final
```

**Test Template**:
```python
def test_decompose_further_on_complexity():
    """RF-012: Escenario 5 - Decompose Further on Complexity"""
    planner = IterativePlanner()

    # Given - complex task failed
    original_plan = create_test_plan()
    complex_task = SubTask(
        task_id="task_002",
        description="Book complete travel package (flight + hotel + activities)",
        agent_type="travel_agent",
        dependencies=[],
        expected_outputs=["complete_package"],
        estimated_duration_seconds=60
    )
    original_plan.subtasks.append(complex_task)
    original_confidence = original_plan.confidence_score

    failure_feedback = ExecutionFeedback(
        task_id="task_002",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Task too complex to execute in one step"],
        duration_seconds=5,
        cost=0.0,
        suggested_adjustments="Task too complex, decompose into smaller steps"
    )

    # When - replan with decompose strategy
    revised_plan, revision = planner.replan(
        original_plan=original_plan,
        feedback=[failure_feedback],
        goal=test_goal
    )

    # Then - new subtasks created
    assert len(revision.new_subtasks) >= 2
    assert len(revision.new_subtasks) <= 4

    # Original task removed
    assert "task_002" in revision.removed_task_ids

    # New tasks are more granular
    for new_task in revision.new_subtasks:
        assert new_task.estimated_duration_seconds < complex_task.estimated_duration_seconds

    # Final output preserved
    final_outputs = [out for task in revision.new_subtasks for out in task.expected_outputs]
    assert "complete_package" in final_outputs or "package" in str(final_outputs)

    # Confidence adjusted
    assert revised_plan.confidence_score == original_confidence - 0.05
```

---

#### Escenario 6: Adjust Parameters for Constraint Violation
```gherkin
Given task_004 (validation) falla porque total_cost=$2150 > budget=$2000
When el planner ejecuta estrategia ADJUST_PARAMETERS
Then debe:
  1. Identificar tasks que contribuyen al overage (flight, hotel)
  2. Agregar constraint "max_price" a task_001 (flight): 600
  3. Agregar constraint "max_price_per_night" a task_002 (hotel): 150
  4. Marcar tasks 001 y 002 como modified_task_ids
  5. Re-ejecutar tasks modificados
  6. Re-ejecutar validation task
  7. Reducir confidence en -0.08
And debe comunicar al usuario qué parámetros se ajustaron y por qué
```

**Test Template**:
```python
def test_adjust_parameters_for_constraint_violation():
    """RF-012: Escenario 6 - Adjust Parameters for Constraint Violation"""
    planner = IterativePlanner()

    # Given - budget violation
    original_plan = create_test_plan()
    original_confidence = original_plan.confidence_score

    violation_feedback = ExecutionFeedback(
        task_id="task_004",
        feedback_type=FeedbackType.CONSTRAINT_VIOLATION,
        actual_outputs={
            "budget_status": "EXCEEDED",
            "total_cost": 2150,
            "budget": 2000,
            "overage": 150,
            "breakdown": {
                "flight": 720,
                "hotel": 660,
                "activities": 103
            }
        },
        errors=["Total cost $2150 exceeds budget $2000"],
        duration_seconds=1,
        cost=0.005,
        suggested_adjustments="Select cheaper flight or hotel options"
    )

    # When - replan with adjust parameters
    revised_plan, revision = planner.replan(
        original_plan=original_plan,
        feedback=[violation_feedback],
        goal=test_goal
    )

    # Then - parameters adjusted
    assert len(revision.modified_task_ids) >= 2

    # Find modified tasks
    modified_tasks = [t for t in revised_plan.subtasks if t.task_id in revision.modified_task_ids]

    # Check for price constraints
    flight_task = next((t for t in modified_tasks if "flight" in t.description.lower()), None)
    hotel_task = next((t for t in modified_tasks if "hotel" in t.description.lower()), None)

    if flight_task:
        assert "max_price" in flight_task.inputs or "budget" in flight_task.inputs

    if hotel_task:
        assert "max_price_per_night" in hotel_task.inputs or "max_price" in hotel_task.inputs

    # Confidence adjusted
    assert abs(revised_plan.confidence_score - (original_confidence - 0.08)) < 0.01

    # User notification details
    assert any("adjust" in c.lower() or "parameter" in c.lower() for c in revision.changes)
```

---

#### Escenario 7: Find Workaround for Unavailable Resource
```gherkin
Given task_002 (book_hotel) falla porque "Preferred hotel fully booked"
When el planner ejecuta estrategia FIND_WORKAROUND
Then debe:
  1. Analizar goal constraints para identificar alternatives
  2. Crear nuevo task: "Search alternative hotels in nearby locations"
  3. Mantener mismo expected_output type (hotel_booking)
  4. Ajustar task inputs para expandir search radius
  5. Reducir confidence en -0.15 (workarounds son menos confiables)
And debe documentar por qué se necesitó el workaround en revision
```

**Test Template**:
```python
def test_find_workaround_for_unavailable_resource():
    """RF-012: Escenario 7 - Find Workaround for Unavailable Resource"""
    planner = IterativePlanner()

    # Given - resource unavailable
    original_plan = create_test_plan()
    original_confidence = original_plan.confidence_score

    failure_feedback = ExecutionFeedback(
        task_id="task_002",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Preferred hotel fully booked"],
        duration_seconds=3,
        cost=0.015,
        suggested_adjustments="Try alternative hotels or different location"
    )

    # When - replan with workaround
    revised_plan, revision = planner.replan(
        original_plan=original_plan,
        feedback=[failure_feedback],
        goal=test_goal
    )

    # Then - workaround created
    assert len(revision.new_subtasks) > 0

    # Workaround task
    workaround_task = revision.new_subtasks[0]
    assert "alternative" in workaround_task.description.lower() or "nearby" in workaround_task.description.lower()

    # Same output type
    assert any("hotel" in out.lower() for out in workaround_task.expected_outputs)

    # Expanded search parameters
    assert workaround_task.inputs is not None
    # May have "radius" or "area" or "alternative_locations"

    # Significant confidence reduction
    assert abs(revised_plan.confidence_score - (original_confidence - 0.15)) < 0.01

    # Workaround documented
    assert any("workaround" in c.lower() for c in revision.changes)
```

---

### Categoría: Feedback Loops and Learning

#### Escenario 8: Collect Execution Feedback for All Tasks
```gherkin
Given un plan con 4 subtasks se ejecuta completamente
When la ejecución finaliza
Then debe haber exactamente 4 ExecutionFeedback objects
And cada feedback debe incluir:
  | Campo | Validación |
  | task_id | Matches subtask ID |
  | feedback_type | SUCCESS, FAILURE, PARTIAL_SUCCESS, etc |
  | actual_outputs | Dict (puede estar vacío si falla) |
  | duration_seconds | > 0 |
  | cost | >= 0 |
And feedback debe estar ordenado por execution timestamp
```

**Test Template**:
```python
def test_collect_execution_feedback():
    """RF-012: Escenario 8 - Collect Execution Feedback for All Tasks"""
    orchestrator = ExecutionOrchestrator()

    # Given - plan with 4 tasks
    plan = create_test_plan()
    assert len(plan.subtasks) == 4

    # When - execute plan
    feedback_list = orchestrator.execute_plan(plan)

    # Then - feedback for all tasks
    assert len(feedback_list) == 4

    # Validate each feedback
    for i, feedback in enumerate(feedback_list):
        # Matches task ID
        assert feedback.task_id in [t.task_id for t in plan.subtasks]

        # Has feedback type
        assert feedback.feedback_type in [
            FeedbackType.SUCCESS,
            FeedbackType.FAILURE,
            FeedbackType.PARTIAL_SUCCESS,
            FeedbackType.CONSTRAINT_VIOLATION,
            FeedbackType.DEPENDENCY_FAILURE
        ]

        # Has duration and cost
        assert feedback.duration_seconds > 0
        assert feedback.cost >= 0.0

    # Ordered by timestamp (if timestamps recorded)
    if hasattr(feedback_list[0], 'timestamp'):
        timestamps = [f.timestamp for f in feedback_list]
        assert timestamps == sorted(timestamps)
```

---

#### Escenario 9: Update Confidence Based on Execution Success
```gherkin
Given un plan con confidence_score=0.85
When se ejecuta exitosamente (4/4 tasks succeed)
Then debe actualizar confidence_score a 0.90 (+0.05 bonus por success)
And debe registrar outcome en ConfidenceCalibrator
And futuras plans similares deben beneficiarse del learning
```

**Test Template**:
```python
def test_update_confidence_based_on_success():
    """RF-012: Escenario 9 - Update Confidence Based on Execution Success"""
    planner = IterativePlanner()
    calibrator = ConfidenceCalibrator()

    # Given - plan with initial confidence
    plan = create_test_plan()
    plan.confidence_score = 0.85
    original_confidence = plan.confidence_score

    # When - successful execution
    success_feedback = [
        ExecutionFeedback(task_id=f"task_{i:03d}", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"result": "ok"}, errors=[],
                         duration_seconds=2, cost=0.01)
        for i in range(1, 5)
    ]

    # Update confidence after success
    planner.update_confidence_on_success(plan, success_feedback)

    # Record outcome
    outcome = PlanOutcome(
        plan_id=plan.plan_id,
        confidence_score=original_confidence,
        success=True,
        execution_time=8.0,
        cost=0.04
    )
    calibrator.record_outcome(outcome)

    # Then - confidence increased
    assert plan.confidence_score > original_confidence
    assert abs(plan.confidence_score - 0.90) < 0.05

    # Outcome recorded
    assert len(calibrator.outcomes) > 0
    assert calibrator.outcomes[-1].success == True
```

---

#### Escenario 10: Penalize Confidence on Failures
```gherkin
Given un plan con confidence_score=0.85
When 2/4 tasks fallan
Then debe reducir confidence_score basado en failure rate:
  | Failures | Reduction |
  | 1 | -0.10 |
  | 2 | -0.20 |
  | 3 | -0.35 |
And debe registrar outcome en calibrator con success=False
```

**Test Template**:
```python
def test_penalize_confidence_on_failures():
    """RF-012: Escenario 10 - Penalize Confidence on Failures"""
    planner = IterativePlanner()
    calibrator = ConfidenceCalibrator()

    # Given - plan with initial confidence
    plan = create_test_plan()
    plan.confidence_score = 0.85
    original_confidence = plan.confidence_score

    # When - 2/4 tasks fail
    mixed_feedback = [
        ExecutionFeedback(task_id="task_001", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"ok": True}, errors=[], duration_seconds=2, cost=0.01),
        ExecutionFeedback(task_id="task_002", feedback_type=FeedbackType.FAILURE,
                         actual_outputs={}, errors=["Failed"], duration_seconds=1, cost=0.0),
        ExecutionFeedback(task_id="task_003", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"ok": True}, errors=[], duration_seconds=2, cost=0.01),
        ExecutionFeedback(task_id="task_004", feedback_type=FeedbackType.FAILURE,
                         actual_outputs={}, errors=["Failed"], duration_seconds=1, cost=0.0),
    ]

    failure_count = sum(1 for f in mixed_feedback if f.feedback_type == FeedbackType.FAILURE)

    # Update confidence after failures
    planner.update_confidence_on_failures(plan, mixed_feedback)

    # Record outcome
    outcome = PlanOutcome(
        plan_id=plan.plan_id,
        confidence_score=original_confidence,
        success=False,  # Overall plan failed
        execution_time=6.0,
        cost=0.02
    )
    calibrator.record_outcome(outcome)

    # Then - confidence reduced based on failure count
    expected_reduction = 0.10 * failure_count  # 0.20 for 2 failures
    assert abs(plan.confidence_score - (original_confidence - expected_reduction)) < 0.05

    # Outcome recorded as failure
    assert calibrator.outcomes[-1].success == False
```

---

### Categoría: Max Revisions and Abort Conditions

#### Escenario 11: Enforce Max Revisions Limit
```gherkin
Given IterativePlanner.MAX_REVISIONS = 3
When un plan ha sido revisado 3 veces
And se intenta una 4ta revisión
Then debe lanzar MaxRevisionsExceeded exception
And debe incluir en mensaje: "Plan {plan_id} exceeded 3 revisions"
And debe incluir latest errors en la exception
And debe notificar al usuario que el plan es unfeasible
```

**Test Template**:
```python
def test_enforce_max_revisions_limit():
    """RF-012: Escenario 11 - Enforce Max Revisions Limit"""
    planner = IterativePlanner()
    planner.MAX_REVISIONS = 3

    # Given - plan already revised 3 times
    plan = create_test_plan()
    plan.metadata["revision_count"] = 3

    # Simulate 3 previous revisions
    for i in range(3):
        revision = PlanRevision(
            revision_id=f"rev_{i}",
            original_plan_id=plan.plan_id,
            trigger=f"Failure {i+1}",
            changes=[f"Change {i+1}"],
            new_subtasks=[],
            removed_task_ids=[],
            modified_task_ids=[],
            confidence_delta=-0.1
        )
        plan.metadata.setdefault("revisions", []).append(revision)

    # When - attempt 4th revision
    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Still failing after 3 retries"],
        duration_seconds=1,
        cost=0.0
    )

    # Then - should raise MaxRevisionsExceeded
    with pytest.raises(MaxRevisionsExceeded) as exc_info:
        planner.replan(
            original_plan=plan,
            feedback=[failure_feedback],
            goal=test_goal
        )

    # Error message includes plan ID and count
    assert plan.plan_id in str(exc_info.value)
    assert "3" in str(exc_info.value)
    assert "revision" in str(exc_info.value).lower()

    # Latest errors included
    assert "Still failing" in str(exc_info.value)
```

---

#### Escenario 12: Abort on Low Confidence After Revisions
```gherkin
Given un plan con confidence_score=0.85 inicialmente
When después de 2 revisiones, confidence_score cae a 0.25
And se intenta una 3ra revisión
Then debe lanzar LowConfidenceError
And debe incluir mensaje: "Plan confidence 0.25 too low after 2 revisions. Aborting."
And debe sugerir: "Relax constraints or change goal"
```

**Test Template**:
```python
def test_abort_on_low_confidence():
    """RF-012: Escenario 12 - Abort on Low Confidence After Revisions"""
    planner = IterativePlanner()

    # Given - plan with degraded confidence
    plan = create_test_plan()
    plan.confidence_score = 0.25  # Very low after 2 revisions
    plan.metadata["revision_count"] = 2

    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Persistent failure"],
        duration_seconds=1,
        cost=0.0
    )

    # When - attempt another revision with low confidence
    # Then - should raise LowConfidenceError
    with pytest.raises(LowConfidenceError) as exc_info:
        planner.replan(
            original_plan=plan,
            feedback=[failure_feedback],
            goal=test_goal
        )

    # Error message
    assert "0.25" in str(exc_info.value) or "confidence" in str(exc_info.value).lower()
    assert "low" in str(exc_info.value).lower()
    assert "abort" in str(exc_info.value).lower()

    # Suggestions provided
    assert "relax" in str(exc_info.value).lower() or "constraint" in str(exc_info.value).lower()
```

---

#### Escenario 13: Track Revision History
```gherkin
Given un plan que ha sido revisado 2 veces
When se consulta plan.metadata["revisions"]
Then debe contener 2 PlanRevision objects con:
  | Revision | Trigger | Changes Count |
  | rev_1 | 1 failures | >= 1 |
  | rev_2 | 1 failures | >= 1 |
And cada revision debe tener confidence_delta negativo
And se debe poder reconstruir el evolution del plan
```

**Test Template**:
```python
def test_track_revision_history():
    """RF-012: Escenario 13 - Track Revision History"""
    planner = IterativePlanner()

    # Given - plan with revisions
    plan = create_test_plan()

    # Simulate 2 revisions
    for i in range(2):
        failure_feedback = ExecutionFeedback(
            task_id=f"task_00{i+1}",
            feedback_type=FeedbackType.FAILURE,
            actual_outputs={},
            errors=[f"Error {i+1}"],
            duration_seconds=1,
            cost=0.0
        )

        revised_plan, revision = planner.replan(
            original_plan=plan,
            feedback=[failure_feedback],
            goal=test_goal
        )

        plan = revised_plan

    # Then - revision history tracked
    assert "revisions" in plan.metadata or "revision_count" in plan.metadata

    revisions = plan.metadata.get("revisions", [])
    assert len(revisions) == 2

    # Each revision has required fields
    for i, rev in enumerate(revisions):
        assert hasattr(rev, 'revision_id') or isinstance(rev, dict)
        assert hasattr(rev, 'trigger') or 'trigger' in rev
        assert hasattr(rev, 'changes') or 'changes' in rev

        # Confidence delta negative
        conf_delta = rev.confidence_delta if hasattr(rev, 'confidence_delta') else rev.get('confidence_delta')
        assert conf_delta < 0
```

---

### Categoría: Human-in-the-Loop

#### Escenario 14: Request Human Approval for Low Confidence Plan
```gherkin
Given un plan generado con confidence_score=0.45 (< 0.5)
When el sistema valida el plan
Then debe marcar plan.metadata.requires_approval = True
And debe crear HumanApprovalRequest con:
  | Campo | Contenido |
  | confidence_score | 0.45 |
  | reasons | Lista de low confidence reasons |
  | recommended_action | REVIEW_AND_ADJUST |
And debe pausar execution hasta recibir human decision
And NO debe ejecutar automáticamente sin aprobación
```

**Test Template**:
```python
def test_request_human_approval_low_confidence():
    """RF-012: Escenario 14 - Request Human Approval for Low Confidence Plan"""
    from unittest.mock import Mock, patch

    planner = IterativePlanner()
    human_approval_service = Mock()

    # Given - low confidence plan
    plan = create_test_plan()
    plan.confidence_score = 0.45

    # When - validate plan
    planner.validate_and_request_approval_if_needed(plan, human_approval_service)

    # Then - approval required
    assert plan.metadata.get("requires_approval") == True

    # Approval request created
    human_approval_service.request_approval.assert_called_once()
    request = human_approval_service.request_approval.call_args[0][0]

    assert request.confidence_score == 0.45
    assert request.recommended_action == "REVIEW_AND_ADJUST"
    assert len(request.reasons) > 0

    # Execution should be paused (not tested here, but plan should not execute)
```

---

#### Escenario 15: Handle Human Approval Decision
```gherkin
Given un plan esperando human approval
When el human reviewer responde con decision="APPROVE"
Then debe ejecutar el plan a pesar de low confidence
And debe registrar en logs: "Plan {plan_id} approved by human despite confidence 0.45"
---
When el human reviewer responde con decision="ADJUST" y adjustments=[...]
Then debe aplicar human adjustments al plan
And debe re-generar plan con adjustments
And debe ejecutar el adjusted plan
---
When el human reviewer responde con decision="REJECT"
Then debe abortar planning
And debe lanzar PlanRejectedError
And debe notificar al usuario
```

**Test Template**:
```python
def test_handle_human_approval_decision():
    """RF-012: Escenario 15 - Handle Human Approval Decision"""
    from unittest.mock import Mock

    planner = IterativePlanner()

    # Given - plan awaiting approval
    plan = create_test_plan()
    plan.confidence_score = 0.45
    plan.metadata["requires_approval"] = True

    # Test case 1: APPROVE
    approval_decision = HumanApprovalDecision(
        plan_id=plan.plan_id,
        action="APPROVE",
        adjustments=None,
        comments="Proceed with caution"
    )

    result = planner.handle_approval_decision(plan, approval_decision)
    assert result == "EXECUTE"  # Plan should execute

    # Test case 2: ADJUST
    adjust_decision = HumanApprovalDecision(
        plan_id=plan.plan_id,
        action="ADJUST",
        adjustments=[
            {"task_id": "task_001", "field": "priority", "new_value": 10}
        ],
        comments="Increase priority of flight search"
    )

    adjusted_plan = planner.handle_approval_decision(plan, adjust_decision)
    assert adjusted_plan is not None
    # Verify adjustment applied
    task_001 = next(t for t in adjusted_plan.subtasks if t.task_id == "task_001")
    assert task_001.priority == 10

    # Test case 3: REJECT
    reject_decision = HumanApprovalDecision(
        plan_id=plan.plan_id,
        action="REJECT",
        adjustments=None,
        comments="Plan not feasible"
    )

    with pytest.raises(PlanRejectedError) as exc_info:
        planner.handle_approval_decision(plan, reject_decision)

    assert "reject" in str(exc_info.value).lower()
```

---

#### Escenario 16: Request Human Intervention After Max Retries
```gherkin
Given un task ha fallado 3 veces consecutivas
When el sistema detecta persistent failure
Then debe crear FailureEscalationRequest con:
  | Campo | Contenido |
  | task_id | task_001 |
  | failure_count | 3 |
  | errors | Lista de errores de cada intento |
  | suggested_actions | [Manual intervention, Change approach] |
And debe notificar al usuario inmediatamente
And debe pausar execution del plan
And debe esperar human guidance antes de continuar
```

**Test Template**:
```python
def test_request_human_intervention_after_max_retries():
    """RF-012: Escenario 16 - Request Human Intervention After Max Retries"""
    from unittest.mock import Mock

    orchestrator = ExecutionOrchestrator()
    escalation_service = Mock()
    orchestrator.escalation_service = escalation_service

    # Given - task failed 3 times
    plan = create_test_plan()
    task_001 = plan.subtasks[0]
    task_001.metadata = {"failure_count": 3, "errors_history": [
        "Error 1: Timeout",
        "Error 2: Timeout",
        "Error 3: Timeout"
    ]}

    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Error 3: Timeout"],
        duration_seconds=1,
        cost=0.0
    )

    # When - detect persistent failure
    orchestrator.handle_task_completion(failure_feedback)

    # Then - escalation requested
    escalation_service.escalate_failure.assert_called_once()
    request = escalation_service.escalate_failure.call_args[0][0]

    assert request.task_id == "task_001"
    assert request.failure_count == 3
    assert len(request.errors) == 3
    assert len(request.suggested_actions) > 0

    # Execution should pause (mock or check state)
    assert orchestrator.is_paused() or plan.metadata.get("execution_paused") == True
```

---

### Categoría: Transparency and Communication

#### Escenario 17: Provide Real-Time Progress Updates
```gherkin
Given un plan con 4 tasks en ejecución
When cada task completa
Then debe enviar progress update al usuario con:
  | Campo | Contenido |
  | task_id | ID del task completado |
  | status | SUCCESS o FAILURE |
  | progress_percentage | (completed_tasks / total_tasks) * 100 |
  | estimated_remaining_time | Basado en remaining tasks |
And updates deben enviarse en < 200ms después de task completion
And NO debe esperar a batch updates
```

**Test Template**:
```python
def test_provide_realtime_progress_updates():
    """RF-012: Escenario 17 - Provide Real-Time Progress Updates"""
    from unittest.mock import Mock

    orchestrator = ExecutionOrchestrator()
    progress_service = Mock()
    orchestrator.progress_service = progress_service

    # Given - plan with 4 tasks
    plan = create_test_plan()
    total_tasks = len(plan.subtasks)

    # When - tasks complete one by one
    for i, task in enumerate(plan.subtasks):
        feedback = ExecutionFeedback(
            task_id=task.task_id,
            feedback_type=FeedbackType.SUCCESS,
            actual_outputs={"result": "ok"},
            errors=[],
            duration_seconds=2,
            cost=0.01
        )

        start_time = time.time()
        orchestrator.handle_task_completion(feedback)
        update_time = time.time() - start_time

        # Then - immediate progress update
        assert update_time < 0.2, f"Update took {update_time:.3f}s (should be < 200ms)"

        # Progress update sent
        assert progress_service.send_update.call_count == i + 1

        last_update = progress_service.send_update.call_args[0][0]
        assert last_update["task_id"] == task.task_id
        assert last_update["status"] in ["SUCCESS", "FAILURE"]

        expected_progress = ((i + 1) / total_tasks) * 100
        assert abs(last_update["progress_percentage"] - expected_progress) < 1.0
```

---

#### Escenario 18: Explain Re-planning Decision to User
```gherkin
Given task_001 falla y se decide re-plan con estrategia RETRY_DIFFERENT_AGENT
When se notifica al usuario
Then el mensaje debe incluir:
  | Elemento | Ejemplo |
  | What failed | "Flight search (task_001) failed" |
  | Why it failed | "Agent timeout after 10s" |
  | What we're doing | "Retrying with backup flight agent" |
  | Expected impact | "Additional 2-3 seconds delay" |
  | Confidence adjustment | "Plan confidence reduced from 0.85 to 0.75" |
And el mensaje debe ser claro y no-technical para end users
And debe incluir link a detailed technical logs para developers
```

**Test Template**:
```python
def test_explain_replanning_decision():
    """RF-012: Escenario 18 - Explain Re-planning Decision to User"""
    from unittest.mock import Mock

    planner = IterativePlanner()
    notification_service = Mock()

    # Given - task failure and replan
    plan = create_test_plan()
    plan.confidence_score = 0.85

    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Agent timeout after 10s"],
        duration_seconds=10,
        cost=0.0
    )

    # When - replan with notification
    revised_plan, revision = planner.replan(
        original_plan=plan,
        feedback=[failure_feedback],
        goal=test_goal
    )

    explanation = planner.generate_user_explanation(
        original_plan=plan,
        revised_plan=revised_plan,
        revision=revision,
        feedback=[failure_feedback]
    )

    # Then - explanation includes all elements
    assert "task_001" in explanation or "flight" in explanation.lower()
    assert "timeout" in explanation.lower()
    assert "retry" in explanation.lower() or "retrying" in explanation.lower()
    assert "backup" in explanation.lower() or "different" in explanation.lower()
    assert "delay" in explanation.lower() or "additional" in explanation.lower()
    assert "0.85" in explanation or "0.75" in explanation  # Confidence scores

    # Should be user-friendly (no technical jargon)
    assert "stack trace" not in explanation.lower()
    assert "exception" not in explanation.lower()

    # Link to detailed logs
    assert "logs" in explanation.lower() or "details" in explanation.lower()
```

---

#### Escenario 19: Log All Planning Decisions with Reasoning
```gherkin
Given cualquier planning decision (decompose, route, replan)
When la decision se ejecuta
Then debe crear log entry con level=INFO que incluya:
  | Campo | Contenido |
  | timestamp | ISO 8601 timestamp |
  | operation | "decompose_task", "route_task", "replan", etc |
  | input | Summarized input (goal, task, feedback) |
  | decision | La decisión tomada |
  | reasoning | Por qué se tomó esta decisión |
  | confidence | Confidence score antes y después |
  | cost | Cost de la operación |
And logs deben ser structured (JSON) para facilitar querying
And logs deben ser searchable por plan_id, task_id, operation
```

**Test Template**:
```python
def test_log_planning_decisions_with_reasoning():
    """RF-012: Escenario 19 - Log All Planning Decisions with Reasoning"""
    import logging
    from unittest.mock import Mock, patch
    import json

    # Mock structured logger
    mock_logger = Mock()

    planner = IterativePlanner(logger=mock_logger)

    # Given - planning decision
    plan = create_test_plan()
    failure_feedback = ExecutionFeedback(
        task_id="task_001",
        feedback_type=FeedbackType.FAILURE,
        actual_outputs={},
        errors=["Timeout"],
        duration_seconds=10,
        cost=0.0
    )

    # When - replan executed
    revised_plan, revision = planner.replan(
        original_plan=plan,
        feedback=[failure_feedback],
        goal=test_goal
    )

    # Then - decision logged
    assert mock_logger.info.called or mock_logger.log.called

    # Get log entry
    log_calls = mock_logger.info.call_args_list if mock_logger.info.called else mock_logger.log.call_args_list
    assert len(log_calls) > 0

    # Check log content (may be JSON string)
    log_entry = log_calls[0][0][0]  # First positional arg

    # If it's a JSON string, parse it
    if isinstance(log_entry, str) and log_entry.startswith('{'):
        log_data = json.loads(log_entry)
    else:
        log_data = log_entry

    # Validate fields
    if isinstance(log_data, dict):
        assert "operation" in log_data or "replan" in str(log_data).lower()
        assert "decision" in log_data or "reasoning" in log_data
        # Confidence before/after would be in the log
```

---

#### Escenario 20: Provide Post-Execution Analysis Report
```gherkin
Given un plan ha completado execution (success o failure)
When se genera el post-execution report
Then debe incluir:
  | Sección | Contenido |
  | Summary | Success/failure, total duration, total cost |
  | Task Breakdown | Status de cada task, durations, costs |
  | Revisions | Lista de all revisions con reasons |
  | Confidence Evolution | confidence_score a lo largo del tiempo |
  | Lessons Learned | Qué falló, qué funcionó, recommendations |
And debe guardar el report en plan.metadata["execution_report"]
And debe ser accessible para future planning improvements
```

**Test Template**:
```python
def test_provide_post_execution_analysis_report():
    """RF-012: Escenario 20 - Provide Post-Execution Analysis Report"""
    orchestrator = ExecutionOrchestrator()
    planner = IterativePlanner()

    # Given - completed plan execution
    plan = create_test_plan()

    # Simulate execution with some failures and revisions
    feedback_list = [
        ExecutionFeedback(task_id="task_001", feedback_type=FeedbackType.FAILURE,
                         actual_outputs={}, errors=["Timeout"], duration_seconds=10, cost=0.0),
        ExecutionFeedback(task_id="task_001_retry", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"ok": True}, errors=[], duration_seconds=3, cost=0.02),
        ExecutionFeedback(task_id="task_002", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"ok": True}, errors=[], duration_seconds=2, cost=0.015),
        ExecutionFeedback(task_id="task_003", feedback_type=FeedbackType.SUCCESS,
                         actual_outputs={"ok": True}, errors=[], duration_seconds=2, cost=0.01),
    ]

    # Add revision history
    plan.metadata["revisions"] = [
        PlanRevision(
            revision_id="rev_1",
            original_plan_id=plan.plan_id,
            trigger="1 failures",
            changes=["Retry task_001 with backup agent"],
            new_subtasks=[],
            removed_task_ids=[],
            modified_task_ids=["task_001"],
            confidence_delta=-0.1
        )
    ]

    # When - generate report
    report = orchestrator.generate_execution_report(plan, feedback_list)

    # Then - report includes all sections
    assert "summary" in report
    assert report["summary"]["total_duration"] > 0
    assert report["summary"]["total_cost"] > 0

    # Task breakdown
    assert "tasks" in report
    assert len(report["tasks"]) > 0

    # Revisions
    assert "revisions" in report
    assert len(report["revisions"]) == 1

    # Confidence evolution
    assert "confidence_evolution" in report
    # Should show how confidence changed

    # Lessons learned
    assert "lessons_learned" in report
    assert len(report["lessons_learned"]) > 0

    # Saved to plan metadata
    assert "execution_report" in plan.metadata
```

---

## Criterios de Validación

### Funcionales
- ✓ Failures detectados inmediatamente (< 100ms)
- ✓ User notifications enviadas en < 500ms después de failure
- ✓ Strategies seleccionadas correctamente basado en failure type
- ✓ Re-planning completado en < 2s
- ✓ Max revisions enforced (default: 3)
- ✓ Low confidence plans requieren human approval
- ✓ Todas las planning decisions logged con reasoning

### No Funcionales
- ✓ Failure detection latency < 100ms
- ✓ User notification latency < 500ms
- ✓ Re-planning time < 2s (p95)
- ✓ Confidence calibration correlation r > 0.7
- ✓ Revision success rate > 70%

### Transparency
- ✓ **Nunca ocultar failures** - immediate notification
- ✓ Explain replanning decisions en user-friendly language
- ✓ Provide real-time progress updates
- ✓ Log all decisions con reasoning para auditing
- ✓ Post-execution reports con lessons learned

---

## Notas de Implementación

### Immediate Failure Transparency Pattern

```python
class TransparentOrchestrator:
    """Orchestrator with immediate failure transparency."""

    def handle_task_completion(self, feedback: ExecutionFeedback):
        """Handle task completion with immediate transparency."""

        # 1. IMMEDIATE detection (< 100ms)
        start_time = time.time()

        if feedback.feedback_type == FeedbackType.FAILURE:
            # 2. IMMEDIATE notification (< 500ms total)
            self._notify_user_immediately(feedback)

            # 3. Log with full context
            self._log_failure_with_context(feedback)

            # 4. Classify and select strategy
            strategy = self._select_recovery_strategy(feedback)

            # 5. Communicate strategy to user
            self._explain_recovery_strategy(feedback, strategy)

            # 6. Execute recovery
            self._execute_recovery(feedback, strategy)

        detection_time = time.time() - start_time
        assert detection_time < 0.5, "Failure handling too slow"

    def _notify_user_immediately(self, feedback: ExecutionFeedback):
        """Send immediate notification - NO batching."""
        notification = {
            "severity": "ERROR",
            "timestamp": datetime.now().isoformat(),
            "task_id": feedback.task_id,
            "error_summary": self._summarize_error(feedback.errors),
            "recovery_strategy": "Analyzing...",  # Updated later
            "estimated_delay": "Computing...",
            "logs_url": f"/logs/{feedback.task_id}"
        }

        # Send immediately - don't wait for batch
        self.notification_service.send(notification)

        # Update with strategy once determined
        # (sent as separate notification)

    def _log_failure_with_context(self, feedback: ExecutionFeedback):
        """Log failure with full context for debugging."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "operation": "task_execution",
            "task_id": feedback.task_id,
            "error": feedback.errors,
            "duration_seconds": feedback.duration_seconds,
            "cost": feedback.cost,
            "context": {
                "plan_id": self.current_plan.plan_id,
                "goal_id": self.current_goal.goal_id,
                "agent_type": self._get_agent_type(feedback.task_id),
                "dependencies": self._get_task_dependencies(feedback.task_id)
            },
            "recovery_attempted": False  # Updated later
        }

        self.logger.error(json.dumps(log_entry))

    def _explain_recovery_strategy(self, feedback: ExecutionFeedback, strategy: str):
        """Explain recovery strategy in user-friendly language."""

        explanations = {
            "RETRY_DIFFERENT_AGENT": {
                "what": f"Retrying {self._get_task_name(feedback.task_id)} with a different agent",
                "why": "The previous agent timed out or was unavailable",
                "impact": "This will add 2-3 seconds to the total time",
                "confidence_change": "Slightly reduced (new agent may not be as optimal)"
            },
            "DECOMPOSE_FURTHER": {
                "what": f"Breaking down {self._get_task_name(feedback.task_id)} into smaller steps",
                "why": "The task was too complex to complete in one operation",
                "impact": "This will add 3-5 seconds but increases success chances",
                "confidence_change": "Maintained (smaller tasks are easier to complete)"
            },
            "ADJUST_PARAMETERS": {
                "what": f"Adjusting search parameters for {self._get_task_name(feedback.task_id)}",
                "why": "The original parameters violated budget constraints",
                "impact": "Results may be slightly different (e.g., cheaper options)",
                "confidence_change": "Slightly reduced (fewer options available)"
            }
        }

        explanation = explanations.get(strategy, {"what": "Attempting recovery"})

        # Send user-friendly notification
        self.notification_service.send({
            "severity": "INFO",
            "title": "Recovery Strategy",
            "what_were_doing": explanation["what"],
            "why": explanation["why"],
            "expected_impact": explanation["impact"],
            "confidence_adjustment": explanation["confidence_change"]
        })
```

### Confidence Calibration System

```python
class ConfidenceCalibrator:
    """Calibrates confidence scores based on historical outcomes."""

    def __init__(self):
        self.outcomes: List[PlanOutcome] = []

    def adjust_confidence(self, raw_confidence: float) -> float:
        """Adjust confidence based on historical calibration."""

        if len(self.outcomes) < 10:
            return raw_confidence  # Not enough data

        metrics = self.calculate_calibration()

        # If historically over-confident, reduce high scores
        if metrics.over_confidence_rate > 0.15:
            if raw_confidence > 0.8:
                adjustment = -0.1 * metrics.over_confidence_rate
                return max(0.0, min(1.0, raw_confidence + adjustment))

        # If historically under-confident, increase low scores
        if metrics.under_confidence_rate > 0.15:
            if raw_confidence < 0.5:
                adjustment = 0.1 * metrics.under_confidence_rate
                return max(0.0, min(1.0, raw_confidence + adjustment))

        return raw_confidence

    def calculate_calibration(self) -> CalibrationMetrics:
        """Calculate calibration metrics."""
        confidences = np.array([o.confidence_score for o in self.outcomes])
        successes = np.array([1.0 if o.success else 0.0 for o in self.outcomes])

        correlation, p_value = pearsonr(confidences, successes)

        # Over-confidence: high confidence but failed
        high_confidence = [o for o in self.outcomes if o.confidence_score > 0.8]
        over_confident = sum(1 for o in high_confidence if not o.success)
        over_confidence_rate = over_confident / len(high_confidence) if high_confidence else 0.0

        # Under-confidence: low confidence but succeeded
        low_confidence = [o for o in self.outcomes if o.confidence_score < 0.5]
        under_confident = sum(1 for o in low_confidence if o.success)
        under_confidence_rate = under_confident / len(low_confidence) if low_confidence else 0.0

        return CalibrationMetrics(
            correlation=correlation,
            over_confidence_rate=over_confidence_rate,
            under_confidence_rate=under_confidence_rate,
            sample_size=len(self.outcomes),
            p_value=p_value
        )
```

---

## Referencias

1. [ADR-054: Planning Architecture](../../../gobernanza/adr/ADR-054-planning-architecture.md)
2. [RT-013: Planning Performance and Quality Standards](../reglas_tecnicas/RT-013_planning_performance_quality_standards.md)
3. [UC-SYS-006: Planning and Replanning Workflow](../casos_uso/UC-SYS-006_planning_replanning_workflow.md)
4. [RF-011: Task Decomposition and Structured Output](./RF-011_task_decomposition_structured_output.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Total Escenarios**: 20
**Principio Clave**: **Transparencia Inmediata Ante Fallos** - Never hide failures, always communicate immediately with context and recovery strategy
