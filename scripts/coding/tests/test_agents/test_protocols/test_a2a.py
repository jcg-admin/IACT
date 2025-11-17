"""Tests for A2A Protocol"""
import pytest
from scripts.coding.ai.agents.protocols.a2a import MessageBus, AgentCard, AgentCapability, A2AAgent, MessageType

def test_register_and_discover_agents():
    bus = MessageBus()
    agent_card = AgentCard(
        agent_id="agent1",
        name="Test Agent",
        description="Test",
        capabilities=[AgentCapability(name="test", description="Test capability", input_schema={}, output_schema={})]
    )
    bus.register_agent(agent_card)
    discovered = bus.discover_agents()
    assert len(discovered) == 1

def test_send_message_between_agents():
    bus = MessageBus()
    agent1 = A2AAgent("agent1", "Agent 1", bus)
    agent2 = A2AAgent("agent2", "Agent 2", bus)
    agent1.publish()
    agent2.publish()

    msg_id = agent1.send_request("agent2", "test_capability", {"data": "test"})
    messages = agent2.get_messages()
    assert len(messages) == 1
    assert messages[0].from_agent == "agent1"
