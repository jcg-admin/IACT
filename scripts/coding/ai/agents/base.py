"""
Base classes for AI Agents

Re-exports from shared.agent_base for backwards compatibility
"""

from scripts.ai.shared.agent_base import (
    Agent,
    AgentResult,
    AgentStatus,
    Pipeline
)

__all__ = ['Agent', 'AgentResult', 'AgentStatus', 'Pipeline']
