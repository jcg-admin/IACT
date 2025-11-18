---
id: RT-007
tipo: regla_tecnica
relacionado: [ADR-050, ADR-051]
fecha: 2025-11-16
---

# RT-007: Context Window Limits

## Constraint

El sistema DEBE enforcar límites de context window y aplicar compression strategies cuando se aproxima a límites.

## Context Window Limits by Model

```python
CONTEXT_LIMITS = {
    "gpt-3.5-turbo": 4096,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-turbo": 128000,
    "claude-2": 100000,
    "claude-3-sonnet": 200000,
}
```

## Threshold Triggers

```python
THRESHOLDS = {
    "warning": 0.7,      # 70% - start monitoring
    "compress": 0.8,     # 80% - begin compression
    "critical": 0.9,     # 90% - aggressive compression
    "max": 1.0,          # 100% - reject/fail
}
```

## Implementation

### 1. Context Size Monitoring

```python
class ContextMonitor:
    def __init__(self, model: str):
        self.max_tokens = CONTEXT_LIMITS[model]
        self.current_tokens = 0

    def count_tokens(self, messages: List[Dict]) -> int:
        """
        Count tokens in message list.

        Uses tiktoken for accurate counting.
        """
        import tiktoken

        encoding = tiktoken.encoding_for_model(self.model)

        total = 0
        for message in messages:
            # Count role + content
            total += len(encoding.encode(message["role"]))
            total += len(encoding.encode(message["content"]))
            total += 4  # Message overhead

        return total

    def get_usage_percent(self, messages: List[Dict]) -> float:
        """Get current context usage as percentage."""
        current = self.count_tokens(messages)
        return current / self.max_tokens

    def is_within_limit(self, messages: List[Dict]) -> bool:
        """Check if context is within safe limits."""
        return self.get_usage_percent(messages) < THRESHOLDS["max"]
```

### 2. Auto-Compression Triggers

```python
class ContextCompressor:
    def __init__(self, monitor: ContextMonitor):
        self.monitor = monitor

    def compress_if_needed(self, messages: List[Dict]) -> List[Dict]:
        """
        RT-007: Auto-compress when thresholds exceeded.

        Compression strategy depends on usage level:
        - 70-80%: Monitor only
        - 80-90%: Trim oldest messages
        - 90-100%: Aggressive summarization
        """
        usage = self.monitor.get_usage_percent(messages)

        if usage < THRESHOLDS["warning"]:
            # Under 70% - no action needed
            return messages

        elif usage < THRESHOLDS["compress"]:
            # 70-80% - log warning
            logger.warning(f"Context usage at {usage*100:.1f}%")
            return messages

        elif usage < THRESHOLDS["critical"]:
            # 80-90% - trim oldest messages
            return self._trim_oldest(messages, target_usage=0.6)

        else:
            # 90-100% - aggressive summarization
            return self._aggressive_summarize(messages, target_usage=0.5)

    def _trim_oldest(self, messages: List[Dict], target_usage: float) -> List[Dict]:
        """Trim oldest messages until target usage."""
        # Keep system message (first) + last N messages
        system_msg = messages[0]

        # Binary search for N
        for n in range(len(messages), 0, -1):
            trimmed = [system_msg] + messages[-n:]

            if self.monitor.get_usage_percent(trimmed) <= target_usage:
                logger.info(f"Trimmed {len(messages) - n - 1} old messages")
                return trimmed

        # Fallback: keep only system + last message
        return [system_msg, messages[-1]]

    def _aggressive_summarize(self, messages: List[Dict], target_usage: float) -> List[Dict]:
        """Aggressive summarization for critical usage."""
        system_msg = messages[0]
        recent = messages[-5:]  # Keep last 5

        # Summarize everything in between
        to_summarize = messages[1:-5]

        summary_prompt = f"""
Summarize this conversation in 2-3 sentences:

{to_summarize}

Summary:
"""
        summary = llm.complete(summary_prompt)

        summarized = [
            system_msg,
            {"role": "system", "content": f"Previous conversation: {summary}"},
            *recent
        ]

        logger.info(f"Aggressive summarization: {len(messages)} → {len(summarized)} messages")

        return summarized
```

### 3. Pre-Send Validation

```python
class ContextValidator:
    def validate_before_send(self, messages: List[Dict]) -> bool:
        """
        RT-007: Validate context is within limits before LLM call.

        Raises:
            ContextTooLargeError if validation fails
        """
        monitor = ContextMonitor(model=self.model)

        if not monitor.is_within_limit(messages):
            usage = monitor.get_usage_percent(messages)

            raise ContextTooLargeError(
                f"Context exceeds limit: {usage*100:.1f}% "
                f"({monitor.current_tokens}/{monitor.max_tokens} tokens). "
                "Apply compression before sending."
            )

        return True
```

## Compression Strategies

### Strategy 1: Trim Oldest

**When**: 80-90% usage
**Method**: Remove oldest messages, keep system + recent

```python
def trim_oldest(messages: List[Dict], keep_last_n: int = 10):
    return [messages[0]] + messages[-keep_last_n:]
```

**Pros**: Simple, fast
**Cons**: Loses historical context

### Strategy 2: Summarization

**When**: 90-100% usage
**Method**: LLM summarizes middle section

```python
def summarize_middle(messages: List[Dict]):
    system = messages[0]
    recent = messages[-5:]
    middle = messages[1:-5]

    summary = llm.summarize(middle)

    return [
        system,
        {"role": "system", "content": f"Previous: {summary}"},
        *recent
    ]
```

**Pros**: Preserves key information
**Cons**: LLM call overhead, potential information loss

### Strategy 3: Hierarchical Compression

**When**: Very long conversations (> 100 turns)
**Method**: Multi-level summarization

```python
def hierarchical_compress(messages: List[Dict]):
    # Level 1: Group into chunks of 20
    chunks = [messages[i:i+20] for i in range(1, len(messages)-5, 20)]

    # Level 2: Summarize each chunk
    summaries = [llm.summarize(chunk) for chunk in chunks]

    # Level 3: Combine summaries
    combined = "\n".join(summaries)

    return [
        messages[0],  # System
        {"role": "system", "content": f"Conversation history:\n{combined}"},
        *messages[-5:]  # Recent
    ]
```

**Pros**: Handles very long conversations
**Cons**: Multiple LLM calls, expensive

## Token Budgeting

Allocate token budget across context types:

```python
TOKEN_BUDGET = {
    "system_prompt": 0.10,      # 10% for instructions
    "tools": 0.20,              # 20% for tool descriptions
    "knowledge": 0.15,          # 15% for RAG results
    "conversation": 0.45,       # 45% for conversation history
    "output_buffer": 0.10,      # 10% reserved for response
}

def allocate_budget(max_tokens: int) -> Dict[str, int]:
    """Allocate token budget across context types."""
    return {
        ctx_type: int(max_tokens * allocation)
        for ctx_type, allocation in TOKEN_BUDGET.items()
    }
```

## Metrics

```python
CONTEXT_METRICS = {
    "context_size_tokens": Histogram(["model", "phase"]),
    "context_compressions_total": Counter(["strategy"]),
    "context_overflows_total": Counter(["model"]),
    "compression_ratio": Histogram(["strategy"]),
}
```

## Validation

```python
def test_auto_compression_triggers():
    """RT-007: Compression triggers at 80% threshold."""
    monitor = ContextMonitor(model="gpt-4")
    compressor = ContextCompressor(monitor)

    # Create large context (85% of limit)
    large_context = create_messages(tokens=int(8192 * 0.85))

    # Should trigger compression
    compressed = compressor.compress_if_needed(large_context)

    # Verify compressed to < 80%
    usage = monitor.get_usage_percent(compressed)
    assert usage < 0.8

def test_context_validation():
    """RT-007: Reject context over 100% limit."""
    validator = ContextValidator(model="gpt-4")

    # Create oversized context
    oversized = create_messages(tokens=9000)  # > 8192 limit

    # Should raise error
    with pytest.raises(ContextTooLargeError):
        validator.validate_before_send(oversized)
```

## Cost Impact

Context size directly impacts API costs:

```python
def estimate_cost(messages: List[Dict], model: str) -> float:
    """Estimate API cost based on context size."""
    monitor = ContextMonitor(model)
    tokens = monitor.count_tokens(messages)

    # Pricing per 1k tokens
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
    }

    price = PRICING[model]["input"]
    cost = (tokens / 1000) * price

    return cost
```

## Referencias

- ADR-050: Context Engineering Architecture
- ADR-051: Context Management Strategies
- tiktoken: https://github.com/openai/tiktoken
