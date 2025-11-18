"""Memory primitives so MCP servers match the agent experience."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Dict, List, Mapping, Optional, Tuple


class MemoryType(str, Enum):
    """Memory taxonomy aligned with the agent documentation."""

    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    PERSONA = "persona"
    EPISODIC = "episodic"
    ENTITY = "entity"


@dataclass(frozen=True)
class MemoryRetentionPolicy:
    """Retention behavior for a memory lane."""

    max_entries: Optional[int] = None
    ttl_seconds: Optional[int] = None

    def is_expired(self, created_at: datetime, now: Optional[datetime] = None) -> bool:
        if self.ttl_seconds is None:
            return False
        now = now or datetime.now(UTC)
        return (now - created_at) > timedelta(seconds=self.ttl_seconds)

    def as_dict(self) -> Dict[str, Optional[int]]:
        return {"max_entries": self.max_entries, "ttl_seconds": self.ttl_seconds}


@dataclass(frozen=True)
class MemoryBackendConfig:
    """Where the memory lives (Mem0, Azure AI Search, etc.)."""

    provider: str
    description: str
    capabilities: Tuple[str, ...] = ()
    parameters: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "provider": self.provider,
            "description": self.description,
        }
        if self.capabilities:
            payload["capabilities"] = list(self.capabilities)
        if self.parameters:
            payload["parameters"] = dict(self.parameters)
        return payload


@dataclass(frozen=True)
class MemoryLayerConfig:
    """Glue retention + backend information with a description."""

    memory_type: MemoryType
    retention: MemoryRetentionPolicy
    storage: MemoryBackendConfig
    purpose: str
    tools: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "memory_type": self.memory_type.value,
            "retention": self.retention.as_dict(),
            "storage": self.storage.as_dict(),
            "purpose": self.purpose,
        }
        if self.tools:
            payload["tools"] = list(self.tools)
        return payload


@dataclass(frozen=True)
class MCPServerMemoryProfile:
    """Full memory definition for a server."""

    layers: Tuple[MemoryLayerConfig, ...]
    structured_rag: Optional[MemoryBackendConfig] = None

    def as_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "layers": [layer.as_dict() for layer in self.layers],
        }
        if self.structured_rag:
            payload["structured_rag"] = self.structured_rag.as_dict()
        return payload


@dataclass
class MemoryEntry:
    """Concrete memory instance stored in runtime."""

    memory_type: MemoryType
    content: str
    metadata: Mapping[str, object] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def matches_keyword(self, keyword: str) -> bool:
        needle = keyword.lower()
        if needle in self.content.lower():
            return True
        return any(needle in str(value).lower() for value in self.metadata.values())


class MemoryStore:
    """In-memory storage used for working + short term buffers."""

    def __init__(self) -> None:
        self._entries: List[MemoryEntry] = []

    def add_entry(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)

    def get_entries(self, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        entries = [
            entry
            for entry in self._entries
            if memory_type is None or entry.memory_type == memory_type
        ]
        return sorted(entries, key=lambda entry: entry.timestamp)

    def search(self, keyword: str, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        return [
            entry
            for entry in self.get_entries(memory_type)
            if entry.matches_keyword(keyword)
        ]

    def prune(
        self,
        policy: MemoryRetentionPolicy,
        memory_type: Optional[MemoryType] = None,
        now: Optional[datetime] = None,
    ) -> None:
        now = now or datetime.now(UTC)
        survivors: List[MemoryEntry] = []
        for entry in self._entries:
            if memory_type is not None and entry.memory_type != memory_type:
                survivors.append(entry)
                continue
            if policy.is_expired(entry.timestamp, now):
                continue
            survivors.append(entry)
        self._entries = survivors

        if policy.max_entries is None:
            return

        if memory_type is not None:
            self._enforce_max_entries(policy.max_entries, memory_type)
            return

        for memory_lane in {entry.memory_type for entry in self._entries}:
            self._enforce_max_entries(policy.max_entries, memory_lane)

    def _enforce_max_entries(self, max_entries: int, memory_type: MemoryType) -> None:
        lane_entries = self.get_entries(memory_type)
        overflow = len(lane_entries) - max_entries
        if overflow <= 0:
            return
        keep_ids = {id(entry) for entry in lane_entries[-max_entries:]}
        self._entries = [
            entry
            for entry in self._entries
            if entry.memory_type != memory_type or id(entry) in keep_ids
        ]


__all__ = [
    "MemoryBackendConfig",
    "MemoryEntry",
    "MemoryLayerConfig",
    "MemoryRetentionPolicy",
    "MemoryStore",
    "MemoryType",
    "MCPServerMemoryProfile",
]
