#!/usr/bin/env python3
"""
Tree of Thoughts (ToT) Agent

Implements Tree-of-Thoughts reasoning from Yao et al. (2023) for systematic
exploration of multiple solution paths with evaluation and backtracking.

Based on: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (Princeton/Google DeepMind, 2023)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple
from enum import Enum
import heapq


class ThoughtState(Enum):
    """State of a thought in the tree."""
    PROMISING = "promising"
    FAILED = "failed"
    SOLVED = "solved"
    PRUNED = "pruned"


class SearchStrategy(Enum):
    """Tree search strategy."""
    BFS = "breadth_first"  # Explore level by level
    DFS = "depth_first"    # Explore deeply first
    BEAM = "beam_search"   # Keep top-k at each level
    BEST_FIRST = "best_first"  # Always expand best node


@dataclass
class Thought:
    """Represents a single thought/reasoning step."""
    id: int
    content: str
    depth: int
    parent_id: Optional[int] = None
    children_ids: List[int] = field(default_factory=list)
    state: ThoughtState = ThoughtState.PROMISING
    value: float = 0.0  # Quality score (0.0 to 1.0)
    votes: Dict[str, int] = field(default_factory=dict)  # For voting evaluation


@dataclass
class ThoughtEvaluation:
    """Evaluation result for a thought."""
    thought_id: int
    value: float
    reasoning: str
    is_solution: bool
    can_expand: bool


class TreeOfThoughtsAgent:
    """
    Agent that implements Tree-of-Thoughts reasoning.

    Process:
    1. Generate multiple thoughts (candidate next steps)
    2. Evaluate each thought's promise
    3. Select best thought(s) to expand
    4. Repeat until solution found or budget exhausted
    5. Backtrack if needed

    Strategies:
    - BFS: Systematic exploration, finds shortest path
    - DFS: Deep exploration, memory efficient
    - Beam: Balance breadth and depth
    - Best-First: Greedy, fast but may miss solutions
    """

    def __init__(
        self,
        strategy: SearchStrategy = SearchStrategy.BEAM,
        max_thoughts_per_step: int = 3,
        max_depth: int = 5,
        beam_width: int = 2,
        value_threshold: float = 0.3
    ):
        """
        Args:
            strategy: Search strategy to use
            max_thoughts_per_step: How many thoughts to generate at each step
            max_depth: Maximum depth to explore
            beam_width: For beam search, how many to keep per level
            value_threshold: Minimum value to consider a thought promising
        """
        self.strategy = strategy
        self.max_thoughts_per_step = max_thoughts_per_step
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.value_threshold = value_threshold

        self.thoughts: Dict[int, Thought] = {}
        self.next_thought_id = 0

    def solve(
        self,
        problem: str,
        initial_thoughts: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> Tuple[Optional[List[Thought]], Dict]:
        """
        Solve problem using Tree-of-Thoughts reasoning.

        Args:
            problem: Problem description
            initial_thoughts: Optional starting thoughts
            context: Additional context

        Returns:
            Tuple of (solution_path, metadata)
        """
        print(f"[ToT] Starting Tree-of-Thoughts search")
        print(f"[ToT] Strategy: {self.strategy.value}")
        print(f"[ToT] Max depth: {self.max_depth}")
        print(f"[ToT] Max thoughts per step: {self.max_thoughts_per_step}")

        # Initialize with root thought
        root = self._create_thought(
            content=f"Problem: {problem}",
            depth=0,
            parent_id=None
        )

        # Generate initial thoughts or use provided
        if initial_thoughts:
            for thought_text in initial_thoughts[:self.max_thoughts_per_step]:
                self._create_thought(
                    content=thought_text,
                    depth=1,
                    parent_id=root.id
                )
        else:
            self._generate_thoughts(root, problem, context)

        # Execute search strategy
        if self.strategy == SearchStrategy.BFS:
            solution = self._bfs_search(root, problem, context)
        elif self.strategy == SearchStrategy.DFS:
            solution = self._dfs_search(root, problem, context)
        elif self.strategy == SearchStrategy.BEAM:
            solution = self._beam_search(root, problem, context)
        elif self.strategy == SearchStrategy.BEST_FIRST:
            solution = self._best_first_search(root, problem, context)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Collect metadata
        metadata = {
            "total_thoughts": len(self.thoughts),
            "max_depth_reached": max((t.depth for t in self.thoughts.values()), default=0),
            "solution_found": solution is not None,
            "strategy_used": self.strategy.value
        }

        if solution:
            print(f"[ToT] Solution found! Path length: {len(solution)}")
        else:
            print(f"[ToT] No solution found within constraints")

        return solution, metadata

    def _create_thought(
        self,
        content: str,
        depth: int,
        parent_id: Optional[int]
    ) -> Thought:
        """Create and register a new thought."""
        thought = Thought(
            id=self.next_thought_id,
            content=content,
            depth=depth,
            parent_id=parent_id
        )

        self.thoughts[thought.id] = thought
        self.next_thought_id += 1

        # Update parent's children
        if parent_id is not None:
            self.thoughts[parent_id].children_ids.append(thought.id)

        return thought

    def _generate_thoughts(
        self,
        parent: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> List[Thought]:
        """
        Generate candidate next thoughts.

        In production: Use LLM to generate diverse thoughts.
        This simplified version uses heuristics based on problem type.
        """
        generated = []

        # Determine problem type and generate appropriate thoughts
        problem_lower = problem.lower()

        if "test" in problem_lower or "validation" in problem_lower:
            # Test generation problem
            candidates = [
                "Consider happy path scenarios first",
                "Identify edge cases that could break the system",
                "Think about error conditions and how to handle them",
                "Consider security implications and malicious inputs"
            ]
        elif "review" in problem_lower or "analyze" in problem_lower:
            # Code review problem
            candidates = [
                "Check for security vulnerabilities (injection, XSS, etc.)",
                "Evaluate performance and scalability concerns",
                "Verify compliance with project restrictions",
                "Assess code maintainability and readability"
            ]
        elif "database" in problem_lower or "migration" in problem_lower:
            # Database problem
            candidates = [
                "Verify no writes to read-only databases",
                "Check for proper transaction handling",
                "Consider migration rollback safety",
                "Evaluate impact on existing data"
            ]
        else:
            # Generic problem
            candidates = [
                "Break down problem into smaller sub-problems",
                "Identify constraints and requirements",
                "Consider multiple approaches",
                "Evaluate trade-offs of each approach"
            ]

        # Create thoughts from candidates (limit by max_thoughts_per_step)
        for candidate in candidates[:self.max_thoughts_per_step]:
            thought = self._create_thought(
                content=candidate,
                depth=parent.depth + 1,
                parent_id=parent.id
            )
            generated.append(thought)

        return generated

    def _evaluate_thought(
        self,
        thought: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> ThoughtEvaluation:
        """
        Evaluate how promising a thought is.

        Evaluation strategies:
        - Value: Score from 0.0 to 1.0
        - Vote: Multiple evaluations vote on quality
        - Step: Binary pass/fail for each step

        This implementation uses value-based scoring.
        """
        # In production: Use LLM to evaluate thought quality
        # This simplified version uses heuristics

        value = 0.5  # Default neutral value
        reasoning = ""
        is_solution = False
        can_expand = thought.depth < self.max_depth

        content_lower = thought.content.lower()

        # Heuristic scoring
        positive_indicators = [
            'consider', 'verify', 'check', 'evaluate', 'identify',
            'break down', 'analyze', 'systematic', 'comprehensive'
        ]
        negative_indicators = [
            'ignore', 'skip', 'assume', 'maybe', 'unclear'
        ]

        # Score based on indicators
        positive_score = sum(0.1 for ind in positive_indicators if ind in content_lower)
        negative_score = sum(0.15 for ind in negative_indicators if ind in content_lower)

        value = min(1.0, max(0.0, 0.5 + positive_score - negative_score))

        # Domain-specific scoring
        if context and 'domain' in context:
            domain = context['domain']

            if domain == 'security' and any(kw in content_lower for kw in ['security', 'vulnerability', 'injection']):
                value += 0.2
                reasoning += "Security-focused (domain relevant). "

            if domain == 'database' and any(kw in content_lower for kw in ['database', 'transaction', 'read-only']):
                value += 0.2
                reasoning += "Database-focused (domain relevant). "

        value = min(1.0, value)

        # Check if this could be a solution
        if 'solution' in content_lower or 'implement' in content_lower or 'fix' in content_lower:
            if value > 0.7:
                is_solution = True
                reasoning += "Potential solution identified. "

        if not reasoning:
            reasoning = f"Evaluated with score {value:.2f}"

        return ThoughtEvaluation(
            thought_id=thought.id,
            value=value,
            reasoning=reasoning,
            is_solution=is_solution,
            can_expand=can_expand
        )

    def _bfs_search(
        self,
        root: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> Optional[List[Thought]]:
        """Breadth-first search strategy."""
        from collections import deque

        queue = deque([root])
        visited = {root.id}

        while queue:
            current = queue.popleft()

            # Generate and evaluate children if not at max depth
            if current.depth < self.max_depth:
                children = self._generate_thoughts(current, problem, context)

                for child in children:
                    if child.id in visited:
                        continue

                    visited.add(child.id)

                    # Evaluate
                    evaluation = self._evaluate_thought(child, problem, context)
                    child.value = evaluation.value

                    # Check if solution
                    if evaluation.is_solution and evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.SOLVED
                        return self._extract_path(child)

                    # Add promising thoughts to queue
                    if evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.PROMISING
                        queue.append(child)
                    else:
                        child.state = ThoughtState.PRUNED

        return None

    def _dfs_search(
        self,
        root: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> Optional[List[Thought]]:
        """Depth-first search strategy."""
        stack = [root]
        visited = {root.id}

        while stack:
            current = stack.pop()

            # Generate and evaluate children if not at max depth
            if current.depth < self.max_depth:
                children = self._generate_thoughts(current, problem, context)

                # Reverse to maintain left-to-right order
                for child in reversed(children):
                    if child.id in visited:
                        continue

                    visited.add(child.id)

                    # Evaluate
                    evaluation = self._evaluate_thought(child, problem, context)
                    child.value = evaluation.value

                    # Check if solution
                    if evaluation.is_solution and evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.SOLVED
                        return self._extract_path(child)

                    # Add promising thoughts to stack (DFS goes deep)
                    if evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.PROMISING
                        stack.append(child)
                    else:
                        child.state = ThoughtState.PRUNED

        return None

    def _beam_search(
        self,
        root: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> Optional[List[Thought]]:
        """Beam search strategy - keep top-k at each level."""
        current_beam = [root]

        for depth in range(self.max_depth):
            next_beam = []

            # Expand each thought in current beam
            for thought in current_beam:
                children = self._generate_thoughts(thought, problem, context)

                for child in children:
                    # Evaluate
                    evaluation = self._evaluate_thought(child, problem, context)
                    child.value = evaluation.value

                    # Check if solution
                    if evaluation.is_solution and evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.SOLVED
                        return self._extract_path(child)

                    # Add to next beam if promising
                    if evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.PROMISING
                        next_beam.append(child)

            # Keep only top beam_width thoughts
            next_beam.sort(key=lambda t: t.value, reverse=True)
            current_beam = next_beam[:self.beam_width]

            # Mark pruned thoughts
            for thought in next_beam[self.beam_width:]:
                thought.state = ThoughtState.PRUNED

            if not current_beam:
                break

        # If no explicit solution found, return best path
        if current_beam:
            best = max(current_beam, key=lambda t: t.value)
            if best.value >= self.value_threshold:
                return self._extract_path(best)

        return None

    def _best_first_search(
        self,
        root: Thought,
        problem: str,
        context: Optional[Dict]
    ) -> Optional[List[Thought]]:
        """Best-first search - always expand highest value node."""
        # Priority queue: (-value, thought_id, thought)
        # Negative value for max-heap behavior
        pq = [(-root.value, root.id, root)]
        visited = {root.id}

        while pq:
            neg_value, thought_id, current = heapq.heappop(pq)

            # Generate and evaluate children if not at max depth
            if current.depth < self.max_depth:
                children = self._generate_thoughts(current, problem, context)

                for child in children:
                    if child.id in visited:
                        continue

                    visited.add(child.id)

                    # Evaluate
                    evaluation = self._evaluate_thought(child, problem, context)
                    child.value = evaluation.value

                    # Check if solution
                    if evaluation.is_solution and evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.SOLVED
                        return self._extract_path(child)

                    # Add promising thoughts to priority queue
                    if evaluation.value >= self.value_threshold:
                        child.state = ThoughtState.PROMISING
                        heapq.heappush(pq, (-child.value, child.id, child))
                    else:
                        child.state = ThoughtState.PRUNED

        return None

    def _extract_path(self, thought: Thought) -> List[Thought]:
        """Extract path from root to given thought."""
        path = []
        current = thought

        while current is not None:
            path.append(current)
            if current.parent_id is not None:
                current = self.thoughts[current.parent_id]
            else:
                break

        return list(reversed(path))

    def visualize_tree(self) -> str:
        """Generate text visualization of thought tree."""
        if not self.thoughts:
            return "Empty tree"

        lines = []
        root = self.thoughts[0]

        def render_node(thought: Thought, prefix: str = "", is_last: bool = True):
            # Node representation
            state_symbol = {
                ThoughtState.PROMISING: "[?]",
                ThoughtState.SOLVED: "[✓]",
                ThoughtState.FAILED: "[✗]",
                ThoughtState.PRUNED: "[—]"
            }

            symbol = state_symbol.get(thought.state, "[ ]")
            connector = "└── " if is_last else "├── "

            lines.append(
                f"{prefix}{connector}{symbol} {thought.content[:60]} (v={thought.value:.2f})"
            )

            # Recursively render children
            if thought.children_ids:
                extension = "    " if is_last else "│   "
                for i, child_id in enumerate(thought.children_ids):
                    child = self.thoughts[child_id]
                    is_last_child = i == len(thought.children_ids) - 1
                    render_node(child, prefix + extension, is_last_child)

        render_node(root)
        return "\n".join(lines)


def main():
    """Example usage of Tree-of-Thoughts."""
    print("Tree of Thoughts Agent - Example\n")
    print("=" * 70)

    # Example 1: Test generation problem with Beam Search
    print("\n[Example 1] Test Generation with Beam Search\n")

    agent = TreeOfThoughtsAgent(
        strategy=SearchStrategy.BEAM,
        max_thoughts_per_step=3,
        max_depth=4,
        beam_width=2
    )

    problem = "Generate comprehensive tests for DBRouterGate that validates IVR database is never written to"

    solution, metadata = agent.solve(
        problem=problem,
        context={'domain': 'database'}
    )

    print(f"\nMetadata:")
    print(f"  Total thoughts explored: {metadata['total_thoughts']}")
    print(f"  Max depth reached: {metadata['max_depth_reached']}")
    print(f"  Solution found: {metadata['solution_found']}")

    if solution:
        print(f"\nSolution path ({len(solution)} steps):")
        for i, thought in enumerate(solution):
            print(f"{i}. {thought.content} (value={thought.value:.2f})")

    print("\n" + "=" * 70)
    print("\nTree visualization:\n")
    print(agent.visualize_tree())

    # Example 2: Code review with Best-First Search
    print("\n" + "=" * 70)
    print("\n[Example 2] Code Review with Best-First Search\n")

    agent2 = TreeOfThoughtsAgent(
        strategy=SearchStrategy.BEST_FIRST,
        max_thoughts_per_step=4,
        max_depth=3
    )

    problem2 = "Review authentication middleware for security vulnerabilities"

    solution2, metadata2 = agent2.solve(
        problem=problem2,
        context={'domain': 'security'}
    )

    print(f"\nMetadata:")
    print(f"  Total thoughts explored: {metadata2['total_thoughts']}")
    print(f"  Strategy: {metadata2['strategy_used']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
