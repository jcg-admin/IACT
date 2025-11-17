---
id: ADR-052
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-048, ADR-050]
---

# ADR-052: Metacognition Architecture for AI Agents

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

### Problem Statement

Los agentes AI actuales ejecutan tareas pero **no reflexionan sobre su propio razonamiento**:

**Problemas actuales**:
- Agentes no aprenden de errores
- No ajustan estrategias basado en resultados pasados
- No detectan cuando su approach es subóptimo
- No explican su razonamiento (transparency)
- Repiten mismos errores

**Ejemplo Travel Agent**:
- Siempre recomienda vuelos económicos sin considerar si fue buena elección
- No nota patrón: "cada vez que recomiendo por precio bajo, usuario rechaza"
- No adapta estrategia: sigue priorizando precio sobre calidad

### What is Metacognition?

**Metacognition = "Thinking about thinking"**

Higher-order cognitive process que involucra:
- Self-awareness de propios procesos cognitivos
- Self-regulation: ajustar comportamiento
- Self-reflection: analizar decisiones pasadas

**True Metacognition en AI**:
```
Agent: "I prioritized cheaper flights because...
        but I might be missing out on direct flights.
        Let me re-check my decision-making strategy."
```

**NOT just**:
```
Agent: "I chose the cheap flight."  // No reflection
```

### Importance of Metacognition

![Importance diagram from lesson]

1. **Self-Reflection**: Assess own performance, identify improvements
2. **Adaptability**: Modify strategies based on experience
3. **Error Correction**: Detect and fix errors autonomously
4. **Resource Management**: Optimize time/compute usage
5. **Transparency**: Explain reasoning to users
6. **Perception**: Improve accuracy in recognizing patterns

### Components of Metacognitive Agent

```
┌─────────────────────────────────────────────────────┐
│             Metacognitive Agent                      │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Persona  │  │  Tools   │  │  Skills  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       └─────────────┴─────────────┘                 │
│              Expertise Unit                          │
│                     │                                │
│       ┌─────────────┴────────────┐                  │
│       │                          │                  │
│  ┌────┴────┐              ┌──────┴──────┐           │
│  │ Planning│              │  Evaluation │           │
│  │ Layer   │◄────────────►│   Layer     │           │
│  └────┬────┘              └──────┬──────┘           │
│       │                          │                  │
│       └──────────┬───────────────┘                  │
│                  │                                  │
│         ┌────────┴────────┐                         │
│         │  Reflection     │                         │
│         │  Layer          │                         │
│         └─────────────────┘                         │
└─────────────────────────────────────────────────────┘
```

**Layers**:
1. **Expertise Unit**: Persona + Tools + Skills
2. **Planning Layer**: Define goals, break into steps
3. **Evaluation Layer**: Assess results, measure success
4. **Reflection Layer**: Analyze why certain results, adjust strategy

## Decision

Implementar **Metacognitive Architecture** con 3 capas: Planning, Evaluation, Reflection.

### Architecture Overview

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. PLANNING LAYER                   │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ • Define clear results       │  │
│  │ • Identify required resources│  │
│  │ • Break into steps           │  │
│  │ • Consider past experience   │  │
│  └──────────────────────────────┘  │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 2. EXECUTION (Existing Agent)       │
│  • Use tools                        │
│  • Retrieve information             │
│  • Generate response                │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 3. EVALUATION LAYER                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ • Measure against goals      │  │
│  │ • Check success criteria     │  │
│  │ • Identify errors            │  │
│  │ • Score relevancy            │  │
│  └──────────────────────────────┘  │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 4. REFLECTION LAYER                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ • Why did this approach work?│  │
│  │ • What patterns emerge?      │  │
│  │ • Should I adjust strategy?  │  │
│  │ • Store learning             │  │
│  └──────────────────────────────┘  │
└──────────┬──────────────────────────┘
           ↓
    Update Strategy
    Store Experience
           ↓
     (Loop back to Planning for next task)
```

### 1. Planning Layer

**Purpose**: Outline steps to achieve goal

**Components**:

```python
class PlanningLayer:
    def create_plan(self, task: str) -> Plan:
        """
        Create plan for task with metacognitive elements.

        Returns:
            Plan {
                task: str,
                desired_result: str,
                steps: List[Step],
                required_resources: List[str],
                success_criteria: List[str],
                past_experience: List[Experience]
            }
        """
        # 1. Define clear result
        desired_result = self.define_result(task)

        # 2. Break into steps
        steps = self.decompose_into_steps(task, desired_result)

        # 3. Identify resources
        resources = self.identify_resources(steps)

        # 4. Retrieve relevant past experience
        experience = self.memory.retrieve(
            query=task,
            memory_types=[MemoryType.EPISODIC]
        )

        # 5. Adjust plan based on experience
        if experience:
            steps = self.adjust_based_on_experience(steps, experience)

        return Plan(
            task=task,
            desired_result=desired_result,
            steps=steps,
            required_resources=resources,
            success_criteria=self.define_success_criteria(desired_result),
            past_experience=experience
        )
```

**Example - Travel Agent**:

```python
task = "Book trip to Paris"

plan = PlanningLayer().create_plan(task)
# Plan {
#   desired_result: "User has confirmed flight + hotel",
#   steps: [
#     "Gather preferences",
#     "Search flights (priority: quality over price based on past feedback)",
#     "Search hotels",
#     "Compile itinerary",
#     "Get user feedback"
#   ],
#   success_criteria: [
#     "Flight matches preferences (direct, morning)",
#     "Hotel within budget and quality > 7",
#     "User approves itinerary"
#   ],
#   past_experience: [
#     "User rejected cheap hotels (quality < 7) last time",
#     "User preferred direct flights even if more expensive"
#   ]
# }
```

### 2. Evaluation Layer

**Purpose**: Assess results against goals

**Components**:

```python
class EvaluationLayer:
    def evaluate_result(self, plan: Plan, result: Any) -> Evaluation:
        """
        Evaluate result of execution against plan.

        Returns:
            Evaluation {
                success: bool,
                criteria_met: Dict[str, bool],
                errors: List[Error],
                relevancy_score: float,
                feedback: str
            }
        """
        evaluation = Evaluation()

        # 1. Check success criteria
        for criterion in plan.success_criteria:
            met = self.check_criterion(criterion, result)
            evaluation.criteria_met[criterion] = met

        # 2. Overall success
        evaluation.success = all(evaluation.criteria_met.values())

        # 3. Identify errors
        if not evaluation.success:
            evaluation.errors = self.identify_errors(result, plan)

        # 4. Relevancy scoring
        evaluation.relevancy_score = self.score_relevancy(result, plan.task)

        # 5. User feedback (if available)
        evaluation.feedback = self.collect_user_feedback()

        return evaluation
```

**Example**:

```python
evaluation = EvaluationLayer().evaluate_result(plan, booking_result)
# Evaluation {
#   success: False,
#   criteria_met: {
#     "Flight matches preferences": True,
#     "Hotel quality > 7": False,  # FAILED
#     "User approves": False
#   },
#   errors: [
#     "Selected hotel has quality=6 (below threshold)"
#   ],
#   relevancy_score: 0.65,
#   feedback: "Hotel too cheap, low quality"
# }
```

### 3. Reflection Layer

**Purpose**: Analyze why certain results, adjust strategy

**Components**:

```python
class ReflectionLayer:
    def reflect_on_result(self, plan: Plan, evaluation: Evaluation) -> Reflection:
        """
        Reflect on execution and evaluation.

        This is TRUE metacognition: reasoning about reasoning.

        Returns:
            Reflection {
                analysis: str,
                patterns_identified: List[str],
                strategy_adjustments: List[str],
                learning: str
            }
        """
        reflection = Reflection()

        # 1. Analyze WHY result occurred
        reflection.analysis = self.analyze_cause(plan, evaluation)

        # 2. Identify patterns
        reflection.patterns_identified = self.identify_patterns(evaluation)

        # 3. Decide strategy adjustments
        reflection.strategy_adjustments = self.decide_adjustments(
            evaluation,
            reflection.patterns_identified
        )

        # 4. Formulate learning
        reflection.learning = self.formulate_learning(
            plan,
            evaluation,
            reflection.strategy_adjustments
        )

        # 5. Store learning in episodic memory
        self.memory.add(
            content=reflection.learning,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "task": plan.task,
                "success": evaluation.success,
                "adjustments": reflection.strategy_adjustments
            }
        )

        return reflection
```

**Example - True Metacognition**:

```python
reflection = ReflectionLayer().reflect_on_result(plan, evaluation)
# Reflection {
#   analysis: """
#     I prioritized cheaper hotels to stay within budget.
#     However, this led to selecting a quality=6 hotel.
#     User feedback indicates quality is more important than price.
#   """,
#   patterns_identified: [
#     "Whenever I prioritize 'cheapest', user rejects low quality (<7)",
#     "User consistently prefers direct flights even if expensive",
#     "My 'budget-first' strategy is flawed for this user"
#   ],
#   strategy_adjustments: [
#     "Change hotel selection from 'cheapest' to 'highest_quality'",
#     "Add quality threshold: minimum quality=7",
#     "Re-rank results: quality first, then price"
#   ],
#   learning: """
#     For this user, quality > price.
#     Adjust future recommendations:
#     - Hotels: quality >= 7, then optimize price
#     - Flights: prefer direct, even if +20% cost
#     This prevents repeated low-quality selections.
#   """
# }
```

## Implementation Strategies

### 1. Corrective RAG (Retrieval-Augmented Generation)

**Purpose**: Use RAG to correct errors and improve accuracy

**Approach**:
1. **Prompting Technique**: Guide retrieval with specific prompts
2. **Tool**: Implement ranking/filtering algorithms
3. **Evaluation**: Assess performance, make adjustments

```python
class CorrectiveRAG:
    def retrieve_and_correct(self, query: str, initial_result: Any) -> Any:
        """
        Retrieve relevant info and correct initial result.

        Steps:
        1. Initial retrieval based on query
        2. Evaluate relevance of results
        3. If relevance < threshold, reformulate query
        4. Re-retrieve with corrected query
        5. Re-rank and filter results
        """
        # Initial retrieval
        results = self.rag_engine.retrieve(query)

        # Evaluate relevance
        relevance_scores = [
            self.evaluate_relevance(r, query) for r in results
        ]

        if max(relevance_scores) < 0.7:
            # Low relevance - reformulate query
            corrected_query = self.reformulate_query(query, initial_result)
            results = self.rag_engine.retrieve(corrected_query)

        # Re-rank using LLM
        ranked = self.llm_rerank(results, query)

        return ranked
```

### 2. Bootstrapping with Goal

**Purpose**: Start with clear goal, iterate to optimize

```python
class GoalBootstrapper:
    def bootstrap_and_iterate(self, goal: str, options: List[Any]) -> Any:
        """
        Bootstrap plan with goal, iterate to refine.

        Steps:
        1. Define goal clearly
        2. Generate initial plan
        3. Execute plan
        4. Evaluate against goal
        5. Iterate to improve
        """
        # 1. Define goal
        success_criteria = self.define_success_criteria(goal)

        # 2. Initial plan
        plan = self.create_initial_plan(goal, options, success_criteria)

        # 3. Execute
        result = self.execute_plan(plan)

        # 4. Evaluate
        evaluation = self.evaluate_result(result, success_criteria)

        # 5. Iterate if needed
        iterations = 0
        while not evaluation.success and iterations < 3:
            # Reflect
            reflection = self.reflect_on_result(plan, evaluation)

            # Adjust plan based on reflection
            plan = self.adjust_plan(plan, reflection.strategy_adjustments)

            # Re-execute
            result = self.execute_plan(plan)
            evaluation = self.evaluate_result(result, success_criteria)
            iterations += 1

        return result
```

### 3. LLM for Re-ranking and Scoring

**Purpose**: Use LLM to evaluate and rank options

```python
class LLMRanker:
    def rerank_with_llm(self, options: List[Dict], preferences: Dict) -> List[Dict]:
        """
        Use LLM to re-rank options based on preferences.

        Returns options sorted by relevance score.
        """
        prompt = f"""
Rank these options based on user preferences:

User Preferences:
{json.dumps(preferences, indent=2)}

Options:
{json.dumps(options, indent=2)}

For each option, provide:
1. Relevance score (0.0-1.0)
2. Reasoning for score

Return JSON:
[
  {{"option_id": "...", "score": 0.9, "reasoning": "..."}},
  ...
]
"""
        response = self.llm.complete(prompt)
        scored_options = json.loads(response)

        # Sort by score
        ranked = sorted(scored_options, key=lambda x: x["score"], reverse=True)

        return ranked
```

## Metacognition Abilities

### 1. Self-Reflection

```python
def self_reflect(self, past_actions: List[Action]) -> Reflection:
    """
    Analyze past actions to identify patterns and improvements.

    Example:
    "I noticed that whenever I recommend budget hotels,
     users complain about quality. I should adjust my
     selection criteria to prioritize quality over price."
    """
```

### 2. Adaptability

```python
def adapt_strategy(self, feedback: Feedback) -> Strategy:
    """
    Modify strategy based on feedback and experience.

    Example:
    Changed from "cheapest" to "highest_quality" strategy
    after observing pattern of low-quality rejections.
    """
```

### 3. Error Correction

```python
def correct_error(self, error: Error) -> Correction:
    """
    Detect and autonomously correct errors.

    Example:
    Detected: Selected hotel with quality=6
    Analysis: User threshold is quality>=7
    Correction: Re-select with quality constraint
    """
```

## Consequences

### Positive

1. **Self-Improving Agents**: Learn from mistakes, improve over time
2. **Better Decision-Making**: Reason about reasoning
3. **Transparency**: Can explain why certain choice was made
4. **Adaptability**: Adjust to changing conditions
5. **Error Recovery**: Detect and fix own errors
6. **Pattern Recognition**: Identify recurring issues
7. **Strategic Thinking**: Not just execute, but plan and reflect

### Negative

1. **Computational Overhead**: Additional LLM calls for reflection
2. **Latency**: Reflection layer adds time
3. **Complexity**: More components to build and debug
4. **Risk of Over-Reflection**: Might overthink simple tasks
5. **Storage Requirements**: Need to store episodic memories

## Implementation Plan

### Phase 1: Planning Layer (Sprint 1-2)
- [ ] Plan creation with clear results
- [ ] Step decomposition
- [ ] Resource identification
- [ ] Experience retrieval

### Phase 2: Evaluation Layer (Sprint 3-4)
- [ ] Success criteria checking
- [ ] Error identification
- [ ] Relevancy scoring
- [ ] User feedback collection

### Phase 3: Reflection Layer (Sprint 5-6)
- [ ] Cause analysis
- [ ] Pattern identification
- [ ] Strategy adjustment
- [ ] Learning formulation
- [ ] Episodic memory storage

### Phase 4: Integration (Sprint 7-8)
- [ ] Corrective RAG implementation
- [ ] LLM re-ranking
- [ ] Goal bootstrapping
- [ ] End-to-end testing

## Metrics

- **Reflection frequency**: % tasks that trigger reflection
- **Strategy adjustments**: # adjustments made based on reflection
- **Error correction rate**: % errors auto-corrected
- **Learning retention**: % learnings reused in future tasks
- **Performance improvement**: Δ success rate over time

## References

- Lesson: "Metacognition in AI Agents"
- ADR-048: AI Agent Memory (episodic memory for learning)
- ADR-050: Context Engineering (context for reflection)
- Pattern: Planning-Execution-Evaluation-Reflection loop

---

**Decision**: Implementar Metacognitive Architecture con Planning, Evaluation, Reflection layers.
**Rationale**: Habilitar true metacognition - agents que razonan sobre su propio razonamiento.
**Trade-offs**: Latency y complejidad vs. self-improvement y transparency.
