"""
Base agents and utilities

Common functionality shared across all AI agents.
Implements 38 advanced prompting techniques:
- 32 core techniques from academic research and industry
- 6 algorithmic search optimization techniques
"""

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
    Priority,
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
    SearchOptimizationResult
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
    'Priority',
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
