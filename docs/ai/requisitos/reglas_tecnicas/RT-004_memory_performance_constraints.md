---
id: RT-004
tipo: regla_tecnica
relacionado: [ADR-048, ADR-049]
fecha: 2025-11-16
---

# RT-004: Memory Performance Constraints

## Constraint

El sistema de memoria DEBE cumplir con límites de latencia según tipo de memoria.

## Performance Requirements

### Latency Targets (p95)

```python
LATENCY_TARGETS = {
    "working": 1,        # < 1ms
    "short_term": 10,    # < 10ms
    "long_term": 100,    # < 100ms
    "episodic": 200,     # < 200ms
    "entity": 150,       # < 150ms
    "structured": 120,   # < 120ms
}  # milliseconds
```

### Throughput Requirements

```python
THROUGHPUT_TARGETS = {
    "working": 10000,    # 10k ops/sec
    "short_term": 1000,  # 1k ops/sec
    "long_term": 100,    # 100 ops/sec
    "episodic": 50,      # 50 ops/sec
    "entity": 75,        # 75 ops/sec
    "structured": 60,    # 60 ops/sec
}  # operations per second
```

## Implementation Guardrails

### 1. Timeout Configuration

```python
def retrieve_memory(query: str, memory_type: MemoryType, timeout_ms: int = None):
    """
    Retrieve memory with timeout enforcement.

    Args:
        query: Search query
        memory_type: Type of memory to search
        timeout_ms: Override timeout (uses RT-004 defaults if None)

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    if timeout_ms is None:
        timeout_ms = LATENCY_TARGETS[memory_type.value]

    with Timeout(timeout_ms / 1000):  # Convert to seconds
        return memory_store.retrieve(query, memory_type)
```

### 2. Performance Monitoring

```python
@monitor_latency
def add_memory(content: str, memory_type: MemoryType):
    """Decorator monitors latency and logs violations."""
    start = time.perf_counter()

    result = memory_store.add(content, memory_type)

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Check against target
    target = LATENCY_TARGETS[memory_type.value]
    if elapsed_ms > target:
        logger.warning(
            f"Memory latency violation: {memory_type.value} "
            f"took {elapsed_ms:.2f}ms (target: {target}ms)"
        )

    return result
```

### 3. Caching Strategy

Para cumplir con latency targets, implementar caching:

```python
class CachedMemory:
    def __init__(self, backend: MemoryBackend):
        self.backend = backend
        self.cache = TTLCache(maxsize=1000, ttl=60)  # 1 min TTL

    def retrieve(self, query: str):
        # Check cache first
        cache_key = hashlib.md5(query.encode()).hexdigest()

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Cache miss - fetch from backend
        result = self.backend.retrieve(query)
        self.cache[cache_key] = result

        return result
```

## Optimization Techniques

### For Working Memory (< 1ms)

- Use Python dict (in-memory)
- No serialization
- No network calls

### For Short-Term Memory (< 10ms)

- Use Redis with pipelining
- Batch operations
- Connection pooling

### For Long-Term Memory (< 100ms)

- Use vector index (Azure AI Search)
- Limit top_k to reasonable value (5-10)
- Filter early (user_id index)

### For Episodic/Entity (< 200ms)

- Pre-compute common queries
- Limit graph traversal depth
- Use graph indexes

## Validation

Tests deben verificar latency:

```python
def test_working_memory_latency():
    """RT-004: Working memory debe ser < 1ms"""
    memory = WorkingMemory()

    start = time.perf_counter()
    memory.set("key", "value")
    result = memory.get("key")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 1, f"Working memory too slow: {elapsed_ms}ms"

def test_long_term_memory_latency():
    """RT-004: Long-term memory debe ser < 100ms (p95)"""
    memory = LongTermMemory(user_id="test")

    latencies = []
    for i in range(100):
        start = time.perf_counter()
        memory.retrieve(f"query {i}", top_k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

    # Check p95
    p95 = sorted(latencies)[94]  # 95th percentile
    assert p95 < 100, f"Long-term memory p95 too slow: {p95}ms"
```

## Error Handling

Si latency target no se cumple:

1. **Log warning** (no fail request)
2. **Increment metric** (monitor degradation)
3. **Consider fallback**:
   - Use cached result
   - Return partial results
   - Degrade gracefully

```python
def retrieve_with_fallback(query: str, memory_type: MemoryType):
    try:
        return retrieve_memory(query, memory_type)
    except TimeoutError:
        logger.warning(f"Memory timeout for {memory_type.value}, using cache")
        return get_cached_result(query) or []
```

## Metrics to Track

```python
METRICS = {
    "memory_latency_ms": Histogram(
        ["memory_type", "operation"]
    ),
    "memory_timeouts_total": Counter(
        ["memory_type"]
    ),
    "memory_cache_hits_total": Counter(
        ["memory_type"]
    ),
}
```

## Referencias

- ADR-048: AI Agent Memory Architecture
- ADR-049: Memory Types and Storage Strategy
- Performance testing: `scripts/coding/tests/ai/test_memory_performance.py`
