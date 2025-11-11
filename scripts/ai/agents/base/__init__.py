"""
Base agents and utilities

Common functionality shared across all AI agents.
"""

from .auto_cot_agent import AutoCoTAgent, Demonstration, Question
from .chain_of_verification import (
    ChainOfVerificationAgent,
    VerifiedResponse,
    Verification,
    VerificationStatus
)
from .prompt_templates import (
    PromptTemplateEngine,
    PromptTemplate,
    TemplateType,
    OutputFormat,
    TemplateVariable
)
from .tree_of_thoughts import (
    TreeOfThoughtsAgent,
    Thought,
    ThoughtState,
    SearchStrategy,
    ThoughtEvaluation
)

__all__ = [
    # Auto-CoT
    'AutoCoTAgent',
    'Demonstration',
    'Question',
    # Chain-of-Verification
    'ChainOfVerificationAgent',
    'VerifiedResponse',
    'Verification',
    'VerificationStatus',
    # Prompt Templates
    'PromptTemplateEngine',
    'PromptTemplate',
    'TemplateType',
    'OutputFormat',
    'TemplateVariable',
    # Tree of Thoughts
    'TreeOfThoughtsAgent',
    'Thought',
    'ThoughtState',
    'SearchStrategy',
    'ThoughtEvaluation'
]
