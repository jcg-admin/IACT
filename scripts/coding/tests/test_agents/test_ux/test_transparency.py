"""Tests for UX Transparency"""
from scripts.coding.ai.agents.ux.transparency import TransparencyEnforcer
from scripts.coding.ai.agents.planning.models import Plan, SubTask, Goal, GoalType

def test_disclose_plan():
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    plan = Plan(plan_id="p1", goal_id="g1", subtasks=[], execution_strategy="sequential",
                estimated_total_duration=10, confidence_score=0.8)

    result = enforcer.disclose_plan(plan)
    assert result["disclosed"] is True
    assert result["confidence"] == 0.8
