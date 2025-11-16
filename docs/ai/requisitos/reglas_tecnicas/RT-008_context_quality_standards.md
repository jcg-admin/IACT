---
id: RT-008
tipo: regla_tecnica
relacionado: [ADR-050, ADR-051]
fecha: 2025-11-16
---

# RT-008: Context Quality Standards

## Constraint

El sistema DEBE mantener estándares de calidad de contexto para prevenir context failures y asegurar reliability.

## Quality Metrics

```python
QUALITY_METRICS = {
    "relevance_score": {
        "min_threshold": 0.7,      # 70% relevance mínima
        "measurement": "semantic_similarity"
    },
    "freshness": {
        "max_age_seconds": 3600,   # Info no más vieja de 1 hora
        "measurement": "timestamp_delta"
    },
    "accuracy": {
        "min_validation_score": 0.9,  # 90% accuracy
        "measurement": "cross_reference_validation"
    },
    "completeness": {
        "min_fields_present": 0.8,  # 80% campos requeridos
        "measurement": "field_coverage"
    },
    "consistency": {
        "max_contradictions": 0,    # Cero contradicciones
        "measurement": "conflict_detection"
    }
}
```

## Quality Checks

### 1. Relevance Validation

**Check before adding to context**:

```python
class RelevanceValidator:
    def validate_relevance(self, content: str, query: str) -> bool:
        """
        RT-008: Validate content relevance before adding to context.

        Args:
            content: Content to add
            query: Current user query or task

        Returns:
            True if relevance score >= threshold
        """
        # Semantic similarity
        content_emb = self.embed(content)
        query_emb = self.embed(query)

        relevance_score = cosine_similarity(content_emb, query_emb)

        threshold = QUALITY_METRICS["relevance_score"]["min_threshold"]

        if relevance_score < threshold:
            logger.warning(
                f"Low relevance: {relevance_score:.2f} < {threshold}. "
                f"Content not added to context."
            )
            return False

        return True
```

### 2. Freshness Check

**Ensure information is up-to-date**:

```python
class FreshnessValidator:
    def validate_freshness(self, content: Dict) -> bool:
        """
        RT-008: Check if content is fresh enough.

        Args:
            content: Dict with 'timestamp' field

        Returns:
            True if content is within freshness threshold
        """
        if "timestamp" not in content:
            logger.warning("Content missing timestamp, assuming stale")
            return False

        age_seconds = time.time() - content["timestamp"]
        max_age = QUALITY_METRICS["freshness"]["max_age_seconds"]

        if age_seconds > max_age:
            logger.warning(
                f"Stale content: {age_seconds}s old (max: {max_age}s)"
            )
            return False

        return True
```

### 3. Accuracy Validation

**Cross-reference with reliable sources**:

```python
class AccuracyValidator:
    def validate_accuracy(self, claim: str) -> bool:
        """
        RT-008: Validate accuracy via cross-referencing.

        Args:
            claim: Factual claim to validate

        Returns:
            True if claim is accurate (>= 90% confidence)
        """
        # Cross-reference with multiple sources
        sources = self.get_reliable_sources()
        validations = []

        for source in sources:
            is_valid = self.check_against_source(claim, source)
            validations.append(is_valid)

        # Calculate validation score
        validation_score = sum(validations) / len(validations)

        threshold = QUALITY_METRICS["accuracy"]["min_validation_score"]

        if validation_score < threshold:
            logger.warning(
                f"Low accuracy: {validation_score:.2f} < {threshold}. "
                f"Claim: {claim}"
            )
            return False

        return True
```

### 4. Completeness Check

**Ensure all required fields are present**:

```python
class CompletenessValidator:
    def validate_completeness(self, data: Dict, required_fields: List[str]) -> bool:
        """
        RT-008: Check if data has all required fields.

        Args:
            data: Data dict to validate
            required_fields: List of required field names

        Returns:
            True if >= 80% required fields present
        """
        present_fields = [f for f in required_fields if f in data]
        completeness = len(present_fields) / len(required_fields)

        threshold = QUALITY_METRICS["completeness"]["min_fields_present"]

        if completeness < threshold:
            missing = set(required_fields) - set(present_fields)
            logger.warning(
                f"Incomplete data: {completeness:.2%} complete. "
                f"Missing: {missing}"
            )
            return False

        return True
```

### 5. Consistency Check

**Detect contradictions**:

```python
class ConsistencyValidator:
    def validate_consistency(self, new_info: str, context: List[Dict]) -> bool:
        """
        RT-008: Check for contradictions with existing context.

        Args:
            new_info: New information to add
            context: Existing context messages

        Returns:
            True if no contradictions detected
        """
        contradictions = []

        for msg in context:
            if self._is_contradictory(new_info, msg["content"]):
                contradictions.append(msg)

        max_contradictions = QUALITY_METRICS["consistency"]["max_contradictions"]

        if len(contradictions) > max_contradictions:
            logger.warning(
                f"Contradictions detected: {len(contradictions)} found. "
                f"New info: {new_info}"
            )
            return False

        return True

    def _is_contradictory(self, text1: str, text2: str) -> bool:
        """Check if two texts contradict each other."""
        # Use LLM to detect contradictions
        prompt = f"""
Do these statements contradict each other?

Statement 1: {text1}
Statement 2: {text2}

Answer: yes/no
"""
        response = llm.complete(prompt).strip().lower()
        return response == "yes"
```

## Quality Enforcement Pipeline

```python
class ContextQualityEnforcer:
    """
    RT-008: Enforce quality standards before adding to context.
    """

    def __init__(self):
        self.relevance_validator = RelevanceValidator()
        self.freshness_validator = FreshnessValidator()
        self.accuracy_validator = AccuracyValidator()
        self.completeness_validator = CompletenessValidator()
        self.consistency_validator = ConsistencyValidator()

    def enforce_quality(self, content: Dict, query: str, context: List[Dict]) -> bool:
        """
        Run all quality checks.

        Args:
            content: Content to validate
            query: Current query
            context: Existing context

        Returns:
            True if all quality checks pass
        """
        # 1. Relevance
        if not self.relevance_validator.validate_relevance(content["text"], query):
            return False

        # 2. Freshness
        if not self.freshness_validator.validate_freshness(content):
            return False

        # 3. Accuracy (if factual claim)
        if content.get("type") == "fact":
            if not self.accuracy_validator.validate_accuracy(content["text"]):
                return False

        # 4. Completeness
        required_fields = ["text", "timestamp", "source"]
        if not self.completeness_validator.validate_completeness(content, required_fields):
            return False

        # 5. Consistency
        if not self.consistency_validator.validate_consistency(content["text"], context):
            return False

        # All checks passed
        return True
```

## Deduplication

**Prevent redundant information**:

```python
class ContentDeduplicator:
    """RT-008: Remove duplicate or near-duplicate content."""

    def is_duplicate(self, new_content: str, existing_context: List[Dict], threshold: float = 0.95) -> bool:
        """
        Check if content is duplicate.

        Args:
            new_content: New content to check
            existing_context: Existing context messages
            threshold: Similarity threshold for duplicate detection

        Returns:
            True if duplicate found
        """
        new_emb = self.embed(new_content)

        for msg in existing_context:
            existing_emb = self.embed(msg["content"])
            similarity = cosine_similarity(new_emb, existing_emb)

            if similarity >= threshold:
                logger.info(
                    f"Duplicate detected: {similarity:.2f} similarity. "
                    f"Skipping add."
                )
                return True

        return False
```

## Context Health Metrics

**Monitor context quality over time**:

```python
class ContextHealthMonitor:
    """RT-008: Monitor context health metrics."""

    def compute_health_score(self, context: List[Dict]) -> Dict:
        """
        Compute overall context health score.

        Returns:
            {
                "health_score": 0.0-1.0,
                "metrics": {
                    "avg_relevance": float,
                    "freshness_ratio": float,
                    "accuracy_ratio": float,
                    "consistency_score": float
                },
                "issues": List[str]
            }
        """
        metrics = {
            "avg_relevance": self._compute_avg_relevance(context),
            "freshness_ratio": self._compute_freshness_ratio(context),
            "accuracy_ratio": self._compute_accuracy_ratio(context),
            "consistency_score": self._compute_consistency(context)
        }

        # Overall health score (weighted average)
        health_score = (
            metrics["avg_relevance"] * 0.3 +
            metrics["freshness_ratio"] * 0.2 +
            metrics["accuracy_ratio"] * 0.3 +
            metrics["consistency_score"] * 0.2
        )

        # Identify issues
        issues = []
        if metrics["avg_relevance"] < 0.7:
            issues.append("Low average relevance")
        if metrics["freshness_ratio"] < 0.5:
            issues.append("Too much stale content")
        if metrics["accuracy_ratio"] < 0.9:
            issues.append("Accuracy concerns")
        if metrics["consistency_score"] < 0.8:
            issues.append("Consistency issues detected")

        return {
            "health_score": health_score,
            "metrics": metrics,
            "issues": issues
        }
```

## Quality Degradation Alerts

```python
def alert_on_quality_degradation(health_score: float):
    """RT-008: Alert when context quality degrades."""
    if health_score < 0.6:
        alert_service.send(
            severity="critical",
            message=f"Context health critically low: {health_score:.2f}"
        )
    elif health_score < 0.75:
        alert_service.send(
            severity="warning",
            message=f"Context health degrading: {health_score:.2f}"
        )
```

## Validation

```python
def test_relevance_filtering():
    """RT-008: Low relevance content should be rejected."""
    validator = RelevanceValidator()

    query = "Book a flight to Paris"
    irrelevant_content = "The weather in Tokyo is sunny"

    is_relevant = validator.validate_relevance(irrelevant_content, query)

    assert is_relevant == False

def test_freshness_check():
    """RT-008: Stale content should be rejected."""
    validator = FreshnessValidator()

    stale_content = {
        "text": "Flight price: $500",
        "timestamp": time.time() - 7200  # 2 hours ago
    }

    is_fresh = validator.validate_freshness(stale_content)

    assert is_fresh == False  # Max age is 1 hour

def test_consistency_detection():
    """RT-008: Contradictions should be detected."""
    validator = ConsistencyValidator()

    context = [
        {"content": "User prefers morning flights"}
    ]

    new_info = "User prefers evening flights"

    is_consistent = validator.validate_consistency(new_info, context)

    assert is_consistent == False  # Contradiction detected
```

## Referencias

- ADR-050: Context Engineering Architecture
- ADR-051: Context Management Strategies
- Pattern: Quality Gates, Validation Pipeline
