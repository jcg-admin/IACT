---
id: ADR-AI-008-ai-memory-architecture
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-046, ADR-047]
---

# ADR-048: AI Agent Memory Architecture

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

### Problem Statement

Los agentes AI actuales en el proyecto son **stateless** (sin estado):

- Cada interacción empieza desde cero
- No recuerdan contexto de conversaciones previas
- No aprenden de interacciones pasadas
- No personalizan experiencia del usuario
- No mejoran con el tiempo

**Impacto medido**:

- Usuario debe repetir preferencias en cada sesión
- Agentes cometen errores ya corregidos anteriormente
- Experiencia frustrante y repetitiva
- No hay continuidad entre sesiones

### Business Value

Dos beneficios principales de agentes AI:

1. **Tool calling**: Completar tareas mediante herramientas
2. **Self-improvement**: Mejorar con el tiempo mediante memoria

**Memory is at the foundation of creating self-improving agents.**

### Technical Context

Tipos de memoria necesarios:

1. **Working Memory**: Scratch paper durante tarea actual
2. **Short-Term Memory**: Contexto de conversación actual
3. **Long-Term Memory**: Preferencias persistentes entre sesiones
4. **Persona Memory**: "Personalidad" consistente del agente
5. **Episodic Memory**: Secuencia de pasos (éxitos/fallos)
6. **Entity Memory**: Entidades extraídas (personas, lugares, cosas)

## Decision

Implementar **Memory Layer** para agentes AI con arquitectura de 3 capas:

### 1. Memory Management Pipeline

```
User Input → Agent Processing → Memory Operations
                                       ↓
                              ┌────────┴────────┐
                              │                 │
                         EXTRACTION          UPDATE
                              │                 │
                         ┌────┴────┐      ┌────┴────┐
                         │ LLM     │      │ LLM     │
                         │ Extract │      │ Decide  │
                         └────┬────┘      └────┬────┘
                              │                 │
                              └────────┬────────┘
                                       ↓
                              HYBRID DATA STORE
                         ┌──────────┬──────────┬──────────┐
                         │ Vector   │ Graph    │ Key-Value│
                         │ Store    │ Store    │ Store    │
                         └──────────┴──────────┴──────────┘
```

**Fase 1 - Extraction**:

- Messages enviados a memory service
- LLM resume historial de conversación
- Extrae nuevos memories (facts, preferences, context)

**Fase 2 - Update**:

- LLM decide: ADD | MODIFY | DELETE
- Actualiza hybrid data store
- Maneja relationships entre entidades (graph)

### 2. Memory Types Implementation

| Memory Type       | Storage        | Retention        | Use Case                                 |
| ----------------- | -------------- | ---------------- | ---------------------------------------- |
| Working           | In-memory dict | Task duration    | Scratch computations                     |
| Short-Term        | Session store  | Single session   | Current conversation context             |
| Long-Term         | Vector DB      | Persistent       | User preferences, historical facts       |
| Persona           | Config + KB    | Permanent        | Agent personality and role               |
| Episodic          | Graph DB       | Configurable     | Task workflows, success/failure patterns |
| Entity            | Graph DB       | Persistent       | Extracted entities and relationships     |
| Structured RAG    | Vector + Graph | Persistent       | Dense structured information             |

### 3. Storage Backends

**Primary**: Azure AI Search

- Vector search para semantic similarity
- Structured RAG para dense information extraction
- Graph capabilities para entity relationships
- Soporta hybrid queries

**Alternative**: Mem0 Service

- Managed memory layer
- Built-in extraction pipeline
- Multi-backend support (vector, graph, key-value)
- Memory versioning

### 4. Self-Improvement Pattern

**Knowledge Agent Pattern**:

```python
# Agente observador
class KnowledgeAgent:
    def observe_conversation(self, user_msg, agent_response):
        # 1. Identificar información valiosa
        if self.is_worth_storing(user_msg, agent_response):
            # 2. Extraer y resumir
            knowledge = self.extract_knowledge(conversation)

            # 3. Guardar en knowledge base
            self.store_in_kb(knowledge)

    def augment_query(self, user_query):
        # 4. Recuperar contexto relevante
        relevant = self.retrieve_from_kb(user_query)

        # 5. Augmentar prompt
        return f"{relevant}\n\nUser Query: {user_query}"
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Working    │  │ Short-Term   │  │  Long-Term   │  │
│  │   Memory     │  │   Memory     │  │   Memory     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Memory Manager │
                    │  (memory.py)    │
                    └────────┬────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
    ┌─────┴─────┐                      ┌───────┴───────┐
    │ Extraction│                      │    Update     │
    │  Engine   │                      │    Engine     │
    └─────┬─────┘                      └───────┬───────┘
          │                                     │
          └──────────────────┬──────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Storage Layer  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴─────┐
    │  Vector   │     │   Graph   │     │ Key-Value │
    │   Store   │     │   Store   │     │   Store   │
    └───────────┘     └───────────┘     └───────────┘
```

### Memory Operations

```python
class MemoryManager:
    def add(self, content: str, memory_type: MemoryType):
        """Add new memory"""

    def retrieve(self, query: str, top_k: int = 5) -> List[Memory]:
        """Retrieve relevant memories"""

    def update(self, memory_id: str, new_content: str):
        """Update existing memory"""

    def delete(self, memory_id: str):
        """Delete memory (forgetting)"""

    def search(self, query: str, filters: Dict = None) -> List[Memory]:
        """Semantic search in memories"""
```

## Consequences

### Positive

1. **Self-Improving Agents**:

   - Learn from past interactions
   - Avoid repeating mistakes
   - Improve recommendations over time

2. **Enhanced User Experience**:

   - Personalized interactions
   - Context continuity across sessions
   - No need to repeat preferences

3. **Reflective Behavior**:

   - Agents can analyze past actions
   - Learn from successes and failures
   - Adapt strategies

4. **Autonomous Operation**:

   - Draw on stored knowledge independently
   - Proactive suggestions based on history
   - Anticipate user needs

5. **Structured Knowledge**:
   - Dense information extraction (Structured RAG)
   - Entity relationships (graph)
   - Precise queries ("What flight to Paris on Tuesday?")

### Negative

1. **Latency**:

   - Memory operations add overhead
   - Mitigation: Cache, fast models for check, async ops

2. **Cost**:

   - Vector DB storage costs
   - LLM calls for extraction/update
   - Mitigation: Cold storage for old data, cheaper models

3. **Complexity**:

   - Multiple storage backends
   - Pipeline management
   - Mitigation: Abstraction layer, managed services (Mem0)

4. **Privacy**:

   - Storing user data long-term
   - Mitigation: Encryption, user control, GDPR compliance

5. **Maintenance**:
   - Knowledge base can grow stale
   - Mitigation: Memory versioning, TTL, user feedback

## Implementation Plan

### Phase 1: Foundation (Sprint 1-2)

- [ ] Implement MemoryManager base class
- [ ] Working memory (in-memory dict)
- [ ] Short-term memory (session store)
- [ ] Basic tests

### Phase 2: Persistent Memory (Sprint 3-4)

- [ ] Azure AI Search integration
- [ ] Long-term memory (vector store)
- [ ] Retrieval functions
- [ ] Tests with real data

### Phase 3: Advanced Types (Sprint 5-6)

- [ ] Persona memory
- [ ] Episodic memory (graph)
- [ ] Entity memory (graph)
- [ ] Knowledge Agent pattern

### Phase 4: Optimization (Sprint 7-8)

- [ ] Latency optimization (caching)
- [ ] Cost optimization (cold storage)
- [ ] Memory versioning
- [ ] Monitoring and metrics

## Metrics

- **Memory retrieval latency**: < 100ms (p95)
- **Storage cost**: < $50/month per 10k users
- **User satisfaction**: +30% (measured via feedback)
- **Agent accuracy improvement**: +20% over time

## References

- Lesson: "Understanding AI Agent Memory"
- Mem0 Documentation: https://docs.mem0.ai/
- Azure AI Search: https://learn.microsoft.com/en-us/azure/search/
- ADR-046: PlacementAgent architecture
- Pattern: Knowledge Agent for self-improvement

## Related Decisions

- ADR-046: Clasificacion Automatica de Artefactos (agent architecture)
- ADR-047: Relacion gobernanza-dominios (context management)

---

**Decision**: Implementar Memory Layer con pipeline extraction-update y hybrid storage.
**Rationale**: Habilitar self-improving agents y mejor UX mediante memoria persistente.
**Trade-offs**: Latency y costo vs. inteligencia y personalización.
