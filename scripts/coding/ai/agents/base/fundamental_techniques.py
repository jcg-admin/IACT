#!/usr/bin/env python3
"""
Fundamental Prompting Techniques

Implements core prompting techniques: Zero-Shot, Few-Shot, and Role Prompting.
These are the foundation for all advanced techniques.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


class PromptingMode(Enum):
    """Type of prompting mode."""
    ZERO_SHOT = "zero_shot"
    ONE_SHOT = "one_shot"
    FEW_SHOT = "few_shot"
    MANY_SHOT = "many_shot"


@dataclass
class Example:
    """Example for few-shot prompting."""
    input: str
    output: str
    explanation: Optional[str] = None


@dataclass
class Role:
    """Role definition for role prompting."""
    title: str
    expertise: List[str]
    perspective: str
    constraints: Optional[List[str]] = None


class ZeroShotPrompting:
    """
    Zero-Shot Prompting: Perform tasks without providing examples.

    Usage: Direct instructions for well-defined tasks where the model
    has sufficient knowledge.
    """

    @staticmethod
    def create_prompt(
        task: str,
        context: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        output_format: Optional[str] = None
    ) -> str:
        """
        Create a zero-shot prompt.

        Args:
            task: The task to perform
            context: Optional context information
            constraints: Optional constraints on the output
            output_format: Optional specification of output format

        Returns:
            Complete zero-shot prompt
        """
        prompt_parts = []

        # Add context if provided
        if context:
            prompt_parts.append(f"CONTEXT:\n{context}\n")

        # Add main task
        prompt_parts.append(f"TASK:\n{task}\n")

        # Add constraints if provided
        if constraints:
            constraints_text = "\n".join(f"- {c}" for c in constraints)
            prompt_parts.append(f"CONSTRAINTS:\n{constraints_text}\n")

        # Add output format if specified
        if output_format:
            prompt_parts.append(f"OUTPUT FORMAT:\n{output_format}\n")

        # Add validation reminder
        prompt_parts.append("""
VALIDATION:
- Base your response only on the information provided
- If you're uncertain about any aspect, state: "Requires verification: [specific aspect]"
- Do not invent information not present in the context
""")

        return "\n".join(prompt_parts)


class FewShotPrompting:
    """
    Few-Shot Prompting: Provide limited examples before the main task.

    Variants:
    - One-shot: 1 example
    - Few-shot: 2-5 examples
    - Many-shot: 5+ examples
    """

    def __init__(self, examples: List[Example]):
        """
        Initialize with examples.

        Args:
            examples: List of example input-output pairs
        """
        self.examples = examples

    def get_mode(self) -> PromptingMode:
        """Determine the prompting mode based on number of examples."""
        num_examples = len(self.examples)
        if num_examples == 0:
            return PromptingMode.ZERO_SHOT
        elif num_examples == 1:
            return PromptingMode.ONE_SHOT
        elif num_examples <= 5:
            return PromptingMode.FEW_SHOT
        else:
            return PromptingMode.MANY_SHOT

    def create_prompt(
        self,
        task: str,
        new_input: str,
        include_explanations: bool = False
    ) -> str:
        """
        Create a few-shot prompt with examples.

        Args:
            task: Description of the task
            new_input: The new input to process
            include_explanations: Whether to include explanations with examples

        Returns:
            Complete few-shot prompt
        """
        prompt_parts = []

        # Add task description
        prompt_parts.append(f"TASK: {task}\n")

        # Add examples
        mode = self.get_mode()
        prompt_parts.append(f"EXAMPLES ({mode.value.replace('_', '-')}):\n")

        for i, example in enumerate(self.examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Input: {example.input}")
            prompt_parts.append(f"Output: {example.output}")

            if include_explanations and example.explanation:
                prompt_parts.append(f"Explanation: {example.explanation}")

            prompt_parts.append("")  # Empty line between examples

        # Add new input
        prompt_parts.append(f"Now process this input:")
        prompt_parts.append(f"Input: {new_input}")
        prompt_parts.append(f"Output:")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_from_data(
        task: str,
        examples_data: List[Dict[str, str]],
        new_input: str
    ) -> str:
        """
        Convenience method to create few-shot prompt from dictionary data.

        Args:
            task: Task description
            examples_data: List of dicts with 'input' and 'output' keys
            new_input: New input to process

        Returns:
            Complete few-shot prompt
        """
        examples = [
            Example(
                input=ex['input'],
                output=ex['output'],
                explanation=ex.get('explanation')
            )
            for ex in examples_data
        ]

        agent = FewShotPrompting(examples)
        return agent.create_prompt(task, new_input)


class RolePrompting:
    """
    Role Prompting: Assign specific roles or personas to guide responses.

    Usage: Tasks requiring specialized knowledge or specific perspectives.
    """

    def __init__(self, role: Role):
        """
        Initialize with a role definition.

        Args:
            role: Role specification
        """
        self.role = role

    def create_prompt(
        self,
        task: str,
        context: Optional[str] = None,
        specific_instructions: Optional[List[str]] = None
    ) -> str:
        """
        Create a role-based prompt.

        Args:
            task: The task to perform
            context: Optional context information
            specific_instructions: Optional specific instructions

        Returns:
            Complete role-based prompt
        """
        prompt_parts = []

        # Define the role
        prompt_parts.append(f"ROLE: {self.role.title}")
        prompt_parts.append(f"\nYou are {self.role.title}.")

        # Add expertise
        if self.role.expertise:
            expertise_text = ", ".join(self.role.expertise)
            prompt_parts.append(f"Your expertise includes: {expertise_text}.")

        # Add perspective
        prompt_parts.append(f"Your perspective: {self.role.perspective}.")

        # Add role constraints
        if self.role.constraints:
            constraints_text = "\n".join(f"- {c}" for c in self.role.constraints)
            prompt_parts.append(f"\nRole constraints:\n{constraints_text}")

        # Add context if provided
        if context:
            prompt_parts.append(f"\nCONTEXT:\n{context}")

        # Add the task
        prompt_parts.append(f"\nTASK:\n{task}")

        # Add specific instructions
        if specific_instructions:
            instructions_text = "\n".join(f"- {i}" for i in specific_instructions)
            prompt_parts.append(f"\nSPECIFIC INSTRUCTIONS:\n{instructions_text}")

        # Add validation
        prompt_parts.append("""
VALIDATION:
- Respond from your assigned role's perspective
- Apply your expertise to the analysis
- If something is outside your expertise, acknowledge it
- Base conclusions on verifiable information
""")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_technical_expert(
        specialization: str,
        years_experience: int,
        specific_skills: List[str]
    ) -> 'RolePrompting':
        """
        Factory method for creating technical expert roles.

        Args:
            specialization: Area of specialization
            years_experience: Years of experience
            specific_skills: List of specific skills

        Returns:
            RolePrompting instance with technical expert role
        """
        role = Role(
            title=f"Senior {specialization} with {years_experience}+ years experience",
            expertise=specific_skills,
            perspective=f"Deep technical knowledge of {specialization} with focus on best practices and production-ready solutions",
            constraints=[
                "Provide technically accurate information",
                "Cite specific technologies and versions when relevant",
                "Consider scalability and maintainability",
                "Flag potential security issues"
            ]
        )

        return RolePrompting(role)

    @staticmethod
    def create_multi_role_prompt(
        roles: List[Role],
        task: str,
        synthesis_instruction: str
    ) -> str:
        """
        Create a prompt with multiple perspectives.

        Args:
            roles: List of roles to consider
            task: The task to analyze
            synthesis_instruction: How to synthesize the perspectives

        Returns:
            Multi-role prompt
        """
        prompt_parts = []

        prompt_parts.append(f"TASK: {task}\n")
        prompt_parts.append("Analyze this from multiple perspectives:\n")

        # Add each role perspective
        for i, role in enumerate(roles, 1):
            prompt_parts.append(f"\n## Perspective {i}: {role.title}")
            prompt_parts.append(f"Expertise: {', '.join(role.expertise)}")
            prompt_parts.append(f"Focus: {role.perspective}")
            prompt_parts.append("Analysis from this perspective:")
            prompt_parts.append("[Your analysis here]\n")

        # Add synthesis instruction
        prompt_parts.append(f"\n## SYNTHESIS")
        prompt_parts.append(synthesis_instruction)

        return "\n".join(prompt_parts)


def main():
    """Example usage of fundamental prompting techniques."""
    print("Fundamental Prompting Techniques - Examples\n")
    print("=" * 70)

    # Example 1: Zero-Shot Prompting
    print("\n[Example 1] Zero-Shot Prompting\n")

    zero_shot_prompt = ZeroShotPrompting.create_prompt(
        task="Analyze this SQL query for performance issues and suggest optimizations",
        context="Database: PostgreSQL 14, Table size: 1M rows, Current query time: 3.5s",
        constraints=[
            "Focus on index usage",
            "Consider query plan analysis",
            "Suggest specific, actionable improvements"
        ],
        output_format="Structured list with: Issue, Impact, Solution"
    )

    print(zero_shot_prompt[:300] + "...\n")

    # Example 2: Few-Shot Prompting
    print("=" * 70)
    print("\n[Example 2] Few-Shot Prompting\n")

    examples = [
        Example(
            input="User needs to reset password",
            output="As a user, I want to reset my password via email so that I can regain access to my account",
            explanation="Converts user need into user story format"
        ),
        Example(
            input="System must validate data",
            output="As a system, I must validate all input data to prevent errors and security vulnerabilities",
            explanation="Frames system requirement as user story"
        )
    ]

    few_shot = FewShotPrompting(examples)
    prompt = few_shot.create_prompt(
        task="Convert user requirements to user story format",
        new_input="Reports generate automatically",
        include_explanations=True
    )

    print(f"Mode: {few_shot.get_mode().value}")
    print(prompt[:400] + "...\n")

    # Example 3: Role Prompting
    print("=" * 70)
    print("\n[Example 3] Role Prompting\n")

    # Technical expert role
    expert = RolePrompting.create_technical_expert(
        specialization="Database Administrator",
        years_experience=15,
        specific_skills=[
            "PostgreSQL optimization",
            "High-availability systems",
            "Query performance tuning",
            "Replication and backup strategies"
        ]
    )

    role_prompt = expert.create_prompt(
        task="Review this database migration strategy for production deployment",
        context="E-commerce system, 500K daily transactions, 24/7 uptime requirement",
        specific_instructions=[
            "Assess downtime risk",
            "Validate rollback plan",
            "Check data integrity measures"
        ]
    )

    print(role_prompt[:400] + "...\n")

    # Example 4: Multi-Role Analysis
    print("=" * 70)
    print("\n[Example 4] Multi-Role Perspective\n")

    roles = [
        Role(
            title="Senior Developer",
            expertise=["Code quality", "Maintainability", "Testing"],
            perspective="Focus on implementation quality and long-term maintainability"
        ),
        Role(
            title="DevOps Engineer",
            expertise=["Deployment", "Monitoring", "Scalability"],
            perspective="Focus on operational concerns and production readiness"
        ),
        Role(
            title="Security Architect",
            expertise=["Security", "Compliance", "Risk assessment"],
            perspective="Focus on security vulnerabilities and compliance requirements"
        )
    ]

    multi_role_prompt = RolePrompting.create_multi_role_prompt(
        roles=roles,
        task="Evaluate this microservices architecture proposal",
        synthesis_instruction="Provide a balanced recommendation considering all three perspectives"
    )

    print(multi_role_prompt[:500] + "...\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
