#!/usr/bin/env python3
"""
TDD Tests for TestGenerationAgent

Tests the agent that uses Tree of Thoughts to generate comprehensive test suites.

Technique: Tree of Thoughts (Yao et al., 2023)
- Explores multiple test generation paths
- Evaluates different test scenarios
- Selects optimal test coverage
- Backtracks when needed

Meta-Application: Using Tree of Thoughts to generate tests for our own code.
"""

import pytest
from scripts.ai.agents.meta import (
    TestGenerationAgent,
    TestSuite,
    TestCase,
    TestType,
    CoverageType
)


# Fixtures
@pytest.fixture
def simple_function():
    """Simple function to generate tests for."""
    return '''
def add(a, b):
    """Add two numbers."""
    return a + b
'''


@pytest.fixture
def complex_function():
    """Complex function with multiple branches."""
    return '''
def calculate_discount(price, customer_type, is_member):
    """Calculate discount based on customer type and membership."""
    if price <= 0:
        raise ValueError("Price must be positive")

    discount = 0.0

    if customer_type == "premium":
        discount = 0.20
    elif customer_type == "regular":
        discount = 0.10
    else:
        discount = 0.05

    if is_member:
        discount += 0.05

    final_price = price * (1 - discount)
    return round(final_price, 2)
'''


@pytest.fixture
def class_with_methods():
    """Class with multiple methods to test."""
    return '''
class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def get_history(self):
        return self.history.copy()
'''


# 1. Initialization Tests
class TestTestGenerationAgentInitialization:
    """Test TestGenerationAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = TestGenerationAgent()

        assert agent.name == "TestGenerationAgent"
        assert agent.tree_of_thoughts is not None

    def test_custom_initialization(self):
        """Should initialize with custom parameters."""
        agent = TestGenerationAgent(
            max_depth=5,
            exploration_breadth=4
        )

        assert agent.max_depth == 5
        assert agent.exploration_breadth == 4


# 2. Test Generation Tests
class TestTestGeneration:
    """Test test suite generation functionality."""

    def test_generate_tests_for_simple_function(self, simple_function):
        """Should generate tests for simple function."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) > 0

    def test_generate_tests_for_complex_function(self, complex_function):
        """Should generate comprehensive tests for complex function."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        assert isinstance(suite, TestSuite)
        # Should have multiple test cases for different branches
        assert len(suite.test_cases) >= 3

    def test_generate_tests_for_class(self, class_with_methods):
        """Should generate tests for class methods."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(class_with_methods)

        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) > 0


# 3. Test Type Coverage Tests
class TestTestTypeCoverage:
    """Test different types of test generation."""

    def test_generates_positive_tests(self, simple_function):
        """Should generate positive test cases."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        positive_tests = [tc for tc in suite.test_cases if tc.test_type == TestType.POSITIVE]
        assert len(positive_tests) > 0

    def test_generates_negative_tests(self, complex_function):
        """Should generate negative test cases for error conditions."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        negative_tests = [tc for tc in suite.test_cases if tc.test_type == TestType.NEGATIVE]
        assert len(negative_tests) > 0

    def test_generates_edge_case_tests(self, complex_function):
        """Should generate edge case tests."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        edge_tests = [tc for tc in suite.test_cases if tc.test_type == TestType.EDGE_CASE]
        assert len(edge_tests) > 0


# 4. Tree of Thoughts Integration Tests
class TestTreeOfThoughtsIntegration:
    """Test Tree of Thoughts technique integration."""

    def test_explores_multiple_paths(self, complex_function):
        """Should explore multiple test generation paths."""
        agent = TestGenerationAgent(exploration_breadth=3)

        suite = agent.generate_tests(complex_function)

        # Should have explored multiple paths
        assert hasattr(suite, 'exploration_paths')
        assert suite.exploration_paths >= 1

    def test_evaluates_test_quality(self, complex_function):
        """Should evaluate quality of generated tests."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        # All test cases should have quality scores
        assert all(hasattr(tc, 'quality_score') for tc in suite.test_cases)
        assert all(0.0 <= tc.quality_score <= 1.0 for tc in suite.test_cases)

    def test_selects_best_tests(self, complex_function):
        """Should select best tests from explored paths."""
        agent = TestGenerationAgent(exploration_breadth=3)

        suite = agent.generate_tests(complex_function)

        # Should have selected high-quality tests
        avg_quality = sum(tc.quality_score for tc in suite.test_cases) / len(suite.test_cases)
        assert avg_quality >= 0.5  # At least medium quality


# 5. Test Case Details Tests
class TestTestCaseDetails:
    """Test generated test case quality."""

    def test_test_cases_have_names(self, simple_function):
        """Test cases should have descriptive names."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        for test_case in suite.test_cases:
            assert test_case.name
            assert len(test_case.name) > 5
            assert 'test_' in test_case.name.lower()

    def test_test_cases_have_code(self, simple_function):
        """Test cases should have executable code."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        for test_case in suite.test_cases:
            assert test_case.code
            assert len(test_case.code) > 10

    def test_test_cases_have_assertions(self, simple_function):
        """Test cases should include assertions."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        for test_case in suite.test_cases:
            assert 'assert' in test_case.code.lower()


# 6. Coverage Analysis Tests
class TestCoverageAnalysis:
    """Test coverage analysis functionality."""

    def test_calculates_coverage_metrics(self, complex_function):
        """Should calculate coverage metrics."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        assert hasattr(suite, 'estimated_coverage')
        assert 0.0 <= suite.estimated_coverage <= 1.0

    def test_identifies_coverage_gaps(self, complex_function):
        """Should identify coverage gaps."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        assert hasattr(suite, 'coverage_gaps')
        assert isinstance(suite.coverage_gaps, list)

    def test_achieves_high_coverage(self, complex_function):
        """Should achieve high coverage for complex functions."""
        agent = TestGenerationAgent(exploration_breadth=5)

        suite = agent.generate_tests(complex_function)

        # Should achieve at least 70% coverage
        assert suite.estimated_coverage >= 0.7


# 7. Test Suite Quality Tests
class TestTestSuiteQuality:
    """Test overall test suite quality."""

    def test_suite_has_description(self, simple_function):
        """Suite should have description."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        assert hasattr(suite, 'description')
        assert suite.description

    def test_suite_has_metadata(self, simple_function):
        """Suite should include metadata."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        assert hasattr(suite, 'total_tests')
        assert suite.total_tests == len(suite.test_cases)

    def test_suite_organizes_by_type(self, complex_function):
        """Suite should organize tests by type."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(complex_function)

        # Should have tests of different types
        test_types = {tc.test_type for tc in suite.test_cases}
        assert len(test_types) > 1


# 8. Edge Cases
class TestTestGenerationEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_empty_code(self):
        """Should handle empty code gracefully."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests("")

        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) == 0

    def test_handles_invalid_syntax(self):
        """Should handle invalid syntax."""
        agent = TestGenerationAgent()

        invalid_code = "def invalid syntax here"

        suite = agent.generate_tests(invalid_code)

        # Should return empty or minimal suite
        assert isinstance(suite, TestSuite)

    def test_handles_very_long_function(self):
        """Should handle very long functions."""
        agent = TestGenerationAgent()

        long_function = "def long_func():\n" + "    pass\n" * 100

        suite = agent.generate_tests(long_function)

        assert isinstance(suite, TestSuite)


# 9. Integration Tests
class TestTestGenerationIntegration:
    """Test integration with other components."""

    def test_suite_serializable(self, simple_function):
        """Suite should be serializable."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        suite_dict = suite.to_dict()
        assert isinstance(suite_dict, dict)
        assert 'test_cases' in suite_dict
        assert 'estimated_coverage' in suite_dict

    def test_test_case_serializable(self, simple_function):
        """Test cases should be serializable."""
        agent = TestGenerationAgent()

        suite = agent.generate_tests(simple_function)

        if suite.test_cases:
            tc_dict = suite.test_cases[0].to_dict()
            assert isinstance(tc_dict, dict)
            assert 'name' in tc_dict
            assert 'test_type' in tc_dict


# 10. LLM Integration Tests (TDD - RED Phase)
class TestLLMIntegration:
    """Test LLM integration for test generation."""

    def test_initializes_with_llm_generator(self):
        """Should initialize LLMGenerator when config provided."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929"
        }
        agent = TestGenerationAgent(config=config)

        # WILL FAIL: Agent doesn't accept config yet
        assert hasattr(agent, 'llm_generator')
        assert agent.llm_generator is not None

    def test_uses_llm_for_test_generation(self, simple_function):
        """Should use LLM to generate high-quality tests."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "use_llm": True
        }
        agent = TestGenerationAgent(config=config)

        suite = agent.generate_tests(simple_function)

        # WILL FAIL: Currently uses heuristics only
        assert hasattr(suite, 'generation_method')
        assert suite.generation_method == 'llm'

    def test_generates_better_tests_with_llm(self, complex_function):
        """LLM should generate higher quality tests than heuristics."""
        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent_with_llm = TestGenerationAgent(config=config)
        agent_without_llm = TestGenerationAgent(config={"use_llm": False})

        suite_with_llm = agent_with_llm.generate_tests(complex_function)
        suite_without_llm = agent_without_llm.generate_tests(complex_function)

        # WILL FAIL: No quality comparison yet
        avg_quality_llm = sum(tc.quality_score for tc in suite_with_llm.test_cases) / len(suite_with_llm.test_cases)
        avg_quality_heuristic = sum(tc.quality_score for tc in suite_without_llm.test_cases) / len(suite_without_llm.test_cases)

        assert avg_quality_llm > avg_quality_heuristic

    def test_fallback_to_heuristics_when_llm_fails(self, simple_function):
        """Should fallback to heuristics if LLM fails."""
        config = {
            "llm_provider": "anthropic",
            "model": "invalid-model",  # This will fail
            "use_llm": True
        }
        agent = TestGenerationAgent(config=config)

        suite = agent.generate_tests(simple_function)

        # WILL FAIL: No fallback mechanism yet
        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) > 0
        assert suite.generation_method == 'heuristic'

    def test_llm_generates_realistic_test_code(self, complex_function):
        """LLM should generate realistic, executable test code."""
        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent = TestGenerationAgent(config=config)

        suite = agent.generate_tests(complex_function)

        # WILL FAIL: Heuristic tests are templated
        for test_case in suite.test_cases:
            # LLM tests should have more realistic values
            assert 'test_param_' not in test_case.code  # Heuristic uses test_param_N
            assert 'invalid_input' not in test_case.code  # Heuristic uses generic names

    def test_respects_api_key_validation(self):
        """Should validate API key before using LLM."""
        import os
        # Temporarily remove API key
        original_key = os.environ.get('ANTHROPIC_API_KEY')
        if original_key:
            del os.environ['ANTHROPIC_API_KEY']

        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }

        try:
            agent = TestGenerationAgent(config=config)
            # WILL FAIL: Should raise error or fallback
            assert hasattr(agent, 'llm_generator')
            # Should either raise error or set use_llm=False
            assert agent.config.get('use_llm') == False or agent.llm_generator is None
        finally:
            # Restore key
            if original_key:
                os.environ['ANTHROPIC_API_KEY'] = original_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
