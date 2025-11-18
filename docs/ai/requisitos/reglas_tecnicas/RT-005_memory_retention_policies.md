---
id: RT-005
tipo: regla_tecnica
relacionado: [ADR-048, ADR-049]
fecha: 2025-11-16
---

# RT-005: Memory Retention Policies

## Constraint

El sistema DEBE aplicar políticas de retención según tipo de memoria para optimizar costo y relevancia.

## Retention Rules

### By Memory Type

```python
RETENTION_POLICIES = {
    "working": {
        "duration": "task",         # Until task completes
        "cleanup": "automatic",     # Cleared on task end
        "backup": False
    },
    "short_term": {
        "duration": "session",      # Until session expires
        "ttl_seconds": 3600,        # 1 hour
        "cleanup": "ttl",           # Redis TTL
        "backup": False
    },
    "long_term": {
        "duration": "persistent",
        "ttl_seconds": None,        # No expiration
        "cleanup": "manual",        # User-initiated
        "backup": True,
        "archive_after_days": 365   # Move to cold storage after 1 year
    },
    "persona": {
        "duration": "permanent",
        "ttl_seconds": None,
        "cleanup": "never",
        "backup": True
    },
    "episodic": {
        "duration": "configurable",
        "ttl_seconds": 7776000,     # 90 days default
        "cleanup": "ttl",
        "backup": True,
        "archive_after_days": 90
    },
    "entity": {
        "duration": "persistent",
        "ttl_seconds": None,
        "cleanup": "manual",
        "backup": True
    },
    "structured": {
        "duration": "persistent",
        "ttl_seconds": None,
        "cleanup": "manual",
        "backup": True,
        "archive_after_days": 180
    }
}
```

## Implementation

### 1. TTL Enforcement

```python
class ShortTermMemory:
    def add_message(self, role: str, content: str):
        key = f"session:{self.session_id}:messages"
        message = json.dumps({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

        # Add to list
        self.redis_client.rpush(key, message)

        # Apply TTL (RT-005: 1 hour for short-term)
        ttl = RETENTION_POLICIES["short_term"]["ttl_seconds"]
        self.redis_client.expire(key, ttl)
```

### 2. Archive to Cold Storage

```python
class LongTermMemory:
    def archive_old_memories(self):
        """
        RT-005: Archive memories older than 1 year to cold storage.
        """
        cutoff_date = datetime.now() - timedelta(
            days=RETENTION_POLICIES["long_term"]["archive_after_days"]
        )

        # Query old memories
        old_memories = self.search_client.search(
            search_text="*",
            filter=f"created_at lt {cutoff_date.isoformat()}"
        )

        for memory in old_memories:
            # Move to blob storage (cold)
            self._archive_to_blob(memory)

            # Delete from search index
            self.search_client.delete_documents([{"id": memory["id"]}])

            logger.info(f"Archived memory {memory['id']} to cold storage")
```

### 3. Episodic Memory Cleanup

```python
class EpisodicMemory:
    def cleanup_old_episodes(self):
        """
        RT-005: Delete episodes older than 90 days.
        """
        ttl_seconds = RETENTION_POLICIES["episodic"]["ttl_seconds"]
        cutoff_timestamp = time.time() - ttl_seconds

        with self.graph.session() as session:
            result = session.run("""
                MATCH (t:Task)-[:HAS_STEP]->(s:Step)
                WHERE s.timestamp < datetime({epochSeconds: $cutoff})
                DETACH DELETE t, s
                RETURN count(t) as deleted_count
            """, cutoff=int(cutoff_timestamp))

            deleted = result.single()["deleted_count"]
            logger.info(f"Cleaned up {deleted} old episodes")
```

### 4. User-Controlled Cleanup

```python
class MemoryManager:
    def delete_user_memories(self, user_id: str, memory_type: MemoryType = None):
        """
        Allow user to delete their memories (GDPR compliance).

        Args:
            user_id: User identifier
            memory_type: Specific type or None for all

        Returns:
            Number of memories deleted
        """
        if memory_type:
            types_to_delete = [memory_type]
        else:
            types_to_delete = list(MemoryType)

        total_deleted = 0

        for mtype in types_to_delete:
            if mtype == MemoryType.LONG_TERM:
                deleted = self.long_term.delete_all(user_id)
                total_deleted += deleted

            elif mtype == MemoryType.ENTITY:
                deleted = self.entity.delete_user_entities(user_id)
                total_deleted += deleted

            # ... other types

        logger.info(f"Deleted {total_deleted} memories for user {user_id}")
        return total_deleted
```

## Cleanup Scheduling

### Cron Jobs

```python
# scripts/cleanup_memories.py

import schedule
import time

def cleanup_short_term():
    """No action needed - Redis TTL handles it"""
    pass

def cleanup_episodic():
    """Run daily"""
    memory = EpisodicMemory(agent_id="*")
    memory.cleanup_old_episodes()

def cleanup_long_term():
    """Run weekly"""
    memory = LongTermMemory(user_id="*")
    memory.archive_old_memories()

# Schedule jobs
schedule.every().day.at("02:00").do(cleanup_episodic)
schedule.every().sunday.at("03:00").do(cleanup_long_term)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

## Backup Strategy

### What to Backup

| Memory Type | Backup | Frequency | Retention |
| ----------- | ------ | --------- | --------- |
| Working     | ❌ No  | N/A       | N/A       |
| Short-Term  | ❌ No  | N/A       | N/A       |
| Long-Term   | ✅ Yes | Daily     | 30 days   |
| Persona     | ✅ Yes | Weekly    | 90 days   |
| Episodic    | ✅ Yes | Daily     | 30 days   |
| Entity      | ✅ Yes | Daily     | 30 days   |
| Structured  | ✅ Yes | Daily     | 30 days   |

### Backup Implementation

```python
def backup_long_term_memory():
    """Daily backup of long-term memories"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/long_term_{timestamp}.json"

    # Export from Azure AI Search
    all_docs = search_client.search(search_text="*", include_total_count=True)

    memories = [doc for doc in all_docs]

    # Write to backup
    with open(backup_path, 'w') as f:
        json.dump(memories, f, indent=2)

    # Upload to blob storage
    blob_client.upload_blob(backup_path)

    logger.info(f"Backed up {len(memories)} long-term memories")
```

## Privacy & GDPR Compliance

### Right to be Forgotten

```python
def gdpr_delete_user_data(user_id: str):
    """
    Complete deletion of user data per GDPR.
    RT-005: Must delete from all memory types.
    """
    manager = MemoryManager(user_id=user_id, agent_id="*")

    # Delete from all memory types
    deleted_counts = {
        "long_term": manager.long_term.delete_all(user_id),
        "entity": manager.entity.delete_user_entities(user_id),
        "structured": manager.structured.delete_user_data(user_id),
    }

    # Delete from backups
    delete_from_backups(user_id)

    # Log for audit
    logger.info(f"GDPR deletion for user {user_id}: {deleted_counts}")

    return deleted_counts
```

### Data Export (GDPR)

```python
def gdpr_export_user_data(user_id: str) -> Dict:
    """Export all user data for GDPR compliance."""
    manager = MemoryManager(user_id=user_id, agent_id="*")

    export = {
        "user_id": user_id,
        "export_date": datetime.now().isoformat(),
        "memories": {
            "long_term": manager.long_term.export_all(user_id),
            "entity": manager.entity.export_all(user_id),
            "structured": manager.structured.export_all(user_id),
        }
    }

    return export
```

## Monitoring

### Metrics to Track

```python
RETENTION_METRICS = {
    "memory_archived_total": Counter(["memory_type"]),
    "memory_deleted_total": Counter(["memory_type", "reason"]),
    "memory_storage_bytes": Gauge(["memory_type"]),
    "memory_age_days": Histogram(["memory_type"]),
}
```

## Validation

```python
def test_short_term_ttl():
    """RT-005: Short-term memory debe expirar en 1 hora"""
    memory = ShortTermMemory(session_id="test")
    memory.add_message("user", "test message")

    # Check exists
    messages = memory.get_conversation_history()
    assert len(messages) == 1

    # Fast-forward time (mock Redis TTL)
    time.sleep(3601)  # 1 hour + 1 second

    # Should be gone
    messages = memory.get_conversation_history()
    assert len(messages) == 0

def test_episodic_cleanup():
    """RT-005: Episodes > 90 days deben ser eliminados"""
    episodic = EpisodicMemory(agent_id="test")

    # Create old episode
    old_timestamp = time.time() - (91 * 24 * 3600)  # 91 days ago
    episodic.record_episode("old_task", steps=[...], timestamp=old_timestamp)

    # Run cleanup
    episodic.cleanup_old_episodes()

    # Verify deleted
    episodes = episodic.query_similar_episodes("old_task")
    assert len(episodes) == 0
```

## Referencias

- ADR-048: AI Agent Memory Architecture
- ADR-049: Memory Types and Storage Strategy
- GDPR Compliance: https://gdpr.eu/
- Cleanup scripts: `scripts/cleanup_memories.py`
