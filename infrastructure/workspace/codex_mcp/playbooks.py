"""Declarative playbooks to orchestrate Codex CLI MCP-based agent systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

RECOMMENDED_PROMPT_PREFIX_TOKEN = "{RECOMMENDED_PROMPT_PREFIX}"
"""Placeholder token representing the Agents SDK recommended handoff prefix."""

ENVIRONMENT_SETUP = {
    "env_vars": ("OPENAI_API_KEY",),
    "dependencies": ("openai-agents", "openai"),
    "post_setup_notes": (
        ".env",
        "Create a .env file with OPENAI_API_KEY and load it via python-dotenv before running the playbooks.",
        "%pip install openai-agents openai",
    ),
}
"""Environment checklist derived from the stakeholder instructions."""


@dataclass(frozen=True)
class MCPServerBlueprint:
    """Execution contract for starting Codex CLI as an MCP server."""

    name: str
    command: str
    args: Tuple[str, ...]
    client_session_timeout_seconds: int


@dataclass(frozen=True)
class AgentBlueprint:
    """Declarative description of an agent wired against the Codex MCP server."""

    name: str
    instructions: str
    model: str | None = None
    tools: Tuple[str, ...] = ()
    mcp_servers: Tuple[MCPServerBlueprint, ...] = ()
    handoffs: Tuple[str, ...] = ()
    deliverables: Tuple[str, ...] = ()


@dataclass(frozen=True)
class HandoffRule:
    """Gate a transition between agents ensuring artefacts exist before continuing."""

    source: str
    target: str
    required_artifacts: Tuple[str, ...]


@dataclass(frozen=True)
class SingleAgentSystem:
    """Encapsulates the two-agent Codex workflow (designer → developer)."""

    server: MCPServerBlueprint
    designer: AgentBlueprint
    developer: AgentBlueprint
    entrypoint: str
    expected_artifacts: Tuple[str, ...]
    handoffs: Tuple[HandoffRule, ...]


@dataclass(frozen=True)
class MultiAgentWorkflow:
    """Encapsulates the orchestrated multi-agent Codex workflow with gating logic."""

    server: MCPServerBlueprint
    project_manager: AgentBlueprint
    designer: AgentBlueprint
    frontend_developer: AgentBlueprint
    backend_developer: AgentBlueprint
    tester: AgentBlueprint
    handoffs: Tuple[HandoffRule, ...]
    task_list_template: str


def codex_cli_server_blueprint() -> MCPServerBlueprint:
    """Return the canonical Codex CLI MCP server invocation."""

    return MCPServerBlueprint(
        name="Codex CLI",
        command="npx",
        args=("-y", "codex", "mcp"),
        client_session_timeout_seconds=360000,
    )


def single_agent_system() -> SingleAgentSystem:
    """Provide the designer→developer configuration described in the guide."""

    server = codex_cli_server_blueprint()

    designer_instructions = (
        "You are an indie game connoisseur. Come up with an idea for a single page html + css + javascript game that a "
        "developer could build in about 50 lines of code. Format your request as a 3 sentence design brief for a game "
        "developer and call the Game Developer coder with your idea."
    )

    developer_instructions = (
        "You are an expert in building simple games using basic html + css + javascript with no dependencies. "
        "Save your work in a file called index.html in the current directory."
        "Always call codex with \"approval-policy\": \"never\" and \"sandbox\": \"workspace-write\""
    )

    designer = AgentBlueprint(
        name="Game Designer",
        instructions=designer_instructions,
        model="gpt-5",
        handoffs=("Game Developer",),
        mcp_servers=(server,),
        deliverables=(),
    )

    developer = AgentBlueprint(
        name="Game Developer",
        instructions=developer_instructions,
        mcp_servers=(server,),
        deliverables=("index.html",),
    )

    handoffs = (
        HandoffRule(
            source="Game Designer",
            target="Game Developer",
            required_artifacts=("index.html",),
        ),
    )

    return SingleAgentSystem(
        server=server,
        designer=designer,
        developer=developer,
        entrypoint="Game Designer",
        expected_artifacts=("index.html",),
        handoffs=handoffs,
    )


def multi_agent_workflow(task_list: str | None = None) -> MultiAgentWorkflow:
    """Provide the multi-agent orchestration blueprint with gated handoffs."""

    server = codex_cli_server_blueprint()

    designer = AgentBlueprint(
        name="Designer",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX_TOKEN}"
            "You are the Designer.\n"
            "Your only source of truth is AGENT_TASKS.md and REQUIREMENTS.md from the Project Manager.\n"
            "Do not assume anything that is not written there.\n\n"
            "You may use the internet for additional guidance or research."
            "Deliverables (write to /design):\n"
            "- design_spec.md – a single page describing the UI/UX layout, main screens, and key visual notes as requested in AGENT_TASKS.md.\n"
            "- wireframe.md – a simple text or ASCII wireframe if specified.\n\n"
            "Keep the output short and implementation-friendly.\n"
            "When complete, handoff to the Project Manager with transfer_to_project_manager."
            "When creating files, call Codex MCP with {\"approval-policy\": \"never\", \"sandbox\": \"workspace-write\"}."
        ),
        model="gpt-5",
        tools=("WebSearchTool",),
        mcp_servers=(server,),
        handoffs=("Project Manager",),
        deliverables=("design/design_spec.md", "design/wireframe.md"),
    )

    frontend_developer = AgentBlueprint(
        name="Frontend Developer",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX_TOKEN}"
            "You are the Frontend Developer.\n"
            "Read AGENT_TASKS.md and design_spec.md. Implement exactly what is described there.\n\n"
            "Deliverables (write to /frontend):\n"
            "- index.html – main page structure\n"
            "- styles.css or inline styles if specified\n"
            "- main.js or game.js if specified\n\n"
            "Follow the Designer’s DOM structure and any integration points given by the Project Manager.\n"
            "Do not add features or branding beyond the provided documents.\n\n"
            "When complete, handoff to the Project Manager with transfer_to_project_manager_agent."
            "When creating files, call Codex MCP with {\"approval-policy\": \"never\", \"sandbox\": \"workspace-write\"}."
        ),
        model="gpt-5",
        mcp_servers=(server,),
        handoffs=("Project Manager",),
        deliverables=("frontend/index.html", "frontend/styles.css", "frontend/game.js"),
    )

    backend_developer = AgentBlueprint(
        name="Backend Developer",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX_TOKEN}"
            "You are the Backend Developer.\n"
            "Read AGENT_TASKS.md and REQUIREMENTS.md. Implement the backend endpoints described there.\n\n"
            "Deliverables (write to /backend):\n"
            "- package.json – include a start script if requested\n"
            "- server.js – implement the API endpoints and logic exactly as specified\n\n"
            "Keep the code as simple and readable as possible. No external database.\n\n"
            "When complete, handoff to the Project Manager with transfer_to_project_manager_agent."
            "When creating files, call Codex MCP with {\"approval-policy\": \"never\", \"sandbox\": \"workspace-write\"}."
        ),
        model="gpt-5",
        mcp_servers=(server,),
        handoffs=("Project Manager",),
        deliverables=("backend/package.json", "backend/server.js"),
    )

    tester = AgentBlueprint(
        name="Tester",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX_TOKEN}"
            "You are the Tester.\n"
            "Read AGENT_TASKS.md and TEST.md. Verify that the outputs of the other roles meet the acceptance criteria.\n\n"
            "Deliverables (write to /tests):\n"
            "- TEST_PLAN.md – bullet list of manual checks or automated steps as requested\n"
            "- test.sh or a simple automated script if specified\n\n"
            "Keep it minimal and easy to run.\n\n"
            "When complete, handoff to the Project Manager with transfer_to_project_manager."
            "When creating files, call Codex MCP with {\"approval-policy\": \"never\", \"sandbox\": \"workspace-write\"}."
        ),
        model="gpt-5",
        mcp_servers=(server,),
        handoffs=("Project Manager",),
        deliverables=("tests/TEST_PLAN.md", "tests/test.sh"),
    )

    project_manager = AgentBlueprint(
        name="Project Manager",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX_TOKEN}"
            "You are the Project Manager.\n\n"
            "Objective:\n"
            "Convert the input task list into three project-root files the team will execute against.\n\n"
            "Deliverables (write in project root):\n"
            "- REQUIREMENTS.md: concise summary of product goals, target users, key features, and constraints.\n"
            "- TEST.md: tasks with [Owner] tags (Designer, Frontend, Backend, Tester) and clear acceptance criteria.\n"
            "- AGENT_TASKS.md: one section per role containing project name, deliverables and key notes.\n\n"
            "Process:\n"
            "- Resolve ambiguities with minimal assumptions.\n"
            "- Create files using Codex MCP with {\"approval-policy\": \"never\", \"sandbox\": \"workspace-write\"}.\n"
            "- Do not create folders beyond the ones specified.\n\n"
            "Handoffs (gated by required files):\n"
            "1) After creating REQUIREMENTS.md, TEST.md, and AGENT_TASKS.md, hand off to the Designer via transfer_to_designer_agent.\n"
            "2) Wait for /design/design_spec.md before proceeding.\n"
            "3) When design_spec.md exists, hand off to Frontend and Backend Developers providing the relevant documents.\n"
            "4) Await /frontend/index.html and /backend/server.js before involving the Tester.\n"
            "5) Finally, hand off to the Tester with transfer_to_tester_agent once prior artefacts exist.\n"
            "6) Do not advance if required files are missing; request fixes and re-check.\n"
            "Do NOT respond with status updates; continue orchestrating until completion."
        ),
        model="gpt-5",
        mcp_servers=(server,),
        handoffs=("Designer", "Frontend Developer", "Backend Developer", "Tester"),
        deliverables=("REQUIREMENTS.md", "TEST.md", "AGENT_TASKS.md"),
    )

    handoffs = (
        HandoffRule(
            source="Project Manager",
            target="Designer",
            required_artifacts=("REQUIREMENTS.md", "TEST.md", "AGENT_TASKS.md"),
        ),
        HandoffRule(
            source="Designer",
            target="Project Manager",
            required_artifacts=("design/design_spec.md",),
        ),
        HandoffRule(
            source="Project Manager",
            target="Frontend Developer",
            required_artifacts=("design/design_spec.md", "REQUIREMENTS.md", "AGENT_TASKS.md"),
        ),
        HandoffRule(
            source="Project Manager",
            target="Backend Developer",
            required_artifacts=("REQUIREMENTS.md", "AGENT_TASKS.md"),
        ),
        HandoffRule(
            source="Frontend Developer",
            target="Project Manager",
            required_artifacts=("frontend/index.html", "frontend/styles.css", "frontend/game.js"),
        ),
        HandoffRule(
            source="Backend Developer",
            target="Project Manager",
            required_artifacts=("backend/server.js", "backend/package.json"),
        ),
        HandoffRule(
            source="Project Manager",
            target="Tester",
            required_artifacts=(
                "design/design_spec.md",
                "frontend/index.html",
                "backend/server.js",
            ),
        ),
        HandoffRule(
            source="Tester",
            target="Project Manager",
            required_artifacts=("tests/TEST_PLAN.md",),
        ),
    )

    if task_list is None:
        task_list = (
            "Goal: Build a tiny browser game to showcase a multi-agent workflow.\n\n"
            "High-level requirements:\n"
            "- Single-screen game called \"Bug Busters\".\n"
            "- Player clicks a moving bug to earn points.\n"
            "- Game ends after 20 seconds and shows final score.\n"
            "- Optional: submit score to a simple backend and display a top-10 leaderboard.\n\n"
            "Roles:\n"
            "- Designer: create a one-page UI/UX spec and basic wireframe.\n"
            "- Frontend Developer: implement the page and game logic.\n"
            "- Backend Developer: implement a minimal API (GET /health, GET/POST /scores).\n"
            "- Tester: write a quick test plan and a simple script to verify core routes.\n\n"
            "Constraints:\n"
            "- No external database—memory storage is fine.\n"
            "- Keep everything readable for beginners; no frameworks required.\n"
            "- All outputs should be small files saved in clearly named folders.\n"
        )

    return MultiAgentWorkflow(
        server=server,
        project_manager=project_manager,
        designer=designer,
        frontend_developer=frontend_developer,
        backend_developer=backend_developer,
        tester=tester,
        handoffs=handoffs,
        task_list_template=task_list,
    )
