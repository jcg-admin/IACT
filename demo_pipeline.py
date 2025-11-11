#!/usr/bin/env python3
"""
Demo: Test meta-development pipeline with real project code.

This script demonstrates the complete architecture improvement pipeline
by analyzing actual code from the IACT project.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.ai.agents.meta import create_architecture_improvement_pipeline


def analyze_file(file_path: str):
    """Analyze a Python file with the complete pipeline."""
    print(f"\n{'='*70}")
    print(f"ANALYZING: {file_path}")
    print(f"{'='*70}\n")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    print(f"File size: {len(code)} characters, {len(code.splitlines())} lines\n")

    # Create pipeline
    pipeline = create_architecture_improvement_pipeline()

    # Run analysis (without test generation for faster results)
    print("Running complete analysis pipeline...")
    print("  - ArchitectureAnalysisAgent (SOLID compliance)")
    print("  - RefactoringOpportunitiesAgent (code smells)")
    print("  - DesignPatternsRecommendationAgent (patterns)")
    print()

    result = pipeline.analyze_code(code, include_test_generation=False)

    # Print results
    print(result.summary)
    print()

    # Show top recommendations
    if result.consolidated_recommendations:
        print(f"\n{'='*70}")
        print("TOP RECOMMENDATIONS (by priority)")
        print(f"{'='*70}\n")

        for i, rec in enumerate(result.consolidated_recommendations[:10], 1):
            print(f"{i}. [{rec.priority.name}] {rec.category}")
            print(f"   {rec.description}")
            print(f"   Effort: {rec.estimated_effort} | Impact: {rec.estimated_impact}")
            if rec.action_items:
                print(f"   Action: {rec.action_items[0]}")
            print()

    # Show SOLID violations if any
    if result.solid_analysis and result.solid_analysis.violations:
        print(f"\n{'='*70}")
        print("SOLID PRINCIPLE VIOLATIONS")
        print(f"{'='*70}\n")

        for v in result.solid_analysis.violations:
            print(f"- {v.principle.value.upper()}: {v.description}")
            print(f"  Recommendation: {v.recommendation}")
            print()

    # Show refactoring opportunities
    if result.refactoring_opportunities:
        print(f"\n{'='*70}")
        print("REFACTORING OPPORTUNITIES")
        print(f"{'='*70}\n")

        for opp in result.refactoring_opportunities[:5]:
            print(f"- [{opp.smell.value}] Priority: {opp.priority}")
            print(f"  {opp.description}")
            print(f"  Suggestion: {opp.refactoring_type.value}")
            print()

    # Show pattern recommendations
    if result.pattern_recommendations:
        print(f"\n{'='*70}")
        print("DESIGN PATTERN RECOMMENDATIONS")
        print(f"{'='*70}\n")

        for pattern in result.pattern_recommendations:
            print(f"- {pattern.pattern_type.value} ({pattern.applicability.name} applicability)")
            print(f"  Reasoning: {pattern.reasoning}")
            print(f"  Benefits: {', '.join(pattern.benefits[:2])}")
            print()

    return result


def main():
    """Main entry point."""
    # Analyze a few interesting files from the project
    files_to_analyze = [
        "scripts/ai/agents/syntax_validator.py",
        "scripts/ai/agents/base.py",
    ]

    results = []

    for file_path in files_to_analyze:
        if Path(file_path).exists():
            result = analyze_file(file_path)
            results.append((file_path, result))
        else:
            print(f"File not found: {file_path}")

    # Summary
    print(f"\n{'='*70}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*70}\n")

    for file_path, result in results:
        filename = Path(file_path).name
        print(f"{filename}:")
        print(f"  Quality Score: {result.overall_score:.2f}/1.00")
        print(f"  Recommendations: {len(result.consolidated_recommendations)}")
        print(f"  SOLID Violations: {len(result.solid_analysis.violations) if result.solid_analysis else 0}")
        print()


if __name__ == "__main__":
    main()
