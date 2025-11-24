---
id: RF-006
tipo: requisito_funcional
relacionado: [UC-SYS-003, ADR-050, RT-008]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-006: Context Failure Mitigation

## Especificación

El sistema DEBE detectar y mitigar 4 tipos de context failures: Poisoning (hallucinations), Distraction (too much history), Confusion (too many tools), y Clash (contradictory info).

## Criterios de Aceptación

### Failure 1: Context Poisoning (Hallucination Detection)

#### Escenario 1: Detect and Block Hallucinated Content

```gherkin
Given agent generates content = "The Eiffel Tower is located in London"
  And fact_checker = FactChecker()
When context_manager.detect_poisoning(content)
Then poisoning detected:
  - claim: "Eiffel Tower is in London"
  - validation_result: INVALID ✗
  - correct_fact: "Eiffel Tower is in Paris, France"
  - confidence: 0.99 (high confidence it's wrong)
  And content is BLOCKED from entering context
  And poisoning_attempt logged
  And metrics.context.poisoning_blocked incremented
  And agent receives error: "Content rejected: hallucination detected"
```

#### Escenario 2: Quarantine Suspicious Content

```gherkin
Given content = "Paris population is 500 million"
  And fact_checker returns: validation_result=SUSPICIOUS (low confidence)
When context_manager.handle_suspicious(content)
Then quarantine applied:
  - content moved to quarantine zone
  - NOT added to main context
  - flagged for human review
  - quarantine_id assigned
  And context remains clean
  And IF human approves later:
      Then content moved from quarantine to main context
```

#### Escenario 3: Validate Against Knowledge Base

```gherkin
Given content = "Claude 3 was released in March 2024"
  And knowledge_base contains: "Claude 3 release date: March 2024"
When context_manager.validate_against_kb(content, kb)
Then validation:
  - knowledge_match: True ✓
  - confidence: 1.0 (exact match)
  - source: "knowledge_base"
  And content is accepted (verified by KB)
```

#### Escenario 4: Reject Low-Confidence Claims

```gherkin
Given content = "The next solar eclipse will be on [hallucinated date]"
  And fact_checker confidence = 0.3 (low)
  And confidence_threshold = 0.8
When context_manager.validate_confidence(content)
Then low_confidence detected:
  - confidence: 0.3 < 0.8 threshold
  And content REJECTED
  And reason: "Insufficient confidence in claim accuracy"
```

#### Escenario 5: Poisoning Metrics Dashboard

```gherkin
Given system operates for 1 day
  And 1000 content additions attempted
  And 15 hallucinations blocked
When poisoning_metrics collected
Then metrics show:
  - poisoning_attempts_blocked: 15
  - poisoning_rate: 1.5% (15/1000)
  - common_poisoning_types: [
      "wrong_locations",
      "invented_dates",
      "false_capabilities"
    ]
  And dashboard alerts if rate > 5%
```

### Failure 2: Context Distraction (Too Much History)

#### Escenario 6: Detect Distraction from Long History

```gherkin
Given conversation_history = 50 messages
  And total_history_tokens = 5000
  And distraction_threshold = 20 messages or 2000 tokens
When context_manager.detect_distraction()
Then distraction detected:
  - message_count: 50 > 20 threshold ✓
  - token_count: 5000 > 2000 threshold ✓
  - distraction_severity: HIGH
  And mitigation triggered automatically
```

#### Escenario 7: Periodic Summarization to Prevent Distraction

```gherkin
Given conversation ongoing
  And message_count reaches 20 (threshold)
When context_manager.apply_periodic_summarization()
Then summarization executed:
  - messages_1_to_15 summarized
  - summary: "User discussed [key points]. Decisions: [decisions]."
  - summary_tokens: 100
  - original_tokens: 1500
  - messages_16_to_20 kept verbatim (recent)
  And history compressed: 1600 tokens → 600 tokens
  And distraction mitigated ✓
```

#### Escenario 8: Sliding Window for Recent Context

```gherkin
Given conversation_history = 40 messages
  And sliding_window_size = 10 messages
When context_manager.apply_sliding_window()
Then window applied:
  - messages_1_to_30: archived to scratchpad
  - messages_31_to_40: kept in context (recent window)
  And only recent 10 messages in active context
  And agent focuses on recent conversation
  And distraction from old messages eliminated
```

#### Escenario 9: Distraction Impact on Performance

```gherkin
Given agent with distracted context (50 messages, 5K tokens)
  And agent with clean context (10 messages, 600 tokens)
When both agents execute same task
Then performance comparison:
  - distracted_agent: response_time = 3.5s, accuracy = 0.72
  - clean_agent: response_time = 1.2s, accuracy = 0.89
  And clean context shows:
      * 2.9x faster response
      * 23% higher accuracy
  And demonstrates distraction impact
```

#### Escenario 10: Alert on Distraction Detection

```gherkin
Given message_count = 25 (>= 20 threshold)
When distraction detected
Then alert generated:
  - alert_type: DISTRACTION
  - severity: MEDIUM
  - message: "Conversation history exceeds threshold (25 > 20 messages)"
  - recommended_action: "Apply summarization or sliding window"
  And alert sent to monitoring dashboard
  And auto-mitigation can be triggered
```

### Failure 3: Context Confusion (Too Many Tools)

#### Escenario 11: Detect Confusion from Excessive Tools

```gherkin
Given agent has 45 tools available
  And tool_descriptions_tokens = 3500
  And confusion_threshold = 30 tools
When context_manager.detect_confusion()
Then confusion detected:
  - tool_count: 45 > 30 threshold ✓
  - confusion_risk: HIGH
  - impact: "Agent struggles to select correct tool"
  And mitigation: RAG_OVER_TOOLS recommended
```

#### Escenario 12: RAG Over Tools - Dynamic Tool Retrieval

```gherkin
Given agent has 45 tools (confusing)
  And RAG_over_tools enabled
  And agent needs: "search for flights"
When context_manager.retrieve_relevant_tools(query="search for flights")
Then relevant tools retrieved:
  - tools_found: [
      search_flights (relevance: 0.95),
      book_flights (relevance: 0.88),
      cancel_flights (relevance: 0.72)
    ]
  - top_3_selected (relevance >= 0.7)
  And ONLY these 3 tools injected into context
  - tool_descriptions_tokens: 250 (vs 3500 for all tools)
  And confusion eliminated ✓
```

#### Escenario 13: Tool Selection Accuracy with vs without RAG

```gherkin
Given agent task = "Book hotel in Paris"
  And WITHOUT RAG: all 45 tools in context
  And WITH RAG: only relevant 3 tools retrieved
When agent selects tool
Then selection accuracy:
  - WITHOUT RAG: selected "search_flights" (wrong!) accuracy = 0.0
  - WITH RAG: selected "search_hotels" (correct!) accuracy = 1.0
  And RAG improves tool selection accuracy
  And confusion prevented
```

#### Escenario 14: Tool Catalog with Embeddings

```gherkin
Given 45 tools in catalog
  And each tool has:
      - name: "search_flights"
      - description: "Search for flights to a destination"
      - embedding: vector_embedding(description)
When context_manager.build_tool_catalog()
Then catalog created:
  - total_tools: 45
  - each_tool_embedded: True
  - catalog_indexed for fast retrieval
  And catalog ready for RAG queries
```

#### Escenario 15: Confusion Metrics

```gherkin
Given system with RAG over tools
  And 500 tool calls made in 1 day
  And confusion_prevention_active = True
When metrics collected
Then confusion metrics:
  - tool_selection_accuracy: 0.92 (92% correct)
  - avg_tools_in_context: 4.2 (vs 45 without RAG)
  - token_savings: 85% (3500 → 300 avg)
  - confusion_incidents: 0
  And RAG effectiveness demonstrated
```

### Failure 4: Context Clash (Contradictory Information)

#### Escenario 16: Detect Contradictory Preferences

```gherkin
Given existing_context contains:
    - preference_1: "User prefers budget hotels (< $50/night)"
    - timestamp_1: "2025-11-15T10:00:00"
  And new_content:
    - preference_2: "User prefers luxury 5-star hotels"
    - timestamp_2: "2025-11-16T10:00:00"
When context_manager.detect_clash(new_content, existing_context)
Then clash detected:
  - clash_type: CONTRADICTORY_PREFERENCES
  - item_1: "budget hotels < $50"
  - item_2: "luxury 5-star hotels"
  - contradiction: True ✓
  And conflict_resolution triggered
```

#### Escenario 17: Resolve Clash - Prefer Recent

```gherkin
Given clash between:
    - old_preference: "budget hotels" (2 days ago)
    - new_preference: "luxury hotels" (1 hour ago)
  And resolution_strategy = PREFER_RECENT
When context_manager.resolve_clash(old, new, strategy)
Then resolution:
  - action: REMOVE old_preference
  - action: KEEP new_preference
  - reason: "New preference is more recent (recency: 1h vs 48h)"
  And context updated:
      - "budget hotels" removed
      - "luxury hotels" kept
  And clash resolved ✓
```

#### Escenario 18: Resolve Clash - Ask User

```gherkin
Given clash between critical preferences
  And resolution_strategy = ASK_USER
  And user is available
When context_manager.resolve_clash_interactive(clash)
Then user prompted:
  - question: "You previously preferred budget hotels, but now
               mentioned luxury hotels. Which do you prefer?"
  - options: ["Budget (< $50)", "Luxury (5-star)", "Flexible"]
  And user response = "Luxury (5-star)"
  And context updated based on user response
  And clash resolved with user input
```

#### Escenario 19: Detect Factual Conflicts

```gherkin
Given existing_context:
    - fact_1: "User location: New York"
  And new_content:
    - fact_2: "User location: London"
  And NO timestamp difference (simultaneous)
When context_manager.detect_clash(new_content, existing_context)
Then factual_clash detected:
  - clash_type: CONFLICTING_FACTS
  - contradiction: "User cannot be in NY and London simultaneously"
  And resolution:
      - Option A: User changed location (update)
      - Option B: Error in one fact (validate)
  And clarification requested
```

#### Escenario 20: Clash Metrics and Prevention

```gherkin
Given system operates for 1 week
  And 50 clashes detected
  And 48 resolved automatically (PREFER_RECENT)
  And 2 required user intervention
When clash_metrics collected
Then metrics show:
  - total_clashes_detected: 50
  - auto_resolved: 48 (96%)
  - user_intervention_required: 2 (4%)
  - common_clash_types: [
      "contradictory_preferences",
      "outdated_information",
      "duplicate_facts"
    ]
  - resolution_strategies_used: {
      "PREFER_RECENT": 45,
      "ASK_USER": 2,
      "MERGE": 3
    }
  And dashboard displays clash analytics
```

## Implementación

Archivo: `scripts/coding/ai/context/failure_mitigation.py`

```python
class ContextFailureMitigator:
    """
    RF-006: Detect and mitigate context failures.
    Handles: Poisoning, Distraction, Confusion, Clash
    """

    def __init__(self, fact_checker, tool_catalog, conflict_resolver):
        self.fact_checker = fact_checker
        self.tool_catalog = tool_catalog
        self.conflict_resolver = conflict_resolver

    # FAILURE 1: POISONING

    def detect_poisoning(self, content: str) -> PoisoningResult:
        """
        RF-006: Detect hallucinations/false claims in content.

        Returns:
            PoisoningResult(is_poisoned, confidence, correct_fact)
        """
        # Extract claims from content
        claims = self._extract_claims(content)

        for claim in claims:
            # Fact-check each claim
            validation = self.fact_checker.verify(claim)

            if not validation.valid:
                # Poisoning detected!
                logger.warning(
                    f"Poisoning detected: {claim}. "
                    f"Correct: {validation.correct_fact}"
                )

                metrics.increment("context.poisoning_blocked")

                return PoisoningResult(
                    is_poisoned=True,
                    poisoned_claim=claim,
                    correct_fact=validation.correct_fact,
                    confidence=validation.confidence
                )

        # No poisoning detected
        return PoisoningResult(is_poisoned=False)

    # FAILURE 2: DISTRACTION

    def detect_distraction(
        self,
        conversation_history: List[Message]
    ) -> DistractionResult:
        """
        RF-006: Detect if conversation history is causing distraction.

        Returns:
            DistractionResult(is_distracted, severity, mitigation)
        """
        message_count = len(conversation_history)
        total_tokens = self._count_tokens(conversation_history)

        # Thresholds (RT-008)
        MESSAGE_THRESHOLD = 20
        TOKEN_THRESHOLD = 2000

        is_distracted = (
            message_count > MESSAGE_THRESHOLD or
            total_tokens > TOKEN_THRESHOLD
        )

        if is_distracted:
            severity = "HIGH" if message_count > 40 else "MEDIUM"

            return DistractionResult(
                is_distracted=True,
                message_count=message_count,
                token_count=total_tokens,
                severity=severity,
                recommended_mitigation="SUMMARIZE" if message_count > 30 else "SLIDING_WINDOW"
            )

        return DistractionResult(is_distracted=False)

    def apply_periodic_summarization(
        self,
        history: List[Message],
        keep_recent: int = 5
    ) -> List[Message]:
        """
        RF-006: Summarize old messages, keep recent verbatim.

        Args:
            history: Full conversation history
            keep_recent: Number of recent messages to keep

        Returns:
            Compressed history with summary + recent messages
        """
        if len(history) <= keep_recent:
            return history  # No summarization needed

        # Split: old vs recent
        old_messages = history[:-keep_recent]
        recent_messages = history[-keep_recent:]

        # Summarize old
        summary_text = self._summarize_messages(old_messages)

        summary_message = Message(
            role="system",
            content=f"[Summary of previous conversation]: {summary_text}",
            timestamp=old_messages[-1].timestamp
        )

        # Combine: summary + recent
        compressed_history = [summary_message] + recent_messages

        logger.info(
            f"Summarization: {len(history)} messages → {len(compressed_history)} "
            f"(summary + {keep_recent} recent)"
        )

        return compressed_history

    # FAILURE 3: CONFUSION

    def detect_confusion(self, tools: List[Tool]) -> ConfusionResult:
        """
        RF-006: Detect if too many tools are causing confusion.

        Returns:
            ConfusionResult(is_confused, tool_count, mitigation)
        """
        tool_count = len(tools)
        CONFUSION_THRESHOLD = 30  # RT-008

        if tool_count > CONFUSION_THRESHOLD:
            return ConfusionResult(
                is_confused=True,
                tool_count=tool_count,
                threshold=CONFUSION_THRESHOLD,
                risk="HIGH",
                recommended_mitigation="RAG_OVER_TOOLS"
            )

        return ConfusionResult(is_confused=False)

    def retrieve_relevant_tools(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tool]:
        """
        RF-006: RAG over tools - retrieve only relevant tools.

        Args:
            query: Task description or query
            top_k: Number of tools to retrieve

        Returns:
            List of most relevant tools
        """
        # Embed query
        query_embedding = self._embed(query)

        # Search tool catalog
        relevant_tools = self.tool_catalog.search(
            query_embedding,
            top_k=top_k
        )

        # Filter by relevance threshold
        filtered_tools = [
            tool for tool in relevant_tools
            if tool.relevance_score >= 0.7
        ]

        logger.info(
            f"RAG over tools: {len(self.tool_catalog.all_tools)} available → "
            f"{len(filtered_tools)} retrieved for query: '{query}'"
        )

        return filtered_tools

    # FAILURE 4: CLASH

    def detect_clash(
        self,
        new_content: str,
        existing_context: List[str]
    ) -> ClashResult:
        """
        RF-006: Detect contradictory information.

        Returns:
            ClashResult(has_clash, contradicting_items)
        """
        clashes = []

        for existing_item in existing_context:
            # Check if new content contradicts existing
            contradiction = self._detect_contradiction(new_content, existing_item)

            if contradiction:
                clashes.append({
                    "existing": existing_item,
                    "new": new_content,
                    "type": contradiction.type,
                    "confidence": contradiction.confidence
                })

        if clashes:
            return ClashResult(
                has_clash=True,
                contradicting_items=clashes
            )

        return ClashResult(has_clash=False)

    def resolve_clash(
        self,
        clash: Clash,
        strategy: str = "PREFER_RECENT"
    ) -> Resolution:
        """
        RF-006: Resolve contradictory information.

        Strategies:
            - PREFER_RECENT: Keep newer, remove older
            - ASK_USER: Request user clarification
            - MERGE: Attempt to merge if possible

        Returns:
            Resolution with actions taken
        """
        if strategy == "PREFER_RECENT":
            # Compare timestamps
            if clash.new_item.timestamp > clash.existing_item.timestamp:
                return Resolution(
                    action="REMOVE",
                    item_to_remove=clash.existing_item,
                    item_to_keep=clash.new_item,
                    reason="New item is more recent"
                )

        elif strategy == "ASK_USER":
            # Interactive resolution
            user_choice = self._ask_user_for_clarification(clash)
            return Resolution(
                action="USER_SELECTED",
                item_to_keep=user_choice,
                reason="User preference"
            )

        elif strategy == "MERGE":
            # Attempt to merge compatible info
            merged = self._attempt_merge(clash.existing_item, clash.new_item)
            if merged:
                return Resolution(
                    action="MERGE",
                    merged_item=merged,
                    reason="Successfully merged compatible information"
                )

        # Default: keep existing, reject new
        return Resolution(
            action="KEEP_EXISTING",
            item_to_keep=clash.existing_item,
            reason="Cannot resolve clash"
        )
```

## Tests

Archivo: `scripts/coding/tests/ai/test_context_failure_mitigation.py`

```python
class TestPoisoningMitigation:
    def test_detect_and_block_hallucination(self):
        """RF-006 Scenario 1: Detect and block hallucinated content."""
        mitigator = ContextFailureMitigator(
            fact_checker=mock_fact_checker,
            tool_catalog=mock_catalog,
            conflict_resolver=mock_resolver
        )

        # Mock fact checker to return INVALID
        mock_fact_checker.verify = lambda claim: VerificationResult(
            valid=False,
            correct_fact="Eiffel Tower is in Paris",
            confidence=0.99
        )

        content = "The Eiffel Tower is in London"

        result = mitigator.detect_poisoning(content)

        assert result.is_poisoned == True
        assert "London" in result.poisoned_claim
        assert "Paris" in result.correct_fact
        assert metrics.get("context.poisoning_blocked") > 0


class TestDistractionMitigation:
    def test_periodic_summarization(self):
        """RF-006 Scenario 7: Periodic summarization."""
        mitigator = ContextFailureMitigator(...)

        history = create_mock_history(messages=25)

        compressed = mitigator.apply_periodic_summarization(
            history,
            keep_recent=5
        )

        # Should have: 1 summary + 5 recent = 6 total
        assert len(compressed) == 6
        assert "summary" in compressed[0].content.lower()
        # Recent 5 kept verbatim
        assert compressed[1:] == history[-5:]


class TestConfusionMitigation:
    def test_rag_over_tools(self):
        """RF-006 Scenario 12: RAG over tools."""
        mitigator = ContextFailureMitigator(...)

        # Mock: 45 tools in catalog
        mock_catalog.all_tools = create_mock_tools(count=45)

        relevant = mitigator.retrieve_relevant_tools(
            query="search for flights",
            top_k=5
        )

        # Should return only relevant tools
        assert len(relevant) <= 5
        assert all("flight" in tool.name.lower() for tool in relevant)


class TestClashMitigation:
    def test_resolve_clash_prefer_recent(self):
        """RF-006 Scenario 17: Resolve clash - prefer recent."""
        mitigator = ContextFailureMitigator(...)

        clash = Clash(
            existing_item=Item(content="budget hotels", timestamp="2025-11-14"),
            new_item=Item(content="luxury hotels", timestamp="2025-11-16")
        )

        resolution = mitigator.resolve_clash(clash, strategy="PREFER_RECENT")

        assert resolution.action == "REMOVE"
        assert resolution.item_to_remove == clash.existing_item
        assert resolution.item_to_keep == clash.new_item
        assert "recent" in resolution.reason.lower()
```

Resultado esperado: `20 passed in 0.30s`

## Métricas

- Poisoning detection rate: > 95%
- Distraction mitigation effectiveness: > 90%
- Tool selection accuracy (with RAG): > 92%
- Clash auto-resolution rate: > 95%
- False positive rate: < 5%

## Referencias

- UC-SYS-003: Gestionar Contexto de Agente
- ADR-050: Context Engineering Architecture
- RT-008: Context Quality Standards

---

**Requisito**: Sistema detecta y mitiga 4 context failures con estrategias específicas: validation (poisoning), summarization (distraction), RAG (confusion), conflict resolution (clash).
**Verificación**: Gherkin scenarios + detection accuracy + mitigation effectiveness + TDD tests.
