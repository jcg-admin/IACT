"""
Meta-Development Agents

Agents that use the 38 prompting techniques to improve the IACT project itself.
This is meta-design: using our tools to improve our tools.

## Architecture Improvement Agents (5 agents)

1. ArchitectureAnalysisAgent - Uses Chain-of-Verification to validate SOLID compliance
2. RefactoringOpportunitiesAgent - Uses Search Optimization to identify code smells
3. DesignPatternsRecommendationAgent - Uses Auto-CoT to suggest design patterns
4. UMLDiagramValidationAgent - Uses Self-Consistency to validate UML diagrams
5. TestGenerationAgent - Uses Tree of Thoughts to generate comprehensive test suites

## Pipeline

- ArchitectureImprovementPipeline - Orchestrates all 5 agents for comprehensive analysis

Each agent demonstrates practical application of advanced prompting techniques
to real software engineering problems.
"""

from .architecture_analysis_agent import (
    ArchitectureAnalysisAgent,
    SOLIDAnalysisResult,
    PrincipleViolation,
    SOLIDPrinciple
)

# Refactoring Opportunities (implemented)
from .refactoring_opportunities_agent import (
    RefactoringOpportunitiesAgent,
    RefactoringOpportunity,
    CodeSmell,
    RefactoringType
)

# TODO: Import other agents as they are implemented
# from .design_patterns_agent import (
#     DesignPatternsRecommendationAgent,
#     PatternRecommendation,
#     PatternType,
#     PatternApplicability
# )
# from .uml_validation_agent import (
#     UMLDiagramValidationAgent,
#     UMLValidationResult,
#     DiagramType,
#     ValidationIssue
# )
# from .test_generation_agent import (
#     TestGenerationAgent,
#     TestSuite,
#     TestCase,
#     TestType
# )
# from .pipeline import (
#     ArchitectureImprovementPipeline,
#     create_architecture_improvement_pipeline
# )

__all__ = [
    # Architecture Analysis (implemented)
    'ArchitectureAnalysisAgent',
    'SOLIDAnalysisResult',
    'PrincipleViolation',
    'SOLIDPrinciple',
    # Refactoring Opportunities (implemented)
    'RefactoringOpportunitiesAgent',
    'RefactoringOpportunity',
    'CodeSmell',
    'RefactoringType',
    # TODO: Add other agents as they are implemented
]
