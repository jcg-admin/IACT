---
id: RF-009
tipo: requisito_funcional
relacionado: [UC-SYS-005, ADR-053, RT-011]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-009: Agent Communication and Hand-off

## Especificación

El sistema DEBE implementar comunicación estandarizada entre agentes y hand-off protocol para transferir tareas entre agentes especializados.

## Criterios de Aceptación

### Escenario 1: Send Message Between Agents

```gherkin
Given FlightAgent has completed search
  And result = {flights: [Flight A, Flight B, Flight C]}
When FlightAgent.send_message(
    to_agent="PaymentAgent",
    message_type="REQUEST",
    content={
        "action": "process_payment",
        "parameters": {"flight": Flight A, "amount": 450}
    }
)
Then message is sent successfully
  And message has required fields:
    - message_id (UUID)
    - from_agent = "FlightAgent"
    - to_agent = "PaymentAgent"
    - message_type = "REQUEST"
    - content (Dict)
    - timestamp (ISO 8601)
  And latency < 10ms
  And message added to PaymentAgent queue
```

### Escenario 2: Receive Messages

```gherkin
Given PaymentAgent message queue contains 3 messages:
    | message_id | from_agent    | message_type |
    | msg_001    | FlightAgent   | REQUEST      |
    | msg_002    | HotelAgent    | REQUEST      |
    | msg_003    | CarAgent      | REQUEST      |
When PaymentAgent.receive_messages()
Then all 3 messages are returned
  And messages ordered by priority (if present) then timestamp
  And latency < 10ms
  And messages removed from queue
```

### Escenario 3: Broadcast Message to All Agents

```gherkin
Given Orchestrator wants to broadcast alert
  And system has 5 agents: [Flight, Hotel, Car, Payment, Notify]
When Orchestrator.broadcast(
    message_type="BROADCAST",
    content={"alert": "System maintenance in 10 minutes"}
)
Then message sent to all 5 agents
  And each agent receives identical message (except to_agent field)
  And total latency < 50ms
  And broadcast logged (RT-012)
```

### Escenario 4: Request-Response Correlation

```gherkin
Given HotelAgent sends request to PaymentAgent
  And request has correlation_id = "cor_123"
When PaymentAgent sends response
Then response message includes:
  - correlation_id = "cor_123" (same as request)
  - message_type = "RESPONSE"
  - from_agent = "PaymentAgent"
  - to_agent = "HotelAgent"
  And HotelAgent can match response to original request
  And roundtrip latency < 50ms
```

### Escenario 5: Message Priority

```gherkin
Given PaymentAgent queue has messages with different priorities:
    | message_id | priority | timestamp           |
    | msg_001    | LOW      | 2025-11-16T10:00:00 |
    | msg_002    | HIGH     | 2025-11-16T10:00:05 |
    | msg_003    | MEDIUM   | 2025-11-16T10:00:02 |
When PaymentAgent.receive_messages()
Then messages returned in priority order:
  - msg_002 (HIGH) first
  - msg_003 (MEDIUM) second
  - msg_001 (LOW) last
  And high priority messages processed first
```

### Escenario 6: Message TTL (Time-To-Live)

```gherkin
Given FlightAgent sends message at T=0
  And message has ttl = 60 (seconds)
  And current_time = T+65 (65 seconds later)
When PaymentAgent.receive_messages()
Then expired message (ttl exceeded) is NOT delivered
  And message is logged as expired (RT-012)
  And metrics.message.expired_count incremented
```

### Escenario 7: Hand-off Between Agents

```gherkin
Given CustomerAgent completes validation
  And result = {order_id: "12345", refund_eligible: True}
  And workflow requires handoff to SellerAgent
When CustomerAgent.handoff(
    to_agent="SellerAgent",
    task_description="Approve refund for order 12345",
    context={
        "order_id": "12345",
        "reason": "defective product",
        "amount": 50
    },
    previous_result=result
)
Then HANDOFF message sent to SellerAgent
  And message contains all required fields (RT-011):
    - task_description
    - context
    - previous_result
    - constraints (if any)
  And handoff logged (RT-012)
  And handoff latency < 200ms
  And workflow_step incremented
```

### Escenario 8: Hand-off with Context Transfer

```gherkin
Given FlightAgent has context:
    - user_preferences: {prefer_morning: True}
    - travel_dates: {departure: "Dec 15", return: "Dec 20"}
    - selected_flight: Flight A
  And context_size = 5 KB
When FlightAgent.handoff(to_agent="PaymentAgent", context=context)
Then context transferred completely to PaymentAgent
  And PaymentAgent receives all 3 context fields
  And context_size logged: 5 KB (RT-012)
  And PaymentAgent can access user_preferences in next step
```

### Escenario 9: Sequential Hand-off Chain

```gherkin
Given refund workflow with 4 agents:
    Step 1: CustomerAgent
    Step 2: SellerAgent
    Step 3: PaymentAgent
    Step 4: NotificationAgent
When workflow executes with handoffs
Then handoffs occur in sequence:
  - CustomerAgent → SellerAgent (handoff 1)
  - SellerAgent → PaymentAgent (handoff 2)
  - PaymentAgent → NotificationAgent (handoff 3)
  And each handoff includes previous_result from prior agent
  And total handoff latency < 600ms (3 handoffs × 200ms)
  And workflow completes successfully
```

### Escenario 10: Conditional Hand-off

```gherkin
Given SellerAgent reviewing refund request
  And approval_result = "APPROVED"
When SellerAgent decides handoff:
  - IF approval_result == "APPROVED":
      Handoff to PaymentAgent
  - ELSE:
      Handoff to NotificationAgent (rejection email)
Then SellerAgent hands off to PaymentAgent (approved path)
  And conditional logic logged
  And correct agent receives handoff
```

### Escenario 11: Message Validation Error

```gherkin
Given FlightAgent attempts to send malformed message
  And message missing required field: "content"
When FlightAgent.send_message(
    to_agent="PaymentAgent",
    message_type="REQUEST"
    # Missing content field!
)
Then MessageValidationError is raised
  And error message = "content is required"
  And message is NOT sent
  And metrics.message.validation_errors incremented
```

### Escenario 12: Message Queue Full

```gherkin
Given PaymentAgent queue has 1000 messages (at capacity)
  And max_messages_per_agent = 1000 (RT-011)
When FlightAgent.send_message(to_agent="PaymentAgent", ...)
Then MessageQueueFullError is raised
  And error message contains "PaymentAgent queue full"
  And sender retries with exponential backoff:
    - Retry 1: wait 100ms
    - Retry 2: wait 500ms
    - Retry 3: wait 2000ms
  And IF queue clears, message is sent successfully
```

### Escenario 13: Acknowledge Receipt

```gherkin
Given Orchestrator sends REQUEST to FlightAgent
  And acknowledgement_required = True
When FlightAgent receives message
Then FlightAgent sends acknowledgement within 100ms
  And acknowledgement message:
    - message_type = "ACK"
    - correlation_id = original_message.message_id
    - from_agent = "FlightAgent"
    - to_agent = "Orchestrator"
  And Orchestrator receives ACK
  And Orchestrator knows FlightAgent received task
```

### Escenario 14: Parallel Messages

```gherkin
Given Orchestrator needs to send 3 messages in parallel
  And messages to: [FlightAgent, HotelAgent, CarAgent]
When Orchestrator.send_messages_parallel([msg1, msg2, msg3])
Then all 3 messages sent concurrently (asyncio.gather)
  And total_latency < 15ms (not 30ms for sequential)
  And all agents receive messages
  And parallel send logged (RT-012)
```

### Escenario 15: Message Retry with Backoff

```gherkin
Given FlightAgent sends message to PaymentAgent
  And message send fails (network error)
When system retries with exponential backoff
Then retry attempts:
  - Attempt 1: immediate fail
  - Attempt 2: wait 100ms, retry → fail
  - Attempt 3: wait 500ms, retry → fail
  - Attempt 4: wait 2000ms, retry → success
  And total retries = 3 (after initial attempt)
  And message eventually delivered
  And retry metrics recorded
```

### Escenario 16: Hand-off Logging

```gherkin
Given CustomerAgent hands off to SellerAgent
  And workflow_id = "wf_refund_123"
  And step_number = 2
When handoff executes
Then log entry created (RT-012) with:
  - category = "handoff"
  - from_agent = "CustomerAgent"
  - to_agent = "SellerAgent"
  - workflow_id = "wf_refund_123"
  - step_number = 2
  - task_description = "Approve refund"
  - context_size_kb = size of transferred context
  - timestamp
  And log stored for 30 days
```

### Escenario 17: Broadcast with Selective Targeting

```gherkin
Given Orchestrator wants to broadcast to specific agent types
  And agent_types = ["booking"]  # Flight, Hotel, Car agents
When Orchestrator.broadcast_to_types(
    agent_types=["booking"],
    content={"alert": "Booking API maintenance"}
)
Then message sent only to booking agents:
  - FlightAgent ✓
  - HotelAgent ✓
  - CarAgent ✓
  - PaymentAgent ✗ (not booking type)
  - NotificationAgent ✗ (not booking type)
  And selective broadcast logged
```

### Escenario 18: Message Content Structure Validation

```gherkin
Given PaymentAgent requires specific content structure
  And required_fields = ["action", "parameters"]
When FlightAgent sends message with content:
  {
    "action": "process_payment",
    "parameters": {"amount": 450, "flight": "Flight A"}
  }
Then content structure validation passes
  And PaymentAgent accepts message
  And IF content missing "action" field:
      Then MessageValidationError raised
```

### Escenario 19: Hand-off with Constraints

```gherkin
Given SellerAgent approves refund
  And user_constraints = {
      "refund_method": "original_payment",
      "processing_time": "within_3_days"
  }
When SellerAgent.handoff(
    to_agent="PaymentAgent",
    constraints=user_constraints
)
Then PaymentAgent receives constraints
  And PaymentAgent respects constraints:
    - Use original payment method ✓
    - Process within 3 days ✓
  And constraints logged with handoff
```

### Escenario 20: Communication Metrics

```gherkin
Given system operates for 1 hour
  And 1000 messages sent between agents
When metrics are collected
Then communication metrics include:
  - messages_sent_count = 1000
  - messages_received_count = 1000
  - message_send_latency_p95 < 10ms
  - message_receive_latency_p95 < 10ms
  - roundtrip_latency_p95 < 50ms
  - handoffs_count = 150
  - handoff_latency_p95 < 200ms
  - message_drop_rate < 0.1%
  And all metrics within SLA targets (RT-011)
```

## Implementación

Archivo: `scripts/coding/ai/multi_agent/communication.py`

```python
class AgentCommunication:
    """
    RF-009: Agent communication layer.
    Handles message sending, receiving, and handoffs.
    """

    def __init__(self):
        self.message_queue = MessageQueue()
        self.metrics = MetricsCollector()
        self.logger = MultiAgentLogger()

    @enforce_latency_target("message_send", 10)
    def send_message(self, message: Message):
        """
        RF-009: Send message to another agent.

        Args:
            message: Message object with required fields

        Raises:
            MessageValidationError: If message invalid
            MessageQueueFullError: If target agent queue full
        """
        # Validate message (RF-009 Scenario 11)
        message._validate()

        # Check TTL
        if message.ttl:
            if (datetime.now() - message.timestamp).total_seconds() > message.ttl:
                self.logger.log_warning(f"Message {message.message_id} expired")
                self.metrics.increment("message.expired_count")
                return

        # Send to queue (with retry on failure)
        try:
            self.message_queue.push(message.to_agent, message)
        except MessageQueueFullError:
            # Retry with exponential backoff (RF-009 Scenario 12)
            self._retry_send_with_backoff(message)

        # Log
        self.logger.log_communication(message, latency_ms)

        # Metrics
        self.metrics.increment("messages_sent", tags={"from": message.from_agent})

    @enforce_latency_target("message_receive", 10)
    def receive_messages(self, agent_id: str) -> List[Message]:
        """
        RF-009: Receive messages for agent.

        Returns:
            List of messages ordered by priority then timestamp
        """
        # Get messages from queue
        messages = self.message_queue.pop_all(agent_id)

        # Sort by priority (HIGH → MEDIUM → LOW) then timestamp
        messages.sort(
            key=lambda m: (
                PRIORITY_ORDER.get(m.priority, 999),
                m.timestamp
            )
        )

        # Metrics
        self.metrics.increment(
            "messages_received",
            tags={"agent": agent_id},
            value=len(messages)
        )

        return messages

    @enforce_latency_target("broadcast_send", 50)
    def broadcast(self, message: Message):
        """
        RF-009: Broadcast message to all agents.
        """
        all_agents = self.get_all_agents()

        for agent_id in all_agents:
            if agent_id != message.from_agent:
                # Create copy for each agent
                msg_copy = Message(
                    from_agent=message.from_agent,
                    to_agent=agent_id,
                    message_type=MessageType.BROADCAST,
                    content=message.content
                )
                self.send_message(msg_copy)

        self.logger.log_info(
            f"Broadcast: {message.from_agent} → {len(all_agents)} agents"
        )

    @enforce_latency_target("handoff_transfer", 200)
    def handoff(
        self,
        from_agent: Agent,
        to_agent: Agent,
        task_description: str,
        context: Dict,
        previous_result: Any,
        constraints: Dict = None
    ):
        """
        RF-009: Hand off task from one agent to another.

        Args:
            from_agent: Agent handing off
            to_agent: Agent receiving
            task_description: What next agent should do
            context: Context from previous agent
            previous_result: Result from previous agent
            constraints: Optional constraints to respect
        """
        # Validate handoff (RT-011)
        if not task_description:
            raise ValueError("task_description required for handoff")

        # Build handoff message
        handoff_message = Message(
            from_agent=from_agent.agent_id,
            to_agent=to_agent.agent_id,
            message_type=MessageType.HANDOFF,
            content={
                "action": "execute_handoff",
                "parameters": {
                    "task_description": task_description,
                    "context": context,
                    "previous_result": previous_result,
                    "constraints": constraints or {}
                }
            }
        )

        # Send handoff
        self.send_message(handoff_message)

        # Log handoff (RF-009 Scenario 16)
        context_size_kb = len(json.dumps(context).encode('utf-8')) / 1024

        self.logger.log_handoff(
            from_agent=from_agent.agent_id,
            to_agent=to_agent.agent_id,
            workflow_id=context.get("workflow_id"),
            step_number=context.get("step_number", 0) + 1,
            task_description=task_description,
            context_size_kb=context_size_kb
        )

        # Metrics
        self.metrics.increment("handoffs_count")
```

## Tests

Archivo: `scripts/coding/tests/ai/test_agent_communication.py`

```python
class TestAgentCommunication:
    def test_send_message_between_agents(self):
        """RF-009 Scenario 1: Send message between agents."""
        comm = AgentCommunication()

        message = Message(
            from_agent="FlightAgent",
            to_agent="PaymentAgent",
            message_type=MessageType.REQUEST,
            content={"action": "process_payment", "parameters": {"amount": 450}}
        )

        start = time.perf_counter()
        comm.send_message(message)
        latency_ms = (time.perf_counter() - start) * 1000

        assert latency_ms < 10
        assert message.message_id is not None
        assert message.timestamp is not None

    def test_receive_messages_priority_order(self):
        """RF-009 Scenario 5: Message priority."""
        comm = AgentCommunication()

        # Send messages with different priorities
        comm.send_message(Message(..., priority=Priority.LOW))
        comm.send_message(Message(..., priority=Priority.HIGH))
        comm.send_message(Message(..., priority=Priority.MEDIUM))

        # Receive
        messages = comm.receive_messages("PaymentAgent")

        # Check order: HIGH, MEDIUM, LOW
        assert messages[0].priority == Priority.HIGH
        assert messages[1].priority == Priority.MEDIUM
        assert messages[2].priority == Priority.LOW

    def test_handoff_between_agents(self):
        """RF-009 Scenario 7: Hand-off between agents."""
        comm = AgentCommunication()
        customer_agent = Agent(agent_id="CustomerAgent")
        seller_agent = Agent(agent_id="SellerAgent")

        context = {"order_id": "12345", "amount": 50}
        result = {"refund_eligible": True}

        start = time.perf_counter()
        comm.handoff(
            from_agent=customer_agent,
            to_agent=seller_agent,
            task_description="Approve refund",
            context=context,
            previous_result=result
        )
        latency_ms = (time.perf_counter() - start) * 1000

        assert latency_ms < 200

        # Verify SellerAgent received handoff
        messages = comm.receive_messages("SellerAgent")
        assert len(messages) == 1
        assert messages[0].message_type == MessageType.HANDOFF

    def test_message_ttl_expiration(self):
        """RF-009 Scenario 6: Message TTL."""
        comm = AgentCommunication()

        # Send message with 1s TTL
        message = Message(..., ttl=1)
        comm.send_message(message)

        # Wait 2 seconds
        time.sleep(2)

        # Receive - message should be expired
        messages = comm.receive_messages("PaymentAgent")

        assert len(messages) == 0  # Expired message not delivered
        assert metrics.get("message.expired_count") > 0
```

Resultado esperado: `20 passed in 0.30s`

## Métricas

- Message send latency p95: < 10ms
- Message receive latency p95: < 10ms
- Roundtrip latency p95: < 50ms
- Handoff latency p95: < 200ms
- Broadcast latency p50: < 50ms
- Message drop rate: < 0.1%

## Referencias

- UC-SYS-005: Multi-Agent Orchestration
- ADR-053: Multi-Agent Design Patterns
- RT-011: Multi-Agent Communication and Coordination

---

**Requisito**: Agentes se comunican mediante mensajes estandarizados y hand-offs con context transfer.
**Verificación**: Gherkin scenarios + latency targets + TDD tests.
