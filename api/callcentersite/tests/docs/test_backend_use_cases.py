import pytest
from pathlib import Path

from callcentersite.docs_backend_use_cases import (
    list_use_case_files,
    parse_use_case,
)


BACKEND_DOCS = Path(__file__).resolve().parents[4] / "docs" / "backend"


@pytest.mark.unit
def test_list_use_cases_returns_all_ids():
    use_cases = list_use_case_files(BACKEND_DOCS)
    ids = {uc.id for uc in use_cases}
    expected_ids = {
        "UC-PERM-001",
        "UC-PERM-002",
        "UC-PERM-003",
        "UC-PERM-004",
        "UC-PERM-005",
        "UC-PERM-006",
        "UC-PERM-007",
        "UC-PERM-008",
        "UC-PERM-010",
    }
    missing = expected_ids - ids
    unexpected = ids - expected_ids
    assert not missing, f"Missing use cases: {missing}"
    assert not unexpected, f"Unexpected use cases found: {unexpected}"


@pytest.mark.unit
def test_parse_use_case_extracts_main_flow_steps():
    uc_file = BACKEND_DOCS / "UC-PERM-001_asignar_grupo_a_usuario.md"
    use_case = parse_use_case(uc_file)

    assert use_case.id == "UC-PERM-001"
    assert "Asignar Grupo de Permisos a Usuario" in use_case.name
    main_steps = " ".join(use_case.main_flow.steps)
    assert "Navega al módulo de gestión de usuarios" in main_steps
    assert "Valida que el administrador tiene permiso" in main_steps
    assert "Registra asignación en auditoría" in main_steps


@pytest.mark.unit
def test_parse_use_case_collects_alternate_and_exception_flows():
    uc_file = BACKEND_DOCS / "UC-PERM-001_asignar_grupo_a_usuario.md"
    use_case = parse_use_case(uc_file)

    alt_titles = {flow.title for flow in use_case.alternate_flows}
    exc_titles = {flow.title for flow in use_case.exception_flows}

    assert {"FA-1", "FA-2", "FA-3"}.issubset(alt_titles)
    assert {"FE-1", "FE-2", "FE-3", "FE-4"}.issubset(exc_titles)

    alt_steps = " ".join(step for flow in use_case.alternate_flows for step in flow.steps)
    exc_steps = " ".join(step for flow in use_case.exception_flows for step in flow.steps)

    assert "Sistema detecta duplicado" in alt_steps
    assert "Sistema valida grupos" in exc_steps
    assert "Sistema detecta error de BD" in exc_steps


@pytest.mark.unit
@pytest.mark.parametrize(
    "filename, expected_phrases",
    [
        (
            "UC-PERM-002_revocar_grupo_a_usuario.md",
            [
                "Accede al módulo de gestión de usuarios",
                "Muestra confirmación de éxito",
            ],
        ),
        (
            "UC-PERM-003_conceder_permiso_excepcional.md",
            [
                "Accede a módulo de permisos excepcionales",
                "Crea registro en permisos_excepcionales",
            ],
        ),
    ],
)
def test_parse_use_case_supports_numbered_sections(filename, expected_phrases):
    uc_file = BACKEND_DOCS / filename
    use_case = parse_use_case(uc_file)

    main_steps_text = " ".join(use_case.main_flow.steps)

    for phrase in expected_phrases:
        assert phrase in main_steps_text, f"Phrase '{phrase}' missing in main flow"


@pytest.mark.unit
def test_numbered_sections_keep_alternate_and_exception_flows():
    uc_file = BACKEND_DOCS / "UC-PERM-002_revocar_grupo_a_usuario.md"
    use_case = parse_use_case(uc_file)

    alt_titles = {flow.title for flow in use_case.alternate_flows}
    exc_titles = {flow.title for flow in use_case.exception_flows}

    assert {"FA-002.1", "FA-002.2", "FA-002.3"}.issubset(alt_titles)
    assert {"FE-002.1", "FE-002.2"}.issubset(exc_titles)

    alt_steps = " ".join(step for flow in use_case.alternate_flows for step in flow.steps)
    exc_steps = " ".join(step for flow in use_case.exception_flows for step in flow.steps)

    assert "Sistema muestra error" in alt_steps
    assert "HTTP 403 Forbidden" in exc_steps
