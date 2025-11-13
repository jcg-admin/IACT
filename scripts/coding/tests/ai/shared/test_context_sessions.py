#!/usr/bin/env python3
"""Tests for context session utilities (TDD)."""

import asyncio
import sys
from pathlib import Path
from types import ModuleType
import importlib.machinery
import importlib.util

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
CODING_ROOT = SCRIPTS_ROOT / "coding"

# Ensure namespace resolution for "scripts" package used across tests
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CODING_ROOT) not in sys.path:
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

MODULE_NAME = "scripts.ai.shared.context_sessions"
module_spec = importlib.util.find_spec(MODULE_NAME)
if module_spec is None:
    module_path = CODING_ROOT / "ai" / "shared" / "context_sessions.py"
    module_spec = importlib.util.spec_from_file_location(MODULE_NAME, module_path)
    module = importlib.util.module_from_spec(module_spec)
    assert module_spec and module_spec.loader, "No se pudo cargar spec para context_sessions"
    module_spec.loader.exec_module(module)
    sys.modules[MODULE_NAME] = module

from scripts.ai.shared.context_sessions import (  # type: ignore  # pylint: disable=wrong-import-position
    TrimmingSession,
    SummarizingSession,
)


def run_async(coro):
    """Helper to execute async coroutines within sync pytest tests."""
    return asyncio.run(coro)


class DummySummarizer:
    """Deterministic summarizer used in tests."""

    def __init__(self):
        self.calls = 0

    async def summarize(self, messages):  # pylint: disable=unused-argument
        self.calls += 1
        shadow = "Summarize the conversation we had so far."
        summary = "Synthetic summary block"
        await asyncio.sleep(0)
        return shadow, summary


def test_trimming_session_keeps_last_turns():
    session = TrimmingSession("session", max_turns=2)
    transcript = [
        {"role": "user", "content": "First question"},
        {"role": "assistant", "content": "First answer"},
        {"role": "user", "content": "Second question"},
        {"role": "assistant", "content": "Second answer"},
        {"role": "user", "content": "Third question"},
        {"role": "assistant", "content": "Third answer"},
    ]

    run_async(session.add_items(transcript))
    history = run_async(session.get_items())

    assert len(history) == 4
    assert history[0]["content"] == "Second question"
    assert history[-1]["content"] == "Third answer"


def test_trimming_session_respects_dynamic_limit():
    session = TrimmingSession("session", max_turns=3)
    run_async(session.add_items([
        {"role": "user", "content": "Alpha"},
        {"role": "assistant", "content": "Ack"},
        {"role": "user", "content": "Beta"},
        {"role": "assistant", "content": "Bee"},
        {"role": "user", "content": "Gamma"},
        {"role": "assistant", "content": "Gee"},
    ]))

    run_async(session.set_max_turns(1))
    history = run_async(session.get_items())

    assert len(history) == 2
    assert history[0]["content"] == "Gamma"

    popped = run_async(session.pop_item())
    assert popped["content"] == "Gee"


def test_summarizing_session_generates_summary_block():
    summarizer = DummySummarizer()
    session = SummarizingSession(
        keep_last_n_turns=1,
        context_limit=2,
        summarizer=summarizer,
        session_id="support",
    )

    run_async(session.add_items([
        {"role": "user", "content": "Initial issue"},
        {"role": "assistant", "content": "First response"},
        {"role": "user", "content": "Follow-up"},
        {"role": "assistant", "content": "Second response"},
        {"role": "user", "content": "Third turn"},
        {"role": "assistant", "content": "Third response"},
    ]))

    history = run_async(session.get_items())
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Summarize the conversation we had so far."
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Synthetic summary block"
    assert history[-2]["content"] == "Third turn"
    assert summarizer.calls == 1

    full_history = run_async(session.get_full_history())
    synthetic_entries = [item for item in full_history if item["metadata"].get("synthetic")]
    assert len(synthetic_entries) == 2
    assert synthetic_entries[0]["metadata"]["kind"] == "history_summary_prompt"
    assert synthetic_entries[1]["metadata"]["kind"] == "history_summary"


def test_summarizing_session_respects_context_limit_without_summary():
    summarizer = DummySummarizer()
    session = SummarizingSession(
        keep_last_n_turns=2,
        context_limit=3,
        summarizer=summarizer,
        session_id="support",
    )

    run_async(session.add_items([
        {"role": "user", "content": "Turn one"},
        {"role": "assistant", "content": "Answer one"},
        {"role": "user", "content": "Turn two"},
        {"role": "assistant", "content": "Answer two"},
    ]))

    history = run_async(session.get_items())
    assert summarizer.calls == 0
    assert history[0]["content"] == "Turn one"
    assert history[-1]["content"] == "Answer two"
