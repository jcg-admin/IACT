"""ETA-AGENTE CODEX implementation for consolidated review governance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a governance violation detected by the agent."""

    code: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class ValidationReport:
    """Aggregated result for ETA-AGENTE CODEX validation."""

    passed: bool
    issues: List[ValidationIssue]
    checked_reviews: List[str]


class ETACodexAgent:
    """Agent that enforces consolidated review governance policies."""

    REVISION_GLOB = "revision_*_consolidada.md"

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root) if repo_root else self._discover_repo_root()

    def validate(self) -> ValidationReport:
        """Run all governance validations and return a consolidated report."""

        issues: List[ValidationIssue] = []
        checked_reviews: List[str] = []

        docs_analysis = self.repo_root / "docs" / "analisis"
        if not docs_analysis.exists():
            issues.append(
                ValidationIssue(
                    code="missing_docs_analisis_dir",
                    message="El directorio `docs/analisis/` no existe.",
                    recommendation="Crear `docs/analisis/` y mover allí las revisiones consolidadas.",
                )
            )
            return ValidationReport(passed=False, issues=issues, checked_reviews=checked_reviews)

        revision_files = sorted(docs_analysis.glob(self.REVISION_GLOB))
        checked_reviews.extend(
            str(path.relative_to(self.repo_root)) for path in revision_files
        )

        issues.extend(self._validate_agent_manifest(docs_analysis))
        issues.extend(self._validate_index_links(revision_files))
        issues.extend(self._detect_legacy_revisions())

        return ValidationReport(passed=not issues, issues=issues, checked_reviews=checked_reviews)

    # --- Internal helpers -------------------------------------------------

    def _discover_repo_root(self) -> Path:
        current = Path(__file__).resolve()
        for candidate in [current] + list(current.parents):
            if (candidate / ".git").exists():
                return candidate
        # Fallback to documentation tree parent
        return current.parents[5]

    def _validate_agent_manifest(self, docs_analysis: Path) -> Iterable[ValidationIssue]:
        manifest = docs_analysis / "AGENTS.md"
        if not manifest.exists():
            return [
                ValidationIssue(
                    code="missing_agent_manifest",
                    message="No se encontró `docs/analisis/AGENTS.md`.",
                    recommendation="Crear el manifiesto del ETA-AGENTE CODEX dentro de `docs/analisis/`.",
                )
            ]

        contents = manifest.read_text(encoding="utf-8")
        if "ETA-AGENTE CODEX" not in contents:
            return [
                ValidationIssue(
                    code="agent_manifest_missing_identifier",
                    message="El manifiesto de agentes no referencia a ETA-AGENTE CODEX.",
                    recommendation="Actualizar `docs/analisis/AGENTS.md` para incluir el identificador oficial.",
                )
            ]
        return []

    def _validate_index_links(self, revision_files: Iterable[Path]) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        revisions = list(revision_files)
        if not revisions:
            return issues

        index_path = self.repo_root / "docs" / "index.md"
        if not index_path.exists():
            issues.append(
                ValidationIssue(
                    code="missing_docs_index",
                    message="No existe `docs/index.md` para enlazar las revisiones consolidadas.",
                    recommendation="Crear `docs/index.md` y enlazar cada revisión consolidada desde `docs/analisis/`.",
                )
            )
            return issues

        index_text = index_path.read_text(encoding="utf-8")
        for revision in revisions:
            relative_link = f"analisis/{revision.name}"
            if relative_link not in index_text:
                issues.append(
                    ValidationIssue(
                        code="index_missing_revision_link",
                        message=(
                            "`docs/index.md` no referencia la revisión consolidada "
                            f"`{relative_link}`."
                        ),
                        recommendation=(
                            "Agregar un enlace en `docs/index.md` dentro de la sección de documentación activa "
                            "apuntando a la revisión consolidada."
                        ),
                    )
                )
        return issues

    def _detect_legacy_revisions(self) -> Iterable[ValidationIssue]:
        legacy_root = self.repo_root / "rev"
        if not legacy_root.exists():
            return []

        issues: List[ValidationIssue] = []
        for leftover in sorted(legacy_root.glob(self.REVISION_GLOB)):
            issues.append(
                ValidationIssue(
                    code="revision_outside_docs_analisis",
                    message=(
                        "Se detectó una revisión consolidada fuera de `docs/analisis/`: "
                        f"`{leftover.relative_to(self.repo_root)}`."
                    ),
                    recommendation=(
                        "Mover la revisión a `docs/analisis/` y eliminar la copia legacy bajo `rev/`."
                    ),
                )
            )
        return issues
