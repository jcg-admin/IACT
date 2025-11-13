import pathlib


PROCEDURE_PATH = (
    pathlib.Path(__file__).resolve().parents[3]
    / "docs"
    / "infrastructure"
    / "cpython_precompilado"
    / "FASE-3-PROCEDIMIENTO.md"
)


def test_parse_procedure_document_extracts_metadata_and_steps():
    from infrastructure.cpython.utils.procedure_parser import parse_procedure_document

    document = parse_procedure_document(PROCEDURE_PATH)

    assert document.metadata["id"] == "DOC-INFRA-CPYTHON-FASE3"

    first_step = document.steps[0]
    assert first_step.identifier == "1.1"
    assert first_step.title == "Verificar Sistema Host"


def test_parse_procedure_document_collapses_multiline_commands():
    from infrastructure.cpython.utils.procedure_parser import parse_procedure_document

    document = parse_procedure_document(PROCEDURE_PATH)

    step = next(item for item in document.steps if item.identifier == "2.2")

    assert any(
        command.startswith("gh release create cpython-3.12.6-build1")
        for command in step.commands
    )


def test_parse_procedure_document_collects_checklists():
    from infrastructure.cpython.utils.procedure_parser import parse_procedure_document

    document = parse_procedure_document(PROCEDURE_PATH)

    checklist_map = {section.title: section.items for section in document.checklists}

    assert "Pre-requisitos" in checklist_map
    assert (
        "Fases 0-2 completadas (infraestructura lista)"
        in checklist_map["Pre-requisitos"]
    )
