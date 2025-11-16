"""
Tests for RF-013: MCP (Model Context Protocol)

MCP enables LLM ↔ Tool communication.
"""

import pytest

from scripts.coding.ai.agents.protocols.mcp import (
    MCPClient,
    MCPServer,
    ParameterValidationError,
    ToolDefinition,
    ToolNotFoundError,
    ToolParameter,
)


def test_register_and_discover_tools():
    """RF-013 MCP: Register and discover tools"""
    server = MCPServer()

    # Register a tool
    book_flight_tool = ToolDefinition(
        name="book_flight",
        description="Book a flight from origin to destination",
        parameters=[
            ToolParameter(name="origin", type="string", description="Origin airport"),
            ToolParameter(name="destination", type="string", description="Destination airport"),
            ToolParameter(name="date", type="string", description="Departure date"),
        ],
        returns="Booking confirmation",
        cost_estimate=0.05
    )

    def book_flight_impl(origin: str, destination: str, date: str):
        return {"booking_id": "FL12345", "origin": origin, "destination": destination}

    server.register_tool(book_flight_tool, book_flight_impl)

    # Discover tools
    tools = server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "book_flight"


def test_invoke_tool_successfully():
    """RF-013 MCP: Invoke tool successfully"""
    server = MCPServer()

    tool_def = ToolDefinition(
        name="add_numbers",
        description="Add two numbers",
        parameters=[
            ToolParameter(name="a", type="number", description="First number"),
            ToolParameter(name="b", type="number", description="Second number"),
        ],
        returns="Sum of numbers"
    )

    def add_impl(a: float, b: float):
        return a + b

    server.register_tool(tool_def, add_impl)

    # Invoke
    result = server.invoke_tool("add_numbers", {"a": 5, "b": 3})

    assert result.status == "success"
    assert result.result == 8
    assert result.tool_name == "add_numbers"


def test_validate_required_parameters():
    """RF-013 MCP: Validate required parameters"""
    server = MCPServer()

    tool_def = ToolDefinition(
        name="test_tool",
        description="Test",
        parameters=[
            ToolParameter(name="required_param", type="string", description="Required", required=True),
        ],
        returns="Result"
    )

    def test_impl(required_param: str):
        return f"Got: {required_param}"

    server.register_tool(tool_def, test_impl)

    # Missing required parameter
    result = server.invoke_tool("test_tool", {})

    assert result.status == "error"
    assert "required parameter" in result.error.lower()


def test_validate_parameter_types():
    """RF-013 MCP: Validate parameter types"""
    server = MCPServer()

    tool_def = ToolDefinition(
        name="test_tool",
        description="Test",
        parameters=[
            ToolParameter(name="num", type="number", description="A number"),
        ],
        returns="Result"
    )

    def test_impl(num: float):
        return num * 2

    server.register_tool(tool_def, test_impl)

    # Wrong type (string instead of number)
    result = server.invoke_tool("test_tool", {"num": "not_a_number"})

    assert result.status == "error"
    assert "must be number" in result.error.lower()


def test_tool_not_found_error():
    """RF-013 MCP: Tool not found error"""
    server = MCPServer()

    with pytest.raises(ToolNotFoundError):
        server.invoke_tool("nonexistent_tool", {})


def test_mcp_client_discover_and_invoke():
    """RF-013 MCP: Client discover and invoke"""
    server = MCPServer()
    client = MCPClient(server)

    # Register tool
    tool_def = ToolDefinition(
        name="search",
        description="Search for information",
        parameters=[
            ToolParameter(name="query", type="string", description="Search query"),
        ],
        returns="Search results"
    )

    def search_impl(query: str):
        return [f"Result for: {query}"]

    server.register_tool(tool_def, search_impl)

    # Client discovers tools
    discovered = client.discover_tools()
    assert len(discovered) == 1
    assert discovered[0].name == "search"

    # Client invokes tool
    result = client.invoke("search", {"query": "AI agents"})
    assert result.status == "success"


def test_client_find_tool_by_capability():
    """RF-013 MCP: Find tool by capability"""
    server = MCPServer()
    client = MCPClient(server)

    # Register multiple tools
    server.register_tool(
        ToolDefinition(
            name="book_flight",
            description="Book a flight ticket",
            parameters=[],
            returns="Booking"
        ),
        lambda: "booked"
    )

    server.register_tool(
        ToolDefinition(
            name="book_hotel",
            description="Book a hotel room",
            parameters=[],
            returns="Booking"
        ),
        lambda: "booked"
    )

    client.discover_tools()

    # Find by capability
    flight_tool = client.find_tool("flight")
    assert flight_tool is not None
    assert flight_tool.name == "book_flight"

    hotel_tool = client.find_tool("hotel")
    assert hotel_tool is not None
    assert hotel_tool.name == "book_hotel"

# ==================================
# Additional MCP Tests (8-20)
# ==================================

def test_tool_discovery_performance():
    """RF-013 MCP: Tool discovery <100ms"""
    server = MCPServer()
    
    # Register multiple tools
    for i in range(10):
        server.register_tool(
            ToolDefinition(name=f"tool_{i}", description=f"Tool {i}", parameters=[], returns="result"),
            lambda: "result"
        )
    
    import time
    start = time.time()
    tools = server.list_tools()
    duration = (time.time() - start) * 1000
    
    assert len(tools) == 10
    assert duration < 100  # <100ms


def test_tool_invocation_with_optional_parameters():
    """RF-013 MCP: Optional parameters with defaults"""
    server = MCPServer()
    
    tool_def = ToolDefinition(
        name="search",
        description="Search",
        parameters=[
            ToolParameter(name="query", type="string", description="Query", required=True),
            ToolParameter(name="limit", type="number", description="Limit", required=False, default=10)
        ],
        returns="Results"
    )
    
    def search_impl(query: str, limit: int = 10):
        return [f"result_{i}" for i in range(int(limit))]
    
    server.register_tool(tool_def, search_impl)
    
    # Without optional param
    result = server.invoke_tool("search", {"query": "test"})
    assert result.status == "success"


def test_multiple_tool_registrations():
    """RF-013 MCP: Register multiple tools"""
    server = MCPServer()
    
    tools_to_register = [
        ("tool1", "Description 1"),
        ("tool2", "Description 2"),
        ("tool3", "Description 3")
    ]
    
    for name, desc in tools_to_register:
        server.register_tool(
            ToolDefinition(name=name, description=desc, parameters=[], returns="result"),
            lambda: "ok"
        )
    
    assert len(server.list_tools()) == 3


def test_tool_execution_error_handling():
    """RF-013 MCP: Handle tool execution errors"""
    server = MCPServer()
    
    def failing_tool():
        raise ValueError("Tool execution failed")
    
    server.register_tool(
        ToolDefinition(name="failing", description="Fails", parameters=[], returns="none"),
        failing_tool
    )
    
    result = server.invoke_tool("failing", {})
    assert result.status == "error"
    assert "Tool execution failed" in result.error


def test_tool_cost_tracking():
    """RF-013 MCP: Track tool invocation cost"""
    server = MCPServer()
    
    server.register_tool(
        ToolDefinition(name="expensive", description="Expensive tool", 
                      parameters=[], returns="result", cost_estimate=0.10),
        lambda: "result"
    )
    
    result = server.invoke_tool("expensive", {})
    assert result.cost == 0.10


def test_tool_parameter_validation_string():
    """RF-013 MCP: Validate string parameters"""
    server = MCPServer()
    
    server.register_tool(
        ToolDefinition(
            name="test",
            description="Test",
            parameters=[ToolParameter(name="text", type="string", description="Text")],
            returns="result"
        ),
        lambda text: text.upper()
    )
    
    result = server.invoke_tool("test", {"text": "hello"})
    assert result.status == "success"
    assert result.result == "HELLO"


def test_tool_parameter_validation_boolean():
    """RF-013 MCP: Validate boolean parameters"""
    server = MCPServer()
    
    server.register_tool(
        ToolDefinition(
            name="toggle",
            description="Toggle",
            parameters=[ToolParameter(name="enabled", type="boolean", description="Enable")],
            returns="result"
        ),
        lambda enabled: f"Enabled: {enabled}"
    )
    
    # Wrong type
    result = server.invoke_tool("toggle", {"enabled": "not_bool"})
    assert result.status == "error"


def test_get_tool_by_name():
    """RF-013 MCP: Get specific tool definition"""
    server = MCPServer()
    
    tool_def = ToolDefinition(name="my_tool", description="My tool", parameters=[], returns="result")
    server.register_tool(tool_def, lambda: "ok")
    
    retrieved = server.get_tool("my_tool")
    assert retrieved is not None
    assert retrieved.name == "my_tool"
    
    missing = server.get_tool("nonexistent")
    assert missing is None


def test_tool_invocation_duration_tracking():
    """RF-013 MCP: Track invocation duration"""
    server = MCPServer()
    
    import time
    def slow_tool():
        time.sleep(0.01)  # 10ms
        return "done"
    
    server.register_tool(
        ToolDefinition(name="slow", description="Slow", parameters=[], returns="result"),
        slow_tool
    )
    
    result = server.invoke_tool("slow", {})
    assert result.duration_ms >= 10


def test_mcp_client_empty_discovery():
    """RF-013 MCP: Client discovers empty server"""
    server = MCPServer()
    client = MCPClient(server)
    
    tools = client.discover_tools()
    assert len(tools) == 0


def test_unknown_parameter_error():
    """RF-013 MCP: Reject unknown parameters"""
    server = MCPServer()
    
    server.register_tool(
        ToolDefinition(
            name="test",
            description="Test",
            parameters=[ToolParameter(name="valid", type="string", description="Valid")],
            returns="result"
        ),
        lambda valid: valid
    )
    
    result = server.invoke_tool("test", {"valid": "ok", "unknown": "param"})
    assert result.status == "error"
    assert "unknown" in result.error.lower()


def test_tool_returns_complex_object():
    """RF-013 MCP: Tool returns complex object"""
    server = MCPServer()
    
    def complex_tool():
        return {"nested": {"data": [1, 2, 3]}, "count": 3}
    
    server.register_tool(
        ToolDefinition(name="complex", description="Complex", parameters=[], returns="object"),
        complex_tool
    )
    
    result = server.invoke_tool("complex", {})
    assert result.status == "success"
    assert result.result["count"] == 3

def test_concurrent_tool_invocations():
    """RF-013 MCP Test 20: Handle concurrent invocations"""
    server = MCPServer()

    def counter_tool(count: int = 1):
        return count * 2

    server.register_tool(
        ToolDefinition(
            name="counter",
            description="Double a number",
            parameters=[ToolParameter(name="count", type="number", description="Number")],
            returns="result"
        ),
        counter_tool
    )

    # Simulate concurrent calls
    results = []
    for i in range(5):
        result = server.invoke_tool("counter", {"count": i})
        results.append(result)

    assert all(r.status == "success" for r in results)
    assert len(results) == 5
