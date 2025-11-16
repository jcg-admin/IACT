"""Declarative registry for Model Context Protocol servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

from .memory import (
    MCPServerMemoryProfile,
    MemoryBackendConfig,
    MemoryLayerConfig,
    MemoryRetentionPolicy,
    MemoryType,
)


@dataclass(frozen=True)
class RemoteMCPServer:
    """Metadata to connect to a remote MCP server exposed over HTTP(S)."""

    name: str
    url: str
    mode: str = "readonly"
    headers: Mapping[str, str] = field(default_factory=dict)

    def as_cli_entry(self) -> Dict[str, object]:
        payload: Dict[str, object] = {"url": self.url, "mode": self.mode}
        if self.headers:
            payload["headers"] = dict(self.headers)
        return payload


@dataclass(frozen=True)
class LocalMCPServer:
    """Metadata for spawning a local MCP server via CLI (e.g., Playwright)."""

    name: str
    command: str
    args: Tuple[str, ...]
    allowed_origins: Tuple[str, ...]
    output_dir: str
    viewport_size: Tuple[int, int]
    env: Mapping[str, str] = field(default_factory=dict)

    def as_cli_entry(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "command": self.command,
            "args": list(self.args),
            "metadata": {
                "allowed_origins": list(self.allowed_origins),
                "output_dir": self.output_dir,
                "viewport_size": self.viewport_size,
            },
        }
        if self.env:
            payload["env"] = dict(self.env)
        return payload


@dataclass(frozen=True)
class MCPRegistry:
    """Collection of remote/local MCP server definitions plus memory profiles."""

    remote_servers: Tuple[RemoteMCPServer, ...]
    local_servers: Tuple[LocalMCPServer, ...]
    memory_profiles: Mapping[str, MCPServerMemoryProfile] = field(default_factory=dict)

    def as_cli_config(self) -> Dict[str, Dict[str, object]]:
        """Serialize registry so CLI tooling can consume it directly."""

        remote = {server.name: server.as_cli_entry() for server in self.remote_servers}
        local = {server.name: server.as_cli_entry() for server in self.local_servers}
        payload: Dict[str, Dict[str, object]] = {"remote": remote, "local": local}
        if self.memory_profiles:
            payload["memory_profiles"] = {
                name: profile.as_dict() for name, profile in self.memory_profiles.items()
            }
        return payload


def build_default_registry() -> MCPRegistry:
    """Build the registry that mirrors the Copilot CLI log shared by the user."""

    remote_servers = (
        RemoteMCPServer(
            name="blackbird-mcp-server",
            url="https://api.githubcopilot.com/mcp/readonly",
            mode="readonly",
        ),
        RemoteMCPServer(
            name="github-mcp-server",
            url="https://api.githubcopilot.com/mcp/readonly",
            mode="readonly",
        ),
    )

    allowed_origins = ("localhost", "localhost:*", "127.0.0.1", "127.0.0.1:*")
    allowed_origins_flag = ";".join(allowed_origins)
    viewport_size = (1280, 720)

    local_servers = (
        LocalMCPServer(
            name="playwright",
            command="npx",
            args=(
                "@playwright/mcp@0.0.40",
                "--viewport-size",
                f"{viewport_size[0]}, {viewport_size[1]}",
                "--output-dir",
                "/tmp/playwright-logs",
                "--allowed-origins",
                allowed_origins_flag,
            ),
            allowed_origins=allowed_origins,
            output_dir="/tmp/playwright-logs",
            viewport_size=viewport_size,
        ),
    )

    memory_profiles = _build_default_memory_profiles()

    return MCPRegistry(
        remote_servers=remote_servers,
        local_servers=local_servers,
        memory_profiles=memory_profiles,
    )


def _build_default_memory_profiles() -> Dict[str, MCPServerMemoryProfile]:
    """Mirror the agent memory stack so MCP servers feel identical."""

    working_layer = MemoryLayerConfig(
        memory_type=MemoryType.WORKING,
        retention=MemoryRetentionPolicy(max_entries=5, ttl_seconds=900),
        storage=MemoryBackendConfig(
            provider="working_buffer",
            description="Scratchpad that extracts requirements, proposals, and current asks.",
            capabilities=("cot", "context-tracking"),
        ),
        purpose="Capture the most relevant snippets for the current MCP exchange.",
        tools=("structured_note_taker",),
    )

    short_term_layer = MemoryLayerConfig(
        memory_type=MemoryType.SHORT_TERM,
        retention=MemoryRetentionPolicy(max_entries=20, ttl_seconds=7200),
        storage=MemoryBackendConfig(
            provider="conversation_buffer",
            description="Stores the current MCP session so follow-ups keep the context.",
            capabilities=("session-context", "followup-linking"),
        ),
        purpose="Maintain rolling conversational context for the duration of a workspace run.",
        tools=("mem0",),
    )

    long_term_layer = MemoryLayerConfig(
        memory_type=MemoryType.LONG_TERM,
        retention=MemoryRetentionPolicy(max_entries=200),
        storage=MemoryBackendConfig(
            provider="mem0",
            description="Persist user preferences, past actions, and lessons learned.",
            capabilities=("preference-storage", "self-improvement"),
            parameters={"workspace": "codex"},
        ),
        purpose="Personalize the MCP experience across sessions and repos.",
        tools=("mem0", "whiteboard_memory"),
    )

    persona_layer = MemoryLayerConfig(
        memory_type=MemoryType.PERSONA,
        retention=MemoryRetentionPolicy(max_entries=50),
        storage=MemoryBackendConfig(
            provider="whiteboard_memory",
            description="Enforces the target persona (designer, developer, reviewer, etc.).",
            capabilities=("role-grounding",),
        ),
        purpose="Keep the MCP responses aligned with the intended role/voice.",
        tools=("persona_enforcer",),
    )

    episodic_layer = MemoryLayerConfig(
        memory_type=MemoryType.EPISODIC,
        retention=MemoryRetentionPolicy(max_entries=100),
        storage=MemoryBackendConfig(
            provider="mem0",
            description="Records task-level attempts, failures, and outcomes.",
            capabilities=("episode-tracking", "workflow-replay"),
        ),
        purpose="Let agents learn from past MCP workflows and improve autonomously.",
        tools=("knowledge_agent",),
    )

    entity_layer = MemoryLayerConfig(
        memory_type=MemoryType.ENTITY,
        retention=MemoryRetentionPolicy(max_entries=500),
        storage=MemoryBackendConfig(
            provider="azure_ai_search",
            description="Structured store for entities and relationships via Azure AI Search.",
            capabilities=("entity-resolution", "structured-rag"),
            parameters={"index": "codex-mcp-entities"},
        ),
        purpose="Track people, repos, and deliverables mentioned during MCP activity.",
        tools=("azure_ai_search",),
    )

    structured_rag_backend = MemoryBackendConfig(
        provider="azure_ai_search",
        description="Structured RAG profile optimized for multi-turn MCP workflows.",
        capabilities=("structured-rag", "precise-grounding"),
        parameters={"index": "codex-mcp-knowledge", "profile": "default"},
    )

    github_profile = MCPServerMemoryProfile(
        layers=(
            working_layer,
            short_term_layer,
            long_term_layer,
            persona_layer,
            episodic_layer,
            entity_layer,
        ),
        structured_rag=structured_rag_backend,
    )

    playwright_profile = MCPServerMemoryProfile(
        layers=(
            working_layer,
            MemoryLayerConfig(
                memory_type=MemoryType.SHORT_TERM,
                retention=MemoryRetentionPolicy(max_entries=10, ttl_seconds=3600),
                storage=MemoryBackendConfig(
                    provider="execution_buffer",
                    description="Short-term steps from Playwright E2E automation.",
                    capabilities=("workflow-steps",),
                ),
                purpose="Keep DOM + navigation context between MCP UI actions.",
                tools=("playwright",),
            ),
            entity_layer,
        ),
        structured_rag=None,
    )

    return {
        "github-mcp-server": github_profile,
        "playwright": playwright_profile,
    }
