"""Builders declarativos para flujos Codex MCP multi-LLM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class _ProviderMetadata:
    default_model: str
    env_vars: List[Dict[str, object]]
    label: str


class CodexMCPWorkflowBuilder:
    """Genera briefs reutilizables para flujos MCP de Codex.

    El builder produce estructuras puramente declarativas que describen
    cómo inicializar el servidor MCP, qué agentes participan y qué
    artefactos deben existir antes de cada handoff. No realiza llamadas a
    redes externas ni ejecuta `openai-agents`; simplemente estructura los
    datos que un orquestador podría consumir.
    """

    _SUPPORTED_PROVIDERS: Dict[str, _ProviderMetadata] = {
        "openai": _ProviderMetadata(
            default_model="gpt-4.1",
            env_vars=[{"name": "OPENAI_API_KEY", "required": True}],
            label="ChatGPT",
        ),
        "anthropic": _ProviderMetadata(
            default_model="claude-3-5-sonnet-20241022",
            env_vars=[{"name": "ANTHROPIC_API_KEY", "required": True}],
            label="Claude",
        ),
        "huggingface": _ProviderMetadata(
            default_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            env_vars=[{"name": "HUGGINGFACEHUB_API_TOKEN", "required": False}],
            label="Hugging Face",
        ),
    }

    def __init__(
        self,
        provider: str,
        *,
        model: Optional[str] = None,
        server_command: str = "npx",
        server_args: Optional[List[str]] = None,
        timeout_seconds: int = 360000,
    ) -> None:
        provider_key = provider.lower()
        if provider_key not in self._SUPPORTED_PROVIDERS:
            raise ValueError(f"Proveedor no soportado: {provider}")

        metadata = self._SUPPORTED_PROVIDERS[provider_key]

        self.provider = provider_key
        self.model = model or metadata.default_model
        self._metadata = metadata
        self._command = server_command
        self._args = server_args or ["-y", "codex", "mcp"]
        self._timeout = timeout_seconds

    # ------------------------------------------------------------------
    # Información base
    def required_environment(self) -> List[Dict[str, object]]:
        """Devuelve la lista de variables de entorno esperadas."""

        return list(self._metadata.env_vars)

    def server_config(self) -> Dict[str, object]:
        """Configura cómo levantar el servidor MCP."""

        return {
            "command": self._command,
            "args": list(self._args),
            "client_session_timeout_seconds": self._timeout,
        }

    # ------------------------------------------------------------------
    # Brief single-agent
    def build_single_agent_brief(self) -> Dict[str, object]:
        """Genera el brief single-agent descrito en la guía del usuario."""

        designer_instructions = (
            "You are an indie game connoisseur. Produce a three sentence design "
            "brief for a simple browser game that fits within about fifty lines "
            "of HTML, CSS, and JavaScript. When ready, call the Game Developer "
            "agent with your idea."
        )

        developer_instructions = (
            "You are an expert in building single page games using plain HTML, CSS, "
            "and JavaScript. Save the implementation to index.html in the working "
            "directory. Always call codex with \"approval-policy\": \"never\" "
            "and \"sandbox\": \"workspace-write\" so the MCP run can write files "
            "directly."
        )

        return {
            "provider": self.provider,
            "model": self.model,
            "provider_label": self._metadata.label,
            "required_env": self.required_environment(),
            "server": self.server_config(),
            "agents": {
                "designer": {
                    "name": "Game Designer",
                    "instructions": designer_instructions,
                    "handoffs": ["developer"],
                    "model": self.model,
                },
                "developer": {
                    "name": "Game Developer",
                    "instructions": developer_instructions,
                    "mcp_policy": {
                        "approval-policy": "never",
                        "sandbox": "workspace-write",
                    },
                },
            },
            "runner": {
                "entry_agent": "designer",
                "task": "Implement a fun new game!",
            },
        }

    # ------------------------------------------------------------------
    # Brief multi-agent
    def build_multi_agent_brief(self) -> Dict[str, object]:
        """Genera un brief multi-agente con gating y observabilidad."""

        base_env = self.required_environment()

        agents = {
            "designer": {
                "name": "Designer",
                "instructions": self._designer_spec(),
                "handoffs": ["project_manager"],
                "tools": ["web-search"],
            },
            "frontend_developer": {
                "name": "Frontend Developer",
                "instructions": self._frontend_spec(),
                "handoffs": ["project_manager"],
            },
            "backend_developer": {
                "name": "Backend Developer",
                "instructions": self._backend_spec(),
                "handoffs": ["project_manager"],
            },
            "tester": {
                "name": "Tester",
                "instructions": self._tester_spec(),
                "handoffs": ["project_manager"],
            },
            "project_manager": {
                "name": "Project Manager",
                "instructions": self._project_manager_spec(),
                "handoffs": [
                    "designer",
                    "frontend_developer",
                    "backend_developer",
                    "tester",
                ],
            },
        }

        gate_checks = [
            {"agent": "designer", "artifact": "design/design_spec.md"},
            {"agent": "frontend_developer", "artifact": "frontend/index.html"},
            {"agent": "backend_developer", "artifact": "backend/server.js"},
            {"agent": "tester", "artifact": "tests/TEST_PLAN.md"},
        ]

        return {
            "provider": self.provider,
            "model": self.model,
            "required_env": base_env,
            "server": self.server_config(),
            "agents": agents,
            "workflow": {
                "entry_agent": "project_manager",
                "gate_checks": gate_checks,
                "task": self._default_task_list(),
            },
            "tracing": {
                "enabled": True,
                "notes": (
                    "Enable OpenAI Traces (or Anthropic/Hugging Face equivalents) to "
                    "inspect prompts, tool calls, and MCP transcripts for the team."
                ),
            },
        }

    # ------------------------------------------------------------------
    # Private helpers
    def _designer_spec(self) -> str:
        return (
            "You are the Designer. Use AGENT_TASKS.md and REQUIREMENTS.md from the "
            "Project Manager as your only source of truth. Deliver design_spec.md "
            "and wireframe.md inside the /design directory. When complete, transfer "
            "control back to the Project Manager with transfer_to_project_manager."
            "When writing files call Codex MCP with {\"approval-policy\":\"never\","
            "\"sandbox\":\"workspace-write\"}."
        )

    def _frontend_spec(self) -> str:
        return (
            "You are the Frontend Developer. Implement the DOM structure described "
            "by design_spec.md. Save artifacts to /frontend (index.html, styles.css, "
            "game.js). Use Codex MCP file writes with {\"approval-policy\":\"never\", "
            "\"sandbox\":\"workspace-write\"}. Return work to the Project Manager."
        )

    def _backend_spec(self) -> str:
        return (
            "You are the Backend Developer. Implement the endpoints listed in "
            "AGENT_TASKS.md and REQUIREMENTS.md using Node.js without external "
            "databases. Save package.json and server.js inside /backend. Use the "
            "same MCP write policy and hand off to the Project Manager when done."
        )

    def _tester_spec(self) -> str:
        return (
            "You are the Tester. Build TEST_PLAN.md inside /tests and add an "
            "optional automation script if requested. Validate outputs against the "
            "acceptance criteria recorded in TEST.md. Use the MCP write policy and "
            "handoff to the Project Manager once checks are complete."
        )

    def _project_manager_spec(self) -> str:
        return (
            "You are the Project Manager. Create REQUIREMENTS.md, TEST.md, and "
            "AGENT_TASKS.md in the repository root using Codex MCP with {\"approval-"
            "policy\":\"never\",\"sandbox\":\"workspace-write\"}. Once the files exist, "
            "handoff to the Designer via transfer_to_designer_agent. Confirm the "
            "Designer produced design/design_spec.md before contacting the Frontend "
            "and Backend Developers (transfer_to_frontend_developer_agent and "
            "transfer_to_backend_developer_agent). Wait until frontend/index.html "
            "and backend/server.js exist before transferring to the Tester via "
            "transfer_to_tester_agent. Do not advance unless the required artifacts "
            "are present; request rework otherwise."
        )

    def _default_task_list(self) -> str:
        return (
            "Goal: Build a tiny browser game to showcase a multi-agent workflow.\n\n"
            "High-level requirements:\n"
            "- Single-screen game called \"Bug Busters\".\n"
            "- Player clicks a moving bug to earn points.\n"
            "- Game ends after 20 seconds and shows final score.\n"
            "- Optional backend to store top-10 scores.\n\n"
            "Roles:\n"
            "- Designer: produce UI/UX spec and wireframe.\n"
            "- Frontend Developer: implement UI and client logic.\n"
            "- Backend Developer: implement GET /health and GET/POST /scores.\n"
            "- Tester: prepare acceptance checklist and optional script.\n\n"
            "Constraints:\n"
            "- No external database; in-memory storage is acceptable.\n"
            "- Keep artefacts readable and framework-free.\n"
            "- Outputs must be saved in the directories referenced above."
        )

