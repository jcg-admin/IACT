---
id: RF-007
tipo: requisito_funcional
relacionado: [UC-SYS-004, ADR-052, RT-009]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-007: Planning and Evaluation

## Especificación

El sistema DEBE implementar Planning Layer y Evaluation Layer para crear planes estructurados con success criteria y evaluar resultados objetivamente.

## Criterios de Aceptación

### Escenario 1: Create Plan with Desired Result

```gherkin
Given task = "Book hotel in Paris"
  And user_id = "user_123"
When PlanningLayer.create_plan(task)
Then plan is returned with:
  - desired_result: Clear description of end state
  - steps: List of concrete steps
  - success_criteria: Measurable criteria
  And desired_result contains:
    - "User has: Confirmed hotel reservation"
    - "System shows: Booking confirmation"
  And latency < 2000ms
```

### Escenario 2: Plan with Past Experience

```gherkin
Given task = "Book hotel in Paris"
  And episodic_memory contains:
    | content                                      | timestamp  |
    | "User rejected cheap hotel (quality < 7)"   | 2025-11-15 |
    | "User prefers quality over price"           | 2025-11-14 |
When PlanningLayer.create_plan(task)
Then plan.steps include:
  - "Filter hotels: quality >= 7"
  - "Sort by quality, not price"
  And plan.metadata.influenced_by_experience = True
  And plan.metadata.past_learnings = ["quality > price"]
```

### Escenario 3: Decompose Task into Steps

```gherkin
Given task = "Book flight to Paris on Dec 15"
When PlanningLayer.decompose_task(task)
Then steps returned are:
  | step                                  | order |
  | "Search flights to Paris on Dec 15"  | 1     |
  | "Filter by user preferences"         | 2     |
  | "Select best option"                 | 3     |
  | "Book selected flight"               | 4     |
  | "Confirm with user"                  | 5     |
  And each step has:
    - description: str
    - expected_output: str
    - dependencies: List[int] (step numbers)
  And latency < 1000ms
```

### Escenario 4: Plan with Success Criteria

```gherkin
Given task = "Recommend ski resort"
  And user has preference: "avoid advanced slopes (injury)"
When PlanningLayer.create_plan(task)
Then plan.success_criteria includes:
  - "Resort has beginner/intermediate slopes"
  - "No advanced-only resorts recommended"
  - "User confirms recommendation"
  And each criterion is:
    - measurable: bool
    - verifiable: bool
```

### Escenario 5: Plan Cache Hit

```gherkin
Given previous plan exists:
    task_cached = "Book hotel in Paris"
    plan_cached = Plan(...)
  And task_new = "Book hotel in Paris for 2 nights"
  And similarity(task_cached, task_new) = 0.87
When PlanningLayer.create_plan(task_new)
Then plan is retrieved from cache
  And plan is adjusted for "2 nights" (minor modification)
  And latency < 500ms (faster than fresh generation)
  And metrics.plan_cache.hit is incremented
```

### Escenario 6: Evaluate Result - Success

```gherkin
Given plan with success_criteria:
    - "Hotel quality >= 7"
    - "Price within budget ($200)"
    - "User confirms"
  And execution_result:
    - hotel_selected = Hotel(quality=8, price=150)
    - user_feedback = "confirmed"
When EvaluationLayer.evaluate_result(plan, execution_result)
Then evaluation returned:
  - success: True
  - criteria_met: [
      {"criterion": "quality >= 7", "met": True, "actual": 8},
      {"criterion": "price <= 200", "met": True, "actual": 150},
      {"criterion": "user confirms", "met": True}
    ]
  - errors: []
  - relevancy_score: 1.0
  And latency < 500ms
```

### Escenario 7: Evaluate Result - Failure

```gherkin
Given plan with success_criteria:
    - "Hotel quality >= 7"
    - "User confirms"
  And execution_result:
    - hotel_selected = Hotel(quality=5, price=80)
    - user_feedback = "rejected - too low quality"
When EvaluationLayer.evaluate_result(plan, execution_result)
Then evaluation returned:
  - success: False
  - criteria_met: [
      {"criterion": "quality >= 7", "met": False, "actual": 5},
      {"criterion": "user confirms", "met": False}
    ]
  - errors: ["Quality below threshold (5 < 7)", "User rejected"]
  - relevancy_score: 0.3
  And latency < 500ms
  And triggers ReflectionLayer
```

### Escenario 8: Check Single Criterion

```gherkin
Given criterion = "Hotel quality >= 7"
  And execution_result.hotel_quality = 8
When EvaluationLayer.check_criterion(criterion, execution_result)
Then result is:
  - met: True
  - actual_value: 8
  - expected_value: ">= 7"
  - explanation: "Quality 8 meets threshold of 7"
  And latency < 200ms
```

### Escenario 9: Assess Relevance Score

```gherkin
Given task = "Find romantic restaurant in Paris"
  And execution_result = {
      "restaurant": "Le Chat Noir",
      "cuisine": "French",
      "ambiance": "romantic",
      "price": "$$"
  }
When EvaluationLayer.assess_relevance(task, execution_result)
Then relevancy_score >= 0.8
  And score_breakdown includes:
    - task_match: 0.9 (high)
    - user_satisfaction: 0.85 (predicted)
    - completeness: 1.0 (all fields present)
  And latency < 300ms
```

### Escenario 10: Parallel Criteria Checking

```gherkin
Given plan with 5 success_criteria
  And execution_result available
When EvaluationLayer.evaluate_result(plan, execution_result)
Then all criteria are checked in parallel (asyncio.gather)
  And total_latency < 500ms
  And total_latency < sum(individual_latencies)
```

### Escenario 11: Plan Creation Timeout

```gherkin
Given task = "Complex multi-day trip planning"
  And create_plan operation takes > 5000ms (timeout)
When PlanningLayer.create_plan(task) with timeout=5000ms
Then MetacognitionTimeoutError is raised
  And error message contains "create_plan exceeded 5000ms"
  And partial plan is NOT returned
  And metrics.metacognition.timeout_errors is incremented
```

### Escenario 12: Cost Budget Check Before Planning

```gherkin
Given user_id = "user_123"
  And daily_metacognition_cost = $4.80
  And daily_budget = $5.00
  And estimated_cost(create_plan) = $0.30
When PlanningLayer.create_plan(task)
Then MetacognitionCostExceeded is raised
  And error message = "Would exceed daily budget: $5.10 > $5.00"
  And plan is NOT created
  And metrics.metacognition.cost_exceeded is incremented
```

### Escenario 13: Retrieve Experience for Similar Task

```gherkin
Given episodic_memory contains:
    | content                               | task_type      | outcome |
    | "Hotel booking - quality > price"     | hotel_booking  | success |
    | "Flight booking - morning preferred"  | flight_booking | success |
  And task = "Book hotel in London"
  And task_type = "hotel_booking"
When PlanningLayer.retrieve_experience(task, task_type)
Then relevant_memories returned:
  - [{"content": "Hotel booking - quality > price", "score": 0.92}]
  And flight_booking memory is NOT included (different task_type)
  And latency < 100ms
```

### Escenario 14: Apply Strategy Adjustments from Past Reflection

```gherkin
Given task = "Book hotel in Paris"
  And past_reflection contains adjustments:
    - "Change priority from 'price' to 'quality'"
    - "Add constraint: quality >= 7"
When PlanningLayer.create_plan(task)
Then plan reflects adjustments:
  - plan.config.priority = "quality" (not "price")
  - plan.constraints includes "quality >= 7"
  And plan.metadata.applied_adjustments = [
      "reflection_id_123: priority=quality",
      "reflection_id_123: constraint quality>=7"
    ]
```

### Escenario 15: Evaluation with Missing Data

```gherkin
Given plan with success_criteria:
    - "Hotel has pool"
    - "Hotel quality >= 7"
  And execution_result:
    - hotel_selected = Hotel(quality=8)  # pool info missing
When EvaluationLayer.evaluate_result(plan, execution_result)
Then evaluation includes:
  - criteria_met: [
      {"criterion": "pool", "met": None, "reason": "data_missing"},
      {"criterion": "quality >= 7", "met": True, "actual": 8}
    ]
  - completeness_score: 0.5 (1 of 2 criteria verifiable)
  And evaluation.warnings = ["Cannot verify criterion: pool (missing data)"]
```

## Implementación

Archivo: `scripts/coding/ai/metacognition/planning_layer.py`

```python
class PlanningLayer:
    """
    RF-007: Planning Layer for metacognitive agents.
    Creates structured plans with success criteria.
    """

    def __init__(self, llm, memory_manager, cost_tracker):
        self.llm = llm
        self.memory = memory_manager
        self.cost_tracker = cost_tracker
        self.plan_cache = PlanCache()

    @enforce_metacognition_latency("create_plan")
    @with_timeout("create_plan")
    def create_plan(self, task: str, user_id: str) -> Plan:
        """
        RF-007: Create plan with desired result, steps, success criteria.

        Args:
            task: User task description
            user_id: User identifier

        Returns:
            Plan object with all required fields

        Raises:
            MetacognitionTimeoutError: If exceeds 5s
            MetacognitionCostExceeded: If would exceed budget
        """
        # Check budget (RT-009)
        estimated_cost = self._estimate_cost("create_plan")
        self.cost_tracker.check_budget_before_operation(
            "create_plan",
            estimated_cost
        )

        # Check cache (RF-007 Scenario 5)
        cached_plan = self.plan_cache.get_cached_plan(task)
        if cached_plan:
            logger.info(f"Plan cache hit: {task[:50]}")
            return cached_plan

        # Retrieve past experience (RF-007 Scenario 2)
        past_experience = self.retrieve_experience(task, user_id)

        # Analyze current context
        context = self._analyze_context(task, user_id)

        # Define desired result
        desired_result = self._define_desired_result(task, context)

        # Decompose into steps
        steps = self.decompose_task(task, desired_result, context)

        # Define success criteria
        success_criteria = self._define_success_criteria(
            task,
            desired_result,
            context
        )

        # Apply past learnings (RF-007 Scenario 14)
        if past_experience:
            steps = self._apply_learnings(steps, past_experience)

        # Create plan
        plan = Plan(
            task=task,
            desired_result=desired_result,
            steps=steps,
            success_criteria=success_criteria,
            metadata={
                "influenced_by_experience": len(past_experience) > 0,
                "past_learnings": [exp["content"] for exp in past_experience],
                "created_at": datetime.now().isoformat()
            }
        )

        # Cache plan
        self.plan_cache.cache_plan(task, plan)

        # Record cost
        actual_cost = self._calculate_cost(plan)
        self.cost_tracker.record_operation_cost("create_plan", actual_cost)

        return plan

    @enforce_metacognition_latency("decompose_task")
    def decompose_task(
        self,
        task: str,
        desired_result: Dict,
        context: Dict
    ) -> List[Step]:
        """
        RF-007: Decompose task into concrete steps.

        Returns:
            List of Step objects with dependencies
        """
        prompt = f"""
Decompose this task into concrete steps:

Task: {task}
Desired Result: {desired_result}
Context: {context}

For each step, specify:
- description: What to do
- expected_output: What this step should produce
- dependencies: Which prior steps must complete first

Return JSON list of steps.
"""
        response = self.llm.complete(prompt)
        steps_data = json.loads(response)

        steps = [
            Step(
                order=i + 1,
                description=s["description"],
                expected_output=s["expected_output"],
                dependencies=s.get("dependencies", [])
            )
            for i, s in enumerate(steps_data)
        ]

        return steps

    @enforce_metacognition_latency("retrieve_experience")
    def retrieve_experience(
        self,
        task: str,
        user_id: str
    ) -> List[Dict]:
        """
        RF-007: Retrieve relevant past experience from episodic memory.

        Args:
            task: Current task
            user_id: User identifier

        Returns:
            List of relevant episodic memories
        """
        # Determine task type
        task_type = self._classify_task_type(task)

        # Search episodic memory (RF-007 Scenario 13)
        relevant_memories = self.memory.retrieve(
            query=task,
            memory_types=[MemoryType.EPISODIC],
            user_id=user_id,
            filters={"task_type": task_type},
            top_k=5
        )

        return relevant_memories
```

Archivo: `scripts/coding/ai/metacognition/evaluation_layer.py`

```python
class EvaluationLayer:
    """
    RF-007: Evaluation Layer for assessing task results.
    Checks success criteria objectively.
    """

    def __init__(self, llm):
        self.llm = llm

    @enforce_metacognition_latency("evaluate_result")
    def evaluate_result(
        self,
        plan: Plan,
        execution_result: Dict
    ) -> Evaluation:
        """
        RF-007: Evaluate execution result against plan's success criteria.

        Args:
            plan: Original plan with success criteria
            execution_result: Actual result from execution

        Returns:
            Evaluation object with success, criteria_met, errors
        """
        # Check all criteria in parallel (RF-007 Scenario 10)
        tasks = [
            self.check_criterion(criterion, execution_result)
            for criterion in plan.success_criteria
        ]

        criteria_results = await asyncio.gather(*tasks)

        # Aggregate results
        success = all(r["met"] for r in criteria_results if r["met"] is not None)

        errors = [
            r["error"] for r in criteria_results
            if not r["met"] and r["met"] is not None
        ]

        warnings = [
            f"Cannot verify criterion: {r['criterion']} ({r['reason']})"
            for r in criteria_results
            if r["met"] is None
        ]

        # Assess relevance (RF-007 Scenario 9)
        relevancy_score = await self.assess_relevance(
            plan.task,
            execution_result
        )

        # Calculate completeness
        verifiable = sum(1 for r in criteria_results if r["met"] is not None)
        total = len(criteria_results)
        completeness_score = verifiable / total if total > 0 else 0

        return Evaluation(
            success=success,
            criteria_met=criteria_results,
            errors=errors,
            warnings=warnings,
            relevancy_score=relevancy_score,
            completeness_score=completeness_score
        )

    @enforce_metacognition_latency("check_criterion")
    async def check_criterion(
        self,
        criterion: str,
        execution_result: Dict
    ) -> Dict:
        """
        RF-007: Check if single criterion is met.

        Returns:
            {
                "criterion": str,
                "met": bool | None,
                "actual": Any,
                "expected": str,
                "explanation": str,
                "error": str | None,
                "reason": str | None
            }
        """
        # Parse criterion (e.g., "Hotel quality >= 7")
        parsed = self._parse_criterion(criterion)

        # Extract actual value from result
        try:
            actual_value = self._extract_value(
                execution_result,
                parsed["field"]
            )
        except KeyError:
            # Missing data (RF-007 Scenario 15)
            return {
                "criterion": criterion,
                "met": None,
                "reason": "data_missing",
                "explanation": f"Field '{parsed['field']}' not in result"
            }

        # Compare
        met = self._compare(
            actual_value,
            parsed["operator"],
            parsed["expected_value"]
        )

        return {
            "criterion": criterion,
            "met": met,
            "actual": actual_value,
            "expected": f"{parsed['operator']} {parsed['expected_value']}",
            "explanation": self._explain(met, actual_value, parsed),
            "error": None if met else f"{parsed['field']} {actual_value} does not meet {criterion}"
        }

    @enforce_metacognition_latency("assess_relevance")
    async def assess_relevance(
        self,
        task: str,
        execution_result: Dict
    ) -> float:
        """
        RF-007: Assess how relevant result is to task.

        Returns:
            Relevance score 0.0-1.0
        """
        # Embed task and result
        task_embedding = self._embed(task)
        result_embedding = self._embed(json.dumps(execution_result))

        # Cosine similarity
        similarity = cosine_similarity(task_embedding, result_embedding)

        # Also check completeness
        expected_fields = self._infer_expected_fields(task)
        present_fields = set(execution_result.keys())
        completeness = len(present_fields & expected_fields) / len(expected_fields)

        # Weighted average
        relevancy_score = 0.7 * similarity + 0.3 * completeness

        return relevancy_score
```

## Tests

Archivo: `scripts/coding/tests/ai/test_planning_evaluation.py`

```python
class TestPlanningLayer:
    def test_create_plan_with_desired_result(self):
        """RF-007 Scenario 1: Create plan with desired result."""
        planner = PlanningLayer(llm=mock_llm, memory=mock_memory, cost_tracker=mock_tracker)

        plan = planner.create_plan(task="Book hotel in Paris", user_id="user_123")

        assert plan is not None
        assert "desired_result" in plan.__dict__
        assert "User has: Confirmed hotel reservation" in plan.desired_result["user_has"]
        assert len(plan.steps) > 0
        assert len(plan.success_criteria) > 0

    def test_plan_with_past_experience(self):
        """RF-007 Scenario 2: Plan incorporates past experience."""
        mock_memory.add(
            content="User rejected cheap hotel (quality < 7)",
            memory_type=MemoryType.EPISODIC
        )

        planner = PlanningLayer(llm=mock_llm, memory=mock_memory, cost_tracker=mock_tracker)

        plan = planner.create_plan(task="Book hotel in Paris", user_id="user_123")

        assert plan.metadata["influenced_by_experience"] == True
        assert any("quality >= 7" in str(step) for step in plan.steps)

    def test_plan_cache_hit(self):
        """RF-007 Scenario 5: Plan cache hit."""
        planner = PlanningLayer(llm=mock_llm, memory=mock_memory, cost_tracker=mock_tracker)

        # First call - cache miss
        plan1 = planner.create_plan(task="Book hotel in Paris", user_id="user_123")

        # Second call - cache hit
        start = time.perf_counter()
        plan2 = planner.create_plan(task="Book hotel in Paris", user_id="user_123")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 500  # Faster than fresh generation
        assert plan2.task == plan1.task


class TestEvaluationLayer:
    def test_evaluate_result_success(self):
        """RF-007 Scenario 6: Evaluate result - success."""
        evaluator = EvaluationLayer(llm=mock_llm)

        plan = Plan(
            task="Book hotel",
            success_criteria=["Hotel quality >= 7", "Price <= 200", "User confirms"]
        )

        result = {
            "hotel": Hotel(quality=8, price=150),
            "user_feedback": "confirmed"
        }

        evaluation = evaluator.evaluate_result(plan, result)

        assert evaluation.success == True
        assert len(evaluation.criteria_met) == 3
        assert all(c["met"] for c in evaluation.criteria_met)

    def test_evaluate_result_failure(self):
        """RF-007 Scenario 7: Evaluate result - failure triggers reflection."""
        evaluator = EvaluationLayer(llm=mock_llm)

        plan = Plan(
            task="Book hotel",
            success_criteria=["Hotel quality >= 7", "User confirms"]
        )

        result = {
            "hotel": Hotel(quality=5, price=80),
            "user_feedback": "rejected - too low quality"
        }

        evaluation = evaluator.evaluate_result(plan, result)

        assert evaluation.success == False
        assert "Quality below threshold" in evaluation.errors[0]
        assert evaluation.relevancy_score < 0.5

    def test_assess_relevance_score(self):
        """RF-007 Scenario 9: Assess relevance score."""
        evaluator = EvaluationLayer(llm=mock_llm)

        task = "Find romantic restaurant in Paris"
        result = {
            "restaurant": "Le Chat Noir",
            "cuisine": "French",
            "ambiance": "romantic",
            "price": "$$"
        }

        relevancy = evaluator.assess_relevance(task, result)

        assert relevancy >= 0.8
        assert relevancy <= 1.0
```

Resultado esperado: `12 passed in 0.25s`

## Métricas

- Planning latency p95: < 2s
- Evaluation latency p95: < 500ms
- Plan cache hit rate: > 40%
- Success criteria accuracy: > 90%
- Relevance score accuracy: > 85%

## Referencias

- UC-SYS-004: Metacognitive Agent Operations
- ADR-052: Metacognition Architecture
- RT-009: Metacognition Performance Constraints

---

**Requisito**: Planning Layer crea planes estructurados, Evaluation Layer evalúa resultados objetivamente.
**Verificación**: Gherkin scenarios + TDD tests.
