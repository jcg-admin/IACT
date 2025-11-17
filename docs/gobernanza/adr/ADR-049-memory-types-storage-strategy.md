---
id: ADR-049
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-048]
---

# ADR-049: Memory Types and Storage Strategy

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

ADR-048 define la arquitectura general de memoria. Este ADR especifica **detalles técnicos** de cada tipo de memoria y estrategia de almacenamiento.

### Problem Statement

Diferentes tipos de memoria tienen diferentes requisitos:

| Aspecto        | Working     | Short-Term  | Long-Term    | Episodic     |
| -------------- | ----------- | ----------- | ------------ | ------------ |
| **Latency**    | < 1ms       | < 10ms      | < 100ms      | < 200ms      |
| **Retention**  | Task        | Session     | Months/Years | Configurable |
| **Size**       | KB          | MB          | GB           | GB           |
| **Query Type** | Key lookup  | Recency     | Semantic     | Graph        |
| **Mutability** | High        | Medium      | Low          | Append-only  |

No existe una solución única. Necesitamos **estrategia híbrida**.

## Decision

Implementar estrategia de almacenamiento diferenciada por tipo de memoria:

### 1. Working Memory

**Use Case**: Scratch paper durante tarea actual

**Example**:

```
Travel Agent: "I want to book a trip to Paris"
Working Memory: {current_request: "book trip", destination: "Paris"}
```

**Storage**: In-memory dictionary (Python dict)

**Implementation**:

```python
class WorkingMemory:
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._data[key] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def clear(self):
        self._data.clear()
```

**Retention**: Duration of current task (cleared after task completion)

**Rationale**:

- Fastest possible access (< 1ms)
- No persistence needed
- Simple implementation

### 2. Short-Term Memory

**Use Case**: Context de conversación actual

**Example**:

```
User: "How much would a flight to Paris cost?"
User: "What about accommodation there?"
Short-Term Memory: {"there" → "Paris"} (within same conversation)
```

**Storage**: Redis (session store)

**Implementation**:

```python
class ShortTermMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.redis_client = Redis(host='localhost', port=6379)
        self.ttl = 3600  # 1 hour

    def add_message(self, role: str, content: str):
        key = f"session:{self.session_id}:messages"
        message = json.dumps({"role": role, "content": content, "timestamp": time.time()})
        self.redis_client.rpush(key, message)
        self.redis_client.expire(key, self.ttl)

    def get_conversation_history(self, last_n: int = 10) -> List[Dict]:
        key = f"session:{self.session_id}:messages"
        messages = self.redis_client.lrange(key, -last_n, -1)
        return [json.loads(m) for m in messages]
```

**Retention**: Single session (TTL: 1 hour)

**Rationale**:

- Fast access for recent messages (< 10ms)
- Automatic expiration (TTL)
- Scales horizontally (Redis cluster)

### 3. Long-Term Memory

**Use Case**: Preferencias persistentes entre sesiones

**Example**:

```
"Ben enjoys skiing and outdoor activities, likes coffee with a
mountain view, and wants to avoid advanced ski slopes due to
a past injury"
```

**Storage**: Azure AI Search (Vector DB)

**Implementation**:

```python
class LongTermMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.search_client = SearchClient(
            endpoint=os.getenv("SEARCH_ENDPOINT"),
            index_name="long_term_memory",
            credential=AzureKeyCredential(os.getenv("SEARCH_KEY"))
        )

    def add_memory(self, content: str, metadata: Dict = None):
        # Generar embedding
        embedding = self._get_embedding(content)

        # Crear documento
        document = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }

        self.search_client.upload_documents([document])

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # Semantic search
        query_embedding = self._get_embedding(query)

        results = self.search_client.search(
            search_text=None,
            vector_queries=[{
                "kind": "vector",
                "vector": query_embedding,
                "fields": "embedding",
                "k": top_k
            }],
            filter=f"user_id eq '{self.user_id}'"
        )

        return [{"content": r["content"], "score": r["@search.score"]} for r in results]
```

**Retention**: Months to years

**Rationale**:

- Semantic search (vector similarity)
- Scalable to millions of memories
- Hybrid queries (vector + filters)

### 4. Persona Memory

**Use Case**: Personalidad consistente del agente

**Example**:

```
Agent Role: "Expert ski trip planner"
Persona: {
  tone: "friendly, knowledgeable",
  expertise: ["skiing", "mountain resorts"],
  constraints: ["safety-first", "budget-conscious"]
}
```

**Storage**: Config file + Long-term memory

**Implementation**:

```python
class PersonaMemory:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.config = self._load_persona_config()
        self.long_term = LongTermMemory(user_id=f"agent_{agent_name}")

    def _load_persona_config(self) -> Dict:
        # Cargar desde config file
        config_path = f"config/personas/{self.agent_name}.json"
        with open(config_path) as f:
            return json.load(f)

    def get_persona_prompt(self) -> str:
        # Retrieve learned persona traits
        learned_traits = self.long_term.retrieve("persona traits", top_k=3)

        # Merge config + learned
        return f"""
You are {self.config['role']}.
Tone: {self.config['tone']}
Expertise: {', '.join(self.config['expertise'])}
Learned behaviors: {learned_traits}
"""
```

**Retention**: Permanent (config) + persistent (learned)

**Rationale**:

- Consistency across interactions
- Evolves over time (learned traits)
- Customizable per agent

### 5. Episodic Memory

**Use Case**: Secuencia de pasos (éxitos/fallos)

**Example**:

```
Episode 1: Attempted to book flight AF1234 → FAILED (unavailable)
          → Tried alternative AF5678 → SUCCESS
Episode 2: User asked about Le Chat Noir → Recommended → POSITIVE feedback
```

**Storage**: Graph DB (Neo4j or Cosmos DB Graph)

**Implementation**:

```python
class EpisodicMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.graph = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def record_episode(self, task_id: str, steps: List[Dict]):
        with self.graph.session() as session:
            for i, step in enumerate(steps):
                session.run("""
                    MERGE (t:Task {id: $task_id})
                    CREATE (s:Step {
                        id: $step_id,
                        action: $action,
                        result: $result,
                        timestamp: datetime()
                    })
                    CREATE (t)-[:HAS_STEP {order: $order}]->(s)
                """, task_id=task_id, step_id=f"{task_id}_step_{i}",
                     action=step['action'], result=step['result'], order=i)

    def query_similar_episodes(self, current_task: str) -> List[Dict]:
        # Find similar past tasks
        with self.graph.session() as session:
            result = session.run("""
                MATCH (t:Task)-[:HAS_STEP]->(s:Step)
                WHERE t.description CONTAINS $query
                RETURN t, collect(s) as steps
                ORDER BY t.timestamp DESC
                LIMIT 5
            """, query=current_task)
            return [record.data() for record in result]
```

**Retention**: Configurable (default: 90 days)

**Rationale**:

- Capture workflow sequences
- Learn from failures
- Graph queries for pattern matching

### 6. Entity Memory

**Use Case**: Entidades extraídas (personas, lugares, cosas)

**Example**:

```
From conversation: "I loved dinner at Le Chat Noir in Paris near the Eiffel Tower"

Entities:
  - Restaurant: "Le Chat Noir" (location: Paris, near: Eiffel Tower)
  - City: "Paris"
  - Landmark: "Eiffel Tower"

Relationships:
  - (Le Chat Noir)-[:LOCATED_IN]->(Paris)
  - (Le Chat Noir)-[:NEAR]->(Eiffel Tower)
```

**Storage**: Graph DB (same as Episodic)

**Implementation**:

```python
class EntityMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.graph = GraphDatabase.driver(...)

    def extract_and_store(self, text: str):
        # Extract entities using NER
        entities = self._extract_entities(text)  # LLM or spaCy

        with self.graph.session() as session:
            for entity in entities:
                session.run("""
                    MERGE (e:Entity {name: $name, type: $type})
                    ON CREATE SET e.first_seen = datetime()
                    SET e.last_seen = datetime()
                    WITH e
                    MERGE (u:User {id: $user_id})
                    MERGE (u)-[:MENTIONED]->(e)
                """, name=entity['name'], type=entity['type'],
                     user_id=self.user_id)

    def get_user_entities(self, entity_type: str = None) -> List[Dict]:
        query = """
            MATCH (u:User {id: $user_id})-[:MENTIONED]->(e:Entity)
        """
        if entity_type:
            query += " WHERE e.type = $type"
        query += " RETURN e ORDER BY e.last_seen DESC"

        with self.graph.session() as session:
            result = session.run(query, user_id=self.user_id, type=entity_type)
            return [record["e"] for record in result]
```

**Retention**: Persistent

**Rationale**:

- Structured knowledge extraction
- Relationship modeling
- Precise queries

### 7. Structured RAG

**Use Case**: Dense structured information extraction

**Example**:

```
Email: "Your flight UA1234 to Paris departs Tuesday 10:30am from SFO, Terminal 3"

Structured extraction:
{
  "flight_number": "UA1234",
  "destination": "Paris",
  "date": "Tuesday",
  "time": "10:30am",
  "airport": "SFO",
  "terminal": "3"
}
```

**Storage**: Azure AI Search (with schema)

**Implementation**:

```python
class StructuredRAG:
    def __init__(self):
        self.search_client = SearchClient(...)

    def extract_structured(self, content: str, schema: Dict) -> Dict:
        # Use LLM with schema to extract
        prompt = f"""
Extract structured information from the following text
according to this schema: {schema}

Text: {content}

Return JSON matching schema.
"""
        response = llm.complete(prompt)
        return json.loads(response)

    def store(self, structured_data: Dict):
        # Store with schema validation
        document = {
            "id": str(uuid.uuid4()),
            "data": structured_data,
            "schema_version": "1.0",
            "created_at": datetime.now().isoformat()
        }
        self.search_client.upload_documents([document])

    def query(self, field_queries: Dict) -> List[Dict]:
        # Precise field queries
        filter_expr = " and ".join([f"{k} eq '{v}'" for k, v in field_queries.items()])

        results = self.search_client.search(
            search_text="*",
            filter=filter_expr
        )
        return list(results)
```

**Retention**: Persistent

**Rationale**:

- Superhuman precision and recall
- Field-based queries
- Structured vs unstructured

## Storage Backend Mapping

| Memory Type   | Primary Storage   | Backup/Alternative | Rationale             |
| ------------- | ----------------- | ------------------ | --------------------- |
| Working       | Python dict       | N/A                | Speed                 |
| Short-Term    | Redis             | In-memory          | TTL support           |
| Long-Term     | Azure AI Search   | Mem0               | Vector + hybrid       |
| Persona       | Config + LongTerm | File system        | Dual: static + learn  |
| Episodic      | Neo4j / Cosmos    | JSON logs          | Graph relationships   |
| Entity        | Neo4j / Cosmos    | Vector store       | Relationship modeling |
| Structured    | Azure AI Search   | PostgreSQL         | Schema enforcement    |

## Consequences

### Positive

1. **Optimal Performance**: Each memory type uses best storage for its access pattern
2. **Scalability**: Horizontal scaling per storage type
3. **Cost-Effective**: Pay for what you need (in-memory vs vector vs graph)
4. **Flexibility**: Can swap backends without changing interface

### Negative

1. **Complexity**: Multiple storage systems to manage
2. **Operational Overhead**: Monitoring, backups, versioning per system
3. **Data Consistency**: Need strategy for cross-store consistency

## Implementation Notes

### Memory Manager Interface

```python
class MemoryManager:
    def __init__(self, user_id: str, agent_id: str):
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory(session_id=...)
        self.long_term = LongTermMemory(user_id=user_id)
        self.persona = PersonaMemory(agent_name=agent_id)
        self.episodic = EpisodicMemory(agent_id=agent_id)
        self.entity = EntityMemory(user_id=user_id)
        self.structured = StructuredRAG()

    def add(self, content: str, memory_type: MemoryType):
        """Route to appropriate storage"""

    def retrieve(self, query: str, memory_types: List[MemoryType] = None):
        """Retrieve from multiple memory types"""
```

## References

- ADR-048: AI Agent Memory Architecture
- Azure AI Search: https://learn.microsoft.com/en-us/azure/search/
- Neo4j: https://neo4j.com/docs/
- Redis: https://redis.io/docs/

---

**Decision**: Estrategia de almacenamiento diferenciada por tipo de memoria.
**Rationale**: Optimizar latency, cost, y funcionalidad según access patterns.
