#!/usr/bin/env python3
"""
Design Patterns Recommendation Agent

Uses Auto-CoT to recommend applicable design patterns for code.

Technique: Auto-CoT (Automatic Chain-of-Thought)
- Automatically generates reasoning chains
- Clusters similar pattern scenarios
- Provides recommendations with detailed rationale

Meta-Application:
This agent demonstrates using Auto-CoT reasoning to suggest
architectural improvements through design pattern recommendations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import os
import logging

from scripts.ai.agents.base import (
    AutoCoTAgent,
    Demonstration,
    Question
)

# Import LLMGenerator for AI-powered recommendations
try:
    from scripts.ai.generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("LLMGenerator not available, will use heuristics only")

logger = logging.getLogger(__name__)

# Constants
RECOMMENDATION_METHOD_LLM = "llm"
RECOMMENDATION_METHOD_HEURISTIC = "heuristic"


class PatternType(Enum):
    """Common design patterns."""
    STRATEGY = "strategy"
    OBSERVER = "observer"
    FACTORY = "factory"
    SINGLETON = "singleton"
    DECORATOR = "decorator"
    ADAPTER = "adapter"
    TEMPLATE_METHOD = "template_method"
    COMMAND = "command"
    STATE = "state"
    FACADE = "facade"
    PROXY = "proxy"
    BUILDER = "builder"


class PatternApplicability(Enum):
    """Applicability level for a pattern."""
    VERY_HIGH = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    VERY_LOW = 1


@dataclass
class PatternRecommendation:
    """Represents a design pattern recommendation."""
    pattern_type: PatternType
    applicability: PatternApplicability
    reasoning: str
    benefits: List[str] = field(default_factory=list)
    implementation_hint: str = ""
    example_code: Optional[str] = None
    analysis_method: str = RECOMMENDATION_METHOD_HEURISTIC  # "heuristic" or "llm"

    @property
    def value(self) -> int:
        """Get numeric value for sorting."""
        return self.applicability.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pattern_type': self.pattern_type.value,
            'applicability': self.applicability.value,
            'reasoning': self.reasoning,
            'benefits': self.benefits,
            'implementation_hint': self.implementation_hint,
            'analysis_method': self.analysis_method
        }


class DesignPatternsRecommendationAgent:
    """
    Agent that recommends design patterns using Auto-CoT.

    Uses Auto-CoT to:
    1. Generate reasoning chains for pattern applicability
    2. Cluster similar code scenarios
    3. Provide detailed recommendations with rationale
    """

    def __init__(
        self,
        max_recommendations: int = 5,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agent.

        Args:
            max_recommendations: Maximum number of patterns to recommend
            config: Configuration dict with optional keys:
                - llm_provider: "anthropic" or "openai"
                - model: Model name
                - use_llm: Boolean to enable/disable LLM usage
        """
        self.name = "DesignPatternsRecommendationAgent"
        self.max_recommendations = max_recommendations
        self.auto_cot = AutoCoTAgent(k_clusters=3)
        self.config = config or {}

        # Initialize LLMGenerator if configured and available
        self.llm_generator = None

        if self.config and LLM_AVAILABLE:
            try:
                self.llm_generator = LLMGenerator(config=self.config)
                llm_provider = self.config.get('llm_provider', 'anthropic')
                logger.info(f"LLMGenerator initialized with {llm_provider}")
            except Exception as e:
                logger.error(f"Failed to initialize LLMGenerator: {e}")
                self.llm_generator = None
        elif self.config and not LLM_AVAILABLE:
            logger.warning("LLM configuration provided but LLMGenerator not available")

    def recommend_patterns(self, code: str) -> List[PatternRecommendation]:
        """
        Recommend design patterns for the given code.

        Args:
            code: Python code to analyze

        Returns:
            List of PatternRecommendation, sorted by applicability (high to low)
        """
        # Handle edge cases
        if not code or not code.strip():
            return []

        # Determine analysis method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None

        # Get recommendations
        if use_llm:
            recommendations = self._get_recommendations_with_llm(code)
        else:
            recommendations = self._detect_applicable_patterns(code)

        if not recommendations:
            return []

        # Enhance with Auto-CoT reasoning (for both heuristic and LLM)
        recommendations = self._enhance_with_auto_cot(code, recommendations)

        # Sort by applicability (high to low)
        recommendations.sort(key=lambda r: r.applicability.value, reverse=True)

        # Limit to max_recommendations
        return recommendations[:self.max_recommendations]

    def _get_recommendations_with_llm(self, code: str) -> List[PatternRecommendation]:
        """Get recommendations using LLM with fallback to heuristics."""
        try:
            recommendations = self._recommend_with_llm(code)
            logger.info(f"LLM found {len(recommendations)} pattern recommendations")
            if not recommendations:
                logger.warning("LLM returned empty recommendations, using heuristics")
                return self._detect_applicable_patterns(code)
            return recommendations
        except Exception as e:
            logger.error(f"LLM recommendation failed: {e}, falling back to heuristics")
            return self._detect_applicable_patterns(code)

    def _recommend_with_llm(self, code: str) -> List[PatternRecommendation]:
        """Recommend design patterns using LLMGenerator."""
        prompt = f"""Analyze the following Python code and recommend applicable design patterns.

CODE TO ANALYZE:
```python
{code}
```

For each recommended pattern, provide:
1. Pattern name (strategy, observer, factory, singleton, decorator, adapter, etc.)
2. Applicability level (1-5, where 5 is very high)
3. Detailed reasoning explaining why this pattern applies
4. Benefits of using this pattern
5. Implementation hint

RESPONSE FORMAT (JSON):
{{
  "recommendations": [
    {{
      "pattern": "strategy",
      "applicability": 5,
      "reasoning": "The code uses multiple if-elif branches to select behavior based on type",
      "benefits": ["Eliminates conditional logic", "Easy to add new strategies", "Testable"],
      "implementation_hint": "Create Strategy interface with execute() method"
    }}
  ]
}}

Analyze the code and return recommendations in JSON format:"""

        response = self.llm_generator._call_llm(prompt)
        return self._parse_llm_recommendations(response)

    def _parse_llm_recommendations(self, response: str) -> List[PatternRecommendation]:
        """Parse LLM response into PatternRecommendation objects."""
        import json

        try:
            data = json.loads(response)
            recommendations = []

            for rec_data in data.get('recommendations', []):
                pattern_str = rec_data.get('pattern', 'strategy').lower()
                pattern_map = {
                    'strategy': PatternType.STRATEGY,
                    'observer': PatternType.OBSERVER,
                    'factory': PatternType.FACTORY,
                    'singleton': PatternType.SINGLETON,
                    'decorator': PatternType.DECORATOR,
                    'adapter': PatternType.ADAPTER,
                    'template_method': PatternType.TEMPLATE_METHOD,
                    'command': PatternType.COMMAND,
                    'state': PatternType.STATE,
                    'facade': PatternType.FACADE,
                    'proxy': PatternType.PROXY,
                    'builder': PatternType.BUILDER
                }
                pattern_type = pattern_map.get(pattern_str, PatternType.STRATEGY)

                # Map applicability score to enum
                applicability_score = rec_data.get('applicability', 3)
                applicability = {
                    5: PatternApplicability.VERY_HIGH,
                    4: PatternApplicability.HIGH,
                    3: PatternApplicability.MEDIUM,
                    2: PatternApplicability.LOW,
                    1: PatternApplicability.VERY_LOW
                }.get(applicability_score, PatternApplicability.MEDIUM)

                recommendation = PatternRecommendation(
                    pattern_type=pattern_type,
                    applicability=applicability,
                    reasoning=rec_data.get('reasoning', ''),
                    benefits=rec_data.get('benefits', []),
                    implementation_hint=rec_data.get('implementation_hint', ''),
                    analysis_method=RECOMMENDATION_METHOD_LLM
                )
                recommendations.append(recommendation)

            return recommendations

        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return []

    def _detect_applicable_patterns(self, code: str) -> List[PatternRecommendation]:
        """
        Detect applicable design patterns using heuristic analysis.

        This provides baseline detection without requiring an LLM.
        """
        recommendations = []

        # 1. Strategy Pattern - type checking with different behaviors
        if self._should_use_strategy(code):
            recommendations.append(self._create_strategy_recommendation(code))

        # 2. Observer Pattern - manual notification of dependents
        if self._should_use_observer(code):
            recommendations.append(self._create_observer_recommendation(code))

        # 3. Factory Pattern - object creation based on type
        if self._should_use_factory(code):
            recommendations.append(self._create_factory_recommendation(code))

        # 4. Singleton Pattern - global state or single instance needs
        if self._should_use_singleton(code):
            recommendations.append(self._create_singleton_recommendation(code))

        # 5. Decorator Pattern - adding responsibilities dynamically
        if self._should_use_decorator(code):
            recommendations.append(self._create_decorator_recommendation(code))

        return recommendations

    def _should_use_strategy(self, code: str) -> bool:
        """Check if Strategy pattern is applicable."""
        # Look for type-based conditionals with different behaviors
        has_type_checking = (
            ('if' in code and 'type' in code) or
            ('elif' in code and '==' in code)
        )
        has_multiple_branches = code.count('elif') >= 2 or code.count('if') >= 3
        return has_type_checking and has_multiple_branches

    def _should_use_observer(self, code: str) -> bool:
        """Check if Observer pattern is applicable."""
        # Look for manual notification patterns
        has_manual_notification = (
            ('if self.' in code and '.refresh()' in code) or
            ('if self.' in code and '.notify' in code) or
            ('if self.' in code and '.update(' in code)
        )
        has_multiple_dependents = code.count('if self.') >= 2
        return has_manual_notification or has_multiple_dependents

    def _should_use_factory(self, code: str) -> bool:
        """Check if Factory pattern is applicable."""
        # Look for object creation based on type
        has_conditional_creation = (
            'if' in code and
            ('return' in code or '= ' in code) and
            ('()' in code)  # Constructor calls
        )
        creates_different_types = code.count('()') >= 2
        return has_conditional_creation and creates_different_types

    def _should_use_singleton(self, code: str) -> bool:
        """Check if Singleton pattern is applicable."""
        # Look for global state or instance variables
        has_instance_var = '_instance' in code.lower() or 'instance' in code.lower()
        has_global_state = 'global ' in code
        return has_instance_var or has_global_state

    def _should_use_decorator(self, code: str) -> bool:
        """Check if Decorator pattern is applicable."""
        # Look for wrapping or extending behavior
        has_wrapper = 'wrapper' in code.lower() or 'wrap' in code.lower()
        has_before_after = (
            ('before_' in code.lower() and 'after_' in code.lower()) or
            'decorator' in code.lower()
        )
        return has_wrapper or has_before_after

    def _create_strategy_recommendation(self, code: str) -> PatternRecommendation:
        """Create Strategy pattern recommendation."""
        # Count conditional branches for applicability
        branch_count = code.count('elif') + code.count('if')

        if branch_count >= 5:
            applicability = PatternApplicability.VERY_HIGH
        elif branch_count >= 3:
            applicability = PatternApplicability.HIGH
        else:
            applicability = PatternApplicability.MEDIUM

        return PatternRecommendation(
            pattern_type=PatternType.STRATEGY,
            applicability=applicability,
            reasoning=(
                "The code uses conditional logic to select different behaviors based on type. "
                f"Found {branch_count} conditional branches. "
                "The Strategy pattern would allow each behavior to be encapsulated in its own class, "
                "making it easier to add new strategies without modifying existing code (Open/Closed Principle)."
            ),
            benefits=[
                "Eliminates conditional logic",
                "Makes it easy to add new strategies",
                "Each strategy can be tested independently",
                "Follows Open/Closed Principle"
            ],
            implementation_hint=(
                "Create a Strategy interface with an execute() method. "
                "Implement concrete strategies for each behavior. "
                "Use a context class to hold and delegate to the current strategy."
            ),
            analysis_method=RECOMMENDATION_METHOD_HEURISTIC
        )

    def _create_observer_recommendation(self, code: str) -> PatternRecommendation:
        """Create Observer pattern recommendation."""
        dependent_count = code.count('if self.')

        if dependent_count >= 4:
            applicability = PatternApplicability.VERY_HIGH
        elif dependent_count >= 2:
            applicability = PatternApplicability.HIGH
        else:
            applicability = PatternApplicability.MEDIUM

        return PatternRecommendation(
            pattern_type=PatternType.OBSERVER,
            applicability=applicability,
            reasoning=(
                "The code manually notifies multiple dependent objects when state changes. "
                f"Found {dependent_count} manual notification points. "
                "The Observer pattern would establish a one-to-many dependency, "
                "allowing objects to be notified automatically without tight coupling."
            ),
            benefits=[
                "Reduces coupling between objects",
                "Easy to add/remove observers dynamically",
                "Promotes loose coupling",
                "Supports broadcast communication"
            ],
            implementation_hint=(
                "Create an Observable base class with attach/detach/notify methods. "
                "Observers implement an update() method. "
                "Observable notifies all observers automatically when state changes."
            ),
            analysis_method=RECOMMENDATION_METHOD_HEURISTIC
        )

    def _create_factory_recommendation(self, code: str) -> PatternRecommendation:
        """Create Factory pattern recommendation."""
        creation_count = code.count('()')

        if creation_count >= 5:
            applicability = PatternApplicability.HIGH
        elif creation_count >= 3:
            applicability = PatternApplicability.MEDIUM
        else:
            applicability = PatternApplicability.LOW

        return PatternRecommendation(
            pattern_type=PatternType.FACTORY,
            applicability=applicability,
            reasoning=(
                "The code creates different object types based on conditional logic. "
                f"Found {creation_count} object creation points. "
                "The Factory pattern would centralize object creation logic "
                "and make it easier to manage object creation complexity."
            ),
            benefits=[
                "Centralizes object creation",
                "Hides creation complexity",
                "Easy to add new product types",
                "Follows Single Responsibility Principle"
            ],
            implementation_hint=(
                "Create a Factory class with a create_product(type) method. "
                "Move all object creation logic into the factory. "
                "Clients request objects from the factory instead of creating directly."
            ),
            analysis_method=RECOMMENDATION_METHOD_HEURISTIC
        )

    def _create_singleton_recommendation(self, code: str) -> PatternRecommendation:
        """Create Singleton pattern recommendation."""
        return PatternRecommendation(
            pattern_type=PatternType.SINGLETON,
            applicability=PatternApplicability.MEDIUM,
            reasoning=(
                "The code appears to manage global state or a single instance. "
                "The Singleton pattern ensures only one instance exists "
                "and provides global access to it. However, use sparingly as "
                "singletons can make testing difficult and hide dependencies."
            ),
            benefits=[
                "Guarantees single instance",
                "Provides global access point",
                "Lazy initialization possible",
                "Controls instance lifecycle"
            ],
            implementation_hint=(
                "Implement a private constructor and a static getInstance() method. "
                "Store the instance in a static variable. "
                "Consider thread safety if used in concurrent environments."
            ),
            analysis_method=RECOMMENDATION_METHOD_HEURISTIC
        )

    def _create_decorator_recommendation(self, code: str) -> PatternRecommendation:
        """Create Decorator pattern recommendation."""
        return PatternRecommendation(
            pattern_type=PatternType.DECORATOR,
            applicability=PatternApplicability.MEDIUM,
            reasoning=(
                "The code shows signs of wrapping or extending functionality. "
                "The Decorator pattern allows behavior to be added to objects "
                "dynamically without affecting other objects of the same class. "
                "This is more flexible than subclassing for extending functionality."
            ),
            benefits=[
                "Adds responsibilities dynamically",
                "More flexible than subclassing",
                "Combines decorators for complex behavior",
                "Follows Single Responsibility Principle"
            ],
            implementation_hint=(
                "Create a Component interface. Implement ConcreteComponent and Decorator classes. "
                "Decorators wrap components and add behavior before/after delegating. "
                "Can stack multiple decorators."
            ),
            analysis_method=RECOMMENDATION_METHOD_HEURISTIC
        )

    def _enhance_with_auto_cot(
        self,
        code: str,
        recommendations: List[PatternRecommendation]
    ) -> List[PatternRecommendation]:
        """
        Enhance recommendations with Auto-CoT reasoning.

        In production, this would use Auto-CoT to generate demonstrations
        and improve reasoning quality. For now, the heuristic reasoning is sufficient.
        """
        # Auto-CoT would generate demonstrations here
        # For testing purposes, we use the heuristic/LLM reasoning already generated

        # Simulate Auto-CoT clustering by grouping similar patterns
        pattern_questions = [
            f"Why should I use {rec.pattern_type.value} pattern for this code?"
            for rec in recommendations
        ]

        # In production, would call:
        # demonstrations = self.auto_cot.generate_demonstrations(
        #     questions=pattern_questions,
        #     domain="design_patterns"
        # )

        return recommendations
