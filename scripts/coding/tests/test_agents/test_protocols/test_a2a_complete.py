"""Complete A2A Protocol Tests (20 tests total)"""
import pytest
from scripts.coding.ai.agents.protocols.a2a import (
    MessageBus, AgentCard, AgentCapability, A2AAgent, A2AMessage, MessageType
)

# Tests 1-2 already exist in test_a2a.py

def test_agent_capability_registration():
    """A2A Test 3: Register agent capabilities"""
    bus = MessageBus()
    agent = A2AAgent("agent1", "Agent 1", bus)

    capability = AgentCapability(
        name="data_analysis",
        description="Analyze data",
        input_schema={"data": "array"},
        output_schema={"result": "object"}
    )

    agent.register_capability(capability)
    assert len(agent.capabilities) == 1

def test_agent_publish_to_bus():
    """A2A Test 4: Agent publishes to message bus"""
    bus = MessageBus()
    agent = A2AAgent("agent1", "Agent 1", bus)
    agent.register_capability(AgentCapability(
        name="test", description="Test", input_schema={}, output_schema={}
    ))

    agent.publish()
    assert "agent1" in bus.agents

def test_discover_agents_by_capability():
    """A2A Test 5: Discover agents by specific capability"""
    bus = MessageBus()

    agent1 = A2AAgent("agent1", "Flight Agent", bus)
    agent1.register_capability(AgentCapability(
        name="book_flight", description="Book flights", input_schema={}, output_schema={}
    ))
    agent1.publish()

    agent2 = A2AAgent("agent2", "Hotel Agent", bus)
    agent2.register_capability(AgentCapability(
        name="book_hotel", description="Book hotels", input_schema={}, output_schema={}
    ))
    agent2.publish()

    flight_agents = bus.discover_agents("flight")
    assert len(flight_agents) == 1
    assert flight_agents[0].agent_id == "agent1"

def test_message_correlation():
    """A2A Test 6: Message correlation for request-response"""
    bus = MessageBus()
    agent1 = A2AAgent("agent1", "A1", bus)
    agent2 = A2AAgent("agent2", "A2", bus)
    agent1.publish()
    agent2.publish()

    msg_id = agent1.send_request("agent2", "test_cap", {"data": "test"})
    agent2.send_response("agent1", msg_id, {"result": "success"})

    responses = [m for m in agent1.get_messages() if m.message_type == MessageType.RESPONSE]
    assert len(responses) == 1
    assert responses[0].correlation_id == msg_id

def test_message_ordering():
    """A2A Test 7: Preserve message ordering"""
    bus = MessageBus()
    agent1 = A2AAgent("agent1", "A1", bus)
    agent2 = A2AAgent("agent2", "A2", bus)
    agent1.publish()
    agent2.publish()

    msg_ids = []
    for i in range(3):
        msg_id = agent1.send_request("agent2", "test", {"seq": i})
        msg_ids.append(msg_id)

    messages = agent2.get_messages()
    assert len(messages) == 3
    assert [m.message_id for m in messages] == msg_ids

def test_agent_card_version():
    """A2A Test 8: Agent card includes version"""
    card = AgentCard(
        agent_id="agent1",
        name="Agent",
        description="Test agent",
        capabilities=[],
        version="2.0.0"
    )
    assert card.version == "2.0.0"

def test_multiple_capabilities_per_agent():
    """A2A Test 9: Agent with multiple capabilities"""
    agent = A2AAgent("multi_agent", "Multi", MessageBus())

    agent.register_capability(AgentCapability(
        name="cap1", description="First", input_schema={}, output_schema={}
    ))
    agent.register_capability(AgentCapability(
        name="cap2", description="Second", input_schema={}, output_schema={}
    ))

    assert len(agent.capabilities) == 2

def test_message_payload_validation():
    """A2A Test 10: Message payload structure"""
    message = A2AMessage(
        message_id="msg1",
        message_type=MessageType.REQUEST,
        from_agent="a1",
        to_agent="a2",
        capability="test",
        payload={"key": "value", "nested": {"data": 123}}
    )
    assert message.payload["nested"]["data"] == 123

def test_agent_discovery_empty_result():
    """A2A Test 11: Discovery with no matches"""
    bus = MessageBus()
    results = bus.discover_agents("nonexistent_capability")
    assert len(results) == 0

def test_message_timestamp():
    """A2A Test 12: Messages include timestamp"""
    message = A2AMessage(
        message_id="msg1",
        message_type=MessageType.NOTIFICATION,
        from_agent="a1",
        to_agent="a2",
        capability="notify",
        payload={}
    )
    assert message.timestamp is not None

def test_send_message_to_nonexistent_agent():
    """A2A Test 13: Send to nonexistent agent fails"""
    bus = MessageBus()
    agent = A2AAgent("agent1", "A1", bus)
    agent.publish()

    msg_id = agent.send_request("nonexistent", "test", {})
    # Message created but not delivered
    assert msg_id is not None

def test_notification_messages():
    """A2A Test 14: Send notification messages"""
    from datetime import datetime
    bus = MessageBus()

    notification = A2AMessage(
        message_id="notif1",
        message_type=MessageType.NOTIFICATION,
        from_agent="system",
        to_agent="agent1",
        capability="status_update",
        payload={"status": "ready"}
    )

    bus.agents["agent1"] = AgentCard(
        agent_id="agent1", name="A1", description="Test", capabilities=[]
    )

    result = bus.send_message(notification)
    assert result is True

def test_error_messages():
    """A2A Test 15: Error message type"""
    error_msg = A2AMessage(
        message_id="err1",
        message_type=MessageType.ERROR,
        from_agent="agent2",
        to_agent="agent1",
        capability="handle_error",
        payload={"error": "Failed to process", "code": 500}
    )
    assert error_msg.message_type == MessageType.ERROR

def test_agent_endpoint_optional():
    """A2A Test 16: Agent endpoint is optional"""
    card = AgentCard(
        agent_id="agent1",
        name="Agent",
        description="Test",
        capabilities=[]
    )
    assert card.endpoint is None

def test_capability_input_output_schemas():
    """A2A Test 17: Capability schemas"""
    capability = AgentCapability(
        name="transform",
        description="Transform data",
        input_schema={"type": "object", "properties": {"data": {"type": "array"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}}
    )
    assert "properties" in capability.input_schema

def test_get_messages_filtering():
    """A2A Test 18: Filter messages for specific agent"""
    bus = MessageBus()
    agent1 = A2AAgent("agent1", "A1", bus)
    agent2 = A2AAgent("agent2", "A2", bus)
    agent1.publish()
    agent2.publish()

    agent1.send_request("agent2", "test", {})
    agent1.send_request("agent2", "test2", {})

    agent2_messages = bus.get_messages_for("agent2")
    assert len(agent2_messages) == 2
    assert all(m.to_agent == "agent2" for m in agent2_messages)

def test_agent_rediscovery():
    """A2A Test 19: Re-discover agents after new registration"""
    bus = MessageBus()

    # Initial discovery
    agents1 = bus.discover_agents()
    assert len(agents1) == 0

    # Add agent
    agent = A2AAgent("agent1", "A1", bus)
    agent.publish()

    # Rediscover
    agents2 = bus.discover_agents()
    assert len(agents2) == 1

def test_message_bus_isolation():
    """A2A Test 20: Multiple message buses are isolated"""
    bus1 = MessageBus()
    bus2 = MessageBus()

    agent1 = A2AAgent("agent1", "A1", bus1)
    agent1.publish()

    # agent1 should not appear in bus2
    assert len(bus2.agents) == 0
    assert len(bus1.agents) == 1
