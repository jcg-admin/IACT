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
