"""
Validators for plan dependencies and completeness.

Implements RF-011 scenarios 11-16 (Dependency and Completeness Validation).
"""

from dataclasses import dataclass
from typing import Dict, List, Set

from .models import Goal, GoalType, Plan


@dataclass
class ValidationResult:
    """Result of validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class CompletenessResult:
    """Result of completeness validation."""

    is_complete: bool
    completeness_score: float
    missing_categories: List[str]


class DependencyValidator:
    """Validate task dependencies in plans."""

    def validate_dependencies(self, plan: Plan) -> ValidationResult:
        """
        Validate all dependencies in plan.

        Checks for:
        - Circular dependencies
        - Dangling dependencies (non-existent tasks)
        - Transitive dependencies (warnings only)

        Args:
            plan: Plan to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Check dangling dependencies (already done by Pydantic, but explicit here)
        task_ids = {task.task_id for task in plan.subtasks}
        for task in plan.subtasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(
                        f"Dependencies reference non-existent tasks: [('{task.task_id}', '{dep_id}')]"
                    )

        # Check circular dependencies (already done by Pydantic validator)
        if self._has_circular_dependency(plan):
            errors.append("Circular dependencies detected")

        # Check transitive dependencies (warning only)
        transitive_deps = self._find_transitive_dependencies(plan)
        if transitive_deps:
            for task_id, redundant_dep in transitive_deps:
                warnings.append(
                    f"Potentially unnecessary dependencies: [('{task_id}', '{redundant_dep}')]"
                )

        # Check missing dependencies based on data flow
        missing_deps = self._find_missing_dependencies(plan)
        if missing_deps:
            for task_id, should_depend_on in missing_deps:
                warnings.append(
                    f"Potentially missing dependencies: [('{task_id}', '{should_depend_on}')]"
                )

        is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def _has_circular_dependency(self, plan: Plan) -> bool:
        """Check for circular dependencies using DFS."""
        task_map = {task.task_id: task for task in plan.subtasks}

        def has_cycle(task_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = task_map.get(task_id)
            if task:
                for dep_id in task.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        visited: Set[str] = set()
        for task in plan.subtasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id, visited, set()):
                    return True

        return False

    def _find_transitive_dependencies(self, plan: Plan) -> List[tuple]:
        """Find transitive dependencies that could be removed."""
        transitive = []
        task_map = {task.task_id: task for task in plan.subtasks}

        for task in plan.subtasks:
            # For each dependency, check if it's reachable through another dependency
            for dep_id in task.dependencies:
                for other_dep_id in task.dependencies:
                    if dep_id != other_dep_id:
                        # Check if dep_id is reachable from other_dep_id
                        if self._is_reachable(task_map, other_dep_id, dep_id):
                            transitive.append((task.task_id, dep_id))
                            break

        return transitive

    def _is_reachable(
        self, task_map: Dict, start_id: str, target_id: str, visited: Set[str] = None
    ) -> bool:
        """Check if target_id is reachable from start_id through dependencies."""
        if visited is None:
            visited = set()

        if start_id == target_id:
            return True

        if start_id in visited:
            return False

        visited.add(start_id)

        start_task = task_map.get(start_id)
        if not start_task:
            return False

        for dep_id in start_task.dependencies:
            if self._is_reachable(task_map, dep_id, target_id, visited):
                return True

        return False

    def _find_missing_dependencies(self, plan: Plan) -> List[tuple]:
        """Find potentially missing dependencies based on data flow."""
        missing = []
        task_map = {task.task_id: task for task in plan.subtasks}

        for task in plan.subtasks:
            # Check if task inputs reference outputs from other tasks
            for input_key, input_value in task.inputs.items():
                if isinstance(input_value, str) and "from " in input_value:
                    # Extract referenced output (e.g., "from flight_dates")
                    ref_output = input_value.replace("from ", "").strip()

                    # Find which task produces this output
                    for other_task in plan.subtasks:
                        if other_task.task_id != task.task_id:
                            if ref_output in other_task.expected_outputs:
                                # Check if dependency is declared
                                if other_task.task_id not in task.dependencies:
                                    missing.append((task.task_id, other_task.task_id))

        return missing


class CompletenessValidator:
    """Validate plan completeness against goal requirements."""

    def __init__(self, goal_templates: Dict[GoalType, List[str]] = None):
        """
        Initialize validator with goal templates.

        Args:
            goal_templates: Map of goal types to required task categories
        """
        self.goal_templates = goal_templates or self._default_templates()

    def _default_templates(self) -> Dict[GoalType, List[str]]:
        """Default templates for required task categories."""
        return {
            GoalType.TRAVEL_PLANNING: [
                "flight_booking",
                "hotel_booking",
                "activity_planning",
                "budget_validation"
            ],
            GoalType.DATA_ANALYSIS: [
                "data_loading",
                "data_cleaning",
                "analysis",
                "visualization",
                "reporting"
            ],
            GoalType.RESEARCH: [
                "source_gathering",
                "analysis",
                "synthesis"
            ]
        }

    def validate_completeness(self, plan: Plan, goal: Goal) -> CompletenessResult:
        """
        Validate plan completeness.

        Args:
            plan: Plan to validate
            goal: Original goal

        Returns:
            CompletenessResult with score and missing categories
        """
        required_categories = self.goal_templates.get(goal.goal_type, [])
        if not required_categories:
            # No template for this goal type
            return CompletenessResult(
                is_complete=True,
                completeness_score=1.0,
                missing_categories=[]
            )

        # Check which categories are present
        present_categories = self._identify_categories(plan)

        # Find missing categories
        missing = []
        for category in required_categories:
            if not self._has_category(category, present_categories):
                missing.append(category)

        # Calculate score
        categories_present = len(required_categories) - len(missing)
        completeness_score = categories_present / len(required_categories)

        is_complete = completeness_score >= 0.95

        return CompletenessResult(
            is_complete=is_complete,
            completeness_score=completeness_score,
            missing_categories=missing
        )

    def _identify_categories(self, plan: Plan) -> Set[str]:
        """Identify categories present in plan based on task descriptions."""
        categories = set()

        for task in plan.subtasks:
            desc_lower = task.description.lower()

            # Flight booking
            if "flight" in desc_lower:
                categories.add("flight_booking")

            # Hotel booking
            if "hotel" in desc_lower:
                categories.add("hotel_booking")

            # Activity planning
            if "activ" in desc_lower:
                categories.add("activity_planning")

            # Budget validation
            if "budget" in desc_lower or "validat" in desc_lower:
                categories.add("budget_validation")

            # Data loading
            if "load" in desc_lower and "data" in desc_lower:
                categories.add("data_loading")

            # Data cleaning
            if "clean" in desc_lower:
                categories.add("data_cleaning")

            # Analysis
            if "analyz" in desc_lower or "trend" in desc_lower:
                categories.add("analysis")

            # Visualization
            if "visual" in desc_lower or "chart" in desc_lower:
                categories.add("visualization")

            # Reporting
            if "report" in desc_lower:
                categories.add("reporting")

            # Source gathering
            if "gather" in desc_lower or "source" in desc_lower:
                categories.add("source_gathering")

            # Synthesis
            if "synth" in desc_lower:
                categories.add("synthesis")

        return categories

    def _has_category(self, category: str, present_categories: Set[str]) -> bool:
        """Check if category is present."""
        return category in present_categories


# Template for goal requirements
GOAL_TEMPLATES = {
    GoalType.TRAVEL_PLANNING: [
        "flight_booking",
        "hotel_booking",
        "activity_planning",
        "budget_validation"
    ],
    GoalType.DATA_ANALYSIS: [
        "data_loading",
        "data_cleaning",
        "analysis",
        "visualization",
        "reporting"
    ]
}
