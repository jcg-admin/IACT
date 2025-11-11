#!/usr/bin/env python3
"""
Search Optimization Techniques

Implements algorithmic approaches to optimize token usage in search queries:
K-NN Clustering, Binary Search, Greedy, Divide-and-Conquer, Branch-and-Bound,
and Hybrid optimization strategies.

Based on classical computer science algorithms adapted for prompt engineering.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple, Set, Any
from enum import Enum
import re
from collections import defaultdict
import math


class SearchStrategy(Enum):
    """Search optimization strategy."""
    KNN_CLUSTERING = "knn_clustering"
    BINARY_SEARCH = "binary_search"
    GREEDY = "greedy"
    DIVIDE_CONQUER = "divide_conquer"
    BRANCH_BOUND = "branch_bound"
    HYBRID = "hybrid"


class CoverageLevel(Enum):
    """Target coverage level for search optimization."""
    RAPID = 0.70  # 70% coverage, 3-4 searches
    BALANCED = 0.85  # 85% coverage, 5-6 searches (recommended)
    COMPREHENSIVE = 0.95  # 95% coverage, 8-10 searches


class Priority(Enum):
    """Priority level for items."""
    CRITICAL = 3
    HIGH = 2
    MEDIUM = 1
    LOW = 0


@dataclass
class SearchItem:
    """Item to be searched."""
    id: str
    content: str
    priority: Priority = Priority.MEDIUM
    keywords: List[str] = field(default_factory=list)
    cluster_id: Optional[int] = None
    semantic_vector: Optional[List[float]] = None


@dataclass
class SearchQuery:
    """Optimized search query."""
    query_text: str
    covered_items: List[str]
    estimated_tokens: int
    information_density: float
    strategy_used: SearchStrategy


@dataclass
class ClusterInfo:
    """Information about a cluster."""
    cluster_id: int
    items: List[SearchItem]
    centroid_keywords: List[str]
    priority_score: float
    estimated_coverage: float


@dataclass
class SearchOptimizationResult:
    """Result of search optimization."""
    queries: List[SearchQuery]
    total_items: int
    covered_items: int
    coverage_percentage: float
    total_estimated_tokens: int
    token_reduction_percentage: float
    strategy_used: SearchStrategy


class KNNClusteringPrompting:
    """
    K-Nearest Neighbors Clustering for Search Optimization.

    Groups similar search items into clusters and creates one query per cluster,
    dramatically reducing the number of searches needed.
    """

    def __init__(self, k: int = 5):
        """
        Args:
            k: Number of clusters to create
        """
        self.k = k

    def cluster_items(
        self,
        items: List[SearchItem],
        similarity_fn: Optional[Callable[[SearchItem, SearchItem], float]] = None
    ) -> List[ClusterInfo]:
        """
        Cluster items using K-NN approach.

        Args:
            items: Items to cluster
            similarity_fn: Optional custom similarity function

        Returns:
            List of cluster information
        """
        if not similarity_fn:
            similarity_fn = self._keyword_similarity

        # Initialize k clusters randomly
        k_actual = min(self.k, len(items))
        clusters = [[] for _ in range(k_actual)]

        # Simple k-means-like clustering
        for item in items:
            # Find most similar cluster centroid
            if not any(clusters):
                # First items become initial centroids
                clusters[len([c for c in clusters if c])].append(item)
            else:
                best_cluster = 0
                best_similarity = -1

                for i, cluster in enumerate(clusters):
                    if cluster:
                        # Calculate similarity to cluster centroid (first item)
                        sim = similarity_fn(item, cluster[0])
                        if sim > best_similarity:
                            best_similarity = sim
                            best_cluster = i

                clusters[best_cluster].append(item)

        # Create cluster info
        cluster_infos = []
        for i, cluster in enumerate(clusters):
            if not cluster:
                continue

            # Extract common keywords
            keyword_freq = defaultdict(int)
            for item in cluster:
                for keyword in item.keywords:
                    keyword_freq[keyword] += 1

            common_keywords = sorted(
                keyword_freq.keys(),
                key=lambda k: keyword_freq[k],
                reverse=True
            )[:5]

            # Calculate priority score
            priority_score = sum(item.priority.value for item in cluster) / len(cluster)

            cluster_infos.append(ClusterInfo(
                cluster_id=i,
                items=cluster,
                centroid_keywords=common_keywords,
                priority_score=priority_score,
                estimated_coverage=len(cluster) / len(items)
            ))

        return cluster_infos

    def create_cluster_query(self, cluster: ClusterInfo) -> str:
        """
        Create optimized query for a cluster.

        Args:
            cluster: Cluster information

        Returns:
            Optimized search query
        """
        # Combine centroid keywords with high-density terms
        query_parts = []

        # Add primary keywords
        if cluster.centroid_keywords:
            query_parts.append(" ".join(cluster.centroid_keywords[:3]))

        # Add context from items
        item_contexts = [item.content.split()[0] for item in cluster.items[:3]]
        if item_contexts:
            query_parts.append(" OR ".join(item_contexts))

        return " ".join(query_parts)

    def _keyword_similarity(self, item1: SearchItem, item2: SearchItem) -> float:
        """Calculate keyword-based similarity between two items."""
        keywords1 = set(item1.keywords)
        keywords2 = set(item2.keywords)

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        # Jaccard similarity
        return intersection / union if union > 0 else 0.0


class BinarySearchPrompting:
    """
    Binary Search by Specificity.

    Start with broad queries, refine progressively only if needed.
    Complexity: O(log n) instead of O(n).
    """

    def __init__(self, coverage_threshold: float = 0.70):
        """
        Args:
            coverage_threshold: Minimum coverage to accept at each level
        """
        self.coverage_threshold = coverage_threshold

    def create_hierarchical_queries(
        self,
        items: List[SearchItem],
        domain: str = "general"
    ) -> List[Tuple[str, int, List[str]]]:
        """
        Create hierarchical queries from broad to specific.

        Args:
            items: Items to search
            domain: Domain context

        Returns:
            List of (query, level, covered_item_ids)
        """
        queries = []
        uncovered_items = set(item.id for item in items)

        # Level 1: Broad query
        broad_query = self._create_broad_query(items, domain)
        broad_coverage = self._estimate_coverage(broad_query, items)

        covered_broad = [
            item.id for item in items
            if self._query_matches_item(broad_query, item)
        ]

        queries.append((broad_query, 1, covered_broad))
        uncovered_items -= set(covered_broad)

        coverage_pct = len(covered_broad) / len(items)

        if coverage_pct >= self.coverage_threshold:
            # Broad query sufficient
            return queries

        # Level 2: Medium specificity (by category)
        if coverage_pct < self.coverage_threshold and uncovered_items:
            categories = self._categorize_items([
                item for item in items if item.id in uncovered_items
            ])

            for category, cat_items in categories.items():
                medium_query = self._create_category_query(category, cat_items)
                covered_medium = [item.id for item in cat_items]
                queries.append((medium_query, 2, covered_medium))
                uncovered_items -= set(covered_medium)

        # Level 3: Specific queries for remaining items
        if uncovered_items:
            for item in items:
                if item.id in uncovered_items:
                    specific_query = self._create_specific_query(item)
                    queries.append((specific_query, 3, [item.id]))

        return queries

    def _create_broad_query(self, items: List[SearchItem], domain: str) -> str:
        """Create broad query covering most items."""
        # Extract most common keywords
        all_keywords = []
        for item in items:
            all_keywords.extend(item.keywords)

        keyword_freq = defaultdict(int)
        for kw in all_keywords:
            keyword_freq[kw] += 1

        top_keywords = sorted(
            keyword_freq.keys(),
            key=lambda k: keyword_freq[k],
            reverse=True
        )[:3]

        return f"{domain} {' '.join(top_keywords)} comprehensive guide"

    def _create_category_query(self, category: str, items: List[SearchItem]) -> str:
        """Create medium-specificity category query."""
        keywords = set()
        for item in items:
            keywords.update(item.keywords[:2])

        return f"{category} {' '.join(list(keywords)[:4])}"

    def _create_specific_query(self, item: SearchItem) -> str:
        """Create highly specific query for single item."""
        return f"{item.content} {' '.join(item.keywords)}"

    def _categorize_items(self, items: List[SearchItem]) -> Dict[str, List[SearchItem]]:
        """Categorize items for medium-level queries."""
        categories = defaultdict(list)

        for item in items:
            # Use first keyword as category
            category = item.keywords[0] if item.keywords else "general"
            categories[category].append(item)

        return dict(categories)

    def _estimate_coverage(self, query: str, items: List[SearchItem]) -> float:
        """Estimate what percentage of items this query would cover."""
        query_terms = set(query.lower().split())
        covered = 0

        for item in items:
            item_terms = set(item.content.lower().split())
            item_terms.update(kw.lower() for kw in item.keywords)

            if query_terms & item_terms:
                covered += 1

        return covered / len(items) if items else 0.0

    def _query_matches_item(self, query: str, item: SearchItem) -> bool:
        """Check if query likely covers this item."""
        query_terms = set(query.lower().split())
        item_terms = set(item.content.lower().split())
        item_terms.update(kw.lower() for kw in item.keywords)

        # Match if >30% of item terms in query
        matches = len(query_terms & item_terms)
        return matches / len(item_terms) >= 0.3 if item_terms else False


class GreedyInformationDensity:
    """
    Greedy Algorithm: Maximize information per token.

    Select searches that maximize (coverage × priority) / tokens ratio.
    """

    def optimize_queries(
        self,
        items: List[SearchItem],
        max_queries: int = 6
    ) -> List[SearchQuery]:
        """
        Select queries greedily by information density.

        Args:
            items: Items to search
            max_queries: Maximum number of queries to generate

        Returns:
            Optimized list of search queries
        """
        uncovered = set(item.id for item in items)
        queries = []

        while uncovered and len(queries) < max_queries:
            # Generate candidate queries
            candidates = self._generate_candidate_queries(
                [item for item in items if item.id in uncovered]
            )

            # Score each candidate
            best_query = None
            best_score = -1

            for candidate in candidates:
                score = self._calculate_information_density(candidate, items)
                if score > best_score:
                    best_score = score
                    best_query = candidate

            if best_query:
                queries.append(best_query)
                uncovered -= set(best_query.covered_items)
            else:
                break

        return queries

    def _generate_candidate_queries(
        self,
        items: List[SearchItem]
    ) -> List[SearchQuery]:
        """Generate candidate queries for remaining items."""
        candidates = []

        # Candidate 1: Combine all high-priority items
        high_priority = [item for item in items if item.priority.value >= Priority.HIGH.value]
        if high_priority:
            query_text = self._create_combined_query(high_priority)
            candidates.append(SearchQuery(
                query_text=query_text,
                covered_items=[item.id for item in high_priority],
                estimated_tokens=len(query_text.split()),
                information_density=0.0,  # Will be calculated
                strategy_used=SearchStrategy.GREEDY
            ))

        # Candidate 2: Group by keyword similarity
        keyword_groups = self._group_by_keywords(items)
        for group in keyword_groups:
            query_text = self._create_combined_query(group)
            candidates.append(SearchQuery(
                query_text=query_text,
                covered_items=[item.id for item in group],
                estimated_tokens=len(query_text.split()),
                information_density=0.0,
                strategy_used=SearchStrategy.GREEDY
            ))

        return candidates

    def _calculate_information_density(
        self,
        query: SearchQuery,
        all_items: List[SearchItem]
    ) -> float:
        """
        Calculate information density score.

        Score = (items_covered × avg_priority) / tokens_used
        """
        if query.estimated_tokens == 0:
            return 0.0

        covered_items = [
            item for item in all_items
            if item.id in query.covered_items
        ]

        if not covered_items:
            return 0.0

        avg_priority = sum(item.priority.value for item in covered_items) / len(covered_items)
        coverage = len(covered_items)

        return (coverage * avg_priority) / query.estimated_tokens

    def _create_combined_query(self, items: List[SearchItem]) -> str:
        """Create query combining multiple items."""
        # Collect unique keywords
        all_keywords = set()
        for item in items:
            all_keywords.update(item.keywords[:2])

        # Take top keywords by frequency
        keyword_list = sorted(list(all_keywords))[:5]

        return " ".join(keyword_list)

    def _group_by_keywords(self, items: List[SearchItem]) -> List[List[SearchItem]]:
        """Group items by keyword similarity."""
        groups = []
        remaining = items.copy()

        while remaining:
            seed = remaining.pop(0)
            group = [seed]

            # Find similar items
            to_remove = []
            for item in remaining:
                if self._keywords_similar(seed, item):
                    group.append(item)
                    to_remove.append(item)

            for item in to_remove:
                remaining.remove(item)

            groups.append(group)

        return groups

    def _keywords_similar(self, item1: SearchItem, item2: SearchItem) -> bool:
        """Check if items have similar keywords."""
        kw1 = set(item1.keywords)
        kw2 = set(item2.keywords)

        if not kw1 or not kw2:
            return False

        intersection = len(kw1 & kw2)
        return intersection >= 1  # At least one common keyword


class DivideAndConquerSearch:
    """
    Divide and Conquer by Categories.

    Divide problem into independent subproblems, search in parallel conceptually.
    """

    def categorize_and_search(
        self,
        items: List[SearchItem],
        category_fn: Optional[Callable[[SearchItem], str]] = None
    ) -> Dict[str, List[SearchQuery]]:
        """
        Categorize items and create independent search strategy per category.

        Args:
            items: Items to search
            category_fn: Function to determine item category

        Returns:
            Dict mapping category to search queries
        """
        if not category_fn:
            category_fn = self._default_categorize

        # Divide: Categorize all items
        categories = defaultdict(list)
        for item in items:
            category = category_fn(item)
            categories[category].append(item)

        # Conquer: Create optimal search for each category independently
        results = {}
        for category, cat_items in categories.items():
            query = self._create_category_search(category, cat_items)
            results[category] = [query]

        return results

    def _default_categorize(self, item: SearchItem) -> str:
        """Default categorization by first keyword."""
        if item.keywords:
            return item.keywords[0]
        return "uncategorized"

    def _create_category_search(
        self,
        category: str,
        items: List[SearchItem]
    ) -> SearchQuery:
        """Create optimized search for a category."""
        # Collect common terms
        all_keywords = set()
        for item in items:
            all_keywords.update(item.keywords)

        # Create query
        query_text = f"{category} {' '.join(sorted(list(all_keywords))[:5])}"

        return SearchQuery(
            query_text=query_text,
            covered_items=[item.id for item in items],
            estimated_tokens=len(query_text.split()),
            information_density=len(items) / len(query_text.split()),
            strategy_used=SearchStrategy.DIVIDE_CONQUER
        )


class BranchAndBoundPrompting:
    """
    Branch and Bound by Priority.

    Prune low-priority searches if sufficient information already obtained.
    """

    def __init__(
        self,
        target_coverage: CoverageLevel = CoverageLevel.BALANCED
    ):
        """
        Args:
            target_coverage: Target coverage level
        """
        self.target_coverage = target_coverage

    def optimize_with_pruning(
        self,
        items: List[SearchItem],
        max_queries: int = 10
    ) -> SearchOptimizationResult:
        """
        Optimize searches with branch-and-bound pruning.

        Args:
            items: Items to search
            max_queries: Maximum queries allowed

        Returns:
            Optimization result with pruned queries
        """
        # Sort items by priority
        sorted_items = sorted(
            items,
            key=lambda x: x.priority.value,
            reverse=True
        )

        queries = []
        covered = set()
        total_items = len(items)

        # Branch: Try queries in priority order
        for priority_level in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            if len(queries) >= max_queries:
                break

            priority_items = [
                item for item in sorted_items
                if item.priority == priority_level and item.id not in covered
            ]

            if not priority_items:
                continue

            # Create query for this priority level
            query = self._create_priority_query(priority_items, priority_level)
            queries.append(query)
            covered.update(query.covered_items)

            # Bound: Check if we've reached target coverage
            coverage = len(covered) / total_items
            if coverage >= self.target_coverage.value:
                # Prune remaining low-priority searches
                break

        # Calculate metrics
        total_tokens = sum(q.estimated_tokens for q in queries)
        naive_tokens = total_items * 10  # Estimated tokens if searching individually

        return SearchOptimizationResult(
            queries=queries,
            total_items=total_items,
            covered_items=len(covered),
            coverage_percentage=len(covered) / total_items,
            total_estimated_tokens=total_tokens,
            token_reduction_percentage=(naive_tokens - total_tokens) / naive_tokens,
            strategy_used=SearchStrategy.BRANCH_BOUND
        )

    def _create_priority_query(
        self,
        items: List[SearchItem],
        priority: Priority
    ) -> SearchQuery:
        """Create query for items of specific priority."""
        keywords = set()
        for item in items:
            keywords.update(item.keywords[:3])

        query_text = f"priority:{priority.name.lower()} {' '.join(sorted(list(keywords))[:5])}"

        return SearchQuery(
            query_text=query_text,
            covered_items=[item.id for item in items],
            estimated_tokens=len(query_text.split()),
            information_density=len(items) / len(query_text.split()),
            strategy_used=SearchStrategy.BRANCH_BOUND
        )


class HybridSearchOptimization:
    """
    Hybrid Algorithm: Combine K-NN + Greedy + Branch-and-Bound.

    1. K-NN: Cluster items by similarity
    2. Greedy: Sort clusters by information density
    3. Branch-and-Bound: Search until target coverage reached
    """

    def __init__(
        self,
        k_clusters: int = 4,
        target_coverage: CoverageLevel = CoverageLevel.BALANCED
    ):
        """
        Args:
            k_clusters: Number of clusters for K-NN
            target_coverage: Target coverage level
        """
        self.knn = KNNClusteringPrompting(k=k_clusters)
        self.greedy = GreedyInformationDensity()
        self.branch_bound = BranchAndBoundPrompting(target_coverage=target_coverage)
        self.target_coverage = target_coverage

    def optimize(
        self,
        items: List[SearchItem],
        similarity_fn: Optional[Callable[[SearchItem, SearchItem], float]] = None
    ) -> SearchOptimizationResult:
        """
        Apply hybrid optimization strategy.

        Args:
            items: Items to search
            similarity_fn: Optional similarity function for clustering

        Returns:
            Optimized search result
        """
        # Step 1: K-NN clustering
        clusters = self.knn.cluster_items(items, similarity_fn)

        # Step 2: Greedy sort by information density
        clusters_sorted = sorted(
            clusters,
            key=lambda c: c.priority_score * len(c.items),
            reverse=True
        )

        # Step 3: Branch-and-bound search
        queries = []
        covered = set()
        total_items = len(items)

        for cluster in clusters_sorted:
            # Create query for cluster
            query_text = self.knn.create_cluster_query(cluster)

            query = SearchQuery(
                query_text=query_text,
                covered_items=[item.id for item in cluster.items],
                estimated_tokens=len(query_text.split()),
                information_density=len(cluster.items) / len(query_text.split()),
                strategy_used=SearchStrategy.HYBRID
            )

            queries.append(query)
            covered.update(query.covered_items)

            # Check coverage
            coverage = len(covered) / total_items
            if coverage >= self.target_coverage.value:
                break

        # Calculate metrics
        total_tokens = sum(q.estimated_tokens for q in queries)
        naive_tokens = total_items * 10

        return SearchOptimizationResult(
            queries=queries,
            total_items=total_items,
            covered_items=len(covered),
            coverage_percentage=len(covered) / total_items,
            total_estimated_tokens=total_tokens,
            token_reduction_percentage=(naive_tokens - total_tokens) / naive_tokens,
            strategy_used=SearchStrategy.HYBRID
        )


def main():
    """Example usage of search optimization techniques."""
    print("Search Optimization Techniques - Example\n")
    print("=" * 70)

    # Create sample items (e.g., software principles to search)
    items = [
        SearchItem(
            id="dry",
            content="DRY principle",
            priority=Priority.CRITICAL,
            keywords=["code", "organization", "duplication", "maintainability"]
        ),
        SearchItem(
            id="srp",
            content="Single Responsibility Principle",
            priority=Priority.CRITICAL,
            keywords=["solid", "organization", "responsibility", "cohesion"]
        ),
        SearchItem(
            id="ocp",
            content="Open-Closed Principle",
            priority=Priority.HIGH,
            keywords=["solid", "extensibility", "modification", "architecture"]
        ),
        SearchItem(
            id="event_driven",
            content="Event-Driven Architecture",
            priority=Priority.HIGH,
            keywords=["architecture", "distributed", "async", "events"]
        ),
        SearchItem(
            id="cqrs",
            content="CQRS Pattern",
            priority=Priority.MEDIUM,
            keywords=["architecture", "distributed", "commands", "queries"]
        ),
    ]

    print(f"\nSample: {len(items)} items to search\n")

    # Test 1: Hybrid Optimization (recommended)
    print("=" * 70)
    print("HYBRID OPTIMIZATION (K-NN + Greedy + Branch-and-Bound)")
    print("=" * 70)

    hybrid = HybridSearchOptimization(
        k_clusters=3,
        target_coverage=CoverageLevel.BALANCED  # 85%
    )

    result = hybrid.optimize(items)

    print(f"\nResults:")
    print(f"  Queries generated: {len(result.queries)}")
    print(f"  Coverage: {result.coverage_percentage:.1%}")
    print(f"  Total tokens: {result.total_estimated_tokens}")
    print(f"  Token reduction: {result.token_reduction_percentage:.1%}")

    print(f"\nOptimized Queries:")
    for i, query in enumerate(result.queries, 1):
        print(f"\n  Query {i}:")
        print(f"    Text: {query.query_text}")
        print(f"    Covers: {len(query.covered_items)} items")
        print(f"    Density: {query.information_density:.2f} items/token")

    # Test 2: Binary Search Prompting
    print("\n" + "=" * 70)
    print("BINARY SEARCH PROMPTING")
    print("=" * 70)

    binary_search = BinarySearchPrompting(coverage_threshold=0.70)
    hierarchical = binary_search.create_hierarchical_queries(items, domain="software architecture")

    print(f"\nHierarchical queries (broad → specific):")
    for query_text, level, covered in hierarchical:
        print(f"\n  Level {level}:")
        print(f"    Query: {query_text}")
        print(f"    Covers: {len(covered)} items")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
