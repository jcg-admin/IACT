"""Workspace automation modules, including Hamilton examples."""

from pathlib import Path

from . import hamilton_llm

__all__ = ("hamilton_llm",)

TEST_SUITES = {
    "hamilton_llm": Path("infrastructure/workspace/tests/hamilton_llm"),
}
"""Mapping from workspace identifier to the directory containing its tests."""
