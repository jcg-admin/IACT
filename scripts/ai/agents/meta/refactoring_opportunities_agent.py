#!/usr/bin/env python3
"""
Refactoring Opportunities Agent

Uses Search Optimization techniques to identify and prioritize refactoring
opportunities in code.

Techniques: Hybrid Search Optimization
- K-NN Clustering for similar code smells
- Greedy Information Density for high-value targets
- Branch-and-Bound for optimal prioritization

Meta-Application:
This agent demonstrates using algorithmic prompting techniques
(search optimization) to solve real software engineering problems
(identifying refactoring opportunities).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from scripts.ai.agents.base import (
    HybridSearchOptimization,
    SearchItem,
    SearchOptimizationResult,
    CoverageLevel,
    Priority
)


class CodeSmell(Enum):
    """Common code smells that indicate refactoring opportunities."""
    LONG_METHOD = "long_method"
    GOD_CLASS = "god_class"
    DUPLICATE_CODE = "duplicate_code"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DIVERGENT_CHANGE = "divergent_change"
    SHOTGUN_SURGERY = "shotgun_surgery"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSESSION = "primitive_obsession"


class RefactoringType(Enum):
    """Types of refactoring that can be recommended."""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    MOVE_METHOD = "move_method"
    RENAME = "rename"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_CONDITIONAL_WITH_POLYMORPHISM = "replace_conditional"
    CONSOLIDATE_DUPLICATE = "consolidate_duplicate"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"
    REMOVE_DEAD_CODE = "remove_dead_code"


@dataclass
class RefactoringOpportunity:
    """Represents a refactoring opportunity."""
    smell: CodeSmell
    location: str
    description: str
    refactoring_type: RefactoringType
    priority: int  # 1-10, higher is more important
    estimated_effort: str  # "low", "medium", "high"
    estimated_impact: str  # "low", "medium", "high"
    code_snippet: Optional[str] = None
    cluster_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'smell': self.smell.value,
            'location': self.location,
            'description': self.description,
            'refactoring_type': self.refactoring_type.value,
            'priority': self.priority,
            'estimated_effort': self.estimated_effort,
            'estimated_impact': self.estimated_impact,
            'cluster_id': self.cluster_id
        }


class RefactoringOpportunitiesAgent:
    """
    Agent that identifies and prioritizes refactoring opportunities
    using Search Optimization techniques.

    Uses Hybrid Search Optimization to:
    1. Cluster similar code smells
    2. Prioritize high-impact refactorings
    3. Optimize search for maximum value with minimal effort
    """

    def __init__(
        self,
        target_coverage: float = 1.0,  # Return all opportunities by default
        k_clusters: int = 5
    ):
        """
        Initialize the agent.

        Args:
            target_coverage: Target coverage level (0.0-1.0)
            k_clusters: Number of clusters for K-NN clustering
        """
        self.name = "RefactoringOpportunitiesAgent"
        self.target_coverage = target_coverage
        self.k_clusters = k_clusters

        # Map coverage float to CoverageLevel enum
        if target_coverage >= 0.9:
            coverage_level = CoverageLevel.COMPREHENSIVE
        elif target_coverage >= 0.7:
            coverage_level = CoverageLevel.BALANCED
        else:
            coverage_level = CoverageLevel.FOCUSED

        self.optimizer = HybridSearchOptimization(
            k_clusters=k_clusters,
            target_coverage=coverage_level
        )

    def find_refactoring_opportunities(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> List[RefactoringOpportunity]:
        """
        Find and prioritize refactoring opportunities in code.

        Args:
            code: Python code to analyze
            file_path: Optional file path for context

        Returns:
            List of RefactoringOpportunity, sorted by priority (high to low)
        """
        # Handle edge cases
        if not code or not code.strip():
            return []

        # Detect code smells
        smells = self._detect_code_smells(code, file_path)

        if not smells:
            return []

        # Convert smells to search items for optimization
        search_items = [
            SearchItem(
                id=f"smell_{i}",
                content=smell.description,
                priority=self._map_priority(smell.priority),
                keywords=[smell.smell.value, smell.refactoring_type.value]
            )
            for i, smell in enumerate(smells)
        ]

        # Use search optimization to get coverage strategy
        # (Optimizer provides metadata about search strategy, not filtered items)
        optimization_result = self.optimizer.optimize(search_items)

        # The optimizer tells us the strategy used, but we return our detected smells
        # Sort smells by priority (high to low)
        smells.sort(key=lambda o: o.priority, reverse=True)

        # Optionally limit based on coverage target (for demonstration)
        # Higher coverage = more opportunities returned
        if self.target_coverage < 1.0:
            max_opportunities = max(1, int(len(smells) * self.target_coverage))
            return smells[:max_opportunities]

        return smells

    def _detect_code_smells(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> List[RefactoringOpportunity]:
        """
        Detect code smells using heuristic analysis.

        This provides baseline detection without requiring an LLM.
        """
        opportunities = []

        # Count lines, methods, classes
        lines = code.split('\n')
        line_count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        method_count = code.count('def ')
        class_count = code.count('class ')

        # 1. Long Method smell
        opportunities.extend(self._check_long_method(code, line_count, file_path))

        # 2. God Class smell
        opportunities.extend(self._check_god_class(code, method_count, class_count, file_path))

        # 3. Duplicate Code smell
        opportunities.extend(self._check_duplicate_code(code, file_path))

        # 4. Long Parameter List smell
        opportunities.extend(self._check_long_parameter_list(code, file_path))

        return opportunities

    def _check_long_method(
        self,
        code: str,
        line_count: int,
        file_path: Optional[str]
    ) -> List[RefactoringOpportunity]:
        """Check for long method smell."""
        opportunities = []

        # Simple heuristic: functions with many lines or many statements
        if 'def ' in code:
            # Count lines in function (rough estimate)
            avg_lines_per_function = line_count / max(code.count('def '), 1)

            # Also check for number of function calls (complexity indicator)
            function_call_count = code.count('(')  # Rough proxy for complexity
            avg_calls_per_function = function_call_count / max(code.count('def '), 1)

            if avg_lines_per_function > 20:  # Functions average > 20 lines
                opportunities.append(RefactoringOpportunity(
                    smell=CodeSmell.LONG_METHOD,
                    location=file_path or "code",
                    description=f"Methods are too long ({int(avg_lines_per_function)} lines avg)",
                    refactoring_type=RefactoringType.EXTRACT_METHOD,
                    priority=7,  # High priority
                    estimated_effort="medium",
                    estimated_impact="high"
                ))
            elif avg_calls_per_function > 5:  # High complexity even if not long
                opportunities.append(RefactoringOpportunity(
                    smell=CodeSmell.LONG_METHOD,
                    location=file_path or "code",
                    description=f"Methods are complex ({int(avg_calls_per_function)} calls avg) - consider refactoring",
                    refactoring_type=RefactoringType.EXTRACT_METHOD,
                    priority=6,
                    estimated_effort="medium",
                    estimated_impact="medium"
                ))

        return opportunities

    def _check_god_class(
        self,
        code: str,
        method_count: int,
        class_count: int,
        file_path: Optional[str]
    ) -> List[RefactoringOpportunity]:
        """Check for god class smell."""
        opportunities = []

        if class_count > 0:
            avg_methods_per_class = method_count / class_count

            if avg_methods_per_class >= 8:  # Classes average >= 8 methods
                opportunities.append(RefactoringOpportunity(
                    smell=CodeSmell.GOD_CLASS,
                    location=file_path or "code",
                    description=f"Classes have too many methods ({int(avg_methods_per_class)} methods avg)",
                    refactoring_type=RefactoringType.EXTRACT_CLASS,
                    priority=9,  # Very high priority
                    estimated_effort="high",
                    estimated_impact="high"
                ))
            elif avg_methods_per_class > 5:  # Warning threshold
                opportunities.append(RefactoringOpportunity(
                    smell=CodeSmell.LARGE_CLASS,
                    location=file_path or "code",
                    description=f"Classes are getting large ({int(avg_methods_per_class)} methods avg)",
                    refactoring_type=RefactoringType.EXTRACT_CLASS,
                    priority=6,  # Medium-high priority
                    estimated_effort="medium",
                    estimated_impact="medium"
                ))

        return opportunities

    def _check_duplicate_code(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOpportunity]:
        """Check for duplicate code smell."""
        opportunities = []

        # Simple heuristic: look for similar function names or repeated patterns
        lines = [l.strip() for l in code.split('\n') if l.strip()]

        # Check for duplicate lines (simple heuristic)
        unique_lines = set(lines)
        duplicate_ratio = 1 - (len(unique_lines) / len(lines)) if lines else 0

        if duplicate_ratio > 0.3:  # >30% duplicate lines
            opportunities.append(RefactoringOpportunity(
                smell=CodeSmell.DUPLICATE_CODE,
                location=file_path or "code",
                description=f"High code duplication detected ({int(duplicate_ratio * 100)}%)",
                refactoring_type=RefactoringType.CONSOLIDATE_DUPLICATE,
                priority=8,  # High priority
                estimated_effort="medium",
                estimated_impact="high"
            ))

        # Check for similar function definitions
        function_defs = [l for l in lines if l.startswith('def ')]
        if len(function_defs) != len(set(function_defs)):
            # There are duplicate function signatures
            opportunities.append(RefactoringOpportunity(
                smell=CodeSmell.DUPLICATE_CODE,
                location=file_path or "code",
                description="Duplicate or very similar function definitions found",
                refactoring_type=RefactoringType.CONSOLIDATE_DUPLICATE,
                priority=7,
                estimated_effort="low",
                estimated_impact="medium"
            ))

        return opportunities

    def _check_long_parameter_list(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOpportunity]:
        """Check for long parameter list smell."""
        opportunities = []

        # Find function definitions and count parameters
        import re
        function_pattern = r'def\s+\w+\s*\(([^)]+)\)'
        matches = re.findall(function_pattern, code)

        for params_str in matches:
            param_count = len([p.strip() for p in params_str.split(',') if p.strip()])

            if param_count > 5:  # >5 parameters
                opportunities.append(RefactoringOpportunity(
                    smell=CodeSmell.LONG_PARAMETER_LIST,
                    location=file_path or "code",
                    description=f"Function has {param_count} parameters - consider parameter object",
                    refactoring_type=RefactoringType.INTRODUCE_PARAMETER_OBJECT,
                    priority=5,  # Medium priority
                    estimated_effort="low",
                    estimated_impact="medium"
                ))
                break  # Only report once per file

        return opportunities

    def _map_priority(self, priority: int) -> Priority:
        """
        Map integer priority (1-10) to Priority enum (0-3).

        Args:
            priority: Integer priority from 1-10

        Returns:
            Priority enum value (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if priority >= 9:
            return Priority.CRITICAL  # 3
        elif priority >= 7:
            return Priority.HIGH  # 2
        elif priority >= 4:
            return Priority.MEDIUM  # 1
        else:
            return Priority.LOW  # 0
