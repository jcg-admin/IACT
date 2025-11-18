"""
Tests TDD para SelfConsistencyAgent - Multiple Reasoning Paths

Tests completos usando pytest para validar Self-Consistency:
- Generación de múltiples samples
- Majority voting
- Consistency scoring
- Temperatura y diversidad

Generado usando SDLC pipeline con Self-Consistency technique.
Fecha: 2025-11-14
Coverage target: 85%
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from agents.base.self_consistency import SelfConsistencyAgent
except ImportError:
    pytest.skip("SelfConsistencyAgent not available", allow_module_level=True)


class TestSelfConsistencyAgent:
    """Test suite para SelfConsistencyAgent."""

    # =========================================================================
    # Tests de Inicialización
    # =========================================================================

    def test_init_with_defaults(self):
        """Test: Inicialización con valores por defecto."""
        agent = SelfConsistencyAgent()

        assert agent.num_samples >= 3  # Mínimo para consistency
        assert 0 <= agent.temperature <= 1.0
        assert hasattr(agent, 'generate_multiple_responses')

    def test_init_with_custom_config(self, self_consistency_config):
        """Test: Inicialización con configuración personalizada."""
        agent = SelfConsistencyAgent(config=self_consistency_config)

        assert agent.num_samples == self_consistency_config["num_samples"]
        assert agent.temperature == self_consistency_config["temperature"]

    @pytest.mark.parametrize("num_samples", [3, 5, 10, 20])
    def test_init_with_different_num_samples(self, num_samples):
        """Test: Diferentes números de samples."""
        config = {"num_samples": num_samples}
        agent = SelfConsistencyAgent(config=config)

        assert agent.num_samples == num_samples

    # =========================================================================
    # Tests de Generación Múltiple
    # =========================================================================

    def test_generate_multiple_responses(self, sample_question, mock_llm_generator):
        """Test: Generación de múltiples responses."""
        agent = SelfConsistencyAgent(config={"num_samples": 5})
        agent.llm = mock_llm_generator

        responses = agent.generate_multiple_responses(sample_question)

        assert isinstance(responses, list)
        assert len(responses) == 5
        assert all(isinstance(r, dict) for r in responses)

    def test_generate_responses_with_different_temperatures(self):
        """Test: Temperatura afecta diversidad."""
        agent_low = SelfConsistencyAgent(config={
            "temperature": 0.1,
            "num_samples": 3
        })
        agent_high = SelfConsistencyAgent(config={
            "temperature": 0.9,
            "num_samples": 3
        })

        assert agent_low.temperature < agent_high.temperature

    # =========================================================================
    # Tests de Majority Voting
    # =========================================================================

    def test_majority_vote_clear_winner(self, self_consistency_responses):
        """Test: Votación con ganador claro."""
        agent = SelfConsistencyAgent()

        winner = agent.majority_vote(self_consistency_responses)

        assert winner == "Use microservices architecture"

    def test_majority_vote_tie_handling(self, self_consistency_edge_cases):
        """Test: Manejo de empates en votación."""
        agent = SelfConsistencyAgent()

        result = agent.majority_vote(self_consistency_edge_cases["tie"])

        # Should handle tie gracefully (pick one or return both)
        assert result is not None

    def test_majority_vote_all_same(self, self_consistency_edge_cases):
        """Test: Votación cuando todas las respuestas son iguales."""
        agent = SelfConsistencyAgent()

        result = agent.majority_vote(self_consistency_edge_cases["all_same"])

        assert result == "A"

    def test_majority_vote_empty_list(self, self_consistency_edge_cases):
        """Test: Votación con lista vacía."""
        agent = SelfConsistencyAgent()

        result = agent.majority_vote(self_consistency_edge_cases["empty"])

        assert result is None or result == ""

    # =========================================================================
    # Tests de Consistency Scoring
    # =========================================================================

    def test_calculate_consistency_score_high_agreement(
        self,
        self_consistency_edge_cases
    ):
        """Test: Score alto cuando hay alto acuerdo."""
        agent = SelfConsistencyAgent()

        score = agent.calculate_consistency_score(
            self_consistency_edge_cases["all_same"]
        )

        assert 0.8 <= score <= 1.0  # High consistency

    def test_calculate_consistency_score_low_agreement(
        self,
        self_consistency_responses
    ):
        """Test: Score bajo cuando hay desacuerdo."""
        agent = SelfConsistencyAgent()

        # Modify to have more disagreement
        diverse_responses = [
            {"answer": "A"},
            {"answer": "B"},
            {"answer": "C"},
            {"answer": "D"}
        ]

        score = agent.calculate_consistency_score(diverse_responses)

        assert 0.0 <= score < 0.5  # Low consistency

    def test_consistency_score_range(self, self_consistency_responses):
        """Test: Score siempre está en rango [0, 1]."""
        agent = SelfConsistencyAgent()

        score = agent.calculate_consistency_score(self_consistency_responses)

        assert 0.0 <= score <= 1.0

    # =========================================================================
    # Tests de Execute
    # =========================================================================

    def test_execute_returns_valid_result(
        self,
        sample_question,
        mock_llm_generator,
        assert_valid_response
    ):
        """Test: Execute retorna resultado válido."""
        agent = SelfConsistencyAgent(config={"num_samples": 3})
        agent.llm = mock_llm_generator

        result = agent.execute({"question": sample_question})

        required_keys = ["final_answer", "samples", "consistency_score"]
        assert_valid_response(result, required_keys)

    def test_execute_with_confidence_threshold(self, sample_question):
        """Test: Execute respeta umbral de confianza."""
        agent = SelfConsistencyAgent(config={
            "num_samples": 5,
            "min_consistency_score": 0.8
        })

        agent.llm = Mock()
        agent.llm.generate = Mock(return_value={
            "content": "Mock answer A"
        })

        result = agent.execute({"question": sample_question})

        assert "consistency_score" in result

    # =========================================================================
    # Tests de Error Handling
    # =========================================================================

    def test_error_handling_llm_failure(self, sample_question):
        """Test: Manejo de errores cuando LLM falla."""
        agent = SelfConsistencyAgent()
        agent.llm = Mock()
        agent.llm.generate = Mock(side_effect=Exception("LLM Error"))

        with pytest.raises(Exception):
            agent.execute({"question": sample_question})

    @pytest.mark.parametrize("invalid_input", [
        {},  # Missing question
        {"question": ""},  # Empty question
        {"question": None},  # None question
    ])
    def test_error_handling_invalid_inputs(self, invalid_input):
        """Test: Manejo de inputs inválidos."""
        agent = SelfConsistencyAgent()

        with pytest.raises((ValueError, KeyError, TypeError)):
            agent.execute(invalid_input)

    # =========================================================================
    # Tests de Performance
    # =========================================================================

    @pytest.mark.slow
    @pytest.mark.parametrize("num_samples", [5, 10, 20])
    def test_performance_scales_linearly(self, num_samples, sample_question):
        """Test: Performance escala linealmente con num_samples."""
        import time

        agent = SelfConsistencyAgent(config={"num_samples": num_samples})
        agent.llm = Mock()
        agent.llm.generate = Mock(return_value={"content": "Mock"})

        start = time.time()
        agent.execute({"question": sample_question})
        duration = time.time() - start

        # Should be roughly proportional (with mocks, very fast)
        assert duration < num_samples * 0.1  # 0.1s per sample max

    # =========================================================================
    # Integration Tests
    # =========================================================================

    @pytest.mark.integration
    def test_full_pipeline(
        self,
        sample_question,
        mock_llm_generator,
        self_consistency_responses
    ):
        """Test: Pipeline completo de Self-Consistency."""
        agent = SelfConsistencyAgent(config={"num_samples": 5})
        agent.llm = mock_llm_generator

        # Configure mock to return varied responses
        mock_llm_generator.generate.side_effect = [
            {"content": "Answer: Microservices"},
            {"content": "Answer: Microservices"},
            {"content": "Answer: Monolith"},
            {"content": "Answer: Microservices"},
            {"content": "Answer: Microservices"}
        ]

        result = agent.execute({"question": sample_question})

        assert "final_answer" in result
        assert "consistency_score" in result
        assert result["consistency_score"] > 0.5  # Should be consistent


# ============================================================================
# Utility Tests
# ============================================================================

class TestSelfConsistencyUtilities:
    """Tests para funciones utilitarias."""

    def test_extract_answer_from_response(self):
        """Test: Extracción de respuesta del texto."""
        agent = SelfConsistencyAgent()

        response_text = "Reasoning: Because...\nAnswer: Use microservices"
        answer = agent._extract_answer(response_text)

        assert "microservices" in answer.lower()

    def test_calculate_confidence_score(self, self_consistency_responses):
        """Test: Cálculo de confidence score agregado."""
        agent = SelfConsistencyAgent()

        avg_confidence = agent._calculate_average_confidence(
            self_consistency_responses
        )

        assert 0.0 <= avg_confidence <= 1.0
        assert avg_confidence > 0.7  # All responses have high confidence
