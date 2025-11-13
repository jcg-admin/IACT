"""Tests para el agente ETA-AGENTE CODEX que gobierna revisiones consolidadas."""

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _setup_repository(
    tmp_path: Path,
    *,
    include_agent_manifest: bool = True,
    link_revision_in_index: bool = True,
    create_legacy_revision: bool = False,
) -> Path:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    analysis = docs / "analisis"
    analysis.mkdir(parents=True, exist_ok=True)

    revision = analysis / "revision_20251112_consolidada.md"
    _write(revision, "# Revisión consolidada 2025-11-12\n")

    if include_agent_manifest:
        _write(analysis / "AGENTS.md", "# ETA-AGENTE CODEX\n")

    if link_revision_in_index:
        index_content = (
            "# Índice\n\n"
            "## [DOCS] Documentación activa\n\n"
            "- [Revisión consolidada](analisis/revision_20251112_consolidada.md)\n"
        )
    else:
        index_content = "# Índice\n\n## [DOCS] Documentación activa\n\n"
    _write(docs / "index.md", index_content)

    if create_legacy_revision:
        legacy = repo / "rev"
        legacy.mkdir(parents=True, exist_ok=True)
        _write(legacy / "revision_20251112_consolidada.md", "# Copia legado\n")

    return repo


class TestETACodexAgent:
    """Casos de validación estructural para el agente."""

    def test_validation_passes_when_structure_compliant(self, tmp_path):
        """Cuando la documentación cumple lineamientos, el agente aprueba la revisión."""
        repo = _setup_repository(tmp_path)

        from scripts.coding.ai.agents.documentation.eta_codex_agent import ETACodexAgent

        agent = ETACodexAgent(repo_root=repo)
        report = agent.validate()

        assert report.passed is True
        assert report.issues == []
        assert "docs/analisis/revision_20251112_consolidada.md" in report.checked_reviews

    def test_detects_revision_outside_docs_analisis(self, tmp_path):
        """El agente debe marcar las revisiones que permanecen en `rev/` como incumplimiento."""
        repo = _setup_repository(tmp_path, create_legacy_revision=True)

        from scripts.coding.ai.agents.documentation.eta_codex_agent import ETACodexAgent

        agent = ETACodexAgent(repo_root=repo)
        report = agent.validate()

        assert report.passed is False
        codes = {issue.code for issue in report.issues}
        assert "revision_outside_docs_analisis" in codes

    def test_detects_missing_agent_manifest(self, tmp_path):
        """Sin `AGENTS.md` específico, la gobernanza de revisiones debe fallar."""
        repo = _setup_repository(tmp_path, include_agent_manifest=False)

        from scripts.coding.ai.agents.documentation.eta_codex_agent import ETACodexAgent

        agent = ETACodexAgent(repo_root=repo)
        report = agent.validate()

        assert report.passed is False
        assert any(issue.code == "missing_agent_manifest" for issue in report.issues)

    def test_detects_index_without_revision_link(self, tmp_path):
        """El índice debe enlazar todas las revisiones consolidadas."""
        repo = _setup_repository(tmp_path, link_revision_in_index=False)

        from scripts.coding.ai.agents.documentation.eta_codex_agent import ETACodexAgent

        agent = ETACodexAgent(repo_root=repo)
        report = agent.validate()

        assert report.passed is False
        assert any(issue.code == "index_missing_revision_link" for issue in report.issues)
