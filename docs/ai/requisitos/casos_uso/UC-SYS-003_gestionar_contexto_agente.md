---
id: UC-SYS-003
tipo: caso_uso_sistema
relacionado: [ADR-050, ADR-051, RT-007, RT-008, RF-005, RF-006]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# UC-SYS-003: Gestionar Contexto de Agente

## Descripción

Sistema gestiona contexto dinámico de agentes mediante 4 estrategias core (Write, Select, Compress, Isolate) y mitiga 4 context failures (Poisoning, Distraction, Confusion, Clash).

## Actores

- **Sistema**: Context Manager + Agent (no humano)
- **Sistemas Externos**:
  - Vector DB (para RAG)
  - LLM Provider
  - Scratchpad Storage
  - Token Counter

## Precondiciones

- Context Manager está activo
- Agent tiene context window configurado (e.g., 8K, 128K tokens)
- Vector DB disponible para RAG
- Scratchpad storage accesible

## Flujo Principal: Gestión de Contexto

### 1. WRITE Strategy - Añadir Contenido al Contexto

```
1.1. Agent recibe nueva información para añadir al contexto
     - Tipo: user_message, tool_result, system_instruction, knowledge
     - Content: "User prefers quality hotels over cheap ones"

1.2. Context Manager valida calidad del contenido (RT-008)
     - Relevance score: 0.85 (>= 0.7 threshold) ✓
     - Freshness: < 1 hour old ✓
     - Accuracy: validation_score 0.92 (>= 0.9) ✓
     - Completeness: all required fields present ✓
     - Consistency: no contradictions detected ✓

1.3. Context Manager verifica context window capacity
     - Current usage: 6,500 tokens
     - Max capacity: 8,192 tokens (GPT-4)
     - Usage: 79% (< 80% threshold)
     - Capacity available: YES ✓

1.4. SI quality valid AND capacity available:
     - Add content to context
     - Update context metadata:
       * added_at: timestamp
       * content_type: "user_preference"
       * relevance_score: 0.85
     - Log context addition (RT-008)

1.5. SI capacity NOT available (>= 80%):
     - [Alternate: Auto-Compression Trigger]
```

### 2. SELECT Strategy - Seleccionar Contexto Relevante

```
2.1. Agent recibe query del usuario
     - Query: "Find hotel in Paris"

2.2. Context Manager identifica contexto relevante mediante RAG
     - Embed query: vector_embedding(query)
     - Search vector DB for similar context
     - Candidates found: 15 items

2.3. Context Manager calcula relevance score para cada candidate
     - Semantic similarity: cosine_similarity(query_emb, context_emb)
     - Recency bonus: +0.1 if < 1 hour old
     - User preference match: +0.15 if matches user profile

2.4. Context Manager ranking por relevance score
     - Top 5 selected (threshold: score >= 0.7):
       1. "User prefers quality > price" (score: 0.92)
       2. "User location: Paris" (score: 0.88)
       3. "Budget: $200/night max" (score: 0.82)
       4. "Previous booking: 5-star hotel" (score: 0.78)
       5. "Preference: near Eiffel Tower" (score: 0.75)

2.5. Context Manager inject selected context en agent prompt
     - Format: "Relevant Context:\n- [item 1]\n- [item 2]..."
     - Position: Before user query
     - Total tokens added: ~150 tokens
```

### 3. COMPRESS Strategy - Comprimir Contexto Cuando Necesario

```
3.1. Context Manager monitorea context window usage
     - Current: 7,000 tokens
     - Max: 8,192 tokens
     - Usage: 85% (>= 80% compress threshold)

3.2. Compression trigger activado (RT-007)
     - Strategy: TRIM_OLDEST + SUMMARIZE

3.3. Context Manager identifica contenido compressible
     - Conversation history: 2,500 tokens (old messages)
     - Tool results: 1,200 tokens (already processed)
     - User preferences: 300 tokens (keep, recent)

3.4. Context Manager aplica compression strategies:

     A. TRIM_OLDEST:
        - Remove messages older than 1 hour
        - Tokens freed: 800

     B. SUMMARIZE:
        - Summarize conversation history (last 10 turns)
        - Original: 2,500 tokens
        - Summary: "User discussed hotel booking in Paris.
                   Preferences: quality, near landmarks, budget $200."
        - Compressed: 50 tokens
        - Compression ratio: 50x

     C. ARCHIVE:
        - Move old tool results to scratchpad
        - Tokens freed: 1,200

3.5. Context Manager update context
     - New usage: 4,450 tokens (54%)
     - Tokens freed: 2,550 tokens
     - Compression successful ✓
     - Log compression (RT-007)

3.6. SI compression NOT sufficient (still >= 90%):
     - [Alternate: Aggressive Compression]
```

### 4. ISOLATE Strategy - Separar Contextos para Evitar Contaminación

```
4.1. Agent maneja múltiples tasks simultáneamente
     - Task A: Book hotel Paris
     - Task B: Find restaurant London

4.2. Context Manager crea isolated contexts (sandboxes)
     - Context A: {task: "hotel", location: "Paris", history: [...]}
     - Context B: {task: "restaurant", location: "London", history: [...]}

4.3. Context Manager verifica isolation:
     - Context A NO contiene información de Task B ✓
     - Context B NO contiene información de Task A ✓
     - Zero cross-contamination

4.4. Agent ejecuta Task A con Context A
     - Only Paris hotel info visible
     - London restaurant info NOT visible ✓

4.5. Agent ejecuta Task B con Context B
     - Only London restaurant info visible
     - Paris hotel info NOT visible ✓

4.6. SI tasks require shared context:
     - Create shared context segment
     - Both tasks can access shared segment
     - Private segments remain isolated
```

## Flujos Alternativos

### Alternate 1: Auto-Compression Trigger (80% Threshold)

```
1A.1. Durante WRITE, context usage >= 80%
      - Current: 6,600 tokens
      - Max: 8,192 tokens
      - Usage: 80.5%

1A.2. Context Manager trigger auto-compression
      - Compression strategy: TRIM_OLDEST
      - Target usage: 60% (4,915 tokens)

1A.3. Context Manager compress
      - Tokens freed: 1,685
      - New usage: 4,915 tokens (60%)

1A.4. Context Manager retry WRITE
      - Add new content (200 tokens)
      - Final usage: 5,115 tokens (62%) ✓
      - [Resume: Step 1.4]
```

### Alternate 2: Aggressive Compression (90% Threshold)

```
3A.1. Context usage >= 90% después de compression normal
      - Current: 7,400 tokens (90%)

3A.2. Context Manager trigger aggressive compression
      - Strategy: SUMMARIZE_ALL + REMOVE_NON_ESSENTIAL

3A.3. Context Manager summarize aggressively:
      - Conversation: 3,000 tokens → 100 tokens (summary)
      - Tool results: 2,000 tokens → 200 tokens (key facts)
      - Keep only: current query, critical context

3A.4. Context Manager resultado:
      - New usage: 3,500 tokens (42%)
      - Aggressive compression successful ✓

3A.5. SI still >= 90%:
      - [Alternate: Critical Threshold - Reject New Content]
```

### Alternate 3: Critical Threshold (95%) - Reject New Content

```
1B.1. Context usage >= 95%
      - Current: 7,800 tokens (95%)
      - New content: 500 tokens
      - Would exceed: 8,300 tokens > 8,192 max

1B.2. Context Manager reject new content
      - Error: ContextWindowExceeded
      - Message: "Context window at critical capacity (95%).
                 Compression did not free enough space.
                 Cannot add new content."

1B.3. Context Manager log critical event
      - Warning level: CRITICAL
      - Metrics: context.window.critical_exceeded++

1B.4. Agent must decide:
      - Option A: Remove old context manually
      - Option B: Use scratchpad for offloading
      - Option C: Split into multiple agent calls
```

### Alternate 4: Context Poisoning Detection

```
2A.1. Agent añade contenido al contexto
      - Content: "The Eiffel Tower is in London"
      - (Hallucination / incorrect fact)

2A.2. Context Manager valida accuracy (RT-008)
      - Fact check: "Eiffel Tower location"
      - Validation result: INVALID
      - Reason: "Eiffel Tower is in Paris, not London"
      - Accuracy score: 0.1 (< 0.9 threshold)

2A.3. Context Manager REJECT poisoned content
      - Content NOT added to context
      - Log poisoning attempt:
         * poisoned_content: "Eiffel Tower in London"
         * validation_result: INVALID
         * reason: "Factual error detected"

2A.4. Metrics: context.poisoning_attempts++

2A.5. Agent receives validation error:
      - "Content rejected: factual inaccuracy detected"
      - Agent can retry with corrected content
```

### Alternate 5: Context Distraction (Too Much History)

```
3B.1. Conversation history grows large
      - 50 messages in history
      - 5,000 tokens consumed by old messages
      - Agent performance degrading

3B.2. Context Manager detect distraction (RT-008)
      - History length: 50 messages
      - Threshold: 20 messages
      - Distraction detected ✓

3B.3. Context Manager apply SUMMARIZATION
      - Summarize messages 1-40 (oldest)
      - Original: 4,000 tokens
      - Summary: "User and agent discussed multiple topics:
                 hotel booking, flights, car rental.
                 Decisions made: [key decisions]"
      - Compressed: 200 tokens

3B.4. Context Manager keep recent messages (41-50)
      - Recent: 1,000 tokens (keep verbatim)
      - Total: 1,200 tokens (from 5,000)

3B.5. Distraction mitigated ✓
```

### Alternate 6: Context Confusion (Too Many Tools)

```
4A.1. Agent has 45 tools available
      - All tools in context: 3,500 tokens
      - Threshold: 30 tools (RT-008)
      - Confusion risk: HIGH

4A.2. Context Manager detect confusion
      - Tool count: 45 > 30
      - Confusion detected ✓

4A.3. Context Manager apply RAG OVER TOOLS (ADR-050)
      - Remove all tool descriptions from context
      - Implement tool retrieval on demand

4A.4. When agent needs tool:
      - Agent: "I need a tool to search flights"
      - Context Manager: search_tools(query="search flights")
      - Results: [search_flights, book_flights]
      - Inject only relevant tools (2 tools, 150 tokens)

4A.5. Context freed: 3,350 tokens (from removing 45 tools)
      - Confusion mitigated ✓
```

### Alternate 7: Context Clash (Contradictory Information)

```
2B.1. Context contiene información contradictoria
      - Item 1: "User prefers budget hotels"
      - Item 2: "User prefers luxury 5-star hotels"
      - (Contradicción)

2B.2. Context Manager detect clash (RT-008)
      - Contradiction detected between Item 1 and Item 2
      - Clash identified ✓

2B.3. Context Manager resolve clash:
      - Strategy: PREFER_RECENT (more recent overrides older)
      - Item 1 timestamp: 2 days ago
      - Item 2 timestamp: 1 hour ago
      - Resolution: Keep Item 2, remove Item 1

2B.4. Context Manager update context:
      - Remove: "User prefers budget hotels"
      - Keep: "User prefers luxury 5-star hotels"
      - Clash resolved ✓

2B.5. Log clash resolution:
      - Contradictory items detected
      - Resolution strategy: PREFER_RECENT
      - Metrics: context.clashes_resolved++
```

### Alternate 8: Scratchpad Offloading

```
3C.1. Agent needs to offload large context externally
      - Situation: Processing 100 documents
      - Each doc: 500 tokens
      - Total: 50,000 tokens (exceeds 8K window)

3C.2. Context Manager use SCRATCHPAD (ADR-050)
      - Write all documents to external scratchpad
      - Each document gets unique ID

3C.3. Agent context contains only IDs:
      - "Documents: [doc_1, doc_2, ..., doc_100]"
      - Tokens in context: 200 tokens (IDs only)

3C.4. When agent needs specific document:
      - Agent: "Retrieve doc_15"
      - Scratchpad: Returns doc_15 content
      - Temporarily inject doc_15 (500 tokens)

3C.5. After processing doc_15:
      - Remove doc_15 from context
      - Tokens freed: 500

3C.6. Scratchpad enables processing 50K tokens with 8K window ✓
```

### Alternate 9: Multi-Turn Conversation State Management

```
4B.1. Long conversation (30 turns)
      - Each turn adds messages
      - Context growing: 6,000 tokens

4B.2. Context Manager apply RUNTIME STATE pattern (ADR-050)
      - Separate: Persistent State vs Ephemeral State

4B.3. Persistent State (keep in context):
      - User preferences: 300 tokens
      - Current goal: 50 tokens
      - Key decisions: 200 tokens
      - Total: 550 tokens

4B.4. Ephemeral State (offload to scratchpad):
      - Old messages: 4,500 tokens → scratchpad
      - Tool results: 950 tokens → scratchpad

4B.5. Context now contains:
      - Persistent state: 550 tokens
      - Recent messages (last 5 turns): 500 tokens
      - Total: 1,050 tokens (from 6,000)

4B.6. Context optimized for long conversations ✓
```

## Postcondiciones

### Éxito

- Contexto gestionado dentro de limits (< 80% usage)
- Contenido validado (quality score >= 0.7)
- Context failures mitigados (poisoning, distraction, confusion, clash)
- Agent tiene contexto relevante para task
- Performance maintained (latency targets met)

### Fallo

- Context window exceeded despite compression
- Content quality below threshold (rejected)
- Context poisoning detected (hallucination)
- Clash irresolvable (contradictory info)

## Requisitos No Funcionales

- **Performance** (RT-007):
  - Compression latency: < 1s
  - Validation latency: < 100ms
  - RAG retrieval: < 200ms
  - Scratchpad write/read: < 50ms

- **Quality** (RT-008):
  - Relevance score: >= 0.7
  - Accuracy score: >= 0.9
  - Freshness: < 1 hour preferred
  - Consistency: 0 contradictions

- **Capacity**:
  - Warning threshold: 70%
  - Compression threshold: 80%
  - Critical threshold: 95%

## Métricas

```python
CONTEXT_MANAGEMENT_METRICS = {
    "context_window_usage_avg": 0.65,  # 65% average
    "context_window_usage_p95": 0.82,  # 82% p95

    "compression_triggered_count": 150,  # per day
    "compression_ratio_avg": 3.5,  # 3.5x compression
    "compression_latency_p95": 800,  # ms

    "poisoning_attempts_blocked": 12,
    "distraction_mitigations": 45,
    "confusion_mitigations": 8,
    "clashes_resolved": 23,

    "context_quality_score_avg": 0.84,
    "relevance_score_avg": 0.79,
    "accuracy_score_avg": 0.94,

    "scratchpad_writes": 230,
    "scratchpad_reads": 450,

    "rag_over_tools_calls": 120,
}
```

## Diagramas

### Secuencia: WRITE con Auto-Compression

```
Agent        ContextManager  VectorDB  Scratchpad  LLM
 |                 |            |         |          |
 |--add_content--->|            |         |          |
 |                 |--validate->|         |          |
 |                 |<--valid----|         |          |
 |                 |            |         |          |
 |                 |--check_capacity      |          |
 |                 | (usage: 82% >= 80%)  |          |
 |                 |            |         |          |
 |                 |--trigger_compression |          |
 |                 |            |         |          |
 |                 |--summarize-----------|--------->|
 |                 |            |         |<-summary-|
 |                 |            |         |          |
 |                 |--offload------------->|         |
 |                 |            |<-success-|         |
 |                 |            |         |          |
 |                 |--new_usage: 62% ✓    |          |
 |                 |            |         |          |
 |<--success-------|            |         |          |
 |                 |            |         |          |
```

### Flujo: Context Failure Mitigation

```
┌─────────────────────────────────────────────────────────┐
│              Context Failure Detection                  │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
        ┌──────────┐
        │ Validate │
        │ Content  │
        └────┬─────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────┐
│Poisoning?│  │Distraction│
│(accuracy)│  │(history) │
└────┬─────┘  └────┬─────┘
     │             │
     │             ▼
     │       ┌──────────┐
     │       │Summarize │
     │       │History   │
     │       └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐  ┌──────────┐
│ Reject   │  │Confusion?│
│ Content  │  │(>30 tools)│
└──────────┘  └────┬─────┘
                   │
                   ▼
             ┌──────────┐
             │RAG over  │
             │Tools     │
             └────┬─────┘
                  │
                  ▼
            ┌──────────┐
            │Clash?    │
            │(conflict)│
            └────┬─────┘
                 │
                 ▼
           ┌──────────┐
           │Resolve   │
           │(recent)  │
           └──────────┘
```

## Referencias

- ADR-050: Context Engineering Architecture
- ADR-051: Context Management Strategies
- RT-007: Context Window Limits
- RT-008: Context Quality Standards
- RF-005: Context Validation and Compression
- RF-006: Context Failure Mitigation

---

**Caso de Uso**: Sistema gestiona contexto dinámico mediante Write, Select, Compress, Isolate y mitiga context failures.
**Objetivo**: Mantener context window optimizado, relevante, y libre de contaminación.
