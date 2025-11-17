---
id: ADR-AI-010-context-engineering-architecture
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-048, ADR-049]
---

# ADR-050: Context Engineering Architecture

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

### Problem Statement

Los agentes AI necesitan manejar **contexto dinámico** que crece y cambia:

**Problemas actuales**:
- Context window tiene tamaño limitado (4k-128k tokens)
- Información irrelevante distrae al modelo
- Información conflictiva causa decisiones inconsistentes
- Conversaciones largas degradan performance
- No hay estrategia sistemática para gestionar contexto

**Impacto medido**:
- Degradación de calidad después de 10+ turnos conversacionales
- Hallucinations incrementan con contexto grande
- Latency aumenta linealmente con context size
- Costos de API aumentan (charged per token en context)

### Context Engineering vs Prompt Engineering

| Aspecto              | Prompt Engineering         | Context Engineering                |
| -------------------- | -------------------------- | ---------------------------------- |
| **Scope**            | Static instructions        | Dynamic information management     |
| **Focus**            | Single interaction         | Multi-turn conversations           |
| **Content**          | System prompts, few-shots  | All context types                  |
| **Goal**             | Guide AI with rules        | Ensure right info at right time    |
| **Complexity**       | Low (one-time setup)       | High (continuous management)       |
| **Time Dimension**   | Stateless                  | Stateful across sessions           |

**Context Engineering = Prompt Engineering + Dynamic Info Management**

### Types of Context

Context no es una sola cosa - viene de múltiples fuentes:

1. **Instructions** (static):
   - System prompts
   - Few-shot examples
   - Tool descriptions
   - Agent persona

2. **Knowledge** (dynamic):
   - RAG retrievals
   - Database queries
   - Long-term memories
   - User preferences

3. **Tools** (functional):
   - Tool definitions
   - Tool call results
   - MCP server responses

4. **Conversation History** (temporal):
   - User messages
   - Assistant responses
   - Multi-turn dialogue

5. **User Preferences** (persistent):
   - Learned likes/dislikes
   - Past decisions
   - Feedback history

## Decision

Implementar **Context Engineering System** con arquitectura de gestión activa de contexto.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Context Engineering System                  │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │   Write    │  │   Select   │  │  Compress  │  │  Isolate   ││
│  │  Strategy  │  │  Strategy  │  │  Strategy  │  │  Strategy  ││
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘│
│        │               │               │               │        │
│        └───────────────┴───────────────┴───────────────┘        │
│                            │                                    │
│                    ┌───────┴────────┐                          │
│                    │ Context Manager│                          │
│                    └───────┬────────┘                          │
│                            │                                    │
│        ┌───────────────────┼───────────────────┐              │
│        │                   │                   │              │
│   ┌────┴─────┐      ┌─────┴──────┐     ┌─────┴──────┐       │
│   │Scratchpad│      │  Memories  │     │ Summarizer │       │
│   └────┬─────┘      └─────┬──────┘     └─────┬──────┘       │
│        │                   │                   │              │
└────────┼───────────────────┼───────────────────┼──────────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                    ┌────────┴────────┐
                    │  LLM Context    │
                    │   Window        │
                    └─────────────────┘
```

### Core Strategies

#### 1. Write Strategy

**Problema**: ¿Qué información debe entrar al contexto?

**Estrategias**:

```python
class ContextWriter:
    def write_instructions(self, system_prompt: str, few_shots: List[Dict]):
        """Write static instructions to context."""

    def write_knowledge(self, query: str, top_k: int = 3):
        """Write retrieved knowledge via RAG."""

    def write_tools(self, tool_loadout: List[str]):
        """Write selected tool definitions."""

    def write_conversation(self, message: Dict):
        """Write user/assistant message."""
```

**Validation**:
- Relevance check before adding
- Deduplication (no repeat info)
- Priority ranking

#### 2. Select Strategy

**Problema**: ¿Qué información es relevante ahora?

**Estrategias**:

```python
class ContextSelector:
    def select_tools_by_rag(self, query: str, max_tools: int = 30):
        """RAG over tool descriptions to select relevant tools."""
        # Research shows < 30 tools prevents confusion

    def select_memories(self, query: str, filters: Dict):
        """Select relevant memories for current task."""

    def select_conversation_window(self, last_n: int = 10):
        """Select recent conversation turns."""
```

**Techniques**:
- RAG over tool descriptions
- Semantic similarity for memories
- Recency-based for conversation

#### 3. Compress Strategy

**Problema**: Contexto crece más allá del límite

**Estrategias**:

```python
class ContextCompressor:
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """Compress conversation into summary."""
        # "User wants to book Paris trip. Prefers morning flights. Budget: $2k."

    def trim_old_messages(self, keep_last_n: int = 10):
        """Remove oldest messages, keep recent."""

    def compress_knowledge(self, facts: List[str]) -> str:
        """Compress multiple facts into compact representation."""
```

**Techniques**:
- Summarization (LLM-based or extractive)
- Trimming (keep first + last N)
- Aggregation (merge similar facts)

#### 4. Isolate Strategy

**Problema**: Evitar contamination entre contextos

**Estrategias**:

```python
class ContextIsolator:
    def create_scratchpad(self) -> Scratchpad:
        """Workspace outside main context."""
        # For processing large data without cluttering context

    def create_sandbox(self) -> SandboxEnv:
        """Isolated environment for code execution."""
        # Run code, return only results

    def create_runtime_state(self) -> Dict:
        """Container for subtask results."""
        # Store step-by-step results separately
```

**Techniques**:
- Scratchpad (temporary workspace)
- Sandbox (isolated execution)
- Runtime state objects (subtask containers)

### Context Management Pipeline

```
New Information arrives
        ↓
1. VALIDATE (is it relevant?)
        ↓ Yes
2. WRITE (add to appropriate storage)
        ↓
3. SELECT (what's needed now?)
        ↓
4. CHECK SIZE (within limits?)
        ↓ No
5. COMPRESS (summarize/trim)
        ↓
6. ISOLATE (if needed)
        ↓
7. INJECT to LLM context window
```

## Implementation Strategies

### 1. Agent Scratchpad

**Purpose**: Notes for current session, outside context window

```python
class AgentScratchpad:
    """
    Workspace for agent to take notes without cluttering context.
    """

    def __init__(self):
        self.notes: Dict[str, Any] = {}
        self.file_path = "/tmp/scratchpad.json"

    def write_note(self, key: str, value: Any):
        """Write note to scratchpad."""
        self.notes[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._persist()

    def read_note(self, key: str) -> Any:
        """Read note from scratchpad."""
        return self.notes.get(key, {}).get("value")

    def get_relevant_notes(self, query: str) -> List[Dict]:
        """Retrieve notes relevant to query."""
        # Semantic search over notes
```

**Use Case**:
- Agent processing large document
- Notes key findings in scratchpad
- Retrieves only relevant notes when needed
- Main context stays clean

### 2. Context Compression

**Purpose**: Reduce context size when approaching limits

```python
class ContextCompressor:
    def __init__(self, llm, max_tokens: int = 4000):
        self.llm = llm
        self.max_tokens = max_tokens

    def compress_if_needed(self, messages: List[Dict]) -> List[Dict]:
        """Compress context if exceeding threshold."""
        current_tokens = self._count_tokens(messages)

        if current_tokens > self.max_tokens * 0.8:  # 80% threshold
            # Summarize middle messages, keep first + last
            summary = self._summarize_middle(messages)

            return [
                messages[0],  # System message
                {"role": "system", "content": f"Previous conversation: {summary}"},
                *messages[-5:]  # Last 5 messages
            ]

        return messages
```

### 3. Tool Loadout Management (RAG over Tools)

**Purpose**: Prevent context confusion by limiting tools

```python
class ToolLoadoutManager:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.max_tools = 30  # Research threshold

    def select_tools(self, user_query: str) -> List[ToolDefinition]:
        """
        Select most relevant tools via RAG.

        Prevents context confusion by limiting tool count.
        """
        # Embed all tool descriptions once
        tool_embeddings = self.vector_store.get_all("tool_descriptions")

        # Semantic search
        relevant_tools = self.vector_store.search(
            query=user_query,
            top_k=self.max_tools,
            collection="tool_descriptions"
        )

        return [self._load_tool(t["name"]) for t in relevant_tools]
```

### 4. Multi-Agent Context Isolation

**Purpose**: Each agent has own context window

```python
class MultiAgentContextManager:
    def __init__(self):
        self.agent_contexts: Dict[str, List[Dict]] = {}

    def get_agent_context(self, agent_id: str) -> List[Dict]:
        """Get isolated context for specific agent."""
        return self.agent_contexts.get(agent_id, [])

    def share_context(self, from_agent: str, to_agent: str, info: str):
        """Explicitly share context between agents."""
        shared_message = {
            "role": "system",
            "content": f"Information from {from_agent}: {info}"
        }

        self.agent_contexts[to_agent].append(shared_message)
```

## Context Failures and Mitigations

### 1. Context Poisoning

**What**: Hallucination enters context, repeatedly referenced

**Example**: Agent hallucinates non-existent flight, keeps trying to book it

**Mitigation**:
```python
class ContextValidator:
    def validate_before_add(self, info: str, source: str) -> bool:
        """Validate information before adding to context."""
        if source == "llm_generation":
            # Verify with external API
            is_valid = self._verify_with_api(info)
            if not is_valid:
                logger.warning(f"Context poisoning detected: {info}")
                return False

        return True

    def quarantine_suspicious(self, info: str):
        """Isolate suspicious info, don't propagate."""
        self.quarantine_storage.add(info)
        # Start fresh context thread
```

### 2. Context Distraction

**What**: Too much history, model focuses on past instead of task

**Example**: Agent obsesses over old backpacking stories, ignores current request

**Mitigation**:
```python
def summarize_periodically(messages: List[Dict], every_n: int = 10) -> List[Dict]:
    """Summarize every N turns to prevent distraction."""
    if len(messages) > every_n:
        # Keep first (system) + last N
        recent = messages[-every_n:]
        old = messages[1:-every_n]  # Exclude system message

        summary = llm.summarize(old)

        return [
            messages[0],  # System
            {"role": "system", "content": f"Previous context: {summary}"},
            *recent
        ]

    return messages
```

### 3. Context Confusion

**What**: Too many tools cause bad tool calls

**Example**: Agent has 100 tools, calls wrong ones

**Mitigation**:
```python
def limit_tool_loadout(query: str, all_tools: List, max_tools: int = 30):
    """RAG over tools, select < 30 most relevant."""
    # Embed tool descriptions
    tool_embeddings = embed_tools(all_tools)

    # Semantic search
    relevant = semantic_search(query, tool_embeddings, top_k=max_tools)

    return relevant  # Only these tools in context
```

### 4. Context Clash

**What**: Conflicting information in context

**Example**: User says "economy" then "business class" - both in context

**Mitigation**:
```python
class ContextPruner:
    def prune_conflicts(self, new_info: str, context: List[Dict]):
        """Remove conflicting old information."""
        # Detect contradiction
        if self._is_contradictory(new_info, context):
            # Remove old preference
            context = self._remove_conflicting(new_info, context)

        # Add new info
        context.append({"role": "user", "content": new_info})

        return context

    def use_scratchpad_for_reconciliation(self, preferences: List[str]) -> str:
        """Use scratchpad to reconcile conflicts."""
        scratchpad_prompt = f"""
Reconcile these conflicting preferences:
{preferences}

What is the user's final preference?
"""
        final = llm.complete(scratchpad_prompt)
        return final
```

## Consequences

### Positive

1. **Improved Reliability**: Less hallucinations, better decisions
2. **Better Performance**: Focused context = better responses
3. **Cost Optimization**: Smaller context = lower API costs
4. **Scalability**: Handles long conversations without degradation
5. **User Experience**: Consistent, relevant responses

### Negative

1. **Complexity**: More moving parts to manage
2. **Latency**: Compression/selection adds overhead
3. **State Management**: Must track scratchpads, summaries, etc.
4. **Risk of Information Loss**: Aggressive pruning may lose important details

## Implementation Plan

### Phase 1: Basic Context Management (Sprint 1-2)
- [ ] Context size monitoring
- [ ] Basic compression (trim old messages)
- [ ] Scratchpad implementation

### Phase 2: Advanced Selection (Sprint 3-4)
- [ ] RAG over tools (loadout management)
- [ ] Memory selection
- [ ] Relevance filtering

### Phase 3: Failure Mitigation (Sprint 5-6)
- [ ] Context validation (poisoning prevention)
- [ ] Periodic summarization (distraction prevention)
- [ ] Conflict detection and pruning (clash prevention)

### Phase 4: Optimization (Sprint 7-8)
- [ ] Runtime state objects
- [ ] Multi-agent context isolation
- [ ] Performance tuning

## Metrics

- Context size: < 80% of max window
- Compression ratio: 10:1 (10 messages → 1 summary)
- Tool loadout: ≤ 30 tools per query
- Poisoning detection rate: > 95%
- Latency overhead: < 200ms for compression

## References

- Lesson: "Context Engineering for AI Agents"
- Research: Tool confusion with >30 tools
- ADR-048: AI Agent Memory Architecture
- Pattern: Scratchpad, RAG over tools

---

**Decision**: Implementar Context Engineering System con strategies activas de write/select/compress/isolate.
**Rationale**: Manejar contexto dinámico de manera sistemática para reliability y performance.
