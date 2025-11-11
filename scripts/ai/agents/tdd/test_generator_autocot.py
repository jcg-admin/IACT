#!/usr/bin/env python3
"""
Test Generator with Auto-CoT Integration

Enhanced version of TestGenerator that uses Auto-CoT to generate
more intelligent and contextual test code.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.auto_cot_agent import AutoCoTAgent, Demonstration
from tdd.test_generator import TestGenerator, TestCase
from typing import Dict, List


class TestGeneratorAutoCoT(TestGenerator):
    """
    Enhanced TestGenerator using Auto-CoT for intelligent test generation.

    Extends base TestGenerator with Auto-CoT capabilities to generate
    more contextual and reasoning-based test code.
    """

    def __init__(self, component_name: str, agent_type: str, use_auto_cot: bool = True):
        super().__init__(component_name, agent_type)
        self.use_auto_cot = use_auto_cot
        self.auto_cot: Optional[AutoCoTAgent] = None

        if use_auto_cot:
            self.auto_cot = AutoCoTAgent(k_clusters=3, max_demonstrations=5)
            self._initialize_auto_cot_demonstrations()

    def _initialize_auto_cot_demonstrations(self):
        """Initialize Auto-CoT with test generation questions."""
        # Preguntas representativas para generar tests
        test_questions = self._get_domain_questions()

        if test_questions:
            print("[TestGenerator-AutoCoT] Generating Auto-CoT demonstrations...")
            self.auto_cot.generate_demonstrations(
                test_questions,
                domain=f"test_generation_{self.agent_type}"
            )

    def _get_domain_questions(self) -> List[str]:
        """Get domain-specific questions for Auto-CoT training."""
        if self.agent_type == "gate":
            return [
                "How to test that a gate correctly identifies violations in code?",
                "What assertions validate that an agent reports errors accurately?",
                "How to verify that a validator handles edge cases properly?",
                "What test cases cover security vulnerabilities in validation?",
                "How to test that a gate's output format is consistent?"
            ]
        elif self.agent_type == "chain":
            return [
                "How to test that a chain executes steps in correct order?",
                "What assertions verify data flows correctly between chain steps?",
                "How to test error propagation in multi-step chains?",
                "What mocks are needed to test chain dependencies?",
                "How to verify that a chain handles failures gracefully?"
            ]
        else:  # template
            return [
                "How to test that a template generates correct output format?",
                "What assertions validate template variable substitution?",
                "How to test template rendering with missing variables?",
                "What edge cases exist for template generation?",
                "How to verify template output is syntactically correct?"
            ]

    def analyze_requirements(
        self,
        requirements: str,
        expected_behavior: Dict[str, any]
    ) -> List[TestCase]:
        """
        Enhanced requirements analysis using Auto-CoT reasoning.

        Overrides parent method to add Auto-CoT reasoning to test generation.
        """
        if not self.use_auto_cot or not self.auto_cot:
            # Fallback to parent implementation
            return super().analyze_requirements(requirements, expected_behavior)

        print("[TestGenerator-AutoCoT] Analyzing requirements with Auto-CoT...")

        test_cases = []

        # Generate basic tests with Auto-CoT reasoning
        test_cases.extend(self._generate_basic_tests_with_cot(requirements))

        # Generate happy path test with Auto-CoT
        happy_path = expected_behavior.get("happy_path", "")
        if happy_path:
            test_case = self._generate_happy_path_with_cot(happy_path, requirements)
            test_cases.append(test_case)

        # Generate edge case tests with Auto-CoT
        edge_cases = expected_behavior.get("edge_cases", [])
        for i, case in enumerate(edge_cases, 1):
            test_case = self._generate_edge_case_with_cot(i, case, requirements)
            test_cases.append(test_case)

        # Generate error case tests with Auto-CoT
        error_cases = expected_behavior.get("error_cases", [])
        for i, case in enumerate(error_cases, 1):
            test_case = self._generate_error_case_with_cot(i, case, requirements)
            test_cases.append(test_case)

        # Generate integration tests
        test_cases.extend(self._generate_integration_tests(requirements))

        self.test_cases = test_cases
        return test_cases

    def _generate_basic_tests_with_cot(self, requirements: str) -> List[TestCase]:
        """Generate basic tests using Auto-CoT reasoning."""
        question = f"How to test basic initialization and setup for: {requirements}"

        # Get Auto-CoT reasoning
        reasoning = self._get_auto_cot_reasoning(question)

        return [
            TestCase(
                name="test_agent_initialization",
                description="Test: Agent initializes correctly with all required attributes",
                category="basic",
                setup_code=[
                    f"# Auto-CoT reasoning: {reasoning[:100]}...",
                    f"agent = {self._get_agent_class()}()",
                ],
                test_code=[
                    "assert agent is not None, 'Agent should initialize'",
                    f"assert agent.name == '{self.component_name}', 'Agent name should match'",
                    "assert hasattr(agent, 'execute'), 'Agent should have execute method'",
                ],
                assertions=[
                    "assert agent is not None",
                    f"assert agent.name == '{self.component_name}'"
                ]
            ),
            TestCase(
                name="test_project_root_detection",
                description="Test: Project root detection is robust and accurate",
                category="basic",
                setup_code=[
                    f"agent = {self._get_agent_class()}()",
                    "root = agent.get_project_root()",
                ],
                test_code=[
                    "assert root.exists(), 'Project root must exist'",
                    "assert root.is_dir(), 'Project root must be directory'",
                    "# Verify markers exist",
                    "markers = ['.git', 'pyproject.toml', 'api/callcentersite']",
                    "assert any((root / marker).exists() for marker in markers), 'Project markers should exist'",
                ],
                assertions=[
                    "assert root.exists()",
                    "assert root.is_dir()"
                ]
            )
        ]

    def _generate_happy_path_with_cot(self, happy_path: str, requirements: str) -> TestCase:
        """Generate happy path test with Auto-CoT reasoning."""
        question = f"How to test happy path: {happy_path} for requirement: {requirements}"

        reasoning = self._get_auto_cot_reasoning(question)

        # Extraer pasos del razonamiento
        steps = self._extract_steps_from_reasoning(reasoning)

        return TestCase(
            name="test_happy_path_success",
            description=f"Test: {happy_path}",
            category="basic",
            setup_code=[
                f"# Auto-CoT reasoning applied: {len(steps)} steps identified",
                f"agent = {self._get_agent_class()}()",
                "# Setup valid input data",
                "valid_input = create_valid_test_data()",
            ],
            test_code=[
                "# Execute happy path",
                "result = agent.execute(valid_input)",
                "",
                "# Validate result",
                "assert result.success is True, 'Happy path should succeed'",
                "assert result.violations_count == 0, 'No violations in happy path'",
                "assert result.output is not None, 'Should produce output'",
            ],
            assertions=[
                "assert result.success is True",
                "assert result.violations_count == 0"
            ]
        )

    def _generate_edge_case_with_cot(
        self,
        index: int,
        case_description: str,
        requirements: str
    ) -> TestCase:
        """Generate edge case test with Auto-CoT reasoning."""
        question = f"How to test edge case: {case_description}"

        reasoning = self._get_auto_cot_reasoning(question)

        # Determinar tipo de edge case
        if "empty" in case_description.lower() or "vacío" in case_description.lower():
            return self._generate_empty_input_test(index, case_description, reasoning)
        elif "none" in case_description.lower() or "null" in case_description.lower():
            return self._generate_null_input_test(index, case_description, reasoning)
        elif "large" in case_description.lower() or "grande" in case_description.lower():
            return self._generate_large_input_test(index, case_description, reasoning)
        else:
            return self._generate_generic_edge_test(index, case_description, reasoning)

    def _generate_error_case_with_cot(
        self,
        index: int,
        case_description: str,
        requirements: str
    ) -> TestCase:
        """Generate error case test with Auto-CoT reasoning."""
        question = f"How to test error handling for: {case_description}"

        reasoning = self._get_auto_cot_reasoning(question)

        return TestCase(
            name=f"test_error_case_{index}",
            description=f"Test: {case_description}",
            category="error",
            setup_code=[
                f"# Auto-CoT guidance: {reasoning[:80]}...",
                f"agent = {self._get_agent_class()}()",
                "# Setup invalid input that triggers error",
                "invalid_input = create_invalid_test_data()",
            ],
            test_code=[
                "# Test error handling",
                "with pytest.raises(ValueError) as exc_info:",
                "    agent.execute(invalid_input)",
                "",
                "# Validate error details",
                "assert 'invalid' in str(exc_info.value).lower(), 'Error message should be descriptive'",
            ],
            assertions=[]
        )

    def _get_auto_cot_reasoning(self, question: str) -> str:
        """Get Auto-CoT reasoning for a question."""
        if not self.auto_cot or not self.auto_cot.demonstrations:
            return "Standard test approach"

        # Usar few-shot prompt con demostraciones Auto-CoT
        try:
            prompt = self.auto_cot.create_few_shot_prompt(question, max_examples=2)
            # En producción: esto llamaría a un LLM real
            # Por ahora retornamos template estructurado
            return self._generate_reasoning_from_prompt(prompt)
        except:
            return "Standard test approach"

    def _generate_reasoning_from_prompt(self, prompt: str) -> str:
        """Generate reasoning from prompt (placeholder for LLM call)."""
        return """Let's think step by step.
First, identify what needs to be tested and why.
Next, determine the setup required (fixtures, mocks, data).
Then, define the exact assertions that validate correctness.
Finally, consider edge cases and error conditions."""

    def _extract_steps_from_reasoning(self, reasoning: str) -> List[str]:
        """Extract explicit steps from reasoning text."""
        lines = reasoning.split('\n')
        steps = []

        step_keywords = ['first', 'next', 'then', 'finally', 'step']

        for line in lines:
            if any(keyword in line.lower() for keyword in step_keywords):
                # Clean up line
                step = line.strip()
                step = step.lstrip('0123456789.-) ')
                if step:
                    steps.append(step)

        return steps

    def _generate_empty_input_test(self, index: int, description: str, reasoning: str) -> TestCase:
        """Generate test for empty input edge case."""
        return TestCase(
            name=f"test_edge_case_empty_{index}",
            description=f"Test: {description}",
            category="edge",
            setup_code=[
                f"# Guided by: {reasoning[:60]}...",
                f"agent = {self._get_agent_class()}()",
                "empty_input = ''  # or [] or {}",
            ],
            test_code=[
                "result = agent.execute(empty_input)",
                "# Should handle empty input gracefully",
                "assert result is not None, 'Should return result even for empty input'",
                "assert isinstance(result.violations, list), 'Violations should be list'",
            ],
            assertions=["assert result is not None"]
        )

    def _generate_null_input_test(self, index: int, description: str, reasoning: str) -> TestCase:
        """Generate test for null/None input edge case."""
        return TestCase(
            name=f"test_edge_case_null_{index}",
            description=f"Test: {description}",
            category="edge",
            setup_code=[
                f"agent = {self._get_agent_class()}()",
            ],
            test_code=[
                "# Test handling of None/null input",
                "result = agent.execute(None)",
                "assert result is not None, 'Should handle None without crashing'",
                "# May return error result or empty result",
            ],
            assertions=["assert result is not None"]
        )

    def _generate_large_input_test(self, index: int, description: str, reasoning: str) -> TestCase:
        """Generate test for large input edge case."""
        return TestCase(
            name=f"test_edge_case_large_input_{index}",
            description=f"Test: {description}",
            category="edge",
            setup_code=[
                f"agent = {self._get_agent_class()}()",
                "# Create large test input",
                "large_input = create_large_test_data(size=10000)",
            ],
            test_code=[
                "import time",
                "start = time.time()",
                "result = agent.execute(large_input)",
                "duration = time.time() - start",
                "",
                "assert result is not None, 'Should handle large input'",
                "assert duration < 5.0, 'Should complete within reasonable time'",
            ],
            assertions=[
                "assert result is not None",
                "assert duration < 5.0"
            ]
        )

    def _generate_generic_edge_test(self, index: int, description: str, reasoning: str) -> TestCase:
        """Generate generic edge case test."""
        return TestCase(
            name=f"test_edge_case_{index}",
            description=f"Test: {description}",
            category="edge",
            setup_code=[
                f"# Test reasoning: {reasoning[:70]}...",
                f"agent = {self._get_agent_class()}()",
            ],
            test_code=[
                f"# Implement specific test for: {description}",
                "# TODO: Add setup and assertions based on edge case",
                "pytest.skip('Requires domain-specific implementation')",
            ],
            assertions=[],
            should_skip=True
        )


# Helper functions for test data creation
def create_valid_test_data():
    """Create valid test data for happy path tests."""
    return {
        'input': 'valid_data',
        'params': {'key': 'value'}
    }


def create_invalid_test_data():
    """Create invalid test data for error case tests."""
    return {
        'input': None,
        'params': {}
    }


def create_large_test_data(size: int = 1000):
    """Create large test data for performance/edge case tests."""
    return {
        'input': 'x' * size,
        'params': {f'key_{i}': f'value_{i}' for i in range(size)}
    }


def main():
    """Example usage of TestGeneratorAutoCoT."""
    print("Test Generator with Auto-CoT - Example\n")

    requirements = "Validate that ViewSets have permission_classes defined"
    expected_behavior = {
        "happy_path": "ViewSet with permissions is validated successfully",
        "edge_cases": [
            "Empty permission_classes list",
            "Permission_classes with only IsAuthenticated"
        ],
        "error_cases": [
            "ViewSet without permission_classes attribute",
            "Invalid permission class type"
        ]
    }

    generator = TestGeneratorAutoCoT(
        component_name="route_linter",
        agent_type="gate",
        use_auto_cot=True
    )

    test_cases = generator.analyze_requirements(requirements, expected_behavior)

    print(f"\nGenerated {len(test_cases)} test cases:")
    for i, tc in enumerate(test_cases, 1):
        print(f"{i}. {tc.name} ({tc.category})")

    # Generate test file
    output_path = Path("test_route_linter_autocot.py")
    generator.generate_test_file(output_path)
    print(f"\nTest file generated: {output_path}")


if __name__ == "__main__":
    main()
