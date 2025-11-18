"""Complete UX Tests (20 tests total) - RF-016"""
import pytest
from scripts.coding.ai.agents.ux.transparency import TransparencyEnforcer
from scripts.coding.ai.agents.ux.control import ApprovalGateEnforcer
from scripts.coding.ai.agents.ux.consistency import ConsistencyGuard
from scripts.coding.ai.agents.planning.models import Plan, SubTask, Goal, GoalType

# Test 1 already exists in test_transparency.py

class MockAction:
    def __init__(self, action_type, amount=0):
        self.type = action_type
        self.amount = amount

def test_provide_explanation():
    """UX Test 2: Provide explanation for actions"""
    enforcer = TransparencyEnforcer()
    explanation = enforcer.provide_explanation("book_flight", "User requested Paris trip")
    assert "book_flight" in explanation
    assert "Paris" in explanation

def test_disclose_confidence_score():
    """UX Test 3: Disclose confidence score"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    plan = Plan(plan_id="p1", goal_id="g1", subtasks=[], execution_strategy="sequential",
                estimated_total_duration=10, confidence_score=0.75)

    result = enforcer.disclose_plan(plan)
    assert result["confidence"] == 0.75

def test_disclose_subtasks_count():
    """UX Test 4: Disclose number of subtasks"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    subtasks = [SubTask(task_id=f"t{i}", description=f"Task {i}", agent_type="test",
                       dependencies=[], expected_outputs=[]) for i in range(5)]
    plan = Plan(plan_id="p1", goal_id="g1", subtasks=subtasks, execution_strategy="sequential",
                estimated_total_duration=50, confidence_score=0.8)

    result = enforcer.disclose_plan(plan)
    assert result["subtasks"] == 5

def test_approval_gate_low_amount():
    """UX Test 5: Low amount actions auto-approve"""
    enforcer = ApprovalGateEnforcer()
    action = MockAction("purchase", amount=100)
    assert enforcer.enforce_approval_gate(action) is True

def test_approval_gate_high_amount():
    """UX Test 6: High amount actions require approval"""
    enforcer = ApprovalGateEnforcer()
    action = MockAction("purchase", amount=5000)
    assert enforcer.enforce_approval_gate(action) is False

def test_approval_gate_threshold():
    """UX Test 7: Approval threshold at 1000"""
    enforcer = ApprovalGateEnforcer()
    action_below = MockAction("purchase", amount=999)
    action_above = MockAction("purchase", amount=1001)

    assert enforcer.enforce_approval_gate(action_below) is True
    assert enforcer.enforce_approval_gate(action_above) is False

def test_consistency_tracking():
    """UX Test 8: Track interaction history"""
    guard = ConsistencyGuard()
    guard.check_consistency("input1", "output1")
    guard.check_consistency("input2", "output2")

    assert len(guard.interaction_history) == 2

def test_consistency_validation():
    """UX Test 9: Consistency check returns boolean"""
    guard = ConsistencyGuard()
    result = guard.check_consistency("test_input", "test_output")
    assert isinstance(result, bool)

def test_transparency_high_impact():
    """UX Test 10: High impact actions disclosed"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.COMPLEX, description="Test", constraints=[], success_criteria=[])
    plan = Plan(plan_id="p1", goal_id="g1", subtasks=[], execution_strategy="sequential",
                estimated_total_duration=100, confidence_score=0.6)

    result = enforcer.disclose_plan(plan, impact_level="high")
    assert result["disclosed"] is True

def test_transparency_plan_id():
    """UX Test 11: Disclosure includes plan ID"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    plan = Plan(plan_id="plan_123", goal_id="g1", subtasks=[], execution_strategy="sequential",
                estimated_total_duration=10, confidence_score=0.8)

    result = enforcer.disclose_plan(plan)
    assert result["plan_id"] == "plan_123"

def test_control_different_action_types():
    """UX Test 12: Different action types"""
    enforcer = ApprovalGateEnforcer()
    read_action = MockAction("read", amount=0)
    write_action = MockAction("write", amount=0)

    # Both should auto-approve with 0 amount
    assert enforcer.enforce_approval_gate(read_action) is True
    assert enforcer.enforce_approval_gate(write_action) is True

def test_consistency_history_order():
    """UX Test 13: History maintains order"""
    guard = ConsistencyGuard()
    guard.check_consistency("A", "1")
    guard.check_consistency("B", "2")
    guard.check_consistency("C", "3")

    assert guard.interaction_history[0]["input"] == "A"
    assert guard.interaction_history[1]["input"] == "B"
    assert guard.interaction_history[2]["input"] == "C"

def test_explanation_format():
    """UX Test 14: Explanation has specific format"""
    enforcer = TransparencyEnforcer()
    explanation = enforcer.provide_explanation("delete_file", "User requested cleanup")

    assert "Action:" in explanation
    assert "Reasoning:" in explanation

def test_transparency_with_no_subtasks():
    """UX Test 15: Handle plan with no subtasks"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    plan = Plan(plan_id="p1", goal_id="g1", subtasks=[], execution_strategy="sequential",
                estimated_total_duration=0, confidence_score=1.0)

    result = enforcer.disclose_plan(plan)
    assert result["subtasks"] == 0

def test_approval_gate_edge_case():
    """UX Test 16: Approval at exact threshold"""
    enforcer = ApprovalGateEnforcer()
    action_exact = MockAction("purchase", amount=1000)
    # At threshold, should still auto-approve
    assert enforcer.enforce_approval_gate(action_exact) is True

def test_consistency_empty_history():
    """UX Test 17: Empty history initially"""
    guard = ConsistencyGuard()
    assert len(guard.interaction_history) == 0

def test_multiple_transparency_calls():
    """UX Test 18: Multiple disclosure calls"""
    enforcer = TransparencyEnforcer()
    goal = Goal(goal_id="g1", goal_type=GoalType.SIMPLE, description="Test", constraints=[], success_criteria=[])
    plan1 = Plan(plan_id="p1", goal_id="g1", subtasks=[], execution_strategy="sequential",
                 estimated_total_duration=10, confidence_score=0.8)
    plan2 = Plan(plan_id="p2", goal_id="g1", subtasks=[], execution_strategy="sequential",
                 estimated_total_duration=20, confidence_score=0.9)

    result1 = enforcer.disclose_plan(plan1)
    result2 = enforcer.disclose_plan(plan2)

    assert result1["plan_id"] != result2["plan_id"]

def test_consistency_check_always_true():
    """UX Test 19: Consistency check (simplified implementation)"""
    guard = ConsistencyGuard()
    # In simplified implementation, always returns True
    assert guard.check_consistency("any_input", "any_output") is True

def test_action_without_amount_attribute():
    """UX Test 20: Handle actions without amount"""
    enforcer = ApprovalGateEnforcer()

    class SimpleAction:
        def __init__(self, action_type):
            self.type = action_type

    action = SimpleAction("read")
    # Should not crash, returns True (auto-approve)
    result = enforcer.enforce_approval_gate(action)
    assert result is True
