---
id: RF-004
tipo: requisito_funcional
relacionado: [UC-SYS-002, ADR-048, ADR-049]
prioridad: media
estado: propuesto
fecha: 2025-11-16
---

# RF-004: Knowledge Agent for Self-Improvement

## Especificación

El sistema DEBE implementar Knowledge Agent pattern para:

1. Observar conversaciones entre user y agent
2. Identificar información valiosa para almacenar
3. Extraer y almacenar knowledge en knowledge base
4. Augmentar futuras queries con knowledge relevante

## Criterios de Aceptación

### Escenario 1: Identificar Información Valiosa

```gherkin
Given conversation:
    User: "I have a ski injury, so avoid advanced slopes"
    Agent: "Understood, I'll recommend beginner-intermediate only"
When KnowledgeAgent.is_worth_storing(conversation)
Then return True
  And reason = "user_preference"
  And confidence >= 0.8
```

### Escenario 2: Extraer Knowledge de Conversación

```gherkin
Given conversation:
    User: "I have a ski injury, so avoid advanced slopes"
    Agent: "Understood, I'll recommend beginner-intermediate only"
When KnowledgeAgent.extract_knowledge(conversation)
Then extracted_knowledge = {
    "type": "user_preference",
    "content": "User has ski injury; avoid advanced slopes",
    "domain": "skiing",
    "confidence": 0.9,
    "source": "conversation",
    "timestamp": "2025-11-16T10:30:00Z"
}
```

### Escenario 3: Almacenar en Knowledge Base

```gherkin
Given extracted_knowledge from previous scenario
When KnowledgeAgent.store_in_kb(extracted_knowledge, user_id="user_123")
Then knowledge stored in long_term_memory
  And memory_type = "long_term"
  And metadata includes:
    - source: "knowledge_agent"
    - confidence: 0.9
    - extracted_at: timestamp
```

### Escenario 4: Augmentar Query con Knowledge

```gherkin
Given knowledge_base contains:
    "User has ski injury; avoid advanced slopes"
  And user_query = "Recommend a ski resort"
When KnowledgeAgent.augment_query(user_query, user_id="user_123")
Then augmented_prompt = """
    Relevant context:
    - User has ski injury; avoid advanced slopes

    User Query: Recommend a ski resort
"""
  And retrieval latency < 100ms
```

### Escenario 5: No Store Trivial Information

```gherkin
Given conversation:
    User: "Hello"
    Agent: "Hi! How can I help you?"
When KnowledgeAgent.is_worth_storing(conversation)
Then return False
  And reason = "trivial_greeting"
  And confidence < 0.3
```

### Escenario 6: Extract Multiple Facts

```gherkin
Given conversation:
    User: "I love Le Chat Noir restaurant in Paris near Eiffel Tower"
When KnowledgeAgent.extract_knowledge(conversation)
Then extracted_knowledge contains multiple facts:
    - "User loves Le Chat Noir restaurant"
    - "Le Chat Noir is in Paris"
    - "Le Chat Noir is near Eiffel Tower"
  And each fact stored separately
```

### Escenario 7: Update Existing Knowledge

```gherkin
Given knowledge_base contains:
    "User prefers morning flights"
  And new conversation:
    User: "Actually, I now prefer evening flights"
When KnowledgeAgent.extract_and_update(conversation)
Then old knowledge marked as outdated
  And new knowledge = "User prefers evening flights"
  And metadata includes:
    - supersedes: old_memory_id
    - updated_at: timestamp
```

### Escenario 8: Fast Check with Cheap Model

```gherkin
Given conversation occurs
When KnowledgeAgent.is_worth_storing(conversation)
Then uses cheap/fast model (GPT-3.5 or similar)
  And latency < 500ms
  And cost < $0.001
  And only IF is_worth_storing == True:
      Then use expensive model for extraction
```

### Escenario 9: Cold Storage for Unused Knowledge

```gherkin
Given knowledge in KB has not been retrieved in 365 days
When KnowledgeAgent.optimize_storage()
Then old knowledge moved to cold storage (blob)
  And removed from vector index
  And cost reduced by 80%
  And still accessible (but slower)
```

### Escenario 10: Knowledge Agent Observes Asynchronously

```gherkin
Given user is chatting with travel agent
When conversation message is sent
Then KnowledgeAgent.observe() runs asynchronously
  And does NOT block user's conversation
  And extraction happens in background
  And latency impact on user < 10ms
```

## Implementación

Archivo: `scripts/coding/ai/memory/knowledge_agent.py`

```python
class KnowledgeAgent:
    """
    Observador de conversaciones que extrae y almacena knowledge.
    Implementa self-improvement pattern.
    """

    def __init__(self, user_id: str, llm_fast, llm_powerful):
        self.user_id = user_id
        self.llm_fast = llm_fast      # GPT-3.5 para is_worth_storing
        self.llm_powerful = llm_powerful  # GPT-4 para extraction
        self.memory = LongTermMemory(user_id)

    def is_worth_storing(self, conversation: List[Dict]) -> Dict:
        """
        RF-004: Determina si conversación contiene info valiosa.

        Args:
            conversation: [{"role": "user", "content": "..."}, ...]

        Returns:
            {
                "worth_storing": bool,
                "reason": str,
                "confidence": float
            }
        """
        # Use cheap model for quick check
        prompt = f"""
Analyze if this conversation contains valuable information to remember:

{conversation}

Does it contain:
- User preferences
- Important facts
- Decisions
- Learned information

Return JSON:
{{"worth_storing": bool, "reason": str, "confidence": float}}
"""
        response = self.llm_fast.complete(prompt)
        result = json.loads(response)

        return result

    def extract_knowledge(self, conversation: List[Dict]) -> List[Dict]:
        """
        RF-004: Extrae knowledge de conversación.

        Returns:
            [
                {
                    "type": "user_preference",
                    "content": "...",
                    "domain": "...",
                    "confidence": float
                },
                ...
            ]
        """
        # Use powerful model for extraction
        prompt = f"""
Extract valuable knowledge from this conversation.

Conversation:
{conversation}

For each fact, extract:
- type: user_preference | fact | decision | entity
- content: brief description
- domain: relevant domain
- confidence: 0.0-1.0

Return JSON list.
"""
        response = self.llm_powerful.complete(prompt)
        extracted = json.loads(response)

        return extracted

    def store_in_kb(self, knowledge: Dict):
        """
        RF-004: Almacena knowledge en knowledge base.
        """
        # Check if similar knowledge exists
        similar = self.memory.retrieve(
            query=knowledge["content"],
            top_k=1
        )

        if similar and similar[0]["score"] > 0.9:
            # Update existing
            self.memory.update(
                memory_id=similar[0]["memory_id"],
                new_content=knowledge["content"],
                metadata={
                    "supersedes": similar[0]["memory_id"],
                    "updated_at": datetime.now().isoformat()
                }
            )
        else:
            # Add new
            self.memory.add(
                content=knowledge["content"],
                metadata={
                    "type": knowledge["type"],
                    "domain": knowledge.get("domain"),
                    "confidence": knowledge["confidence"],
                    "source": "knowledge_agent",
                    "extracted_at": datetime.now().isoformat()
                }
            )

    def augment_query(self, user_query: str) -> str:
        """
        RF-004: Augmenta query con knowledge relevante.

        Args:
            user_query: Query del usuario

        Returns:
            Augmented prompt con context relevante
        """
        # Retrieve relevant knowledge
        relevant = self.memory.retrieve(
            query=user_query,
            top_k=5
        )

        if not relevant:
            return user_query

        # Build context
        context_lines = ["Relevant context:"]
        for item in relevant:
            context_lines.append(f"- {item['content']}")

        context = "\n".join(context_lines)

        # Augment prompt
        augmented = f"""
{context}

User Query: {user_query}
"""
        return augmented

    async def observe_async(self, conversation: List[Dict]):
        """
        RF-004: Observa conversación de manera asíncrona.

        No bloquea conversación del usuario.
        """
        # Quick check (fast model)
        decision = self.is_worth_storing(conversation)

        if not decision["worth_storing"]:
            return

        # Extract (powerful model, async)
        knowledge_list = self.extract_knowledge(conversation)

        # Store
        for knowledge in knowledge_list:
            self.store_in_kb(knowledge)

        logger.info(
            f"Knowledge agent stored {len(knowledge_list)} facts "
            f"from conversation"
        )
```

## Integration Pattern

```python
# En el agent principal
class TravelAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.knowledge_agent = KnowledgeAgent(user_id, llm_fast, llm_powerful)
        self.conversation_history = []

    async def process_message(self, user_message: str) -> str:
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Augment with knowledge (RF-004)
        augmented_prompt = self.knowledge_agent.augment_query(user_message)

        # Generate response
        response = await self.llm.complete(augmented_prompt)

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Observe asynchronously (NO blocking)
        asyncio.create_task(
            self.knowledge_agent.observe_async(self.conversation_history[-2:])
        )

        return response
```

## Tests

Archivo: `scripts/coding/tests/ai/test_knowledge_agent.py`

```python
class TestKnowledgeAgent:
    def test_is_worth_storing_preference(self):
        """RF-004: Detectar preferencia valiosa"""
        agent = KnowledgeAgent(user_id="test", llm_fast=mock_llm, llm_powerful=mock_llm)

        conversation = [
            {"role": "user", "content": "I have a ski injury, avoid advanced slopes"},
            {"role": "assistant", "content": "Understood, beginner-intermediate only"}
        ]

        result = agent.is_worth_storing(conversation)

        assert result["worth_storing"] == True
        assert result["confidence"] >= 0.8

    def test_extract_knowledge(self):
        """RF-004: Extraer knowledge de conversación"""
        agent = KnowledgeAgent(user_id="test", llm_fast=mock_llm, llm_powerful=mock_llm)

        conversation = [
            {"role": "user", "content": "I love Le Chat Noir in Paris"}
        ]

        extracted = agent.extract_knowledge(conversation)

        assert len(extracted) > 0
        assert any("Le Chat Noir" in k["content"] for k in extracted)

    def test_augment_query(self):
        """RF-004: Augmentar query con knowledge"""
        agent = KnowledgeAgent(user_id="test", llm_fast=mock_llm, llm_powerful=mock_llm)

        # Store knowledge
        agent.store_in_kb({
            "type": "user_preference",
            "content": "User has ski injury; avoid advanced slopes",
            "confidence": 0.9
        })

        # Augment query
        augmented = agent.augment_query("Recommend a ski resort")

        assert "ski injury" in augmented
        assert "avoid advanced slopes" in augmented
        assert "Recommend a ski resort" in augmented

    @pytest.mark.asyncio
    async def test_observe_async_no_blocking(self):
        """RF-004: Observación asíncrona no bloquea"""
        agent = KnowledgeAgent(user_id="test", llm_fast=mock_llm, llm_powerful=mock_llm)

        conversation = [
            {"role": "user", "content": "I prefer morning flights"}
        ]

        # Should return immediately (< 10ms)
        start = time.perf_counter()
        task = asyncio.create_task(agent.observe_async(conversation))
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 10  # Non-blocking

        # Wait for task to complete
        await task
```

Resultado esperado: `8 passed in 0.20s`

## Métricas

- is_worth_storing latency: < 500ms
- extract_knowledge latency: < 2000ms
- augment_query latency: < 100ms
- Async observe blocking time: < 10ms
- Cost per conversation: < $0.01

## Referencias

- UC-SYS-002: Gestionar Memoria de Agente
- ADR-048: AI Agent Memory Architecture (Knowledge Agent Pattern)
- Lesson: "Making AI Agents Self-Improving"
