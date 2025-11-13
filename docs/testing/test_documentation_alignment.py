"""Tests de consistencia documental para proteger los ajustes de la revisión 2025-11-12."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_acknowledges_absence_of_root_makefile():
    readme = _read(REPO_ROOT / "README.md")
    assert "No existe un Makefile en la raíz" in readme
    assert "docs/operaciones/verificar_servicios.md" in readme
    assert "./scripts/verificar_servicios.sh" in readme
    assert "[IMPLEMENTADO]" in readme
    assert "make docs-serve" not in readme


def test_docs_index_and_stubs_are_canonical():
    index = _read(REPO_ROOT / "docs/index.md")
    assert "## [DOCS] Documentación activa" in index
    assert "## [LEGADO] Contenido legado" in index

    index_stub = _read(REPO_ROOT / "docs/INDEX.md")
    indice_stub = _read(REPO_ROOT / "docs/INDICE.md")
    expected = "Consulta el índice consolidado en [index.md](index.md)."
    assert expected in index_stub
    assert expected in indice_stub


def test_scripts_documentation_reflects_current_inventory():
    scripts_readme = _read(REPO_ROOT / "scripts/README.md")
    assert "Cualquier referencia anterior a `scripts/requisitos/`" in scripts_readme
    assert "validation/" in scripts_readme
    assert "validacion/" in scripts_readme

    docs_scripts = _read(REPO_ROOT / "docs/scripts/README.md")
    assert "No existen scripts como `scripts/sdlc_agent.py`" in docs_scripts
    assert "scripts/ci" in docs_scripts


def test_logs_and_analysis_documentation_are_updated():
    schema = _read(REPO_ROOT / "logs_data/SCHEMA.md")
    assert "Automatización parcial" in schema
    assert "scripts/dora_metrics.py" in schema

    analyzer = _read(REPO_ROOT / "scripts/analyze_backend.py")
    assert "logs_data/analysis/backend_analysis_results.json" in analyzer


def test_run_all_tests_targets_ui_directory():
    script = _read(REPO_ROOT / "scripts/run_all_tests.sh")
    assert "UI_DIR" in script
    assert "FRONTEND_DIR" not in script


def test_cpython_install_script_renamed():
    renamed_path = REPO_ROOT / "infrastructure/cpython/scripts/install_prebuilt_cpython.sh"
    assert renamed_path.exists()


def test_revision_20251112_lives_in_docs_analisis():
    revision_path = REPO_ROOT / "docs/analisis/revision_20251112_consolidada.md"
    assert revision_path.exists()

    index_contents = _read(REPO_ROOT / "docs/index.md")
    assert "analisis/revision_20251112_consolidada.md" in index_contents

    legacy_path = REPO_ROOT / "rev/revision_20251112_consolidada.md"
    assert not legacy_path.exists()


def test_docs_analisis_agent_guides_revision_location():
    agent_path = REPO_ROOT / "docs/analisis/AGENTS.md"
    assert agent_path.exists()

    agent_contents = _read(agent_path)
    assert "ETA-AGENTE CODEX" in agent_contents
    assert "colocar las revisiones consolidadas" in agent_contents


def test_eta_codex_agent_is_implemented_in_agents_tree():
    agent_module = REPO_ROOT / "scripts/coding/ai/agents/documentation/eta_codex_agent.py"
    assert agent_module.exists()

    tests_path = REPO_ROOT / "scripts/coding/tests/ai/agents/documentation/test_eta_codex_agent.py"
    assert tests_path.exists()


def test_phi3_prompt_engineering_playbook_is_published_and_linked():
    guide_path = REPO_ROOT / "docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md"
    assert guide_path.exists()

    readme = _read(REPO_ROOT / "README.md")
    assert "PHI3_PROMPT_ENGINEERING_PLAYBOOK.md" in readme

    prompting_index = _read(REPO_ROOT / "docs/ai_capabilities/prompting/README.md")
    assert "Phi-3" in prompting_index


def test_codex_mcp_multi_agent_guide_is_linked():
    guide_path = REPO_ROOT / "docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md"
    assert guide_path.exists()

    readme = _read(REPO_ROOT / "README.md")
    assert "CODEX_MCP_MULTI_AGENT_GUIDE.md" in readme

    prompting_index = _read(REPO_ROOT / "docs/ai_capabilities/prompting/README.md")
    assert "Codex MCP Multi-Agent Guide" in prompting_index

    agent_catalog = _read(REPO_ROOT / ".agent" / "agents" / "README.md")
    assert "CodexMCPWorkflow Orchestrator" in agent_catalog


def test_issue_templates_connect_execplans_and_agents():
    templates_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
    assert templates_dir.exists(), "La carpeta .github/ISSUE_TEMPLATE debe existir"

    feature_template = _read(templates_dir / "feature_request.md")
    assert "ExecPlan" in feature_template
    assert ".agent/PLANS.md" in feature_template

    custom_template = _read(templates_dir / "custom.md")
    assert ".agent/agents" in custom_template
    assert "Agente" in custom_template

    bug_template = _read(templates_dir / "bug_report.md")
    assert "SecurityAgent" in bug_template or "DependencyAgent" in bug_template


def test_ci_workflows_cover_quality_security_and_dependencies():
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    quality = workflows_dir / "code-quality.yml"
    codeql = workflows_dir / "codeql.yml"
    dependency = workflows_dir / "dependency-review.yml"

    assert quality.exists()
    assert codeql.exists()
    assert dependency.exists()

    quality_yaml = _read(quality)
    assert "./scripts/run_all_tests.sh" in quality_yaml
    assert "pytest" in quality_yaml

    codeql_yaml = _read(codeql)
    assert "github/codeql-action/init" in codeql_yaml

    dependency_yaml = _read(dependency)
    assert "dependency-review-action" in dependency_yaml


def test_readme_links_issue_templates_and_agents():
    readme = _read(REPO_ROOT / "README.md")
    assert "ISSUE_TEMPLATE" in readme
    assert ".agent/agents" in readme


def test_agent_catalog_links_to_docs_and_scripts():
    agent_readme = _read(REPO_ROOT / ".agent" / "README.md")
    assert "docs/ai/SDLC_AGENTS_GUIDE.md" in agent_readme
    assert "scripts/coding/ai/agents" in agent_readme
