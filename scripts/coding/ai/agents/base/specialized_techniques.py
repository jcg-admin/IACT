#!/usr/bin/env python3
"""
Specialized, Enterprise, and Evaluation Techniques

Implements: Code Generation, Mathematical Reasoning, Analogical Prompting,
Program-Aided LMs, Medprompt, Batch Prompting, Progressive Prompts,
A/B Testing, Effectiveness Evaluation, Length Management, Multimodal,
Prompt Compression, and Creative Writing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable, Tuple
from enum import Enum
import re
import hashlib


class CodeLanguage(Enum):
    """Programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    SQL = "sql"


class TestVariant(Enum):
    """A/B test variant."""
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"


@dataclass
class CodeSpec:
    """Code generation specification."""
    functionality: str
    language: CodeLanguage
    requirements: List[str]
    constraints: List[str] = field(default_factory=list)
    test_cases: List[Dict] = field(default_factory=list)


@dataclass
class Analogy:
    """Analogy mapping."""
    source_domain: str
    target_domain: str
    mappings: Dict[str, str]


@dataclass
class PromptVariant:
    """Variant for A/B testing."""
    id: str
    variant_type: TestVariant
    prompt_text: str
    hypothesis: str


class CodeGenerationPrompting:
    """
    Code Generation Prompting: Specialized for code generation.

    Usage: Software development assistance, code generation, analysis.
    """

    @staticmethod
    def create_prompt(spec: CodeSpec) -> str:
        """
        Create code generation prompt.

        Args:
            spec: Code specification

        Returns:
            Code generation prompt
        """
        prompt_parts = []

        prompt_parts.append("CODE GENERATION TASK\n")
        prompt_parts.append(f"Language: {spec.language.value}\n")

        prompt_parts.append(f"FUNCTIONALITY:\n{spec.functionality}\n")

        prompt_parts.append("TECHNICAL REQUIREMENTS:")
        for req in spec.requirements:
            prompt_parts.append(f"  - {req}")

        if spec.constraints:
            prompt_parts.append("\nCONSTRAINTS:")
            for constraint in spec.constraints:
                prompt_parts.append(f"  - {constraint}")

        prompt_parts.append("\nOUTPUT FORMAT:")
        prompt_parts.append(f"```{spec.language.value}")
        prompt_parts.append("# Complete, working code with:")
        prompt_parts.append("# - Type hints/annotations")
        prompt_parts.append("# - Docstrings/comments")
        prompt_parts.append("# - Error handling")
        prompt_parts.append("# - Input validation")
        prompt_parts.append("```")

        if spec.test_cases:
            prompt_parts.append("\nTEST CASES TO SATISFY:")
            for i, test in enumerate(spec.test_cases, 1):
                prompt_parts.append(f"\nTest {i}:")
                prompt_parts.append(f"  Input: {test.get('input', 'N/A')}")
                prompt_parts.append(f"  Expected: {test.get('expected', 'N/A')}")

        prompt_parts.append("\nVALIDATION:")
        prompt_parts.append("- Code must be syntactically correct")
        prompt_parts.append("- All requirements must be met")
        prompt_parts.append("- Test cases must pass")
        prompt_parts.append("- Follow language best practices")

        return "\n".join(prompt_parts)


class MathematicalReasoning:
    """
    Mathematical Reasoning: Specialized for mathematical problems.

    Usage: Math problem solving, calculations, proof generation.
    """

    @staticmethod
    def create_prompt(
        problem: str,
        requires_proof: bool = False,
        requires_visualization: bool = False
    ) -> str:
        """
        Create mathematical reasoning prompt.

        Args:
            problem: Mathematical problem
            requires_proof: Whether proof is needed
            requires_visualization: Whether diagrams are needed

        Returns:
            Math-focused prompt
        """
        prompt_parts = []

        prompt_parts.append("MATHEMATICAL PROBLEM SOLVING\n")
        prompt_parts.append(f"PROBLEM:\n{problem}\n")

        prompt_parts.append("SOLUTION APPROACH:")
        prompt_parts.append("Step 1: Understand the Problem")
        prompt_parts.append("  - Identify given information")
        prompt_parts.append("  - Identify what needs to be found")
        prompt_parts.append("  - Identify applicable theorems/formulas")

        prompt_parts.append("\nStep 2: Plan Solution")
        prompt_parts.append("  - Choose appropriate method")
        prompt_parts.append("  - Outline solution steps")

        prompt_parts.append("\nStep 3: Execute Solution")
        prompt_parts.append("  - Show all calculations")
        prompt_parts.append("  - Explain each step")
        prompt_parts.append("  - Maintain mathematical rigor")

        prompt_parts.append("\nStep 4: Verify Solution")
        prompt_parts.append("  - Check calculations")
        prompt_parts.append("  - Verify answer makes sense")
        prompt_parts.append("  - Check edge cases if applicable")

        if requires_proof:
            prompt_parts.append("\nPROOF REQUIREMENTS:")
            prompt_parts.append("  - State theorem/proposition clearly")
            prompt_parts.append("  - Show all logical steps")
            prompt_parts.append("  - Justify each inference")
            prompt_parts.append("  - Conclude with Q.E.D.")

        if requires_visualization:
            prompt_parts.append("\nVISUALIZATION:")
            prompt_parts.append("  - Describe relevant diagrams")
            prompt_parts.append("  - Explain visual representations")

        return "\n".join(prompt_parts)


class AnalogicalPrompting:
    """
    Analogical Prompting: Use analogies to explain complex concepts.

    Usage: Technical explanations, education, presentations.
    """

    def __init__(self, analogy: Analogy):
        """
        Initialize with analogy.

        Args:
            analogy: Analogy specification
        """
        self.analogy = analogy

    def create_prompt(self, concept_to_explain: str) -> str:
        """
        Create analogical prompt.

        Args:
            concept_to_explain: Technical concept to explain

        Returns:
            Analogy-based prompt
        """
        prompt_parts = []

        prompt_parts.append("ANALOGICAL EXPLANATION TASK\n")
        prompt_parts.append(f"CONCEPT TO EXPLAIN: {concept_to_explain}\n")

        prompt_parts.append(f"ANALOGY:")
        prompt_parts.append(f"Source Domain: {self.analogy.source_domain}")
        prompt_parts.append(f"Target Domain: {self.analogy.target_domain}\n")

        prompt_parts.append("CONCEPT MAPPINGS:")
        for source, target in self.analogy.mappings.items():
            prompt_parts.append(f"  {source} → {target}")

        prompt_parts.append("\nINSTRUCTIONS:")
        prompt_parts.append("1. Explain the technical concept using the analogy")
        prompt_parts.append("2. Map each technical element to analogical element")
        prompt_parts.append("3. Maintain consistency throughout explanation")
        prompt_parts.append("4. Highlight where analogy breaks down (if applicable)")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_microservices_city_analogy() -> 'AnalogicalPrompting':
        """
        Factory method for microservices-as-city analogy.

        Returns:
            AnalogicalPrompting instance
        """
        analogy = Analogy(
            source_domain="City Infrastructure",
            target_domain="Microservices Architecture",
            mappings={
                "Buildings": "Microservices",
                "Roads/Streets": "API connections",
                "Traffic Control": "Load Balancer",
                "Utilities (water, power)": "Shared databases",
                "Emergency Services": "Monitoring and alerting",
                "City Planning": "Architecture design",
                "Traffic": "Data flow"
            }
        )
        return AnalogicalPrompting(analogy)


class ProgramAidedLanguageModels:
    """
    Program-Aided Language Models: Combine reasoning with code execution.

    Usage: Problems requiring precise calculations or verification.
    """

    @staticmethod
    def create_prompt(
        problem: str,
        available_tools: List[str],
        requires_verification: bool = True
    ) -> str:
        """
        Create PAL prompt.

        Args:
            problem: Problem to solve
            available_tools: Programming tools/libraries available
            requires_verification: Whether to verify with code

        Returns:
            PAL-enhanced prompt
        """
        prompt_parts = []

        prompt_parts.append("PROGRAM-AIDED PROBLEM SOLVING\n")
        prompt_parts.append(f"PROBLEM:\n{problem}\n")

        prompt_parts.append("AVAILABLE TOOLS:")
        for tool in available_tools:
            prompt_parts.append(f"  - {tool}")

        prompt_parts.append("\nAPPROACH:")
        prompt_parts.append("1. Analyze problem and identify computational steps")
        prompt_parts.append("2. Write code to perform calculations/verification")
        prompt_parts.append("3. Execute code and capture results")
        prompt_parts.append("4. Interpret results in context of problem")

        prompt_parts.append("\nCODE GENERATION:")
        prompt_parts.append("Generate Python code that:")
        prompt_parts.append("  - Performs necessary calculations")
        prompt_parts.append("  - Uses appropriate data structures")
        prompt_parts.append("  - Includes assertions for verification")
        prompt_parts.append("  - Outputs results clearly")

        if requires_verification:
            prompt_parts.append("\nVERIFICATION:")
            prompt_parts.append("  - Run code to verify answer")
            prompt_parts.append("  - Check edge cases programmatically")
            prompt_parts.append("  - Compare with manual calculation")

        return "\n".join(prompt_parts)


class MedpromptFramework:
    """
    Medprompt: Microsoft's enterprise framework combining multiple techniques.

    Usage: High-criticality applications requiring maximum accuracy.
    """

    @staticmethod
    def create_prompt(
        task: str,
        examples: List[Dict[str, str]],
        num_ensemble: int = 3,
        use_cot: bool = True,
        use_self_consistency: bool = True
    ) -> str:
        """
        Create Medprompt-style prompt.

        Args:
            task: Task to perform
            examples: Few-shot examples
            num_ensemble: Number of ensemble runs
            use_cot: Use Chain-of-Thought
            use_self_consistency: Use Self-Consistency

        Returns:
            Medprompt prompt
        """
        prompt_parts = []

        prompt_parts.append("MEDPROMPT FRAMEWORK TASK\n")

        # Phase 1: Few-shot examples
        prompt_parts.append("EXAMPLES:")
        for i, ex in enumerate(examples, 1):
            prompt_parts.append(f"\nExample {i}:")
            prompt_parts.append(f"Input: {ex.get('input', '')}")
            if use_cot:
                prompt_parts.append(f"Reasoning: {ex.get('reasoning', '')}")
            prompt_parts.append(f"Output: {ex.get('output', '')}")

        # Phase 2: Main task
        prompt_parts.append(f"\n\nTASK:\n{task}")

        # Phase 3: Instructions
        if use_cot:
            prompt_parts.append("\nThink step by step:")

        if use_self_consistency:
            prompt_parts.append(f"\nGenerate {num_ensemble} independent solutions.")
            prompt_parts.append("Select the most consistent answer.")

        return "\n".join(prompt_parts)


class BatchPrompting:
    """
    Batch Prompting: Process multiple similar queries efficiently.

    Usage: Large-scale processing of similar tasks.
    """

    @staticmethod
    def create_prompt(
        shared_instructions: str,
        cases: List[Dict[str, Any]],
        output_format: str = "table"
    ) -> str:
        """
        Create batch processing prompt.

        Args:
            shared_instructions: Instructions applying to all cases
            cases: List of cases to process
            output_format: Format for results (table, json, etc.)

        Returns:
            Batch prompt
        """
        prompt_parts = []

        prompt_parts.append("BATCH PROCESSING TASK\n")
        prompt_parts.append(f"SHARED INSTRUCTIONS:\n{shared_instructions}\n")

        prompt_parts.append(f"CASES TO PROCESS ({len(cases)} total):\n")
        for i, case in enumerate(cases, 1):
            prompt_parts.append(f"Case {i}:")
            for key, value in case.items():
                prompt_parts.append(f"  {key}: {value}")
            prompt_parts.append("")

        prompt_parts.append(f"OUTPUT FORMAT: {output_format}")
        if output_format == "table":
            prompt_parts.append("Provide results in a comparison table with standardized metrics.")

        return "\n".join(prompt_parts)


class ProgressivePrompts:
    """
    Progressive Prompts: Build context progressively through interactions.

    Usage: Complex specifications requiring gradual understanding.
    """

    def __init__(self):
        """Initialize progressive prompts."""
        self.levels: List[Dict[str, str]] = []
        self.accumulated_context: str = ""

    def add_level(
        self,
        level_name: str,
        prompt: str,
        builds_on_previous: bool = True
    ) -> 'ProgressivePrompts':
        """
        Add a progressive level.

        Args:
            level_name: Name of this level
            prompt: Prompt for this level
            builds_on_previous: Whether to include previous context

        Returns:
            Self for chaining
        """
        self.levels.append({
            'name': level_name,
            'prompt': prompt,
            'builds_on': builds_on_previous
        })
        return self

    def get_level_prompt(self, level_index: int) -> str:
        """
        Get prompt for a specific level with accumulated context.

        Args:
            level_index: Index of level (0-based)

        Returns:
            Prompt with appropriate context
        """
        if level_index >= len(self.levels):
            raise IndexError(f"Level {level_index} does not exist")

        level = self.levels[level_index]
        prompt_parts = []

        # Add accumulated context if needed
        if level['builds_on'] and self.accumulated_context:
            prompt_parts.append("CONTEXT FROM PREVIOUS ANALYSIS:")
            prompt_parts.append(self.accumulated_context)
            prompt_parts.append("")

        # Add current level
        prompt_parts.append(f"LEVEL {level_index + 1}: {level['name']}")
        prompt_parts.append(level['prompt'])

        return "\n".join(prompt_parts)


class ABTestingPrompts:
    """
    A/B Testing: Compare prompt variants systematically.

    Usage: Optimization of production prompts.
    """

    def __init__(self, control_prompt: str):
        """
        Initialize with control prompt.

        Args:
            control_prompt: Baseline prompt
        """
        self.variants: List[PromptVariant] = []
        self.variants.append(PromptVariant(
            id=self._generate_id(control_prompt),
            variant_type=TestVariant.CONTROL,
            prompt_text=control_prompt,
            hypothesis="Baseline performance"
        ))

    def add_variant(
        self,
        variant_type: TestVariant,
        prompt_text: str,
        hypothesis: str
    ) -> 'ABTestingPrompts':
        """
        Add a test variant.

        Args:
            variant_type: Type of variant
            prompt_text: Variant prompt
            hypothesis: What improvement is expected

        Returns:
            Self for chaining
        """
        variant = PromptVariant(
            id=self._generate_id(prompt_text),
            variant_type=variant_type,
            prompt_text=prompt_text,
            hypothesis=hypothesis
        )
        self.variants.append(variant)
        return self

    @staticmethod
    def _generate_id(text: str) -> str:
        """Generate unique ID for variant."""
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def create_test_plan(self, sample_size: int, metrics: List[str]) -> str:
        """
        Create A/B test plan.

        Args:
            sample_size: Number of samples per variant
            metrics: Metrics to measure

        Returns:
            Test plan description
        """
        plan_parts = []

        plan_parts.append("A/B TEST PLAN\n")
        plan_parts.append(f"Sample Size per Variant: {sample_size}")
        plan_parts.append(f"Total Samples: {sample_size * len(self.variants)}\n")

        plan_parts.append("VARIANTS:")
        for variant in self.variants:
            plan_parts.append(f"\n{variant.variant_type.value.upper()} ({variant.id}):")
            plan_parts.append(f"  Hypothesis: {variant.hypothesis}")
            plan_parts.append(f"  Prompt: {variant.prompt_text[:100]}...")

        plan_parts.append("\nMETRICS TO MEASURE:")
        for metric in metrics:
            plan_parts.append(f"  - {metric}")

        plan_parts.append("\nANALYSIS APPROACH:")
        plan_parts.append("  - Statistical significance testing (p < 0.05)")
        plan_parts.append("  - Confidence intervals for metrics")
        plan_parts.append("  - Qualitative analysis of failure cases")

        return "\n".join(plan_parts)


class EffectivenessEvaluation:
    """
    Effectiveness Evaluation: Systematic prompt quality assessment.

    Usage: Quality control and optimization.
    """

    @staticmethod
    def create_evaluation_framework(
        prompt_to_evaluate: str,
        test_cases: List[Dict],
        metrics: List[str]
    ) -> str:
        """
        Create evaluation framework.

        Args:
            prompt_to_evaluate: Prompt to assess
            test_cases: Test cases for evaluation
            metrics: Metrics to compute

        Returns:
            Evaluation framework description
        """
        framework_parts = []

        framework_parts.append("PROMPT EFFECTIVENESS EVALUATION\n")
        framework_parts.append(f"PROMPT UNDER EVALUATION:")
        framework_parts.append(f"{prompt_to_evaluate}\n")

        framework_parts.append(f"TEST CASES ({len(test_cases)} total):")
        for i, test in enumerate(test_cases[:3], 1):  # Show first 3
            framework_parts.append(f"\n  Test {i}:")
            framework_parts.append(f"    Input: {test.get('input', 'N/A')}")
            framework_parts.append(f"    Expected: {test.get('expected', 'N/A')}")
        if len(test_cases) > 3:
            framework_parts.append(f"  ... and {len(test_cases) - 3} more")

        framework_parts.append("\nEVALUATION METRICS:")
        for metric in metrics:
            framework_parts.append(f"  - {metric}")

        framework_parts.append("\nEVALUATION PROCESS:")
        framework_parts.append("  1. Execute prompt on all test cases")
        framework_parts.append("  2. Calculate each metric")
        framework_parts.append("  3. Identify failure patterns")
        framework_parts.append("  4. Recommend improvements")

        return "\n".join(framework_parts)


class LengthManagement:
    """
    Length Management: Handle long prompts and context limits.

    Usage: Managing context windows and long documents.
    """

    @staticmethod
    def chunk_content(
        content: str,
        max_chunk_size: int,
        overlap: int = 100
    ) -> List[str]:
        """
        Chunk content with overlap.

        Args:
            content: Content to chunk
            max_chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of chunks
        """
        chunks = []
        start = 0

        while start < len(content):
            end = start + max_chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks

    @staticmethod
    def create_summarization_chain_prompt(chunks: List[str]) -> str:
        """
        Create prompt for progressive summarization.

        Args:
            chunks: Content chunks

        Returns:
            Summarization prompt
        """
        prompt_parts = []

        prompt_parts.append("PROGRESSIVE SUMMARIZATION TASK\n")
        prompt_parts.append(f"Process {len(chunks)} chunks progressively:\n")

        for i, chunk in enumerate(chunks, 1):
            prompt_parts.append(f"Chunk {i}:")
            prompt_parts.append(f"Summarize key points from:")
            prompt_parts.append(chunk[:200] + "...")
            prompt_parts.append("")

        prompt_parts.append("FINAL STEP:")
        prompt_parts.append("Integrate all chunk summaries into comprehensive summary")

        return "\n".join(prompt_parts)


class PromptCompression:
    """
    Prompt Compression: Reduce token usage while maintaining effectiveness.

    Usage: Cost optimization and context management.
    """

    @staticmethod
    def compress_prompt(prompt: str, target_reduction: float = 0.3) -> str:
        """
        Compress prompt by removing redundancy.

        Args:
            prompt: Original prompt
            target_reduction: Target reduction percentage (0.0-1.0)

        Returns:
            Compressed prompt
        """
        # Simple compression techniques
        compressed = prompt

        # Remove excessive whitespace
        compressed = re.sub(r'\n{3,}', '\n\n', compressed)
        compressed = re.sub(r' {2,}', ' ', compressed)

        # Remove redundant phrases (simplified)
        redundant = [
            "please note that",
            "it is important to",
            "you should be aware that",
            "as mentioned before",
            "in other words"
        ]
        for phrase in redundant:
            compressed = compressed.replace(phrase, '')

        return compressed.strip()

    @staticmethod
    def create_compression_instructions() -> str:
        """
        Create instructions for LLM-based compression.

        Returns:
            Compression prompt
        """
        return """PROMPT COMPRESSION TASK

Original prompt to compress:
{original_prompt}

COMPRESSION GOALS:
- Reduce token count by ~30-50%
- Preserve all critical information
- Maintain clarity and specificity
- Keep essential examples intact

COMPRESSION TECHNIQUES:
- Remove redundant phrases
- Use abbreviations for repeated terms
- Combine related instructions
- Eliminate unnecessary explanations

Output compressed prompt maintaining >95% semantic equivalence.
"""


class CreativeWritingPrompts:
    """
    Creative Writing Prompts: Structured creativity with constraints.

    Usage: Content generation with style and tone control.
    """

    @staticmethod
    def create_prompt(
        objective: str,
        audience: str,
        tone: str,
        length_range: Tuple[int, int],
        must_include: List[str],
        style_guidelines: List[str]
    ) -> str:
        """
        Create creative writing prompt with constraints.

        Args:
            objective: What to create
            audience: Target audience
            tone: Desired tone
            length_range: (min, max) words
            must_include: Required elements
            style_guidelines: Style constraints

        Returns:
            Creative writing prompt
        """
        prompt_parts = []

        prompt_parts.append("CREATIVE CONTENT GENERATION\n")
        prompt_parts.append(f"OBJECTIVE: {objective}")
        prompt_parts.append(f"AUDIENCE: {audience}")
        prompt_parts.append(f"TONE: {tone}")
        prompt_parts.append(f"LENGTH: {length_range[0]}-{length_range[1]} words\n")

        prompt_parts.append("REQUIRED ELEMENTS:")
        for element in must_include:
            prompt_parts.append(f"  - {element}")

        prompt_parts.append("\nSTYLE GUIDELINES:")
        for guideline in style_guidelines:
            prompt_parts.append(f"  - {guideline}")

        prompt_parts.append("\nCREATIVE CONSTRAINTS:")
        prompt_parts.append("  - Balance creativity with requirements")
        prompt_parts.append("  - Maintain consistency in tone")
        prompt_parts.append("  - Keep audience appropriate")

        return "\n".join(prompt_parts)


def main():
    """Example usage of specialized techniques."""
    print("Specialized, Enterprise, and Evaluation Techniques - Examples\n")
    print("=" * 70)

    # Example 1: Code Generation
    print("\n[Example 1] Code Generation Prompting\n")

    spec = CodeSpec(
        functionality="Parse and validate JSON configuration files",
        language=CodeLanguage.PYTHON,
        requirements=[
            "Handle nested JSON structures",
            "Validate against schema",
            "Provide detailed error messages"
        ],
        constraints=[
            "Use Python 3.9+ features",
            "No external dependencies besides stdlib"
        ],
        test_cases=[
            {"input": '{"key": "value"}', "expected": "Valid"},
            {"input": 'invalid json', "expected": "JSONDecodeError"}
        ]
    )

    prompt = CodeGenerationPrompting.create_prompt(spec)
    print(prompt[:400] + "...\n")

    # Example 2: Medprompt Framework
    print("=" * 70)
    print("\n[Example 2] Medprompt Framework\n")

    examples = [
        {
            "input": "SELECT * FROM users WHERE active = true",
            "reasoning": "Full table scan on users, filter applied after. Need index on active column.",
            "output": "Add index on active column: CREATE INDEX idx_users_active ON users(active)"
        }
    ]

    medprompt = MedpromptFramework.create_prompt(
        task="Optimize this SQL query",
        examples=examples,
        num_ensemble=3,
        use_cot=True,
        use_self_consistency=True
    )
    print(medprompt[:400] + "...\n")

    # Example 3: Batch Prompting
    print("=" * 70)
    print("\n[Example 3] Batch Prompting\n")

    cases = [
        {"code": "def foo(): pass", "language": "Python"},
        {"code": "function bar() {}", "language": "JavaScript"},
        {"code": "func baz() {}", "language": "Go"}
    ]

    batch_prompt = BatchPrompting.create_prompt(
        shared_instructions="Analyze code complexity and suggest improvements",
        cases=cases,
        output_format="table"
    )
    print(batch_prompt[:400] + "...\n")

    # Example 4: A/B Testing
    print("=" * 70)
    print("\n[Example 4] A/B Testing Prompts\n")

    control = "Analyze this code for issues"
    ab_test = ABTestingPrompts(control)
    ab_test.add_variant(
        TestVariant.VARIANT_A,
        "As a senior developer, systematically analyze this code for security, performance, and maintainability issues",
        "Role-based prompt improves thoroughness"
    )

    plan = ab_test.create_test_plan(
        sample_size=100,
        metrics=["Accuracy", "Completeness", "Relevance"]
    )
    print(plan[:400] + "...\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
