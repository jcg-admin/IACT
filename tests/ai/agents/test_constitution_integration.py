"""
Tests de integración de constitution con agentes AI.

Verifica que los agentes cargan correctamente la constitution y
validan sus outputs contra los principios establecidos.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

# Import del módulo a testear
try:
    from constitution_loader import (
        Constitution,
        ConstitutionValidator,
        load_constitution,
        create_validator
    )
    from base import Agent, AgentResult, AgentStatus
    CONSTITUTION_AVAILABLE = True
except ImportError:
    CONSTITUTION_AVAILABLE = False


# Marcar todos los tests para que se ejecuten solo si constitution está disponible
pytestmark = pytest.mark.skipif(
    not CONSTITUTION_AVAILABLE,
    reason="Constitution loader no disponible"
)


class TestConstitutionLoader:
    """Tests para Constitution y ConstitutionValidator."""

    def test_load_constitution(self):
        """Verifica que se puede cargar la constitution."""
        constitution = load_constitution()

        assert constitution is not None
        assert len(constitution.principles) > 0
        assert constitution.principles  # Tiene principios cargados

    def test_get_principle_by_number(self):
        """Verifica que se pueden obtener principios por número."""
        constitution = load_constitution()

        principle1 = constitution.get_principle(1)
        assert principle1 is not None
        assert "Calidad" in principle1.name or "Quality" in principle1.name

    def test_get_quality_principle(self):
        """Verifica método de conveniencia para principio de calidad."""
        constitution = load_constitution()

        quality_principle = constitution.get_quality_principle()
        assert quality_principle is not None
        assert quality_principle.number == 1

    def test_get_traceability_principle(self):
        """Verifica método de conveniencia para principio de trazabilidad."""
        constitution = load_constitution()

        traceability_principle = constitution.get_traceability_principle()
        assert traceability_principle is not None
        assert traceability_principle.number == 3


class TestConstitutionValidator:
    """Tests para validaciones de constitution."""

    @pytest.fixture
    def validator(self):
        """Fixture que proporciona un validator configurado."""
        constitution = load_constitution()
        return create_validator(constitution)

    def test_validate_no_emojis_clean_output(self, validator):
        """Verifica que output sin emojis pasa validación."""
        clean_output = {
            "code": "def test(): return True",
            "documentation": "This is clean documentation"
        }

        violations = validator.validate_no_emojis(clean_output)
        assert len(violations) == 0

    def test_validate_no_emojis_with_emojis(self, validator):
        """Verifica que output con emojis falla validación."""
        dirty_output = {
            "documentation": "Tests passed ✅"
        }

        violations = validator.validate_no_emojis(dirty_output)
        assert len(violations) > 0
        assert "emojis" in violations[0].lower()

    def test_validate_traceability_with_requirements(self, validator):
        """Verifica que output con trazabilidad pasa validación."""
        output_with_trace = {
            "documentation": "Implements REQ-AUTH-001 for user authentication",
            "spec": "See SPEC-AUTH-001 for details"
        }

        violations = validator.validate_traceability(output_with_trace)
        assert len(violations) == 0

    def test_validate_traceability_without_requirements(self, validator):
        """Verifica que output sin trazabilidad falla validación."""
        output_without_trace = {
            "documentation": "This is some code without any references"
        }

        violations = validator.validate_traceability(output_without_trace)
        assert len(violations) > 0
        assert "trazabilidad" in violations[0].lower()

    def test_validate_quality_no_placeholders(self, validator):
        """Verifica que output sin placeholders pasa validación."""
        complete_output = {
            "code": """
            def authenticate(user, password):
                '''Authenticates a user.'''
                return validate_credentials(user, password)
            """
        }

        violations = validator.validate_quality_over_speed(complete_output)
        # No debería contener violaciones de placeholders
        placeholder_violations = [v for v in violations if "placeholder" in v.lower()]
        assert len(placeholder_violations) == 0

    def test_validate_quality_with_placeholders(self, validator):
        """Verifica que output con placeholders falla validación."""
        incomplete_output = {
            "code": "def authenticate(): # TODO: implement this"
        }

        violations = validator.validate_quality_over_speed(incomplete_output)
        assert len(violations) > 0
        assert any("placeholder" in v.lower() for v in violations)

    def test_validate_authority_allowed_action(self, validator):
        """Verifica que acciones permitidas retornan True."""
        allowed_actions = [
            "generar_tests",
            "crear_documentacion",
            "formatear_codigo",
            "ejecutar_linters"
        ]

        for action in allowed_actions:
            has_authority = validator.validate_authority_limits(action, {})
            assert has_authority, f"Acción '{action}' debería estar permitida"

    def test_validate_authority_restricted_action(self, validator):
        """Verifica que acciones restringidas retornan False."""
        restricted_actions = [
            "modificar_arquitectura",
            "cambiar_esquema_bd",
            "modificar_api_publica",
            "merge_to_main"
        ]

        for action in restricted_actions:
            has_authority = validator.validate_authority_limits(action, {})
            assert not has_authority, f"Acción '{action}' debería requerir escalación"

    def test_validate_all_comprehensive(self, validator):
        """Verifica validación completa de todas las categorías."""
        output_data = {
            "code": """
            def process_data():
                '''Processes data according to REQ-PROC-001.'''
                return cleaned_data
            """,
            "tests": """
            def test_process_data():
                assert process_data() is not None
            """
        }

        all_violations = validator.validate_all(output_data)

        # Verificar que se ejecutan todas las categorías
        assert "quality" in all_violations
        assert "traceability" in all_violations
        assert "emojis" in all_violations
        assert "testing" in all_violations


class DummyAgent(Agent):
    """Agente dummy para testing de integración."""

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación dummy que retorna los datos de entrada."""
        return input_data


class TestAgentConstitutionIntegration:
    """Tests de integración entre Agent y Constitution."""

    def test_agent_loads_constitution(self):
        """Verifica que agente carga constitution automáticamente."""
        agent = DummyAgent("test-agent")

        assert agent.constitution is not None
        assert agent.constitution_validator is not None

    def test_agent_applies_constitution_guardrails(self):
        """Verifica que guardrails usan constitution validator."""
        agent = DummyAgent("test-agent")

        # Output con emojis debería fallar guardrails
        output_with_emojis = {
            "result": "Success ✅"
        }

        guardrail_errors = agent.apply_guardrails(output_with_emojis)
        assert len(guardrail_errors) > 0
        assert any("emoji" in error.lower() for error in guardrail_errors)

    def test_agent_check_authority_method(self):
        """Verifica que método check_authority funciona correctamente."""
        agent = DummyAgent("test-agent")

        # Acción permitida
        assert agent.check_authority("generar_tests") == True

        # Acción restringida
        assert agent.check_authority("modificar_arquitectura") == False

    def test_agent_execution_with_constitution_violations(self):
        """Verifica que agente bloquea ejecución si hay violaciones."""
        agent = DummyAgent("test-agent")

        # Input que generará output con emojis
        input_data = {
            "message": "Test passed ✅"
        }

        result = agent.execute(input_data)

        # El resultado debería estar bloqueado por guardrails
        assert result.status == AgentStatus.BLOCKED
        assert len(result.errors) > 0

    def test_agent_execution_with_valid_output(self):
        """Verifica que agente permite ejecución con output válido."""
        agent = DummyAgent("test-agent")

        # Input que genera output válido (con trazabilidad)
        input_data = {
            "code": "def test(): return True",
            "trace": "Implements REQ-TEST-001"
        }

        result = agent.execute(input_data)

        # El resultado debería ser exitoso
        assert result.status == AgentStatus.SUCCESS


# Tests marcados como critical para pre-push hook
@pytest.mark.critical
class TestConstitutionCritical:
    """Tests críticos de constitution que deben pasar antes de push."""

    def test_constitution_file_exists(self):
        """Verifica que archivo de constitution existe."""
        base_dir = Path(__file__).parent.parent.parent
        constitution_path = base_dir / "docs" / "gobernanza" / "agentes" / "constitution.md"

        assert constitution_path.exists(), "Constitution file debe existir"

    def test_constitution_loads_without_errors(self):
        """Verifica que constitution carga sin errores."""
        try:
            constitution = load_constitution()
            assert constitution is not None
            assert len(constitution.principles) >= 6  # Al menos 6 principios básicos
        except Exception as e:
            pytest.fail(f"Constitution debe cargar sin errores: {e}")

    def test_validator_creates_successfully(self):
        """Verifica que validator se crea sin errores."""
        try:
            validator = create_validator()
            assert validator is not None
        except Exception as e:
            pytest.fail(f"Validator debe crearse sin errores: {e}")


if __name__ == "__main__":
    # Ejecutar tests si se ejecuta directamente
    pytest.main([__file__, "-v"])
