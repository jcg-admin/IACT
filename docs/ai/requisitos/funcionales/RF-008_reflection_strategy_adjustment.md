---
id: RF-008
tipo: requisito_funcional
relacionado: [UC-SYS-004, ADR-052, RT-009, RT-010]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-008: Reflection and Strategy Adjustment

## Especificación

El sistema DEBE implementar Reflection Layer para analizar fallos, identificar patterns, y generar strategy adjustments que mejoren el comportamiento futuro del agente (TRUE METACOGNITION).

## Criterios de Aceptación

### Escenario 1: Reflect on Failure - Root Cause Analysis

```gherkin
Given plan = Plan(task="Book hotel", strategy="cheapest")
  And evaluation = Evaluation(
      success=False,
      errors=["Quality too low (5 < 7)", "User rejected"]
  )
When ReflectionLayer.reflect_on_result(plan, evaluation)
Then reflection returned contains:
  - analysis: "I prioritized cheapest price, which led to quality=5 hotel.
              User feedback indicates quality > price.
              My 'budget-first' strategy is flawed for this user."
  And reflection.depth_score >= 0.7
  And analysis identifies ROOT CAUSE (strategy flaw), not just symptom
  And latency < 3000ms
```

### Escenario 2: Identify Patterns from Past Episodes

```gherkin
Given episodic_memory contains:
    | task              | strategy    | outcome   |
    | "Book hotel NYC"  | "cheapest"  | rejected  |
    | "Book hotel LA"   | "cheapest"  | rejected  |
    | "Book hotel SF"   | "cheapest"  | rejected  |
  And current failure: "Book hotel Paris", strategy="cheapest", rejected
When ReflectionLayer.identify_patterns(evaluation, user_id="user_123")
Then patterns_identified includes:
  - "Whenever I prioritize 'cheapest', user rejects quality <7"
  And pattern_validity >= 0.75 (3/3 = 100% confidence)
  And pattern has min_occurrences >= 3
  And latency < 1000ms
```

### Escenario 3: Decide Strategy Adjustments (Actionable)

```gherkin
Given analysis = "My 'budget-first' strategy conflicts with user quality preference"
  And patterns = ["cheapest → rejected quality <7"]
When ReflectionLayer.decide_adjustments(analysis, patterns)
Then adjustments returned:
  - "Change priority from 'price' to 'quality'"
  - "Add constraint: quality >= 7 in search"
  - "Sort by quality*reviews, not price"
  And actionability_score >= 0.8 (concrete, executable)
  And each adjustment matches ACTIONABLE_PATTERNS regex
  And latency < 1000ms
```

### Escenario 4: Formulate Learning

```gherkin
Given plan = Plan(...)
  And evaluation = Evaluation(success=False)
  And adjustments = ["priority=quality", "constraint: quality>=7"]
When ReflectionLayer.formulate_learning(plan, evaluation, adjustments)
Then learning is:
  """
  For this user, quality > price.
  Future hotel searches: quality >= 7, then optimize price.
  This prevents repeated low-quality selections.
  """
  And learning.length >= 50 characters
  And learning describes HOW to apply in future
```

### Escenario 5: Validate Reflection Quality

```gherkin
Given reflection = Reflection(
    analysis="...",
    patterns_identified=["..."],
    strategy_adjustments=["..."],
    learning="..."
  )
When ReflectionQualityValidator.validate_reflection(reflection)
Then validation_result is:
  - is_valid: True
  - quality_score: 0.85
  - metrics: {
      "completeness": 1.0,
      "depth_score": 0.8,
      "actionability_score": 0.9,
      "relevance_score": 0.75
    }
  - violations: []
```

### Escenario 6: Reject Low-Quality Reflection

```gherkin
Given reflection = Reflection(
    analysis="It failed",  # Too shallow
    patterns_identified=[],
    strategy_adjustments=["Do better"],  # Not actionable
    learning=""  # Missing
  )
When ReflectionQualityValidator.validate_reflection(reflection)
Then validation_result is:
  - is_valid: False
  - quality_score: 0.3
  - violations: [
      "Shallow reflection: depth=0.3 < 0.7",
      "Not actionable: 0.4 < 0.8",
      "Incomplete reflection: 0.5 < 0.9"
    ]
  And reflection is NOT stored in memory
```

### Escenario 7: Improvement Loop - Retry with Enhanced Prompt

```gherkin
Given first reflection has quality_score = 0.4 (rejected)
  And max_attempts = 3
When ReflectionImprovementLoop.generate_quality_reflection(plan, evaluation)
Then system retries with enhanced prompt:
  - Attempt 1: Standard prompt → quality=0.4 (fail)
  - Attempt 2: Enhanced prompt with quality guidance → quality=0.7 (fail)
  - Attempt 3: Explicit examples + guidance → quality=0.85 (success)
  And final reflection has quality_score >= 0.8
  And metrics.improvement_loop.iterations = 3
```

### Escenario 8: Store Reflection in Episodic Memory

```gherkin
Given reflection with quality_score = 0.85 (valid)
  And plan_id = "plan_123"
  And user_id = "user_123"
When ReflectionLayer.store_reflection(reflection, plan_id, user_id)
Then memory stored with:
  - memory_type: EPISODIC
  - content: reflection.learning
  - metadata: {
      "plan_id": "plan_123",
      "task": plan.task,
      "patterns": reflection.patterns_identified,
      "adjustments": reflection.strategy_adjustments,
      "quality_score": 0.85
    }
  - ttl: 90 days
  And latency < 100ms
```

### Escenario 9: Apply Adjustments Immediately

```gherkin
Given reflection.strategy_adjustments = [
    "Change priority from 'price' to 'quality'",
    "Add constraint: quality >= 7"
  ]
  And agent.config = {"hotel_search": {"priority": "price"}}
When ReflectionLayer.apply_adjustments(reflection.strategy_adjustments, agent)
Then agent.config updated to:
  - {"hotel_search": {"priority": "quality", "min_quality": 7}}
  And config persisted to database
  And metrics.adjustments_applied is incremented
```

### Escenario 10: Analyze Cause - Deep vs Shallow

```gherkin
Given evaluation with errors = ["Selected wrong hotel"]
When ReflectionLayer.analyze_cause(plan, evaluation)
Then analysis MUST identify:
  - Not just WHAT: "Wrong hotel selected" (shallow)
  - But WHY: "Prioritized price over quality" (medium)
  - And ROOT CAUSE: "'Budget-first' strategy conflicts with user preference" (deep)
  And depth_score >= 0.7
```

### Escenario 11: Pattern Validation - Insufficient Occurrences

```gherkin
Given pattern_candidate = "User prefers window seats on flights"
  And episodic_memory has only 1 occurrence of this pattern
When PatternValidator.validate(pattern_candidate, user_id="user_123")
Then pattern_validity = 0.0
  And reason = "Insufficient data (1 < 3 min_occurrences)"
  And pattern is NOT included in reflection.patterns_identified
```

### Escenario 12: Reflection Cost Budget Check

```gherkin
Given daily_metacognition_cost = $4.98
  And daily_budget = $5.00
  And estimated_cost(reflect_on_result) = $0.03
When ReflectionLayer.reflect_on_result(plan, evaluation)
Then MetacognitionCostExceeded is raised
  And error message = "Would exceed daily budget: $5.01 > $5.00"
  And reflection is NOT generated
  And system logs degradation event
```

### Escenario 13: Reflection Timeout

```gherkin
Given reflection generation takes > 10s (hard timeout)
When ReflectionLayer.reflect_on_result(plan, evaluation) with timeout=10s
Then MetacognitionTimeoutError is raised
  And partial reflection is NOT stored
  And metrics.metacognition.reflection.timeout is incremented
  And system falls back to non-reflective mode
```

### Escenario 14: Corrective RAG - Relevance Grading

```gherkin
Given tool_result = search_results([doc1, doc2, doc3])
  And query = "Best ski resorts for beginners"
When CorrectiveRAG.grade_relevance(tool_result, query)
Then relevance_grades = [
    {"doc": doc1, "score": 0.9, "relevant": True},
    {"doc": doc2, "score": 0.3, "relevant": False},
    {"doc": doc3, "score": 0.85, "relevant": True}
  ]
  And irrelevant docs (score < 0.5) are filtered
  And latency < 500ms
```

### Escenario 15: Corrective RAG - Knowledge Refinement

```gherkin
Given initial_query = "ski resorts"
  And relevance_score = 0.3 (low)
  And max_iterations = 3
When CorrectiveRAG.refine_knowledge(initial_query)
Then refinement_iterations:
  - Iteration 1: query="ski resorts" → relevance=0.3
  - Iteration 2: query="beginner ski resorts with lessons" → relevance=0.6
  - Iteration 3: query="beginner-friendly ski resorts, avoid advanced" → relevance=0.85
  And final_relevance >= 0.7
  And total_latency < 5000ms
```

### Escenario 16: LLM Re-ranking

```gherkin
Given search_results = [hotel1, hotel2, hotel3, hotel4, hotel5]
  And initial_ranking by price: [hotel3, hotel5, hotel1, hotel4, hotel2]
  And task = "Find romantic hotel in Paris"
When LLMReranker.rerank_results(search_results, task)
Then reranked_results ordered by relevance to "romantic":
  - [hotel2 (romantic ambiance), hotel4 (couples suite), hotel1, hotel3, hotel5]
  And each result has llm_score: 0.0-1.0
  And latency < 800ms
```

### Escenario 17: Reflection with No Past Experience

```gherkin
Given new_user with user_id = "new_user_456"
  And episodic_memory is empty
  And evaluation = Evaluation(success=False)
When ReflectionLayer.reflect_on_result(plan, evaluation)
Then reflection still generated with:
  - analysis: Root cause from current failure only
  - patterns_identified: []  # No patterns (insufficient data)
  - strategy_adjustments: Generic improvements based on current error
  - learning: How to handle similar tasks
  And quality_score >= 0.6 (lower threshold for first reflection)
```

### Escenario 18: Multiple Failures - Pattern Emerges

```gherkin
Given user_id = "user_123"
  And episodic_memory initially empty
  And 3 consecutive failures:
    - Failure 1: "cheap hotel rejected" → reflection stored
    - Failure 2: "cheap hotel rejected" → reflection stored
    - Failure 3: "cheap hotel rejected" → reflection with pattern
When ReflectionLayer.reflect_on_result(plan3, evaluation3)
Then reflection3.patterns_identified includes:
  - "User consistently rejects cheap hotels (quality <7)"
  And pattern_validity = 1.0 (3/3 occurrences)
  And adjustments become more aggressive:
    - "ALWAYS filter quality >= 7 for this user"
```

### Escenario 19: Success After Applying Learnings

```gherkin
Given past_reflection with adjustments = ["priority=quality", "min_quality=7"]
  And adjustments have been applied to agent config
  And new_task = "Book hotel in London"
When agent executes with new strategy:
  - Priority: quality (not price)
  - Constraint: quality >= 7
  And evaluation = Evaluation(success=True, user_confirmed=True)
Then system stores SUCCESS in episodic memory:
  - content: "Hotel booking SUCCESS - quality-first strategy worked"
  - metadata: {
      "strategy": "quality-first",
      "applied_from_reflection": "reflection_id_123",
      "validation": "strategy_adjustment_effective"
    }
  And metrics.success_after_reflection_rate is incremented
```

### Escenario 20: Reflection Quality Metrics Collection

```gherkin
Given 100 reflections generated over 1 day
When system collects quality metrics
Then metrics include:
  - reflection_quality_score_avg: 0.82
  - reflection_quality_score_p95: 0.91
  - depth_score_avg: 0.75
  - actionability_score_avg: 0.85
  - rejected_count: 5 (5%)
  - improvement_loop.iterations_avg: 1.3
  - success_after_reflection_rate: 0.78 (78% of tasks succeed after applying learnings)
```

## Implementación

Archivo: `scripts/coding/ai/metacognition/reflection_layer.py`

```python
class ReflectionLayer:
    """
    RF-008: Reflection Layer for TRUE METACOGNITION.
    Analyzes WHY failures occur, identifies patterns, adjusts strategies.
    """

    def __init__(self, llm, memory_manager, cost_tracker, quality_validator):
        self.llm = llm
        self.memory = memory_manager
        self.cost_tracker = cost_tracker
        self.validator = quality_validator
        self.improvement_loop = ReflectionImprovementLoop(llm, quality_validator)

    @enforce_metacognition_latency("reflect_on_result")
    @with_timeout("reflect_on_result")
    def reflect_on_result(
        self,
        plan: Plan,
        evaluation: Evaluation,
        user_id: str
    ) -> Reflection:
        """
        RF-008: Reflect on task result (TRUE METACOGNITION).

        Args:
            plan: Original plan
            evaluation: Evaluation result
            user_id: User identifier

        Returns:
            High-quality Reflection with adjustments

        Raises:
            MetacognitionTimeoutError: If exceeds 10s
            MetacognitionCostExceeded: If would exceed budget
        """
        # Check budget (RF-008 Scenario 12)
        estimated_cost = self._estimate_cost("reflect_on_result")
        self.cost_tracker.check_budget_before_operation(
            "reflect_on_result",
            estimated_cost
        )

        # Generate reflection with quality improvement loop (RF-008 Scenario 7)
        reflection = self.improvement_loop.generate_quality_reflection(
            plan,
            evaluation,
            user_id
        )

        # Store in episodic memory (RF-008 Scenario 8)
        self.store_reflection(reflection, plan.plan_id, user_id)

        # Apply adjustments immediately (RF-008 Scenario 9)
        self.apply_adjustments(reflection.strategy_adjustments, user_id)

        # Record cost
        actual_cost = self._calculate_cost(reflection)
        self.cost_tracker.record_operation_cost("reflect_on_result", actual_cost)

        return reflection

    @enforce_metacognition_latency("analyze_cause")
    def analyze_cause(self, plan: Plan, evaluation: Evaluation) -> str:
        """
        RF-008: Analyze ROOT CAUSE of failure (not just symptoms).

        Returns:
            Deep analysis identifying strategy flaws
        """
        prompt = f"""
Analyze WHY this task failed. Go beyond symptoms to ROOT CAUSE.

Plan:
{plan}

Evaluation:
{evaluation}

REQUIREMENTS:
1. DEPTH: Identify ROOT CAUSE, not just what happened
   - BAD: "Wrong hotel selected" (symptom)
   - GOOD: "'Budget-first' strategy conflicts with user quality preference" (root cause)

2. Focus on STRATEGY and REASONING flaws
   - What did you assume incorrectly?
   - What strategy did you use that didn't work?
   - Why did that strategy fail?

Provide deep analysis (min 100 characters).
"""
        analysis = self.llm.complete(prompt)

        # Validate depth (RT-010)
        depth_score = self.validator.depth_analyzer.assess_depth(analysis)

        if depth_score < 0.7:
            logger.warning(
                f"Shallow analysis (depth={depth_score:.2f}). "
                f"Requesting deeper analysis."
            )
            # Retry with more explicit prompt
            analysis = self._retry_analysis_with_guidance(plan, evaluation)

        return analysis

    @enforce_metacognition_latency("identify_patterns")
    def identify_patterns(
        self,
        evaluation: Evaluation,
        user_id: str
    ) -> List[str]:
        """
        RF-008: Identify patterns from past episodic memories.

        Returns:
            List of validated patterns (>= 3 occurrences)
        """
        # Search episodic memory for similar failures
        similar_episodes = self.memory.retrieve(
            query=f"failed {evaluation.errors[0] if evaluation.errors else 'task'}",
            memory_types=[MemoryType.EPISODIC],
            user_id=user_id,
            top_k=20
        )

        if len(similar_episodes) < 3:
            # Not enough data for patterns (RF-008 Scenario 11)
            logger.info(
                f"Insufficient episodes for pattern detection: "
                f"{len(similar_episodes)} < 3"
            )
            return []

        # Use LLM to identify patterns
        prompt = f"""
Analyze these past failures and identify patterns:

{similar_episodes}

Current failure:
{evaluation}

Identify recurring patterns (e.g., "Whenever X strategy, Y outcome").
Only include patterns with >= 3 occurrences.

Return JSON list of patterns.
"""
        response = self.llm.complete(prompt)
        pattern_candidates = json.loads(response)

        # Validate each pattern (RT-010)
        validated_patterns = []
        for pattern in pattern_candidates:
            validity = self.validator.pattern_validator.validate(pattern, user_id)

            if validity >= 0.75:
                validated_patterns.append(pattern)
            else:
                logger.warning(
                    f"Pattern rejected (validity={validity:.2f}): {pattern}"
                )

        return validated_patterns

    @enforce_metacognition_latency("decide_adjustments")
    def decide_adjustments(
        self,
        analysis: str,
        patterns: List[str]
    ) -> List[str]:
        """
        RF-008: Decide concrete, executable strategy adjustments.

        Returns:
            List of actionable adjustments
        """
        prompt = f"""
Based on this analysis and patterns, decide CONCRETE strategy adjustments.

Analysis:
{analysis}

Patterns:
{patterns}

REQUIREMENTS - Adjustments MUST be:
1. CONCRETE: Specific changes, not vague
   - BAD: "Do better"
   - GOOD: "Change priority from 'price' to 'quality'"

2. EXECUTABLE: Can be implemented in code
   - BAD: "Be more careful"
   - GOOD: "Add constraint: quality >= 7 in search"

3. ACTIONABLE: Use patterns like:
   - "Change X to Y"
   - "Add constraint: Z"
   - "Remove W"
   - "Filter results where V"

Return JSON list of adjustments.
"""
        response = self.llm.complete(prompt)
        adjustments = json.loads(response)

        # Validate actionability (RT-010)
        actionability = self.validator.actionability_checker.score(adjustments)

        if actionability < 0.8:
            logger.warning(
                f"Adjustments not actionable (score={actionability:.2f}). "
                f"Requesting more concrete adjustments."
            )
            # Retry with examples
            adjustments = self._retry_adjustments_with_examples(analysis, patterns)

        return adjustments

    def formulate_learning(
        self,
        plan: Plan,
        evaluation: Evaluation,
        adjustments: List[str]
    ) -> str:
        """
        RF-008: Formulate learning for future application.

        Returns:
            Learning description (min 50 chars)
        """
        prompt = f"""
Formulate what was learned from this failure.

Plan:
{plan}

Evaluation:
{evaluation}

Adjustments:
{adjustments}

Describe:
1. What was learned
2. How to apply it in future
3. What this prevents

Min 50 characters.
"""
        learning = self.llm.complete(prompt)

        if len(learning) < 50:
            raise ValueError(f"Learning too short: {len(learning)} < 50")

        return learning

    def store_reflection(
        self,
        reflection: Reflection,
        plan_id: str,
        user_id: str
    ):
        """
        RF-008: Store reflection in episodic memory.
        """
        self.memory.add(
            content=reflection.learning,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "plan_id": plan_id,
                "task": reflection.task,
                "patterns": reflection.patterns_identified,
                "adjustments": reflection.strategy_adjustments,
                "quality_score": reflection.quality_score,
                "analysis": reflection.analysis,
                "timestamp": datetime.now().isoformat()
            },
            user_id=user_id
        )

        logger.info(
            f"Reflection stored: quality={reflection.quality_score:.2f}, "
            f"patterns={len(reflection.patterns_identified)}, "
            f"adjustments={len(reflection.strategy_adjustments)}"
        )

    def apply_adjustments(
        self,
        adjustments: List[str],
        user_id: str
    ):
        """
        RF-008: Apply strategy adjustments to agent config.
        """
        for adjustment in adjustments:
            # Parse adjustment
            parsed = self._parse_adjustment(adjustment)

            if parsed["type"] == "change_priority":
                self._update_config(
                    user_id,
                    f"{parsed['domain']}.priority",
                    parsed["new_value"]
                )

            elif parsed["type"] == "add_constraint":
                self._add_constraint(
                    user_id,
                    parsed["domain"],
                    parsed["constraint"]
                )

            elif parsed["type"] == "remove_strategy":
                self._remove_strategy(
                    user_id,
                    parsed["domain"],
                    parsed["strategy_name"]
                )

            logger.info(f"Applied adjustment: {adjustment}")
            metrics.increment("metacognition.adjustments_applied")
```

Archivo: `scripts/coding/ai/metacognition/corrective_rag.py`

```python
class CorrectiveRAG:
    """
    RF-008: Corrective RAG for self-correction in retrieval.
    """

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    @enforce_metacognition_latency("corrective_rag_cycle")
    def refine_knowledge(
        self,
        initial_query: str,
        max_iterations: int = 3
    ) -> Tuple[List[Dict], float]:
        """
        RF-008: Iteratively refine query until relevance is high.

        Returns:
            (refined_results, final_relevance_score)
        """
        query = initial_query
        iteration = 0

        while iteration < max_iterations:
            # Retrieve
            results = self.retriever.search(query, top_k=10)

            # Grade relevance
            relevance_grades = self.grade_relevance(results, initial_query)

            # Calculate average relevance
            avg_relevance = sum(g["score"] for g in relevance_grades) / len(relevance_grades)

            if avg_relevance >= 0.7:
                # Good enough
                logger.info(
                    f"Corrective RAG converged at iteration {iteration + 1}: "
                    f"relevance={avg_relevance:.2f}"
                )
                return results, avg_relevance

            # Refine query
            query = self._refine_query(query, initial_query, relevance_grades)
            iteration += 1

        logger.warning(
            f"Corrective RAG did not converge after {max_iterations} iterations: "
            f"relevance={avg_relevance:.2f}"
        )

        return results, avg_relevance

    @enforce_metacognition_latency("relevance_grading")
    def grade_relevance(
        self,
        results: List[Dict],
        query: str
    ) -> List[Dict]:
        """
        RF-008: Grade relevance of each result.

        Returns:
            [{"doc": doc, "score": float, "relevant": bool}, ...]
        """
        grades = []

        for doc in results:
            prompt = f"""
Grade relevance of this document to the query.

Query: {query}

Document:
{doc["content"][:500]}

Return JSON: {{"score": 0.0-1.0, "reason": "..."}}
"""
            response = self.llm.complete(prompt)
            grade_data = json.loads(response)

            grades.append({
                "doc": doc,
                "score": grade_data["score"],
                "relevant": grade_data["score"] >= 0.5,
                "reason": grade_data["reason"]
            })

        return grades
```

## Tests

Archivo: `scripts/coding/tests/ai/test_reflection_strategy.py`

```python
class TestReflectionLayer:
    def test_reflect_root_cause_analysis(self):
        """RF-008 Scenario 1: Root cause analysis."""
        reflector = ReflectionLayer(
            llm=mock_llm,
            memory=mock_memory,
            cost_tracker=mock_tracker,
            quality_validator=mock_validator
        )

        plan = Plan(task="Book hotel", strategy="cheapest")
        evaluation = Evaluation(
            success=False,
            errors=["Quality too low (5 < 7)", "User rejected"]
        )

        reflection = reflector.reflect_on_result(plan, evaluation, "user_123")

        assert reflection.analysis is not None
        assert len(reflection.analysis) > 50
        assert "strategy" in reflection.analysis.lower()
        assert reflection.depth_score >= 0.7

    def test_identify_patterns(self):
        """RF-008 Scenario 2: Identify patterns from past episodes."""
        # Add 3 similar failures to memory
        for i in range(3):
            mock_memory.add(
                content=f"Hotel booking failed - cheap hotel rejected {i}",
                memory_type=MemoryType.EPISODIC,
                metadata={"strategy": "cheapest", "outcome": "rejected"}
            )

        reflector = ReflectionLayer(...)
        evaluation = Evaluation(success=False, errors=["Quality too low"])

        patterns = reflector.identify_patterns(evaluation, "user_123")

        assert len(patterns) > 0
        assert any("cheapest" in p.lower() for p in patterns)

    def test_decide_adjustments_actionable(self):
        """RF-008 Scenario 3: Decide actionable adjustments."""
        reflector = ReflectionLayer(...)

        analysis = "Budget-first strategy conflicts with quality preference"
        patterns = ["cheapest → rejected"]

        adjustments = reflector.decide_adjustments(analysis, patterns)

        assert len(adjustments) > 0
        assert any("quality" in adj.lower() for adj in adjustments)
        # Check actionability
        actionability = mock_validator.actionability_checker.score(adjustments)
        assert actionability >= 0.8

    def test_improvement_loop(self):
        """RF-008 Scenario 7: Improvement loop retries."""
        reflector = ReflectionLayer(...)

        # Mock: first attempt fails quality, second succeeds
        mock_llm.set_responses([
            '{"analysis": "It failed"}',  # Attempt 1 - shallow
            '{"analysis": "My budget-first strategy conflicts with user quality preference..."}',  # Attempt 2 - deep
        ])

        reflection = reflector.improvement_loop.generate_quality_reflection(
            plan, evaluation, "user_123"
        )

        assert reflection.quality_score >= 0.8
        assert metrics.get("improvement_loop.iterations") == 2

    def test_store_and_apply_adjustments(self):
        """RF-008 Scenarios 8, 9: Store reflection and apply adjustments."""
        reflector = ReflectionLayer(...)

        reflection = Reflection(
            analysis="...",
            patterns_identified=["..."],
            strategy_adjustments=["Change priority to 'quality'", "Add constraint: quality>=7"],
            learning="Quality > price for this user"
        )

        # Store
        reflector.store_reflection(reflection, "plan_123", "user_123")

        # Verify stored
        memories = mock_memory.retrieve(
            query="quality price",
            memory_types=[MemoryType.EPISODIC]
        )
        assert len(memories) > 0

        # Apply
        reflector.apply_adjustments(reflection.strategy_adjustments, "user_123")

        # Verify config updated
        config = get_agent_config("user_123")
        assert config["hotel_search"]["priority"] == "quality"


class TestCorrectiveRAG:
    def test_relevance_grading(self):
        """RF-008 Scenario 14: Relevance grading."""
        rag = CorrectiveRAG(llm=mock_llm, retriever=mock_retriever)

        results = [
            {"content": "Best ski resorts for beginners in Colorado"},
            {"content": "Advanced ski techniques for experts"},
            {"content": "Beginner-friendly ski lessons"}
        ]

        query = "Best ski resorts for beginners"

        grades = rag.grade_relevance(results, query)

        assert len(grades) == 3
        assert grades[0]["relevant"] == True  # Matches query
        assert grades[1]["relevant"] == False  # For experts, not beginners

    def test_knowledge_refinement(self):
        """RF-008 Scenario 15: Knowledge refinement loop."""
        rag = CorrectiveRAG(llm=mock_llm, retriever=mock_retriever)

        # Mock: first query low relevance, refined query high relevance
        mock_retriever.set_responses([
            (results_low_relevance, 0.3),
            (results_medium_relevance, 0.6),
            (results_high_relevance, 0.85)
        ])

        refined_results, final_relevance = rag.refine_knowledge(
            "ski resorts",
            max_iterations=3
        )

        assert final_relevance >= 0.7
        assert len(refined_results) > 0
```

Resultado esperado: `20 passed in 0.35s`

## Métricas

- Reflection latency p95: < 3s
- Reflection quality score avg: > 0.8
- Depth score avg: > 0.7
- Actionability score avg: > 0.8
- Pattern validity avg: > 0.75
- Rejection rate: < 5%
- Success after reflection rate: > 78%

## Referencias

- UC-SYS-004: Metacognitive Agent Operations
- ADR-052: Metacognition Architecture
- RT-009: Metacognition Performance Constraints
- RT-010: Reflection Quality Standards

---

**Requisito**: Reflection Layer analiza fallos profundamente, identifica patterns válidos, genera adjustments ejecutables.
**Verificación**: Gherkin scenarios + quality validation + TDD tests.
