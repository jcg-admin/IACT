"""Workspace automation modules, including Hamilton examples, Codex playbooks and dev tools."""

from pathlib import Path

from . import codex_mcp, dev_tools, hamilton_llm

__all__ = ("codex_mcp", "dev_tools", "hamilton_llm")

TEST_SUITES = {
    "hamilton_llm": Path("infrastructure/workspace/tests/hamilton_llm"),
    "dev_tools_language_server": Path("infrastructure/workspace/tests/dev_tools/language_server"),
    "codex_mcp": Path("infrastructure/workspace/tests/codex_mcp"),
}
"""Mapping from workspace identifier to the directory containing its tests."""
