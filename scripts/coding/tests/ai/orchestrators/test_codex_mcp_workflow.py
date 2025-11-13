"""Tests para el builder de flujos Codex MCP multi-LLM."""

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
sys.modules["scripts"] = scripts_pkg

from scripts.coding.ai.orchestrators import codex_mcp_workflow as workflow


SUPPORTED_PROVIDERS = [
    ("openai", "gpt-4.1"),
    ("anthropic", "claude-3-5-sonnet-20241022"),
    ("huggingface", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
]


@pytest.mark.parametrize("provider,expected_model", SUPPORTED_PROVIDERS)
def test_single_agent_brief_includes_mcp_flags(provider, expected_model):
    builder = workflow.CodexMCPWorkflowBuilder(provider)
    brief = builder.build_single_agent_brief()

    assert brief["provider"] == provider
    assert brief["model"] == expected_model

    server = brief["server"]
    assert server["command"] == "npx"
    assert server["args"] == ["-y", "codex", "mcp"]
    assert server["client_session_timeout_seconds"] == 360000

    developer = brief["agents"]["developer"]
    assert "approval-policy\": \"never\"" in developer["instructions"]
    assert "sandbox\": \"workspace-write\"" in developer["instructions"]


def test_unknown_provider_raises_value_error():
    with pytest.raises(ValueError):
        workflow.CodexMCPWorkflowBuilder("unsupported")


@pytest.mark.parametrize("provider,_", SUPPORTED_PROVIDERS)
def test_required_env_variables_are_declared(provider, _):
    builder = workflow.CodexMCPWorkflowBuilder(provider)
    env_info = builder.required_environment()

    env_names = {entry["name"] for entry in env_info}

    if provider == "openai":
        assert env_names == {"OPENAI_API_KEY"}
    elif provider == "anthropic":
        assert env_names == {"ANTHROPIC_API_KEY"}
    else:
        assert "HUGGINGFACEHUB_API_TOKEN" in env_names
        optional_entry = next(item for item in env_info if item["name"] == "HUGGINGFACEHUB_API_TOKEN")
        assert optional_entry["required"] is False


@pytest.mark.parametrize("provider,_", SUPPORTED_PROVIDERS)
def test_multi_agent_brief_includes_gatekeeping(provider, _):
    builder = workflow.CodexMCPWorkflowBuilder(provider)
    brief = builder.build_multi_agent_brief()

    manager = brief["agents"]["project_manager"]
    instructions = manager["instructions"]
    assert "REQUIREMENTS.md" in instructions
    assert "AGENT_TASKS.md" in instructions
    assert "transfer_to_designer_agent" in instructions
    assert "transfer_to_frontend_developer_agent" in instructions
    assert "transfer_to_backend_developer_agent" in instructions
    assert "transfer_to_tester_agent" in instructions

    gates = brief["workflow"]["gate_checks"]
    expected_paths = {
        "design/design_spec.md",
        "frontend/index.html",
        "backend/server.js",
    }
    actual_paths = {gate["artifact"] for gate in gates}
    assert expected_paths.issubset(actual_paths)

    tracing = brief["tracing"]
    assert tracing["enabled"] is True
    assert "Traces" in tracing["notes"]
