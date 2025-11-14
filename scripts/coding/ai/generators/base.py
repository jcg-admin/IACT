"""
Base classes for Generators

Re-exports from shared.agent_base for backwards compatibility
"""

from scripts.coding.ai.shared.agent_base import (
    Agent,
    AgentResult,
    AgentStatus,
    Pipeline
)

__all__ = ['Agent', 'AgentResult', 'AgentStatus', 'Pipeline']
