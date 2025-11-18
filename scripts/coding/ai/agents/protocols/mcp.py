"""
MCP (Model Context Protocol): LLM ↔ Tool communication

Implements RF-013 MCP scenarios.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Parameter definition for a tool."""

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, number, boolean, object)")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if optional")


class ToolDefinition(BaseModel):
    """Definition of a tool that can be invoked."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: List[ToolParameter] = Field(
        default_factory=list, description="Tool parameters"
    )
    returns: str = Field(..., description="Return value description")
    cost_estimate: float = Field(default=0.01, description="Estimated cost in USD")


class ToolInvocationResult(BaseModel):
    """Result of tool invocation."""

    status: str = Field(..., description="Status: success, error, timeout")
    tool_name: str = Field(..., description="Name of invoked tool")
    result: Optional[Any] = Field(None, description="Tool result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    cost: float = Field(default=0.0, description="Actual cost in USD")


class ToolNotFoundError(Exception):
    """Raised when tool is not found."""

    pass


class ParameterValidationError(Exception):
    """Raised when parameters fail validation."""

    pass


class MCPServer:
    """MCP Server for tool discovery and invocation."""

    def __init__(self):
        """Initialize MCP server."""
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_implementations: Dict[str, Callable] = {}

    def register_tool(
        self, tool_def: ToolDefinition, implementation: Callable
    ) -> None:
        """
        Register a tool with its implementation.

        Args:
            tool_def: Tool definition
            implementation: Callable that implements the tool
        """
        self.tools[tool_def.name] = tool_def
        self.tool_implementations[tool_def.name] = implementation
        logger.info(f"Registered tool: {tool_def.name}")

    def list_tools(self) -> List[ToolDefinition]:
        """
        List all available tools (MCP Discovery).

        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """
        Get tool definition by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool definition or None if not found
        """
        return self.tools.get(tool_name)

    def invoke_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> ToolInvocationResult:
        """
        Invoke a tool (MCP Execution).

        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool

        Returns:
            Tool invocation result

        Raises:
            ToolNotFoundError: If tool not found
            ParameterValidationError: If parameters invalid
        """
        import time

        start_time = time.time()

        # Check tool exists
        if tool_name not in self.tool_implementations:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")

        tool_def = self.tools[tool_name]

        # Validate parameters
        try:
            self._validate_parameters(tool_def, parameters)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ToolInvocationResult(
                status="error",
                tool_name=tool_name,
                error=f"Parameter validation failed: {str(e)}",
                duration_ms=duration_ms,
                cost=0.0
            )

        # Execute tool
        try:
            implementation = self.tool_implementations[tool_name]
            result = implementation(**parameters)

            duration_ms = (time.time() - start_time) * 1000

            return ToolInvocationResult(
                status="success",
                tool_name=tool_name,
                result=result,
                duration_ms=duration_ms,
                cost=tool_def.cost_estimate
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Tool execution failed: {tool_name} - {str(e)}")

            return ToolInvocationResult(
                status="error",
                tool_name=tool_name,
                error=str(e),
                duration_ms=duration_ms,
                cost=0.0
            )

    def _validate_parameters(
        self, tool_def: ToolDefinition, parameters: Dict[str, Any]
    ) -> None:
        """
        Validate parameters against tool definition.

        Args:
            tool_def: Tool definition
            parameters: Parameters to validate

        Raises:
            ParameterValidationError: If validation fails
        """
        # Check required parameters
        for param in tool_def.parameters:
            if param.required and param.name not in parameters:
                raise ParameterValidationError(
                    f"Missing required parameter: {param.name}"
                )

        # Check parameter types (basic validation)
        for param_name, param_value in parameters.items():
            # Find parameter definition
            param_def = next(
                (p for p in tool_def.parameters if p.name == param_name), None
            )

            if param_def is None:
                raise ParameterValidationError(
                    f"Unknown parameter: {param_name}"
                )

            # Basic type checking
            expected_type = param_def.type
            if expected_type == "string" and not isinstance(param_value, str):
                raise ParameterValidationError(
                    f"Parameter '{param_name}' must be string, got {type(param_value).__name__}"
                )
            elif expected_type == "number" and not isinstance(param_value, (int, float)):
                raise ParameterValidationError(
                    f"Parameter '{param_name}' must be number, got {type(param_value).__name__}"
                )
            elif expected_type == "boolean" and not isinstance(param_value, bool):
                raise ParameterValidationError(
                    f"Parameter '{param_name}' must be boolean, got {type(param_value).__name__}"
                )


class MCPClient:
    """MCP Client for discovering and invoking tools."""

    def __init__(self, server: MCPServer):
        """
        Initialize MCP client.

        Args:
            server: MCP server to connect to
        """
        self.server = server
        self.discovered_tools: List[ToolDefinition] = []

    def discover_tools(self) -> List[ToolDefinition]:
        """
        Discover available tools from server.

        Returns:
            List of available tools
        """
        self.discovered_tools = self.server.list_tools()
        return self.discovered_tools

    def find_tool(self, capability: str) -> Optional[ToolDefinition]:
        """
        Find tool by capability (semantic search).

        Args:
            capability: Capability description (e.g., "book flight")

        Returns:
            Matching tool or None
        """
        # Simple keyword matching (in real impl, use embeddings)
        capability_lower = capability.lower()

        for tool in self.discovered_tools:
            if capability_lower in tool.description.lower():
                return tool
            if capability_lower in tool.name.lower():
                return tool

        return None

    def invoke(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> ToolInvocationResult:
        """
        Invoke a tool through the server.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Invocation result
        """
        return self.server.invoke_tool(tool_name, parameters)
