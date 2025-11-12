"""Tests for the SDLC planner agent wiring."""

from pathlib import Path

import pytest


@pytest.fixture()
def planner_agent(tmp_path):
    """Create a planner agent instance with a temporary output directory."""
    from scripts.ai.sdlc.planner_agent import SDLCPlannerAgent

    config = {
        "project_root": str(Path.cwd()),
        "output_dir": str(tmp_path / "sdlc_outputs"),
    }

    return SDLCPlannerAgent(config=config)


def test_planner_agent_generates_issue(planner_agent):
    """Planner agent should return a structured issue payload."""
    result = planner_agent.execute(
        {
            "feature_request": "Documentar arquitectura unificada para frontend",
            "project_context": "",
            "backlog": [],
        }
    )

    assert result.is_success()
    data = result.data
    assert data["issue_title"].startswith("Documentar arquitectura")
    assert data["acceptance_criteria"]
    assert data["phase_result"].decision == "go"
