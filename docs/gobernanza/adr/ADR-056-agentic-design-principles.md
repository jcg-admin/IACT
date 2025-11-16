# ADR-056: AI Agentic Design Principles

**Estado**: Aceptado
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Human-Centric UX Design
**Relación**:
- Complementa [ADR-054: Planning Architecture](./ADR-054-planning-architecture.md)
- Complementa [ADR-055: Agent Protocols](./ADR-055-agent-protocols-architecture.md)
- Implementado en [RF-016](../ai/requisitos/funcionales/RF-016_agent_ux_implementation.md)

---

## Contexto

AI agents must be designed with humans at the center. Without human-centric design principles:

- **Poor trust**: Users don't trust opaque agent decisions
- **Loss of control**: Users feel helpless when agents act autonomously
- **Inconsistent experience**: Unpredictable behavior leads to frustration
- **Reduced adoption**: Users abandon agents that don't respect their needs
- **Ethical issues**: Agents that don't consider human values cause harm

**Real-world example**: A scheduling agent that silently books meetings without user approval destroys trust, even if 95% of bookings are correct. The 5% errors are catastrophic.

We need design principles that ensure agents:
1. **Connect, don't collapse** user workflows
2. **Are accessible yet invisible** when working well
3. **Reflect, nudge, adapt** across past/present/future
4. **Embrace uncertainty** and communicate it
5. **Establish trust** through transparency and consistency

---

## Decisión

We adopt **Human-Centric Agentic Design Principles** organized in three dimensions:

### 1. Agent Space: How Agents Fit into User Environments

#### Principle 1.1: Connecting, Not Collapsing

**Problem**: Traditional automation collapses complex workflows into black boxes, removing user agency.

**Principle**: Agents should connect workflows, making them more efficient while preserving user control at key decision points.

**Implementation**:
```python
class ConnectingAgent:
    """Agent that connects workflows, doesn't collapse them."""

    def execute_task(self, task: Task, user_approval_required: bool = True):
        """
        Execute task with connection points for user involvement.

        Args:
            task: Task to execute
            user_approval_required: Whether to request approval before execution

        Returns:
            Task result
        """
        # 1. Show what agent will do (transparency)
        plan = self.generate_plan(task)
        self.display_plan_to_user(plan)

        # 2. Request approval at key decision points (control)
        if user_approval_required:
            approval = self.request_user_approval(plan)
            if not approval.approved:
                return self.handle_rejection(approval.feedback)

        # 3. Execute with progress updates (visibility)
        result = self.execute_with_updates(plan)

        # 4. Allow user to intervene during execution (agency)
        if self.user_wants_to_intervene():
            return self.handle_intervention()

        return result

    def display_plan_to_user(self, plan: Plan):
        """Show user what agent will do before doing it."""
        print(f"I'm going to:")
        for step in plan.subtasks:
            print(f"  {step.priority}. {step.description}")
        print(f"\nEstimated time: {plan.estimated_total_duration}s")
        print(f"Confidence: {plan.confidence_score:.0%}")

    def request_user_approval(self, plan: Plan) -> UserApproval:
        """Request user approval before execution."""
        print(f"\nProceed with this plan? (yes/no/modify)")
        user_input = input("> ")

        if user_input.lower() == "yes":
            return UserApproval(approved=True)
        elif user_input.lower() == "modify":
            modifications = self.get_user_modifications()
            return UserApproval(approved=True, modifications=modifications)
        else:
            feedback = input("What would you like to change? ")
            return UserApproval(approved=False, feedback=feedback)
```

**Anti-pattern**: Silent execution without showing plan
```python
# BAD: Collapses workflow, no user visibility
def bad_execute_task(task):
    plan = generate_plan(task)
    result = execute(plan)  # User has no idea what happened
    return result
```

**Good pattern**: Connect user to each step
```python
# GOOD: User sees and approves plan
def good_execute_task(task):
    plan = generate_plan(task)
    display_plan_to_user(plan)  # Transparency
    if request_approval(plan):  # Control
        result = execute_with_updates(plan)  # Visibility
        return result
```

#### Principle 1.2: Accessible Yet Invisible

**Problem**: Agents are either too prominent (annoying) or too hidden (undiscoverable).

**Principle**: Agents should be easy to access when needed but stay invisible when working well.

**Implementation**:
```python
class AccessibleYetInvisibleAgent:
    """Agent that appears when needed, disappears when not."""

    def __init__(self):
        self.visibility_mode = "invisible"  # Start invisible
        self.last_interaction = None

    def should_surface(self, context: Dict) -> bool:
        """
        Determine if agent should surface to user.

        Surface when:
        - User explicitly invokes agent
        - Agent detects opportunity to help
        - Agent needs user input
        - Error occurred that requires user attention

        Stay invisible when:
        - Task executing successfully
        - No user action needed
        """
        # Explicit invocation
        if context.get("user_invoked"):
            return True

        # Proactive help (but not annoying)
        if self._should_offer_help(context):
            return True

        # Error requires attention
        if context.get("error_severity") == "high":
            return True

        # Need user input
        if context.get("needs_user_input"):
            return True

        # Otherwise, stay invisible
        return False

    def _should_offer_help(self, context: Dict) -> bool:
        """Decide if agent should proactively offer help."""
        # Only offer help if:
        # 1. High confidence can help (> 0.8)
        # 2. Significant value (save > 5 minutes)
        # 3. Not offered recently (> 1 hour ago)

        if context.get("confidence") < 0.8:
            return False

        if context.get("estimated_time_saved") < 300:  # < 5 min
            return False

        if self.last_interaction:
            time_since = (datetime.now() - self.last_interaction).total_seconds()
            if time_since < 3600:  # < 1 hour
                return False

        return True

    def execute_invisibly(self, task: Task):
        """Execute task invisibly (no UI except errors)."""
        try:
            result = self.execute(task)

            # Only show notification if significant
            if result.impact_score > 0.7:
                self.show_subtle_notification(
                    f"✓ Completed: {task.description}",
                    duration_seconds=3
                )

            return result

        except Exception as e:
            # Surface on error
            self.visibility_mode = "visible"
            self.show_error_dialog(e)
            raise

    def show_subtle_notification(self, message: str, duration_seconds: int):
        """Show non-intrusive notification."""
        # Small toast in corner, auto-dismiss
        print(f"[Agent] {message}")
        # In real app: Toast notification that fades after duration
```

**Anti-pattern**: Always visible (annoying)
```python
# BAD: Clippy syndrome - always in your face
def bad_agent():
    while True:
        print("Hi! Do you need help?")  # Every 5 seconds
        time.sleep(5)
```

**Good pattern**: Invisible until needed
```python
# GOOD: Appears only when valuable
def good_agent(context):
    if should_surface(context):
        offer_help()
    else:
        work_silently_in_background()
```

---

### 2. Agent Time: How Agents Relate to Past, Present, Future

#### Principle 2.1: Reflecting (Past)

**Problem**: Agents don't learn from past interactions, repeating mistakes.

**Principle**: Agents should reflect on past interactions and adapt behavior based on learnings.

**Implementation**:
```python
class ReflectingAgent:
    """Agent that learns from past interactions."""

    def __init__(self):
        self.interaction_history: List[Interaction] = []
        self.learned_preferences: Dict[str, Any] = {}

    def reflect_on_interaction(self, interaction: Interaction):
        """
        Reflect on completed interaction to extract learnings.

        Args:
            interaction: Completed interaction with user
        """
        # Store interaction
        self.interaction_history.append(interaction)

        # Extract learnings
        learnings = self._extract_learnings(interaction)

        # Update preferences
        for learning in learnings:
            self._apply_learning(learning)

        # Log reflection
        logger.info(f"Reflected on {interaction.id}: {len(learnings)} learnings")

    def _extract_learnings(self, interaction: Interaction) -> List[Learning]:
        """Extract learnings from interaction."""
        learnings = []

        # Learning 1: User preferences
        if interaction.user_feedback:
            if interaction.user_feedback.rating >= 4:
                # User liked this approach
                learnings.append(Learning(
                    type="preference",
                    key=interaction.task_type,
                    value=interaction.approach_used,
                    confidence=0.8
                ))
            elif interaction.user_feedback.rating <= 2:
                # User disliked this approach
                learnings.append(Learning(
                    type="anti_preference",
                    key=interaction.task_type,
                    value=interaction.approach_used,
                    confidence=0.8
                ))

        # Learning 2: Error patterns
        if interaction.errors:
            learnings.append(Learning(
                type="error_pattern",
                key=interaction.context,
                value=interaction.errors,
                confidence=0.9
            ))

        # Learning 3: Timing preferences
        if interaction.user_interrupted:
            learnings.append(Learning(
                type="timing",
                key="avoid_time",
                value=interaction.timestamp.hour,
                confidence=0.6
            ))

        return learnings

    def _apply_learning(self, learning: Learning):
        """Apply learning to agent behavior."""
        if learning.type == "preference":
            self.learned_preferences[learning.key] = learning.value
        elif learning.type == "anti_preference":
            # Avoid this approach in future
            self.learned_preferences[f"avoid_{learning.key}"] = learning.value

    def apply_past_learnings(self, task: Task) -> Task:
        """Apply past learnings to current task."""
        # Check if we've learned preferences for this task type
        if task.task_type in self.learned_preferences:
            preferred_approach = self.learned_preferences[task.task_type]
            task.preferred_approach = preferred_approach

            print(f"💡 Based on past interactions, using {preferred_approach}")

        return task

# Example usage
agent = ReflectingAgent()

# Interaction 1: User likes detailed plans
interaction1 = Interaction(
    task_type="travel_planning",
    approach_used="detailed_plan_with_alternatives",
    user_feedback=Feedback(rating=5, comment="Love the detail!")
)
agent.reflect_on_interaction(interaction1)

# Interaction 2: Same task type
task2 = Task(task_type="travel_planning", description="Plan trip to Tokyo")
task2 = agent.apply_past_learnings(task2)
# Output: "💡 Based on past interactions, using detailed_plan_with_alternatives"
```

#### Principle 2.2: Nudging (Present)

**Problem**: Agents either don't intervene (passive) or take over completely (aggressive).

**Principle**: Agents should nudge users towards good decisions while respecting autonomy.

**Implementation**:
```python
class NudgingAgent:
    """Agent that nudges users, doesn't force."""

    def nudge(self, context: Dict) -> Optional[Nudge]:
        """
        Generate nudge based on context.

        Nudge when:
        - User about to make suboptimal decision (confidence > 0.8)
        - Alternative is significantly better (> 20% improvement)
        - Nudge is actionable (user can easily act on it)

        Don't nudge when:
        - Low confidence (< 0.6)
        - Marginal improvement (< 10%)
        - User explicitly ignoring nudges
        """
        # Detect opportunity
        opportunity = self._detect_opportunity(context)

        if not opportunity:
            return None

        # Only nudge if confident and valuable
        if opportunity.confidence < 0.8:
            return None

        if opportunity.improvement < 0.2:  # < 20% improvement
            return None

        # Check nudge fatigue
        if self._user_has_nudge_fatigue():
            return None

        # Generate nudge
        nudge = Nudge(
            type="suggestion",
            message=self._generate_nudge_message(opportunity),
            action=opportunity.recommended_action,
            dismissible=True,  # User can always dismiss
            priority="low"  # Nudges are low priority
        )

        return nudge

    def _generate_nudge_message(self, opportunity: Opportunity) -> str:
        """Generate user-friendly nudge message."""
        # Good nudge: Specific, actionable, value-focused
        return (
            f"💡 Suggestion: {opportunity.recommended_action}\n"
            f"   Why: {opportunity.reason}\n"
            f"   Benefit: {opportunity.benefit}"
        )

# Example
agent = NudgingAgent()

context = {
    "user_action": "book_expensive_flight",
    "cheaper_alternative_available": True,
    "price_difference": 150,  # $150 cheaper
    "same_airline": True
}

nudge = agent.nudge(context)
if nudge:
    print(nudge.message)
    # Output:
    # "💡 Suggestion: Book the 2pm flight instead of 10am
    #    Why: Same airline, same duration
    #    Benefit: Save $150"
```

**Anti-pattern**: Forcing user
```python
# BAD: Takes over user decision
def bad_nudge():
    print("I'm booking the cheaper flight for you.")
    book_flight(cheaper_flight)  # No user consent
```

**Good pattern**: Suggesting with context
```python
# GOOD: Suggests but lets user decide
def good_nudge():
    print("💡 There's a cheaper flight ($150 less) at 2pm. Want to see it?")
    if user_accepts():
        show_alternative()
```

#### Principle 2.3: Adapting (Future)

**Problem**: Agents use static approaches that don't evolve with user needs.

**Principle**: Agents should adapt their behavior based on changing context and user evolution.

**Implementation**:
```python
class AdaptingAgent:
    """Agent that adapts to changing user needs."""

    def __init__(self):
        self.user_profile = UserProfile()
        self.adaptation_history: List[Adaptation] = []

    def detect_user_evolution(self) -> List[EvolutionSignal]:
        """Detect signals that user needs are evolving."""
        signals = []

        # Signal 1: Changing interaction patterns
        recent_interactions = self.interaction_history[-10:]
        older_interactions = self.interaction_history[-30:-10]

        if self._interaction_pattern_changed(recent_interactions, older_interactions):
            signals.append(EvolutionSignal(
                type="interaction_pattern_change",
                confidence=0.8,
                description="User interaction patterns have shifted"
            ))

        # Signal 2: Explicit feedback change
        recent_ratings = [i.rating for i in recent_interactions if i.rating]
        if recent_ratings and sum(recent_ratings) / len(recent_ratings) < 3.0:
            signals.append(EvolutionSignal(
                type="satisfaction_decline",
                confidence=0.9,
                description="User satisfaction declining"
            ))

        # Signal 3: New task types
        recent_tasks = {i.task_type for i in recent_interactions}
        older_tasks = {i.task_type for i in older_interactions}

        new_tasks = recent_tasks - older_tasks
        if new_tasks:
            signals.append(EvolutionSignal(
                type="new_task_types",
                confidence=0.7,
                description=f"User exploring new tasks: {new_tasks}"
            ))

        return signals

    def adapt_to_evolution(self, signals: List[EvolutionSignal]):
        """Adapt agent behavior based on evolution signals."""
        for signal in signals:
            if signal.type == "satisfaction_decline":
                # User unhappy - adapt approach
                print("📊 I notice you've been less satisfied lately.")
                print("   Would you like me to adjust my approach?")

                if self._user_confirms():
                    new_approach = self._negotiate_new_approach()
                    self._apply_new_approach(new_approach)

            elif signal.type == "new_task_types":
                # User exploring new areas - offer training
                print(f"💡 I see you're trying {signal.description}")
                print("   Want me to learn more about this to help better?")

                if self._user_confirms():
                    self._enhance_capabilities(signal.new_tasks)

    def _negotiate_new_approach(self) -> str:
        """Collaboratively determine new approach with user."""
        print("What would you like me to change?")
        print("  1. More detailed planning")
        print("  2. Faster decisions (less asking)")
        print("  3. More conservative (ask before everything)")

        choice = input("> ")

        approach_map = {
            "1": "detailed_planner",
            "2": "autonomous_executor",
            "3": "conservative_assistant"
        }

        return approach_map.get(choice, "balanced")

# Example
agent = AdaptingAgent()

# Detect user evolution
signals = agent.detect_user_evolution()

if signals:
    agent.adapt_to_evolution(signals)
    # Output: "📊 I notice you've been less satisfied lately.
    #          Would you like me to adjust my approach?"
```

---

### 3. Agent Core: Fundamental Behaviors

#### Principle 3.1: Embrace Uncertainty

**Problem**: Agents pretend to be certain when they're not, leading to overconfidence errors.

**Principle**: Agents should communicate uncertainty honestly and adjust behavior accordingly.

**Implementation**:
```python
class UncertaintyAwareAgent:
    """Agent that embraces and communicates uncertainty."""

    def execute_with_uncertainty(self, task: Task):
        """Execute task while being honest about uncertainty."""
        # Estimate confidence
        confidence = self.estimate_confidence(task)

        # Communicate uncertainty to user
        self._communicate_uncertainty(task, confidence)

        # Adjust behavior based on confidence
        if confidence > 0.9:
            # High confidence - execute autonomously
            return self.execute_autonomously(task)

        elif confidence > 0.7:
            # Medium confidence - show plan, quick approval
            plan = self.generate_plan(task)
            print(f"Here's my plan (I'm {confidence:.0%} confident):")
            self.display_plan(plan)

            if self.quick_approval():
                return self.execute(plan)

        elif confidence > 0.5:
            # Low confidence - detailed review required
            print(f"⚠️  I'm only {confidence:.0%} confident about this.")
            print("   Let me show you my reasoning...")

            plan = self.generate_plan(task)
            self.explain_reasoning(plan)

            if self.detailed_approval():
                return self.execute(plan)

        else:
            # Very low confidence - ask for help
            print(f"🤔 I'm not confident I can do this well ({confidence:.0%} confidence).")
            print("   Options:")
            print("   1. Let me try anyway (you'll review)")
            print("   2. Guide me through it")
            print("   3. Skip this task")

            choice = input("> ")

            if choice == "1":
                return self.execute_with_review(task)
            elif choice == "2":
                return self.execute_with_guidance(task)
            else:
                return None

    def _communicate_uncertainty(self, task: Task, confidence: float):
        """Communicate uncertainty honestly to user."""
        if confidence < 0.7:
            print(f"⚠️  Uncertainty alert:")
            print(f"   Task: {task.description}")
            print(f"   My confidence: {confidence:.0%}")

            reasons = self._explain_low_confidence(task)
            print(f"   Why uncertain:")
            for reason in reasons:
                print(f"     - {reason}")

    def _explain_low_confidence(self, task: Task) -> List[str]:
        """Explain why confidence is low."""
        reasons = []

        # Check for uncertainty sources
        if task.task_type not in self.learned_preferences:
            reasons.append("I haven't done this type of task before")

        if task.has_ambiguous_requirements:
            reasons.append("Some requirements are unclear")

        if task.dependencies_uncertain:
            reasons.append("Some dependencies might not be available")

        return reasons

# Example
agent = UncertaintyAwareAgent()

# High confidence task
task1 = Task(description="Book flight to Paris", confidence=0.95)
agent.execute_with_uncertainty(task1)
# Output: Executes autonomously (high confidence)

# Low confidence task
task2 = Task(description="Organize complex multi-city trip", confidence=0.55)
agent.execute_with_uncertainty(task2)
# Output: "⚠️  I'm only 55% confident about this.
#          Let me show you my reasoning..."
```

#### Principle 3.2: Establish Trust

**Problem**: Users don't trust agents because they don't understand how they work.

**Principle**: Agents should build trust through transparency, consistency, and explainability.

**Implementation**:
```python
class TrustworthyAgent:
    """Agent designed to establish and maintain trust."""

    def execute_transparently(self, task: Task):
        """Execute with full transparency."""
        # 1. Explain what you'll do
        print(f"📋 Task: {task.description}")
        print(f"   How I'll do it:")

        plan = self.generate_plan(task)
        for i, step in enumerate(plan.subtasks, 1):
            print(f"   {i}. {step.description} (agent: {step.agent_type})")

        # 2. Explain why this approach
        print(f"\n   Why this approach:")
        print(f"   - {self.explain_approach_rationale(plan)}")

        # 3. Show what could go wrong
        risks = self.identify_risks(plan)
        if risks:
            print(f"\n   ⚠️  Potential risks:")
            for risk in risks:
                print(f"   - {risk.description} (probability: {risk.probability:.0%})")

        # 4. Request approval
        if not self.request_approval():
            return None

        # 5. Execute with progress updates
        print(f"\n🚀 Executing...")
        for step in plan.subtasks:
            print(f"   ⏳ {step.description}...")
            result = self.execute_step(step)
            print(f"   ✓ {step.description} - Done")

        # 6. Explain results
        print(f"\n✅ Completed")
        self.explain_results(plan)

    def explain_approach_rationale(self, plan: Plan) -> str:
        """Explain why this approach was chosen."""
        return (
            f"Based on {len(self.interaction_history)} similar tasks, "
            f"this approach has {plan.confidence_score:.0%} success rate"
        )

    def maintain_consistency(self):
        """Ensure consistent behavior across interactions."""
        # Consistency principle: Same task + same context = same approach

        if not self.is_behavior_consistent():
            print("⚠️  Warning: My behavior has changed")
            print("   Reason: I learned from recent feedback")
            print("   Old approach: {self.previous_approach}")
            print("   New approach: {self.current_approach}")
            print("   Want to revert? (yes/no)")

            if input("> ") == "yes":
                self.revert_to_previous_approach()

# Example
agent = TrustworthyAgent()

task = Task(description="Plan weekend trip")
agent.execute_transparently(task)

# Output:
# "📋 Task: Plan weekend trip
#    How I'll do it:
#    1. Search flights (agent: flight_agent)
#    2. Search hotels (agent: hotel_agent)
#    3. Recommend activities (agent: activity_agent)
#
#    Why this approach:
#    - Based on 15 similar tasks, this approach has 87% success rate
#
#    ⚠️  Potential risks:
#    - Limited flight availability (probability: 30%)
#    - Price changes during booking (probability: 15%)"
```

---

## Guidelines Summary

### Transparency
- **Always explain** what you're doing before you do it
- **Show reasoning** behind decisions
- **Communicate uncertainty** honestly
- **Report progress** during long operations

### Control
- **Request approval** for significant actions
- **Allow interruption** during execution
- **Respect rejections** and learn from them
- **Provide escape hatches** (cancel, undo)

### Consistency
- **Same input → same behavior** (unless learned otherwise)
- **Explain changes** in behavior
- **Maintain preferences** across sessions
- **Be predictable** in interactions

---

## Metrics

| Principle | Metric | Target |
|-----------|--------|--------|
| Connecting not Collapsing | User approval requests | > 0 for high-impact actions |
| Accessible yet Invisible | Proactive help acceptance rate | > 60% |
| Reflecting | Learning application rate | > 70% |
| Nudging | Nudge acceptance rate | > 40% |
| Adapting | Time to detect user evolution | < 2 weeks |
| Embrace Uncertainty | Confidence calibration (r) | > 0.7 |
| Establish Trust | User trust score (survey) | > 4.0 / 5.0 |

---

## Referencias

1. [Human-AI Interaction Guidelines - Microsoft](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)
2. [Designing for Trust in AI - Google PAIR](https://pair.withgoogle.com/guidebook/)
3. [Nudge Theory - Thaler & Sunstein](https://en.wikipedia.org/wiki/Nudge_theory)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Aprobado por**: AI Architecture Team & UX Team
