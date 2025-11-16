---
id: RT-010
tipo: regla_tecnica
relacionado: [ADR-052, RT-009, RF-008]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RT-010: Reflection Quality Standards

## Propósito

Definir estándares de calidad para outputs metacognitivos (reflections, patterns, strategy adjustments) para garantizar que el agente mejora realmente de sus experiencias.

## Reglas Técnicas

### 1. Reflection Quality Metrics

```python
REFLECTION_QUALITY_METRICS = {
    # 1. Depth Score: ¿Qué tan profunda es la reflexión?
    "depth_score": {
        "min_threshold": 0.7,
        "description": "Measure of analysis depth (0-1)",
        "criteria": {
            "surface": 0.3,    # "It failed" (no analysis)
            "shallow": 0.5,    # "Wrong hotel selected" (what)
            "medium": 0.7,     # "Selected cheap hotel, user wanted quality" (why)
            "deep": 0.9,       # "Budget-first strategy conflicts with user preference" (root cause)
        }
    },

    # 2. Actionability Score: ¿Genera acciones concretas?
    "actionability_score": {
        "min_threshold": 0.8,
        "description": "Does reflection produce concrete adjustments?",
        "criteria": {
            "none": 0.0,       # No adjustments suggested
            "vague": 0.4,      # "Do better next time"
            "specific": 0.8,   # "Change priority from price to quality"
            "executable": 1.0, # "Add constraint: quality >= 7"
        }
    },

    # 3. Pattern Validity: ¿Los patterns son correctos?
    "pattern_validity": {
        "min_threshold": 0.75,
        "description": "Are identified patterns statistically valid?",
        "criteria": {
            "min_occurrences": 3,        # Pattern must occur >= 3 times
            "min_confidence": 0.75,      # Statistical confidence >= 75%
            "max_false_positives": 0.1,  # < 10% false positives
        }
    },

    # 4. Relevance Score: ¿Relevante al task actual?
    "relevance_score": {
        "min_threshold": 0.6,
        "description": "Is reflection relevant to current task?",
        "calculation": "cosine_similarity(reflection_embedding, task_embedding)"
    },

    # 5. Novelty Score: ¿Aporta algo nuevo?
    "novelty_score": {
        "min_threshold": 0.3,
        "description": "Does reflection provide new insight?",
        "calculation": "1 - max_similarity_to_existing_reflections"
    },

    # 6. Completeness: ¿Cubre todos los campos requeridos?
    "completeness": {
        "min_threshold": 0.9,
        "required_fields": [
            "analysis",           # Root cause analysis
            "patterns_identified", # List of patterns
            "strategy_adjustments", # Concrete adjustments
            "learning",           # What was learned
        ]
    }
}
```

### 2. Quality Validation Pipeline

```python
class ReflectionQualityValidator:
    """RT-010: Validate reflection quality before storage."""

    def __init__(self):
        self.depth_analyzer = DepthAnalyzer()
        self.actionability_checker = ActionabilityChecker()
        self.pattern_validator = PatternValidator()

    def validate_reflection(self, reflection: Reflection) -> ValidationResult:
        """
        RT-010: Validate reflection against quality standards.

        Returns:
            ValidationResult(
                is_valid: bool,
                quality_score: float,
                violations: List[str],
                metrics: Dict[str, float]
            )
        """
        violations = []
        metrics = {}

        # 1. Check completeness
        completeness = self._check_completeness(reflection)
        metrics["completeness"] = completeness

        if completeness < REFLECTION_QUALITY_METRICS["completeness"]["min_threshold"]:
            violations.append(
                f"Incomplete reflection: {completeness:.2f} < 0.9. "
                f"Missing fields: {self._get_missing_fields(reflection)}"
            )

        # 2. Assess depth
        depth_score = self.depth_analyzer.assess_depth(reflection.analysis)
        metrics["depth_score"] = depth_score

        if depth_score < REFLECTION_QUALITY_METRICS["depth_score"]["min_threshold"]:
            violations.append(
                f"Shallow reflection: depth={depth_score:.2f} < 0.7. "
                f"Need root cause analysis, not just symptoms."
            )

        # 3. Check actionability
        actionability = self.actionability_checker.score(
            reflection.strategy_adjustments
        )
        metrics["actionability_score"] = actionability

        if actionability < REFLECTION_QUALITY_METRICS["actionability_score"]["min_threshold"]:
            violations.append(
                f"Not actionable: {actionability:.2f} < 0.8. "
                f"Adjustments must be concrete and executable."
            )

        # 4. Validate patterns
        for pattern in reflection.patterns_identified:
            pattern_validity = self.pattern_validator.validate(pattern)
            if pattern_validity < REFLECTION_QUALITY_METRICS["pattern_validity"]["min_threshold"]:
                violations.append(
                    f"Invalid pattern '{pattern}': confidence={pattern_validity:.2f} < 0.75"
                )

        # 5. Calculate overall quality score
        quality_score = self._calculate_quality_score(metrics)

        return ValidationResult(
            is_valid=len(violations) == 0,
            quality_score=quality_score,
            violations=violations,
            metrics=metrics
        )

    def _check_completeness(self, reflection: Reflection) -> float:
        """Check if all required fields are present and non-empty."""
        required = REFLECTION_QUALITY_METRICS["completeness"]["required_fields"]
        present = 0

        for field in required:
            value = getattr(reflection, field, None)
            if value and (isinstance(value, str) and len(value) > 10 or
                          isinstance(value, list) and len(value) > 0):
                present += 1

        return present / len(required)

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Weighted average of quality metrics."""
        weights = {
            "completeness": 0.2,
            "depth_score": 0.3,
            "actionability_score": 0.3,
            "relevance_score": 0.1,
            "novelty_score": 0.1,
        }

        score = sum(
            metrics.get(metric, 0) * weight
            for metric, weight in weights.items()
        )

        return score
```

### 3. Depth Analysis

```python
class DepthAnalyzer:
    """RT-010: Analyze depth of reflection."""

    DEPTH_INDICATORS = {
        # Surface level (0.0-0.3)
        "surface": [
            "it failed", "it didn't work", "error occurred",
            "task unsuccessful"
        ],

        # Shallow level (0.4-0.6) - describes WHAT happened
        "shallow": [
            "wrong result", "incorrect output", "selected wrong",
            "chose bad option"
        ],

        # Medium level (0.7-0.8) - describes WHY it happened
        "medium": [
            "because", "due to", "caused by", "resulted from",
            "prioritized", "assumed", "overlooked"
        ],

        # Deep level (0.9-1.0) - identifies ROOT CAUSE and strategy flaw
        "deep": [
            "strategy", "approach", "methodology", "reasoning",
            "conflicting", "contradictory", "fundamental flaw",
            "incorrect assumption", "systematic error"
        ]
    }

    def assess_depth(self, analysis: str) -> float:
        """
        RT-010: Assess depth of root cause analysis.

        Returns score 0.0-1.0 based on depth indicators.
        """
        analysis_lower = analysis.lower()

        # Count indicators at each depth
        depth_counts = {
            level: sum(1 for indicator in indicators if indicator in analysis_lower)
            for level, indicators in self.DEPTH_INDICATORS.items()
        }

        # Calculate weighted score
        if depth_counts["deep"] >= 2:
            base_score = 0.9
        elif depth_counts["medium"] >= 2:
            base_score = 0.7
        elif depth_counts["shallow"] >= 1:
            base_score = 0.5
        else:
            base_score = 0.3

        # Bonus for length (deeper analysis tends to be longer)
        length_bonus = min(0.1, len(analysis) / 5000)  # Max +0.1

        # Penalty if too short
        if len(analysis) < 50:
            return 0.2

        return min(1.0, base_score + length_bonus)
```

### 4. Actionability Checking

```python
class ActionabilityChecker:
    """RT-010: Check if adjustments are concrete and executable."""

    ACTIONABLE_PATTERNS = [
        r"change .+ to .+",           # "change from X to Y"
        r"add constraint: .+",        # "add constraint: quality >= 7"
        r"set .+ = .+",               # "set priority = quality"
        r"increase .+ by .+",         # "increase threshold by 0.1"
        r"decrease .+ from .+ to .+", # "decrease weight from 0.8 to 0.5"
        r"remove .+",                 # "remove budget-first strategy"
        r"filter .+ where .+",        # "filter results where score < 0.7"
    ]

    VAGUE_PATTERNS = [
        r"do better",
        r"improve",
        r"try harder",
        r"be more careful",
        r"pay attention",
    ]

    def score(self, adjustments: List[str]) -> float:
        """
        RT-010: Score actionability of strategy adjustments.

        Returns:
            0.0: No adjustments
            0.4: Vague adjustments
            0.8: Specific adjustments
            1.0: Fully executable adjustments
        """
        if not adjustments:
            return 0.0

        import re

        actionable_count = 0
        vague_count = 0

        for adjustment in adjustments:
            # Check for actionable patterns
            if any(re.search(pattern, adjustment.lower()) for pattern in self.ACTIONABLE_PATTERNS):
                actionable_count += 1
            # Check for vague patterns
            elif any(re.search(pattern, adjustment.lower()) for pattern in self.VAGUE_PATTERNS):
                vague_count += 1

        total = len(adjustments)

        # All actionable = 1.0
        if actionable_count == total:
            return 1.0

        # Mix of actionable and vague = 0.8
        if actionable_count >= total * 0.8:
            return 0.8

        # Mostly vague = 0.4
        if vague_count >= total * 0.5:
            return 0.4

        # Some actionable = 0.6
        return 0.6
```

### 5. Pattern Validation

```python
class PatternValidator:
    """RT-010: Validate identified patterns statistically."""

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def validate(self, pattern: str, user_id: str) -> float:
        """
        RT-010: Validate pattern against historical data.

        Returns confidence score 0.0-1.0.
        """
        # Retrieve episodic memories matching pattern
        episodes = self.memory.retrieve(
            query=pattern,
            memory_types=[MemoryType.EPISODIC],
            user_id=user_id,
            top_k=50
        )

        # Count occurrences
        occurrences = self._count_pattern_occurrences(pattern, episodes)

        min_occurrences = REFLECTION_QUALITY_METRICS["pattern_validity"]["criteria"]["min_occurrences"]

        if occurrences < min_occurrences:
            return 0.0  # Insufficient data

        # Calculate statistical confidence
        total_episodes = len(episodes)
        confidence = occurrences / total_episodes

        return confidence

    def _count_pattern_occurrences(self, pattern: str, episodes: List[Dict]) -> int:
        """Count how many episodes match the pattern."""
        # Use LLM to assess if episode matches pattern
        count = 0

        for episode in episodes:
            if self._episode_matches_pattern(episode["content"], pattern):
                count += 1

        return count

    def _episode_matches_pattern(self, episode_content: str, pattern: str) -> bool:
        """Use LLM to assess if episode matches pattern."""
        # Could use embedding similarity or LLM call
        # For now, simple keyword matching
        pattern_keywords = pattern.lower().split()
        episode_lower = episode_content.lower()

        matches = sum(1 for kw in pattern_keywords if kw in episode_lower)
        return matches >= len(pattern_keywords) * 0.7  # 70% keywords must match
```

### 6. Quality Enforcement

```python
class ReflectionQualityEnforcer:
    """RT-010: Enforce quality standards, reject low-quality reflections."""

    def __init__(self):
        self.validator = ReflectionQualityValidator()
        self.rejection_count = 0

    def enforce_quality(self, reflection: Reflection) -> Tuple[bool, str]:
        """
        RT-010: Validate and optionally reject reflection.

        Returns:
            (is_accepted, reason)
        """
        validation = self.validator.validate_reflection(reflection)

        # Accept if valid
        if validation.is_valid:
            logger.info(
                f"Reflection accepted: quality_score={validation.quality_score:.2f}"
            )
            return True, "Accepted"

        # Reject if quality too low
        if validation.quality_score < 0.5:
            self.rejection_count += 1
            logger.warning(
                f"Reflection REJECTED: quality_score={validation.quality_score:.2f}. "
                f"Violations: {validation.violations}"
            )

            metrics.increment("metacognition.reflection.rejected")

            return False, f"Quality too low: {', '.join(validation.violations)}"

        # Accept with warning if moderate quality
        logger.warning(
            f"Reflection accepted WITH WARNINGS: quality_score={validation.quality_score:.2f}. "
            f"Issues: {validation.violations}"
        )

        metrics.increment("metacognition.reflection.accepted_with_warnings")

        return True, f"Accepted with warnings: {', '.join(validation.violations)}"
```

### 7. Reflection Improvement Loop

Si reflection es rechazada, re-generar con prompt mejorado.

```python
class ReflectionImprovementLoop:
    """RT-010: Iteratively improve reflection quality."""

    MAX_ITERATIONS = 3

    def __init__(self, llm, validator):
        self.llm = llm
        self.validator = validator

    def generate_quality_reflection(
        self,
        plan: Plan,
        evaluation: Evaluation,
        max_attempts: int = None
    ) -> Reflection:
        """
        RT-010: Generate reflection, iteratively improve if needed.

        Args:
            plan: Original plan
            evaluation: Evaluation result
            max_attempts: Max improvement iterations (default: 3)

        Returns:
            High-quality reflection
        """
        max_attempts = max_attempts or self.MAX_ITERATIONS

        for attempt in range(1, max_attempts + 1):
            # Generate reflection
            reflection = self._generate_reflection(plan, evaluation, attempt)

            # Validate
            validation = self.validator.validate_reflection(reflection)

            if validation.is_valid:
                logger.info(
                    f"Quality reflection generated (attempt {attempt}): "
                    f"score={validation.quality_score:.2f}"
                )
                return reflection

            # Not valid - improve prompt
            logger.warning(
                f"Attempt {attempt} failed validation: "
                f"score={validation.quality_score:.2f}. "
                f"Violations: {validation.violations}"
            )

            # If last attempt, return best effort
            if attempt == max_attempts:
                logger.error(
                    f"Failed to generate quality reflection after {max_attempts} attempts. "
                    f"Returning best effort."
                )
                return reflection

        # Should not reach here
        raise ReflectionQualityError("Failed to generate reflection")

    def _generate_reflection(
        self,
        plan: Plan,
        evaluation: Evaluation,
        attempt: int
    ) -> Reflection:
        """Generate reflection with improved prompt on retry."""

        if attempt == 1:
            # First attempt - standard prompt
            prompt = self._create_standard_prompt(plan, evaluation)
        else:
            # Retry - enhanced prompt with quality guidance
            prompt = self._create_enhanced_prompt(plan, evaluation, attempt)

        response = self.llm.complete(prompt)
        reflection = parse_reflection(response)

        return reflection

    def _create_enhanced_prompt(
        self,
        plan: Plan,
        evaluation: Evaluation,
        attempt: int
    ) -> str:
        """Create prompt with explicit quality guidance."""

        return f"""
Reflect on this task result. Your reflection MUST meet quality standards:

Plan:
{plan}

Evaluation:
{evaluation}

QUALITY REQUIREMENTS (Attempt {attempt}/{self.MAX_ITERATIONS}):

1. DEPTH: Identify ROOT CAUSE, not just symptoms
   - BAD: "It failed because wrong hotel selected"
   - GOOD: "My budget-first strategy conflicts with user's quality preference"

2. ACTIONABILITY: Provide CONCRETE, EXECUTABLE adjustments
   - BAD: "Do better next time"
   - GOOD: "Add constraint: quality >= 7 in hotel search"

3. PATTERNS: Only identify patterns with >= 3 occurrences
   - Include statistical evidence for patterns

4. COMPLETENESS: Include all required fields:
   - analysis: Root cause analysis (min 100 chars)
   - patterns_identified: List of validated patterns
   - strategy_adjustments: List of concrete adjustments
   - learning: What was learned for future (min 50 chars)

Return JSON with these exact fields.
"""
```

### 8. Quality Metrics Collection

```python
# Métricas requeridas
REQUIRED_QUALITY_METRICS = [
    "metacognition.reflection.quality_score_avg",
    "metacognition.reflection.quality_score_p50",
    "metacognition.reflection.quality_score_p95",

    "metacognition.reflection.depth_score_avg",
    "metacognition.reflection.actionability_score_avg",
    "metacognition.reflection.completeness_avg",

    "metacognition.reflection.rejected_count",
    "metacognition.reflection.accepted_with_warnings_count",

    "metacognition.pattern.invalid_count",
    "metacognition.pattern.validity_avg",

    "metacognition.improvement_loop.iterations_avg",
    "metacognition.improvement_loop.success_rate",
]
```

## Quality Targets

| Metric                          | Target         | Alert Threshold |
| ------------------------------- | -------------- | --------------- |
| Reflection quality score avg    | > 0.8          | < 0.6           |
| Depth score avg                 | > 0.7          | < 0.5           |
| Actionability score avg         | > 0.8          | < 0.6           |
| Completeness avg                | > 0.9          | < 0.7           |
| Rejection rate                  | < 5%           | > 15%           |
| Pattern validity avg            | > 0.75         | < 0.5           |
| Improvement loop success rate   | > 95%          | < 80%           |

## Excepciones

```python
class ReflectionQualityError(Exception):
    """Base exception for reflection quality issues."""
    pass

class InsufficientDepthError(ReflectionQualityError):
    """Reflection lacks depth (no root cause analysis)."""
    pass

class NotActionableError(ReflectionQualityError):
    """Strategy adjustments are vague, not executable."""
    pass

class InvalidPatternError(ReflectionQualityError):
    """Identified pattern lacks statistical validity."""
    pass

class IncompleteReflectionError(ReflectionQualityError):
    """Reflection missing required fields."""
    pass
```

## Cumplimiento

- Reflection DEBE tener quality_score >= 0.8 para storage
- Reflection DEBE incluir root cause analysis (depth >= 0.7)
- Strategy adjustments DEBEN ser concrete y executable (actionability >= 0.8)
- Patterns DEBEN tener >= 3 occurrences para validity
- Sistema DEBE reject reflections con quality < 0.5
- Sistema DEBE iterar hasta MAX_ITERATIONS para mejorar quality

## Referencias

- ADR-052: Metacognition Architecture for AI Agents
- RT-009: Metacognition Performance Constraints
- RT-008: Context Quality Standards

---

**Regla**: Reflections deben ser deep, actionable, y statistically valid.
**Enforcement**: Quality validation pipeline + improvement loop.
