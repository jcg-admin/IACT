---
id: RT-011
tipo: regla_tecnica
relacionado: [ADR-053, RF-009, RF-010]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RT-011: Multi-Agent Communication and Coordination

## Propósito

Definir reglas técnicas para comunicación y coordinación entre agentes en sistemas multi-agent para garantizar interoperabilidad, performance, y reliability.

## Reglas Técnicas

### 1. Message Format Standard

```python
MESSAGE_FORMAT_STANDARD = {
    # Required fields
    "required_fields": [
        "message_id",        # UUID
        "from_agent",        # Agent ID (sender)
        "to_agent",          # Agent ID (receiver) or "broadcast"
        "message_type",      # REQUEST, RESPONSE, BROADCAST, HANDOFF, ERROR
        "content",           # Dict with message payload
        "timestamp",         # ISO 8601 timestamp
    ],

    # Optional fields
    "optional_fields": [
        "metadata",          # Dict with additional context
        "correlation_id",    # For request-response correlation
        "priority",          # HIGH, MEDIUM, LOW
        "ttl",              # Time-to-live in seconds
        "reply_to",         # Agent to send response to (if different from sender)
    ],

    # Content structure
    "content_structure": {
        "action": "str",             # Action to perform
        "parameters": "Dict",        # Parameters for action
        "context": "Dict",           # Contextual information
        "previous_result": "Any",    # Result from previous agent (handoff)
    }
}
```

**Enforcement**:
```python
class Message:
    """RT-011: Standard message format for multi-agent communication."""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        content: Dict,
        metadata: Dict = None,
        correlation_id: str = None,
        priority: Priority = Priority.MEDIUM,
        ttl: int = None
    ):
        # Required fields
        self.message_id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.now()

        # Optional fields
        self.metadata = metadata or {}
        self.correlation_id = correlation_id
        self.priority = priority
        self.ttl = ttl

        # Validate (RT-011)
        self._validate()

    def _validate(self):
        """RT-011: Validate message format."""
        # Check required fields
        if not self.from_agent:
            raise ValueError("from_agent is required")

        if not self.to_agent:
            raise ValueError("to_agent is required")

        if not isinstance(self.content, dict):
            raise ValueError("content must be Dict")

        # Check content structure
        if "action" not in self.content:
            raise ValueError("content.action is required")

    def to_dict(self) -> Dict:
        """Serialize to dict."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
            "priority": self.priority.value if self.priority else None,
            "ttl": self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Deserialize from dict."""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            metadata=data.get("metadata"),
            correlation_id=data.get("correlation_id"),
            priority=Priority(data["priority"]) if data.get("priority") else None,
            ttl=data.get("ttl")
        )
```

### 2. Communication Latency Targets

```python
COMMUNICATION_LATENCY_TARGETS = {
    # Message delivery latency
    "message_send": 10,              # < 10ms to send message
    "message_receive": 10,           # < 10ms to receive message
    "message_roundtrip": 50,         # < 50ms for request-response

    # Agent response latency
    "agent_acknowledge": 100,        # < 100ms to acknowledge receipt
    "agent_process": 5000,           # < 5s to process and respond

    # Broadcast latency
    "broadcast_send": 50,            # < 50ms to broadcast to all agents
    "broadcast_delivery": 100,       # < 100ms for all agents to receive

    # Handoff latency
    "handoff_transfer": 200,         # < 200ms to transfer task to next agent
}
```

**Enforcement**:
```python
class AgentCommunication:
    """RT-011: Communication layer with latency enforcement."""

    def __init__(self):
        self.message_queue = MessageQueue()
        self.metrics = MetricsCollector()

    @enforce_latency_target("message_send", 10)
    def send_message(self, message: Message):
        """
        RT-011: Send message to another agent.

        Latency target: < 10ms
        """
        start = time.perf_counter()

        # Validate message (RT-011)
        if not isinstance(message, Message):
            raise ValueError("Must be Message instance")

        # Check TTL
        if message.ttl:
            if (datetime.now() - message.timestamp).total_seconds() > message.ttl:
                logger.warning(f"Message {message.message_id} expired (TTL exceeded)")
                return

        # Send to queue
        self.message_queue.push(message.to_agent, message)

        # Record latency
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.metrics.record_latency("message_send", elapsed_ms)

        # Log
        logger.info(
            f"Message sent: {message.from_agent} → {message.to_agent} "
            f"({message.message_type.value}) [{elapsed_ms:.2f}ms]"
        )

    @enforce_latency_target("message_receive", 10)
    def receive_messages(self, agent_id: str) -> List[Message]:
        """
        RT-011: Receive messages for agent.

        Latency target: < 10ms
        """
        start = time.perf_counter()

        # Get messages from queue
        messages = self.message_queue.pop_all(agent_id)

        # Deserialize
        message_objects = [Message.from_dict(m) for m in messages]

        # Record latency
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.metrics.record_latency("message_receive", elapsed_ms)

        return message_objects

    @enforce_latency_target("broadcast_send", 50)
    def broadcast(self, message: Message):
        """
        RT-011: Broadcast message to all agents.

        Latency target: < 50ms
        """
        start = time.perf_counter()

        # Get all agent IDs
        all_agents = self.get_all_agents()

        # Send to all (except sender)
        for agent_id in all_agents:
            if agent_id != message.from_agent:
                # Create copy for each agent
                msg_copy = Message(
                    from_agent=message.from_agent,
                    to_agent=agent_id,
                    message_type=MessageType.BROADCAST,
                    content=message.content,
                    metadata=message.metadata
                )
                self.message_queue.push(agent_id, msg_copy)

        # Record latency
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.metrics.record_latency("broadcast_send", elapsed_ms)

        logger.info(
            f"Broadcast: {message.from_agent} → {len(all_agents)} agents "
            f"[{elapsed_ms:.2f}ms]"
        )
```

### 3. Coordination Mechanisms

```python
COORDINATION_MECHANISMS = {
    # Centralized coordination
    "orchestrator": {
        "type": "centralized",
        "max_agents": 50,               # Max agents orchestrator can manage
        "routing_latency_target": 100,  # < 100ms to route task
        "aggregation_timeout": 30000,   # 30s max to aggregate results
    },

    # Decentralized coordination
    "peer_to_peer": {
        "type": "decentralized",
        "max_peers_per_agent": 10,      # Max peers each agent can communicate with
        "negotiation_rounds": 3,        # Max negotiation rounds
        "negotiation_timeout": 5000,    # 5s max for negotiation
    },

    # Shared state coordination
    "shared_state": {
        "type": "shared_memory",
        "lock_timeout": 1000,           # 1s max to acquire lock
        "max_concurrent_writers": 5,    # Max agents writing simultaneously
        "consistency_model": "eventual", # "strong" or "eventual"
    }
}
```

**Orchestrator Implementation**:
```python
class Orchestrator:
    """RT-011: Centralized orchestrator for multi-agent coordination."""

    def __init__(self, agents: List[Agent]):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.router = AgentRouter()
        self.communication = AgentCommunication()
        self.shared_state = SharedState()

    @enforce_latency_target("routing", 100)
    def route_task(self, task: Task) -> Agent:
        """
        RT-011: Route task to appropriate agent.

        Latency target: < 100ms
        """
        # Determine which agent should handle task
        agent_id = self.router.determine_agent(
            task=task.description,
            agents=list(self.agents.keys())
        )

        if agent_id not in self.agents:
            raise ValueError(f"No agent found for task: {task.description}")

        return self.agents[agent_id]

    def orchestrate(self, user_request: str, user_id: str) -> Result:
        """RT-011: Orchestrate multi-agent workflow."""

        # 1. Decompose request
        subtasks = self.decompose(user_request)

        # 2. Determine execution strategy
        can_parallelize = self._can_parallelize(subtasks)

        if can_parallelize:
            # Parallel execution
            results = self._execute_parallel(subtasks)
        else:
            # Sequential execution
            results = self._execute_sequential(subtasks)

        # 3. Aggregate results
        final_result = self.aggregate(results)

        return final_result

    def _execute_parallel(self, subtasks: List[Task]) -> Dict:
        """Execute subtasks in parallel."""
        futures = []

        for subtask in subtasks:
            agent = self.route_task(subtask)

            # Send message to agent (async)
            future = self.communication.send_message_async(
                Message(
                    from_agent="orchestrator",
                    to_agent=agent.agent_id,
                    message_type=MessageType.REQUEST,
                    content={
                        "action": "execute",
                        "parameters": {"task": subtask}
                    }
                )
            )

            futures.append((subtask.id, future))

        # Wait for all responses (with timeout)
        results = {}
        timeout = COORDINATION_MECHANISMS["orchestrator"]["aggregation_timeout"]

        for task_id, future in futures:
            try:
                result = future.get(timeout=timeout / 1000)  # Convert to seconds
                results[task_id] = result
            except TimeoutError:
                logger.error(f"Task {task_id} timed out")
                results[task_id] = AgentResult(
                    success=False,
                    error="Timeout"
                )

        return results
```

### 4. Conflict Resolution

```python
CONFLICT_RESOLUTION_RULES = {
    # Priority-based
    "priority": {
        "enabled": True,
        "order": ["HIGH", "MEDIUM", "LOW"],
        "description": "Higher priority messages processed first"
    },

    # Timestamp-based
    "timestamp": {
        "enabled": True,
        "strategy": "first_come_first_serve",
        "description": "Earlier messages processed first"
    },

    # Agent hierarchy
    "hierarchy": {
        "enabled": False,  # Optional
        "levels": {
            "orchestrator": 0,    # Highest
            "specialized_agent": 1,
            "general_agent": 2
        },
        "description": "Higher-level agents override lower-level"
    },

    # Voting
    "voting": {
        "enabled": False,  # For collaborative filtering
        "strategy": "majority",  # "majority", "weighted", "unanimous"
        "description": "Agents vote on decision"
    }
}
```

**Implementation**:
```python
class ConflictResolver:
    """RT-011: Resolve conflicts between agents."""

    def resolve_conflicting_recommendations(
        self,
        recommendations: List[Recommendation]
    ) -> Recommendation:
        """
        RT-011: Resolve when agents provide conflicting recommendations.

        Strategy: Weighted voting based on agent confidence + expertise
        """
        # Check if conflict exists
        if not self._has_conflict(recommendations):
            # No conflict - return highest confidence
            return max(recommendations, key=lambda r: r.confidence)

        # Conflict exists - resolve via weighted voting
        weights = self._calculate_weights(recommendations)

        # Weighted aggregate
        final_recommendation = self._weighted_aggregate(
            recommendations,
            weights
        )

        logger.info(
            f"Conflict resolved: {len(recommendations)} recommendations → "
            f"{final_recommendation.option} (confidence={final_recommendation.confidence:.2f})"
        )

        return final_recommendation

    def _has_conflict(self, recommendations: List[Recommendation]) -> bool:
        """Check if recommendations conflict."""
        options = [r.option for r in recommendations]
        unique_options = set(options)

        return len(unique_options) > 1  # More than one option → conflict

    def _calculate_weights(self, recommendations: List[Recommendation]) -> Dict:
        """Calculate weight for each recommendation."""
        weights = {}

        for rec in recommendations:
            # Weight based on:
            # 1. Agent expertise in domain (0.5)
            # 2. Confidence score (0.3)
            # 3. Historical accuracy (0.2)

            expertise_weight = self._get_expertise_weight(rec.agent_id, rec.domain)
            confidence_weight = rec.confidence
            accuracy_weight = self._get_historical_accuracy(rec.agent_id)

            total_weight = (
                0.5 * expertise_weight +
                0.3 * confidence_weight +
                0.2 * accuracy_weight
            )

            weights[rec.agent_id] = total_weight

        return weights
```

### 5. Handoff Protocol

```python
HANDOFF_PROTOCOL = {
    # Handoff requirements
    "required_fields": [
        "task_description",      # What next agent should do
        "context",               # Context from previous agent
        "previous_result",       # Result from previous agent
        "constraints",           # Constraints to respect
    ],

    # Handoff types
    "types": {
        "sequential": "Linear handoff: A → B → C",
        "conditional": "Conditional: A → (B if X, else C)",
        "parallel_merge": "Parallel: (A || B || C) → D (aggregate)",
    },

    # Handoff latency
    "latency_target": 200,  # < 200ms to transfer task
}
```

**Implementation**:
```python
class HandoffManager:
    """RT-011: Manage handoffs between agents."""

    @enforce_latency_target("handoff_transfer", 200)
    def handoff(
        self,
        from_agent: Agent,
        to_agent: Agent,
        task: Task,
        result: AgentResult
    ):
        """
        RT-011: Hand off task from one agent to another.

        Latency target: < 200ms
        """
        # Validate handoff (RT-011)
        if not result.should_handoff:
            raise ValueError("Result does not indicate handoff")

        if not result.next_agent_id:
            raise ValueError("No next agent specified")

        # Build handoff message
        handoff_message = Message(
            from_agent=from_agent.agent_id,
            to_agent=to_agent.agent_id,
            message_type=MessageType.HANDOFF,
            content={
                "action": "execute_handoff",
                "parameters": {
                    "task_description": result.next_task_description,
                    "context": self._build_context(from_agent, task, result),
                    "previous_result": result.data,
                    "constraints": task.constraints
                }
            },
            metadata={
                "workflow_id": task.workflow_id,
                "handoff_step": task.step_number + 1
            }
        )

        # Send handoff
        self.communication.send_message(handoff_message)

        # Log
        logger.info(
            f"Handoff: {from_agent.agent_id} → {to_agent.agent_id} "
            f"(workflow={task.workflow_id}, step={task.step_number + 1})"
        )

        # Update shared state
        self.shared_state.update_workflow_status(
            workflow_id=task.workflow_id,
            current_agent=to_agent.agent_id,
            step=task.step_number + 1
        )
```

### 6. Message Queue Configuration

```python
MESSAGE_QUEUE_CONFIG = {
    # Queue type
    "type": "priority_queue",  # "fifo", "priority_queue", "topic"

    # Capacity
    "max_messages_per_agent": 1000,
    "max_total_messages": 10000,

    # Retention
    "message_ttl_default": 3600,  # 1 hour
    "message_ttl_max": 86400,     # 24 hours

    # Delivery
    "delivery_guarantee": "at_least_once",  # "at_most_once", "at_least_once", "exactly_once"
    "max_retries": 3,
    "retry_backoff_ms": [100, 500, 2000],  # Exponential backoff

    # Prioritization
    "priority_levels": {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2
    }
}
```

## Performance Metrics

```python
REQUIRED_METRICS = [
    "multi_agent.message.send_latency_p50",
    "multi_agent.message.send_latency_p95",
    "multi_agent.message.send_latency_p99",

    "multi_agent.message.receive_latency_p50",
    "multi_agent.message.receive_latency_p95",

    "multi_agent.message.roundtrip_latency_p50",
    "multi_agent.message.roundtrip_latency_p95",

    "multi_agent.handoff.latency_p50",
    "multi_agent.handoff.latency_p95",

    "multi_agent.broadcast.latency_p50",

    "multi_agent.orchestration.routing_latency_p95",
    "multi_agent.orchestration.aggregation_latency_p95",

    "multi_agent.message.queue_depth",
    "multi_agent.message.dropped_count",
    "multi_agent.message.expired_count",

    "multi_agent.conflict.resolution_count",
    "multi_agent.conflict.resolution_latency_avg",
]
```

## Performance Targets

| Metric                          | Target         | Alert Threshold |
| ------------------------------- | -------------- | --------------- |
| Message send latency p95        | < 10ms         | > 20ms          |
| Message receive latency p95     | < 10ms         | > 20ms          |
| Roundtrip latency p95           | < 50ms         | > 100ms         |
| Handoff latency p95             | < 200ms        | > 500ms         |
| Broadcast latency p50           | < 50ms         | > 100ms         |
| Routing latency p95             | < 100ms        | > 200ms         |
| Queue depth                     | < 100          | > 500           |
| Message drop rate               | < 0.1%         | > 1%            |

## Excepciones

```python
class MultiAgentCommunicationError(Exception):
    """Base exception for multi-agent communication errors."""
    pass

class MessageValidationError(MultiAgentCommunicationError):
    """Message does not conform to format standard."""
    pass

class RoutingError(MultiAgentCommunicationError):
    """Cannot route task to appropriate agent."""
    pass

class HandoffError(MultiAgentCommunicationError):
    """Handoff between agents failed."""
    pass

class ConflictResolutionError(MultiAgentCommunicationError):
    """Cannot resolve conflict between agents."""
    pass

class MessageQueueFullError(MultiAgentCommunicationError):
    """Message queue is full."""
    pass
```

## Cumplimiento

- Messages DEBEN seguir formato estándar (required fields)
- Message send/receive DEBE completar en < 10ms (p95)
- Roundtrip request-response DEBE completar en < 50ms (p95)
- Handoff DEBE completar en < 200ms (p95)
- Broadcast DEBE completar en < 50ms (p50)
- Sistema DEBE manejar conflicts via voting/priority/hierarchy
- Message queue DEBE soportar >= 1000 messages per agent

## Referencias

- ADR-053: Multi-Agent Design Patterns
- RT-009: Metacognition Performance Constraints (latency patterns)
- ADR-050: Context Engineering (shared state management)

---

**Regla**: Comunicación y coordinación entre agentes debe ser rápida, confiable, y estandarizada.
**Enforcement**: Message format validation, latency targets, conflict resolution, handoff protocol.
