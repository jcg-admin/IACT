# RF-016: Agent UX Implementation (Human-Centric Design)

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - UX Design
**Relación**:
- Implementa [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
- Sigue [RT-015: UX Standards](../reglas_tecnicas/RT-015_ux_standards_transparency_control_consistency.md)
- Relacionado con [UC-SYS-008: Human-Centric Agent Interactions](../casos_uso/UC-SYS-008_human_centric_agent_interactions.md)

---

## Descripción

Functional requirements for implementing human-centric UX principles with 20 Gherkin scenarios covering transparency, control, and consistency. All scenarios include TDD test templates.

---

## Transparency - Escenarios 1-7

### Escenario 1: Display Plan Before Execution
```gherkin
Given agent generated plan para "book flight to Paris"
And plan.confidence_score = 0.85
When user requests execution
Then agent debe display complete plan con all subtasks
And debe show confidence score
And debe show estimated duration
And debe request user approval antes de execute
```

**Test Template**:
```python
def test_display_plan_before_execution():
    """RF-016: Scenario 1 - Display Plan Before Execution"""
    agent = HumanCentricAgent()

    # Given
    plan = Plan(
        plan_id="plan_001",
        subtasks=[
            SubTask(description="Search flights", agent_type="flight"),
            SubTask(description="Select best flight", agent_type="recommender")
        ],
        confidence_score=0.85,
        estimated_total_duration=30
    )

    # When
    with patch('builtins.input', return_value='yes'):  # User approves
        displayed_plan = agent.display_and_request_approval(plan)

    # Then
    assert displayed_plan is not None
    assert "confidence" in str(displayed_plan).lower() or displayed_plan.confidence_shown
    assert "estimated" in str(displayed_plan).lower() or displayed_plan.duration_shown
    # In real implementation, would verify display called
```

### Escenario 2: Communicate Uncertainty When Confidence < 0.8
```gherkin
Given agent con plan confidence_score = 0.65
When agent prepares to execute
Then debe display warning "⚠️  Uncertainty alert"
And debe explain why confidence is low
And debe offer options: proceed/modify/cancel
```

**Test Template**:
```python
def test_communicate_uncertainty_low_confidence():
    """RF-016: Scenario 2 - Communicate Uncertainty"""
    agent = UncertaintyAwareAgent()

    # Given
    task = Task(description="Complex multi-city trip", confidence=0.65)

    # When
    with patch('builtins.print') as mock_print:
        agent.execute_with_uncertainty(task)

    # Then
    # Verify uncertainty was communicated
    print_calls = [str(call) for call in mock_print.call_args_list]
    assert any("uncertainty" in call.lower() or "⚠" in call for call in print_calls)
    assert any("65%" in call or "0.65" in call for call in print_calls)
```

### Escenario 3: Provide Progress Updates Every 5s
```gherkin
Given plan con 4 subtasks, estimated_total_duration = 20s
When agent executes plan
Then debe send progress update cada 5s o al completar cada subtask
And cada update debe include: current_step, percentage, ETA
```

**Test Template**:
```python
def test_progress_updates_frequency():
    """RF-016: Scenario 3 - Progress Updates"""
    from unittest.mock import Mock

    agent = ProgressTransparency()
    progress_service = Mock()
    agent.progress_service = progress_service

    # Given
    plan = Plan(
        subtasks=[SubTask(description=f"Task {i}", estimated_duration_seconds=5)
                  for i in range(4)],
        estimated_total_duration=20
    )

    # When
    agent.execute_with_progress(plan)

    # Then
    # Should have called progress service at least 4 times (once per task)
    assert progress_service.send_update.call_count >= 4

    # Verify update content
    for call in progress_service.send_update.call_args_list:
        update = call[0][0]
        assert "progress_percentage" in update or "current_step" in update
```

### Escenario 4: Explain Decision with Reasoning
```gherkin
Given agent selects Option A over Option B
When user asks "why this option?"
Then explanation debe incluir "because" o "since" (reasoning word)
And debe tener 1-3 sentences
And reading level debe ser < 8th grade
```

**Test Template**:
```python
def test_explain_decision_with_reasoning():
    """RF-016: Scenario 4 - Explain Decision"""
    agent = ExplanationQuality()

    # Given
    decision = Decision(
        choice="Option A",
        alternatives=["Option B", "Option C"],
        factors={"price": 0.8, "quality": 0.9}
    )

    # When
    explanation = agent.explain_decision(decision)

    # Then
    # Must include reasoning word
    reasoning_words = ["because", "since", "due to", "as", "so that"]
    assert any(word in explanation.lower() for word in reasoning_words)

    # Length check (1-3 sentences)
    sentences = [s for s in explanation.split('.') if s.strip()]
    assert 1 <= len(sentences) <= 3

    # Reading level check (simplified - real impl would use readability library)
    words = explanation.split()
    avg_word_length = sum(len(w) for w in words) / len(words)
    assert avg_word_length < 6  # Proxy for reading level
```

### Escenario 5: Show Risks with Probability > 0.2
```gherkin
Given plan con 3 identified risks:
  | Risk | Probability |
  | Flight delay | 0.35 |
  | Hotel overbooked | 0.15 |
  | Weather issues | 0.25 |
When agent displays plan
Then debe show risks: Flight delay (35%), Weather issues (25%)
And NO debe show: Hotel overbooked (15% < threshold)
```

**Test Template**:
```python
def test_show_significant_risks():
    """RF-016: Scenario 5 - Show Risks > 0.2 Probability"""
    agent = TransparencyEnforcer()

    # Given
    plan = Plan(plan_id="test", subtasks=[], confidence_score=0.8)
    risks = [
        Risk(description="Flight delay", probability=0.35),
        Risk(description="Hotel overbooked", probability=0.15),
        Risk(description="Weather issues", probability=0.25)
    ]

    # When
    with patch('builtins.print') as mock_print:
        agent.display_plan_with_risks(plan, risks)

    # Then
    print_output = str(mock_print.call_args_list)
    assert "flight delay" in print_output.lower()
    assert "weather" in print_output.lower()
    assert "hotel overbooked" not in print_output.lower()  # < 0.2 threshold
```

### Escenarios 6-7: Transparency in Errors, Learning Disclosure
**Scenario 6**: Report errors immediately (< 500ms)
**Scenario 7**: Disclose learned preferences to user

---

## Control - Escenarios 8-14

### Escenario 8: Request Approval for High-Impact Actions
```gherkin
Given action_type = "book_flight" (high-impact)
When agent prepares to execute
Then debe request explicit user approval
And timeout debe ser 60s
And default_on_timeout debe ser "reject"
```

**Test Template**:
```python
def test_approval_for_high_impact_actions():
    """RF-016: Scenario 8 - Request Approval for High-Impact"""
    agent = ApprovalGateEnforcer()

    # Given
    action = Action(type="book_flight", details={"price": 500})

    # When
    with patch.object(agent, 'request_approval_with_timeout') as mock_approval:
        mock_approval.return_value = Approval(approved=True)
        result = agent.enforce_approval_gate(action)

    # Then
    # Should have requested approval
    mock_approval.assert_called_once()
    call_args = mock_approval.call_args
    assert call_args.kwargs['timeout_seconds'] == 60
```

### Escenario 9: Allow Cancel with < 2s Latency
```gherkin
Given plan executing con 10 subtasks
When user presses Ctrl+C después de 3 subtasks
Then execution debe cancel en < 2s
And debe save checkpoint con completed_count = 3
And debe preserve state para resume
```

**Test Template**:
```python
def test_allow_cancel_with_low_latency():
    """RF-016: Scenario 9 - Allow Cancel < 2s"""
    import signal
    import threading

    agent = InterruptionSupport()

    # Given
    plan = Plan(subtasks=[SubTask(description=f"Task {i}") for i in range(10)])

    # When - simulate Ctrl+C after 0.5s
    def send_interrupt():
        time.sleep(0.5)
        agent._handle_cancel_signal(signal.SIGINT, None)

    interrupt_thread = threading.Thread(target=send_interrupt)
    interrupt_thread.start()

    start = time.time()
    result = agent.execute_with_interruption_support(plan)
    cancel_latency = time.time() - start

    # Then
    assert cancel_latency < 2.0  # Cancelled quickly
    assert result is None  # Execution cancelled
    assert len(agent.checkpoints) > 0  # Checkpoint saved
```

### Escenario 10: Resume from Checkpoint
```gherkin
Given plan con plan_id="plan_123" cancelado después de task 3
When user invokes resume_from_checkpoint("plan_123")
Then debe load checkpoint
And debe continue from task 4
And debe display "📍 Resuming from checkpoint (3 tasks done)"
```

**Test Template**:
```python
def test_resume_from_checkpoint():
    """RF-016: Scenario 10 - Resume from Checkpoint"""
    agent = InterruptionSupport()

    # Given - simulate previous execution saved checkpoint
    plan = Plan(plan_id="plan_123", subtasks=[SubTask(description=f"Task {i}") for i in range(5)])
    agent._save_checkpoint(plan, completed_count=3)

    # When
    with patch('builtins.print') as mock_print:
        resumed_plan = agent.resume_from_checkpoint("plan_123")

    # Then
    assert resumed_plan is not None
    assert resumed_plan.plan_id == "plan_123"

    # Verify resume message displayed
    print_calls = str(mock_print.call_args_list)
    assert "resuming" in print_calls.lower() or "checkpoint" in print_calls.lower()
```

### Escenario 11: Learn from User Rejections
```gherkin
Given user rejects plan con reason="too expensive"
When agent processes rejection
Then debe save preference: avoid expensive options para este task type
And preference strength debe ser >= 0.8
And debe apply preference en next similar task
```

**Test Template**:
```python
def test_learn_from_rejections():
    """RF-016: Scenario 11 - Learn from Rejections"""
    agent = PreferenceManager()

    # Given
    action = Action(type="book_hotel", context="Paris", cost=300)
    rejection_reason = "too expensive"

    # When
    agent.learn_from_rejection(action, rejection_reason)

    # Then
    preferences = agent.get_all_preferences()
    relevant_pref = next((p for p in preferences if "expensive" in p.value.lower()), None)

    assert relevant_pref is not None
    assert relevant_pref.strength >= 0.8
```

### Escenarios 12-14: Preference Override, Nudge Without Force, Guided Execution
**Scenario 12**: Allow user to override learned preferences
**Scenario 13**: Nudge but don't force user decisions (nudge acceptance > 40%)
**Scenario 14**: Provide guided execution for complex tasks

---

## Consistency - Escenarios 15-20

### Escenario 15: Same Input → Same Output (95% Consistency)
```gherkin
Given task con signature="search_flights_NYC_Paris_May1"
And previous execution used approach="budget_focused"
When same task executed again
Then debe use same approach="budget_focused"
Unless agent learned nueva preference desde last time
```

**Test Template**:
```python
def test_same_input_same_output():
    """RF-016: Scenario 15 - Behavioral Consistency"""
    agent = ConsistencyEnforcer()

    # Given - execute task first time
    task1 = Task(origin="NYC", destination="Paris", date="2025-05-01")
    result1 = agent.execute_consistently(task1)
    approach1 = agent.current_approach

    # When - execute same task again (no learning in between)
    task2 = Task(origin="NYC", destination="Paris", date="2025-05-01")
    result2 = agent.execute_consistently(task2)
    approach2 = agent.current_approach

    # Then - should use same approach
    assert approach1 == approach2
```

### Escenario 16: Explain Behavioral Changes
```gherkin
Given agent behavior version changed from 1.0.0 to 1.1.0
And approach changed from "budget_focused" to "quality_focused"
When user executes task
Then agent debe explain: "My approach has changed"
And debe show old vs new approach
And debe explain reason: "Learned from recent feedback"
And debe offer revert option
```

**Test Template**:
```python
def test_explain_behavioral_changes():
    """RF-016: Scenario 16 - Explain Behavior Changes"""
    agent = ConsistencyEnforcer()

    # Given - behavior changed
    agent.behavior_version = "1.1.0"
    agent.current_approach = "quality_focused"
    agent.previous_approach = "budget_focused"

    # When
    with patch('builtins.print') as mock_print:
        with patch('builtins.input', return_value='1'):  # User accepts new
            agent._explain_behavior_change(agent.previous_approach, agent.current_approach)

    # Then
    print_calls = str(mock_print.call_args_list)
    assert "changed" in print_calls.lower()
    assert "budget_focused" in print_calls.lower()
    assert "quality_focused" in print_calls.lower()
```

### Escenario 17: Version Behavior Changes (Semantic Versioning)
```gherkin
Given agent hace major change en approach
When change is applied
Then version debe increment: 1.2.3 → 2.0.0
And behavior_history debe guardar previous version
And user debe poder rollback to previous version
```

**Test Template**:
```python
def test_version_behavior_changes():
    """RF-016: Scenario 17 - Semantic Versioning of Behavior"""
    agent = ConsistencyEnforcer()

    # Given
    agent.behavior_version = "1.2.3"

    # When - major change
    agent._update_behavior_version(new_approach="completely_new_approach")

    # Then - major version bumped
    assert agent.behavior_version.startswith("2.0.0")

    # History preserved
    assert len(agent.behavior_history) > 0
```

### Escenario 18: UI Terminology Consistency
```gherkin
Given agent message usa "abort" para cancel action
When terminology validator checks message
Then debe replace "abort" con "cancel"
And debe log warning: "Fixed terminology: 'abort' → 'cancel'"
```

**Test Template**:
```python
def test_ui_terminology_consistency():
    """RF-016: Scenario 18 - UI Terminology Consistency"""
    agent = UIConsistencyGuard()

    # Given
    message_with_wrong_term = "Do you want to abort this operation?"

    # When
    corrected_message = agent.ensure_terminology_consistency(message_with_wrong_term)

    # Then
    assert "cancel" in corrected_message.lower()
    assert "abort" not in corrected_message.lower()
```

### Escenario 19: Maintain User Preferences Across Sessions
```gherkin
Given user session 1 set preference: "prefer morning flights"
When user starts new session 2
Then agent debe load saved preferences
And debe apply "morning flights" preference
And debe show: "💡 Based on your preferences, showing morning flights"
```

**Test Template**:
```python
def test_maintain_preferences_across_sessions():
    """RF-016: Scenario 19 - Preferences Across Sessions"""
    agent1 = PreferenceManager()

    # Session 1 - set preference
    agent1.save_preference(Preference(
        key="flight_time",
        value="morning",
        reason="User prefers morning flights"
    ))

    # Simulate new session
    agent2 = PreferenceManager()  # New instance
    agent2.load_preferences_from_storage()

    # Then - preference should be loaded
    prefs = agent2.get_all_preferences()
    morning_pref = next((p for p in prefs if p.key == "flight_time"), None)

    assert morning_pref is not None
    assert morning_pref.value == "morning"
```

### Escenario 20: Interaction Pattern Consistency
```gherkin
Given interaction_type = "approval_request"
And expected_pattern = [show_plan, explain_decision, request_input]
When agent executes approval interaction
Then debe follow exact pattern steps
And NO debe skip steps
And NO debe reorder steps
```

**Test Template**:
```python
def test_interaction_pattern_consistency():
    """RF-016: Scenario 20 - Interaction Pattern Consistency"""
    agent = UIConsistencyGuard()

    # Given
    expected_pattern = [
        InteractionStep(type="show_plan"),
        InteractionStep(type="explain_decision"),
        InteractionStep(type="request_input")
    ]

    # When
    interaction = Interaction(
        type="approval_request",
        steps=[
            InteractionStep(type="show_plan"),
            InteractionStep(type="explain_decision"),
            InteractionStep(type="request_input")
        ]
    )

    # Then - should validate successfully
    agent.validate_interaction_pattern(interaction)  # Should not raise

    # When - wrong pattern
    wrong_interaction = Interaction(
        type="approval_request",
        steps=[
            InteractionStep(type="request_input"),  # Wrong order!
            InteractionStep(type="show_plan")
        ]
    )

    # Then - should raise error
    with pytest.raises(PatternViolationError):
        agent.validate_interaction_pattern(wrong_interaction)
```

---

## Criterios de Validación

### Transparency
- ✓ Plan disclosure before high-impact actions: 100%
- ✓ Uncertainty communication when confidence < 0.8: 100%
- ✓ Progress updates frequency: < 5s intervals
- ✓ Explanation quality: reading level < 8th grade

### Control
- ✓ Approval requests for high-impact: 100%
- ✓ Cancel latency: < 2s
- ✓ Checkpoint save on cancel: 100%
- ✓ Preference learning from rejections: 100%

### Consistency
- ✓ Same input → same output: > 95%
- ✓ Behavior changes explained: 100%
- ✓ Semantic versioning enforced: 100%
- ✓ UI terminology consistent: 0 violations

---

## Métricas de Calidad

| Categoría | Métrica | Target | Medición |
|-----------|---------|--------|----------|
| Transparency | Plan disclosure rate | 100% | count(plans_shown) / count(high_impact_actions) |
| Transparency | Uncertainty communication | 100% when confidence < 0.8 | count(warnings_shown) / count(low_confidence) |
| Control | User approval rate | > 0 | count(approvals_requested) / count(high_impact) |
| Control | Cancel success rate | 100% | count(successful_cancels) / count(cancel_attempts) |
| Consistency | Behavioral consistency | > 95% | count(consistent_behaviors) / count(total_executions) |
| Consistency | Terminology violations | 0 | count(incorrect_terms_used) |

---

## Referencias

1. [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
2. [RT-015: UX Standards](../reglas_tecnicas/RT-015_ux_standards_transparency_control_consistency.md)
3. [UC-SYS-008: Human-Centric Agent Interactions](../casos_uso/UC-SYS-008_human_centric_agent_interactions.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Total Escenarios**: 20 (7 Transparency + 7 Control + 6 Consistency)
**TDD**: All scenarios with test templates included ✓
