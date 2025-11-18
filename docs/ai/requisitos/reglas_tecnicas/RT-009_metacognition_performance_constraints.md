---
id: RT-009
tipo: regla_tecnica
relacionado: [ADR-052, RF-007, RF-008]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RT-009: Metacognition Performance Constraints

## Propósito

Definir constraints de performance para operaciones metacognitivas (Planning, Evaluation, Reflection) para garantizar que el overhead de metacognición no degrade user experience.

## Reglas Técnicas

### 1. Latency Targets por Layer

```python
METACOGNITION_LATENCY_TARGETS = {
    # Planning Layer
    "create_plan": 2000,           # < 2s para crear plan completo
    "decompose_task": 1000,        # < 1s para descomponer en steps
    "retrieve_experience": 100,    # < 100ms para buscar episodic memory

    # Evaluation Layer
    "evaluate_result": 500,        # < 500ms para evaluar resultado
    "check_criteria": 200,         # < 200ms para verificar criterios
    "assess_relevance": 300,       # < 300ms para calcular relevancy score

    # Reflection Layer
    "reflect_on_result": 3000,     # < 3s para reflexión completa
    "analyze_cause": 1500,         # < 1.5s para analizar causas
    "identify_patterns": 1000,     # < 1s para identificar patterns
    "decide_adjustments": 1000,    # < 1s para decidir adjustments

    # Corrective RAG
    "corrective_rag_cycle": 5000,  # < 5s para ciclo completo
    "relevance_grading": 500,      # < 500ms para grading
    "knowledge_refinement": 2000,  # < 2s para refinement

    # LLM Re-ranking
    "rerank_results": 800,         # < 800ms para re-ranking
}
```

**Enforcement**:
```python
import functools
import time
from typing import Callable, Any

def enforce_metacognition_latency(operation: str):
    """Decorator para enforce latency targets."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()

            try:
                result = func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                target_ms = METACOGNITION_LATENCY_TARGETS[operation]

                if elapsed_ms > target_ms:
                    logger.warning(
                        f"Metacognition latency violation: {operation} "
                        f"took {elapsed_ms:.2f}ms (target: {target_ms}ms)"
                    )

                metrics.record_latency(
                    operation=f"metacognition.{operation}",
                    latency_ms=elapsed_ms,
                    target_ms=target_ms
                )

            return result
        return wrapper
    return decorator


# Usage
class PlanningLayer:
    @enforce_metacognition_latency("create_plan")
    def create_plan(self, task: str) -> Plan:
        """RT-009: Must complete in < 2s."""
        # ... implementation
```

### 2. Timeout Enforcement

```python
METACOGNITION_TIMEOUTS = {
    # Hard timeouts (operation must abort)
    "create_plan": 5000,           # Abort if > 5s
    "evaluate_result": 2000,       # Abort if > 2s
    "reflect_on_result": 10000,    # Abort if > 10s
    "corrective_rag_cycle": 15000, # Abort if > 15s
}

def with_timeout(operation: str):
    """Decorator para hard timeout enforcement."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            timeout_ms = METACOGNITION_TIMEOUTS[operation]

            # Use threading.Timer or asyncio.wait_for
            try:
                result = asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_ms / 1000
                )
                return result
            except asyncio.TimeoutError:
                logger.error(
                    f"Metacognition timeout: {operation} "
                    f"exceeded {timeout_ms}ms hard limit"
                )
                raise MetacognitionTimeoutError(
                    f"{operation} exceeded timeout: {timeout_ms}ms"
                )
        return wrapper
    return decorator
```

### 3. Memory Storage Constraints

Metacognición genera memories (episodic, learnings). Debe respetar quotas.

```python
METACOGNITION_STORAGE_LIMITS = {
    # Episodic Memory (stored reflections)
    "max_episodic_memories_per_user": 5000,
    "max_episodic_memory_size_mb": 50,

    # Pattern Storage (identified patterns)
    "max_patterns_per_domain": 500,
    "max_pattern_size_bytes": 2048,  # 2 KB per pattern

    # Strategy Adjustments (stored adjustments)
    "max_adjustments_per_agent": 1000,
    "max_adjustment_history_days": 90,

    # Reflection Cache (recent reflections)
    "max_cached_reflections": 100,
    "cache_ttl_seconds": 3600,  # 1 hour
}

def check_metacognition_storage(memory_type: str, user_id: str):
    """RT-009: Enforce storage limits for metacognition memories."""
    current_count = get_memory_count(user_id, memory_type)
    max_count = METACOGNITION_STORAGE_LIMITS[f"max_{memory_type}_per_user"]

    if current_count >= max_count:
        raise MetacognitionStorageQuotaExceeded(
            f"User {user_id} exceeded {memory_type} quota: "
            f"{current_count}/{max_count}"
        )
```

### 4. Cost Budgets

Metacognición usa LLM calls (Planning, Reflection). Debe tener cost budgets.

```python
METACOGNITION_COST_BUDGETS = {
    # Per-operation cost limits (USD)
    "create_plan": 0.01,           # Max $0.01 per plan
    "evaluate_result": 0.005,      # Max $0.005 per evaluation
    "reflect_on_result": 0.02,     # Max $0.02 per reflection
    "corrective_rag_cycle": 0.03,  # Max $0.03 per cycle

    # Per-user daily limits
    "max_daily_metacognition_cost_usd": 5.0,  # Max $5/day per user

    # Per-agent limits
    "max_monthly_metacognition_cost_usd": 100.0,  # Max $100/month per agent
}

class MetacognitionCostTracker:
    """RT-009: Track and enforce cost budgets."""

    def __init__(self, user_id: str, agent_id: str):
        self.user_id = user_id
        self.agent_id = agent_id
        self.daily_cost = self._get_daily_cost()

    def check_budget_before_operation(self, operation: str, estimated_cost: float):
        """Check if operation within budget."""
        operation_budget = METACOGNITION_COST_BUDGETS[operation]

        if estimated_cost > operation_budget:
            raise MetacognitionCostExceeded(
                f"{operation} estimated cost ${estimated_cost:.4f} "
                f"exceeds budget ${operation_budget}"
            )

        # Check daily limit
        if self.daily_cost + estimated_cost > METACOGNITION_COST_BUDGETS["max_daily_metacognition_cost_usd"]:
            raise DailyMetacognitionBudgetExceeded(
                f"User {self.user_id} would exceed daily budget: "
                f"${self.daily_cost + estimated_cost:.2f} > "
                f"${METACOGNITION_COST_BUDGETS['max_daily_metacognition_cost_usd']}"
            )

    def record_operation_cost(self, operation: str, actual_cost: float):
        """Record actual cost after operation."""
        self.daily_cost += actual_cost

        metrics.record_cost(
            operation=f"metacognition.{operation}",
            cost_usd=actual_cost,
            user_id=self.user_id
        )
```

### 5. Parallel vs Sequential Execution

```python
METACOGNITION_EXECUTION_RULES = {
    # Operations that MUST run sequentially
    "sequential": [
        ("create_plan", "execute_plan", "evaluate_result", "reflect_on_result"),
    ],

    # Operations that CAN run in parallel
    "parallel": {
        "during_planning": [
            "retrieve_experience",  # Parallel: get episodic memory
            "analyze_context",      # Parallel: analyze current context
        ],
        "during_evaluation": [
            "check_criteria",       # Parallel: check multiple criteria
            "assess_relevance",     # Parallel: calculate relevance score
        ],
        "during_reflection": [
            "analyze_cause",        # Parallel: analyze root cause
            "identify_patterns",    # Parallel: pattern matching
        ]
    }
}

# Example: Planning with parallel retrieval
async def create_plan_with_context(task: str) -> Plan:
    """RT-009: Parallelize independent operations."""

    # Run in parallel
    experience, context = await asyncio.gather(
        retrieve_experience(task),  # Episodic memory search
        analyze_context(task)       # Context analysis
    )

    # Then sequential planning
    plan = decompose_task(task, experience, context)
    return plan
```

### 6. Caching Strategies

```python
METACOGNITION_CACHE_CONFIG = {
    # Plan caching (reuse plans for similar tasks)
    "plan_cache": {
        "enabled": True,
        "ttl_seconds": 3600,      # 1 hour
        "max_entries": 1000,
        "similarity_threshold": 0.85  # Cosine similarity
    },

    # Reflection caching (avoid re-reflecting on same error)
    "reflection_cache": {
        "enabled": True,
        "ttl_seconds": 7200,      # 2 hours
        "max_entries": 500,
    },

    # Pattern caching (frequently used patterns)
    "pattern_cache": {
        "enabled": True,
        "ttl_seconds": 86400,     # 24 hours
        "max_entries": 2000,
    }
}

class PlanCache:
    """RT-009: Cache plans to reduce latency and cost."""

    def __init__(self):
        self.cache = {}
        self.embeddings = {}

    def get_cached_plan(self, task: str) -> Optional[Plan]:
        """Check if similar task has cached plan."""
        task_embedding = embed_text(task)

        # Find similar cached plans
        for cached_task, cached_plan in self.cache.items():
            cached_embedding = self.embeddings[cached_task]
            similarity = cosine_similarity(task_embedding, cached_embedding)

            if similarity >= METACOGNITION_CACHE_CONFIG["plan_cache"]["similarity_threshold"]:
                logger.info(
                    f"Plan cache hit: {task[:50]} (similarity: {similarity:.2f})"
                )
                metrics.increment("metacognition.plan_cache.hit")
                return cached_plan

        metrics.increment("metacognition.plan_cache.miss")
        return None

    def cache_plan(self, task: str, plan: Plan):
        """Cache plan for future reuse."""
        self.cache[task] = plan
        self.embeddings[task] = embed_text(task)
```

### 7. Degradation Strategy

Si metacognición excede latency/cost, debe degradar gracefully.

```python
METACOGNITION_DEGRADATION_STRATEGY = {
    # Level 0: Full metacognition (normal)
    "full": {
        "planning": True,
        "evaluation": True,
        "reflection": True,
        "corrective_rag": True,
        "llm_rerank": True,
    },

    # Level 1: Skip expensive operations
    "reduced": {
        "planning": True,
        "evaluation": True,
        "reflection": False,      # Skip reflection (most expensive)
        "corrective_rag": True,
        "llm_rerank": False,      # Skip re-ranking
    },

    # Level 2: Minimal metacognition
    "minimal": {
        "planning": True,          # Keep planning
        "evaluation": True,        # Keep evaluation
        "reflection": False,
        "corrective_rag": False,
        "llm_rerank": False,
    },

    # Level 3: Disabled (fallback to non-metacognitive)
    "disabled": {
        "planning": False,
        "evaluation": False,
        "reflection": False,
        "corrective_rag": False,
        "llm_rerank": False,
    }
}

class MetacognitiveDegradationManager:
    """RT-009: Degrade metacognition when exceeding constraints."""

    def __init__(self):
        self.current_level = "full"
        self.violation_count = 0

    def on_latency_violation(self, operation: str, elapsed_ms: float):
        """Adjust degradation level on violations."""
        self.violation_count += 1

        # Degradation thresholds
        if self.violation_count > 10:
            self.current_level = "reduced"
            logger.warning("Metacognition degraded to 'reduced' level")

        if self.violation_count > 25:
            self.current_level = "minimal"
            logger.warning("Metacognition degraded to 'minimal' level")

        if self.violation_count > 50:
            self.current_level = "disabled"
            logger.error("Metacognition disabled due to repeated violations")

    def should_execute(self, operation: str) -> bool:
        """RT-009: Check if operation should execute at current level."""
        strategy = METACOGNITION_DEGRADATION_STRATEGY[self.current_level]
        return strategy.get(operation, False)
```

## Métricas de Performance

```python
# Métricas requeridas
REQUIRED_METRICS = [
    "metacognition.planning.latency_p50",
    "metacognition.planning.latency_p95",
    "metacognition.planning.latency_p99",

    "metacognition.evaluation.latency_p50",
    "metacognition.evaluation.latency_p95",

    "metacognition.reflection.latency_p50",
    "metacognition.reflection.latency_p95",

    "metacognition.cost_per_operation_usd",
    "metacognition.daily_cost_per_user_usd",

    "metacognition.cache_hit_rate",
    "metacognition.degradation_level",

    "metacognition.timeout_errors_count",
    "metacognition.quota_exceeded_count",
]
```

## Targets de Performance

| Metric                          | Target         | Alert Threshold |
| ------------------------------- | -------------- | --------------- |
| Planning latency p95            | < 2s           | > 3s            |
| Evaluation latency p95          | < 500ms        | > 1s            |
| Reflection latency p95          | < 3s           | > 5s            |
| Cost per reflection             | < $0.02        | > $0.05         |
| Daily cost per user             | < $5           | > $7            |
| Cache hit rate (plans)          | > 40%          | < 20%           |
| Timeout error rate              | < 1%           | > 5%            |

## Excepciones

```python
class MetacognitionPerformanceError(Exception):
    """Base exception for metacognition performance issues."""
    pass

class MetacognitionTimeoutError(MetacognitionPerformanceError):
    """Operation exceeded hard timeout."""
    pass

class MetacognitionCostExceeded(MetacognitionPerformanceError):
    """Operation would exceed cost budget."""
    pass

class DailyMetacognitionBudgetExceeded(MetacognitionPerformanceError):
    """User exceeded daily metacognition budget."""
    pass

class MetacognitionStorageQuotaExceeded(MetacognitionPerformanceError):
    """Exceeded storage quota for metacognition memories."""
    pass
```

## Cumplimiento

- Planning layer DEBE completar en < 2s (p95)
- Evaluation layer DEBE completar en < 500ms (p95)
- Reflection layer DEBE completar en < 3s (p95)
- Sistema DEBE enforce hard timeouts
- Sistema DEBE respetar cost budgets
- Sistema DEBE degradar gracefully cuando exceda constraints
- Sistema DEBE cachear plans/reflections para reduce latency

## Referencias

- ADR-052: Metacognition Architecture for AI Agents
- RT-004: Memory Performance Constraints
- RT-007: Context Window Limits

---

**Regla**: Metacognición debe tener performance predecible y cost-effective.
**Enforcement**: Decorators, timeouts, budgets, degradation strategy.
