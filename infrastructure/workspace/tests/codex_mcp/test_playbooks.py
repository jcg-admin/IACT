"""TDD suite for the Codex MCP workspace playbooks."""

from dataclasses import is_dataclass

import pytest


@pytest.fixture(name="codex_module")
def _codex_module():
    return __import__("infrastructure.workspace.codex_mcp", fromlist=["*"])


def test_codex_cli_server_blueprint_matches_reference_command(codex_module):
    server = codex_module.codex_cli_server_blueprint()
    assert is_dataclass(server), "El blueprint del servidor debe ser un dataclass"

    assert server.name == "Codex CLI"
    assert server.command == "npx"
    assert server.args == ("-y", "codex", "mcp")
    assert server.client_session_timeout_seconds == 360000


def test_single_agent_system_enforces_workspace_write_policy(codex_module):
    system = codex_module.single_agent_system()

    assert system.entrypoint == "Game Designer"
    assert "call the Game Developer" in system.designer.instructions

    developer = system.developer
    assert '"approval-policy": "never"' in developer.instructions
    assert '"sandbox": "workspace-write"' in developer.instructions
    assert "index.html" in developer.instructions

    assert system.handoffs[0].source == "Game Designer"
    assert system.handoffs[0].target == "Game Developer"
    assert system.expected_artifacts == ("index.html",)


def test_environment_setup_documents_dependencies(codex_module):
    requirements = codex_module.ENVIRONMENT_SETUP

    assert "OPENAI_API_KEY" in requirements["env_vars"], "Se debe documentar la variable de entorno"
    assert "openai-agents" in requirements["dependencies"]
    assert ".env" in requirements["post_setup_notes"]


def test_multi_agent_workflow_gates_handoffs_with_artifacts(codex_module):
    workflow = codex_module.multi_agent_workflow()

    assert codex_module.RECOMMENDED_PROMPT_PREFIX_TOKEN in workflow.designer.instructions
    assert codex_module.RECOMMENDED_PROMPT_PREFIX_TOKEN in workflow.project_manager.instructions

    first_handoff = workflow.handoffs[0]
    assert first_handoff.source == "Project Manager"
    assert first_handoff.target == "Designer"
    assert {"REQUIREMENTS.md", "AGENT_TASKS.md"}.issubset(set(first_handoff.required_artifacts))

    tester_handoff = [rule for rule in workflow.handoffs if rule.target == "Tester"][0]
    assert {"frontend/index.html", "backend/server.js"}.issubset(set(tester_handoff.required_artifacts))

    for agent in (workflow.frontend_developer, workflow.backend_developer, workflow.tester):
        assert '"sandbox": "workspace-write"' in agent.instructions

    assert "Bug Busters" in workflow.task_list_template


def test_workspace_exports_dataclasses_for_agents(codex_module):
    workflow = codex_module.multi_agent_workflow()

    assert is_dataclass(workflow.project_manager)
    assert is_dataclass(workflow.handoffs[0])

    deliverables = {
        workflow.frontend_developer.name: set(workflow.frontend_developer.deliverables),
        workflow.backend_developer.name: set(workflow.backend_developer.deliverables),
        workflow.tester.name: set(workflow.tester.deliverables),
    }

    assert {"frontend/index.html", "frontend/styles.css"}.issubset(deliverables["Frontend Developer"])
    assert {"backend/server.js", "backend/package.json"}.issubset(deliverables["Backend Developer"])
    assert {"tests/TEST_PLAN.md"}.issubset(deliverables["Tester"])
