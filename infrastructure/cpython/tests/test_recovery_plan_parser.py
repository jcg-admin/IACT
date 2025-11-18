import pathlib

import pytest


PLAN_PATH = pathlib.Path(__file__).resolve().parents[1] / "artifacts" / "CPython_toolchain_recovery_plan.md"


@pytest.fixture
def plan_path():
    return PLAN_PATH


def test_parse_recovery_plan_extracts_tasks_and_subtasks(plan_path):
    from infrastructure.cpython.utils.recovery_plan_parser import parse_recovery_plan

    tasks = parse_recovery_plan(plan_path)

    assert [task.number for task in tasks] == ["1", "2", "3"]
    assert tasks[0].title == "Restaurar conectividad APT"
    assert [sub.identifier for sub in tasks[0].subtasks] == ["1.1", "1.2", "1.3"]
    assert "ping archive.ubuntu.com" in tasks[0].subtasks[0].summary
    assert "proxy" in tasks[0].subtasks[2].summary


def test_parse_recovery_plan_includes_code_block_details(plan_path):
    from infrastructure.cpython.utils.recovery_plan_parser import parse_recovery_plan

    tasks = parse_recovery_plan(plan_path)
    task_two = tasks[1]
    subtask = next(sub for sub in task_two.subtasks if sub.identifier == "2.2")

    assert subtask.summary.startswith("Restablecer estados en frío")
    assert subtask.details == [
        "cd /vagrant",
        "source utils/state_manager.sh",
        "reset_operation_state bootstrap_complete",
        "reset_operation_state bootstrap_install_build_deps",
        "reset_operation_state bootstrap_install_tools",
    ]


def test_format_tasks_generates_human_readable_output(plan_path):
    from infrastructure.cpython.utils.recovery_plan_parser import parse_recovery_plan, format_tasks

    tasks = parse_recovery_plan(plan_path)
    rendered = format_tasks(tasks[:2])

    assert "Tarea 1: Restaurar conectividad APT" in rendered
    assert "  - 1.1" in rendered
    assert "Tarea 2: Limpiar y reprovisionar dependencias" in rendered
    assert "    cd /vagrant" in rendered


def test_generate_auto_cot_outline_creates_reasoned_steps(plan_path):
    from infrastructure.cpython.utils.recovery_plan_parser import (
        parse_recovery_plan,
        generate_auto_cot_outline,
    )

    tasks = parse_recovery_plan(plan_path)
    outline = generate_auto_cot_outline(tasks)

    assert outline[0]["task_id"] == "1"
    first_chain = outline[0]["thought_chain"]
    assert first_chain[0]["step_id"] == "1.1"
    assert "ping archive.ubuntu.com" in first_chain[0]["statement"]
    assert first_chain[1]["actions"] == ["sudo apt-get update", "capturar logs en /vagrant/logs/apt-update.log"]


def test_evaluate_self_consistency_reports_numbering_issues(plan_path):
    from infrastructure.cpython.utils.recovery_plan_parser import (
        parse_recovery_plan,
        evaluate_self_consistency,
    )

    tasks = parse_recovery_plan(plan_path)
    report = evaluate_self_consistency(tasks)

    assert report["is_consistent"] is True
    assert report["issues"] == []

    inconsistent_tasks = parse_recovery_plan(plan_path)
    inconsistent_tasks[0].subtasks[0].identifier = "2.5"
    report = evaluate_self_consistency(inconsistent_tasks)

    assert report["is_consistent"] is False
    assert any("2.5" in issue for issue in report["issues"])
