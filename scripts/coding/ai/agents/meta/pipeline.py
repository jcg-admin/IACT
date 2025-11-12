#!/usr/bin/env python3
"""
Architecture Improvement Pipeline

Orchestrates all 5 meta-development agents to provide comprehensive
architecture analysis and recommendations.

Pipeline Flow:
1. ArchitectureAnalysisAgent - SOLID compliance check
2. RefactoringOpportunitiesAgent - Code smell detection
3. DesignPatternsRecommendationAgent - Pattern recommendations
4. UMLDiagramValidationAgent - Diagram validation
5. TestGenerationAgent - Test suite generation

The pipeline collects results from each agent and provides consolidated
recommendations prioritized by impact and effort.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

from .architecture_analysis_agent import (
    ArchitectureAnalysisAgent,
    SOLIDAnalysisResult
)
from .refactoring_opportunities_agent import (
    RefactoringOpportunitiesAgent,
    RefactoringOpportunity
)
from .design_patterns_agent import (
    DesignPatternsRecommendationAgent,
    PatternRecommendation
)
from .uml_validation_agent import (
    UMLDiagramValidationAgent,
    UMLValidationResult
)
from .test_generation_agent import (
    TestGenerationAgent,
    TestSuite
)


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class ConsolidatedRecommendation:
    """A single recommendation from the pipeline."""
    source_agent: str
    priority: RecommendationPriority
    category: str
    description: str
    rationale: str
    estimated_effort: str
    estimated_impact: str
    action_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'source_agent': self.source_agent,
            'priority': self.priority.value,
            'category': self.category,
            'description': self.description,
            'rationale': self.rationale,
            'estimated_effort': self.estimated_effort,
            'estimated_impact': self.estimated_impact,
            'action_items': self.action_items
        }


@dataclass
class PipelineResult:
    """Comprehensive result from the architecture improvement pipeline."""
    solid_analysis: Optional[SOLIDAnalysisResult] = None
    refactoring_opportunities: List[RefactoringOpportunity] = field(default_factory=list)
    pattern_recommendations: List[PatternRecommendation] = field(default_factory=list)
    uml_validation: Optional[UMLValidationResult] = None
    test_suite: Optional[TestSuite] = None
    consolidated_recommendations: List[ConsolidatedRecommendation] = field(default_factory=list)
    overall_score: float = 0.0
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'solid_analysis': self.solid_analysis.to_dict() if self.solid_analysis else None,
            'refactoring_opportunities': [ro.to_dict() for ro in self.refactoring_opportunities],
            'pattern_recommendations': [pr.to_dict() for pr in self.pattern_recommendations],
            'uml_validation': self.uml_validation.to_dict() if self.uml_validation else None,
            'test_suite': self.test_suite.to_dict() if self.test_suite else None,
            'consolidated_recommendations': [cr.to_dict() for cr in self.consolidated_recommendations],
            'overall_score': self.overall_score,
            'summary': self.summary
        }


class ArchitectureImprovementPipeline:
    """
    Pipeline that orchestrates all 5 meta-development agents.

    Provides comprehensive architecture analysis and actionable recommendations.
    """

    def __init__(self):
        """Initialize the pipeline with all agents."""
        self.architecture_agent = ArchitectureAnalysisAgent()
        self.refactoring_agent = RefactoringOpportunitiesAgent()
        self.patterns_agent = DesignPatternsRecommendationAgent()
        self.uml_agent = UMLDiagramValidationAgent()
        self.test_gen_agent = TestGenerationAgent()

    def analyze_code(
        self,
        code: str,
        uml_diagram: Optional[str] = None,
        include_test_generation: bool = True
    ) -> PipelineResult:
        """
        Run complete architecture analysis pipeline.

        Args:
            code: Python code to analyze
            uml_diagram: Optional UML diagram to validate
            include_test_generation: Whether to generate tests

        Returns:
            PipelineResult with all analysis results and recommendations
        """
        result = PipelineResult()

        # Agent 1: SOLID Compliance Analysis
        solid_analysis = self.architecture_agent.analyze_solid_compliance(code)
        result.solid_analysis = solid_analysis

        # Agent 2: Refactoring Opportunities
        refactoring_opportunities = self.refactoring_agent.find_refactoring_opportunities(code)
        result.refactoring_opportunities = refactoring_opportunities

        # Agent 3: Design Pattern Recommendations
        pattern_recommendations = self.patterns_agent.recommend_patterns(code)
        result.pattern_recommendations = pattern_recommendations

        # Agent 4: UML Validation (if diagram provided)
        if uml_diagram:
            uml_validation = self.uml_agent.validate_diagram(uml_diagram)
            result.uml_validation = uml_validation

        # Agent 5: Test Generation
        if include_test_generation:
            test_suite = self.test_gen_agent.generate_tests(code)
            result.test_suite = test_suite

        # Consolidate recommendations
        result.consolidated_recommendations = self._consolidate_recommendations(result)

        # Calculate overall score
        result.overall_score = self._calculate_overall_score(result)

        # Generate summary
        result.summary = self._generate_summary(result)

        return result

    def _consolidate_recommendations(self, result: PipelineResult) -> List[ConsolidatedRecommendation]:
        """
        Consolidate recommendations from all agents into prioritized list.
        """
        recommendations = []

        # Add SOLID violations
        if result.solid_analysis and result.solid_analysis.violations:
            for violation in result.solid_analysis.violations:
                recommendations.append(ConsolidatedRecommendation(
                    source_agent="ArchitectureAnalysisAgent",
                    priority=RecommendationPriority.HIGH,
                    category="SOLID Compliance",
                    description=f"{violation.principle.value.upper()} violation: {violation.description}",
                    rationale="SOLID principles are fundamental to maintainable code",
                    estimated_effort="medium",
                    estimated_impact="high",
                    action_items=[violation.recommendation]
                ))

        # Add refactoring opportunities
        for opportunity in result.refactoring_opportunities:
            priority = self._map_refactoring_priority(opportunity.priority)
            recommendations.append(ConsolidatedRecommendation(
                source_agent="RefactoringOpportunitiesAgent",
                priority=priority,
                category="Code Quality",
                description=opportunity.description,
                rationale=f"Detected {opportunity.smell.value} code smell",
                estimated_effort=opportunity.estimated_effort,
                estimated_impact=opportunity.estimated_impact,
                action_items=[f"Apply {opportunity.refactoring_type.value} refactoring"]
            ))

        # Add pattern recommendations
        for pattern in result.pattern_recommendations:
            priority = self._map_pattern_priority(pattern.applicability.value)
            recommendations.append(ConsolidatedRecommendation(
                source_agent="DesignPatternsRecommendationAgent",
                priority=priority,
                category="Design Patterns",
                description=f"Consider {pattern.pattern_type.value} pattern",
                rationale=pattern.reasoning,
                estimated_effort="medium",
                estimated_impact="medium",
                action_items=[pattern.implementation_hint] + pattern.benefits
            ))

        # Add UML issues
        if result.uml_validation and result.uml_validation.issues:
            for issue in result.uml_validation.issues:
                priority = self._map_uml_priority(issue.severity)
                recommendations.append(ConsolidatedRecommendation(
                    source_agent="UMLDiagramValidationAgent",
                    priority=priority,
                    category="UML Validation",
                    description=issue.description,
                    rationale="UML diagrams should be valid and consistent",
                    estimated_effort="low",
                    estimated_impact="medium",
                    action_items=[f"Fix {issue.issue_type} at {issue.location}"]
                ))

        # Add test coverage recommendations
        if result.test_suite and result.test_suite.coverage_gaps:
            for gap in result.test_suite.coverage_gaps:
                recommendations.append(ConsolidatedRecommendation(
                    source_agent="TestGenerationAgent",
                    priority=RecommendationPriority.MEDIUM,
                    category="Test Coverage",
                    description=gap,
                    rationale="Comprehensive tests improve code reliability",
                    estimated_effort="low",
                    estimated_impact="high",
                    action_items=["Implement suggested test cases"]
                ))

        # Sort by priority (high to low)
        recommendations.sort(key=lambda r: r.priority.value, reverse=True)

        return recommendations

    def _map_refactoring_priority(self, priority: int) -> RecommendationPriority:
        """Map refactoring priority (1-10) to RecommendationPriority."""
        if priority >= 9:
            return RecommendationPriority.CRITICAL
        elif priority >= 7:
            return RecommendationPriority.HIGH
        elif priority >= 4:
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW

    def _map_pattern_priority(self, applicability: int) -> RecommendationPriority:
        """Map pattern applicability (1-5) to RecommendationPriority."""
        if applicability >= 5:
            return RecommendationPriority.HIGH
        elif applicability >= 4:
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW

    def _map_uml_priority(self, severity: str) -> RecommendationPriority:
        """Map UML severity to RecommendationPriority."""
        if severity == "critical":
            return RecommendationPriority.CRITICAL
        elif severity == "high":
            return RecommendationPriority.HIGH
        elif severity == "medium":
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW

    def _calculate_overall_score(self, result: PipelineResult) -> float:
        """
        Calculate overall code quality score (0.0 to 1.0).

        Higher is better.
        """
        score = 1.0

        # Deduct for SOLID violations
        if result.solid_analysis:
            violation_penalty = len(result.solid_analysis.violations) * 0.1
            score -= min(0.5, violation_penalty)

        # Deduct for refactoring opportunities
        high_priority_refactorings = sum(
            1 for r in result.refactoring_opportunities
            if r.priority >= 7
        )
        refactoring_penalty = high_priority_refactorings * 0.05
        score -= min(0.3, refactoring_penalty)

        # Bonus for test coverage
        if result.test_suite:
            score += result.test_suite.estimated_coverage * 0.2

        return max(0.0, min(1.0, score))

    def _generate_summary(self, result: PipelineResult) -> str:
        """Generate human-readable summary of analysis."""
        lines = []

        lines.append("Architecture Analysis Summary")
        lines.append("=" * 50)

        # SOLID analysis
        if result.solid_analysis:
            violation_count = len(result.solid_analysis.violations)
            lines.append(f"\nSOLID Compliance: {violation_count} violation(s)")

        # Refactoring
        if result.refactoring_opportunities:
            lines.append(f"Refactoring Opportunities: {len(result.refactoring_opportunities)}")

        # Patterns
        if result.pattern_recommendations:
            lines.append(f"Design Pattern Suggestions: {len(result.pattern_recommendations)}")

        # UML
        if result.uml_validation:
            status = "Valid" if result.uml_validation.is_valid else "Invalid"
            lines.append(f"UML Validation: {status}")

        # Tests
        if result.test_suite:
            coverage = result.test_suite.estimated_coverage * 100
            lines.append(f"Test Coverage: {coverage:.1f}%")

        # Overall
        lines.append(f"\nOverall Quality Score: {result.overall_score:.2f}/1.00")
        lines.append(f"Priority Recommendations: {len(result.consolidated_recommendations)}")

        return "\n".join(lines)


def create_architecture_improvement_pipeline() -> ArchitectureImprovementPipeline:
    """Factory function to create a pipeline instance."""
    return ArchitectureImprovementPipeline()
