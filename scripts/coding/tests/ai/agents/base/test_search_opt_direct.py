#!/usr/bin/env python3
"""
Direct tests for search optimization (bypasses __init__.py to avoid numpy dependency)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import directly from module
from scripts.ai.agents.base.search_optimization_techniques import (
    HybridSearchOptimization,
    SearchItem,
    Priority,
    CoverageLevel
)

def test_hybrid_basic():
    """Basic test of hybrid optimization."""
    items = [
        SearchItem(
            id=f"item{i}",
            content=f"Test item {i}",
            priority=Priority.MEDIUM,
            keywords=[f"keyword{i % 3}"]
        )
        for i in range(10)
    ]

    optimizer = HybridSearchOptimization(k_clusters=3, target_coverage=CoverageLevel.BALANCED)
    result = optimizer.optimize(items)

    print(f"✓ Queries: {len(result.queries)} (reduced from {len(items)})")
    print(f"✓ Coverage: {result.coverage_percentage:.1%}")
    print(f"✓ Token reduction: {result.token_reduction_percentage:.1%}")

    assert len(result.queries) < len(items), "Should reduce queries"
    assert result.coverage_percentage > 0.5, "Should cover >50%"
    assert result.token_reduction_percentage > 0.3, "Should reduce tokens >30%"

    return True

if __name__ == "__main__":
    print("Testing search optimization directly...")
    test_hybrid_basic()
    print("\n✓ All direct tests passed!")
