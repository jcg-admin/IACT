"""Documentation coverage for validation and pipeline instructions."""

from __future__ import annotations

from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2] / "workspace"
README_PATH = WORKSPACE_ROOT / "README.md"


def test_workspace_readme_describes_validation_commands_and_pipeline() -> None:
    if not README_PATH.exists():
        raise AssertionError(f"Expected {README_PATH} to exist")

    readme_content = README_PATH.read_text(encoding="utf-8")

    assert "## Validación del agente" in readme_content
    assert "pytest infrastructure/workspace/tests -v --cov" in readme_content
    assert "npm test" in readme_content
    assert "## Pipeline CI/CD" in readme_content
    assert ".github/workflows/infrastructure-ci.yml" in readme_content


def test_workspace_readme_clarifies_mise_is_optional() -> None:
    if not README_PATH.exists():
        raise AssertionError(f"Expected {README_PATH} to exist")

    readme_content = README_PATH.read_text(encoding="utf-8")

    assert "mise ~/.config/mise/config.toml tools" in readme_content
    assert "no es necesario" in readme_content.lower()


def test_workspace_readme_explains_how_to_run_the_agent_without_manage_py() -> None:
    if not README_PATH.exists():
        raise AssertionError(f"Expected {README_PATH} to exist")

    readme_content = README_PATH.read_text(encoding="utf-8")

    assert "## Ejecución del agente" in readme_content
    assert "python -m infrastructure.workspace.vpn_proxy_agent.mcp_server" in readme_content
    assert "npm run vpn:setup-dev" in readme_content
    assert "manage.py" in readme_content
    assert "no aplica" in readme_content.lower()
