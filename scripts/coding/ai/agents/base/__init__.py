"""
Base agents and utilities

Common functionality shared across all AI agents.
Implements 38 advanced prompting techniques:
- 32 core techniques from academic research and industry
- 6 algorithmic search optimization techniques
"""

# Import base classes from sibling base.py module
# This resolves the architecture conflict between base.py and base/ package
import importlib.util
from pathlib import Path

# Load base.py module explicitly by file path
_base_py_path = Path(__file__).parent.parent / 'base.py'
_spec = importlib.util.spec_from_file_location("agents_base_module", _base_py_path)
_base_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_module)

# Import classes from the loaded module
Agent = _base_module.Agent
AgentResult = _base_module.AgentResult
AgentStatus = _base_module.AgentStatus
Pipeline = _base_module.Pipeline

# Clean up temporary variables
del _base_py_path, _spec, _base_module

# Advanced techniques (Phase 1: 5 techniques)
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
from .self_consistency import (
    SelfConsistencyAgent,
    SelfConsistencyResult,
    ReasoningPath,
    create_chain_of_thought_prompt
)

# Fundamental techniques (Phase 2: 3 techniques)
from .fundamental_techniques import (
    ZeroShotPrompting,
    FewShotPrompting,
    RolePrompting,
    PromptingMode,
    Example,
    Role
)

# Structuring techniques (Phase 2: 4 techniques)
from .structuring_techniques import (
    PromptChaining,
    TaskDecomposition,
    LeastToMostPrompting,
    InstructionHierarchy,
    Priority as StructuringPriority,  # Use alias to avoid conflict
    ChainStep,
    SubTask,
    Instruction
)

# Knowledge techniques (Phase 2: 4 techniques)
from .knowledge_techniques import (
    GeneratedKnowledgePrompting,
    RetrievalAugmentedGeneration,
    ReActPrompting,
    AutomaticReasoningAndToolUse,
    KnowledgeSource,
    ActionStatus,
    KnowledgeItem,
    ReActStep,
    Tool
)

# Optimization techniques (Phase 2: 7 techniques)
from .optimization_techniques import (
    DelimitersAndFormatting,
    ConstrainedGeneration,
    NegativePrompting,
    ConstitutionalAI,
    EmotionalPrompting,
    MetaPrompting,
    IterativeRefinement,
    DelimiterType,
    ConstraintType,
    Principle,
    MetricDefinition
)

# Specialized techniques (Phase 2: 12 techniques)
from .specialized_techniques import (
    CodeGenerationPrompting,
    MathematicalReasoning,
    AnalogicalPrompting,
    ProgramAidedLanguageModels,
    MedpromptFramework,
    BatchPrompting,
    ProgressivePrompts,
    ABTestingPrompts,
    EffectivenessEvaluation,
    LengthManagement,
    PromptCompression,
    CreativeWritingPrompts,
    CodeLanguage,
    TestVariant,
    CodeSpec,
    Analogy,
    PromptVariant
)

# Search optimization techniques (Phase 3: 6 techniques)
from .search_optimization_techniques import (
    KNNClusteringPrompting,
    BinarySearchPrompting,
    GreedyInformationDensity,
    DivideAndConquerSearch,
    BranchAndBoundPrompting,
    HybridSearchOptimization,
    SearchStrategy,
    CoverageLevel,
    SearchItem,
    SearchQuery,
    ClusterInfo,
    SearchOptimizationResult,
    Priority  # Numeric priority values for search optimization
)

__all__ = [
    # Base classes from base.py
    'Agent',
    'AgentResult',
    'AgentStatus',
    'Pipeline',
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
    'ThoughtEvaluation',
    # Self-Consistency
    'SelfConsistencyAgent',
    'SelfConsistencyResult',
    'ReasoningPath',
    'create_chain_of_thought_prompt',
    # Fundamental Techniques
    'ZeroShotPrompting',
    'FewShotPrompting',
    'RolePrompting',
    'PromptingMode',
    'Example',
    'Role',
    # Structuring Techniques
    'PromptChaining',
    'TaskDecomposition',
    'LeastToMostPrompting',
    'InstructionHierarchy',
    'StructuringPriority',
    'Priority',  # From search_optimization_techniques (numeric values)
    'ChainStep',
    'SubTask',
    'Instruction',
    # Knowledge Techniques
    'GeneratedKnowledgePrompting',
    'RetrievalAugmentedGeneration',
    'ReActPrompting',
    'AutomaticReasoningAndToolUse',
    'KnowledgeSource',
    'ActionStatus',
    'KnowledgeItem',
    'ReActStep',
    'Tool',
    # Optimization Techniques
    'DelimitersAndFormatting',
    'ConstrainedGeneration',
    'NegativePrompting',
    'ConstitutionalAI',
    'EmotionalPrompting',
    'MetaPrompting',
    'IterativeRefinement',
    'DelimiterType',
    'ConstraintType',
    'Principle',
    'MetricDefinition',
    # Specialized Techniques
    'CodeGenerationPrompting',
    'MathematicalReasoning',
    'AnalogicalPrompting',
    'ProgramAidedLanguageModels',
    'MedpromptFramework',
    'BatchPrompting',
    'ProgressivePrompts',
    'ABTestingPrompts',
    'EffectivenessEvaluation',
    'LengthManagement',
    'PromptCompression',
    'CreativeWritingPrompts',
    'CodeLanguage',
    'TestVariant',
    'CodeSpec',
    'Analogy',
    'PromptVariant',
    # Search Optimization Techniques
    'KNNClusteringPrompting',
    'BinarySearchPrompting',
    'GreedyInformationDensity',
    'DivideAndConquerSearch',
    'BranchAndBoundPrompting',
    'HybridSearchOptimization',
    'SearchStrategy',
    'CoverageLevel',
    'SearchItem',
    'SearchQuery',
    'ClusterInfo',
    'SearchOptimizationResult'
]
