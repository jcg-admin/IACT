#!/usr/bin/env python3
"""
Example: Auto-CoT Usage for Different Domains

Demonstrates how to use Auto-CoT Agent for various software development tasks.
"""

import sys
from pathlib import Path

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import AutoCoTAgent


def example_code_review():
    """Example: Code Review with Auto-CoT"""
    print("="*70)
    print("EXAMPLE 1: Code Review with Auto-CoT")
    print("="*70 + "\n")

    # Domain questions for code review
    code_review_questions = [
        "How to identify potential security vulnerabilities in this API endpoint?",
        "What performance optimizations can be applied to this database query?",
        "Is this function following SOLID principles and best practices?",
        "How to refactor this complex nested loop for better readability?",
        "What are the code smells in this class design?",
        "How to improve test coverage for this module?",
        "Is this error handling robust and informative enough?",
        "What naming conventions are violated in this code?"
    ]

    # Generate demonstrations
    agent = AutoCoTAgent(k_clusters=4, max_demonstrations=6)
    demonstrations = agent.generate_demonstrations(
        code_review_questions,
        domain="code_review"
    )

    print(f"\nGenerated {len(demonstrations)} demonstrations\n")

    # Show first demonstration
    if demonstrations:
        demo = demonstrations[0]
        print("Sample Demonstration:")
        print(f"Q: {demo.question}")
        print(f"A: {demo.reasoning}")
        print(f"Answer: {demo.answer}")
        print(f"Quality Score: {demo.quality_score:.2f}\n")

    # Use for new code review
    new_question = "How to optimize this slow-running SQL query with multiple JOINs?"
    print(f"New Question: {new_question}\n")

    prompt = agent.create_few_shot_prompt(new_question, max_examples=3)
    print("Generated Few-Shot Prompt:")
    print("-" * 70)
    print(prompt[:500] + "...")
    print("-" * 70)

    # Save for reuse
    agent.save_demonstrations(Path("autocot_code_review.json"))
    print("\n[OK] Demonstrations saved to autocot_code_review.json\n")


def example_test_generation():
    """Example: Test Generation with Auto-CoT"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Test Generation with Auto-CoT")
    print("="*70 + "\n")

    test_questions = [
        "How to test database transactions with rollback scenarios?",
        "What assertions validate API response structure and status codes?",
        "How to mock external service dependencies in integration tests?",
        "What makes a test flaky and how to prevent it?",
        "How to test async functions and coroutines properly?",
        "What edge cases should be covered for input validation?",
        "How to test error propagation through multiple layers?",
        "What performance benchmarks should API tests include?"
    ]

    agent = AutoCoTAgent(k_clusters=4, max_demonstrations=5)
    demonstrations = agent.generate_demonstrations(
        test_questions,
        domain="test_generation"
    )

    print(f"Generated {len(demonstrations)} test generation demonstrations\n")

    # Show quality distribution
    quality_scores = [d.quality_score for d in demonstrations]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

    print(f"Quality Metrics:")
    print(f"  Average Score: {avg_quality:.2f}")
    print(f"  Highest Score: {max(quality_scores):.2f}")
    print(f"  Lowest Score: {min(quality_scores):.2f}\n")

    # Create few-shot prompt for new test
    new_question = "How to test a REST API endpoint that processes file uploads?"
    prompt = agent.create_few_shot_prompt(new_question, max_examples=2)

    print(f"New Test Question: {new_question}")
    print(f"Prompt Length: {len(prompt)} characters")
    print(f"Examples Included: 2\n")

    agent.save_demonstrations(Path("autocot_test_generation.json"))
    print("[OK] Test generation demonstrations saved\n")


def example_debugging():
    """Example: Debugging Assistance with Auto-CoT"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Debugging Assistance with Auto-CoT")
    print("="*70 + "\n")

    debugging_questions = [
        "Why is my SQL query returning NULL values unexpectedly?",
        "How to fix 'Connection timeout' error in REST API calls?",
        "What causes 'Memory leak' warnings in this Python application?",
        "Why is CSS not loading correctly on the production server?",
        "How to resolve 'Circular dependency' error in module imports?",
        "What's causing the '500 Internal Server Error' in this endpoint?",
        "Why does the application hang when processing large files?",
        "How to debug race conditions in concurrent code?"
    ]

    agent = AutoCoTAgent(k_clusters=5, max_demonstrations=8)
    demonstrations = agent.generate_demonstrations(
        debugging_questions,
        domain="debugging"
    )

    print(f"Generated {len(demonstrations)} debugging demonstrations\n")

    # Show demonstration structure
    if demonstrations:
        demo = demonstrations[0]
        steps = demo.reasoning.count('\n')
        print(f"Sample Debugging Flow:")
        print(f"  Question: {demo.question[:60]}...")
        print(f"  Reasoning Steps: {steps}")
        print(f"  Answer Length: {len(demo.answer)} chars")
        print(f"  Quality: {demo.quality_score:.2f}\n")

    # Apply to new debugging scenario
    new_problem = "Application crashes with 'Out of Memory' when loading user data"
    print(f"New Problem: {new_problem}")

    prompt = agent.create_few_shot_prompt(new_problem, max_examples=3)
    print(f"Created debugging prompt with 3 examples\n")

    agent.save_demonstrations(Path("autocot_debugging.json"))
    print("[OK] Debugging demonstrations saved\n")


def example_migration_validation():
    """Example: Database Migration Validation with Auto-CoT"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Migration Validation with Auto-CoT")
    print("="*70 + "\n")

    migration_questions = [
        "How to detect potentially dangerous DROP operations in migrations?",
        "What checks validate that migrations maintain backward compatibility?",
        "How to verify that migration rollback is safe and tested?",
        "What indexes should be added before altering large tables?",
        "How to validate that foreign key constraints are correct?",
        "What timing issues can occur with schema changes in production?",
        "How to check if migration will cause application downtime?",
        "What data migrations need manual verification before deployment?"
    ]

    agent = AutoCoTAgent(k_clusters=4, max_demonstrations=6)
    demonstrations = agent.generate_demonstrations(
        migration_questions,
        domain="migration_validation"
    )

    print(f"Generated {len(demonstrations)} migration validation demonstrations\n")

    # Show clustering results
    print("Clustering Results:")
    print("  Cluster 0: DROP/DELETE operations")
    print("  Cluster 1: Backward compatibility checks")
    print("  Cluster 2: Index and constraint validation")
    print("  Cluster 3: Production deployment safety\n")

    # Validate new migration
    new_migration = """
    ALTER TABLE users
    DROP COLUMN legacy_field,
    ADD COLUMN new_field VARCHAR(255);
    """

    new_question = f"Validate this migration for safety:\n{new_migration}"
    print(f"New Migration to Validate:")
    print(new_migration)

    prompt = agent.create_few_shot_prompt(new_question, max_examples=2)
    print(f"\nCreated validation prompt (length: {len(prompt)} chars)\n")

    agent.save_demonstrations(Path("autocot_migration_validation.json"))
    print("[OK] Migration validation demonstrations saved\n")


def example_performance_analysis():
    """Example: Performance Analysis with Auto-CoT"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Performance Analysis with Auto-CoT")
    print("="*70 + "\n")

    performance_questions = [
        "How to identify N+1 query problems in ORM code?",
        "What causes high memory usage in this data processing pipeline?",
        "How to optimize this slow-running algorithm?",
        "What caching strategy would improve API response time?",
        "How to detect and fix database index performance issues?",
        "What causes CPU spikes during peak traffic hours?",
        "How to optimize large file uploads for better throughput?",
        "What code patterns lead to thread contention?"
    ]

    agent = AutoCoTAgent(k_clusters=4, max_demonstrations=7)
    demonstrations = agent.generate_demonstrations(
        performance_questions,
        domain="performance_analysis"
    )

    print(f"Generated {len(demonstrations)} performance analysis demonstrations\n")

    # Quality analysis
    high_quality = [d for d in demonstrations if d.quality_score >= 0.7]
    print(f"Quality Analysis:")
    print(f"  Total Demonstrations: {len(demonstrations)}")
    print(f"  High Quality (>= 0.7): {len(high_quality)}")
    print(f"  Acceptance Rate: {len(high_quality)/len(demonstrations)*100:.1f}%\n")

    # Analyze performance issue
    new_issue = "API endpoint takes 5 seconds to respond under load"
    print(f"New Performance Issue: {new_issue}")

    prompt = agent.create_few_shot_prompt(new_issue, max_examples=3)
    print(f"Analysis prompt created with {3} examples\n")

    agent.save_demonstrations(Path("autocot_performance.json"))
    print("[OK] Performance analysis demonstrations saved\n")


def main():
    """Run all Auto-CoT examples."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  Auto-CoT Examples: Software Development Use Cases".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")

    # Run examples
    example_code_review()
    example_test_generation()
    example_debugging()
    example_migration_validation()
    example_performance_analysis()

    print("="*70)
    print("SUMMARY")
    print("="*70)
    print("\nGenerated demonstration files:")
    print("  - autocot_code_review.json")
    print("  - autocot_test_generation.json")
    print("  - autocot_debugging.json")
    print("  - autocot_migration_validation.json")
    print("  - autocot_performance.json")
    print("\nThese can be loaded and reused:")
    print("  agent.load_demonstrations(Path('autocot_code_review.json'))")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
