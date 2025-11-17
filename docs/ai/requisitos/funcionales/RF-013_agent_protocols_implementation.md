# RF-013: Agent Protocols Implementation (MCP, A2A, NLWeb)

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Agent Protocols
**Relación**:
- Implementa [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
- Sigue [RT-014: Protocol Performance and Security Standards](../reglas_tecnicas/RT-014_protocol_performance_security_standards.md)
- Relacionado con [UC-SYS-007: Multi-Protocol Agent Integration](../casos_uso/UC-SYS-007_multi_protocol_agent_integration.md)

---

## Descripción

Comprehensive functional requirements for implementing all three agent protocols: MCP (Model Context Protocol), A2A (Agent-to-Agent), and NLWeb (Natural Language Web). Includes 60 Gherkin scenarios covering tool discovery, agent communication, browser automation, security, and fallback mechanisms.

---

## MCP (Model Context Protocol) - Escenarios 1-20

### Escenario 1: MCP Tool Discovery
```gherkin
Given an MCP Server con 5 tools registered
When MCP Client connects y ejecuta list_tools()
Then debe retornar 5 ToolDefinition objects
And cada tool debe tener name, description, parameters, returns
And la operación debe completar en < 100ms
```

**Test Template**:
```python
def test_mcp_tool_discovery():
    """RF-013: MCP Scenario 1 - Tool Discovery"""
    server = MCPServer(name="test_server")

    # Register 5 tools
    for i in range(5):
        tool_def = ToolDefinition(name=f"tool_{i}", description=f"Tool {i}",
                                 parameters=[], returns={"type": "object"})
        server.register_tool(tool_def, lambda: {})

    client = MCPClient(llm_client=mock_llm)

    start = time.time()
    client.connect_to_server(server)
    duration = time.time() - start

    tools = client.get_available_tools()
    assert len(tools) == 5
    assert all(hasattr(t, 'name') and hasattr(t, 'description') for t in tools)
    assert duration < 0.1
```

### Escenario 2: MCP Tool Invocation Success
```gherkin
Given MCP Server con tool "search_flights" registered
When Client invoca search_flights con {origin: "NYC", destination: "Paris"}
Then debe retornar {"status": "success", "result": [...]}
And debe completar en < 500ms
And debe registrar metric mcp_tool_invocations_total
```

**Test Template**:
```python
def test_mcp_tool_invocation_success():
    """RF-013: MCP Scenario 2 - Tool Invocation Success"""
    server = MCPServer(name="travel")

    def search_flights_impl(origin, destination):
        return [{"airline": "Test Air", "price": 500}]

    tool_def = ToolDefinition(
        name="search_flights",
        description="Search flights",
        parameters=[
            ToolParameter(name="origin", type="string", required=True),
            ToolParameter(name="destination", type="string", required=True)
        ],
        returns={"type": "array"}
    )
    server.register_tool(tool_def, search_flights_impl)

    client = MCPClient(llm_client=mock_llm)
    client.connect_to_server(server)

    start = time.time()
    result = client.invoke_tool("search_flights", {"origin": "NYC", "destination": "Paris"})
    duration = time.time() - start

    assert result["status"] == "success"
    assert len(result["result"]) > 0
    assert duration < 0.5
```

### Escenario 3: MCP Parameter Validation
```gherkin
Given tool "search_flights" requiere parameters origin y destination
When Client invoca sin parameter "destination"
Then debe lanzar ValidationError con mensaje "Missing required parameter: destination"
And no debe ejecutar la tool implementation
```

**Test Template**:
```python
def test_mcp_parameter_validation():
    """RF-013: MCP Scenario 3 - Parameter Validation"""
    server = MCPServer(name="travel")

    tool_def = ToolDefinition(
        name="search_flights",
        parameters=[
            ToolParameter(name="origin", type="string", required=True),
            ToolParameter(name="destination", type="string", required=True)
        ],
        returns={"type": "array"}
    )

    def impl(**kwargs):
        raise AssertionError("Should not be called")

    server.register_tool(tool_def, impl)

    client = MCPClient(llm_client=mock_llm)
    client.connect_to_server(server)

    with pytest.raises(ValidationError) as exc:
        client.invoke_tool("search_flights", {"origin": "NYC"})  # Missing destination

    assert "destination" in str(exc.value)
```

### Escenarios 4-10: Security, Rate Limiting, Type Validation
**Note**: Similar structure for authentication (Scenario 4), rate limiting (Scenario 5), type validation (Scenario 6), enum validation (Scenario 7), tool not found (Scenario 8), timeout handling (Scenario 9), concurrent invocations (Scenario 10).

### Escenarios 11-15: Integration with LLM
**Scenario 11**: LLM function calling with MCP tools
**Scenario 12**: Multi-tool orchestration
**Scenario 13**: Tool result formatting
**Scenario 14**: Error propagation to LLM
**Scenario 15**: Tool caching

### Escenarios 16-20: Advanced Features
**Scenario 16**: Dynamic tool registration
**Scenario 17**: Tool versioning
**Scenario 18**: Tool deprecation
**Scenario 19**: Batch tool invocation
**Scenario 20**: Tool execution tracing

---

## A2A (Agent-to-Agent Protocol) - Escenarios 21-40

### Escenario 21: Agent Registry and Discovery
```gherkin
Given Agent Registry vacío
When se registran 3 agents (FlightAgent, HotelAgent, ActivityAgent)
Then registry.discover_agents() debe retornar 3 AgentCard objects
And cada card debe tener agent_id, name, capabilities
And discover_agents(capability_required="search_flights") debe retornar solo FlightAgent
```

**Test Template**:
```python
def test_agent_registry_discovery():
    """RF-013: A2A Scenario 21 - Agent Discovery"""
    registry = AgentRegistry()

    flight_card = AgentCard(
        agent_id="flight", name="Flight Agent",
        capabilities=[AgentCapability(name="search_flights", description="Search")]
    )
    hotel_card = AgentCard(
        agent_id="hotel", name="Hotel Agent",
        capabilities=[AgentCapability(name="search_hotels", description="Search")]
    )

    registry.register_agent(flight_card)
    registry.register_agent(hotel_card)

    all_agents = registry.discover_agents()
    assert len(all_agents) == 2

    flight_agents = registry.discover_agents(capability_required="search_flights")
    assert len(flight_agents) == 1
    assert flight_agents[0].agent_id == "flight"
```

### Escenario 22: A2A Message Sending
```gherkin
Given FlightAgent executor creado
When send_message(to_agent="hotel", message_type=REQUEST, capability="search_hotels", content={...})
Then debe retornar A2AMessage con message_id generado
And message.from_agent debe ser "flight"
And message.timestamp debe ser reciente (< 1s ago)
And operación debe completar en < 50ms
```

**Test Template**:
```python
def test_a2a_message_sending():
    """RF-013: A2A Scenario 22 - Message Sending"""
    flight_card = AgentCard(agent_id="flight", name="Flight", capabilities=[])
    executor = AgentExecutor(flight_card)

    start = time.time()
    message = executor.send_message(
        to_agent="hotel",
        message_type=MessageType.REQUEST,
        capability="search_hotels",
        content={"location": "Paris"}
    )
    duration = time.time() - start

    assert message.message_id is not None
    assert message.from_agent == "flight"
    assert message.to_agent == "hotel"
    assert (datetime.now() - message.timestamp).total_seconds() < 1.0
    assert duration < 0.05
```

### Escenario 23: A2A Message Receiving and Processing
```gherkin
Given HotelAgent con capability "search_hotels" implementado
When recibe REQUEST message con capability="search_hotels"
Then debe ejecutar la implementation
And debe retornar RESPONSE message con status="success"
And correlation_id debe match el REQUEST message_id
```

**Test Template**:
```python
def test_a2a_message_receiving():
    """RF-013: A2A Scenario 23 - Message Receiving"""
    hotel_card = AgentCard(agent_id="hotel", name="Hotel", capabilities=[])
    executor = AgentExecutor(hotel_card)

    def search_hotels_impl(location):
        return [{"name": "Hotel Paris", "price": 200}]

    executor.register_capability("search_hotels", search_hotels_impl)

    request = A2AMessage(
        from_agent="flight",
        to_agent="hotel",
        message_type=MessageType.REQUEST,
        capability="search_hotels",
        content={"location": "Paris"}
    )

    response = executor.receive_message(request)

    assert response is not None
    assert response.message_type == MessageType.RESPONSE
    assert response.content["status"] == "success"
    assert response.correlation_id == request.message_id
```

### Escenarios 24-30: Artifacts, Events, Security
**Scenario 24**: Create and share artifacts
**Scenario 25**: Artifact access control
**Scenario 26**: Message encryption
**Scenario 27**: Agent identity verification
**Scenario 28**: Event broadcasting
**Scenario 29**: Message queue management
**Scenario 30**: Message priority handling

### Escenarios 31-40: Advanced Communication
**Scenario 31**: Request-response pattern with timeout
**Scenario 32**: Asynchronous event handling
**Scenario 33**: Multi-agent coordination
**Scenario 34**: Capability negotiation
**Scenario 35**: Agent lifecycle management
**Scenario 36**: Message persistence
**Scenario 37**: Dead letter queue
**Scenario 38**: Circuit breaker for failing agents
**Scenario 39**: Agent health monitoring
**Scenario 40**: Distributed tracing across agents

---

## NLWeb (Natural Language Web) - Escenarios 41-60

### Escenario 41: NLWeb Interface Definition
```gherkin
Given NLWebInterface para airline website
When interface define action "search_flights" con 6 steps (navigate, type, type, type, click, extract)
Then interface.actions["search_flights"] debe tener 6 NLWebAction objects
And cada action debe tener action_type y selector (excepto navigate y extract)
```

**Test Template**:
```python
def test_nlweb_interface_definition():
    """RF-013: NLWeb Scenario 41 - Interface Definition"""
    interface = NLWebInterface(
        interface_id="airline",
        name="Airline Booking",
        base_url="https://airline.com",
        actions={
            "search_flights": [
                NLWebAction(action_type=ActionType.NAVIGATE, value="https://airline.com/flights"),
                NLWebAction(action_type=ActionType.TYPE, selector="#from", value="{origin}"),
                NLWebAction(action_type=ActionType.TYPE, selector="#to", value="{destination}"),
                NLWebAction(action_type=ActionType.TYPE, selector="#date", value="{date}"),
                NLWebAction(action_type=ActionType.CLICK, selector="button[type='submit']"),
                NLWebAction(action_type=ActionType.EXTRACT, selector=".flight-card",
                           extract_schema={"airline": ".name", "price": ".price"})
            ]
        }
    )

    assert "search_flights" in interface.actions
    assert len(interface.actions["search_flights"]) == 6
    assert interface.actions["search_flights"][0].action_type == ActionType.NAVIGATE
```

### Escenario 42: NLWeb Action Execution
```gherkin
Given NLWebExecutor con browser iniciado
When ejecuta action NAVIGATE con value="https://airline.com"
Then page.url debe ser "https://airline.com"
And operación debe completar en < 3s
```

**Test Template**:
```python
def test_nlweb_action_execution():
    """RF-013: NLWeb Scenario 42 - Action Execution"""
    interface = NLWebInterface(
        interface_id="test",
        name="Test",
        base_url="https://example.com",
        actions={}
    )

    executor = NLWebExecutor(interface)
    executor.start_browser(headless=True)

    navigate_action = NLWebAction(
        action_type=ActionType.NAVIGATE,
        value="https://example.com"
    )

    start = time.time()
    executor._execute_single_action(navigate_action)
    duration = time.time() - start

    assert "example.com" in executor.page.url
    assert duration < 3.0

    executor.stop_browser()
```

### Escenario 43: NLWeb Parameter Injection
```gherkin
Given action con value="{origin}"
When ejecuta con parameters={"origin": "NYC"}
Then el valor inyectado debe ser "NYC"
And el placeholder {origin} debe ser reemplazado
```

**Test Template**:
```python
def test_nlweb_parameter_injection():
    """RF-013: NLWeb Scenario 43 - Parameter Injection"""
    interface = NLWebInterface(
        interface_id="test",
        name="Test",
        base_url="https://example.com",
        actions={}
    )

    executor = NLWebExecutor(interface)

    action = NLWebAction(
        action_type=ActionType.TYPE,
        selector="#input",
        value="{origin}"
    )

    injected = executor._inject_parameters(action, {"origin": "NYC"})

    assert injected.value == "NYC"
    assert "{origin}" not in injected.value
```

### Escenarios 44-50: Data Extraction, Sandboxing
**Scenario 44**: Data extraction with selectors
**Scenario 45**: LLM-based extraction fallback
**Scenario 46**: URL validation (sandboxing)
**Scenario 47**: Browser restart on performance degradation
**Scenario 48**: Screenshot capture on error
**Scenario 49**: Wait for element with timeout
**Scenario 50**: Handle dynamic content

### Escenarios 51-60: Natural Language Commands, Fallbacks
**Scenario 51**: Parse NL command to action
**Scenario 52**: Ambiguous command clarification
**Scenario 53**: Fallback to NLWeb when MCP unavailable
**Scenario 54**: Selector auto-healing (when webpage changes)
**Scenario 55**: Multi-page workflows
**Scenario 56**: Form submission with validation
**Scenario 57**: Cookie and session management
**Scenario 58**: Error recovery (retry navigation)
**Scenario 59**: Parallel browser sessions
**Scenario 60**: Performance monitoring and throttling

---

## Criterios de Validación

### MCP
- ✓ Tool discovery < 100ms
- ✓ Tool invocation < 500ms (simple), < 2s (complex)
- ✓ Parameter validation enforced
- ✓ Authentication and rate limiting active
- ✓ 20/20 scenarios passing

### A2A
- ✓ Message send/receive < 100ms
- ✓ Agent discovery < 200ms
- ✓ Message encryption enabled
- ✓ Identity verification enforced
- ✓ 20/20 scenarios passing

### NLWeb
- ✓ Browser launch < 2s
- ✓ Action execution < 1s per action
- ✓ Data extraction < 2s
- ✓ URL sandboxing enforced
- ✓ 20/20 scenarios passing

---

## Referencias

1. [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
2. [RT-014: Protocol Performance and Security Standards](../reglas_tecnicas/RT-014_protocol_performance_security_standards.md)
3. [UC-SYS-007: Multi-Protocol Agent Integration](../casos_uso/UC-SYS-007_multi_protocol_agent_integration.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Total Escenarios**: 60 (20 MCP + 20 A2A + 20 NLWeb)
