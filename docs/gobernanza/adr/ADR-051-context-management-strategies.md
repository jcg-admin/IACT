---
id: ADR-051
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-050]
---

# ADR-051: Context Management Strategies

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

ADR-050 define arquitectura general de Context Engineering. Este ADR especifica **estrategias detalladas** de planning y manejo práctico de contexto.

### Problem Statement

Necesitamos estrategias concretas para:

1. **Planning**: ¿Qué contexto necesita el agente?
2. **Management**: ¿Cómo gestionar ese contexto dinámicamente?
3. **Optimization**: ¿Cómo mantener contexto relevante y eficiente?

## Decision

Implementar **dual-strategy approach**: Planning Strategies + Practical Strategies.

## Planning Strategies

### 1. Define Clear Results

**Framework**: Responder "¿Cómo se verá el mundo cuando el agente termine?"

**Template**:
```markdown
## Task: [Task Name]

### Desired Result:
- User has: [tangible outcome]
- System shows: [visible change]
- Data state: [database/file changes]

### Success Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

**Example - Travel Booking**:
```python
class TaskDefinition:
    task = "Book trip to Paris"

    desired_result = {
        "user_has": "Confirmed flight + hotel reservation",
        "system_shows": "Booking confirmation with itinerary",
        "data_state": "Booking records in database"
    }

    success_criteria = [
        "Flight matches user preferences (morning, direct)",
        "Hotel within budget and near attractions",
        "Total cost < user budget",
        "Confirmation emails sent"
    ]
```

### 2. Map the Context

**Framework**: "¿Qué información necesita el agente?"

**Context Mapping Template**:
```python
CONTEXT_MAP = {
    "instructions": {
        "source": "system_prompt + few_shots",
        "static": True,
        "priority": "high"
    },
    "user_preferences": {
        "source": "long_term_memory",
        "dynamic": True,
        "retrieval": "semantic_search",
        "priority": "high"
    },
    "available_tools": {
        "source": "tool_registry",
        "dynamic": True,
        "selection": "RAG_over_descriptions",
        "priority": "medium",
        "limit": 30  # Max tools to prevent confusion
    },
    "knowledge_base": {
        "source": "vector_db",
        "dynamic": True,
        "retrieval": "RAG",
        "priority": "medium",
        "top_k": 5
    },
    "conversation_history": {
        "source": "message_buffer",
        "dynamic": True,
        "window": "last_10_turns",
        "priority": "medium"
    }
}
```

**Example - Travel Agent**:
```python
def map_context_for_booking(user_query: str):
    """Map all context sources needed for booking."""

    context_needs = {
        # Static instructions
        "system_prompt": load_prompt("travel_agent_persona.txt"),

        # User preferences (from memory)
        "preferences": memory.retrieve(
            query=user_query,
            memory_types=[MemoryType.LONG_TERM],
            filters={"category": "travel_preferences"}
        ),

        # Available tools (RAG selection)
        "tools": tool_manager.select_tools(
            query=user_query,
            max_tools=30
        ),

        # Knowledge (RAG retrieval)
        "destination_info": rag.retrieve(
            query="Paris travel guide",
            top_k=5
        ),

        # Conversation (recent history)
        "history": conversation.get_last_n_turns(10)
    }

    return context_needs
```

### 3. Create Context Pipelines

**Framework**: "¿Cómo obtendrá el agente esta información?"

**Pipeline Architecture**:
```
User Query
    ↓
┌───────────────────────────────────┐
│   Context Pipeline Orchestrator   │
└───────┬───────────────────────────┘
        │
    ┌───┴────┐
    │ Router │ (determines what context is needed)
    └───┬────┘
        │
    ┌───┴────────────────────────────────────┐
    │                                        │
┌───┴────┐  ┌──────────┐  ┌─────────┐  ┌───┴────┐
│  RAG   │  │ Memory   │  │  Tools  │  │ Runtime│
│ Engine │  │ Retrieval│  │ Selector│  │  State │
└───┬────┘  └────┬─────┘  └────┬────┘  └───┬────┘
    │            │             │            │
    └────────────┴─────────────┴────────────┘
                 │
         ┌───────┴────────┐
         │ Context Builder│
         └───────┬────────┘
                 │
         ┌───────┴────────┐
         │ LLM Call       │
         └────────────────┘
```

**Implementation**:
```python
class ContextPipeline:
    """
    Orchestrates context gathering from multiple sources.
    """

    def __init__(self):
        self.rag_engine = RAGEngine()
        self.memory_retrieval = MemoryManager()
        self.tool_selector = ToolLoadoutManager()
        self.runtime_state = RuntimeStateManager()

    def build_context(self, user_query: str, task_type: str) -> Dict:
        """
        Build complete context for LLM call.

        Args:
            user_query: User's current query
            task_type: Type of task (booking, info, planning, etc.)

        Returns:
            Complete context dict ready for LLM
        """
        # Route to appropriate pipeline
        if task_type == "booking":
            return self._booking_pipeline(user_query)
        elif task_type == "info":
            return self._info_pipeline(user_query)
        # ... other pipelines

    def _booking_pipeline(self, user_query: str) -> Dict:
        """Pipeline for booking tasks."""

        # Step 1: Retrieve user preferences (parallel)
        preferences = self.memory_retrieval.retrieve(
            query=user_query,
            memory_types=[MemoryType.LONG_TERM],
            filters={"category": "travel"}
        )

        # Step 2: Select relevant tools (parallel)
        tools = self.tool_selector.select_tools(
            query=user_query,
            categories=["booking", "search"]
        )

        # Step 3: Retrieve knowledge (parallel)
        knowledge = self.rag_engine.retrieve(
            query=user_query,
            collections=["destinations", "travel_guides"]
        )

        # Step 4: Get runtime state (if resuming task)
        state = self.runtime_state.get_current_task_state()

        # Step 5: Build context
        return {
            "system_prompt": self._get_system_prompt("booking"),
            "user_preferences": preferences,
            "available_tools": tools,
            "knowledge": knowledge,
            "task_state": state,
            "conversation": self._get_recent_history(10)
        }
```

## Practical Strategies

### 1. Agent Scratchpad

**Purpose**: External workspace for agent's "thoughts"

**Implementation**:
```python
class AgentScratchpad:
    """
    Persistent workspace outside context window.
    Agent can write notes, retrieve later.
    """

    def __init__(self, agent_id: str, session_id: str):
        self.agent_id = agent_id
        self.session_id = session_id
        self.storage = {}  # In-memory, could be Redis
        self.embeddings = {}  # For semantic search

    def write(self, key: str, content: str, tags: List[str] = None):
        """Write to scratchpad."""
        self.storage[key] = {
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat()
        }

        # Create embedding for semantic search
        self.embeddings[key] = self._embed(content)

    def read(self, key: str) -> str:
        """Direct read by key."""
        return self.storage.get(key, {}).get("content")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Semantic search over scratchpad."""
        query_emb = self._embed(query)

        # Cosine similarity
        scores = {
            key: cosine_sim(query_emb, emb)
            for key, emb in self.embeddings.items()
        }

        # Top K
        top_keys = sorted(scores, key=scores.get, reverse=True)[:top_k]

        return [
            {"key": k, "content": self.storage[k]["content"], "score": scores[k]}
            for k in top_keys
        ]
```

**Use Case**:
```python
# Agent processing large document
scratchpad = AgentScratchpad(agent_id="doc_analyzer", session_id="sess_123")

# Write key findings
scratchpad.write("key_insight_1", "Document discusses AI safety concerns")
scratchpad.write("key_insight_2", "Mentions regulation need")
scratchpad.write("statistics", "70% of respondents favor regulation")

# Later, when answering query
results = scratchpad.search("What are the main concerns?", top_k=2)
# Returns: key_insight_1, key_insight_2 (without cluttering context)
```

### 2. Memories (Cross-Session)

**Purpose**: Persistent storage across multiple sessions

**Linked to**: ADR-048 (AI Agent Memory)

```python
# Memories store information long-term
memory_manager.add(
    content="User prefers morning flights",
    memory_type=MemoryType.LONG_TERM
)

# Retrieved in future sessions
preferences = memory_manager.retrieve(
    query="flight preferences",
    memory_types=[MemoryType.LONG_TERM]
)
```

### 3. Compressing Context

**Techniques**:

**A. Summarization**:
```python
class ConversationSummarizer:
    def summarize_turns(self, messages: List[Dict]) -> str:
        """Compress multiple turns into summary."""

        prompt = f"""
Summarize this conversation concisely:

{messages}

Focus on:
- User's main request
- Decisions made
- Current state

Summary:
"""
        return llm.complete(prompt)
```

**B. Trimming**:
```python
def trim_conversation(messages: List[Dict], keep_first: int = 1, keep_last: int = 10):
    """Keep first (system) + last N messages."""
    if len(messages) <= keep_first + keep_last:
        return messages

    return [
        *messages[:keep_first],  # System message
        *messages[-keep_last:]   # Recent turns
    ]
```

**C. Aggregation**:
```python
def aggregate_preferences(preferences: List[str]) -> str:
    """Merge similar preferences."""
    # "morning flights" + "early departures" → "Prefers early morning flights"

    prompt = f"""
Merge these preferences into concise statement:
{preferences}

Merged:
"""
    return llm.complete(prompt)
```

### 4. Multi-Agent Systems

**Context Isolation Pattern**:
```python
class MultiAgentContextManager:
    """
    Each agent has isolated context.
    Explicit handoffs between agents.
    """

    def __init__(self):
        self.agent_contexts = {}

    def handoff(self, from_agent: str, to_agent: str, summary: str):
        """
        Handoff from one agent to another.

        Args:
            from_agent: Agent ID handing off
            to_agent: Agent ID receiving
            summary: Compact summary of current state
        """
        # Add handoff message to receiving agent's context
        if to_agent not in self.agent_contexts:
            self.agent_contexts[to_agent] = []

        self.agent_contexts[to_agent].append({
            "role": "system",
            "content": f"Handoff from {from_agent}: {summary}"
        })
```

### 5. Sandbox Environments

**Purpose**: Execute code/process data outside context

**Implementation**:
```python
class SandboxEnvironment:
    """
    Isolated environment for code execution.
    Returns only results, not full execution logs.
    """

    def execute_code(self, code: str, timeout: int = 30) -> Dict:
        """
        Execute code in sandbox.

        Returns:
            {
                "stdout": str,
                "stderr": str,
                "result": Any,
                "execution_time_ms": float
            }
        """
        # Create isolated container
        container = self._create_container()

        try:
            # Run code
            start = time.perf_counter()
            result = container.exec_run(code, timeout=timeout)
            elapsed_ms = (time.perf_counter() - start) * 1000

            return {
                "stdout": result.output.decode('utf-8'),
                "stderr": result.stderr if result.stderr else "",
                "exit_code": result.exit_code,
                "execution_time_ms": elapsed_ms
            }
        finally:
            # Cleanup
            container.stop()
            container.remove()
```

**Agent Usage**:
```python
# Agent needs to process large CSV
# Instead of reading entire CSV into context:

code = """
import pandas as pd
df = pd.read_csv('large_data.csv')
summary = df.describe()
print(summary.to_string())
"""

result = sandbox.execute_code(code)

# Only summary returned to agent context, not full CSV
agent_context.add({
    "role": "system",
    "content": f"Data summary:\n{result['stdout']}"
})
```

### 6. Runtime State Objects

**Purpose**: Container for subtask results

**Implementation**:
```python
class RuntimeState:
    """
    Stores intermediate results for complex multi-step tasks.
    Each subtask can access only relevant state.
    """

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.state = {
            "status": "in_progress",
            "steps_completed": [],
            "current_step": None,
            "results": {},
            "errors": []
        }

    def complete_step(self, step_name: str, result: Any):
        """Mark step as complete, store result."""
        self.state["steps_completed"].append(step_name)
        self.state["results"][step_name] = result

    def get_context_for_step(self, step_name: str) -> Dict:
        """Get only relevant context for this step."""

        # Dependencies for this step
        deps = STEP_DEPENDENCIES.get(step_name, [])

        # Build minimal context
        return {
            "task_id": self.task_id,
            "step": step_name,
            "dependencies": {
                dep: self.state["results"][dep]
                for dep in deps
                if dep in self.state["results"]
            }
        }
```

**Example - Multi-Step Booking**:
```python
# Step 1: Search flights
runtime.complete_step("search_flights", {
    "flights": [flight1, flight2, flight3]
})

# Step 2: Select flight (only needs search results)
context_step2 = runtime.get_context_for_step("select_flight")
# Returns: {"dependencies": {"search_flights": {...}}}

# Step 3: Book flight (only needs selected flight)
context_step3 = runtime.get_context_for_step("book_flight")
# Returns: {"dependencies": {"select_flight": {...}}}
```

## Decision Matrix

| Strategy          | Use When                          | Avoid When                      |
| ----------------- | --------------------------------- | ------------------------------- |
| Scratchpad        | Processing large data             | Simple queries                  |
| Memories          | Cross-session continuity          | Single-shot tasks               |
| Compression       | Context > 80% limit               | Context still small             |
| Multi-Agent       | Distinct specialized tasks        | Single cohesive task            |
| Sandbox           | Code execution, file processing   | Text-only tasks                 |
| Runtime State     | Multi-step complex tasks          | Simple linear workflows         |

## Consequences

### Positive

1. **Systematic Approach**: Clear framework for context management
2. **Flexibility**: Multiple strategies for different scenarios
3. **Performance**: Optimized context = better responses
4. **Scalability**: Handles complex, long-running tasks

### Negative

1. **Implementation Complexity**: Many components to build
2. **Learning Curve**: Team needs to understand all strategies
3. **Debugging Difficulty**: More places for things to go wrong

## References

- ADR-050: Context Engineering Architecture
- Lesson: "Context Engineering for AI Agents"
- Pattern: Agent Scratchpad, Runtime State Objects

---

**Decision**: Implementar dual-strategy approach (Planning + Practical) para context management.
**Rationale**: Proveer framework completo desde planning hasta ejecución práctica.
