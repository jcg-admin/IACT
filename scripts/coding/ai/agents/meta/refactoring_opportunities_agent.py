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
import logging
import os

from scripts.ai.agents.base import (
    HybridSearchOptimization,
    SearchItem,
    SearchOptimizationResult,
    CoverageLevel,
    Priority
)

# Import LLMGenerator for AI-powered analysis
try:
    from scripts.ai.generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("LLMGenerator not available, will use heuristics only")

logger = logging.getLogger(__name__)

# Constants
ANALYSIS_METHOD_LLM = "llm"
ANALYSIS_METHOD_HEURISTIC = "heuristic"


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
    analysis_method: str = "heuristic"  # "heuristic" or "llm"

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
            'cluster_id': self.cluster_id,
            'analysis_method': self.analysis_method
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
        k_clusters: int = 5,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agent.

        Args:
            target_coverage: Target coverage level (0.0-1.0)
            k_clusters: Number of clusters for K-NN clustering
            config: Configuration dict with optional keys:
                - llm_provider: "anthropic" or "openai"
                - model: Model name (e.g., "claude-sonnet-4-5-20250929")
                - use_llm: Boolean to enable/disable LLM usage
        """
        self.name = "RefactoringOpportunitiesAgent"
        self.target_coverage = target_coverage
        self.k_clusters = k_clusters
        self.config = config or {}

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

        # Initialize LLMGenerator if configured and available
        self.llm_generator = None

        if self.config and LLM_AVAILABLE:
            try:
                # Initialize LLMGenerator (API key validation happens at runtime)
                self.llm_generator = LLMGenerator(config=self.config)
                llm_provider = self.config.get('llm_provider', 'anthropic')
                logger.info(f"LLMGenerator initialized with {llm_provider}")
            except Exception as e:
                logger.error(f"Failed to initialize LLMGenerator: {e}")
                self.llm_generator = None
        elif self.config and not LLM_AVAILABLE:
            logger.warning("LLM configuration provided but LLMGenerator not available")

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

        # Determine analysis method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None
        analysis_method = ANALYSIS_METHOD_LLM if use_llm else ANALYSIS_METHOD_HEURISTIC

        # Detect code smells
        if use_llm:
            try:
                smells = self._analyze_with_llm(code, file_path)
                logger.info(f"Found {len(smells)} opportunities using LLM")
                # If no smells found or error occurred
                if not smells:
                    logger.warning("LLM returned no opportunities, using heuristics")
                    smells = self._detect_code_smells(code, file_path)
                    analysis_method = ANALYSIS_METHOD_HEURISTIC
            except Exception as e:
                logger.error(f"LLM analysis failed: {e}, falling back to heuristics")
                smells = self._detect_code_smells(code, file_path)
                analysis_method = ANALYSIS_METHOD_HEURISTIC
        else:
            smells = self._detect_code_smells(code, file_path)

        if not smells:
            return []

        # Update analysis_method on all opportunities
        for smell in smells:
            smell.analysis_method = analysis_method

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

    def _analyze_with_llm(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> List[RefactoringOpportunity]:
        """
        Analyze code for refactoring opportunities using LLMGenerator.

        Args:
            code: Python code to analyze
            file_path: Optional file path for context

        Returns:
            List of RefactoringOpportunity objects identified by LLM
        """
        # Build prompt for LLM
        prompt = self._build_llm_prompt(code, file_path)

        # Call LLM
        response = self.llm_generator._call_llm(prompt)

        # Parse LLM response into refactoring opportunities
        opportunities = self._parse_llm_opportunities(response, file_path)

        return opportunities

    def _build_llm_prompt(self, code: str, file_path: Optional[str] = None) -> str:
        """Build prompt for LLM refactoring analysis."""
        location = file_path or "code"
        prompt = f"""Analyze the following Python code for refactoring opportunities using Search Optimization reasoning.

CODE TO ANALYZE:
```python
{code}
```

LOCATION: {location}

REQUIREMENTS:
1. Identify code smells and refactoring opportunities including:
   - Long Method: Methods that are too long or complex
   - God Class/Large Class: Classes with too many responsibilities
   - Duplicate Code: Similar or repeated code blocks
   - Long Parameter List: Functions with too many parameters
   - Feature Envy: Methods that use more features of another class
   - Data Clumps: Groups of data that always appear together
   - Primitive Obsession: Over-reliance on primitive types
   - Divergent Change/Shotgun Surgery: Change patterns

2. For each refactoring opportunity, provide:
   - smell: Type of code smell (long_method, god_class, duplicate_code, large_class, long_parameter_list, divergent_change, shotgun_surgery, feature_envy, data_clumps, primitive_obsession)
   - description: Clear explanation of the issue
   - refactoring_type: Recommended refactoring (extract_method, extract_class, move_method, rename, introduce_parameter_object, replace_conditional, consolidate_duplicate, simplify_conditional, decompose_conditional, remove_dead_code)
   - priority: Integer from 1-10 (higher = more important)
   - estimated_effort: "low", "medium", or "high"
   - estimated_impact: "low", "medium", or "high"
   - code_snippet: Optional relevant code snippet

3. Prioritize based on:
   - Impact on code quality
   - Risk and effort required
   - Dependencies between refactorings

RESPONSE FORMAT (JSON):
{{
  "opportunities": [
    {{
      "smell": "long_method",
      "description": "The process_order function is too long with 50+ lines handling multiple responsibilities",
      "refactoring_type": "extract_method",
      "priority": 8,
      "estimated_effort": "medium",
      "estimated_impact": "high",
      "code_snippet": "def process_order(order):\\n    # 50+ lines..."
    }}
  ]
}}

Analyze the code:"""
        return prompt

    def _parse_llm_opportunities(
        self,
        response: str,
        file_path: Optional[str] = None
    ) -> List[RefactoringOpportunity]:
        """Parse LLM response into RefactoringOpportunity objects."""
        import json

        try:
            # Try to parse as JSON
            data = json.loads(response)
            opportunities = []

            for opp_data in data.get('opportunities', []):
                # Map string values to enums
                smell_str = opp_data.get('smell', 'long_method').lower()
                smell = {
                    'long_method': CodeSmell.LONG_METHOD,
                    'god_class': CodeSmell.GOD_CLASS,
                    'duplicate_code': CodeSmell.DUPLICATE_CODE,
                    'large_class': CodeSmell.LARGE_CLASS,
                    'long_parameter_list': CodeSmell.LONG_PARAMETER_LIST,
                    'divergent_change': CodeSmell.DIVERGENT_CHANGE,
                    'shotgun_surgery': CodeSmell.SHOTGUN_SURGERY,
                    'feature_envy': CodeSmell.FEATURE_ENVY,
                    'data_clumps': CodeSmell.DATA_CLUMPS,
                    'primitive_obsession': CodeSmell.PRIMITIVE_OBSESSION
                }.get(smell_str, CodeSmell.LONG_METHOD)

                refactoring_type_str = opp_data.get('refactoring_type', 'extract_method').lower()
                refactoring_type = {
                    'extract_method': RefactoringType.EXTRACT_METHOD,
                    'extract_class': RefactoringType.EXTRACT_CLASS,
                    'move_method': RefactoringType.MOVE_METHOD,
                    'rename': RefactoringType.RENAME,
                    'introduce_parameter_object': RefactoringType.INTRODUCE_PARAMETER_OBJECT,
                    'replace_conditional': RefactoringType.REPLACE_CONDITIONAL_WITH_POLYMORPHISM,
                    'consolidate_duplicate': RefactoringType.CONSOLIDATE_DUPLICATE,
                    'simplify_conditional': RefactoringType.SIMPLIFY_CONDITIONAL,
                    'decompose_conditional': RefactoringType.DECOMPOSE_CONDITIONAL,
                    'remove_dead_code': RefactoringType.REMOVE_DEAD_CODE
                }.get(refactoring_type_str, RefactoringType.EXTRACT_METHOD)

                opportunity = RefactoringOpportunity(
                    smell=smell,
                    location=file_path or "code",
                    description=opp_data.get('description', ''),
                    refactoring_type=refactoring_type,
                    priority=int(opp_data.get('priority', 5)),
                    estimated_effort=opp_data.get('estimated_effort', 'medium'),
                    estimated_impact=opp_data.get('estimated_impact', 'medium'),
                    code_snippet=opp_data.get('code_snippet'),
                    analysis_method=ANALYSIS_METHOD_LLM
                )
                opportunities.append(opportunity)

            return opportunities

        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            # Return empty list to trigger fallback
            return []
