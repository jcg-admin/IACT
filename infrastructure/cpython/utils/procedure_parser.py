"""Parsers for procedural CPython documentation in the infrastructure space."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


_STEP_PATTERN = re.compile(r"^###\s+(?P<identifier>\d+\.\d+)\s+(?P<title>.+)$")
_SECTION_PATTERN = re.compile(r"^##\s+(?P<title>.+)$")
_CODE_LANG_COMMANDS = {"", "bash", "sh", "shell"}


@dataclass
class ProcedureStep:
    """Represents a concrete action described in the procedure."""

    identifier: str
    title: str
    notes: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)


@dataclass
class ChecklistSection:
    """Checklist grouped under a specific section of the document."""

    title: str
    items: List[str] = field(default_factory=list)


@dataclass
class ProcedureDocument:
    """Structured representation of a CPython procedural document."""

    metadata: Dict[str, object]
    steps: List[ProcedureStep]
    checklists: List[ChecklistSection]


def parse_procedure_document(path: Path | str) -> ProcedureDocument:
    """Parse a markdown procedure into metadata, steps, and checklists."""

    document_path = Path(path)
    lines = document_path.read_text(encoding="utf-8").splitlines()

    metadata, start_index = _parse_front_matter(lines)

    steps: List[ProcedureStep] = []
    checklists: List[ChecklistSection] = []
    checklist_map: Dict[str, ChecklistSection] = {}

    current_section: str | None = None
    current_step: ProcedureStep | None = None
    in_code_block = False
    code_block_language = ""
    code_lines: List[str] = []

    index = start_index
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_language = stripped[3:].strip().lower()
                code_lines = []
            else:
                in_code_block = False
                commands = _commands_from_code_block(code_lines, code_block_language)
                if commands and current_step is not None:
                    current_step.commands.extend(commands)
                code_block_language = ""
                code_lines = []
            index += 1
            continue

        if in_code_block:
            code_lines.append(line)
            index += 1
            continue

        section_match = _SECTION_PATTERN.match(line)
        if section_match:
            current_section = section_match.group("title").strip()
            checklist_section = checklist_map.get(current_section)
            if checklist_section is None:
                checklist_section = ChecklistSection(title=current_section)
                checklist_map[current_section] = checklist_section
                checklists.append(checklist_section)
            index += 1
            continue

        if stripped.startswith("- [ ]"):
            checklist_section = _ensure_checklist_section(
                checklist_map, checklists, current_section or "General"
            )
            checklist_section.items.append(stripped[5:].strip())
            index += 1
            continue

        step_match = _STEP_PATTERN.match(line)
        if step_match:
            current_step = ProcedureStep(
                identifier=step_match.group("identifier"),
                title=step_match.group("title").strip(),
            )
            steps.append(current_step)
            index += 1
            continue

        if current_step is not None and stripped and not stripped.startswith("**"):
            current_step.notes.append(stripped)

        index += 1

    return ProcedureDocument(metadata=metadata, steps=steps, checklists=checklists)


def _parse_front_matter(lines: Sequence[str]) -> Tuple[Dict[str, object], int]:
    """Extract metadata from the YAML front matter if present."""

    if not lines or lines[0].strip() != "---":
        return {}, 0

    metadata: Dict[str, object] = {}
    index = 1
    while index < len(lines) and lines[index].strip() != "---":
        line = lines[index].strip()
        if not line or line.startswith("#"):
            index += 1
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = _parse_front_matter_value(value.strip())
        index += 1

    # Skip closing --- if found.
    if index < len(lines) and lines[index].strip() == "---":
        index += 1

    return metadata, index


def _parse_front_matter_value(raw_value: str) -> object:
    """Parse a front matter value preserving simple types."""

    if not raw_value:
        return ""

    if raw_value[0] in {'"', "'"} and raw_value[-1] == raw_value[0]:
        return raw_value[1:-1]

    if raw_value.startswith("[") and raw_value.endswith("]"):
        try:
            return ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            return raw_value

    if raw_value.isdigit():
        return int(raw_value)

    return raw_value


def _commands_from_code_block(lines: Iterable[str], language: str) -> List[str]:
    """Extract executable commands from a code block."""

    if language not in _CODE_LANG_COMMANDS:
        return []

    commands: List[str] = []
    buffer = ""
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.endswith("\\"):
            part = stripped.rstrip("\\").strip()
            buffer = f"{buffer} {part}".strip() if buffer else part
            continue

        if buffer:
            combined = f"{buffer} {stripped}".strip()
            commands.append(combined)
            buffer = ""
        else:
            commands.append(stripped)

    if buffer:
        commands.append(buffer.strip())

    return commands


def _ensure_checklist_section(
    checklist_map: Dict[str, ChecklistSection],
    checklists: List[ChecklistSection],
    title: str,
) -> ChecklistSection:
    section = checklist_map.get(title)
    if section is None:
        section = ChecklistSection(title=title)
        checklist_map[title] = section
        checklists.append(section)
    return section


__all__ = [
    "ChecklistSection",
    "ProcedureDocument",
    "ProcedureStep",
    "parse_procedure_document",
]
