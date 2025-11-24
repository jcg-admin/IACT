---
id: RT-006
tipo: regla_tecnica
relacionado: [ADR-048, ADR-049]
fecha: 2025-11-16
---

# RT-006: Memory Storage Limits

## Constraint

El sistema DEBE enforcar límites de almacenamiento para prevenir crecimiento descontrolado y controlar costos.

## Storage Quotas

### Per-User Limits

```python
USER_QUOTAS = {
    "working": {
        "max_entries": 100,          # Max keys in working memory
        "max_size_kb": 10,           # 10 KB total
    },
    "short_term": {
        "max_messages": 100,         # Last 100 messages
        "max_size_mb": 1,            # 1 MB per session
    },
    "long_term": {
        "max_memories": 10000,       # 10k memories per user
        "max_size_mb": 100,          # 100 MB per user
    },
    "entity": {
        "max_entities": 5000,        # 5k entities per user
        "max_relationships": 10000,  # 10k relationships
    },
    "episodic": {
        "max_episodes": 1000,        # 1k episodes per agent
        "max_steps_per_episode": 50, # 50 steps max
    },
    "structured": {
        "max_documents": 5000,       # 5k structured docs per user
        "max_size_mb": 50,           # 50 MB
    }
}
```

### Global Limits

```python
GLOBAL_QUOTAS = {
    "long_term_total_gb": 1000,      # 1 TB total
    "graph_nodes_total": 10_000_000, # 10M nodes
    "graph_edges_total": 50_000_000, # 50M edges
}
```

## Quota Enforcement

### 1. Check Before Add

```python
class LongTermMemory:
    def add_memory(self, content: str, metadata: Dict = None):
        # Check quota (RT-006)
        current_count = self._count_user_memories()
        max_count = USER_QUOTAS["long_term"]["max_memories"]

        if current_count >= max_count:
            raise QuotaExceededError(
                f"User has {current_count} memories (max: {max_count}). "
                "Delete old memories or upgrade quota."
            )

        # Check size
        content_size_kb = len(content.encode('utf-8')) / 1024
        current_size_mb = self._get_user_storage_size_mb()
        max_size_mb = USER_QUOTAS["long_term"]["max_size_mb"]

        if current_size_mb + (content_size_kb / 1024) > max_size_mb:
            raise QuotaExceededError(
                f"Adding memory would exceed size quota "
                f"({current_size_mb:.2f} MB / {max_size_mb} MB)"
            )

        # Proceed with add
        self._add_memory_internal(content, metadata)
```

### 2. Auto-Prune Old Memories

Si quota exceeded, auto-delete oldest memories:

```python
class LongTermMemory:
    def add_with_auto_prune(self, content: str, metadata: Dict = None):
        """
        Add memory, auto-pruning oldest if quota exceeded.
        RT-006: Implements LRU eviction strategy.
        """
        try:
            self.add_memory(content, metadata)
        except QuotaExceededError:
            logger.warning("Quota exceeded, pruning oldest memories")

            # Delete oldest 10%
            all_memories = self._list_all_memories_sorted_by_age()
            to_delete = int(len(all_memories) * 0.1)

            for memory in all_memories[:to_delete]:
                self.delete(memory["id"])

            # Retry add
            self.add_memory(content, metadata)
```

### 3. Working Memory Size Limit

```python
class WorkingMemory:
    def set(self, key: str, value: Any):
        # Check entry count (RT-006)
        if len(self._data) >= USER_QUOTAS["working"]["max_entries"]:
            raise QuotaExceededError(
                f"Working memory has {len(self._data)} entries "
                f"(max: {USER_QUOTAS['working']['max_entries']})"
            )

        # Check total size
        total_size_kb = sum(
            len(str(v).encode('utf-8')) for v in self._data.values()
        ) / 1024

        value_size_kb = len(str(value).encode('utf-8')) / 1024
        max_size_kb = USER_QUOTAS["working"]["max_size_kb"]

        if total_size_kb + value_size_kb > max_size_kb:
            # Auto-evict LRU entry
            lru_key = self._get_lru_key()
            del self._data[lru_key]

        self._data[key] = value
```

### 4. Short-Term Message Limit

```python
class ShortTermMemory:
    def add_message(self, role: str, content: str):
        key = f"session:{self.session_id}:messages"

        # Check message count (RT-006)
        current_count = self.redis_client.llen(key)
        max_messages = USER_QUOTAS["short_term"]["max_messages"]

        if current_count >= max_messages:
            # Remove oldest (LPOP)
            self.redis_client.lpop(key)

        # Add newest (RPUSH)
        message = json.dumps({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self.redis_client.rpush(key, message)
```

## Cost Management

### Pricing Tiers

```python
PRICING_TIERS = {
    "free": {
        "long_term_memories": 100,
        "long_term_size_mb": 10,
        "entity_count": 500,
        "cost_per_month": 0,
    },
    "pro": {
        "long_term_memories": 10000,
        "long_term_size_mb": 100,
        "entity_count": 5000,
        "cost_per_month": 20,
    },
    "enterprise": {
        "long_term_memories": 100000,
        "long_term_size_mb": 1000,
        "entity_count": 50000,
        "cost_per_month": 200,
    }
}
```

### Cost Tracking

```python
class MemoryManager:
    def estimate_monthly_cost(self, user_id: str) -> float:
        """
        RT-006: Estimate storage cost based on usage.
        """
        # Get current usage
        usage = self.get_usage_stats(user_id)

        costs = {
            "vector_store": usage["long_term_size_mb"] * 0.40,  # $0.40/GB/month
            "graph_store": (usage["entity_count"] / 1000) * 5.00,  # $5/1k nodes
            "redis": usage["short_term_size_mb"] * 0.15,  # $0.15/GB/month
        }

        total = sum(costs.values())

        return {
            "total_monthly_usd": total,
            "breakdown": costs,
            "usage": usage
        }
```

## Compression Strategies

### 1. Content Compression

```python
import zlib

class LongTermMemory:
    def _compress_content(self, content: str) -> bytes:
        """RT-006: Compress large content to save space."""
        return zlib.compress(content.encode('utf-8'))

    def _decompress_content(self, compressed: bytes) -> str:
        """RT-006: Decompress on retrieval."""
        return zlib.decompress(compressed).decode('utf-8')

    def add_memory(self, content: str, metadata: Dict = None):
        # Compress if large (> 1 KB)
        if len(content) > 1024:
            compressed = self._compress_content(content)
            is_compressed = True
        else:
            compressed = content.encode('utf-8')
            is_compressed = False

        # Store with compression flag
        document = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "content": base64.b64encode(compressed).decode('ascii'),
            "is_compressed": is_compressed,
            "metadata": metadata or {},
        }

        self.search_client.upload_documents([document])
```

### 2. Embedding Cache

```python
class EmbeddingCache:
    """RT-006: Cache embeddings to avoid recomputation."""

    def __init__(self):
        self.cache = LRUCache(maxsize=10000)

    def get_embedding(self, text: str) -> List[float]:
        cache_key = hashlib.md5(text.encode()).hexdigest()

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Compute embedding
        embedding = model.encode(text)
        self.cache[cache_key] = embedding

        return embedding
```

## Monitoring

### Usage Dashboard

```python
def get_usage_stats(user_id: str) -> Dict:
    """
    RT-006: Get user storage usage across all memory types.
    """
    manager = MemoryManager(user_id=user_id, agent_id="*")

    return {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),

        # Counts
        "working_entries": len(manager.working._data),
        "short_term_messages": manager.short_term.get_message_count(),
        "long_term_memories": manager.long_term.count_memories(),
        "entity_count": manager.entity.count_entities(),
        "episodic_count": manager.episodic.count_episodes(),

        # Sizes
        "working_size_kb": manager.working.get_size_kb(),
        "short_term_size_mb": manager.short_term.get_size_mb(),
        "long_term_size_mb": manager.long_term.get_size_mb(),
        "graph_size_mb": manager.entity.get_size_mb(),

        # Quotas
        "quotas": USER_QUOTAS,

        # % Used
        "long_term_quota_pct": (
            manager.long_term.count_memories() /
            USER_QUOTAS["long_term"]["max_memories"] * 100
        ),
    }
```

### Alerts

```python
def check_quota_alerts(user_id: str):
    """RT-006: Alert when approaching quota limits."""
    stats = get_usage_stats(user_id)

    # Alert at 80% usage
    if stats["long_term_quota_pct"] > 80:
        alert_service.send(
            user_id=user_id,
            severity="warning",
            message=f"Long-term memory at {stats['long_term_quota_pct']:.0f}% capacity"
        )

    # Alert at 95% usage
    if stats["long_term_quota_pct"] > 95:
        alert_service.send(
            user_id=user_id,
            severity="critical",
            message="Long-term memory nearly full. Delete old memories or upgrade."
        )
```

## Validation

```python
def test_long_term_quota_enforcement():
    """RT-006: Must reject add when quota exceeded."""
    memory = LongTermMemory(user_id="test")

    # Fill to quota
    max_memories = USER_QUOTAS["long_term"]["max_memories"]
    for i in range(max_memories):
        memory.add_memory(f"Memory {i}")

    # Next one should fail
    with pytest.raises(QuotaExceededError):
        memory.add_memory("One too many")

def test_auto_prune():
    """RT-006: Auto-prune should delete oldest when quota exceeded."""
    memory = LongTermMemory(user_id="test")

    # Fill to quota
    max_memories = USER_QUOTAS["long_term"]["max_memories"]
    for i in range(max_memories):
        memory.add_memory(f"Memory {i}")

    # Add with auto-prune
    memory.add_with_auto_prune("New memory")

    # Should still be at quota (oldest deleted)
    assert memory.count_memories() == max_memories
```

## Referencias

- ADR-048: AI Agent Memory Architecture
- ADR-049: Memory Types and Storage Strategy
- Cost estimation: Azure AI Search pricing
- Compression: zlib documentation
