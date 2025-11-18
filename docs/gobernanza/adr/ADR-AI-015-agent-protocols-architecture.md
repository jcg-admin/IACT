# ADR-055: Agent Protocols Architecture (MCP, A2A, NLWeb)

**Estado**: Aceptado
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Agent Communication Protocols
**Relación**:
- Extiende [ADR-053: Multi-Agent Design Patterns](./ADR-053-multi-agent-design-patterns.md)
- Relacionado con [ADR-054: Planning Architecture](./ADR-054-planning-architecture.md)
- Implementado en [RF-013](../ai/requisitos/funcionales/RF-013_mcp_tool_discovery_invocation.md), [RF-014](../ai/requisitos/funcionales/RF-014_a2a_inter_agent_communication.md), [RF-015](../ai/requisitos/funcionales/RF-015_nlweb_natural_language_interface.md)

---

## Contexto

AI agents necesitan protocolos estandarizados para comunicarse con tools, otros agents, y sistemas externos. Sin protocolos definidos:

- **Tool integration chaos**: Cada tool tiene su propia API, sin discovery mechanism
- **Agent isolation**: Agents no pueden comunicarse de forma estructurada
- **External system coupling**: Tight coupling con APIs específicas, difícil cambiar providers
- **No interoperability**: Agents de diferentes frameworks no pueden colaborar
- **Limited observability**: Sin protocolo estándar, difícil tracing y debugging

**Real-world example**: Un travel booking agent necesita:
1. **MCP**: Conectarse a flight search tool, hotel booking tool, payment processor
2. **A2A**: Comunicarse con specialized agents (FlightExpert, HotelExpert, PaymentAgent)
3. **NLWeb**: Interactuar con airline websites vía natural language (cuando no hay API)

We need standardized protocols that provide:
1. **MCP (Model Context Protocol)**: Standard para LLM ↔ tool communication
2. **A2A (Agent-to-Agent)**: Standard para inter-agent communication
3. **NLWeb (Natural Language Web)**: Standard para natural language interfaces to websites

---

## Decisión

We adopt a **Multi-Protocol Architecture** con tres protocols complementarios:

### 1. MCP (Model Context Protocol)

Standard protocol para conectar LLMs con external tools y data sources.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐                          ┌──────────────────┐
│  MCP Client  │ ◄──────── MCP ────────► │   MCP Server     │
│  (LLM Host)  │         Protocol         │  (Tool Provider) │
└──────────────┘                          └──────────────────┘
       │                                            │
       │                                            │
   ┌───▼────┐                                  ┌────▼────┐
   │  LLM   │                                  │  Tools  │
   │ (GPT-4)│                                  │ - search│
   └────────┘                                  │ - calc  │
                                              │ - db    │
                                              └─────────┘
```

**Components**:

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# 1. Tool Schema (MCP Tool Definition)
class ToolParameter(BaseModel):
    """Parameter definition for a tool."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Type: string, number, boolean, object, array")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=False, description="Is parameter required")
    enum: Optional[List[str]] = Field(None, description="Allowed values if enum")
    default: Optional[Any] = Field(None, description="Default value")

class ToolDefinition(BaseModel):
    """MCP Tool definition."""
    name: str = Field(..., description="Unique tool name")
    description: str = Field(..., description="What the tool does")
    parameters: List[ToolParameter] = Field(..., description="Tool parameters")
    returns: Dict[str, str] = Field(..., description="Return value schema")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    category: str = Field(default="general", description="Tool category")
    version: str = Field(default="1.0.0", description="Tool version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "search_flights",
                "description": "Search for available flights between two cities",
                "parameters": [
                    {
                        "name": "origin",
                        "type": "string",
                        "description": "Departure city or airport code",
                        "required": True
                    },
                    {
                        "name": "destination",
                        "type": "string",
                        "description": "Arrival city or airport code",
                        "required": True
                    },
                    {
                        "name": "date",
                        "type": "string",
                        "description": "Departure date (YYYY-MM-DD)",
                        "required": True
                    },
                    {
                        "name": "passengers",
                        "type": "number",
                        "description": "Number of passengers",
                        "required": False,
                        "default": 1
                    }
                ],
                "returns": {
                    "type": "array",
                    "description": "List of available flights"
                },
                "category": "travel",
                "version": "1.0.0"
            }
        }

# 2. MCP Server (Tool Provider)
class MCPServer:
    """MCP Server provides tools to MCP Clients."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_implementations: Dict[str, callable] = {}

    def register_tool(self, tool_def: ToolDefinition, implementation: callable):
        """
        Register a tool with its definition and implementation.

        Args:
            tool_def: Tool definition (schema)
            implementation: Callable that executes the tool
        """
        self.tools[tool_def.name] = tool_def
        self.tool_implementations[tool_def.name] = implementation

    def list_tools(self) -> List[ToolDefinition]:
        """List all available tools (MCP Discovery)."""
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name."""
        return self.tools.get(tool_name)

    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool (MCP Execution).

        Args:
            tool_name: Name of the tool to invoke
            parameters: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ToolNotFoundError: If tool doesn't exist
            ValidationError: If parameters invalid
        """
        if tool_name not in self.tool_implementations:
            raise ToolNotFoundError(f"Tool {tool_name} not found")

        tool_def = self.tools[tool_name]

        # Validate parameters
        self._validate_parameters(tool_def, parameters)

        # Execute tool
        try:
            implementation = self.tool_implementations[tool_name]
            result = implementation(**parameters)

            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e)
            }

    def _validate_parameters(self, tool_def: ToolDefinition, parameters: Dict[str, Any]):
        """Validate tool parameters against definition."""
        # Check required parameters
        required_params = {p.name for p in tool_def.parameters if p.required}
        provided_params = set(parameters.keys())

        missing = required_params - provided_params
        if missing:
            raise ValidationError(f"Missing required parameters: {missing}")

        # Check parameter types
        for param_def in tool_def.parameters:
            if param_def.name in parameters:
                value = parameters[param_def.name]
                # Type validation logic here
                pass  # Simplified for brevity

# 3. MCP Client (LLM Host)
class MCPClient:
    """MCP Client connects to MCP Servers to use tools."""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.connected_servers: Dict[str, MCPServer] = {}
        self.available_tools: Dict[str, ToolDefinition] = {}

    def connect_to_server(self, server: MCPServer):
        """
        Connect to an MCP Server and discover its tools.

        Args:
            server: MCP Server instance
        """
        self.connected_servers[server.name] = server

        # Discover tools from server
        tools = server.list_tools()
        for tool in tools:
            self.available_tools[tool.name] = tool

        print(f"✓ Connected to MCP Server '{server.name}': {len(tools)} tools discovered")

    def get_available_tools(self) -> List[ToolDefinition]:
        """Get all available tools from connected servers."""
        return list(self.available_tools.values())

    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool through MCP.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Tool result
        """
        # Find which server provides this tool
        tool_def = self.available_tools.get(tool_name)
        if not tool_def:
            raise ToolNotFoundError(f"Tool {tool_name} not available")

        # Find server (simplified - in real impl, track tool-to-server mapping)
        for server in self.connected_servers.values():
            if tool_name in server.tools:
                return server.invoke_tool(tool_name, parameters)

        raise ToolNotFoundError(f"No server provides tool {tool_name}")

    def llm_call_with_tools(self, messages: List[Dict], model: str = "gpt-4"):
        """
        Make LLM call with access to MCP tools.

        Args:
            messages: Conversation messages
            model: LLM model to use

        Returns:
            LLM response with tool calls if needed
        """
        # Convert MCP tools to OpenAI function format
        openai_tools = self._convert_tools_to_openai_format()

        response = self.llm_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        # Handle tool calls
        message = response.choices[0].message

        if message.tool_calls:
            # Execute tool calls via MCP
            tool_results = []
            for tool_call in message.tool_calls:
                result = self.invoke_tool(
                    tool_name=tool_call.function.name,
                    parameters=json.loads(tool_call.function.arguments)
                )
                tool_results.append(result)

            return {
                "message": message,
                "tool_calls": message.tool_calls,
                "tool_results": tool_results
            }
        else:
            return {
                "message": message,
                "tool_calls": None,
                "tool_results": None
            }

    def _convert_tools_to_openai_format(self) -> List[Dict]:
        """Convert MCP tool definitions to OpenAI function format."""
        openai_tools = []

        for tool_def in self.available_tools.values():
            # Build parameters schema
            properties = {}
            required = []

            for param in tool_def.parameters:
                properties[param.name] = {
                    "type": param.type,
                    "description": param.description
                }
                if param.enum:
                    properties[param.name]["enum"] = param.enum
                if param.required:
                    required.append(param.name)

            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_def.name,
                    "description": tool_def.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

# Example Usage: MCP
def example_mcp():
    """Example of using MCP protocol."""

    # 1. Create MCP Server (Tool Provider)
    server = MCPServer(name="travel_tools", version="1.0.0")

    # 2. Define and register tools
    search_flights_def = ToolDefinition(
        name="search_flights",
        description="Search for available flights",
        parameters=[
            ToolParameter(name="origin", type="string", description="Departure city", required=True),
            ToolParameter(name="destination", type="string", description="Arrival city", required=True),
            ToolParameter(name="date", type="string", description="Departure date", required=True)
        ],
        returns={"type": "array", "description": "List of flights"}
    )

    def search_flights_impl(origin: str, destination: str, date: str):
        """Implementation of search_flights tool."""
        # Actual implementation here
        return [
            {"airline": "Air France", "price": 650, "departure": "10:00"},
            {"airline": "United", "price": 720, "departure": "14:30"}
        ]

    server.register_tool(search_flights_def, search_flights_impl)

    # 3. Create MCP Client (LLM Host)
    client = MCPClient(llm_client=openai.Client())

    # 4. Connect to server (discovery happens automatically)
    client.connect_to_server(server)

    # 5. Use tools via LLM
    messages = [
        {"role": "user", "content": "Find me flights from NYC to Paris on May 1st"}
    ]

    response = client.llm_call_with_tools(messages)

    if response["tool_results"]:
        print(f"Tool results: {response['tool_results']}")
```

---

### 2. A2A (Agent-to-Agent Protocol)

Standard protocol para inter-agent communication y collaboration.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                  A2A ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐                          ┌──────────────────┐
│   Agent A    │ ◄──────── A2A ────────►  │     Agent B      │
│ (Flight      │         Protocol         │   (Hotel Expert) │
│  Expert)     │                          │                  │
└──────────────┘                          └──────────────────┘
       │                                            │
       ▼                                            ▼
┌────────────────────────────────────────────────────────────┐
│                   A2A Message Bus                           │
│  - Message Routing                                          │
│  - Agent Discovery (Agent Cards)                            │
│  - Event Queue                                              │
│  - Artifact Storage                                         │
└────────────────────────────────────────────────────────────┘
```

**Components**:

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

# 1. Agent Card (Agent Discovery)
class AgentCapability(BaseModel):
    """Capability that an agent can perform."""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What this capability does")
    input_schema: Dict[str, Any] = Field(..., description="Expected input schema")
    output_schema: Dict[str, Any] = Field(..., description="Output schema")

class AgentCard(BaseModel):
    """Agent Card for discovery (like a business card)."""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="What this agent does")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    version: str = Field(default="1.0.0", description="Agent version")
    owner: str = Field(..., description="Agent owner/organization")
    contact: str = Field(..., description="Contact endpoint (URL, email)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_flight_expert",
                "name": "Flight Expert Agent",
                "description": "Specialized in flight search and booking",
                "capabilities": [
                    {
                        "name": "search_flights",
                        "description": "Search available flights",
                        "input_schema": {"origin": "string", "destination": "string", "date": "string"},
                        "output_schema": {"flights": "array"}
                    },
                    {
                        "name": "book_flight",
                        "description": "Book a specific flight",
                        "input_schema": {"flight_id": "string", "passenger_info": "object"},
                        "output_schema": {"booking_confirmation": "object"}
                    }
                ],
                "version": "1.0.0",
                "owner": "TravelCo",
                "contact": "https://api.travelco.com/agents/flight"
            }
        }

# 2. A2A Message
class MessageType(str, Enum):
    """Types of A2A messages."""
    REQUEST = "request"  # Request for action
    RESPONSE = "response"  # Response to request
    EVENT = "event"  # Event notification
    QUERY = "query"  # Information query
    ARTIFACT = "artifact"  # Artifact sharing

class A2AMessage(BaseModel):
    """A2A Message for inter-agent communication."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    from_agent: str = Field(..., description="Sender agent ID")
    to_agent: str = Field(..., description="Recipient agent ID")
    message_type: MessageType = Field(..., description="Type of message")
    capability: Optional[str] = Field(None, description="Capability being invoked (for REQUEST)")
    content: Dict[str, Any] = Field(..., description="Message content/payload")
    correlation_id: Optional[str] = Field(None, description="ID to correlate request/response")
    priority: int = Field(default=5, ge=1, le=10, description="Message priority")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# 3. Artifact (Shared Data between Agents)
class Artifact(BaseModel):
    """Artifact shared between agents."""
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique artifact ID")
    type: str = Field(..., description="Artifact type (document, data, model, etc.)")
    name: str = Field(..., description="Artifact name")
    content: Any = Field(..., description="Artifact content")
    created_by: str = Field(..., description="Agent that created this artifact")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    access_control: List[str] = Field(default_factory=list, description="Agent IDs with access")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# 4. Agent Executor (A2A Runtime)
class AgentExecutor:
    """Executes agent operations and handles A2A communication."""

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self.capability_implementations: Dict[str, callable] = {}
        self.message_queue: List[A2AMessage] = []
        self.artifacts: Dict[str, Artifact] = {}

    def register_capability(self, capability_name: str, implementation: callable):
        """Register implementation for a capability."""
        self.capability_implementations[capability_name] = implementation

    def send_message(self, to_agent: str, message_type: MessageType,
                    content: Dict[str, Any], capability: Optional[str] = None) -> A2AMessage:
        """
        Send message to another agent.

        Args:
            to_agent: Recipient agent ID
            message_type: Type of message
            content: Message content
            capability: Capability being invoked (if REQUEST)

        Returns:
            Sent message
        """
        message = A2AMessage(
            from_agent=self.agent_card.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            capability=capability,
            content=content
        )

        # Send via message bus (simplified - in real impl, use actual message bus)
        print(f"✉ {self.agent_card.name} → {to_agent}: {message_type} ({capability})")

        return message

    def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """
        Receive and process message from another agent.

        Args:
            message: Incoming message

        Returns:
            Response message if applicable
        """
        print(f"📨 {self.agent_card.name} received: {message.message_type} from {message.from_agent}")

        if message.message_type == MessageType.REQUEST:
            # Handle capability request
            if message.capability and message.capability in self.capability_implementations:
                implementation = self.capability_implementations[message.capability]

                try:
                    result = implementation(**message.content)

                    # Send response
                    response = A2AMessage(
                        from_agent=self.agent_card.agent_id,
                        to_agent=message.from_agent,
                        message_type=MessageType.RESPONSE,
                        content={"status": "success", "result": result},
                        correlation_id=message.message_id
                    )

                    return response

                except Exception as e:
                    # Send error response
                    error_response = A2AMessage(
                        from_agent=self.agent_card.agent_id,
                        to_agent=message.from_agent,
                        message_type=MessageType.RESPONSE,
                        content={"status": "error", "error": str(e)},
                        correlation_id=message.message_id
                    )

                    return error_response

        return None

    def create_artifact(self, artifact_type: str, name: str, content: Any,
                       access_control: List[str] = None) -> Artifact:
        """
        Create artifact to share with other agents.

        Args:
            artifact_type: Type of artifact
            name: Artifact name
            content: Artifact content
            access_control: List of agent IDs with access

        Returns:
            Created artifact
        """
        artifact = Artifact(
            type=artifact_type,
            name=name,
            content=content,
            created_by=self.agent_card.agent_id,
            access_control=access_control or []
        )

        self.artifacts[artifact.artifact_id] = artifact

        print(f"📦 Artifact created: {name} ({artifact_type})")

        return artifact

# 5. Agent Registry (Discovery Service)
class AgentRegistry:
    """Central registry for agent discovery."""

    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}

    def register_agent(self, agent_card: AgentCard):
        """Register an agent."""
        self.agents[agent_card.agent_id] = agent_card
        print(f"✓ Agent registered: {agent_card.name}")

    def discover_agents(self, capability_required: Optional[str] = None) -> List[AgentCard]:
        """
        Discover agents, optionally filtered by capability.

        Args:
            capability_required: Required capability name

        Returns:
            List of matching agent cards
        """
        if not capability_required:
            return list(self.agents.values())

        # Filter agents by capability
        matching_agents = []
        for agent_card in self.agents.values():
            for cap in agent_card.capabilities:
                if cap.name == capability_required:
                    matching_agents.append(agent_card)
                    break

        return matching_agents

# Example Usage: A2A
def example_a2a():
    """Example of A2A protocol usage."""

    # 1. Create Agent Cards
    flight_agent_card = AgentCard(
        agent_id="agent_flight",
        name="Flight Expert",
        description="Flight search and booking specialist",
        capabilities=[
            AgentCapability(
                name="search_flights",
                description="Search flights",
                input_schema={"origin": "string", "destination": "string"},
                output_schema={"flights": "array"}
            )
        ],
        owner="TravelCo",
        contact="https://api.travel.com/flight"
    )

    hotel_agent_card = AgentCard(
        agent_id="agent_hotel",
        name="Hotel Expert",
        description="Hotel search and booking specialist",
        capabilities=[
            AgentCapability(
                name="search_hotels",
                description="Search hotels",
                input_schema={"location": "string", "checkin": "string"},
                output_schema={"hotels": "array"}
            )
        ],
        owner="TravelCo",
        contact="https://api.travel.com/hotel"
    )

    # 2. Create Agent Executors
    flight_executor = AgentExecutor(flight_agent_card)
    hotel_executor = AgentExecutor(hotel_agent_card)

    # 3. Register capability implementations
    def search_flights_impl(origin: str, destination: str):
        return [{"airline": "Air France", "price": 650}]

    def search_hotels_impl(location: str, checkin: str):
        return [{"name": "Hotel Paris", "price_per_night": 180}]

    flight_executor.register_capability("search_flights", search_flights_impl)
    hotel_executor.register_capability("search_hotels", search_hotels_impl)

    # 4. Create Agent Registry
    registry = AgentRegistry()
    registry.register_agent(flight_agent_card)
    registry.register_agent(hotel_agent_card)

    # 5. Agent-to-Agent Communication
    # Flight agent sends request to Hotel agent
    request = flight_executor.send_message(
        to_agent="agent_hotel",
        message_type=MessageType.REQUEST,
        capability="search_hotels",
        content={"location": "Paris", "checkin": "2025-05-01"}
    )

    # Hotel agent processes request
    response = hotel_executor.receive_message(request)

    print(f"Response: {response.content if response else 'No response'}")
```

---

### 3. NLWeb (Natural Language Web)

Standard protocol para natural language interfaces to websites (cuando no hay API disponible).

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                  NLWEB ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐                          ┌──────────────────┐
│   Agent      │ ◄──────── NLWeb ───────► │    Website       │
│              │         Interface         │  (Airline, Hotel)│
└──────────────┘                          └──────────────────┘
       │                                            │
       │ Natural Language Command                   │
       │ "Search flights NYC to Paris May 1"        │
       │                                            │
       ▼                                            ▼
┌────────────────────────────────────────────────────────────┐
│               NLWeb Translation Layer                       │
│  1. Parse NL command                                        │
│  2. Map to website actions (DOM interactions)               │
│  3. Execute via browser automation                          │
│  4. Extract results using selectors + LLM                   │
└────────────────────────────────────────────────────────────┘
```

**Components**:

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright, Page
import re

# 1. NLWeb Action
class ActionType(str, Enum):
    """Types of NLWeb actions."""
    NAVIGATE = "navigate"  # Navigate to URL
    CLICK = "click"  # Click element
    TYPE = "type"  # Type text
    SELECT = "select"  # Select option
    EXTRACT = "extract"  # Extract data
    WAIT = "wait"  # Wait for element

class NLWebAction(BaseModel):
    """NLWeb action to execute on a website."""
    action_type: ActionType = Field(..., description="Type of action")
    selector: Optional[str] = Field(None, description="CSS/XPath selector")
    value: Optional[str] = Field(None, description="Value to input (for TYPE, SELECT)")
    extract_schema: Optional[Dict[str, str]] = Field(None, description="Schema for EXTRACT")
    wait_condition: Optional[str] = Field(None, description="Wait condition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# 2. NLWeb Interface Definition
class NLWebInterface(BaseModel):
    """Definition of a natural language interface to a website."""
    interface_id: str = Field(..., description="Unique interface ID")
    name: str = Field(..., description="Interface name")
    base_url: str = Field(..., description="Base URL of website")
    description: str = Field(..., description="What this interface does")
    actions: Dict[str, List[NLWebAction]] = Field(..., description="Named action sequences")
    selectors: Dict[str, str] = Field(default_factory=dict, description="Common selectors")
    version: str = Field(default="1.0.0", description="Interface version")

    class Config:
        json_schema_extra = {
            "example": {
                "interface_id": "airline_booking",
                "name": "Airline Booking Interface",
                "base_url": "https://www.airline.com",
                "description": "Natural language interface for flight search and booking",
                "actions": {
                    "search_flights": [
                        {"action_type": "navigate", "value": "https://www.airline.com/flights"},
                        {"action_type": "type", "selector": "#from", "value": "{origin}"},
                        {"action_type": "type", "selector": "#to", "value": "{destination}"},
                        {"action_type": "type", "selector": "#date", "value": "{date}"},
                        {"action_type": "click", "selector": "button[type='submit']"},
                        {"action_type": "wait", "wait_condition": ".results"},
                        {"action_type": "extract", "selector": ".flight-card",
                         "extract_schema": {"airline": ".airline-name", "price": ".price", "time": ".departure-time"}}
                    ]
                },
                "selectors": {
                    "origin_input": "#from",
                    "destination_input": "#to",
                    "date_input": "#date",
                    "search_button": "button[type='submit']",
                    "results_container": ".results"
                }
            }
        }

# 3. NLWeb Executor
class NLWebExecutor:
    """Executes NLWeb actions using browser automation."""

    def __init__(self, interface: NLWebInterface):
        self.interface = interface
        self.page: Optional[Page] = None
        self.playwright = None
        self.browser = None

    def start_browser(self, headless: bool = True):
        """Start browser session."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

    def stop_browser(self):
        """Stop browser session."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def execute_action_sequence(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a named action sequence.

        Args:
            action_name: Name of action sequence
            parameters: Parameters to inject into actions

        Returns:
            Execution result (extracted data if EXTRACT action)
        """
        if action_name not in self.interface.actions:
            raise ValueError(f"Action '{action_name}' not found in interface")

        if not self.page:
            self.start_browser()

        actions = self.interface.actions[action_name]
        result = {}

        for action in actions:
            # Inject parameters into action values
            injected_action = self._inject_parameters(action, parameters)

            # Execute action
            action_result = self._execute_single_action(injected_action)

            if action.action_type == ActionType.EXTRACT:
                result = action_result

        return result

    def _inject_parameters(self, action: NLWebAction, parameters: Dict[str, Any]) -> NLWebAction:
        """Inject parameters into action (replace {param} placeholders)."""
        injected = action.copy()

        if injected.value:
            for param_name, param_value in parameters.items():
                injected.value = injected.value.replace(f"{{{param_name}}}", str(param_value))

        return injected

    def _execute_single_action(self, action: NLWebAction) -> Optional[Dict[str, Any]]:
        """Execute a single NLWeb action."""
        if action.action_type == ActionType.NAVIGATE:
            self.page.goto(action.value)
            return None

        elif action.action_type == ActionType.CLICK:
            self.page.click(action.selector)
            return None

        elif action.action_type == ActionType.TYPE:
            self.page.fill(action.selector, action.value)
            return None

        elif action.action_type == ActionType.SELECT:
            self.page.select_option(action.selector, action.value)
            return None

        elif action.action_type == ActionType.WAIT:
            self.page.wait_for_selector(action.wait_condition, timeout=10000)
            return None

        elif action.action_type == ActionType.EXTRACT:
            # Extract data using selectors
            elements = self.page.query_selector_all(action.selector)
            extracted_data = []

            for element in elements:
                item = {}
                for field_name, field_selector in action.extract_schema.items():
                    field_element = element.query_selector(field_selector)
                    if field_element:
                        item[field_name] = field_element.inner_text()

                extracted_data.append(item)

            return {"extracted_data": extracted_data}

        return None

# 4. Natural Language Command Parser
class NLWebCommandParser:
    """Parse natural language commands into NLWeb action sequences."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def parse_command(self, nl_command: str, available_actions: List[str]) -> Dict[str, Any]:
        """
        Parse natural language command into action + parameters.

        Args:
            nl_command: Natural language command
            available_actions: List of available action names

        Returns:
            Dict with action_name and parameters
        """
        system_prompt = f"""You are a natural language command parser.
        Parse the user's command into a structured action.

        Available actions: {', '.join(available_actions)}

        Return JSON with:
        {{
          "action_name": "action name from available actions",
          "parameters": {{parameter_name: value}}
        }}
        """

        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nl_command}
            ],
            response_format={"type": "json_object"}
        )

        parsed = json.loads(response.choices[0].message.content)
        return parsed

# Example Usage: NLWeb
def example_nlweb():
    """Example of NLWeb protocol usage."""

    # 1. Define NLWeb Interface for an airline website
    airline_interface = NLWebInterface(
        interface_id="airline_booking",
        name="Airline Booking",
        base_url="https://www.airline.com",
        description="Book flights via natural language",
        actions={
            "search_flights": [
                NLWebAction(action_type=ActionType.NAVIGATE, value="https://www.airline.com/flights"),
                NLWebAction(action_type=ActionType.TYPE, selector="#from", value="{origin}"),
                NLWebAction(action_type=ActionType.TYPE, selector="#to", value="{destination}"),
                NLWebAction(action_type=ActionType.TYPE, selector="#date", value="{date}"),
                NLWebAction(action_type=ActionType.CLICK, selector="button[type='submit']"),
                NLWebAction(action_type=ActionType.WAIT, wait_condition=".results"),
                NLWebAction(action_type=ActionType.EXTRACT, selector=".flight-card",
                           extract_schema={"airline": ".airline-name", "price": ".price"})
            ]
        }
    )

    # 2. Create NLWeb Executor
    executor = NLWebExecutor(airline_interface)

    # 3. Execute action via natural language
    # User command: "Search flights from NYC to Paris on May 1"
    # This gets parsed into:
    result = executor.execute_action_sequence(
        action_name="search_flights",
        parameters={
            "origin": "NYC",
            "destination": "Paris",
            "date": "2025-05-01"
        }
    )

    print(f"Extracted flights: {result}")

    # 4. Cleanup
    executor.stop_browser()
```

---

## Comparación de Protocolos

| Aspecto | MCP | A2A | NLWeb |
|---------|-----|-----|-------|
| **Purpose** | LLM ↔ Tool communication | Agent ↔ Agent communication | Agent ↔ Website (no API) |
| **Components** | Client, Server, Tools | Agent Card, Message, Artifact | Interface, Executor, Parser |
| **Discovery** | list_tools() | Agent Registry | Interface Registry |
| **Communication** | Function calls | Messages (async) | Browser automation |
| **Data Format** | JSON schema | Structured messages | DOM interactions + extraction |
| **Use Case** | Invoke tools from LLM | Multi-agent collaboration | Scrape/interact with websites |
| **Latency** | Low (< 100ms) | Medium (< 500ms) | High (1-5s, browser overhead) |
| **Reliability** | High (typed contracts) | High (message acknowledgment) | Medium (depends on website stability) |

---

## Ventajas

### MCP Benefits
1. **Standardized tool integration**: Single protocol para todas las tools
2. **Dynamic discovery**: Agents discover tools at runtime
3. **Type safety**: Schema validation via ToolDefinition
4. **Version management**: Tools can evolve without breaking clients

### A2A Benefits
1. **Agent interoperability**: Agents from different frameworks can collaborate
2. **Loose coupling**: Agents don't need to know implementation details
3. **Artifact sharing**: Shared data persistence across agents
4. **Event-driven**: Agents can react to events from other agents

### NLWeb Benefits
1. **API-less integration**: Access websites without APIs
2. **Future-proof**: Works even if website changes (LLM adapts)
3. **Natural language commands**: User-friendly interface
4. **Fallback option**: When MCP tools don't exist

---

## Desventajas y Mitigaciones

### MCP Limitations
**Problema**: Tools must be pre-registered on server

**Mitigación**:
- Hot-reload: Server can register tools dynamically
- Plugin system: Tools loaded from plugins directory
- Remote tool discovery: Query multiple MCP servers

### A2A Limitations
**Problema**: Message overhead for simple operations

**Mitigación**:
- Direct invocation for same-process agents
- Batch messages for multiple operations
- Use MCP for tool-like operations (lighter weight)

### NLWeb Limitations
**Problema**: Slow (browser overhead), brittle (website changes)

**Mitigación**:
- Cache interface definitions
- Fallback to screenshot + vision LLM if selectors break
- Use NLWeb only as last resort when MCP/API unavailable

---

## Referencias

1. **MCP Specification**: [Anthropic MCP Docs](https://modelcontextprotocol.io)
2. **A2A Protocol**: [Multi-Agent Communication Standards](https://github.com/AI-Engineer-Foundation/agent-protocol)
3. **Playwright**: [Browser automation framework](https://playwright.dev)
4. **OpenAI Function Calling**: [Function calling guide](https://platform.openai.com/docs/guides/function-calling)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
**Aprobado por**: AI Architecture Team
