#!/usr/bin/env python3
"""
Optimization and Control Techniques

Implements: Delimiters/Formatting, Constrained Generation, Negative Prompting,
Constitutional AI, Emotional Prompting, Meta-Prompting, and Iterative Refinement.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import re
import json


class DelimiterType(Enum):
    """Types of delimiters for content separation."""
    TRIPLE_QUOTES = '"""'
    TRIPLE_BACKTICKS = "```"
    XML_TAGS = "<tag></tag>"
    MARKDOWN_HEADERS = "##"
    HORIZONTAL_RULES = "---"
    BRACKETS = "[]"


class ConstraintType(Enum):
    """Types of output constraints."""
    FORMAT = "format"
    LENGTH = "length"
    CONTENT = "content"
    STYLE = "style"
    STRUCTURE = "structure"


@dataclass
class Principle:
    """Constitutional AI principle."""
    name: str
    description: str
    priority: int  # 1 = highest
    violation_action: str  # What to do if violated


@dataclass
class MetricDefinition:
    """Definition of an evaluation metric."""
    name: str
    description: str
    measurement_method: str
    target_value: Optional[float] = None


class DelimitersAndFormatting:
    """
    Delimiters and Formatting: Clear content separation and structure.

    Usage: Complex prompts with multiple sections or content types.
    """

    @staticmethod
    def create_delimited_prompt(
        sections: Dict[str, str],
        delimiter_type: DelimiterType = DelimiterType.MARKDOWN_HEADERS
    ) -> str:
        """
        Create prompt with clear section delimiters.

        Args:
            sections: Dict of section_name: content
            delimiter_type: Type of delimiter to use

        Returns:
            Delimited prompt
        """
        prompt_parts = []

        for section_name, content in sections.items():
            if delimiter_type == DelimiterType.MARKDOWN_HEADERS:
                prompt_parts.append(f"## {section_name.upper()}\n")
                prompt_parts.append(content)
                prompt_parts.append("")

            elif delimiter_type == DelimiterType.HORIZONTAL_RULES:
                prompt_parts.append(f"--- {section_name.upper()} ---")
                prompt_parts.append(content)
                prompt_parts.append("---\n")

            elif delimiter_type == DelimiterType.TRIPLE_BACKTICKS:
                prompt_parts.append(f"{section_name.upper()}:")
                prompt_parts.append("```")
                prompt_parts.append(content)
                prompt_parts.append("```\n")

            elif delimiter_type == DelimiterType.XML_TAGS:
                tag = section_name.lower().replace(" ", "_")
                prompt_parts.append(f"<{tag}>")
                prompt_parts.append(content)
                prompt_parts.append(f"</{tag}>\n")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_multi_content_prompt(
        instruction: str,
        code_blocks: Dict[str, str],
        data_sections: Dict[str, Any],
        requirements: List[str]
    ) -> str:
        """
        Create prompt with multiple content types clearly delimited.

        Args:
            instruction: Main instruction
            code_blocks: Dict of language: code
            data_sections: Dict of name: data
            requirements: List of requirements

        Returns:
            Well-structured prompt
        """
        prompt_parts = []

        # Instruction
        prompt_parts.append("## INSTRUCTION")
        prompt_parts.append(instruction)
        prompt_parts.append("")

        # Code blocks
        if code_blocks:
            prompt_parts.append("## CODE TO ANALYZE")
            for lang, code in code_blocks.items():
                prompt_parts.append(f"\n### {lang.upper()} Code:")
                prompt_parts.append(f"```{lang}")
                prompt_parts.append(code)
                prompt_parts.append("```")

        # Data sections
        if data_sections:
            prompt_parts.append("\n## DATA")
            for name, data in data_sections.items():
                prompt_parts.append(f"\n### {name}:")
                if isinstance(data, (dict, list)):
                    prompt_parts.append(f"```json")
                    prompt_parts.append(json.dumps(data, indent=2))
                    prompt_parts.append("```")
                else:
                    prompt_parts.append(str(data))

        # Requirements
        if requirements:
            prompt_parts.append("\n## REQUIREMENTS")
            for i, req in enumerate(requirements, 1):
                prompt_parts.append(f"{i}. {req}")

        return "\n".join(prompt_parts)


class ConstrainedGeneration:
    """
    Constrained Generation: Generate output with specific constraints.

    Usage: When output must meet exact format or content specifications.
    """

    def __init__(self):
        """Initialize constraint system."""
        self.constraints: List[Dict[str, Any]] = []

    def add_format_constraint(
        self,
        format_type: str,
        specification: Dict[str, Any]
    ) -> 'ConstrainedGeneration':
        """
        Add a format constraint.

        Args:
            format_type: Type of format (json, xml, markdown, etc.)
            specification: Format specification

        Returns:
            Self for chaining
        """
        self.constraints.append({
            'type': ConstraintType.FORMAT,
            'format_type': format_type,
            'specification': specification
        })
        return self

    def add_length_constraint(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        unit: str = "characters"
    ) -> 'ConstrainedGeneration':
        """
        Add length constraint.

        Args:
            min_length: Minimum length
            max_length: Maximum length
            unit: Unit of measurement (characters, words, lines)

        Returns:
            Self for chaining
        """
        self.constraints.append({
            'type': ConstraintType.LENGTH,
            'min': min_length,
            'max': max_length,
            'unit': unit
        })
        return self

    def add_content_constraint(
        self,
        must_include: Optional[List[str]] = None,
        must_not_include: Optional[List[str]] = None,
        required_sections: Optional[List[str]] = None
    ) -> 'ConstrainedGeneration':
        """
        Add content constraints.

        Args:
            must_include: Elements that must be present
            must_not_include: Elements that must not be present
            required_sections: Required sections

        Returns:
            Self for chaining
        """
        self.constraints.append({
            'type': ConstraintType.CONTENT,
            'must_include': must_include or [],
            'must_not_include': must_not_include or [],
            'required_sections': required_sections or []
        })
        return self

    def create_prompt(self, task: str) -> str:
        """
        Create constrained generation prompt.

        Args:
            task: The generation task

        Returns:
            Prompt with constraints
        """
        prompt_parts = []

        prompt_parts.append(f"TASK: {task}\n")
        prompt_parts.append("OUTPUT CONSTRAINTS:\n")

        for i, constraint in enumerate(self.constraints, 1):
            constraint_type = constraint['type']

            if constraint_type == ConstraintType.FORMAT:
                format_type = constraint['format_type']
                spec = constraint['specification']
                prompt_parts.append(f"{i}. FORMAT CONSTRAINT:")
                prompt_parts.append(f"   Type: {format_type}")
                prompt_parts.append(f"   Specification:")
                prompt_parts.append(f"   ```json")
                prompt_parts.append(f"   {json.dumps(spec, indent=6)}")
                prompt_parts.append(f"   ```")

            elif constraint_type == ConstraintType.LENGTH:
                prompt_parts.append(f"{i}. LENGTH CONSTRAINT:")
                if constraint.get('min'):
                    prompt_parts.append(f"   Minimum: {constraint['min']} {constraint['unit']}")
                if constraint.get('max'):
                    prompt_parts.append(f"   Maximum: {constraint['max']} {constraint['unit']}")

            elif constraint_type == ConstraintType.CONTENT:
                prompt_parts.append(f"{i}. CONTENT CONSTRAINT:")
                if constraint['must_include']:
                    must_include = ", ".join(constraint['must_include'])
                    prompt_parts.append(f"   Must include: {must_include}")
                if constraint['must_not_include']:
                    must_not = ", ".join(constraint['must_not_include'])
                    prompt_parts.append(f"   Must NOT include: {must_not}")
                if constraint['required_sections']:
                    sections = ", ".join(constraint['required_sections'])
                    prompt_parts.append(f"   Required sections: {sections}")

            prompt_parts.append("")

        prompt_parts.append("VALIDATION:")
        prompt_parts.append("Output MUST comply with ALL constraints above.")
        prompt_parts.append("Non-compliant output will be rejected.")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_json_constraint(schema: Dict[str, Any]) -> 'ConstrainedGeneration':
        """
        Factory method for JSON output constraints.

        Args:
            schema: JSON schema specification

        Returns:
            ConstrainedGeneration instance with JSON constraints
        """
        cg = ConstrainedGeneration()
        cg.add_format_constraint("json", schema)
        return cg


class NegativePrompting:
    """
    Negative Prompting: Specify what NOT to do or include.

    Usage: Control output by preventing unwanted behaviors or content.
    """

    @staticmethod
    def create_prompt(
        task: str,
        do_not_do: List[str],
        do_not_include: List[str],
        do_not_assume: List[str]
    ) -> str:
        """
        Create prompt with negative constraints.

        Args:
            task: Main task
            do_not_do: Behaviors to avoid
            do_not_include: Content to exclude
            do_not_assume: Assumptions not to make

        Returns:
            Prompt with negative constraints
        """
        prompt_parts = []

        prompt_parts.append(f"TASK: {task}\n")

        prompt_parts.append("NEGATIVE CONSTRAINTS:\n")

        prompt_parts.append("DO NOT do the following:")
        for item in do_not_do:
            prompt_parts.append(f"  ✗ {item}")

        prompt_parts.append("\nDO NOT include:")
        for item in do_not_include:
            prompt_parts.append(f"  ✗ {item}")

        prompt_parts.append("\nDO NOT assume:")
        for item in do_not_assume:
            prompt_parts.append(f"  ✗ {item}")

        prompt_parts.append("\nThese constraints are MANDATORY.")

        return "\n".join(prompt_parts)


class ConstitutionalAI:
    """
    Constitutional AI: Ethical principles and behavioral guidelines.

    Usage: Tasks requiring ethical considerations or value alignment.
    """

    def __init__(self):
        """Initialize with principles."""
        self.principles: List[Principle] = []

    def add_principle(
        self,
        name: str,
        description: str,
        priority: int = 2,
        violation_action: str = "reject"
    ) -> 'ConstitutionalAI':
        """
        Add a constitutional principle.

        Args:
            name: Principle name
            description: What the principle requires
            priority: Priority level (1 = highest)
            violation_action: What to do if violated

        Returns:
            Self for chaining
        """
        principle = Principle(
            name=name,
            description=description,
            priority=priority,
            violation_action=violation_action
        )
        self.principles.append(principle)
        return self

    def create_prompt(self, task: str) -> str:
        """
        Create constitutionally-guided prompt.

        Args:
            task: The task to perform

        Returns:
            Prompt with constitutional principles
        """
        prompt_parts = []

        prompt_parts.append(f"TASK: {task}\n")

        prompt_parts.append("CONSTITUTIONAL PRINCIPLES:")
        prompt_parts.append("Follow these fundamental principles:\n")

        # Sort by priority
        sorted_principles = sorted(self.principles, key=lambda p: p.priority)

        for principle in sorted_principles:
            priority_label = {1: "[CRITICAL]", 2: "[HIGH]", 3: "[MEDIUM]"}.get(
                principle.priority, "[LOW]"
            )
            prompt_parts.append(f"{priority_label} {principle.name}:")
            prompt_parts.append(f"  {principle.description}")
            prompt_parts.append(f"  If violated: {principle.violation_action}")
            prompt_parts.append("")

        prompt_parts.append("Adhere to ALL principles in your response.")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_privacy_first() -> 'ConstitutionalAI':
        """
        Factory method for privacy-first principles.

        Returns:
            ConstitutionalAI instance with privacy principles
        """
        ca = ConstitutionalAI()
        ca.add_principle(
            "Privacy Protection",
            "Minimize collection and exposure of personal data. Never request unnecessary personal information.",
            priority=1,
            violation_action="reject request and explain privacy concern"
        ).add_principle(
            "Transparency",
            "Be clear about data usage and processing. Provide explanations for decisions.",
            priority=2
        ).add_principle(
            "User Control",
            "Respect user preferences and provide opt-out mechanisms.",
            priority=2
        ).add_principle(
            "Data Minimization",
            "Only use data necessary for the specific task.",
            priority=1
        )
        return ca


class EmotionalPrompting:
    """
    Emotional Prompting: Use emotional cues to improve response quality.

    Usage: Critical tasks where careful attention is important.
    """

    @staticmethod
    def create_prompt(
        task: str,
        importance_level: str = "high",
        consequences: Optional[str] = None,
        audience_impact: Optional[str] = None
    ) -> str:
        """
        Create emotionally-enhanced prompt.

        Args:
            task: The task to perform
            importance_level: How critical the task is (low/medium/high/critical)
            consequences: Potential consequences of errors
            audience_impact: Who will be affected

        Returns:
            Emotionally-enhanced prompt
        """
        prompt_parts = []

        # Add importance framing
        importance_messages = {
            "low": "This task requires careful attention.",
            "medium": "This is an important task that requires thoughtful analysis.",
            "high": "This is a critical task. Your accuracy and thoroughness are essential.",
            "critical": "This is an extremely critical task with significant consequences. Please give this your utmost care and attention."
        }

        prompt_parts.append(importance_messages.get(importance_level, importance_messages["medium"]))
        prompt_parts.append("")

        # Add consequences if provided
        if consequences:
            prompt_parts.append(f"CONSEQUENCES OF ERRORS: {consequences}")
            prompt_parts.append("")

        # Add audience impact
        if audience_impact:
            prompt_parts.append(f"IMPACT: {audience_impact}")
            prompt_parts.append("")

        # Add the task
        prompt_parts.append(f"TASK:\n{task}\n")

        # Add emotional appeal
        prompt_parts.append("Please take your time and provide the most accurate, complete response possible.")
        prompt_parts.append("Double-check your analysis before finalizing your answer.")

        return "\n".join(prompt_parts)


class MetaPrompting:
    """
    Meta-Prompting: Prompts that generate optimized prompts.

    Usage: Automatic prompt optimization for specific use cases.
    """

    @staticmethod
    def create_prompt_generation_prompt(
        use_case: str,
        objectives: List[str],
        constraints: List[str],
        target_audience: str,
        output_format: str
    ) -> str:
        """
        Create prompt that generates optimized prompts.

        Args:
            use_case: What the generated prompt will be used for
            objectives: What the prompt should achieve
            constraints: Limitations or requirements
            target_audience: Who will use the generated prompt
            output_format: Expected output format

        Returns:
            Meta-prompt for prompt generation
        """
        prompt_parts = []

        prompt_parts.append("META-PROMPTING TASK: Generate an optimized prompt\n")

        prompt_parts.append(f"USE CASE:\n{use_case}\n")

        prompt_parts.append("OBJECTIVES:")
        prompt_parts.append("The generated prompt must achieve:")
        for obj in objectives:
            prompt_parts.append(f"  - {obj}")

        prompt_parts.append("\nCONSTRAINTS:")
        for constraint in constraints:
            prompt_parts.append(f"  - {constraint}")

        prompt_parts.append(f"\nTARGET AUDIENCE: {target_audience}")
        prompt_parts.append(f"OUTPUT FORMAT: {output_format}\n")

        prompt_parts.append("PROMPT ENGINEERING BEST PRACTICES TO APPLY:")
        prompt_parts.append("  - Clear, specific instructions")
        prompt_parts.append("  - Appropriate context and examples")
        prompt_parts.append("  - Explicit output format specification")
        prompt_parts.append("  - Validation criteria")
        prompt_parts.append("  - Anti-hallucination safeguards\n")

        prompt_parts.append("Generate an optimized prompt that incorporates these elements.")

        return "\n".join(prompt_parts)


class IterativeRefinement:
    """
    Iterative Refinement: Systematic improvement of prompts based on results.

    Usage: Optimization of prompts for production use.
    """

    def __init__(self, initial_prompt: str):
        """
        Initialize with initial prompt.

        Args:
            initial_prompt: Starting prompt
        """
        self.iterations: List[Dict[str, Any]] = []
        self.current_prompt = initial_prompt
        self.iterations.append({
            'version': 0,
            'prompt': initial_prompt,
            'metrics': {},
            'changes': "Initial version"
        })

    def add_iteration(
        self,
        refined_prompt: str,
        metrics: Dict[str, float],
        changes_made: str
    ) -> 'IterativeRefinement':
        """
        Add a refinement iteration.

        Args:
            refined_prompt: The improved prompt
            metrics: Performance metrics
            changes_made: Description of changes

        Returns:
            Self for chaining
        """
        version = len(self.iterations)
        self.iterations.append({
            'version': version,
            'prompt': refined_prompt,
            'metrics': metrics,
            'changes': changes_made
        })
        self.current_prompt = refined_prompt
        return self

    def get_improvement_summary(self) -> str:
        """
        Get summary of improvements across iterations.

        Returns:
            Summary report
        """
        if len(self.iterations) < 2:
            return "No iterations yet"

        summary_parts = []
        summary_parts.append("ITERATIVE REFINEMENT SUMMARY\n")

        for i, iteration in enumerate(self.iterations):
            summary_parts.append(f"Version {iteration['version']}:")
            summary_parts.append(f"  Changes: {iteration['changes']}")

            if iteration['metrics']:
                summary_parts.append("  Metrics:")
                for metric, value in iteration['metrics'].items():
                    summary_parts.append(f"    {metric}: {value}")

            summary_parts.append("")

        # Calculate improvements
        if len(self.iterations) >= 2:
            first = self.iterations[0]
            latest = self.iterations[-1]

            if first['metrics'] and latest['metrics']:
                summary_parts.append("OVERALL IMPROVEMENT:")
                for metric in first['metrics']:
                    if metric in latest['metrics']:
                        change = latest['metrics'][metric] - first['metrics'][metric]
                        pct = (change / first['metrics'][metric]) * 100 if first['metrics'][metric] != 0 else 0
                        summary_parts.append(f"  {metric}: {change:+.2f} ({pct:+.1f}%)")

        return "\n".join(summary_parts)


def main():
    """Example usage of optimization techniques."""
    print("Optimization and Control Techniques - Examples\n")
    print("=" * 70)

    # Example 1: Delimiters and Formatting
    print("\n[Example 1] Delimiters and Formatting\n")

    sections = {
        "Code to Analyze": "def process_data(data):\n    return data.upper()",
        "Requirements": "Must handle None values\nMust be performant",
        "Expected Output": "Analysis report with recommendations"
    }

    prompt = DelimitersAndFormatting.create_delimited_prompt(sections)
    print(prompt[:300] + "...\n")

    # Example 2: Constrained Generation
    print("=" * 70)
    print("\n[Example 2] Constrained Generation\n")

    schema = {
        "type": "object",
        "properties": {
            "analysis": {"type": "string", "maxLength": 200},
            "score": {"type": "number", "minimum": 0, "maximum": 10},
            "issues": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["analysis", "score"]
    }

    cg = ConstrainedGeneration.create_json_constraint(schema)
    prompt = cg.create_prompt("Analyze this code for quality")
    print(prompt[:400] + "...\n")

    # Example 3: Constitutional AI
    print("=" * 70)
    print("\n[Example 3] Constitutional AI\n")

    ca = ConstitutionalAI.create_privacy_first()
    prompt = ca.create_prompt("Design a user analytics system")
    print(prompt[:400] + "...\n")

    # Example 4: Emotional Prompting
    print("=" * 70)
    print("\n[Example 4] Emotional Prompting\n")

    prompt = EmotionalPrompting.create_prompt(
        task="Review this security configuration for production deployment",
        importance_level="critical",
        consequences="Security vulnerabilities could expose sensitive customer data",
        audience_impact="500,000+ active users depend on this system"
    )
    print(prompt[:400] + "...\n")

    # Example 5: Meta-Prompting
    print("=" * 70)
    print("\n[Example 5] Meta-Prompting\n")

    meta_prompt = MetaPrompting.create_prompt_generation_prompt(
        use_case="Code review for Django applications",
        objectives=[
            "Identify security vulnerabilities",
            "Check Django best practices",
            "Evaluate performance"
        ],
        constraints=[
            "Must be concise (under 300 words)",
            "Must include specific examples",
            "Must work with code snippets"
        ],
        target_audience="Senior developers",
        output_format="Structured report with priorities"
    )
    print(meta_prompt[:400] + "...\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
