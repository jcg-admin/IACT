# RT-015: UX Standards (Transparency, Control, Consistency)

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Human-Centric UX
**Relación**:
- Implementa [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
- Relacionado con [RT-012: Multi-Agent Observability](./RT-012_multi_agent_observability.md)

---

## Propósito

Define measurable UX standards for transparency, control, and consistency to ensure agents are trustworthy, respectful of user autonomy, and predictable in behavior.

---

## Transparency Standards

### Standard 1: Plan Disclosure

| Requirement | Standard | Enforcement |
|-------------|----------|-------------|
| Show plan before execution | 100% for high-impact actions | Mandatory approval gate |
| Plan detail level | All subtasks visible | Validation check |
| Confidence disclosure | Always show if < 0.8 | Auto-display |
| Risk disclosure | Show risks with P > 0.2 | Risk analyzer |

**Enforcement Code**:
```python
class TransparencyEnforcer:
    HIGH_IMPACT_ACTIONS = ["book", "purchase", "delete", "send", "publish"]

    def enforce_plan_disclosure(self, plan: Plan, action_type: str):
        """Enforce plan disclosure before execution."""
        # Check if high-impact
        is_high_impact = any(keyword in action_type.lower()
                            for keyword in self.HIGH_IMPACT_ACTIONS)

        if is_high_impact or plan.confidence_score < 0.8:
            # MUST show plan
            self.display_plan(plan)

            # MUST request approval
            if not self.request_user_approval():
                raise UserRejectedPlanError("User rejected plan")

    def display_plan(self, plan: Plan):
        """Display plan with all required transparency."""
        print(f"📋 Plan: {plan.plan_id}")
        print(f"   Confidence: {plan.confidence_score:.0%}")
        print(f"   Estimated time: {plan.estimated_total_duration}s")
        print(f"\n   Steps:")
        for i, task in enumerate(plan.subtasks, 1):
            print(f"   {i}. {task.description}")
            print(f"      Agent: {task.agent_type}")
            print(f"      Priority: {task.priority}/10")

        # Show risks if significant
        risks = self.analyze_risks(plan)
        high_risks = [r for r in risks if r.probability > 0.2]

        if high_risks:
            print(f"\n   ⚠️  Risks:")
            for risk in high_risks:
                print(f"   - {risk.description} (P={risk.probability:.0%})")
```

### Standard 2: Progress Updates

| Requirement | Standard | Enforcement |
|-------------|----------|-------------|
| Update frequency | Every 5s or per subtask | Progress monitor |
| Update content | Current step + % complete | Structured format |
| ETA accuracy | ± 20% of actual | ETA tracker |
| Error reporting | < 500ms from detection | Immediate notification |

**Enforcement Code**:
```python
class ProgressTransparency:
    def execute_with_progress(self, plan: Plan):
        """Execute plan with transparent progress updates."""
        total_tasks = len(plan.subtasks)

        for i, task in enumerate(plan.subtasks, 1):
            # Progress update
            progress = (i / total_tasks) * 100
            eta = self.estimate_remaining_time(plan, i)

            print(f"⏳ Progress: {progress:.0f}% ({i}/{total_tasks})")
            print(f"   Current: {task.description}")
            print(f"   ETA: {eta}s")

            # Execute task
            try:
                result = self.execute_task(task)
                print(f"   ✓ Completed")
            except Exception as e:
                # IMMEDIATE error reporting (< 500ms)
                print(f"   ✗ Error: {str(e)}")
                self.notify_error_immediately(e)
                raise
```

### Standard 3: Explanation Quality

| Requirement | Standard | Measurement |
|-------------|----------|-------------|
| Explain decisions | 100% for user-facing decisions | Mandatory explanation |
| Explanation length | 1-3 sentences | Length validator |
| Use plain language | < 8th grade reading level | Readability score |
| Include reasoning | Show "why" not just "what" | Content check |

**Enforcement Code**:
```python
class ExplanationQuality:
    def explain_decision(self, decision: Decision) -> str:
        """Generate quality explanation for decision."""
        explanation = self._generate_explanation(decision)

        # Validate explanation quality
        self._validate_explanation(explanation)

        return explanation

    def _validate_explanation(self, explanation: str):
        """Validate explanation meets standards."""
        # Length check (1-3 sentences)
        sentences = explanation.split('.')
        if len(sentences) < 1 or len(sentences) > 3:
            raise ExplanationQualityError(
                f"Explanation must be 1-3 sentences, got {len(sentences)}"
            )

        # Reading level check (< 8th grade)
        reading_level = self._calculate_reading_level(explanation)
        if reading_level > 8:
            raise ExplanationQualityError(
                f"Explanation too complex (grade {reading_level}), simplify"
            )

        # Must include reasoning ("because", "since", "due to")
        reasoning_words = ["because", "since", "due to", "as", "so that"]
        if not any(word in explanation.lower() for word in reasoning_words):
            raise ExplanationQualityError(
                "Explanation must include reasoning (why)"
            )
```

---

## Control Standards

### Standard 4: User Approval Gates

| Action Type | Approval Required | Timeout | Default |
|-------------|-------------------|---------|---------|
| High-impact (book, purchase) | Always | 60s | Reject |
| Medium-impact (send, schedule) | If confidence < 0.8 | 30s | Reject |
| Low-impact (search, read) | Never | N/A | Proceed |
| First-time action | Always | 60s | Reject |

**Enforcement Code**:
```python
class ApprovalGateEnforcer:
    def enforce_approval_gate(self, action: Action) -> bool:
        """Enforce approval gate based on action type."""
        approval_config = self._get_approval_config(action)

        if not approval_config.approval_required:
            return True  # No approval needed

        # Request approval with timeout
        try:
            approval = self.request_approval_with_timeout(
                action=action,
                timeout_seconds=approval_config.timeout
            )
            return approval.approved

        except TimeoutError:
            # Timeout - use default
            if approval_config.default_on_timeout == "reject":
                logger.warning(f"Approval timeout for {action.type}, rejecting")
                return False
            else:
                return True

    def _get_approval_config(self, action: Action) -> ApprovalConfig:
        """Get approval configuration for action."""
        if action.type in ["book", "purchase", "delete", "publish"]:
            return ApprovalConfig(
                approval_required=True,
                timeout=60,
                default_on_timeout="reject"
            )
        elif action.confidence < 0.8:
            return ApprovalConfig(
                approval_required=True,
                timeout=30,
                default_on_timeout="reject"
            )
        else:
            return ApprovalConfig(approval_required=False)
```

### Standard 5: Interruption Support

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Allow cancel | 100% of operations | Cancel handler |
| Cancel latency | < 2s | Interrupt signal |
| State preservation | Auto-save on cancel | State manager |
| Resume capability | 100% after cancel | Checkpoint system |

**Enforcement Code**:
```python
import signal
import threading

class InterruptionSupport:
    def __init__(self):
        self.cancel_requested = threading.Event()
        self.checkpoints = []

    def execute_with_interruption_support(self, plan: Plan):
        """Execute plan with interruption support."""
        # Register cancel handler
        signal.signal(signal.SIGINT, self._handle_cancel_signal)

        print("Press Ctrl+C to cancel at any time")

        for i, task in enumerate(plan.subtasks):
            # Check for cancellation before each task
            if self.cancel_requested.is_set():
                print("\n⏸  Execution cancelled by user")
                self._save_checkpoint(plan, i)
                return None

            # Execute task
            result = self.execute_task(task)

            # Save checkpoint after each task
            self._save_checkpoint(plan, i+1)

        return result

    def _handle_cancel_signal(self, signum, frame):
        """Handle cancel signal (Ctrl+C)."""
        print("\n⚠️  Cancel requested...")
        self.cancel_requested.set()

    def _save_checkpoint(self, plan: Plan, completed_count: int):
        """Save checkpoint for resumption."""
        checkpoint = {
            "plan_id": plan.plan_id,
            "completed_tasks": completed_count,
            "timestamp": datetime.now(),
            "state": plan.model_dump()
        }
        self.checkpoints.append(checkpoint)

    def resume_from_checkpoint(self, plan_id: str) -> Optional[Plan]:
        """Resume plan from last checkpoint."""
        checkpoint = self._find_latest_checkpoint(plan_id)
        if not checkpoint:
            return None

        print(f"📍 Resuming from checkpoint ({checkpoint['completed_tasks']} tasks done)")
        return Plan.model_validate(checkpoint['state'])
```

### Standard 6: Preference Management

| Requirement | Standard | Storage |
|-------------|----------|---------|
| Learn from rejections | 100% | Preference DB |
| Apply preferences | > 90% relevance | Auto-apply |
| Allow override | Always | UI control |
| Explain preference source | On request | Audit log |

**Enforcement Code**:
```python
class PreferenceManager:
    def learn_from_rejection(self, action: Action, rejection_reason: str):
        """Learn preference from user rejection."""
        preference = Preference(
            key=f"{action.type}_{action.context}",
            value="avoid",
            reason=rejection_reason,
            strength=0.8,
            learned_at=datetime.now()
        )

        self.save_preference(preference)
        logger.info(f"Learned preference: {preference}")

    def apply_preferences(self, action: Action) -> Action:
        """Apply learned preferences to action."""
        relevant_prefs = self.find_relevant_preferences(action)

        for pref in relevant_prefs:
            if pref.strength > 0.7:  # Only apply strong preferences
                action = self._apply_preference(action, pref)
                print(f"💡 Applied preference: {pref.reason}")

        return action

    def allow_preference_override(self):
        """Allow user to override preferences."""
        print("Current preferences:")
        for pref in self.get_all_preferences():
            print(f"  - {pref.key}: {pref.value} ({pref.reason})")

        print("\nOverride a preference? (yes/no)")
        if input("> ") == "yes":
            pref_key = input("Which preference? ")
            self.delete_preference(pref_key)
            print(f"✓ Preference '{pref_key}' removed")
```

---

## Consistency Standards

### Standard 7: Behavioral Consistency

| Requirement | Standard | Measurement |
|-------------|----------|-------------|
| Same input → same output | > 95% | Consistency score |
| Explain behavioral changes | 100% | Change log |
| Version behavior changes | Always | Semantic versioning |
| Allow rollback | 100% | Behavior snapshots |

**Enforcement Code**:
```python
class ConsistencyEnforcer:
    def __init__(self):
        self.behavior_version = "1.0.0"
        self.behavior_history = []

    def execute_consistently(self, task: Task) -> Result:
        """Execute task consistently based on version."""
        # Compute task signature
        task_signature = self._compute_signature(task)

        # Check if we've seen this before
        previous_result = self._find_previous_result(task_signature)

        if previous_result:
            # Same task seen before
            current_approach = self._select_approach(task)
            previous_approach = previous_result.approach

            if current_approach != previous_approach:
                # Behavior changed - explain why
                self._explain_behavior_change(previous_approach, current_approach)

                print("Use new approach? (yes/no/always)")
                choice = input("> ")

                if choice == "no":
                    return self._execute_with_approach(task, previous_approach)
                elif choice == "always":
                    self._update_behavior_version(current_approach)

        # Execute with current approach
        result = self._execute_with_approach(task, current_approach)

        # Save for future consistency
        self._save_result(task_signature, result, current_approach)

        return result

    def _explain_behavior_change(self, old_approach: str, new_approach: str):
        """Explain why behavior changed."""
        print(f"⚠️  My approach has changed for this type of task:")
        print(f"   Old: {old_approach}")
        print(f"   New: {new_approach}")
        print(f"   Reason: Learned from recent feedback (success rate improved)")

    def _update_behavior_version(self, new_approach: str):
        """Update behavior version (semantic versioning)."""
        major, minor, patch = map(int, self.behavior_version.split('.'))

        # Major change if approach fundamentally different
        if self._is_major_change(new_approach):
            major += 1
            minor = 0
            patch = 0
        else:
            minor += 1
            patch = 0

        new_version = f"{major}.{minor}.{patch}"

        self.behavior_history.append({
            "version": self.behavior_version,
            "approach": self.current_approach,
            "timestamp": datetime.now()
        })

        self.behavior_version = new_version
        print(f"✓ Behavior updated to version {new_version}")
```

### Standard 8: UI Consistency

| Element | Standard | Enforcement |
|---------|----------|-------------|
| Terminology | Same terms for same concepts | Glossary |
| Icons | Same icons for same actions | Style guide |
| Interaction patterns | Consistent flows | Pattern library |
| Response times | ± 20% variance | Performance monitor |

**Enforcement Code**:
```python
class UIConsistencyGuard:
    TERMINOLOGY = {
        "plan": "plan",  # Never "strategy", "approach", "method"
        "cancel": "cancel",  # Never "abort", "stop", "quit"
        "approve": "approve",  # Never "accept", "confirm", "ok"
    }

    def ensure_terminology_consistency(self, message: str) -> str:
        """Ensure message uses consistent terminology."""
        for correct_term, incorrect_variants in self.VARIANT_MAP.items():
            for variant in incorrect_variants:
                if variant in message.lower():
                    message = message.replace(variant, correct_term)
                    logger.warning(
                        f"Fixed terminology: '{variant}' → '{correct_term}'"
                    )

        return message

    def validate_interaction_pattern(self, interaction: Interaction):
        """Validate interaction follows consistent pattern."""
        expected_pattern = self.PATTERN_LIBRARY.get(interaction.type)

        if not expected_pattern:
            raise PatternNotFoundError(f"No pattern for {interaction.type}")

        # Validate steps match expected pattern
        for i, step in enumerate(interaction.steps):
            expected_step = expected_pattern[i]

            if step.type != expected_step.type:
                raise PatternViolationError(
                    f"Step {i}: expected {expected_step.type}, got {step.type}"
                )
```

---

## Measurement and Monitoring

### Dashboard Metrics

```yaml
transparency_metrics:
  - name: "Plan Disclosure Rate"
    query: (plans_disclosed / total_high_impact_actions) * 100
    target: 100%

  - name: "Progress Update Frequency"
    query: avg(time_between_updates)
    target: < 5s

  - name: "Explanation Quality Score"
    query: avg(readability_score)
    target: < 8 (grade level)

control_metrics:
  - name: "Approval Request Rate"
    query: (approval_requests / high_impact_actions) * 100
    target: 100%

  - name: "User Rejection Rate"
    query: (rejections / approval_requests) * 100
    target: < 20%

  - name: "Cancel Support Availability"
    query: (cancelable_operations / total_operations) * 100
    target: 100%

consistency_metrics:
  - name: "Behavioral Consistency Score"
    query: same_input_same_output_rate
    target: > 95%

  - name: "Unexplained Behavior Changes"
    query: behavior_changes_without_explanation
    target: 0

  - name: "UI Terminology Violations"
    query: count(incorrect_terminology_usage)
    target: 0
```

---

## Referencias

1. [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
2. [Microsoft Human-AI Interaction Guidelines](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/)
3. [ISO 9241-110: Ergonomics of human-system interaction](https://www.iso.org/standard/38009.html)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
