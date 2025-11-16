---
id: RF-005
tipo: requisito_funcional
relacionado: [UC-SYS-003, ADR-050, RT-007, RT-008]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-005: Context Validation and Compression

## Especificación

El sistema DEBE validar calidad de contenido antes de añadir al contexto y comprimir automáticamente cuando se alcanzan thresholds de capacidad.

## Criterios de Aceptación

### Context Validation

#### Escenario 1: Validate Content Quality - All Metrics Pass

```gherkin
Given content to add = "User prefers quality hotels near landmarks"
  And context_manager = ContextManager()
When context_manager.validate_quality(content, query="find hotel")
Then validation result:
  - is_valid: True
  - quality_score: 0.87
  - metrics:
      * relevance_score: 0.90 (>= 0.7) ✓
      * freshness_score: 1.0 (current) ✓
      * accuracy_score: 0.95 (>= 0.9) ✓
      * completeness: 1.0 (all fields present) ✓
      * consistency: 1.0 (no contradictions) ✓
  And content is accepted
  And validation latency < 100ms
```

#### Escenario 2: Validate Relevance Score

```gherkin
Given query = "Book flight to Paris"
  And content_candidates = [
      "Flight booking tips",           # Relevant
      "Hotel recommendations Paris",   # Semi-relevant
      "Car rental in London"           # Not relevant
  ]
When context_manager.validate_relevance(candidates, query)
Then relevance scores calculated:
  - "Flight booking tips": 0.92 (high relevance) ✓
  - "Hotel recommendations Paris": 0.65 (below 0.7 threshold) ✗
  - "Car rental in London": 0.25 (low relevance) ✗
  And only content with score >= 0.7 is accepted
  And accepted count = 1 ("Flight booking tips")
```

#### Escenario 3: Validate Freshness

```gherkin
Given content_1 = {text: "User location", timestamp: "2025-11-16T10:00:00"}
  And content_2 = {text: "Preference", timestamp: "2025-11-15T10:00:00"}
  And current_time = "2025-11-16T10:30:00"
  And freshness_threshold = 3600 seconds (1 hour)
When context_manager.validate_freshness([content_1, content_2])
Then freshness results:
  - content_1: age = 30 min < 1 hour → fresh ✓
  - content_2: age = 24 hours > 1 hour → stale ✗
  And fresh_content = [content_1]
  And stale content receives lower priority or is rejected
```

#### Escenario 4: Validate Accuracy (Fact-Checking)

```gherkin
Given content = "The Eiffel Tower is located in Paris, France"
  And validation_service = FactChecker()
When context_manager.validate_accuracy(content)
Then fact_check result:
  - claim: "Eiffel Tower is in Paris, France"
  - validation_result: VALID ✓
  - confidence: 0.99
  - accuracy_score: 0.99 (>= 0.9 threshold)
  And content is accepted
```

#### Escenario 5: Reject Inaccurate Content

```gherkin
Given content = "The Eiffel Tower is in London"
  And validation_service = FactChecker()
When context_manager.validate_accuracy(content)
Then fact_check result:
  - claim: "Eiffel Tower is in London"
  - validation_result: INVALID ✗
  - correct_fact: "Eiffel Tower is in Paris"
  - accuracy_score: 0.0 (< 0.9 threshold)
  And content is REJECTED
  And error raised: ContentValidationError("Factual inaccuracy detected")
  And metrics.context.poisoning_attempts incremented
```

#### Escenario 6: Validate Completeness

```gherkin
Given required_fields = ["user_id", "preference", "timestamp"]
  And content_complete = {
      "user_id": "user_123",
      "preference": "quality hotels",
      "timestamp": "2025-11-16T10:00:00"
  }
  And content_incomplete = {
      "user_id": "user_123",
      "preference": "quality hotels"
      # Missing timestamp!
  }
When context_manager.validate_completeness(content_complete, required_fields)
Then completeness_score = 1.0 (3/3 fields present) ✓
  And content accepted

When context_manager.validate_completeness(content_incomplete, required_fields)
Then completeness_score = 0.67 (2/3 fields present) < 0.8 threshold
  And content REJECTED or flagged with warning
```

#### Escenario 7: Detect Consistency Violations (Contradictions)

```gherkin
Given existing_context contains:
  - "User prefers budget hotels"
  And new_content = "User prefers luxury 5-star hotels"
When context_manager.validate_consistency(new_content, existing_context)
Then contradiction detected:
  - contradicting_item: "User prefers budget hotels"
  - new_item: "User prefers luxury 5-star hotels"
  - consistency_score: 0.0 (contradiction)
  And validation fails
  And warning: "Contradictory preference detected"
  And user or system must resolve conflict
```

### Context Compression

#### Escenario 8: Auto-Compression Trigger at 80% Threshold

```gherkin
Given context_window_max = 8192 tokens
  And current_usage = 6600 tokens (80.6%)
  And compression_threshold = 0.80 (80%)
When context_manager.check_capacity()
Then auto_compression triggered:
  - reason: "Usage 80.6% >= 80% threshold"
  - strategy: TRIM_OLDEST
  - target_usage: 60% (4915 tokens)
  And compression executes automatically
  And latency < 1000ms
```

#### Escenario 9: Trim Oldest Messages

```gherkin
Given conversation_history = [msg_1, msg_2, ..., msg_20]
  And msg_1 timestamp: 2 hours ago
  And msg_20 timestamp: 5 minutes ago
  And trim_threshold = 1 hour
When context_manager.trim_oldest(history, threshold=3600)
Then messages trimmed:
  - msg_1 to msg_12 removed (older than 1 hour)
  - msg_13 to msg_20 kept (within 1 hour)
  - tokens_before: 2500
  - tokens_after: 1000
  - tokens_freed: 1500
  And trimmed messages logged
```

#### Escenario 10: Summarize Conversation History

```gherkin
Given conversation_history with 30 messages
  And total_tokens = 3000
  And llm = GPT4()
When context_manager.summarize_history(history, max_summary_tokens=200)
Then summary generated:
  - summary_text: "User discussed hotel booking in Paris.
                   Preferences: quality > price, near landmarks.
                   Decision: Book Hotel A at $150/night."
  - summary_tokens: 150
  - original_tokens: 3000
  - compression_ratio: 20x (3000 / 150)
  And summary replaces original history in context
  And summarization latency < 1000ms
```

#### Escenario 11: Archive to Scratchpad

```gherkin
Given tool_results = [result_1, result_2, result_3]
  And total_tokens = 1200
  And results already processed (no longer needed in main context)
When context_manager.archive_to_scratchpad(tool_results)
Then results archived:
  - scratchpad.write("tool_results_archive", tool_results)
  - main_context: removed tool_results
  - tokens_freed: 1200
  - scratchpad_reference added: "tool_results_archive_id_123"
  - reference_tokens: 20
  And IF agent needs archived results later:
      Then agent can retrieve via scratchpad_id
```

#### Escenario 12: Compress with Multiple Strategies

```gherkin
Given context_usage = 7000 tokens (85%)
  And target_usage = 60% (4915 tokens)
  And tokens_to_free = 2085
When context_manager.compress_multi_strategy()
Then strategies applied in sequence:
  - Step 1: TRIM_OLDEST (remove msg > 1h) → freed 800 tokens
  - Step 2: SUMMARIZE (summarize msg 1-20) → freed 900 tokens
  - Step 3: ARCHIVE (move tool results) → freed 400 tokens
  - Total freed: 2100 tokens
  And final_usage = 4900 tokens (59.8%) < 60% target ✓
  And compression successful
```

#### Escenario 13: Compression Ratio Calculation

```gherkin
Given original_context_size = 5000 tokens
  And compressed_context_size = 1000 tokens
When context_manager.calculate_compression_ratio(original, compressed)
Then compression_ratio = 5.0 (5x compression)
  And metrics.context.compression_ratio_avg updated
  And compression logged with ratio
```

#### Escenario 14: Aggressive Compression at 90% Threshold

```gherkin
Given context_usage = 7400 tokens (90.2%)
  And aggressive_threshold = 0.90 (90%)
When context_manager.compress_aggressive()
Then aggressive strategies applied:
  - Summarize ALL conversation (not just old)
  - Remove ALL tool results (keep only IDs)
  - Keep only: current query + critical context
  And result:
      * original: 7400 tokens
      * compressed: 800 tokens
      * compression_ratio: 9.25x
      * final_usage: 9.7%
  And aggressive compression logged
```

#### Escenario 15: Compression Failure - Cannot Free Enough Space

```gherkin
Given context_usage = 7800 tokens (95%)
  And target_usage = 60%
  And all compression strategies applied
  And still: usage = 7200 tokens (87%)
When compression cannot reach target
Then compression_failed event:
  - reason: "Cannot compress further without losing critical context"
  - current_usage: 87%
  - target_usage: 60%
  - recommendation: "Split into multiple agent calls or use scratchpad"
  And warning logged
  And metrics.context.compression_failures incremented
  And new content write may be rejected
```

### Token Counting and Budgeting

#### Escenario 16: Count Tokens for Content

```gherkin
Given content = "User prefers quality hotels near Eiffel Tower in Paris"
  And tokenizer = get_tokenizer("gpt-4")
When token_count = context_manager.count_tokens(content, tokenizer)
Then token_count = 12 tokens
  And counting latency < 10ms
```

#### Escenario 17: Check Context Budget Before Adding

```gherkin
Given context_budget = 8192 tokens
  And current_usage = 7000 tokens
  And available_budget = 1192 tokens
  And new_content_tokens = 500
When context_manager.check_budget(new_content_tokens)
Then budget_check:
  - available: 1192 tokens
  - required: 500 tokens
  - sufficient: True ✓
  - usage_after_add: 7500 tokens (91.5%)
  And content can be added
```

#### Escenario 18: Reject Content Exceeding Budget

```gherkin
Given context_budget = 8192 tokens
  And current_usage = 7900 tokens
  And available_budget = 292 tokens
  And new_content_tokens = 500
When context_manager.check_budget(new_content_tokens)
Then budget_check:
  - available: 292 tokens
  - required: 500 tokens
  - sufficient: False ✗
  And ContextBudgetExceeded error raised
  And content REJECTED
  And suggestion: "Compress context or split content"
```

#### Escenario 19: Progressive Token Budget Allocation

```gherkin
Given total_budget = 8192 tokens
  And allocations = {
      "system_instructions": 500,
      "user_preferences": 300,
      "conversation_history": 2000,
      "tool_descriptions": 1500,
      "current_query": 200,
      "available_for_tools": 3692
  }
When context_manager.allocate_budgets(total_budget, allocations)
Then each component has allocated budget:
  - system_instructions: max 500 tokens
  - user_preferences: max 300 tokens
  - etc.
  And IF component exceeds allocation:
      Then component is compressed to fit
  And total allocations <= total_budget ✓
```

#### Escenario 20: Monitor Token Usage in Real-Time

```gherkin
Given context_manager monitoring enabled
  And usage thresholds = {70%: WARNING, 80%: COMPRESS, 90%: CRITICAL}
When context usage increases:
  - At 60%: No action
  - At 72%: WARNING logged
  - At 82%: AUTO_COMPRESS triggered
  - At 92%: CRITICAL alert + aggressive compression
Then appropriate actions taken at each threshold
  And metrics updated:
      * context.usage_warning_count
      * context.compression_triggered_count
      * context.critical_alerts_count
  And dashboard displays real-time usage graph
```

## Implementación

Archivo: `scripts/coding/ai/context/validation.py`

```python
class ContextQualityValidator:
    """
    RF-005: Validate content quality before adding to context.
    """

    def __init__(self, llm, fact_checker):
        self.llm = llm
        self.fact_checker = fact_checker

    def validate_quality(
        self,
        content: str,
        query: str = None,
        existing_context: List[str] = None
    ) -> ValidationResult:
        """
        RF-005: Validate content across all quality metrics.

        Returns:
            ValidationResult with is_valid, quality_score, metrics
        """
        metrics = {}

        # 1. Relevance (RF-005 Scenario 2)
        if query:
            relevance = self._validate_relevance(content, query)
            metrics["relevance_score"] = relevance

            if relevance < 0.7:
                return ValidationResult(
                    is_valid=False,
                    quality_score=relevance,
                    metrics=metrics,
                    reason="Low relevance score"
                )

        # 2. Freshness (RF-005 Scenario 3)
        freshness = self._validate_freshness(content)
        metrics["freshness_score"] = freshness

        # 3. Accuracy (RF-005 Scenario 4, 5)
        accuracy = self._validate_accuracy(content)
        metrics["accuracy_score"] = accuracy

        if accuracy < 0.9:
            return ValidationResult(
                is_valid=False,
                quality_score=accuracy,
                metrics=metrics,
                reason="Factual inaccuracy detected"
            )

        # 4. Completeness (RF-005 Scenario 6)
        completeness = self._validate_completeness(content)
        metrics["completeness"] = completeness

        if completeness < 0.8:
            return ValidationResult(
                is_valid=False,
                quality_score=completeness,
                metrics=metrics,
                reason="Incomplete content"
            )

        # 5. Consistency (RF-005 Scenario 7)
        if existing_context:
            consistency = self._validate_consistency(content, existing_context)
            metrics["consistency"] = consistency

            if consistency < 0.5:  # Contradiction
                return ValidationResult(
                    is_valid=False,
                    quality_score=consistency,
                    metrics=metrics,
                    reason="Contradictory content detected"
                )

        # Calculate overall quality score
        quality_score = sum(metrics.values()) / len(metrics)

        return ValidationResult(
            is_valid=True,
            quality_score=quality_score,
            metrics=metrics
        )

    def _validate_relevance(self, content: str, query: str) -> float:
        """Calculate semantic relevance using embeddings."""
        content_emb = self._embed(content)
        query_emb = self._embed(query)

        similarity = cosine_similarity(content_emb, query_emb)

        return similarity

    def _validate_accuracy(self, content: str) -> float:
        """Fact-check content for accuracy."""
        claims = self._extract_claims(content)

        if not claims:
            return 1.0  # No verifiable claims

        accuracy_scores = []

        for claim in claims:
            result = self.fact_checker.verify(claim)
            accuracy_scores.append(result.confidence if result.valid else 0.0)

        return sum(accuracy_scores) / len(accuracy_scores)
```

Archivo: `scripts/coding/ai/context/compression.py`

```python
class ContextCompressor:
    """
    RF-005: Compress context when capacity thresholds reached.
    """

    def __init__(self, llm, scratchpad):
        self.llm = llm
        self.scratchpad = scratchpad

    @enforce_latency_target("compression", 1000)
    def compress(
        self,
        context: Dict,
        target_usage: float = 0.6
    ) -> CompressionResult:
        """
        RF-005: Compress context to target usage.

        Args:
            context: Current context
            target_usage: Target usage percentage (0.0-1.0)

        Returns:
            CompressionResult with compressed context, tokens freed
        """
        original_tokens = self._count_tokens(context)
        current_usage = original_tokens / self.max_tokens

        if current_usage < target_usage:
            # No compression needed
            return CompressionResult(
                compressed_context=context,
                tokens_freed=0,
                compression_ratio=1.0
            )

        # Apply compression strategies (RF-005 Scenario 12)
        compressed = context.copy()
        tokens_freed = 0

        # Strategy 1: Trim oldest
        if self._has_conversation_history(compressed):
            trimmed, freed = self._trim_oldest(
                compressed["conversation_history"],
                threshold_seconds=3600
            )
            compressed["conversation_history"] = trimmed
            tokens_freed += freed

        # Strategy 2: Summarize
        current_usage = self._calculate_usage(compressed)

        if current_usage > target_usage and self._has_long_history(compressed):
            summarized, freed = self._summarize_history(
                compressed["conversation_history"],
                max_summary_tokens=200
            )
            compressed["conversation_history"] = [summarized]
            tokens_freed += freed

        # Strategy 3: Archive
        current_usage = self._calculate_usage(compressed)

        if current_usage > target_usage and self._has_tool_results(compressed):
            archived, freed = self._archive_tool_results(
                compressed["tool_results"]
            )
            compressed["tool_results"] = archived  # Just IDs
            tokens_freed += freed

        # Calculate final stats
        final_tokens = self._count_tokens(compressed)
        compression_ratio = original_tokens / final_tokens if final_tokens > 0 else 1.0

        return CompressionResult(
            compressed_context=compressed,
            tokens_freed=tokens_freed,
            compression_ratio=compression_ratio,
            final_usage=final_tokens / self.max_tokens
        )

    def _summarize_history(
        self,
        history: List[Message],
        max_summary_tokens: int
    ) -> Tuple[Message, int]:
        """Summarize conversation history using LLM."""
        # Prepare history for summarization
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in history
        ])

        original_tokens = self._count_tokens(history_text)

        # Generate summary
        prompt = f"""
Summarize this conversation in {max_summary_tokens} tokens or less.
Focus on key decisions, preferences, and outcomes.

Conversation:
{history_text}

Summary:
"""
        summary_text = self.llm.complete(prompt, max_tokens=max_summary_tokens)

        summary_message = {
            "role": "system",
            "content": f"[Summary of previous conversation]: {summary_text}"
        }

        summary_tokens = self._count_tokens(summary_text)
        tokens_freed = original_tokens - summary_tokens

        return summary_message, tokens_freed
```

## Tests

Archivo: `scripts/coding/tests/ai/test_context_validation_compression.py`

```python
class TestContextValidation:
    def test_validate_quality_all_pass(self):
        """RF-005 Scenario 1: All quality metrics pass."""
        validator = ContextQualityValidator(llm=mock_llm, fact_checker=mock_checker)

        content = "User prefers quality hotels near landmarks"
        query = "find hotel"

        result = validator.validate_quality(content, query)

        assert result.is_valid == True
        assert result.quality_score >= 0.8
        assert result.metrics["relevance_score"] >= 0.7
        assert result.metrics["accuracy_score"] >= 0.9

    def test_reject_inaccurate_content(self):
        """RF-005 Scenario 5: Reject factually incorrect content."""
        validator = ContextQualityValidator(llm=mock_llm, fact_checker=mock_checker)

        # Mock fact checker to return INVALID
        mock_checker.verify = lambda claim: VerificationResult(valid=False, confidence=0.0)

        content = "The Eiffel Tower is in London"

        result = validator.validate_quality(content)

        assert result.is_valid == False
        assert result.metrics["accuracy_score"] < 0.9
        assert "inaccuracy" in result.reason.lower()


class TestContextCompression:
    def test_auto_compression_at_80_percent(self):
        """RF-005 Scenario 8: Auto-compression triggers at 80%."""
        compressor = ContextCompressor(llm=mock_llm, scratchpad=mock_scratchpad)
        compressor.max_tokens = 8192

        # Context at 80.6% usage
        context = create_mock_context(tokens=6600)

        result = compressor.compress(context, target_usage=0.6)

        assert result.tokens_freed > 0
        assert result.final_usage <= 0.6
        assert result.compression_ratio > 1.0

    def test_summarize_conversation_history(self):
        """RF-005 Scenario 10: Summarize history."""
        compressor = ContextCompressor(llm=mock_llm, scratchpad=mock_scratchpad)

        history = create_mock_history(messages=30, tokens=3000)

        summary_msg, tokens_freed = compressor._summarize_history(
            history,
            max_summary_tokens=200
        )

        assert tokens_freed > 2500  # Significant compression
        assert "summary" in summary_msg["content"].lower()
        assert compressor._count_tokens(summary_msg["content"]) <= 200
```

Resultado esperado: `20 passed in 0.25s`

## Métricas

- Validation latency p95: < 100ms
- Compression latency p95: < 1000ms
- Compression ratio avg: > 3.0x
- Context quality score avg: > 0.8
- Accuracy validation rate: > 95%

## Referencias

- UC-SYS-003: Gestionar Contexto de Agente
- ADR-050: Context Engineering Architecture
- RT-007: Context Window Limits
- RT-008: Context Quality Standards

---

**Requisito**: Sistema valida calidad de contenido (5 metrics) y comprime automáticamente (3 strategies) cuando alcanza thresholds.
**Verificación**: Gherkin scenarios + quality thresholds + compression targets + TDD tests.
