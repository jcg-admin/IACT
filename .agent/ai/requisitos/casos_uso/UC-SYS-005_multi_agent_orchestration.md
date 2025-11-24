---
id: UC-SYS-005
tipo: caso_uso_sistema
relacionado: [ADR-053, RT-011, RT-012, RF-009, RF-010]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# UC-SYS-005: Multi-Agent Orchestration

## Descripción

Sistema orquesta múltiples agentes especializados para completar tareas complejas mediante comunicación, coordinación, y hand-offs entre agentes.

## Actores

- **Sistema**: Orchestrator + Multiple Specialized Agents (no humano)
- **Sistemas Externos**:
  - Message Queue
  - Shared State Storage
  - Distributed Tracing System
  - Metrics Collector

## Precondiciones

- Orchestrator está activo
- Agentes especializados están registrados y disponibles
- Message Queue está operacional
- Shared State está accesible

## Flujo Principal: Orchestrated Workflow

### 1. Request Reception and Decomposition

```
1.1. Sistema recibe user request
     - Example: "Book trip to Paris Dec 15-20"

1.2. Orchestrator decompose request en subtasks
     - Subtask 1: "Find flights to Paris Dec 15-20"
     - Subtask 2: "Find hotels in Paris Dec 15-20"
     - Subtask 3: "Find rental car in Paris Dec 15-20"
     - Subtask 4: "Process payment"
     - Subtask 5: "Send confirmation"

1.3. Orchestrator determina execution strategy
     - Subtasks 1, 2, 3 CAN run in parallel (independent)
     - Subtask 4 MUST wait for 1, 2, 3 (sequential dependency)
     - Subtask 5 MUST wait for 4 (sequential dependency)
     - Strategy: HYBRID (parallel + sequential)

1.4. Orchestrator start workflow trace (RT-012)
     - workflow_id = "wf_book_trip_123"
     - user_request = "Book trip to Paris Dec 15-20"
```

### 2. Agent Routing

```
2.1. Para cada subtask, Orchestrator determina appropriate agent
     - Subtask 1 → FlightAgent (domain="flights")
     - Subtask 2 → HotelAgent (domain="hotels")
     - Subtask 3 → CarAgent (domain="rental_cars")
     - Subtask 4 → PaymentAgent (domain="payment")
     - Subtask 5 → NotificationAgent (domain="notifications")

2.2. Orchestrator verifica agent availability
     - FlightAgent: IDLE ✓
     - HotelAgent: IDLE ✓
     - CarAgent: IDLE ✓
     - PaymentAgent: IDLE ✓
     - NotificationAgent: IDLE ✓

2.3. Orchestrator create messages for each agent (RT-011)
     - Message format: standard (message_id, from, to, type, content)
     - Latency target: < 100ms for routing
```

### 3. Parallel Execution (Subtasks 1-3)

```
3.1. Orchestrator send messages to Flight, Hotel, Car agents (parallel)
     - Message 1: to=FlightAgent, action="search_flights"
     - Message 2: to=HotelAgent, action="search_hotels"
     - Message 3: to=CarAgent, action="search_cars"
     - All messages sent asynchronously

3.2. Each agent receives message (RT-011 latency < 10ms)
     - Agents log receipt (RT-012)
     - Agents acknowledge to Orchestrator (< 100ms)

3.3. Each agent executes task
     - FlightAgent:
       * Add span to trace: "search_flights"
       * Search flights to Paris Dec 15-20
       * Duration: 2.5s
       * Result: 5 flight options found
       * Return result to Orchestrator

     - HotelAgent:
       * Add span to trace: "search_hotels"
       * Search hotels in Paris Dec 15-20
       * Duration: 3.1s
       * Result: 8 hotel options found
       * Return result to Orchestrator

     - CarAgent:
       * Add span to trace: "search_cars"
       * Search rental cars in Paris Dec 15-20
       * Duration: 1.8s
       * Result: 4 car options found
       * Return result to Orchestrator

3.4. Orchestrator waits for all parallel tasks (aggregation timeout: 30s)
     - All 3 agents complete within timeout ✓
     - Total parallel duration: max(2.5s, 3.1s, 1.8s) = 3.1s
     - Update shared state with results

3.5. Orchestrator log parallel execution (RT-012)
     - 3 subtasks completed in parallel
     - Total latency: 3.1s
     - All successful ✓
```

### 4. Sequential Execution (Subtask 4)

```
4.1. Orchestrator wait for subtasks 1-3 to complete ✓

4.2. Orchestrator aggregate results from Flight, Hotel, Car
     - Best flight: Flight A ($450)
     - Best hotel: Hotel B ($150/night = $750 total)
     - Best car: Car C ($80/day = $480 total)
     - Total cost: $450 + $750 + $480 = $1,680

4.3. Orchestrator send message to PaymentAgent (sequential)
     - Message: to=PaymentAgent, action="process_payment"
     - Content: {amount: 1680, items: [flight, hotel, car]}

4.4. PaymentAgent receive and execute
     - Add span to trace: "process_payment"
     - Validate payment method
     - Process payment of $1,680
     - Duration: 5.2s
     - Result: Payment successful, transaction_id="txn_789"

4.5. PaymentAgent return result to Orchestrator
```

### 5. Hand-off to Notification Agent (Subtask 5)

```
5.1. Orchestrator prepare handoff from PaymentAgent → NotificationAgent
     - Context: {flight, hotel, car, payment_confirmation}
     - Task: "Send confirmation email to user"

5.2. Orchestrator send HANDOFF message (RT-011 latency < 200ms)
     - Message type: HANDOFF
     - From: PaymentAgent
     - To: NotificationAgent
     - Content: {
         task: "send_confirmation",
         context: {...},
         previous_result: payment_result
       }

5.3. NotificationAgent receive handoff
     - Add span to trace: "send_confirmation"
     - Log handoff (RT-012)

5.4. NotificationAgent execute
     - Build confirmation email with flight, hotel, car, payment details
     - Send email to user
     - Duration: 0.4s
     - Result: Email sent ✓

5.5. NotificationAgent return result to Orchestrator
```

### 6. Workflow Completion

```
6.1. Orchestrator aggregates all results
     - Flight: Found and selected ✓
     - Hotel: Found and selected ✓
     - Car: Found and selected ✓
     - Payment: Processed ✓
     - Notification: Sent ✓

6.2. Orchestrator end workflow trace (RT-012)
     - Status: SUCCESS
     - Total duration: 15.3s
     - Agents involved: 5
     - Spans: 5
     - Messages exchanged: 8
     - Handoffs: 2

6.3. Sistema return final result to user
     - "Trip booked successfully! Confirmation sent to your email."
     - Total cost: $1,680
     - Confirmation ID: txn_789

6.4. Sistema record metrics (RT-012)
     - workflow.completed_count++
     - workflow.duration_ms = 15,300ms
     - workflow.success = true
```

## Flujos Alternativos

### Alternate 1: Agent Unavailable

```
2A.1. Durante routing, agent no está disponible
      - FlightAgent status: ERROR (not IDLE)

2A.2. Orchestrator log error
      - "FlightAgent unavailable"

2A.3. SI existe backup agent:
      - Route to BackupFlightAgent
      - [Resume: Step 3.1]

2A.4. SI NO existe backup:
      - Workflow FAILS
      - Return error to user: "Flight booking service unavailable"
      - [End - Failure]
```

### Alternate 2: Agent Timeout

```
3A.1. Durante parallel execution, agent no responde en tiempo
      - HotelAgent toma > 30s (aggregation timeout exceeded)

3A.2. Orchestrator cancel HotelAgent task
      - Send CANCEL message to HotelAgent

3A.3. Orchestrator log timeout (RT-012)
      - agent_id=HotelAgent, error="timeout"

3A.4. SI task is optional:
      - Continue without hotel booking
      - [Resume: Step 4.1]

3A.5. SI task is required:
      - Workflow FAILS
      - Return error: "Hotel booking timed out"
      - [End - Failure]
```

### Alternate 3: Agent Error

```
3B.1. Durante execution, agent encuent error
      - CarAgent: "No rental cars available Dec 15-20"

3B.2. Agent return error result
      - AgentResult(success=False, error="No cars available")

3B.3. Orchestrator log error (RT-012)
      - agent_id=CarAgent, error_type="NoResultsError"

3B.4. SI error es recoverable:
      - Retry con diferentes parámetros
      - [Resume: Step 3.3 para CarAgent]

3B.5. SI error NO es recoverable:
      - Workflow FAILS parcialmente
      - Return: "Flight and hotel booked, but car rental unavailable"
      - [Continue to payment con partial booking]
```

### Alternate 4: Conflicting Recommendations (Collaborative Filtering)

```
4A.1. Multiple agents provide different recommendations
      - HotelAgent A recommends: Hotel X (price-focused)
      - HotelAgent B recommends: Hotel Y (quality-focused)
      - HotelAgent C recommends: Hotel Z (location-focused)

4A.2. Orchestrator detect conflict (RT-011)
      - 3 different recommendations → conflict

4A.3. Orchestrator resolve conflict via voting
      - Weights: {price: 0.2, quality: 0.4, location: 0.3, reviews: 0.1}
      - Hotel X score: 0.65
      - Hotel Y score: 0.82 (winner)
      - Hotel Z score: 0.71

4A.4. Orchestrator select Hotel Y
      - [Resume: Step 4.2 con Hotel Y selected]
```

### Alternate 5: Message Queue Full

```
3C.1. Durante message send, queue está full
      - MessageQueueFullError raised

3C.2. Orchestrator retry con exponential backoff
      - Retry 1: wait 100ms, retry → fail
      - Retry 2: wait 500ms, retry → fail
      - Retry 3: wait 2000ms, retry → success

3C.3. SI retry success:
      - [Resume: Step 3.1]

3C.4. SI all retries fail:
      - Workflow FAILS
      - Log error: "Message queue full, cannot proceed"
      - [End - Failure]
```

### Alternate 6: Shared State Lock Timeout

```
3D.1. Durante shared state update, lock no se puede adquirir
      - Lock timeout: 1s exceeded

3D.2. Orchestrator retry lock acquisition
      - Max 3 retries con backoff

3D.3. SI lock acquired en retry:
      - Update shared state
      - [Resume: Step 3.5]

3D.4. SI lock NOT acquired:
      - Log warning: "Shared state not updated (lock timeout)"
      - Continue sin shared state update (eventual consistency)
      - [Resume: Step 4.1]
```

## Flujos de Patterns Específicos

### Pattern: Group Chat (Stock Recommendation)

```
GC.1. User request: "What stock should I buy?"

GC.2. Orchestrator create group chat con 3 expert agents:
      - IndustryExpertAgent (tech sector)
      - TechnicalAnalysisAgent (chart patterns)
      - FundamentalAnalysisAgent (financials)

GC.3. Orchestrator broadcast query to group
      - Message type: BROADCAST
      - To: all 3 agents

GC.4. Each agent analyze y responde al group:
      - IndustryExpert: "AAPL strong in tech sector"
      - TechnicalAnalyst: "AAPL shows bullish pattern (RSI=65)"
      - FundamentalAnalyst: "AAPL P/E ratio attractive (P/E=28)"

GC.5. All agents see all responses (group context)

GC.6. Orchestrator aggregate recommendations:
      - All 3 agree on AAPL
      - Confidence: HIGH (unanimous)

GC.7. Return recommendation: "Buy AAPL (unanimous expert consensus)"
```

### Pattern: Hand-off (Refund Process)

```
HO.1. User request: "Process refund for order #12345"

HO.2. Orchestrator create linear workflow:
      - Step 1: CustomerAgent (validate request)
      - Step 2: SellerAgent (approve/reject)
      - Step 3: PaymentAgent (process refund)
      - Step 4: NotificationAgent (notify customer)

HO.3. CustomerAgent validates request:
      - Order #12345 exists ✓
      - Within refund window (30 days) ✓
      - Result: APPROVED for refund
      - Handoff to SellerAgent

HO.4. SellerAgent reviews:
      - Item returned: YES ✓
      - Condition: GOOD ✓
      - Result: APPROVED
      - Handoff to PaymentAgent

HO.5. PaymentAgent processes:
      - Refund amount: $50
      - Payment reversed ✓
      - Result: REFUNDED
      - Handoff to NotificationAgent

HO.6. NotificationAgent sends email:
      - "Refund of $50 processed for order #12345"
      - Email sent ✓

HO.7. Workflow complete: Refund processed end-to-end
```

## Postcondiciones

### Éxito

- Workflow completado con all subtasks successful
- Trace almacenado con complete timeline
- Metrics recorded (duration, agent utilization, message count)
- User recibe confirmation

### Fallo

- Workflow failed due to agent unavailability, timeout, or error
- Trace almacenado con failure reason
- Metrics recorded (failure count, error type)
- User recibe error message

## Requisitos No Funcionales

- **Performance** (RT-011):
  - Message send/receive: < 10ms
  - Routing: < 100ms
  - Handoff: < 200ms
  - Aggregation timeout: < 30s

- **Observability** (RT-012):
  - All agent actions logged
  - All messages logged
  - Workflow traced end-to-end
  - Real-time dashboards updated (5s refresh)

- **Reliability**:
  - Retry failed messages (3 attempts with backoff)
  - Handle agent failures gracefully
  - Eventual consistency for shared state

## Métricas

```python
MULTI_AGENT_METRICS = {
    "workflow_duration_avg": 15.3,  # seconds
    "workflow_success_rate": 0.95,  # 95%

    "parallel_speedup": 2.8,  # vs sequential
    # Sequential: 2.5 + 3.1 + 1.8 = 7.4s
    # Parallel: max(2.5, 3.1, 1.8) = 3.1s
    # Speedup: 7.4 / 3.1 = 2.39x

    "agent_utilization_avg": 0.65,  # 65%
    "message_latency_p95": 8,  # ms
    "handoff_latency_p95": 150,  # ms

    "error_rate": 0.05,  # 5%
    "timeout_rate": 0.02,  # 2%
}
```

## Diagramas

### Secuencia: Parallel + Sequential Workflow

```
User         Orchestrator  FlightAgent  HotelAgent  CarAgent  PaymentAgent  NotifyAgent
 |                |              |            |         |          |             |
 |--request------>|              |            |         |          |             |
 |                |--decompose   |            |         |          |             |
 |                |--route       |            |         |          |             |
 |                |              |            |         |          |             |
 |                |--search----->|            |         |          |             |
 |                |--search------|----------->|         |          |             |
 |                |--search------|------------|-------->|          |             |
 |                |              |            |         |          |             |
 |                |              |    [Parallel Execution - 3.1s]  |             |
 |                |              |            |         |          |             |
 |                |<--result-----|            |         |          |             |
 |                |<--result-----|------------|         |          |             |
 |                |<--result-----|------------|---------|          |             |
 |                |              |            |         |          |             |
 |                |--aggregate   |            |         |          |             |
 |                |              |            |         |          |             |
 |                |--pay---------|------------|---------|--------->|             |
 |                |              |            |         |          |             |
 |                |              |            |         |    [Payment - 5.2s]    |
 |                |              |            |         |          |             |
 |                |<--result-----|------------|---------|----------|             |
 |                |              |            |         |          |             |
 |                |--handoff-----|------------|---------|----------|------------>|
 |                |              |            |         |          |             |
 |                |              |            |         |          |    [Notify - 0.4s]
 |                |              |            |         |          |             |
 |                |<--result-----|------------|---------|----------|-------------|
 |                |              |            |         |          |             |
 |<--confirmation-|              |            |         |          |             |
 |                |              |            |         |          |             |
```

## Referencias

- ADR-053: Multi-Agent Design Patterns
- RT-011: Multi-Agent Communication and Coordination
- RT-012: Multi-Agent Performance and Observability
- ADR-048: AI Agent Memory (shared state, episodic memory)

---

**Caso de Uso**: Sistema orquesta múltiples agentes especializados mediante comunicación, coordinación, y patterns.
**Objetivo**: Completar tareas complejas con especialización, paralelización, y fault tolerance.
