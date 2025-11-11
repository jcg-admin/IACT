#!/usr/bin/env python3
"""
Structuring and Control Techniques

Implements: Prompt Chaining, Task Decomposition, Least-to-Most Prompting,
and Instruction Hierarchy for complex problem solving.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum


class Priority(Enum):
    """Priority level for instructions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChainStep:
    """Single step in a prompt chain."""
    step_id: str
    prompt: str
    context_from_previous: bool = True
    output_processor: Optional[Callable[[str], Dict]] = None
    expected_output_format: Optional[str] = None


@dataclass
class SubTask:
    """Subtask in task decomposition."""
    id: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"
    validation_criteria: List[str] = field(default_factory=list)


@dataclass
class Instruction:
    """Hierarchical instruction with priority."""
    level: int  # 1 = highest, 2 = objectives, 3+ = details
    priority: Priority
    content: str
    constraints: Optional[List[str]] = None


class PromptChaining:
    """
    Prompt Chaining: Sequence of prompts where output feeds next input.

    Usage: Complex tasks that benefit from division into sequential stages.
    """

    def __init__(self):
        """Initialize prompt chain."""
        self.steps: List[ChainStep] = []
        self.context_accumulation: Dict[str, Any] = {}

    def add_step(
        self,
        step_id: str,
        prompt_template: str,
        context_from_previous: bool = True,
        output_processor: Optional[Callable] = None
    ) -> 'PromptChaining':
        """
        Add a step to the chain.

        Args:
            step_id: Unique identifier for this step
            prompt_template: Prompt template (can use {previous_output}, {context})
            context_from_previous: Whether to pass context from previous step
            output_processor: Optional function to process output

        Returns:
            Self for chaining
        """
        step = ChainStep(
            step_id=step_id,
            prompt=prompt_template,
            context_from_previous=context_from_previous,
            output_processor=output_processor
        )
        self.steps.append(step)
        return self

    def execute_chain(
        self,
        initial_input: str,
        executor: Callable[[str], str]
    ) -> Dict[str, Any]:
        """
        Execute the complete chain.

        Args:
            initial_input: Initial input for the chain
            executor: Function that executes a prompt and returns output

        Returns:
            Dict with outputs from all steps
        """
        results = {}
        previous_output = initial_input

        for step in self.steps:
            # Build prompt with context
            if step.context_from_previous:
                prompt = step.prompt.format(
                    previous_output=previous_output,
                    **self.context_accumulation
                )
            else:
                prompt = step.prompt

            print(f"[Chain] Executing step: {step.step_id}")

            # Execute step
            output = executor(prompt)

            # Process output if processor provided
            if step.output_processor:
                processed = step.output_processor(output)
                self.context_accumulation.update(processed)

            # Store result
            results[step.step_id] = output
            previous_output = output

        return results

    @staticmethod
    def create_analysis_chain(domain: str) -> 'PromptChaining':
        """
        Factory method for creating common analysis chains.

        Args:
            domain: Domain of analysis (code, architecture, data, etc.)

        Returns:
            Pre-configured PromptChaining instance
        """
        chain = PromptChaining()

        if domain == "code":
            chain.add_step(
                "requirements_extraction",
                "Analyze this code and extract functional requirements:\n{previous_output}\n\nList all requirements found."
            ).add_step(
                "architecture_analysis",
                "Based on these requirements:\n{previous_output}\n\nAnalyze the architectural patterns used."
            ).add_step(
                "recommendations",
                "Based on the architecture analysis:\n{previous_output}\n\nProvide specific improvement recommendations."
            )

        elif domain == "architecture":
            chain.add_step(
                "component_identification",
                "Identify all major components in this system:\n{previous_output}"
            ).add_step(
                "interaction_analysis",
                "For these components:\n{previous_output}\n\nAnalyze critical interactions and data flows."
            ).add_step(
                "risk_assessment",
                "Given components and interactions:\n{previous_output}\n\nIdentify architectural risks and mitigation strategies."
            )

        return chain


class TaskDecomposition:
    """
    Task Decomposition: Systematic division of complex tasks into subtasks.

    Usage: Complex problems requiring structured approach.
    """

    def __init__(self, main_task: str):
        """
        Initialize with main task.

        Args:
            main_task: Description of the main task
        """
        self.main_task = main_task
        self.subtasks: List[SubTask] = []

    def add_subtask(
        self,
        task_id: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        complexity: str = "medium",
        validation: Optional[List[str]] = None
    ) -> 'TaskDecomposition':
        """
        Add a subtask.

        Args:
            task_id: Unique identifier
            description: Subtask description
            dependencies: IDs of tasks that must complete first
            complexity: Estimated complexity (low/medium/high)
            validation: Validation criteria

        Returns:
            Self for chaining
        """
        subtask = SubTask(
            id=task_id,
            description=description,
            dependencies=dependencies or [],
            estimated_complexity=complexity,
            validation_criteria=validation or []
        )
        self.subtasks.append(subtask)
        return self

    def get_execution_order(self) -> List[SubTask]:
        """
        Get subtasks in executable order based on dependencies.

        Returns:
            Ordered list of subtasks
        """
        # Simple topological sort
        completed = set()
        ordered = []

        while len(ordered) < len(self.subtasks):
            added_this_round = False

            for subtask in self.subtasks:
                if subtask.id in completed:
                    continue

                # Check if all dependencies are completed
                if all(dep in completed for dep in subtask.dependencies):
                    ordered.append(subtask)
                    completed.add(subtask.id)
                    added_this_round = True

            if not added_this_round and len(ordered) < len(self.subtasks):
                # Circular dependency detected
                raise ValueError("Circular dependency detected in subtasks")

        return ordered

    def create_decomposition_prompt(self) -> str:
        """
        Create a prompt describing the task decomposition.

        Returns:
            Complete decomposition prompt
        """
        prompt_parts = []

        prompt_parts.append(f"MAIN TASK: {self.main_task}\n")
        prompt_parts.append("DECOMPOSITION INTO SUBTASKS:\n")

        ordered_tasks = self.get_execution_order()

        for i, subtask in enumerate(ordered_tasks, 1):
            prompt_parts.append(f"\nSubtask {i}: {subtask.id}")
            prompt_parts.append(f"Description: {subtask.description}")
            prompt_parts.append(f"Complexity: {subtask.estimated_complexity}")

            if subtask.dependencies:
                deps_text = ", ".join(subtask.dependencies)
                prompt_parts.append(f"Dependencies: {deps_text}")

            if subtask.validation_criteria:
                validation_text = "\n  - ".join(subtask.validation_criteria)
                prompt_parts.append(f"Validation:\n  - {validation_text}")

        prompt_parts.append("\n\nEXECUTION STRATEGY:")
        prompt_parts.append("Complete subtasks in the order listed, validating each before proceeding.")

        return "\n".join(prompt_parts)


class LeastToMostPrompting:
    """
    Least-to-Most Prompting: Start with simplest elements, build to complex.

    Usage: Problems benefiting from incremental approach.
    """

    def __init__(self, problem: str):
        """
        Initialize with problem description.

        Args:
            problem: The complex problem to solve
        """
        self.problem = problem
        self.progression: List[Dict[str, str]] = []

    def add_level(
        self,
        level: int,
        description: str,
        builds_on: Optional[List[int]] = None
    ) -> 'LeastToMostPrompting':
        """
        Add a complexity level.

        Args:
            level: Complexity level (1 = simplest)
            description: What to implement at this level
            builds_on: Previous levels this builds upon

        Returns:
            Self for chaining
        """
        self.progression.append({
            'level': level,
            'description': description,
            'builds_on': builds_on or ([] if level == 1 else [level - 1])
        })
        return self

    def create_prompt(self) -> str:
        """
        Create least-to-most prompt.

        Returns:
            Complete prompt with progressive complexity
        """
        prompt_parts = []

        prompt_parts.append(f"PROBLEM: {self.problem}\n")
        prompt_parts.append("APPROACH: Least-to-Most (incremental complexity)\n")
        prompt_parts.append("PROGRESSION:\n")

        # Sort by level
        sorted_progression = sorted(self.progression, key=lambda x: x['level'])

        for item in sorted_progression:
            level = item['level']
            desc = item['description']
            builds_on = item['builds_on']

            if level == 1:
                prompt_parts.append(f"\nLevel {level} (SIMPLEST): {desc}")
            else:
                builds_text = f" (builds on Level {', '.join(map(str, builds_on))})"
                prompt_parts.append(f"\nLevel {level}{builds_text}: {desc}")

            prompt_parts.append(f"  - Implement and validate before proceeding")

        prompt_parts.append("\n\nINSTRUCTIONS:")
        prompt_parts.append("1. Start with Level 1 (simplest)")
        prompt_parts.append("2. Fully implement and test each level")
        prompt_parts.append("3. Build incrementally on previous levels")
        prompt_parts.append("4. Validate functionality at each step")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_implementation_progression(feature: str, num_levels: int = 5) -> 'LeastToMostPrompting':
        """
        Factory method for implementation progressions.

        Args:
            feature: Feature to implement
            num_levels: Number of complexity levels

        Returns:
            LeastToMostPrompting instance with levels
        """
        ltm = LeastToMostPrompting(f"Implement {feature} feature")

        # Generic progression levels
        levels = [
            "Basic functionality with minimal features",
            "Add input validation and error handling",
            "Implement edge case handling",
            "Add optimization and performance improvements",
            "Complete with monitoring and logging"
        ]

        for i, desc in enumerate(levels[:num_levels], 1):
            ltm.add_level(i, desc)

        return ltm


class InstructionHierarchy:
    """
    Instruction Hierarchy: Structured prompts with clear priority levels.

    Usage: Complex tasks with multiple requirements and constraints.
    """

    def __init__(self, primary_objective: str):
        """
        Initialize with primary objective.

        Args:
            primary_objective: Main goal of the task
        """
        self.primary_objective = primary_objective
        self.instructions: List[Instruction] = []

    def add_instruction(
        self,
        level: int,
        priority: Priority,
        content: str,
        constraints: Optional[List[str]] = None
    ) -> 'InstructionHierarchy':
        """
        Add an instruction at a specific hierarchy level.

        Args:
            level: Hierarchy level (1 = highest)
            priority: Priority of this instruction
            content: Instruction content
            constraints: Optional constraints

        Returns:
            Self for chaining
        """
        instruction = Instruction(
            level=level,
            priority=priority,
            content=content,
            constraints=constraints
        )
        self.instructions.append(instruction)
        return self

    def create_prompt(self) -> str:
        """
        Create hierarchical prompt.

        Returns:
            Complete structured prompt
        """
        prompt_parts = []

        prompt_parts.append(f"PRIMARY OBJECTIVE: {self.primary_objective}\n")

        # Group by level
        by_level: Dict[int, List[Instruction]] = {}
        for inst in self.instructions:
            if inst.level not in by_level:
                by_level[inst.level] = []
            by_level[inst.level].append(inst)

        # Sort levels
        for level in sorted(by_level.keys()):
            level_name = {
                1: "CRITICAL REQUIREMENTS",
                2: "PRIMARY OBJECTIVES",
                3: "SECONDARY OBJECTIVES",
                4: "OPTIONAL ENHANCEMENTS"
            }.get(level, f"LEVEL {level}")

            prompt_parts.append(f"\n{level_name}:")

            # Sort by priority within level
            instructions = sorted(
                by_level[level],
                key=lambda x: list(Priority).index(x.priority)
            )

            for inst in instructions:
                priority_marker = {
                    Priority.CRITICAL: "[CRITICAL]",
                    Priority.HIGH: "[HIGH]",
                    Priority.MEDIUM: "[MEDIUM]",
                    Priority.LOW: "[LOW]"
                }[inst.priority]

                prompt_parts.append(f"  {priority_marker} {inst.content}")

                if inst.constraints:
                    for constraint in inst.constraints:
                        prompt_parts.append(f"    • {constraint}")

        return "\n".join(prompt_parts)


def main():
    """Example usage of structuring techniques."""
    print("Structuring and Control Techniques - Examples\n")
    print("=" * 70)

    # Example 1: Prompt Chaining
    print("\n[Example 1] Prompt Chaining for Code Analysis\n")

    chain = PromptChaining.create_analysis_chain("code")
    print(f"Chain created with {len(chain.steps)} steps:")
    for step in chain.steps:
        print(f"  - {step.step_id}")
    print()

    # Example 2: Task Decomposition
    print("=" * 70)
    print("\n[Example 2] Task Decomposition\n")

    decomp = TaskDecomposition("Migrate monolithic app to microservices")
    decomp.add_subtask(
        "analysis",
        "Analyze current monolith architecture and identify service boundaries",
        complexity="high",
        validation=["Service boundaries clearly defined", "Dependencies mapped"]
    ).add_subtask(
        "design",
        "Design microservices architecture with communication patterns",
        dependencies=["analysis"],
        complexity="high",
        validation=["Architecture documented", "Communication patterns defined"]
    ).add_subtask(
        "service_1",
        "Implement first microservice (user authentication)",
        dependencies=["design"],
        complexity="medium"
    ).add_subtask(
        "service_2",
        "Implement second microservice (user management)",
        dependencies=["design", "service_1"],
        complexity="medium"
    ).add_subtask(
        "integration",
        "Integrate all services and implement API gateway",
        dependencies=["service_1", "service_2"],
        complexity="high"
    )

    prompt = decomp.create_decomposition_prompt()
    print(prompt[:500] + "...\n")

    # Example 3: Least-to-Most Prompting
    print("=" * 70)
    print("\n[Example 3] Least-to-Most Implementation\n")

    ltm = LeastToMostPrompting("Implement complete authentication system")
    ltm.add_level(1, "Basic username/password validation").add_level(
        2, "Add password hashing and secure storage"
    ).add_level(
        3, "Implement JWT token generation and validation"
    ).add_level(
        4, "Add refresh token mechanism"
    ).add_level(
        5, "Implement multi-factor authentication (2FA)"
    )

    prompt = ltm.create_prompt()
    print(prompt[:500] + "...\n")

    # Example 4: Instruction Hierarchy
    print("=" * 70)
    print("\n[Example 4] Instruction Hierarchy\n")

    hierarchy = InstructionHierarchy("Optimize database performance for production")

    hierarchy.add_instruction(
        level=1,
        priority=Priority.CRITICAL,
        content="Maintain data integrity and consistency",
        constraints=["No data loss acceptable", "ACID compliance required"]
    ).add_instruction(
        level=1,
        priority=Priority.CRITICAL,
        content="Ensure zero downtime during optimization",
        constraints=["Rolling deployment required", "Fallback plan mandatory"]
    ).add_instruction(
        level=2,
        priority=Priority.HIGH,
        content="Reduce average query response time by 50%",
        constraints=["Baseline measurements required", "Target: <100ms for 95th percentile"]
    ).add_instruction(
        level=2,
        priority=Priority.HIGH,
        content="Implement comprehensive monitoring",
        constraints=["Real-time alerting", "Performance metrics dashboard"]
    ).add_instruction(
        level=3,
        priority=Priority.MEDIUM,
        content="Optimize top 10 slowest queries"
    ).add_instruction(
        level=4,
        priority=Priority.LOW,
        content="Document optimization decisions and rationale"
    )

    prompt = hierarchy.create_prompt()
    print(prompt)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
