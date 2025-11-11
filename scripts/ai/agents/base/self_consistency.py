#!/usr/bin/env python3
"""
Self-Consistency Decoding Agent

Implements Self-Consistency from Wang et al. (2022) to improve reasoning accuracy
through multiple sampling and majority voting.

Based on: "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (Google Research, 2022)
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple
from collections import Counter
import re

# Add parent paths for LLMGenerator import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMGenerator = None


@dataclass
class ReasoningPath:
    """Represents a single reasoning chain and its extracted answer."""
    full_response: str
    extracted_answer: str
    reasoning_steps: List[str]
    confidence: float = 1.0


@dataclass
class SelfConsistencyResult:
    """Result of self-consistency decoding."""
    final_answer: str
    confidence_score: float
    vote_distribution: Dict[str, int]
    all_paths: List[ReasoningPath]
    consensus_strength: float
    total_samples: int


class SelfConsistencyAgent:
    """
    Agent that implements Self-Consistency Decoding.

    Process:
    1. Generate multiple diverse reasoning chains (same prompt, different samples)
    2. Extract final answer from each chain
    3. Apply majority voting
    4. Return most consistent answer with confidence metrics

    Key Benefits:
    - 12-23% accuracy improvement on reasoning tasks
    - No additional training required
    - Works with any pre-trained model
    - Scales with model size
    """

    def __init__(
        self,
        num_samples: int = 10,
        temperature: float = 0.7,
        answer_extractor: Optional[Callable[[str], str]] = None,
        min_confidence: float = 0.5,
        llm_provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
        use_llm: bool = True
    ):
        """
        Args:
            num_samples: Number of reasoning chains to generate (5-40 recommended)
            temperature: Sampling temperature for diversity (0.5-0.8 recommended)
            answer_extractor: Custom function to extract answers from responses
            min_confidence: Minimum confidence threshold to accept result
            llm_provider: Proveedor LLM ('anthropic' o 'openai')
            model: Modelo específico a usar
            use_llm: Si True, usa LLM real; si False, requiere generator_fn
        """
        self.num_samples = num_samples
        self.temperature = temperature
        self.answer_extractor = answer_extractor or self._default_answer_extractor
        self.min_confidence = min_confidence
        self.use_llm = use_llm and LLM_AVAILABLE

        if self.use_llm:
            llm_config = {
                "llm_provider": llm_provider,
                "model": model
            }
            self.llm = LLMGenerator(config=llm_config)
        else:
            self.llm = None

    def solve_with_consistency(
        self,
        prompt: str,
        generator_fn: Optional[Callable[[str, float], str]] = None,
        context: Optional[Dict] = None
    ) -> SelfConsistencyResult:
        """
        Solve problem using self-consistency decoding.

        Args:
            prompt: Problem prompt (should include Chain-of-Thought instruction)
            generator_fn: Optional function that generates response given (prompt, temperature).
                         If None and use_llm=True, uses internal LLM.
            context: Optional context for answer extraction

        Returns:
            SelfConsistencyResult with final answer and metrics
        """
        # Determine which generator to use
        if generator_fn is None:
            if self.use_llm and self.llm:
                generator_fn = self._llm_generator_wrapper
            else:
                raise ValueError("No generator_fn provided and LLM not available. Pass generator_fn or enable use_llm.")

        print(f"[Self-Consistency] Generating {self.num_samples} reasoning paths...")

        # Step 1: Generate multiple reasoning chains
        reasoning_paths = []
        for i in range(self.num_samples):
            # Generate response with specified temperature for diversity
            response = generator_fn(prompt, self.temperature)

            # Extract answer from response
            extracted_answer = self.answer_extractor(response)

            # Parse reasoning steps
            steps = self._extract_reasoning_steps(response)

            reasoning_path = ReasoningPath(
                full_response=response,
                extracted_answer=extracted_answer,
                reasoning_steps=steps
            )
            reasoning_paths.append(reasoning_path)

            print(f"[Self-Consistency] Path {i+1}/{self.num_samples}: Answer='{extracted_answer}'")

        # Step 2: Apply majority voting
        answers = [path.extracted_answer for path in reasoning_paths]
        vote_counts = Counter(answers)

        # Get most common answer
        most_common_answer, vote_count = vote_counts.most_common(1)[0]

        # Calculate confidence (percentage of votes for winning answer)
        confidence_score = vote_count / self.num_samples

        # Calculate consensus strength (how dominant is the winning answer)
        consensus_strength = self._calculate_consensus_strength(vote_counts)

        print(f"[Self-Consistency] Final answer: '{most_common_answer}'")
        print(f"[Self-Consistency] Confidence: {confidence_score:.2%} ({vote_count}/{self.num_samples} votes)")
        print(f"[Self-Consistency] Consensus strength: {consensus_strength:.2f}")

        result = SelfConsistencyResult(
            final_answer=most_common_answer,
            confidence_score=confidence_score,
            vote_distribution=dict(vote_counts),
            all_paths=reasoning_paths,
            consensus_strength=consensus_strength,
            total_samples=self.num_samples
        )

        # Check if confidence meets threshold
        if confidence_score < self.min_confidence:
            print(f"[Self-Consistency] WARNING: Confidence {confidence_score:.2%} below threshold {self.min_confidence:.2%}")
            print(f"[Self-Consistency] Vote distribution: {dict(vote_counts)}")

        return result

    def _llm_generator_wrapper(self, prompt: str, temperature: float) -> str:
        """Wrapper to make LLMGenerator compatible with generator_fn signature."""
        if not self.llm:
            raise RuntimeError("LLM not initialized")

        # LLMGenerator's _call_llm accepts prompt but not temperature directly
        # We'll rely on the temperature set in the config or pass it if supported
        try:
            # Try to call with temperature if the method supports it
            response = self.llm._call_llm(prompt, temperature=temperature)
        except TypeError:
            # Fallback: call without temperature parameter
            response = self.llm._call_llm(prompt)

        return response

    def _default_answer_extractor(self, response: str) -> str:
        """
        Default answer extraction using pattern matching.

        Looks for common patterns:
        - "Respuesta: X"
        - "La respuesta es X"
        - "Answer: X"
        - "Por tanto, X"
        - "Therefore, X"
        """
        patterns = [
            r"Respuesta final?:\s*(.+)",
            r"La respuesta es\s+(.+)",
            r"Answer:\s*(.+)",
            r"Por tanto,?\s*(.+)",
            r"Therefore,?\s*(.+)",
            r"Result:\s*(.+)",
            r"Resultado:\s*(.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                answer = match.group(1).strip()
                # Clean up common endings
                answer = re.sub(r'[\.;,]$', '', answer)
                return answer.strip()

        # If no pattern found, try last non-empty line
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if lines:
            return lines[-1]

        return response.strip()

    def _extract_reasoning_steps(self, response: str) -> List[str]:
        """Extract individual reasoning steps from response."""
        steps = []

        # Look for numbered steps: "Paso 1:", "Step 1:", "1.", etc.
        step_pattern = r'(?:Paso|Step)\s*\d+:?\s*(.+)|^\d+\.\s*(.+)'

        for line in response.split('\n'):
            match = re.match(step_pattern, line.strip(), re.IGNORECASE)
            if match:
                step_text = match.group(1) or match.group(2)
                if step_text:
                    steps.append(step_text.strip())

        # If no explicit steps found, split by sentences
        if not steps:
            steps = [s.strip() for s in response.split('.') if s.strip()]

        return steps

    def _calculate_consensus_strength(self, vote_counts: Counter) -> float:
        """
        Calculate how strong the consensus is.

        Returns:
        - 1.0: Perfect consensus (all votes for one answer)
        - 0.5-1.0: Strong consensus (one answer clearly dominates)
        - 0.0-0.5: Weak consensus (votes distributed)
        """
        if not vote_counts:
            return 0.0

        total_votes = sum(vote_counts.values())
        sorted_counts = sorted(vote_counts.values(), reverse=True)

        if len(sorted_counts) == 1:
            # Perfect consensus
            return 1.0

        # Ratio of top answer to second answer
        top_votes = sorted_counts[0]
        second_votes = sorted_counts[1]

        # Normalized strength: how much better is top vs second
        strength = (top_votes - second_votes) / total_votes

        return strength

    def analyze_disagreements(
        self,
        result: SelfConsistencyResult,
        top_n: int = 3
    ) -> Dict:
        """
        Analyze why different reasoning paths arrived at different answers.

        Returns analysis of disagreements to help improve prompts.
        """
        # Group paths by answer
        paths_by_answer = {}
        for path in result.all_paths:
            answer = path.extracted_answer
            if answer not in paths_by_answer:
                paths_by_answer[answer] = []
            paths_by_answer[answer].append(path)

        # Analyze top N answers
        top_answers = sorted(
            paths_by_answer.keys(),
            key=lambda a: len(paths_by_answer[a]),
            reverse=True
        )[:top_n]

        analysis = {
            'top_answers': {},
            'common_reasoning_patterns': [],
            'divergence_points': []
        }

        for answer in top_answers:
            paths = paths_by_answer[answer]

            # Analyze reasoning patterns for this answer
            all_steps = []
            for path in paths:
                all_steps.extend(path.reasoning_steps)

            # Find common reasoning elements
            step_frequency = Counter(all_steps)
            common_steps = step_frequency.most_common(5)

            analysis['top_answers'][answer] = {
                'vote_count': len(paths),
                'percentage': len(paths) / result.total_samples,
                'common_reasoning': [step for step, count in common_steps],
                'example_path': paths[0].full_response[:200] + "..."
            }

        return analysis

    def get_confidence_interpretation(self, confidence: float) -> str:
        """Get human-readable interpretation of confidence score."""
        if confidence >= 0.9:
            return "Very High (strong agreement)"
        elif confidence >= 0.7:
            return "High (good agreement)"
        elif confidence >= 0.5:
            return "Medium (moderate agreement)"
        elif confidence >= 0.3:
            return "Low (weak agreement)"
        else:
            return "Very Low (no clear consensus)"

    def should_trust_result(self, result: SelfConsistencyResult) -> Tuple[bool, str]:
        """
        Determine if result should be trusted based on multiple factors.

        Returns:
            (should_trust, reasoning)
        """
        reasons = []

        # Check confidence threshold
        if result.confidence_score < self.min_confidence:
            reasons.append(f"Confidence {result.confidence_score:.2%} below threshold {self.min_confidence:.2%}")

        # Check consensus strength
        if result.consensus_strength < 0.3:
            reasons.append(f"Weak consensus (strength={result.consensus_strength:.2f})")

        # Check if answer is too short (might be incomplete)
        if len(result.final_answer.strip()) < 3:
            reasons.append("Answer suspiciously short")

        # Check vote distribution
        if len(result.vote_distribution) > len(result.all_paths) * 0.5:
            reasons.append("High answer diversity (many different answers)")

        should_trust = len(reasons) == 0

        if should_trust:
            reasoning = f"High quality result: {result.confidence_score:.2%} confidence, {result.consensus_strength:.2f} consensus"
        else:
            reasoning = "Concerns: " + "; ".join(reasons)

        return should_trust, reasoning


def create_chain_of_thought_prompt(problem: str, domain: str = "general") -> str:
    """
    Create a Chain-of-Thought prompt for use with Self-Consistency.

    Self-Consistency works best with CoT prompts that encourage step-by-step reasoning.
    """
    templates = {
        "math": f"""
{problem}

Piensa paso a paso:
Paso 1: Identifica qué información tienes
Paso 2: Determina qué operaciones necesitas realizar
Paso 3: Ejecuta los cálculos
Paso 4: Verifica tu respuesta

Respuesta final: [tu respuesta aquí]
""",
        "code_review": f"""
Analiza este código para identificar problemas:

{problem}

Analiza paso a paso:
Paso 1: Revisa sintaxis y estructura
Paso 2: Identifica posibles bugs
Paso 3: Evalúa seguridad
Paso 4: Considera performance

Respuesta final: [Lista de issues priorizados]
""",
        "debugging": f"""
Este error ocurre en el sistema:

{problem}

Diagnostica paso a paso:
Paso 1: Analiza los síntomas
Paso 2: Identifica posibles causas
Paso 3: Evalúa probabilidad de cada causa
Paso 4: Determina causa raíz más probable

Respuesta final: [Causa raíz identificada]
""",
        "general": f"""
{problem}

Piensa paso a paso y muestra tu razonamiento:
Paso 1: [Comprende el problema]
Paso 2: [Analiza las opciones]
Paso 3: [Evalúa cada opción]
Paso 4: [Llega a una conclusión]

Respuesta final: [tu respuesta aquí]
"""
    }

    return templates.get(domain, templates["general"])


def main():
    """Example usage of Self-Consistency Decoding."""
    print("Self-Consistency Decoding Agent - Example\n")
    print("=" * 70)

    # Example: Math problem solving
    print("\n[Example 1] Math Problem with Self-Consistency\n")

    problem = """
Sarah tiene 23 manzanas. Compra 3 bolsas más, cada una con 8 manzanas.
Luego regala 11 manzanas a sus amigos.
¿Cuántas manzanas le quedan?
"""

    # Create Chain-of-Thought prompt
    prompt = create_chain_of_thought_prompt(problem, domain="math")

    # Simulated generator function (in production, this would call LLM)
    def mock_generator(prompt: str, temperature: float) -> str:
        """Mock generator that simulates multiple reasoning paths."""
        import random
        random.seed(hash(prompt + str(temperature) + str(random.random())))

        # Simulate different reasoning paths
        paths = [
            """
Paso 1: Sarah empieza con 23 manzanas
Paso 2: Compra 3 bolsas × 8 manzanas = 24 manzanas más
Paso 3: Total después de comprar: 23 + 24 = 47 manzanas
Paso 4: Regala 11 manzanas: 47 - 11 = 36 manzanas
Respuesta final: 36
""",
            """
Paso 1: Manzanas iniciales: 23
Paso 2: Manzanas nuevas: 3 × 8 = 24
Paso 3: Total: 23 + 24 = 47
Paso 4: Después de regalar: 47 - 11 = 36
Respuesta final: 36
""",
            """
Paso 1: 23 manzanas al inicio
Paso 2: 3 bolsas de 8 = 3 × 8 = 24 manzanas
Paso 3: 23 + 24 = 47 manzanas totales
Paso 4: Regala 11: 47 - 11 = 36
Respuesta final: 36
""",
            """
Paso 1: Sarah tiene 23 manzanas
Paso 2: Compra 3 × 8 = 22 manzanas [ERROR]
Paso 3: Total: 23 + 22 = 45
Paso 4: Regala 11: 45 - 11 = 34
Respuesta final: 34
"""
        ]

        # Return random path with some probability of error
        if random.random() < 0.2:  # 20% chance of getting wrong path
            return paths[3]
        else:
            return random.choice(paths[:3])

    # Initialize Self-Consistency agent
    agent = SelfConsistencyAgent(num_samples=10, temperature=0.7)

    # Solve with self-consistency
    result = agent.solve_with_consistency(prompt, mock_generator)

    # Display results
    print("\n" + "=" * 70)
    print("SELF-CONSISTENCY RESULTS")
    print("=" * 70)

    print(f"\nFinal Answer: {result.final_answer}")
    print(f"Confidence: {result.confidence_score:.2%}")
    print(f"Confidence Level: {agent.get_confidence_interpretation(result.confidence_score)}")
    print(f"Consensus Strength: {result.consensus_strength:.2f}")

    print(f"\nVote Distribution:")
    for answer, count in sorted(result.vote_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = count / result.total_samples * 100
        print(f"  '{answer}': {count} votes ({percentage:.1f}%)")

    # Check if result should be trusted
    should_trust, reasoning = agent.should_trust_result(result)
    print(f"\nShould trust result: {should_trust}")
    print(f"Reasoning: {reasoning}")

    # Analyze disagreements
    print("\n" + "=" * 70)
    print("DISAGREEMENT ANALYSIS")
    print("=" * 70)

    analysis = agent.analyze_disagreements(result, top_n=2)
    for answer, details in analysis['top_answers'].items():
        print(f"\nAnswer: '{answer}'")
        print(f"  Votes: {details['vote_count']} ({details['percentage']:.1%})")
        print(f"  Common reasoning: {details['common_reasoning'][:2]}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
