"""
A2A (Agent-to-Agent Protocol): Agent ↔ Agent communication

Implements RF-013 A2A scenarios.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentCapability(BaseModel):
    """Capability that an agent can perform."""

    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    input_schema: Dict[str, Any] = Field(..., description="Expected input schema")
    output_schema: Dict[str, Any] = Field(..., description="Output schema")


class AgentCard(BaseModel):
    """Agent Card: Agent self-description for discovery."""

    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="What this agent does")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    version: str = Field(default="1.0.0", description="Agent version")
    endpoint: Optional[str] = Field(None, description="Agent endpoint URL")


class MessageType(str, Enum):
    """Types of A2A messages."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class A2AMessage(BaseModel):
    """Message exchanged between agents."""

    message_id: str = Field(..., description="Unique message ID")
    message_type: MessageType = Field(..., description="Message type")
    from_agent: str = Field(..., description="Sender agent ID")
    to_agent: str = Field(..., description="Recipient agent ID")
    capability: str = Field(..., description="Capability being invoked")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = Field(None, description="For request-response correlation")


class MessageBus:
    """Central message bus for A2A communication."""

    def __init__(self):
        """Initialize message bus."""
        self.agents: Dict[str, AgentCard] = {}
        self.messages: List[A2AMessage] = []
        self.subscriptions: Dict[str, List[str]] = {}  # agent_id -> [capabilities]

    def register_agent(self, agent_card: AgentCard) -> None:
        """
        Register an agent on the bus.

        Args:
            agent_card: Agent card with capabilities
        """
        self.agents[agent_card.agent_id] = agent_card

    def discover_agents(self, capability: Optional[str] = None) -> List[AgentCard]:
        """
        Discover agents by capability.

        Args:
            capability: Optional capability filter

        Returns:
            List of matching agent cards
        """
        if capability is None:
            return list(self.agents.values())

        matching = []
        for agent_card in self.agents.values():
            for cap in agent_card.capabilities:
                if capability.lower() in cap.name.lower() or capability.lower() in cap.description.lower():
                    matching.append(agent_card)
                    break

        return matching

    def send_message(self, message: A2AMessage) -> bool:
        """
        Send message to target agent.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        # Verify target agent exists
        if message.to_agent not in self.agents:
            return False

        self.messages.append(message)
        return True

    def get_messages_for(self, agent_id: str) -> List[A2AMessage]:
        """
        Get all messages for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of messages for this agent
        """
        return [msg for msg in self.messages if msg.to_agent == agent_id]


class A2AAgent:
    """Base class for agents that communicate via A2A."""

    def __init__(self, agent_id: str, name: str, message_bus: MessageBus):
        """
        Initialize A2A agent.

        Args:
            agent_id: Unique agent ID
            name: Agent name
            message_bus: Message bus to use
        """
        self.agent_id = agent_id
        self.name = name
        self.message_bus = message_bus
        self.capabilities: List[AgentCapability] = []

    def register_capability(self, capability: AgentCapability) -> None:
        """
        Register a capability this agent can perform.

        Args:
            capability: Capability definition
        """
        self.capabilities.append(capability)

    def publish(self) -> None:
        """Publish agent card to message bus."""
        agent_card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description=f"{self.name} agent",
            capabilities=self.capabilities
        )
        self.message_bus.register_agent(agent_card)

    def send_request(
        self, to_agent: str, capability: str, payload: Dict[str, Any]
    ) -> str:
        """
        Send request to another agent.

        Args:
            to_agent: Target agent ID
            capability: Capability to invoke
            payload: Request payload

        Returns:
            Message ID for correlation
        """
        import uuid

        message_id = str(uuid.uuid4())

        message = A2AMessage(
            message_id=message_id,
            message_type=MessageType.REQUEST,
            from_agent=self.agent_id,
            to_agent=to_agent,
            capability=capability,
            payload=payload
        )

        self.message_bus.send_message(message)
        return message_id

    def send_response(
        self, to_agent: str, correlation_id: str, payload: Dict[str, Any]
    ) -> None:
        """
        Send response to a request.

        Args:
            to_agent: Target agent ID
            correlation_id: Original request message ID
            payload: Response payload
        """
        import uuid

        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESPONSE,
            from_agent=self.agent_id,
            to_agent=to_agent,
            capability="response",
            payload=payload,
            correlation_id=correlation_id
        )

        self.message_bus.send_message(message)

    def get_messages(self) -> List[A2AMessage]:
        """
        Get all messages for this agent.

        Returns:
            List of messages
        """
        return self.message_bus.get_messages_for(self.agent_id)
