---
id: ADR-AI-013-multi-service-design-patterns
tipo: adr
estado: propuesto
fecha: 2025-11-16
relacionado: [ADR-048, ADR-050, ADR-052]
---

# ADR-053: Multi-Agent Design Patterns

## Status

**Estado**: Propuesto
**Fecha**: 2025-11-16
**Autores**: Equipo AI

## Context

### Problem Statement

Single-agent systems funcionan bien para tareas simples, pero enfrentan limitaciones con:

**Problemas actuales**:
- **Complejidad**: Un solo agente maneja múltiples dominios → confusión, decisiones subóptimas
- **Escalabilidad**: No se puede escalar fácilmente agregando más capacidad
- **Especialización**: Agente generalista vs expertos especializados
- **Context overload**: Un agente con todas las tools → context window saturado
- **Single point of failure**: Si el agente falla, todo el sistema falla

**Ejemplo concreto - Travel Booking (Single Agent)**:
```python
# Single agent con TODAS las tools
travel_agent = Agent(
    name="TravelAgent",
    tools=[
        search_flights, book_flights, cancel_flights,
        search_hotels, book_hotels, cancel_hotels,
        search_rental_cars, book_rental_cars, cancel_rental_cars,
        get_weather, get_attractions, get_restaurants,
        process_payment, send_confirmation_email,
        handle_customer_support, process_refunds
    ]  # 14+ tools → context confusion (ADR-050)
)

# Problema: Agent confundido sobre qué tool usar cuándo
user: "I need to book a trip to Paris"
agent: *calls search_restaurants* (wrong tool!)
```

**Research findings**:
- Agents con > 30 tools tienen degradación en decision quality
- Single agent no puede procesar large workloads en parallel
- Falta de especialización reduce accuracy en dominios complejos

### When to Use Multi-Agents

Multi-agentes son aplicables en estos escenarios:

1. **Large Workloads**: Dividir en subtasks paralelas
   - Ejemplo: Procesar 10,000 refund requests simultáneamente

2. **Complex Tasks**: Descomponer en subtasks especializadas
   - Ejemplo: Autonomous vehicles (navigation, obstacle detection, communication)

3. **Diverse Expertise**: Diferentes agentes con expertise específica
   - Ejemplo: Healthcare (diagnostics agent, treatment agent, monitoring agent)

### Single-Agent vs Multi-Agent

| Aspecto              | Single Agent                | Multi-Agent                          |
| -------------------- | --------------------------- | ------------------------------------ |
| **Especialización**  | Generalista                 | Expertos especializados              |
| **Escalabilidad**    | Vertical (más poder)        | Horizontal (más agentes)             |
| **Context**          | Overloaded (todas las tools)| Cada agente con tools específicas    |
| **Fault Tolerance**  | Single point of failure     | Si uno falla, otros continúan        |
| **Complejidad**      | Simple para tareas simples  | Mejor para tareas complejas          |
| **Coordinación**     | No necesaria                | Requiere orchestration               |

## Decision

Implementar **Multi-Agent Architecture** con patterns especializados para diferentes use cases.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent System                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Orchestrator / Router                         │ │
│  │  - Routes tasks to appropriate agents                      │ │
│  │  - Manages agent communication                             │ │
│  │  - Handles hand-offs between agents                        │ │
│  └─────────┬──────────────────────────────────────────────────┘ │
│            │                                                     │
│  ┌─────────┴──────────────────────────────────────────┐        │
│  │                                                     │        │
│  ▼                  ▼                  ▼               ▼        │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐           │
│ │ Agent 1 │  │ Agent 2 │  │ Agent 3 │  │ Agent N  │           │
│ │ (Flight)│  │ (Hotel) │  │(Car)    │  │(Support) │           │
│ └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘           │
│      │            │            │            │                  │
│      └────────────┴────────────┴────────────┘                  │
│                   │                                             │
│          ┌────────┴────────┐                                   │
│          │  Shared State   │                                   │
│          │  (Runtime State)│                                   │
│          └─────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Building Blocks

#### 1. Agent Communication

**Problema**: ¿Cómo se comunican los agentes?

**Solución**: Message-passing protocol

```python
class Message:
    """Message exchanged between agents."""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        content: Dict,
        metadata: Dict = None
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type  # REQUEST, RESPONSE, BROADCAST, HANDOFF
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.message_id = str(uuid.uuid4())

# Communication Protocol
class AgentCommunication:
    def send_message(self, message: Message):
        """Send message to another agent."""

    def receive_message(self, agent_id: str) -> List[Message]:
        """Receive messages for this agent."""

    def broadcast(self, message: Message):
        """Broadcast message to all agents."""
```

**Ejemplo - Flight agent → Hotel agent**:
```python
# Flight agent found flight
flight_agent.send_message(
    Message(
        from_agent="flight_agent",
        to_agent="hotel_agent",
        message_type=MessageType.REQUEST,
        content={
            "action": "book_hotel",
            "travel_dates": {
                "check_in": "2025-12-15",
                "check_out": "2025-12-20"
            },
            "location": "Paris",
            "user_preferences": {
                "near_airport": True
            }
        }
    )
)
```

#### 2. Coordination Mechanisms

**Problema**: ¿Cómo coordinan sus acciones los agentes?

**Estrategias**:

**A. Centralized Orchestrator**:
```python
class Orchestrator:
    """Centralized coordinator for multi-agent system."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.router = AgentRouter()
        self.state = SharedState()

    def route_task(self, task: str, user_id: str) -> Agent:
        """Route task to appropriate agent."""
        # Determine which agent should handle task
        agent_id = self.router.determine_agent(task)
        return self.agents[agent_id]

    def orchestrate(self, user_request: str) -> Result:
        """Orchestrate multi-agent workflow."""
        # 1. Decompose request into subtasks
        subtasks = self.decompose(user_request)

        # 2. Route each subtask to appropriate agent
        results = {}
        for subtask in subtasks:
            agent = self.route_task(subtask.task, subtask.user_id)
            results[subtask.id] = agent.execute(subtask)

        # 3. Aggregate results
        final_result = self.aggregate(results)

        return final_result
```

**B. Decentralized (Peer-to-Peer)**:
```python
class Agent:
    """Agent in decentralized multi-agent system."""

    def __init__(self, agent_id: str, peers: List[str]):
        self.agent_id = agent_id
        self.peers = peers  # Other agents this agent can communicate with

    def negotiate_with_peer(self, peer_id: str, task: Task) -> bool:
        """Negotiate with peer agent for task delegation."""
        # Ask peer if they can handle task
        can_handle = self.ask_peer(peer_id, task)

        if can_handle:
            # Delegate task
            self.send_message(
                Message(
                    from_agent=self.agent_id,
                    to_agent=peer_id,
                    message_type=MessageType.HANDOFF,
                    content={"task": task}
                )
            )
            return True

        return False
```

**C. Hybrid**:
- Orchestrator para routing inicial
- Peer-to-peer para fine-grained coordination

#### 3. Agent Architecture

**Internal Structure**:

```python
class SpecializedAgent:
    """Agent specializing in specific domain."""

    def __init__(
        self,
        agent_id: str,
        domain: str,
        tools: List[Tool],
        llm,
        memory_manager
    ):
        self.agent_id = agent_id
        self.domain = domain  # "flights", "hotels", "cars", etc.
        self.tools = tools    # Domain-specific tools only
        self.llm = llm
        self.memory = memory_manager

        # Communication
        self.communication = AgentCommunication()

        # State
        self.current_task = None
        self.status = AgentStatus.IDLE

    def can_handle(self, task: str) -> bool:
        """Determine if this agent can handle task."""
        # Check if task is in this agent's domain
        keywords = self._extract_keywords(task)
        domain_match = any(
            kw in DOMAIN_KEYWORDS[self.domain]
            for kw in keywords
        )

        return domain_match

    def execute(self, task: Task) -> AgentResult:
        """Execute task using domain-specific tools."""
        self.status = AgentStatus.BUSY
        self.current_task = task

        # Use tools specific to this domain
        result = self._execute_with_tools(task)

        self.status = AgentStatus.IDLE
        self.current_task = None

        return result

    def request_help(self, other_agent_id: str, question: str):
        """Request help from another agent."""
        self.communication.send_message(
            Message(
                from_agent=self.agent_id,
                to_agent=other_agent_id,
                message_type=MessageType.REQUEST,
                content={"question": question}
            )
        )
```

#### 4. Visibility and Observability

**Problema**: ¿Cómo monitoreamos interacciones entre agentes?

**Solución**: Comprehensive logging + visualization

```python
class MultiAgentObservability:
    """Observability for multi-agent systems."""

    def __init__(self):
        self.logger = Logger()
        self.tracer = Tracer()
        self.metrics = MetricsCollector()

    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        task: Task,
        result: Any,
        duration_ms: float
    ):
        """Log action taken by agent."""
        self.logger.log({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "task": task.to_dict(),
            "result": result,
            "duration_ms": duration_ms
        })

    def log_communication(self, message: Message):
        """Log communication between agents."""
        self.logger.log({
            "type": "agent_communication",
            "from": message.from_agent,
            "to": message.to_agent,
            "message_type": message.message_type,
            "timestamp": message.timestamp.isoformat()
        })

    def trace_workflow(self, workflow_id: str) -> Trace:
        """Trace complete multi-agent workflow."""
        # Collect all logs for this workflow
        logs = self.logger.query(workflow_id=workflow_id)

        # Build trace
        trace = Trace(
            workflow_id=workflow_id,
            agents_involved=[log["agent_id"] for log in logs],
            messages_exchanged=self._extract_messages(logs),
            total_duration_ms=self._calculate_duration(logs)
        )

        return trace

    def visualize_workflow(self, workflow_id: str):
        """Generate visualization of agent interactions."""
        trace = self.trace_workflow(workflow_id)

        # Generate graph
        graph = self._build_graph(trace)

        return graph  # Can be rendered in dashboard
```

**Dashboard Example**:
```
Workflow: book_trip_paris_123
Duration: 15.3s
Agents: 5 (flight, hotel, car, payment, notification)

┌─────────────────────────────────────────────────────────┐
│  User Request: "Book trip to Paris Dec 15-20"           │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
       ┌───────────────┐
       │ Orchestrator  │
       └───┬───┬───┬───┘
           │   │   │
    ┌──────┘   │   └──────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Flight  │ │Hotel   │ │Car     │
│Agent   │ │Agent   │ │Agent   │
│2.5s    │ │3.1s    │ │1.8s    │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┴──────────┘
               │
               ▼
         ┌──────────┐
         │Payment   │
         │Agent     │
         │5.2s      │
         └─────┬────┘
               │
               ▼
         ┌──────────┐
         │Notify    │
         │Agent     │
         │0.4s      │
         └──────────┘
```

## Multi-Agent Patterns

### Pattern 1: Group Chat

**Use Case**: Multiple agents need to collaborate simultaneously

**Architecture**:
```python
class GroupChatPattern:
    """
    All agents in a shared "room" can see all messages.
    Useful for collaborative problem-solving.
    """

    def __init__(self, agents: List[Agent]):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.message_history: List[Message] = []

    def broadcast_to_group(self, message: Message):
        """Broadcast message to all agents in group."""
        self.message_history.append(message)

        # All agents see this message
        for agent_id, agent in self.agents.items():
            if agent_id != message.from_agent:
                agent.receive_message(message)

    def get_group_context(self) -> List[Message]:
        """Get full conversation history."""
        return self.message_history
```

**Ejemplo - Stock Recommendation**:
```python
# Three expert agents collaborating
group = GroupChatPattern(agents=[
    IndustryExpertAgent("tech_expert"),
    TechnicalAnalysisAgent("ta_expert"),
    FundamentalAnalysisAgent("fa_expert")
])

# User query broadcasted to all
user_query = "What stock should I buy?"
group.broadcast_to_group(
    Message(
        from_agent="user",
        to_agent="group",
        message_type=MessageType.BROADCAST,
        content={"query": user_query}
    )
)

# Each agent contributes
# - tech_expert: "AAPL strong in tech sector"
# - ta_expert: "AAPL shows bullish pattern"
# - fa_expert: "AAPL P/E ratio attractive"

# Final recommendation aggregates all inputs
```

### Pattern 2: Hand-off

**Use Case**: Sequential workflow where agents pass tasks to each other

**Architecture**:
```python
class HandOffPattern:
    """
    Agent A completes task, hands off to Agent B.
    Linear workflow: A → B → C → D
    """

    def __init__(self, workflow: List[Agent]):
        self.workflow = workflow  # Ordered list of agents
        self.current_step = 0

    def execute_workflow(self, initial_task: Task) -> Result:
        """Execute workflow with hand-offs."""
        task = initial_task

        for agent in self.workflow:
            # Agent executes
            result = agent.execute(task)

            # Check if should hand off to next
            if result.should_handoff and self.has_next_agent():
                # Hand off to next agent
                next_agent = self.get_next_agent()

                self.log_handoff(agent.agent_id, next_agent.agent_id, result)

                # Create task for next agent
                task = Task(
                    description=result.next_task_description,
                    context=result.context
                )
            else:
                # Workflow complete
                return result

        return result
```

**Ejemplo - Refund Process**:
```python
refund_workflow = HandOffPattern(workflow=[
    CustomerAgent(),      # 1. Receive refund request
    SellerAgent(),        # 2. Approve/reject refund
    PaymentAgent(),       # 3. Process payment
    NotificationAgent()   # 4. Notify customer
])

result = refund_workflow.execute_workflow(
    Task(description="Process refund for order #12345")
)

# Flow:
# CustomerAgent validates request → hands off to SellerAgent
# SellerAgent approves → hands off to PaymentAgent
# PaymentAgent refunds $50 → hands off to NotificationAgent
# NotificationAgent sends email → workflow complete
```

### Pattern 3: Collaborative Filtering

**Use Case**: Multiple agents provide recommendations, aggregate for final decision

**Architecture**:
```python
class CollaborativeFilteringPattern:
    """
    Each agent provides independent recommendation.
    Aggregate to produce final recommendation.
    """

    def __init__(self, agents: List[Agent], aggregator):
        self.agents = agents
        self.aggregator = aggregator

    def get_recommendation(self, query: str) -> Recommendation:
        """Get collaborative recommendation."""
        # Get recommendation from each agent (in parallel)
        recommendations = []

        for agent in self.agents:
            rec = agent.recommend(query)
            recommendations.append({
                "agent": agent.agent_id,
                "recommendation": rec,
                "confidence": rec.confidence
            })

        # Aggregate recommendations
        final_recommendation = self.aggregator.aggregate(recommendations)

        return final_recommendation
```

**Ejemplo - Hotel Recommendation**:
```python
hotel_recommender = CollaborativeFilteringPattern(
    agents=[
        PriceAgent(),      # Recommends based on price
        QualityAgent(),    # Recommends based on quality
        LocationAgent(),   # Recommends based on location
        ReviewsAgent()     # Recommends based on reviews
    ],
    aggregator=WeightedAverageAggregator(weights={
        "price": 0.2,
        "quality": 0.4,
        "location": 0.3,
        "reviews": 0.1
    })
)

recommendation = hotel_recommender.get_recommendation(
    "Hotel in Paris near Eiffel Tower"
)

# Each agent scores hotels:
# - PriceAgent: Hotel A=0.9, Hotel B=0.6
# - QualityAgent: Hotel A=0.7, Hotel B=0.9
# - LocationAgent: Hotel A=0.8, Hotel B=0.8
# - ReviewsAgent: Hotel A=0.6, Hotel B=0.9

# Weighted aggregate: Hotel B wins (0.82 > 0.76)
```

## Real-World Example: Travel Booking

**Single-Agent (Before)**:
```python
# Monolithic agent
travel_agent = Agent(
    tools=[...14 tools...],  # ALL travel-related tools
    system_prompt="You are a travel agent..."
)

# Problems:
# - Context overload (too many tools)
# - Cannot parallelize (single agent)
# - No specialization
# - Single point of failure
```

**Multi-Agent (After)**:
```python
# Specialized agents
flight_agent = Agent(
    domain="flights",
    tools=[search_flights, book_flights, cancel_flights]
)

hotel_agent = Agent(
    domain="hotels",
    tools=[search_hotels, book_hotels, cancel_hotels]
)

car_agent = Agent(
    domain="rental_cars",
    tools=[search_cars, book_cars, cancel_cars]
)

payment_agent = Agent(
    domain="payment",
    tools=[process_payment, process_refund]
)

# Orchestrator
orchestrator = Orchestrator(agents=[
    flight_agent,
    hotel_agent,
    car_agent,
    payment_agent
])

# Workflow
result = orchestrator.orchestrate("Book trip to Paris Dec 15-20")

# Flow:
# 1. Orchestrator decomposes: [find flight, find hotel, find car, pay]
# 2. Parallel execution:
#    - flight_agent searches flights (2.5s)
#    - hotel_agent searches hotels (3.1s)
#    - car_agent searches cars (1.8s)
# 3. Sequential: payment_agent processes payment (5.2s)
# 4. Total: ~10s (vs ~15s with single agent)
```

## Advantages

1. **Specialization**: Each agent expert in domain
2. **Scalability**: Add more agents horizontally
3. **Parallelization**: Multiple agents work simultaneously
4. **Fault Tolerance**: If one agent fails, others continue
5. **Context Management**: Each agent has focused context (< 30 tools)
6. **Modularity**: Easy to add/remove/update agents

## When NOT to Use Multi-Agents

Multi-agents adds complexity. Avoid when:

- **Simple tasks**: Single-agent is sufficient
- **No parallelization benefit**: Tasks are purely sequential
- **Tight coupling**: Tasks cannot be decomposed
- **Overhead > benefit**: Communication overhead exceeds gains

## Consequences

### Positive

1. **Better Performance**: Parallelization + specialization
2. **Better Scalability**: Add agents as needed
3. **Better Reliability**: Fault tolerance
4. **Better Maintainability**: Modular agents

### Negative

1. **Increased Complexity**: Orchestration, communication, coordination
2. **Debugging Difficulty**: Distributed system challenges
3. **Latency Overhead**: Communication between agents
4. **State Management**: Shared state synchronization

## Implementation Guidelines

### 1. Decide on Architecture

- **Centralized**: Use Orchestrator for routing + coordination
- **Decentralized**: Agents negotiate peer-to-peer
- **Hybrid**: Orchestrator + peer-to-peer for fine-grained tasks

### 2. Define Agent Boundaries

```python
# Good: Clear domain separation
FlightAgent(domain="flights", tools=[search_flights, book_flights])
HotelAgent(domain="hotels", tools=[search_hotels, book_hotels])

# Bad: Overlapping domains
TravelAgent1(tools=[search_flights, search_hotels])  # Unclear
TravelAgent2(tools=[book_flights, book_hotels])      # Unclear
```

### 3. Implement Communication Protocol

- Message types: REQUEST, RESPONSE, BROADCAST, HANDOFF
- Message format: Structured (JSON)
- Delivery: Sync vs Async

### 4. Add Observability

- Log all agent actions
- Log all messages
- Visualize workflows
- Track metrics

## References

- Lesson: "Multi-agent design patterns"
- ADR-048: AI Agent Memory (for shared state)
- ADR-050: Context Engineering (context per agent)
- ADR-052: Metacognition (agents can reflect on multi-agent performance)

---

**Decision**: Implementar multi-agent architecture con patterns especializados (Group Chat, Hand-off, Collaborative Filtering).
**Rationale**: Especialización, escalabilidad, fault tolerance, mejor context management.
