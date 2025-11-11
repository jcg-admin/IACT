"""Utilities to reason about the CPython toolchain recovery plan."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence


_TASK_PATTERN = re.compile(r"^###\s+Tarea\s+(?P<number>\d+)\.\s*(?P<title>.+)$")
_SUBTASK_PATTERN = re.compile(r"^\s*(?P<identifier>\d+\.\d+)\s+(?P<summary>.+)$")


@dataclass
class RecoverySubTask:
    """Represents an actionable step inside a recovery plan task."""

    identifier: str
    summary: str
    details: List[str] = field(default_factory=list)


@dataclass
class RecoveryTask:
    """Represents a high-level task inside the recovery plan."""

    number: str
    title: str
    subtasks: List[RecoverySubTask] = field(default_factory=list)


def parse_recovery_plan(path: Path | str) -> List[RecoveryTask]:
    """Parse the recovery plan markdown document into structured tasks."""

    plan_path = Path(path)
    text = plan_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    tasks: List[RecoveryTask] = []
    current_task: RecoveryTask | None = None
    current_subtask: RecoverySubTask | None = None
    capture_code_block = False

    for line in lines:
        task_match = _TASK_PATTERN.match(line)
        if task_match:
            current_task = RecoveryTask(
                number=task_match.group("number"),
                title=task_match.group("title").strip(),
            )
            tasks.append(current_task)
            current_subtask = None
            capture_code_block = False
            continue

        if current_task is None:
            continue

        stripped = line.strip()
        if stripped.startswith("```"):
            if capture_code_block:
                capture_code_block = False
            else:
                capture_code_block = True
            continue

        if capture_code_block and current_subtask is not None:
            if stripped:
                current_subtask.details.append(stripped)
            continue

        subtask_match = _SUBTASK_PATTERN.match(line)
        if subtask_match:
            current_subtask = RecoverySubTask(
                identifier=subtask_match.group("identifier"),
                summary=subtask_match.group("summary").strip(),
            )
            current_task.subtasks.append(current_subtask)
            capture_code_block = False
            continue

        if current_subtask is not None and stripped:
            # Continuation lines belong to the current subtask summary.
            current_subtask.summary = f"{current_subtask.summary} {stripped}".strip()

    return tasks


def format_tasks(tasks: Sequence[RecoveryTask]) -> str:
    """Render a sequence of tasks into a human-readable string."""

    lines: List[str] = []
    for task in tasks:
        lines.append(f"Tarea {task.number}: {task.title}")
        for subtask in task.subtasks:
            lines.append(f"  - {subtask.identifier} {subtask.summary}")
            for detail in subtask.details:
                lines.append(f"    {detail}")
        lines.append("")

    return "\n".join(lines).strip()


def generate_auto_cot_outline(tasks: Sequence[RecoveryTask]) -> List[dict[str, object]]:
    """Build a structured Auto-CoT outline from recovery plan tasks."""

    outline: List[dict[str, object]] = []
    for task in tasks:
        thought_chain: List[dict[str, object]] = []
        for subtask in task.subtasks:
            statement = _normalise_statement(subtask.summary)
            actions = _derive_actions(subtask)
            thought_chain.append(
                {
                    "step_id": subtask.identifier,
                    "statement": statement,
                    "actions": actions,
                }
            )

        outline.append(
            {
                "task_id": task.number,
                "title": task.title,
                "thought_chain": thought_chain,
            }
        )

    return outline


def evaluate_self_consistency(tasks: Sequence[RecoveryTask]) -> dict[str, object]:
    """Validate numbering and structure consistency across parsed tasks."""

    issues: List[str] = []
    seen_task_numbers: set[str] = set()
    for index, task in enumerate(tasks, start=1):
        if task.number in seen_task_numbers:
            issues.append(f"Tarea {task.number} aparece duplicada")
        seen_task_numbers.add(task.number)

        if task.number != str(index):
            issues.append(
                f"Tarea {task.number} está fuera de orden: se esperaba {index}"
            )

        if not task.subtasks:
            issues.append(f"Tarea {task.number} no contiene subtareas")

        seen_subtasks: set[str] = set()
        for sub_index, subtask in enumerate(task.subtasks, start=1):
            if subtask.identifier in seen_subtasks:
                issues.append(
                    f"Subtarea {subtask.identifier} duplicada en tarea {task.number}"
                )
            seen_subtasks.add(subtask.identifier)

            prefix = f"{task.number}."
            if not subtask.identifier.startswith(prefix):
                issues.append(
                    f"Subtarea {subtask.identifier} no corresponde a tarea {task.number}"
                )
                continue

            try:
                sub_number = int(subtask.identifier.split(".", 1)[1])
            except ValueError:
                issues.append(
                    f"Subtarea {subtask.identifier} contiene un índice inválido"
                )
                continue

            if sub_number != sub_index:
                issues.append(
                    "Subtarea {identifier} fuera de orden: se esperaba {expected}".format(
                        identifier=subtask.identifier,
                        expected=f"{task.number}.{sub_index}",
                    )
                )

            if subtask.details and any(not detail.strip() for detail in subtask.details):
                issues.append(
                    f"Subtarea {subtask.identifier} contiene detalles vacíos"
                )

    return {"is_consistent": not issues, "issues": issues}


def _normalise_statement(summary: str) -> str:
    """Normalise a subtask summary to serve as a reasoning statement."""

    statement = summary.replace("`", "").strip()
    if statement.endswith("."):
        statement = statement[:-1]
    return statement


def _derive_actions(subtask: RecoverySubTask) -> List[str]:
    """Infer actionable steps from a subtask."""

    actions: List[str] = []
    if subtask.details:
        actions.extend(detail.strip() for detail in subtask.details if detail.strip())
        return actions

    summary = subtask.summary
    raw_snippets = [snippet.strip() for snippet in re.findall(r"`([^`]+)`", summary)]
    command_snippets = [snippet for snippet in raw_snippets if " " in snippet]
    actions.extend(command_snippets)

    plain_summary = summary.replace("`", "")
    segments = [
        seg.strip(" .")
        for seg in re.split(r"\s+y\s+", plain_summary)
        if seg.strip(" .")
    ]

    for segment in segments:
        cleaned = segment
        lower_cleaned = (
            cleaned[0].lower() + cleaned[1:]
            if len(cleaned) > 1
            else cleaned.lower()
        )
        if lower_cleaned.lower().startswith("ejecutar") and command_snippets:
            # The executable action is already captured by the command reference.
            continue
        if lower_cleaned:
            actions.append(lower_cleaned)

    # Ensure uniqueness while preserving order.
    return _deduplicate(actions)


def _deduplicate(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


__all__ = [
    "RecoveryTask",
    "RecoverySubTask",
    "parse_recovery_plan",
    "format_tasks",
    "generate_auto_cot_outline",
    "evaluate_self_consistency",
]
