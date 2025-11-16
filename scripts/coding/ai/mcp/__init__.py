"""Helpers for configuring MCP servers and registries."""

from .registry import (
    MCPRegistry,
    LocalMCPServer,
    RemoteMCPServer,
    build_default_registry,
)

__all__ = [
    "MCPRegistry",
    "LocalMCPServer",
    "RemoteMCPServer",
    "build_default_registry",
]
