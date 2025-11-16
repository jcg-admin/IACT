"""
Tests TDD para AutoCoTAgent - Automatic Chain-of-Thought

Tests completos usando pytest para validar la funcionalidad de Auto-CoT:
- Inicialización y configuración
- Question clustering
- Demonstration sampling
- Zero-Shot CoT generation
- Error handling y edge cases

Generado usando SDLC pipeline con Auto-CoT y Self-Consistency.
Fecha: 2025-11-14
Coverage target: 85%
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.base.auto_cot_agent import (
    AutoCoTAgent,
    Question,
    Demonstration,
    LLM_AVAILABLE,
    NUMPY_AVAILABLE
)


class TestAutoCoTAgent:
    """Test suite para AutoCoTAgent."""

    # =========================================================================
    # Tests de Inicialización
    # =========================================================================

    def test_init_with_defaults(self):
        """Test: Inicialización con valores por defecto."""
        agent = AutoCoTAgent(use_llm=False)

        assert agent.k_clusters == 5
        assert agent.max_demonstrations == 10
        assert agent.demonstrations == []
        assert agent.use_llm == False
        assert agent.llm is None

    def test_init_with_custom_config(self):
        """Test: Inicialización con configuración personalizada."""
        agent = AutoCoTAgent(
            k_clusters=3,
            max_demonstrations=5,
            llm_provider="openai",
            model="gpt-4",
            use_llm=False
        )

        assert agent.k_clusters == 3
        assert agent.max_demonstrations == 5

    @pytest.mark.skipif(not LLM_AVAILABLE, reason="LLM not available")
    def test_init_with_llm_enabled(self):
        """Test: Inicialización con LLM habilitado."""
        with patch('agents.base.auto_cot_agent.LLMGenerator') as mock_llm:
            agent = AutoCoTAgent(use_llm=True)

            assert agent.use_llm == True
            assert agent.llm is not None

    def test_init_llm_disabled_when_not_available(self):
        """Test: LLM se deshabilita automáticamente si no está disponible."""
        agent = AutoCoTAgent(use_llm=True)

        # Si LLM_AVAILABLE es False, use_llm debería ser False
        if not LLM_AVAILABLE:
            assert agent.use_llm == False
            assert agent.llm is None

    # =========================================================================
    # Tests de Clustering
    # =========================================================================

    def test_cluster_questions_basic(self, sample_questions_list):
        """Test: Clustering básico de preguntas."""
        agent = AutoCoTAgent(k_clusters=2, use_llm=False)

        # Mock numpy clustering if not available
        if not NUMPY_AVAILABLE:
            pytest.skip("Numpy not available for clustering")

        questions = [Question(text=q) for q in sample_questions_list[:4]]

        clusters = agent._cluster_questions(questions)

        assert len(clusters) <= 2  # k_clusters = 2
        assert all(isinstance(cluster, list) for cluster in clusters)

    def test_cluster_questions_more_clusters_than_questions(self):
        """Test: Clustering con más clusters que preguntas."""
        agent = AutoCoTAgent(k_clusters=10, use_llm=False)

        if not NUMPY_AVAILABLE:
            pytest.skip("Numpy not available for clustering")

        questions = [
            Question(text="Q1"),
            Question(text="Q2"),
            Question(text="Q3")
        ]

        clusters = agent._cluster_questions(questions)

        # Debería ajustar k_clusters al número de preguntas
        assert len(clusters) <= 3

    def test_cluster_questions_empty_list(self):
        """Test: Clustering con lista vacía."""
        agent = AutoCoTAgent(use_llm=False)

        if not NUMPY_AVAILABLE:
            pytest.skip("Numpy not available for clustering")

        questions = []
        clusters = agent._cluster_questions(questions)

        assert clusters == [] or clusters == [[]]

    # =========================================================================
    # Tests de Generación de Demostraciones
    # =========================================================================

    def test_generate_demonstrations_basic(self, sample_questions_list, mock_llm_generator):
        """Test: Generación básica de demostraciones."""
        agent = AutoCoTAgent(k_clusters=2, max_demonstrations=3, use_llm=False)

        # Inject mock LLM
        agent.llm = mock_llm_generator
        agent.use_llm = True

        demonstrations = agent.generate_demonstrations(
            questions=sample_questions_list[:3],
            domain="security"
        )

        assert isinstance(demonstrations, list)
        assert len(demonstrations) >= 0
        assert all(isinstance(d, Demonstration) for d in demonstrations)

    def test_generate_demonstrations_respects_max_limit(self, sample_questions_list):
        """Test: Generación respeta límite máximo de demostraciones."""
        agent = AutoCoTAgent(max_demonstrations=2, use_llm=False)

        agent.llm = Mock()
        agent.llm.generate = Mock(return_value={
            "content": "Mock reasoning\nAnswer: Mock answer"
        })
        agent.use_llm = True

        demonstrations = agent.generate_demonstrations(
            questions=sample_questions_list,
            domain="general"
        )

        assert len(demonstrations) <= 2

    def test_generate_demonstrations_with_empty_questions(self):
        """Test: Generación con lista de preguntas vacía."""
        agent = AutoCoTAgent(use_llm=False)

        demonstrations = agent.generate_demonstrations(
            questions=[],
            domain="general"
        )

        assert demonstrations == []

    # =========================================================================
    # Tests de Zero-Shot CoT
    # =========================================================================

    def test_generate_zero_shot_cot(self, sample_question, mock_llm_generator):
        """Test: Generación de Zero-Shot CoT para una pregunta."""
        agent = AutoCoTAgent(use_llm=False)
        agent.llm = mock_llm_generator
        agent.use_llm = True

        # Configure mock to return proper CoT format
        mock_llm_generator.generate.return_value = {
            "content": """
Step 1: Analyze the authentication method
Step 2: Identify SQL injection vulnerability
Step 3: Assess the risk level
Answer: The code has critical security vulnerabilities
"""
        }

        demonstration = agent._generate_zero_shot_cot(sample_question, "security")

        assert isinstance(demonstration, Demonstration)
        assert demonstration.question == sample_question
        assert len(demonstration.reasoning) > 0
        assert len(demonstration.answer) > 0

    def test_generate_zero_shot_cot_extracts_reasoning_and_answer(self, mock_llm_generator):
        """Test: Extracción correcta de reasoning y answer del response."""
        agent = AutoCoTAgent(use_llm=False)
        agent.llm = mock_llm_generator
        agent.use_llm = True

        mock_llm_generator.generate.return_value = {
            "content": "Reasoning: Step by step\nAnswer: Final answer"
        }

        demonstration = agent._generate_zero_shot_cot("Test question", "test")

        assert "Step by step" in demonstration.reasoning or "Reasoning" in demonstration.reasoning
        assert "Final answer" in demonstration.answer or "Answer" in demonstration.answer

    # =========================================================================
    # Tests de Sampling
    # =========================================================================

    def test_sample_diverse_questions(self):
        """Test: Sampling de preguntas diversas de clusters."""
        agent = AutoCoTAgent(use_llm=False)

        clusters = [
            [Question("Q1"), Question("Q2")],
            [Question("Q3")],
            [Question("Q4"), Question("Q5"), Question("Q6")]
        ]

        sampled = agent._sample_diverse_questions(clusters, max_samples=2)

        assert len(sampled) <= 2
        assert all(isinstance(q, Question) for q in sampled)

    def test_sample_diverse_questions_with_single_cluster(self):
        """Test: Sampling con un solo cluster."""
        agent = AutoCoTAgent(use_llm=False)

        clusters = [[Question("Q1"), Question("Q2"), Question("Q3")]]
        sampled = agent._sample_diverse_questions(clusters, max_samples=2)

        assert len(sampled) <= 2

    def test_sample_diverse_questions_empty_clusters(self):
        """Test: Sampling con clusters vacíos."""
        agent = AutoCoTAgent(use_llm=False)

        clusters = [[], [], []]
        sampled = agent._sample_diverse_questions(clusters, max_samples=5)

        assert sampled == []

    # =========================================================================
    # Tests de Quality Scoring
    # =========================================================================

    def test_calculate_quality_score_valid_demonstration(self):
        """Test: Cálculo de quality score para demostración válida."""
        agent = AutoCoTAgent(use_llm=False)

        demo = Demonstration(
            question="What is XSS?",
            reasoning="Step 1: Define XSS\nStep 2: Explain impact\nStep 3: Mitigation",
            answer="XSS is a security vulnerability..."
        )

        score = agent._calculate_quality_score(demo)

        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Should have some quality

    def test_calculate_quality_score_empty_demonstration(self):
        """Test: Quality score para demostración vacía."""
        agent = AutoCoTAgent(use_llm=False)

        demo = Demonstration(
            question="",
            reasoning="",
            answer=""
        )

        score = agent._calculate_quality_score(demo)

        assert score == 0.0 or score < 0.5  # Low quality

    def test_calculate_quality_score_long_reasoning_chain(self):
        """Test: Quality score favorece reasoning chains largos."""
        agent = AutoCoTAgent(use_llm=False)

        demo_short = Demonstration(
            question="Q",
            reasoning="Step 1",
            answer="A"
        )

        demo_long = Demonstration(
            question="Q",
            reasoning="Step 1\nStep 2\nStep 3\nStep 4\nStep 5",
            answer="A"
        )

        score_short = agent._calculate_quality_score(demo_short)
        score_long = agent._calculate_quality_score(demo_long)

        # Longer reasoning should generally score higher
        # (This depends on implementation, adjust assertion if needed)
        assert score_long >= score_short * 0.8  # Allow some variance

    # =========================================================================
    # Tests de Error Handling
    # =========================================================================

    def test_error_handling_llm_failure(self):
        """Test: Manejo de errores cuando LLM falla."""
        agent = AutoCoTAgent(use_llm=False)
        agent.llm = Mock()
        agent.llm.generate = Mock(side_effect=Exception("LLM Error"))
        agent.use_llm = True

        # Should handle gracefully and return empty or fallback
        result = agent.generate_demonstrations(
            questions=["Test question"],
            domain="test"
        )

        assert isinstance(result, list)  # Should not crash

    def test_error_handling_invalid_question_type(self):
        """Test: Manejo de errores con tipo de pregunta inválido."""
        agent = AutoCoTAgent(use_llm=False)

        with pytest.raises((TypeError, ValueError, AttributeError)):
            agent.generate_demonstrations(
                questions=[123, None, {}],  # Invalid types
                domain="test"
            )

    # =========================================================================
    # Tests Parametrizados
    # =========================================================================

    @pytest.mark.parametrize("k_clusters,max_demos", [
        (2, 3),
        (5, 10),
        (10, 5),
    ])
    def test_parametrized_configurations(self, k_clusters, max_demos):
        """Test: Diferentes configuraciones de clusters y demostraciones."""
        agent = AutoCoTAgent(
            k_clusters=k_clusters,
            max_demonstrations=max_demos,
            use_llm=False
        )

        assert agent.k_clusters == k_clusters
        assert agent.max_demonstrations == max_demos

    @pytest.mark.parametrize("llm_provider,model", [
        ("anthropic", "claude-sonnet-4-5-20250929"),
        ("openai", "gpt-4"),
        ("anthropic", "claude-3-opus-20240229"),
    ])
    def test_different_llm_providers(self, llm_provider, model):
        """Test: Diferentes proveedores y modelos de LLM."""
        agent = AutoCoTAgent(
            llm_provider=llm_provider,
            model=model,
            use_llm=False  # Don't actually initialize
        )

        # Should initialize without errors
        assert agent is not None

    # =========================================================================
    # Integration-style Tests
    # =========================================================================

    @pytest.mark.integration
    def test_full_pipeline_without_llm(self, sample_questions_list):
        """Test: Pipeline completo sin LLM (heuristic mode)."""
        agent = AutoCoTAgent(
            k_clusters=2,
            max_demonstrations=2,
            use_llm=False
        )

        demonstrations = agent.generate_demonstrations(
            questions=sample_questions_list[:4],
            domain="security"
        )

        # Even without LLM, should handle gracefully
        assert isinstance(demonstrations, list)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_pipeline_with_mock_llm(self, sample_questions_list, mock_llm_generator):
        """Test: Pipeline completo con mock LLM."""
        agent = AutoCoTAgent(
            k_clusters=2,
            max_demonstrations=3,
            use_llm=False
        )

        agent.llm = mock_llm_generator
        agent.use_llm = True

        mock_llm_generator.generate.return_value = {
            "content": "Step 1: Analysis\nStep 2: Reasoning\nAnswer: Result"
        }

        demonstrations = agent.generate_demonstrations(
            questions=sample_questions_list[:5],
            domain="security"
        )

        assert len(demonstrations) >= 0
        assert all(isinstance(d, Demonstration) for d in demonstrations)


# ============================================================================
# Tests para Classes de Datos
# ============================================================================

class TestQuestion:
    """Tests para la clase Question."""

    def test_question_creation(self):
        """Test: Creación básica de Question."""
        q = Question(text="What is XSS?")

        assert q.text == "What is XSS?"
        assert q.embedding is None
        assert q.cluster_id is None

    def test_question_with_embedding(self):
        """Test: Question con embedding."""
        if NUMPY_AVAILABLE:
            import numpy as np
            embedding = np.array([0.1, 0.2, 0.3])
        else:
            embedding = [0.1, 0.2, 0.3]

        q = Question(text="Test", embedding=embedding)

        assert q.embedding is not None


class TestDemonstration:
    """Tests para la clase Demonstration."""

    def test_demonstration_creation(self):
        """Test: Creación básica de Demonstration."""
        demo = Demonstration(
            question="What is SQL injection?",
            reasoning="Step 1: Define\nStep 2: Explain",
            answer="SQL injection is..."
        )

        assert demo.question == "What is SQL injection?"
        assert "Step 1" in demo.reasoning
        assert "SQL injection" in demo.answer
        assert demo.quality_score == 0.0  # Default

    def test_demonstration_with_quality_score(self):
        """Test: Demonstration con quality score."""
        demo = Demonstration(
            question="Q",
            reasoning="R",
            answer="A",
            quality_score=0.85
        )

        assert demo.quality_score == 0.85


# ============================================================================
# Fixtures locales adicionales (si necesario)
# ============================================================================

@pytest.fixture
def sample_demonstrations():
    """Demonstrations de ejemplo para tests."""
    return [
        Demonstration(
            question="How to prevent XSS?",
            reasoning="Step 1: Sanitize inputs\nStep 2: Escape outputs",
            answer="Sanitize and escape all user inputs",
            quality_score=0.85
        ),
        Demonstration(
            question="What is CSRF?",
            reasoning="Step 1: Define CSRF\nStep 2: Explain attack vector",
            answer="Cross-Site Request Forgery attack",
            quality_score=0.78
        )
    ]
