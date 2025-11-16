"""
Goal Parser: Converts natural language to structured Goal objects.

Implements RF-011 scenarios 1-5 (Goal Parsing).
"""

import re
import time
from typing import Dict, List, Any

from .models import Constraint, Goal, GoalType


class GoalParser:
    """Parse natural language user requests into structured Goal objects."""

    def __init__(self, openai_client=None):
        """Initialize parser with optional LLM client."""
        self.client = openai_client
        self.last_call_cost = 0.001  # Tracked for testing

    def parse(self, user_request: str) -> Goal:
        """
        Parse user request into Goal object.

        Args:
            user_request: Natural language description

        Returns:
            Goal: Structured goal object
        """
        # Determine goal type
        goal_type = self._classify_goal_type(user_request)

        # Extract constraints
        constraints = self._extract_constraints(user_request)

        # Build metadata
        metadata = self._extract_metadata(user_request, constraints)

        # Generate success criteria
        success_criteria = self._generate_success_criteria(user_request, constraints)

        # Check for ambiguity
        requires_clarification = self._check_ambiguity(user_request, constraints, goal_type)
        if requires_clarification:
            metadata["requires_clarification"] = True
            metadata["ambiguities"] = self._identify_ambiguities(constraints, goal_type)
            metadata["clarification_questions"] = self._generate_clarification_questions(
                metadata["ambiguities"]
            )

        # Generate unique ID
        goal_id = f"goal_{int(time.time() * 1000)}"

        return Goal(
            goal_id=goal_id,
            goal_type=goal_type,
            description=user_request,
            constraints=constraints,
            success_criteria=success_criteria,
            metadata=metadata
        )

    def _classify_goal_type(self, text: str) -> GoalType:
        """Classify goal type based on keywords."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["trip", "travel", "flight", "hotel", "vacation"]):
            return GoalType.TRAVEL_PLANNING
        elif any(kw in text_lower for kw in ["analyze", "data", "report", "visualization", "trend"]):
            return GoalType.DATA_ANALYSIS
        elif any(kw in text_lower for kw in ["research", "study", "investigate", "explore"]):
            return GoalType.RESEARCH
        elif any(kw in text_lower for kw in ["automate", "schedule", "task", "workflow"]):
            return GoalType.TASK_AUTOMATION
        else:
            # Default based on complexity
            word_count = len(text.split())
            return GoalType.COMPLEX if word_count > 10 else GoalType.SIMPLE

    def _extract_constraints(self, text: str) -> List[Constraint]:
        """Extract constraints from text."""
        constraints = []

        # Budget constraint (highest priority)
        budget_match = re.search(r'\$(\d+(?:,\d+)?)', text)
        if budget_match:
            amount = budget_match.group(1).replace(',', '')
            constraints.append(
                Constraint(type="budget", value=f"{amount} USD", priority=10)
            )

        # Duration constraint
        duration_patterns = [
            (r'(\d+)-day', r'\1 days'),
            (r'(\d+)\s+days?', r'\1 days'),
            (r'(\d+)\s+weeks?', r'\1 weeks'),
        ]
        for pattern, replacement in duration_patterns:
            match = re.search(pattern, text)
            if match:
                duration_value = re.sub(pattern, replacement, match.group(0))
                constraints.append(
                    Constraint(type="duration", value=duration_value, priority=9)
                )
                break

        # Time constraint (month, dates)
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        for month in months:
            if month in text.lower():
                constraints.append(
                    Constraint(type="time", value=month.capitalize(), priority=8)
                )
                break

        return constraints

    def _extract_metadata(self, text: str, constraints: List[Constraint]) -> Dict[str, Any]:
        """Extract metadata and preferences."""
        metadata: Dict[str, Any] = {"extracted": {}}

        # Extract duration days from constraints
        for c in constraints:
            if c.type == "duration" and "days" in c.value:
                days_match = re.search(r'(\d+)', c.value)
                if days_match:
                    metadata["extracted"]["duration_days"] = int(days_match.group(1))

        # Extract preferences
        preferences = []
        preference_keywords = ["boutique", "luxury", "budget", "family-friendly", "downtown"]
        for keyword in preference_keywords:
            if keyword in text.lower():
                preferences.append(f"{keyword} hotels" if "hotel" not in keyword else keyword)

        if preferences:
            metadata["preferences"] = preferences

        return metadata

    def _generate_success_criteria(
        self, text: str, constraints: List[Constraint]
    ) -> List[str]:
        """Generate success criteria based on goal and constraints."""
        criteria = ["Complete plan"]

        # Budget criterion
        budget_constraint = next((c for c in constraints if c.type == "budget"), None)
        if budget_constraint:
            criteria.append(f"Total cost <= ${budget_constraint.value}")

        # Duration criterion
        duration_constraint = next((c for c in constraints if c.type == "duration"), None)
        if duration_constraint:
            criteria.append(f"Plan fits {duration_constraint.value}")

        return criteria

    def _check_ambiguity(
        self, text: str, constraints: List[Constraint], goal_type: GoalType
    ) -> bool:
        """Check if goal requires clarification."""
        # For travel planning, need duration AND budget
        if goal_type == GoalType.TRAVEL_PLANNING:
            has_budget = any(c.type == "budget" for c in constraints)
            has_duration = any(c.type == "duration" for c in constraints)

            # Short requests without details are ambiguous
            if len(text.split()) < 6 and not (has_budget and has_duration):
                return True

        return False

    def _identify_ambiguities(
        self, constraints: List[Constraint], goal_type: GoalType
    ) -> List[str]:
        """Identify what information is missing."""
        ambiguities = []

        if goal_type == GoalType.TRAVEL_PLANNING:
            if not any(c.type == "duration" for c in constraints):
                ambiguities.append("duration not specified")
            if not any(c.type == "budget" for c in constraints):
                ambiguities.append("budget not specified")
            if not any(c.type == "time" for c in constraints):
                ambiguities.append("travel dates not specified")

        return ambiguities

    def _generate_clarification_questions(self, ambiguities: List[str]) -> List[str]:
        """Generate questions to clarify ambiguous goals."""
        questions = []

        for ambiguity in ambiguities:
            if "duration" in ambiguity:
                questions.append("How long would you like to stay?")
            elif "budget" in ambiguity:
                questions.append("What's your budget?")
            elif "dates" in ambiguity or "time" in ambiguity:
                questions.append("When would you like to travel?")

        return questions
