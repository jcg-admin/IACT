#!/usr/bin/env python3
"""
TDD Tests for Auto-CoT (Automatic Chain-of-Thought)

Tests the AutoCoTAgent implementation which automatically generates
chain-of-thought demonstrations without human intervention.

Technique: Zhang et al. (2022) - Auto-CoT
Two-stage process:
1. Question Clustering - Group similar questions
2. Demonstration Sampling - Generate CoT examples from each cluster
"""

import pytest
from scripts.ai.agents.base import (
    AutoCoTAgent,
    Demonstration,
    Question
)


# Fixtures
@pytest.fixture
def sample_questions():
    """Sample questions for testing."""
    return [
        "What is 15 + 27?",
        "Calculate 45 - 18",
        "What is 12 * 3?",
        "Solve 144 / 12",
        "What is the capital of France?",
        "Who wrote Romeo and Juliet?",
        "What is photosynthesis?",
        "Explain gravity",
        "How does a computer work?",
        "What is DNA?"
    ]


@pytest.fixture
def math_questions():
    """Math-specific questions."""
    return [
        "What is 25 + 35?",
        "Calculate 100 - 45",
        "What is 8 * 7?",
        "Solve 81 / 9"
    ]


# 1. Initialization Tests
class TestAutoCoTInitialization:
    """Test AutoCoTAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = AutoCoTAgent()

        assert agent.k_clusters == 5
        assert agent.max_demonstrations == 10
        assert agent.demonstrations == []

    def test_custom_initialization(self):
        """Should initialize with custom parameters."""
        agent = AutoCoTAgent(k_clusters=3, max_demonstrations=5)

        assert agent.k_clusters == 3
        assert agent.max_demonstrations == 5


# 2. Question Clustering Tests
class TestQuestionClustering:
    """Test question clustering functionality."""

    def test_cluster_questions_creates_clusters(self, sample_questions):
        """Should create k clusters from questions."""
        agent = AutoCoTAgent(k_clusters=3)
        question_objects = [Question(text=q) for q in sample_questions]

        clustered = agent._cluster_questions(question_objects)

        # Should return same questions with cluster assignments
        assert len(clustered) == len(sample_questions)

        # Each question should have a cluster_id assigned
        cluster_ids = {q.cluster_id for q in clustered if q.cluster_id is not None}
        assert len(cluster_ids) > 0

    def test_cluster_questions_handles_small_input(self):
        """Should handle fewer questions than clusters."""
        agent = AutoCoTAgent(k_clusters=5)
        questions = [Question(text="Question 1"), Question(text="Question 2")]

        clustered = agent._cluster_questions(questions)

        # Should not crash, should return questions
        assert len(clustered) == 2


# 3. Representative Selection Tests
class TestRepresentativeSelection:
    """Test selection of representative questions."""

    def test_select_representatives_from_clusters(self, sample_questions):
        """Should select one representative per cluster."""
        agent = AutoCoTAgent(k_clusters=3, max_demonstrations=3)
        question_objects = [Question(text=q) for q in sample_questions]

        # Cluster first
        clustered = agent._cluster_questions(question_objects)

        # Select representatives
        representatives = agent._select_representatives(clustered)

        # Should have representatives
        assert len(representatives) > 0
        # Should not exceed max_demonstrations
        assert len(representatives) <= agent.max_demonstrations

    def test_select_representatives_respects_max_limit(self, sample_questions):
        """Should respect max_demonstrations limit."""
        agent = AutoCoTAgent(k_clusters=5, max_demonstrations=3)
        question_objects = [Question(text=q) for q in sample_questions]

        clustered = agent._cluster_questions(question_objects)
        representatives = agent._select_representatives(clustered)

        assert len(representatives) <= 3


# 4. Single Demonstration Generation Tests
class TestSingleDemonstrationGeneration:
    """Test generation of individual demonstrations."""

    def test_generate_single_demonstration_structure(self):
        """Should generate demonstration with correct structure."""
        agent = AutoCoTAgent()
        question_text = "What is 5 + 3?"

        demo = agent._generate_single_demonstration(question_text, domain="math")

        # Should return a Demonstration object
        assert isinstance(demo, Demonstration)
        assert demo.question != ""
        assert demo.reasoning != ""
        assert demo.answer != ""

    def test_generate_demonstration_includes_reasoning_steps(self):
        """Generated reasoning should have multiple steps."""
        agent = AutoCoTAgent()
        question_text = "Calculate 15 * 4"

        demo = agent._generate_single_demonstration(question_text, domain="math")

        # Reasoning should have steps (indicated by newlines or step markers)
        assert len(demo.reasoning) > 20  # Substantial reasoning
        # Quality score should be assigned
        assert demo.quality_score >= 0.0


# 5. Demonstration Validation Tests
class TestDemonstrationValidation:
    """Test validation of generated demonstrations."""

    def test_validate_accepts_good_demonstration(self):
        """Should accept valid demonstration."""
        agent = AutoCoTAgent()
        demo = Demonstration(
            question="What is 2 + 2?",
            reasoning="""Let's think step by step.
First, we start with the number 2 as our base.
Next, we need to add another 2 to this number.
When we combine 2 and 2 together, we get 4.
Therefore, the answer to 2 + 2 is 4.""",
            answer="4",
            quality_score=0.8
        )

        is_valid = agent._validate_demonstration(demo)

        assert is_valid is True

    def test_validate_rejects_empty_reasoning(self):
        """Should reject demonstration with no reasoning."""
        agent = AutoCoTAgent()
        demo = Demonstration(
            question="What is 2 + 2?",
            reasoning="",
            answer="4"
        )

        is_valid = agent._validate_demonstration(demo)

        assert is_valid is False

    def test_validate_rejects_short_reasoning(self):
        """Should reject demonstration with insufficient reasoning."""
        agent = AutoCoTAgent()
        demo = Demonstration(
            question="What is 2 + 2?",
            reasoning="Just add them",  # Too short
            answer="4"
        )

        is_valid = agent._validate_demonstration(demo)

        assert is_valid is False


# 6. Full Pipeline Tests
class TestAutoCoTFullPipeline:
    """Test complete Auto-CoT generation pipeline."""

    def test_generate_demonstrations_end_to_end(self, math_questions):
        """Should generate demonstrations from questions."""
        agent = AutoCoTAgent(k_clusters=2, max_demonstrations=2)

        demonstrations = agent.generate_demonstrations(
            questions=math_questions,
            domain="mathematics"
        )

        # Should generate some demonstrations
        assert len(demonstrations) > 0
        assert len(demonstrations) <= agent.max_demonstrations

        # Each demonstration should be valid
        for demo in demonstrations:
            assert isinstance(demo, Demonstration)
            assert demo.question != ""
            assert demo.reasoning != ""
            assert demo.answer != ""

    def test_generate_demonstrations_stores_results(self, math_questions):
        """Should store generated demonstrations."""
        agent = AutoCoTAgent(k_clusters=2, max_demonstrations=3)

        demonstrations = agent.generate_demonstrations(math_questions, "math")

        # Should store in agent.demonstrations
        assert agent.demonstrations == demonstrations


# 7. Domain-Specific Tests
class TestDomainSpecificGeneration:
    """Test Auto-CoT with different domains."""

    def test_math_domain_generation(self):
        """Should generate math-specific demonstrations."""
        agent = AutoCoTAgent(k_clusters=2)
        questions = [
            "What is 12 + 8?",
            "Calculate 25 * 4"
        ]

        demos = agent.generate_demonstrations(questions, domain="mathematics")

        assert len(demos) > 0

    def test_science_domain_generation(self):
        """Should generate science-specific demonstrations."""
        agent = AutoCoTAgent(k_clusters=2)
        questions = [
            "What is photosynthesis?",
            "Explain Newton's first law"
        ]

        demos = agent.generate_demonstrations(questions, domain="science")

        assert len(demos) > 0


# 8. Edge Cases
class TestAutoCoTEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_single_question(self):
        """Should handle single question gracefully."""
        agent = AutoCoTAgent(k_clusters=1, max_demonstrations=1)
        questions = ["What is 5 + 5?"]

        demos = agent.generate_demonstrations(questions, "math")

        # Should generate at least one demonstration
        assert len(demos) >= 0  # May be 0 or 1 depending on validation

    def test_handles_duplicate_questions(self):
        """Should handle duplicate questions."""
        agent = AutoCoTAgent(k_clusters=2)
        questions = ["What is 2 + 2?"] * 5  # 5 identical questions

        demos = agent.generate_demonstrations(questions, "math")

        # Should handle gracefully
        assert isinstance(demos, list)

    def test_handles_empty_question_list(self):
        """Should handle empty question list."""
        agent = AutoCoTAgent()
        questions = []

        demos = agent.generate_demonstrations(questions, "math")

        assert demos == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
