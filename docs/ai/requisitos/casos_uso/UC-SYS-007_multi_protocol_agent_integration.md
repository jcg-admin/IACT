# UC-SYS-007: Multi-Protocol Agent Integration

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Agent Protocols
**Actor Principal**: Multi-Protocol Travel Booking System
**Stakeholders**: User, Flight Agent, Hotel Agent, MCP Servers, External Websites
**Relación**:
- Implementa [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
- Sigue [RT-014: Protocol Performance and Security Standards](../reglas_tecnicas/RT-014_protocol_performance_security_standards.md)

---

## Descripción

Demonstrates integration of all three protocols (MCP, A2A, NLWeb) in a unified travel booking system where agents use MCP for tool access, A2A for inter-agent communication, and NLWeb as fallback when APIs unavailable.

---

## Precondiciones

1. **MCP Server disponible**: Travel tools registered (search_flights, search_hotels)
2. **Agent Registry operativo**: FlightAgent y HotelAgent registered
3. **Browser automation ready**: Playwright configured para NLWeb fallback
4. **Security configured**: Authentication, rate limiting, encryption enabled

---

## Post condiciones

### Éxito
1. Travel plan completed usando optimal protocol para cada operation
2. MCP usado para 80%+ operations (fastest path)
3. A2A usado para agent coordination
4. NLWeb usado solo cuando MCP/A2A unavailable (< 5% operations)
5. Total latency < 10s para complete booking

### Fracaso
1. Protocol fallback failed (no alternative available)
2. Security violation detected
3. Total latency > 20s (timeout)

---

## Flujo Principal

### Escenario: Book trip using multi-protocol integration

**Input**: "Book a trip to Paris: flight from NYC May 1, hotel 3 nights"

#### Paso 1: MCP Tool Discovery

```python
# 1.1. Connect to MCP Server
mcp_client = MCPClient(llm_client=openai.Client())
travel_server = MCPServer(name="travel_tools")

# Register tools
flight_tool = ToolDefinition(
    name="search_flights",
    description="Search flights",
    parameters=[
        ToolParameter(name="origin", type="string", required=True),
        ToolParameter(name="destination", type="string", required=True),
        ToolParameter(name="date", type="string", required=True)
    ],
    returns={"type": "array"}
)
travel_server.register_tool(flight_tool, search_flights_impl)

# Connect and discover (< 100ms)
mcp_client.connect_to_server(travel_server)
# Output: "✓ Connected to MCP Server 'travel_tools': 5 tools discovered"
```

#### Paso 2: A2A Agent Discovery and Registration

```python
# 2.1. Create Agent Cards
flight_agent_card = AgentCard(
    agent_id="agent_flight",
    name="Flight Expert",
    capabilities=[
        AgentCapability(name="search_flights", description="Search flights",
                       input_schema={"origin": "str", "dest": "str"},
                       output_schema={"flights": "array"})
    ]
)

hotel_agent_card = AgentCard(
    agent_id="agent_hotel",
    name="Hotel Expert",
    capabilities=[
        AgentCapability(name="search_hotels", description="Search hotels",
                       input_schema={"location": "str", "dates": "str"},
                       output_schema={"hotels": "array"})
    ]
)

# 2.2. Register with Agent Registry
registry = AgentRegistry()
registry.register_agent(flight_agent_card)
registry.register_agent(hotel_agent_card)
```

#### Paso 3: Execute via MCP (Primary Path)

```python
# 3.1. Search flights via MCP
result = mcp_client.invoke_tool(
    tool_name="search_flights",
    parameters={"origin": "NYC", "destination": "Paris", "date": "2025-05-01"}
)

# Result (450ms):
{
    "status": "success",
    "result": [
        {"airline": "Air France", "price": 650, "departure": "10:00"},
        {"airline": "United", "price": 720, "departure": "14:30"}
    ]
}
```

#### Paso 4: A2A Coordination (Hotel depends on Flight dates)

```python
# 4.1. Flight agent sends message to Hotel agent
flight_executor = AgentExecutor(flight_agent_card)
hotel_executor = AgentExecutor(hotel_agent_card)

# Create artifact with flight details
flight_artifact = flight_executor.create_artifact(
    artifact_type="flight_booking",
    name="Paris Flight Details",
    content={"arrival_date": "2025-05-01", "departure_date": "2025-05-04"},
    access_control=["agent_hotel"]
)

# Send A2A message (< 50ms)
message = flight_executor.send_message(
    to_agent="agent_hotel",
    message_type=MessageType.REQUEST,
    capability="search_hotels",
    content={
        "location": "Paris",
        "checkin": "2025-05-01",
        "checkout": "2025-05-04",
        "artifact_id": flight_artifact.artifact_id
    }
)

# Hotel agent processes request
response = hotel_executor.receive_message(message)
# Response (600ms): {"status": "success", "result": [...]}
```

#### Paso 5: NLWeb Fallback (if MCP/A2A fail)

```python
# 5.1. IF MCP tool unavailable, fallback to NLWeb
try:
    result = mcp_client.invoke_tool("search_flights", params)
except ToolNotFoundError:
    # Fallback to NLWeb (browser automation)
    airline_interface = NLWebInterface(
        interface_id="airline_booking",
        base_url="https://www.airline.com",
        actions={
            "search_flights": [
                NLWebAction(action_type=ActionType.NAVIGATE,
                           value="https://www.airline.com/flights"),
                NLWebAction(action_type=ActionType.TYPE,
                           selector="#from", value="{origin}"),
                NLWebAction(action_type=ActionType.TYPE,
                           selector="#to", value="{destination}"),
                NLWebAction(action_type=ActionType.CLICK,
                           selector="button[type='submit']"),
                NLWebAction(action_type=ActionType.EXTRACT,
                           selector=".flight-card",
                           extract_schema={"airline": ".name", "price": ".price"})
            ]
        }
    )

    nlweb_executor = NLWebExecutor(airline_interface)
    result = nlweb_executor.execute_action_sequence(
        action_name="search_flights",
        parameters={"origin": "NYC", "destination": "Paris"}
    )
    # Result (4.5s - slower but functional)
```

---

## Flujos Alternos

### FA-1: MCP Tool Invocation Fails → Retry then Fallback

**Trigger**: MCP tool times out

```python
# Primary: MCP (fails)
try:
    result = mcp_client.invoke_tool("search_flights", params)
except TimeoutError:
    logger.warning("MCP timeout, retrying...")

    # Retry once
    try:
        result = mcp_client.invoke_tool("search_flights", params)
    except TimeoutError:
        logger.error("MCP failed, falling back to NLWeb")

        # Fallback: NLWeb
        result = nlweb_executor.execute_action_sequence("search_flights", params)
```

**Metrics**: MCP attempt: 2.5s (timeout), Retry: 2.5s (timeout), NLWeb: 4.5s → Total: 9.5s

### FA-2: A2A Message Lost → Timeout and Resend

**Trigger**: A2A message not acknowledged within 5s

```python
import asyncio

async def send_with_ack(executor, message, timeout=5.0):
    """Send A2A message with acknowledgment."""
    ack_received = asyncio.Event()

    # Send message
    executor.send_message(...)

    # Wait for acknowledgment
    try:
        await asyncio.wait_for(ack_received.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"No ACK for {message.message_id}, resending...")
        executor.send_message(...)  # Resend
```

### FA-3: Security Violation Detected → Block and Alert

**Trigger**: Authentication failure or rate limit exceeded

```python
# Rate limit check
if not rate_limiter.allow_request(client_id):
    raise RateLimitExceeded(f"Client {client_id} exceeded rate limit")

# Authentication check
if not security_manager.authenticate_client(client_id, signature, timestamp):
    logger.critical(f"Authentication failed for {client_id}")
    # Alert security team
    alert_service.send_alert(
        severity="CRITICAL",
        message=f"Authentication failure: {client_id}",
        details={"client_id": client_id, "timestamp": timestamp}
    )
    raise AuthenticationError("Invalid credentials")
```

---

## Métricas de Éxito

| Métrica | Objetivo | Resultado Ejemplo |
|---------|----------|-------------------|
| MCP Usage | > 80% | 85% (flight+hotel via MCP) |
| A2A Coordination Latency | < 100ms | 75ms |
| NLWeb Fallback Rate | < 5% | 3% |
| Total Booking Time | < 10s | 8.2s |
| Security Violations | 0 | 0 |

---

## Protocolo Selection Logic

```python
class ProtocolSelector:
    """Selects optimal protocol for each operation."""

    def select_protocol(self, operation: str, context: Dict) -> str:
        """
        Select protocol based on availability and performance.

        Priority:
        1. MCP (fastest, most reliable)
        2. A2A (for agent coordination)
        3. NLWeb (fallback only)
        """
        # Check if MCP tool available
        if self._is_mcp_tool_available(operation):
            return "MCP"

        # Check if A2A agent can handle
        if self._is_a2a_agent_available(operation):
            return "A2A"

        # Fallback to NLWeb
        if self._is_nlweb_interface_available(operation):
            return "NLWeb"

        raise NoProtocolAvailable(f"No protocol for operation: {operation}")
```

---

## Referencias

1. [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
2. [RT-014: Protocol Performance and Security Standards](../reglas_tecnicas/RT-014_protocol_performance_security_standards.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
