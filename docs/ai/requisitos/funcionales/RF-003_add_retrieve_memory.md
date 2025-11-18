---
id: RF-003
tipo: requisito_funcional
relacionado: [UC-SYS-002, RT-004, RT-006, ADR-048]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-003: Add and Retrieve Memory

## Especificación

El sistema DEBE permitir agregar y recuperar memories de diferentes tipos con latency targets específicos.

## Criterios de Aceptación

### Escenario 1: Add Working Memory (< 1ms)

```gherkin
Given agent_id = "travel_agent"
  And user_id = "user_123"
When sistema.memory.add(
    content="current_task: book flight to Paris",
    memory_type="working"
)
Then memory_id is returned
  And latency < 1ms
  And memory stored in Python dict (in-memory)
```

### Escenario 2: Add Short-Term Memory (< 10ms)

```gherkin
Given session_id = "sess_abc123"
When sistema.memory.add(
    content="User: How much is a flight to Paris?",
    memory_type="short_term"
)
Then memory_id is returned
  And latency < 10ms
  And memory stored in Redis
  And TTL set to 3600 seconds (1 hour)
```

### Escenario 3: Add Long-Term Memory (< 100ms)

```gherkin
Given user_id = "user_123"
  And user has not exceeded quota
When sistema.memory.add(
    content="User enjoys skiing and mountain views",
    memory_type="long_term"
)
Then memory_id is returned
  And latency < 100ms
  And memory stored in Azure AI Search (vector DB)
  And embedding generated from content
```

### Escenario 4: Retrieve by Semantic Search

```gherkin
Given user_id = "user_123"
  And long_term_memory contains:
    | content                                  |
    | "User enjoys skiing"                     |
    | "User avoids advanced slopes"            |
    | "User likes coffee with mountain view"   |
When sistema.memory.retrieve(
    query="skiing preferences",
    memory_type="long_term",
    top_k=2
)
Then results contain 2 memories
  And results[0].content contains "skiing"
  And results[1].content contains "slopes"
  And latency < 100ms
  And results ordered by relevance (score)
```

### Escenario 5: Retrieve from Multiple Types

```gherkin
Given user has memories in multiple types:
    - working: {"current_destination": "Paris"}
    - long_term: ["User likes French cuisine"]
When sistema.memory.retrieve(
    query="Paris trip planning",
    memory_types=["working", "long_term"]
)
Then results include memories from both types
  And working_memory results returned first (lower latency)
  And total latency < 150ms
```

### Escenario 6: Quota Exceeded

```gherkin
Given user_id = "user_123"
  And user has 10,000 long_term memories (at quota)
When sistema.memory.add(
    content="One more memory",
    memory_type="long_term"
)
Then QuotaExceededError is raised
  And error message contains "max: 10,000"
  And suggestion to "delete old memories or upgrade"
```

### Escenario 7: Auto-Prune When Quota Exceeded

```gherkin
Given user_id = "user_123"
  And user has 10,000 long_term memories (at quota)
  And auto_prune is enabled
When sistema.memory.add_with_auto_prune(
    content="New memory",
    memory_type="long_term"
)
Then oldest 10% memories are deleted (1,000 memories)
  And new memory is added
  And total remains at 10,000
  And result indicates "add_with_prune"
```

### Escenario 8: Compression for Large Content

```gherkin
Given content size = 5 KB (> 1 KB threshold)
When sistema.memory.add(
    content=large_content,
    memory_type="long_term"
)
Then content is compressed with zlib
  And compressed_size < original_size
  And metadata includes is_compressed=True
  And retrieval auto-decompresses
```

### Escenario 9: Retrieve with Filters

```gherkin
Given long_term_memory contains:
    | content                | metadata                |
    | "User likes skiing"    | {"category": "sports"}  |
    | "User likes coffee"    | {"category": "food"}    |
When sistema.memory.retrieve(
    query="preferences",
    memory_type="long_term",
    filters={"category": "sports"}
)
Then results contain only "sports" memories
  And "coffee" memory not included
```

### Escenario 10: Retrieve Empty Results

```gherkin
Given user_id = "new_user"
  And user has no long_term memories
When sistema.memory.retrieve(
    query="anything",
    memory_type="long_term"
)
Then results = []
  And no error raised
  And latency < 50ms (fast path for empty)
```

## Implementación

Archivo: `scripts/coding/ai/memory/memory_manager.py`

```python
class MemoryManager:
    def __init__(self, user_id: str, agent_id: str, auto_prune: bool = False):
        self.user_id = user_id
        self.agent_id = agent_id
        self.auto_prune = auto_prune

        # Initialize backends
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory(...)
        self.long_term = LongTermMemory(user_id)

    def add(self, content: str, memory_type: MemoryType,
            metadata: Dict = None) -> Dict:
        """
        Add memory to storage.

        Returns:
            {
                "memory_id": str,
                "operation": "add",
                "memory_type": str,
                "latency_ms": float,
                "quota_remaining": int
            }
        """
        start = time.perf_counter()

        # Validate (RF-003)
        if not content:
            raise ValueError("Content cannot be empty")

        # Check quota (RT-006)
        if memory_type != MemoryType.WORKING:
            self._check_quota(memory_type)

        # Route to backend
        backend = self._get_backend(memory_type)
        memory_id = backend.add(content, metadata)

        # Metrics
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Check latency target (RT-004)
        target = LATENCY_TARGETS[memory_type.value]
        if elapsed_ms > target:
            logger.warning(
                f"Latency violation: {memory_type.value} "
                f"took {elapsed_ms:.2f}ms (target: {target}ms)"
            )

        return {
            "memory_id": memory_id,
            "operation": "add",
            "memory_type": memory_type.value,
            "latency_ms": elapsed_ms,
            "quota_remaining": self._get_quota_remaining(memory_type)
        }

    def retrieve(self, query: str, memory_types: List[MemoryType] = None,
                 top_k: int = 5, filters: Dict = None) -> List[Dict]:
        """
        Retrieve memories by semantic search.

        Returns:
            [
                {
                    "memory_id": str,
                    "content": str,
                    "memory_type": str,
                    "score": float,
                    "metadata": Dict
                },
                ...
            ]
        """
        if memory_types is None:
            memory_types = [MemoryType.LONG_TERM]

        all_results = []

        for mtype in memory_types:
            backend = self._get_backend(mtype)
            results = backend.search(query, top_k, filters)
            all_results.extend(results)

        # Sort by score (descending)
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return all_results[:top_k]

    def add_with_auto_prune(self, content: str, memory_type: MemoryType,
                           metadata: Dict = None) -> Dict:
        """RF-003: Add with auto-pruning if quota exceeded."""
        try:
            return self.add(content, memory_type, metadata)
        except QuotaExceededError:
            # Auto-prune oldest 10%
            backend = self._get_backend(memory_type)
            backend.prune_oldest(percent=0.1)

            # Retry
            result = self.add(content, memory_type, metadata)
            result["operation"] = "add_with_prune"
            return result
```

## Tests

Archivo: `scripts/coding/tests/ai/test_memory_add_retrieve.py`

```python
class TestAddMemory:
    def test_add_working_memory_latency(self):
        """RF-003: Working memory < 1ms"""
        manager = MemoryManager(user_id="test", agent_id="test_agent")

        result = manager.add(
            content="task: book flight",
            memory_type=MemoryType.WORKING
        )

        assert result["latency_ms"] < 1
        assert result["memory_id"] is not None

    def test_add_short_term_with_ttl(self):
        """RF-003: Short-term memory with TTL"""
        manager = MemoryManager(user_id="test", agent_id="test_agent")

        result = manager.add(
            content="User: Flight to Paris?",
            memory_type=MemoryType.SHORT_TERM
        )

        # Check TTL was set
        ttl = manager.short_term.get_ttl()
        assert ttl == 3600  # 1 hour

    def test_add_long_term_semantic_search(self):
        """RF-003: Long-term memory with semantic search"""
        manager = MemoryManager(user_id="test", agent_id="test_agent")

        # Add memories
        manager.add("User enjoys skiing", MemoryType.LONG_TERM)
        manager.add("User avoids advanced slopes", MemoryType.LONG_TERM)

        # Retrieve
        results = manager.retrieve(
            query="skiing preferences",
            memory_types=[MemoryType.LONG_TERM],
            top_k=2
        )

        assert len(results) == 2
        assert "skiing" in results[0]["content"].lower()

class TestQuotaEnforcement:
    def test_quota_exceeded_error(self):
        """RF-003: Raise error when quota exceeded"""
        manager = MemoryManager(user_id="test", agent_id="test_agent")

        # Fill to quota
        max_count = USER_QUOTAS["long_term"]["max_memories"]
        for i in range(max_count):
            manager.add(f"Memory {i}", MemoryType.LONG_TERM)

        # Should fail
        with pytest.raises(QuotaExceededError) as exc:
            manager.add("Exceeds quota", MemoryType.LONG_TERM)

        assert "max: 10,000" in str(exc.value)

    def test_auto_prune(self):
        """RF-003: Auto-prune when quota exceeded"""
        manager = MemoryManager(
            user_id="test",
            agent_id="test_agent",
            auto_prune=True
        )

        # Fill to quota
        max_count = USER_QUOTAS["long_term"]["max_memories"]
        for i in range(max_count):
            manager.add(f"Memory {i}", MemoryType.LONG_TERM)

        # Should auto-prune
        result = manager.add_with_auto_prune(
            "New memory",
            MemoryType.LONG_TERM
        )

        assert result["operation"] == "add_with_prune"
        assert manager.count_memories(MemoryType.LONG_TERM) == max_count
```

Resultado esperado: `13 passed in 0.15s`

## Métricas

- Latency p95:
  - Working: < 1ms ✓
  - Short-term: < 10ms ✓
  - Long-term: < 100ms ✓
- Quota enforcement: 100% ✓
- Semantic search precision: > 80% @top-5

## Referencias

- UC-SYS-002: Gestionar Memoria de Agente
- RT-004: Memory Performance Constraints
- RT-006: Memory Storage Limits
- ADR-048: AI Agent Memory Architecture
