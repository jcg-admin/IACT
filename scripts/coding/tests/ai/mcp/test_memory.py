"""Tests for MCP memory primitives and retention policies."""

import importlib.machinery
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
CODING_ROOT = SCRIPTS_ROOT / "coding"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_ROOT))
sys.path.insert(0, str(CODING_ROOT))

namespace_paths = [str(SCRIPTS_ROOT), str(CODING_ROOT)]
scripts_pkg = ModuleType("scripts")
scripts_pkg.__package__ = "scripts"
scripts_pkg.__path__ = namespace_paths
scripts_pkg.__spec__ = importlib.machinery.ModuleSpec(
    name="scripts",
    loader=None,
    is_package=True,
)
sys.modules.setdefault("scripts", scripts_pkg)


@pytest.fixture(name="memory_module")
def _memory_module():
    return __import__("scripts.coding.ai.mcp.memory", fromlist=["*"])


def test_memory_store_groups_entries_by_type(memory_module):
    store = memory_module.MemoryStore()

    working_entry = memory_module.MemoryEntry(
        memory_type=memory_module.MemoryType.WORKING,
        content="Book a trip to Paris",
        metadata={"intent": "travel"},
    )
    long_term_entry = memory_module.MemoryEntry(
        memory_type=memory_module.MemoryType.LONG_TERM,
        content="Ben enjoys skiing and coffee with a mountain view",
        metadata={"user": "Ben"},
    )

    store.add_entry(working_entry)
    store.add_entry(long_term_entry)

    working_entries = store.get_entries(memory_module.MemoryType.WORKING)
    long_term_entries = store.get_entries(memory_module.MemoryType.LONG_TERM)

    assert working_entries == [working_entry]
    assert long_term_entries == [long_term_entry]


def test_memory_store_prunes_entries_with_retention_policy(memory_module):
    store = memory_module.MemoryStore()
    policy = memory_module.MemoryRetentionPolicy(max_entries=2, ttl_seconds=60)

    first = memory_module.MemoryEntry(
        memory_type=memory_module.MemoryType.SHORT_TERM,
        content="Flight preference: window seat",
    )
    second = memory_module.MemoryEntry(
        memory_type=memory_module.MemoryType.SHORT_TERM,
        content="Hotel preference: near museums",
    )
    third = memory_module.MemoryEntry(
        memory_type=memory_module.MemoryType.SHORT_TERM,
        content="Restaurant preference: vegetarian",
    )

    store.add_entry(first)
    store.add_entry(second)
    store.add_entry(third)

    store.prune(policy, memory_type=memory_module.MemoryType.SHORT_TERM)

    remaining = store.get_entries(memory_module.MemoryType.SHORT_TERM)
    assert len(remaining) == 2
    assert remaining[-1].content == "Restaurant preference: vegetarian"


def test_registry_exposes_memory_profiles(memory_module):
    registry_module = __import__("scripts.coding.ai.mcp.registry", fromlist=["*"])
    registry = registry_module.build_default_registry()

    assert "github-mcp-server" in registry.memory_profiles
    profile = registry.memory_profiles["github-mcp-server"]

    layers = {layer.memory_type: layer for layer in profile.layers}
    assert memory_module.MemoryType.WORKING in layers
    assert layers[memory_module.MemoryType.LONG_TERM].storage.provider == "mem0"
    assert profile.structured_rag.provider == "azure_ai_search"
