from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence
import re


@dataclass(frozen=True)
class Flow:
    """Represents a flow section within a use case."""

    title: str
    steps: List[str]


@dataclass(frozen=True)
class UseCase:
    """Structured representation of a backend use case document."""

    id: str
    name: str
    path: Path
    main_flow: Flow
    alternate_flows: List[Flow]
    exception_flows: List[Flow]


def list_use_case_files(base_dir: Path | None = None) -> List[UseCase]:
    """Return all documented use cases under ``docs/backend``.

    The function scans for Markdown files that start with ``UC-`` and parses
    each one into a :class:`UseCase` instance. The DORA directory is not
    traversed because only the backend documentation is considered.
    """

    docs_dir = base_dir or Path(__file__).resolve().parents[3] / "docs" / "backend"
    use_case_files = sorted(docs_dir.glob("UC-*.md"))
    return [parse_use_case(path) for path in use_case_files]


def parse_use_case(path: Path) -> UseCase:
    """Parse a use case Markdown file into a structured representation."""

    lines = path.read_text(encoding="utf-8").splitlines()
    use_case_id = _extract_metadata_field(lines, "id")
    name = _extract_metadata_field(lines, "nombre") or path.stem

    main_flow_lines = _slice_section(lines, "## Flujo principal")
    alternate_flow_lines = _slice_section(lines, "## Flujos alternos")
    exception_flow_lines = _slice_section(lines, "## Flujos de excepción")

    main_flow = Flow("Flujo principal", _extract_table_steps(main_flow_lines))
    alternate_flows = _extract_named_flows(alternate_flow_lines)
    exception_flows = _extract_named_flows(exception_flow_lines)

    return UseCase(
        id=use_case_id,
        name=name,
        path=path,
        main_flow=main_flow,
        alternate_flows=alternate_flows,
        exception_flows=exception_flows,
    )


def _extract_metadata_field(lines: Sequence[str], field: str) -> str:
    pattern = re.compile(rf"^{re.escape(field)}:\s*(.+)", re.IGNORECASE)
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip()
    return ""


def _slice_section(lines: Sequence[str], header: str) -> List[str]:
    header_lower = header.lower()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == header_lower:
            start = idx + 1
            break
    if start is None:
        return []

    section: List[str] = []
    for line in lines[start:]:
        if line.startswith("## ") and line.strip().lower() != header_lower:
            break
        section.append(line)
    return section


def _extract_table_steps(lines: Iterable[str]) -> List[str]:
    steps: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        columns = [col.strip() for col in line.strip("|").split("|")]
        if len(columns) < 2:
            continue
        actor, system = columns[0], columns[1]
        header_cells = {actor.lower(), system.lower()}
        if header_cells == {"actor", "sistema"}:
            continue
        if columns[0] and set(columns[0]) <= {"-"}:
            continue
        if columns[1] and set(columns[1]) <= {"-"}:
            continue
        if actor and system:
            steps.append(f"{actor}: {system}")
        else:
            steps.append(actor or system)
    return steps


def _extract_named_flows(lines: Sequence[str]) -> List[Flow]:
    flows: List[Flow] = []
    current_title = None
    current_lines: List[str] = []

    for line in lines:
        if line.startswith("## "):
            break
        if line.startswith("### "):
            if current_title is not None:
                flows.append(Flow(current_title, _extract_table_steps(current_lines)))
            current_title = _normalize_flow_title(line)
            current_lines = []
            continue
        current_lines.append(line)

    if current_title is not None:
        flows.append(Flow(current_title, _extract_table_steps(current_lines)))

    return flows


def _normalize_flow_title(raw_title: str) -> str:
    title = raw_title.lstrip("# ").strip()
    match = re.match(r"(?P<code>[A-Z]+-[0-9]+)", title)
    if match:
        return match.group("code")
    return title
