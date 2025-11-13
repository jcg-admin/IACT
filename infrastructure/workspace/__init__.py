"""Workspace automation modules, including Hamilton examples and dev tools."""

from pathlib import Path

from . import dev_tools, hamilton_llm

__all__ = ("dev_tools", "hamilton_llm")

TEST_SUITES = {
    "hamilton_llm": Path("infrastructure/workspace/tests/hamilton_llm"),
    "dev_tools_language_server": Path("infrastructure/workspace/tests/dev_tools/language_server"),
}
"""Mapping from workspace identifier to the directory containing its tests."""
