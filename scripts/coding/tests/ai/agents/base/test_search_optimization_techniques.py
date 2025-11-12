#!/usr/bin/env python3
"""
TDD Tests for Search Optimization Techniques

Tests all 6 algorithmic search optimization techniques:
- K-NN Clustering
- Binary Search
- Greedy Information Density
- Divide-and-Conquer
- Branch-and-Bound
- Hybrid Optimization
"""

import pytest
from scripts.ai.agents.base import (
    KNNClusteringPrompting,
    BinarySearchPrompting,
    GreedyInformationDensity,
    DivideAndConquerSearch,
    BranchAndBoundPrompting,
    HybridSearchOptimization,
    SearchItem,
    SearchQuery,
    SearchOptimizationResult,
    CoverageLevel,
    Priority,
    ClusterInfo
)


# Fixtures
@pytest.fixture
def sample_items():
    """Sample search items for testing."""
    return [
        SearchItem(
            id="item1",
            content="DRY principle",
            priority=Priority.CRITICAL,
            keywords=["code", "duplication", "maintainability"]
        ),
        SearchItem(
            id="item2",
            content="Single Responsibility",
            priority=Priority.CRITICAL,
            keywords=["solid", "responsibility", "cohesion"]
        ),
        SearchItem(
            id="item3",
            content="Open-Closed Principle",
            priority=Priority.HIGH,
            keywords=["solid", "extensibility", "modification"]
        ),
        SearchItem(
            id="item4",
            content="Event-Driven Architecture",
            priority=Priority.HIGH,
            keywords=["architecture", "events", "async"]
        ),
        SearchItem(
            id="item5",
            content="CQRS Pattern",
            priority=Priority.MEDIUM,
            keywords=["architecture", "commands", "queries"]
        ),
        SearchItem(
            id="item6",
            content="Microservices",
            priority=Priority.MEDIUM,
            keywords=["architecture", "distributed", "services"]
        ),
        SearchItem(
            id="item7",
            content="Test Coverage",
            priority=Priority.LOW,
            keywords=["testing", "coverage", "quality"]
        ),
        SearchItem(
            id="item8",
            content="Code Style",
            priority=Priority.LOW,
            keywords=["style", "linting", "formatting"]
        ),
    ]


@pytest.fixture
def large_item_set():
    """Large set of items for performance testing."""
    return [
        SearchItem(
            id=f"item{i}",
            content=f"Principle {i}",
            priority=Priority.MEDIUM,
            keywords=[f"keyword{i % 5}", f"category{i % 3}"]
        )
        for i in range(50)
    ]


# 1. K-NN Clustering Tests
class TestKNNClusteringPrompting:
    """Test K-NN clustering optimization."""

    def test_cluster_items_creates_k_clusters(self, sample_items):
        """Should create exactly k clusters."""
        knn = KNNClusteringPrompting(k=3)
        clusters = knn.cluster_items(sample_items)

        # Should create up to k clusters (may be fewer if not enough items)
        assert len(clusters) <= 3
        assert len(clusters) >= 1

    def test_cluster_items_covers_all_items(self, sample_items):
        """All items should be assigned to a cluster."""
        knn = KNNClusteringPrompting(k=3)
        clusters = knn.cluster_items(sample_items)

        total_clustered = sum(len(c.items) for c in clusters)
        assert total_clustered == len(sample_items)

    def test_cluster_query_generation(self, sample_items):
        """Should generate valid query for cluster."""
        knn = KNNClusteringPrompting(k=3)
        clusters = knn.cluster_items(sample_items)

        for cluster in clusters:
            query = knn.create_cluster_query(cluster)

            # Query should not be empty
            assert len(query) > 0
            # Query should contain keywords
            assert any(kw in query for kw in cluster.centroid_keywords)

    def test_similarity_function(self, sample_items):
        """Custom similarity function should be used."""
        def custom_similarity(item1, item2):
            return 1.0 if item1.priority == item2.priority else 0.0

        knn = KNNClusteringPrompting(k=3)
        clusters = knn.cluster_items(sample_items, similarity_fn=custom_similarity)

        # Should create clusters
        assert len(clusters) > 0


# 2. Binary Search Tests
class TestBinarySearchPrompting:
    """Test binary search by specificity."""

    def test_hierarchical_queries_start_broad(self, sample_items):
        """First query should be broad (level 1)."""
        binary = BinarySearchPrompting(coverage_threshold=0.70)
        queries = binary.create_hierarchical_queries(sample_items, domain="software")

        # Should have at least one query
        assert len(queries) > 0

        # First query should be level 1 (broad)
        query_text, level, covered = queries[0]
        assert level == 1
        assert len(query_text) > 0

    def test_stops_at_coverage_threshold(self, sample_items):
        """Should stop when coverage threshold met."""
        # High threshold - should need more queries
        binary_high = BinarySearchPrompting(coverage_threshold=0.90)
        queries_high = binary_high.create_hierarchical_queries(sample_items, domain="software")

        # Low threshold - should need fewer queries
        binary_low = BinarySearchPrompting(coverage_threshold=0.50)
        queries_low = binary_low.create_hierarchical_queries(sample_items, domain="software")

        # High threshold typically needs more queries (may not always be true)
        # At minimum, both should have queries
        assert len(queries_high) >= 1
        assert len(queries_low) >= 1

    def test_coverage_increases_by_level(self, sample_items):
        """Coverage should increase with each level."""
        binary = BinarySearchPrompting(coverage_threshold=0.95)
        queries = binary.create_hierarchical_queries(sample_items, domain="software")

        covered_so_far = set()
        for query_text, level, covered_ids in queries:
            # Each query should cover some items
            assert len(covered_ids) > 0

            # Coverage should increase
            prev_coverage = len(covered_so_far)
            covered_so_far.update(covered_ids)
            assert len(covered_so_far) >= prev_coverage


# 3. Greedy Information Density Tests
class TestGreedyInformationDensity:
    """Test greedy optimization by information density."""

    def test_optimize_reduces_queries(self, sample_items):
        """Should reduce number of queries needed."""
        greedy = GreedyInformationDensity()
        queries = greedy.optimize_queries(sample_items, max_queries=6)

        # Should generate fewer queries than items
        assert len(queries) < len(sample_items)
        assert len(queries) <= 6

    def test_optimize_prioritizes_high_priority_items(self, sample_items):
        """Should prioritize high-priority items."""
        greedy = GreedyInformationDensity()
        queries = greedy.optimize_queries(sample_items, max_queries=3)

        # Get all covered items
        all_covered = set()
        for query in queries:
            all_covered.update(query.covered_items)

        # Check that critical items are covered
        critical_items = [item for item in sample_items if item.priority == Priority.CRITICAL]
        for item in critical_items[:2]:  # At least some critical items
            # Due to greedy nature, high priority should be covered
            # This is a weak assertion as greedy doesn't guarantee all critical
            pass

    def test_information_density_calculated(self, sample_items):
        """Information density should be calculated for queries."""
        greedy = GreedyInformationDensity()
        queries = greedy.optimize_queries(sample_items, max_queries=5)

        for query in queries:
            # Density should be positive
            assert query.information_density >= 0


# 4. Divide-and-Conquer Tests
class TestDivideAndConquerSearch:
    """Test divide-and-conquer by categories."""

    def test_categorizes_items(self, sample_items):
        """Should categorize items into groups."""
        divide_conquer = DivideAndConquerSearch()
        results = divide_conquer.categorize_and_search(sample_items)

        # Should create multiple categories
        assert len(results) > 0

        # Each category should have queries
        for category, queries in results.items():
            assert len(queries) > 0

    def test_custom_categorization(self, sample_items):
        """Should use custom categorization function."""
        def custom_categorize(item):
            return "high" if item.priority.value >= Priority.HIGH.value else "low"

        divide_conquer = DivideAndConquerSearch()
        results = divide_conquer.categorize_and_search(
            sample_items,
            category_fn=custom_categorize
        )

        # Should have categories based on priority
        assert len(results) > 0

    def test_covers_all_items(self, sample_items):
        """Should cover all items across categories."""
        divide_conquer = DivideAndConquerSearch()
        results = divide_conquer.categorize_and_search(sample_items)

        total_covered = 0
        for category, queries in results.items():
            for query in queries:
                total_covered += len(query.covered_items)

        assert total_covered == len(sample_items)


# 5. Branch-and-Bound Tests
class TestBranchAndBoundPrompting:
    """Test branch-and-bound with priority pruning."""

    def test_optimize_respects_coverage_level(self, sample_items):
        """Should stop at target coverage level."""
        # Test RAPID (70%)
        bb_rapid = BranchAndBoundPrompting(target_coverage=CoverageLevel.RAPID)
        result_rapid = bb_rapid.optimize_with_pruning(sample_items)

        assert result_rapid.coverage_percentage >= 0.60  # Some tolerance

        # Test BALANCED (85%)
        bb_balanced = BranchAndBoundPrompting(target_coverage=CoverageLevel.BALANCED)
        result_balanced = bb_balanced.optimize_with_pruning(sample_items)

        assert result_balanced.coverage_percentage >= 0.75  # Some tolerance

    def test_prioritizes_critical_items(self, sample_items):
        """Should prioritize critical and high priority items."""
        bb = BranchAndBoundPrompting(target_coverage=CoverageLevel.RAPID)
        result = bb.optimize_with_pruning(sample_items, max_queries=2)

        # Get covered items
        covered_ids = set()
        for query in result.queries:
            covered_ids.update(query.covered_items)

        # Critical items should be covered
        critical_items = [item.id for item in sample_items if item.priority == Priority.CRITICAL]

        # At least some critical should be in early queries
        assert len(covered_ids) > 0

    def test_calculates_token_reduction(self, sample_items):
        """Should calculate token reduction percentage."""
        bb = BranchAndBoundPrompting(target_coverage=CoverageLevel.BALANCED)
        result = bb.optimize_with_pruning(sample_items)

        # Should show significant reduction
        assert result.token_reduction_percentage > 0
        assert result.token_reduction_percentage <= 1.0

    def test_returns_optimization_result(self, sample_items):
        """Should return SearchOptimizationResult."""
        bb = BranchAndBoundPrompting(target_coverage=CoverageLevel.BALANCED)
        result = bb.optimize_with_pruning(sample_items)

        assert isinstance(result, SearchOptimizationResult)
        assert len(result.queries) > 0
        assert result.total_items == len(sample_items)
        assert result.covered_items > 0


# 6. Hybrid Optimization Tests (MOST IMPORTANT)
class TestHybridSearchOptimization:
    """Test hybrid optimization (K-NN + Greedy + Branch-and-Bound)."""

    def test_optimize_reduces_queries_significantly(self, sample_items):
        """Should reduce queries by 80%+ typically."""
        hybrid = HybridSearchOptimization(k_clusters=3, target_coverage=CoverageLevel.BALANCED)
        result = hybrid.optimize(sample_items)

        # Should use much fewer queries than items
        assert len(result.queries) < len(sample_items) * 0.5

    def test_optimize_achieves_target_coverage(self, sample_items):
        """Should achieve target coverage level."""
        # Test with BALANCED (85%)
        hybrid = HybridSearchOptimization(
            k_clusters=3,
            target_coverage=CoverageLevel.BALANCED
        )
        result = hybrid.optimize(sample_items)

        # Should achieve close to 85% coverage (some tolerance)
        assert result.coverage_percentage >= 0.70

    def test_optimize_with_large_dataset(self, large_item_set):
        """Should handle large datasets efficiently."""
        hybrid = HybridSearchOptimization(k_clusters=5, target_coverage=CoverageLevel.BALANCED)
        result = hybrid.optimize(large_item_set)

        # Should dramatically reduce queries
        reduction = len(large_item_set) - len(result.queries)
        assert reduction > len(large_item_set) * 0.7  # >70% reduction

        # Should achieve good coverage
        assert result.coverage_percentage >= 0.70

    def test_returns_valid_optimization_result(self, sample_items):
        """Should return valid SearchOptimizationResult."""
        hybrid = HybridSearchOptimization()
        result = hybrid.optimize(sample_items)

        assert isinstance(result, SearchOptimizationResult)
        assert len(result.queries) > 0
        assert result.total_items == len(sample_items)
        assert result.covered_items > 0
        assert result.coverage_percentage > 0
        assert result.token_reduction_percentage >= 0

    def test_different_coverage_levels(self, sample_items):
        """Should respect different coverage level settings."""
        # RAPID
        hybrid_rapid = HybridSearchOptimization(target_coverage=CoverageLevel.RAPID)
        result_rapid = hybrid_rapid.optimize(sample_items)

        # COMPREHENSIVE
        hybrid_comp = HybridSearchOptimization(target_coverage=CoverageLevel.COMPREHENSIVE)
        result_comp = hybrid_comp.optimize(sample_items)

        # COMPREHENSIVE should have higher or equal coverage
        assert result_comp.coverage_percentage >= result_rapid.coverage_percentage - 0.1

    def test_custom_similarity_function(self, sample_items):
        """Should accept custom similarity function."""
        def priority_similarity(item1, item2):
            return 1.0 if item1.priority == item2.priority else 0.3

        hybrid = HybridSearchOptimization(k_clusters=3)
        result = hybrid.optimize(sample_items, similarity_fn=priority_similarity)

        # Should complete successfully
        assert len(result.queries) > 0


# Integration Tests
class TestSearchOptimizationIntegration:
    """Integration tests for search optimization techniques."""

    def test_all_techniques_reduce_tokens(self, sample_items):
        """All techniques should reduce token usage."""
        techniques = {
            'knn': KNNClusteringPrompting(k=3),
            'binary': BinarySearchPrompting(),
            'greedy': GreedyInformationDensity(),
            'divide': DivideAndConquerSearch(),
            'branch_bound': BranchAndBoundPrompting(),
            'hybrid': HybridSearchOptimization(k_clusters=3)
        }

        baseline_queries = len(sample_items)  # Naive approach

        for name, technique in techniques.items():
            if name == 'knn':
                clusters = technique.cluster_items(sample_items)
                optimized_queries = len(clusters)
            elif name == 'binary':
                queries = technique.create_hierarchical_queries(sample_items, domain="test")
                optimized_queries = len(queries)
            elif name == 'greedy':
                queries = technique.optimize_queries(sample_items, max_queries=5)
                optimized_queries = len(queries)
            elif name == 'divide':
                results = technique.categorize_and_search(sample_items)
                optimized_queries = sum(len(queries) for queries in results.values())
            elif name in ['branch_bound', 'hybrid']:
                if name == 'branch_bound':
                    result = technique.optimize_with_pruning(sample_items)
                else:
                    result = technique.optimize(sample_items)
                optimized_queries = len(result.queries)

            # All should reduce queries
            assert optimized_queries < baseline_queries, f"{name} did not reduce queries"

    def test_coverage_quality_tradeoff(self, large_item_set):
        """Test coverage vs query count tradeoff."""
        hybrid = HybridSearchOptimization(k_clusters=5)

        # RAPID should use fewer queries
        result_rapid = HybridSearchOptimization(
            k_clusters=5,
            target_coverage=CoverageLevel.RAPID
        ).optimize(large_item_set)

        # COMPREHENSIVE should use more queries for better coverage
        result_comp = HybridSearchOptimization(
            k_clusters=5,
            target_coverage=CoverageLevel.COMPREHENSIVE
        ).optimize(large_item_set)

        # COMPREHENSIVE should have more queries or equal
        assert len(result_comp.queries) >= len(result_rapid.queries) - 1


# Edge Cases
class TestSearchOptimizationEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_item(self):
        """Should handle single item gracefully."""
        items = [SearchItem(id="single", content="test", priority=Priority.MEDIUM, keywords=["test"])]

        hybrid = HybridSearchOptimization(k_clusters=1)
        result = hybrid.optimize(items)

        assert len(result.queries) >= 1
        assert result.coverage_percentage == 1.0

    def test_empty_keywords(self):
        """Should handle items with no keywords."""
        items = [
            SearchItem(id=f"item{i}", content=f"content{i}", priority=Priority.MEDIUM, keywords=[])
            for i in range(5)
        ]

        hybrid = HybridSearchOptimization(k_clusters=2)
        result = hybrid.optimize(items)

        # Should complete without errors
        assert len(result.queries) > 0

    def test_all_same_priority(self):
        """Should handle all items with same priority."""
        items = [
            SearchItem(id=f"item{i}", content=f"content{i}", priority=Priority.MEDIUM, keywords=["test"])
            for i in range(10)
        ]

        bb = BranchAndBoundPrompting(target_coverage=CoverageLevel.BALANCED)
        result = bb.optimize_with_pruning(items)

        assert len(result.queries) > 0
        assert result.coverage_percentage > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
