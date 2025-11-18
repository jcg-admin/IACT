#!/usr/bin/env python3
"""
Auto-CoT (Automatic Chain-of-Thought) Agent

Implementa la técnica Auto-CoT de Zhang et al. (2022) para generar
automáticamente ejemplos de razonamiento paso a paso sin intervención humana.

Basado en: "Automatic Chain of Thought Prompting in Large Language Models"
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import re

# Add parent paths for LLMGenerator import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMGenerator = None

# Optional dependencies for clustering
try:
    import numpy as np
    from sklearn.cluster import KMeans
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    KMeans = None


@dataclass
class Question:
    """Representa una pregunta del dominio."""
    text: str
    embedding: Optional[Any] = None  # np.ndarray when numpy available
    cluster_id: Optional[int] = None


@dataclass
class Demonstration:
    """Representa una demostración CoT generada automáticamente."""
    question: str
    reasoning: str
    answer: str
    quality_score: float = 0.0


class AutoCoTAgent:
    """
    Agente que implementa Auto-CoT para generar demostraciones automáticas.

    Proceso de 2 etapas:
    1. Question Clustering: Agrupa preguntas similares
    2. Demonstration Sampling: Genera CoT con Zero-Shot para cada cluster
    """

    def __init__(
        self,
        k_clusters: int = 5,
        max_demonstrations: int = 10,
        llm_provider: str = "anthropic",
        model: str = "claude-sonnet-4-5-20250929",
        use_llm: bool = True
    ):
        """
        Args:
            k_clusters: Número de clusters para agrupar preguntas
            max_demonstrations: Máximo de demostraciones a generar
            llm_provider: Proveedor LLM ('anthropic' o 'openai')
            model: Modelo específico a usar
            use_llm: Si True, usa LLM real; si False, usa templates
        """
        self.k_clusters = k_clusters
        self.max_demonstrations = max_demonstrations
        self.demonstrations: List[Demonstration] = []
        self.use_llm = use_llm and LLM_AVAILABLE

        if self.use_llm:
            llm_config = {
                "llm_provider": llm_provider,
                "model": model
            }
            self.llm = LLMGenerator(config=llm_config)
        else:
            self.llm = None

    def generate_demonstrations(
        self,
        questions: List[str],
        domain: str = "general"
    ) -> List[Demonstration]:
        """
        Genera demostraciones Auto-CoT desde un conjunto de preguntas.

        Args:
            questions: Lista de preguntas del dominio
            domain: Nombre del dominio para contexto

        Returns:
            Lista de demostraciones generadas
        """
        print(f"[Auto-CoT] Generating demonstrations for domain: {domain}")
        print(f"[Auto-CoT] Input: {len(questions)} questions")

        # Etapa 1: Question Clustering
        question_objects = [Question(text=q) for q in questions]
        clustered_questions = self._cluster_questions(question_objects)

        print(f"[Auto-CoT] Clustered into {self.k_clusters} groups")

        # Etapa 2: Demonstration Sampling
        representative_questions = self._select_representatives(clustered_questions)

        print(f"[Auto-CoT] Selected {len(representative_questions)} representative questions")

        demonstrations = []
        for i, question in enumerate(representative_questions, 1):
            print(f"[Auto-CoT] Generating demonstration {i}/{len(representative_questions)}")

            demo = self._generate_single_demonstration(question, domain)

            if demo and self._validate_demonstration(demo):
                demonstrations.append(demo)
            else:
                print(f"[Auto-CoT] Skipped low-quality demonstration")

        self.demonstrations = demonstrations
        print(f"[Auto-CoT] Generated {len(demonstrations)} high-quality demonstrations")

        return demonstrations

    def _cluster_questions(self, questions: List[Question]) -> List[Question]:
        """
        Agrupa preguntas usando k-means clustering.

        En implementación real, usarías embeddings de BERT/sentence-transformers.
        Esta versión simplificada usa características básicas.
        """
        if not NUMPY_AVAILABLE:
            # Fallback: simple round-robin clustering without ML
            k = min(self.k_clusters, len(questions))
            for i, q in enumerate(questions):
                q.cluster_id = i % max(k, 1)
                q.embedding = None
            return questions

        # Generar embeddings simplificados (en producción: usar BERT)
        for q in questions:
            q.embedding = self._simple_embedding(q.text)

        # Aplicar k-means
        embeddings = np.array([q.embedding for q in questions])

        # Ajustar k si hay menos preguntas que clusters
        k = min(self.k_clusters, len(questions))

        if k < 2:
            # Sin clustering necesario
            for q in questions:
                q.cluster_id = 0
            return questions

        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        for i, q in enumerate(questions):
            q.cluster_id = int(cluster_labels[i])

        return questions

    def _simple_embedding(self, text: str) -> Any:  # np.ndarray when available
        """
        Genera embedding simplificado de texto.

        En producción: usar sentence-transformers o API de embeddings.
        Esta versión usa características léxicas básicas.
        """
        features = []

        # Longitud
        features.append(len(text.split()))

        # Presencia de palabras clave técnicas
        tech_keywords = ['code', 'test', 'function', 'class', 'error', 'bug', 'api']
        features.append(sum(1 for kw in tech_keywords if kw in text.lower()))

        # Presencia de símbolos de código
        code_symbols = ['(', ')', '{', '}', '[', ']', ';']
        features.append(sum(1 for sym in code_symbols if sym in text))

        # Complejidad (preguntas vs afirmaciones)
        features.append(1 if '?' in text else 0)

        # Tipo de pregunta
        question_words = ['what', 'how', 'why', 'when', 'where', 'which']
        features.append(sum(1 for qw in question_words if qw in text.lower()))

        # Normalizar
        features_array = np.array(features, dtype=float)
        norm = np.linalg.norm(features_array)
        if norm > 0:
            features_array = features_array / norm

        # Padding para tener dimensión fija
        target_dim = 10
        if len(features_array) < target_dim:
            features_array = np.pad(
                features_array,
                (0, target_dim - len(features_array)),
                mode='constant'
            )

        return features_array

    def _select_representatives(
        self,
        questions: List[Question]
    ) -> List[str]:
        """
        Selecciona pregunta representativa de cada cluster.

        Selecciona la pregunta más cercana al centroide del cluster.
        """
        representatives = []

        for cluster_id in range(self.k_clusters):
            cluster_questions = [q for q in questions if q.cluster_id == cluster_id]

            if not cluster_questions:
                continue

            # Calcular centroide del cluster
            embeddings = np.array([q.embedding for q in cluster_questions])
            centroid = np.mean(embeddings, axis=0)

            # Encontrar pregunta más cercana al centroide
            min_distance = float('inf')
            representative = None

            for q in cluster_questions:
                distance = np.linalg.norm(q.embedding - centroid)
                if distance < min_distance:
                    min_distance = distance
                    representative = q

            if representative:
                representatives.append(representative.text)

        # Limitar al máximo de demostraciones
        return representatives[:self.max_demonstrations]

    def _generate_single_demonstration(
        self,
        question: str,
        domain: str
    ) -> Optional[Demonstration]:
        """
        Genera una demostración CoT para una pregunta usando Zero-Shot CoT.

        Si use_llm=True, llama a LLM real. Sino, usa templates.
        """
        if self.use_llm and self.llm:
            return self._generate_with_llm(question, domain)
        else:
            return self._generate_with_template(question, domain)

    def _generate_with_llm(self, question: str, domain: str) -> Optional[Demonstration]:
        """Genera demostración usando LLM con Zero-Shot CoT."""
        try:
            # Zero-Shot CoT prompt
            prompt = f"""You are an expert in {domain}. Answer the following question using step-by-step reasoning.

Question: {question}

Instructions:
1. Think through the problem step by step
2. Show your reasoning process clearly
3. Provide a final answer at the end

Format your response as:
REASONING: [Your step-by-step reasoning]
ANSWER: [Your final answer]

Let's think step by step."""

            llm_response = self.llm._call_llm(prompt)

            # Parse response to extract reasoning and answer
            reasoning, answer = self._parse_llm_response(llm_response, question, domain)

            return Demonstration(
                question=question,
                reasoning=reasoning,
                answer=answer,
                quality_score=self._score_demonstration(question, reasoning, answer)
            )

        except Exception as e:
            print(f"[Auto-CoT] LLM generation failed: {e}, falling back to template")
            return self._generate_with_template(question, domain)

    def _parse_llm_response(self, llm_response: str, question: str, domain: str) -> Tuple[str, str]:
        """Parse LLM response to extract reasoning and answer."""
        # Try to find REASONING: and ANSWER: sections
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?=ANSWER:|$)', llm_response, re.DOTALL | re.IGNORECASE)
        answer_match = re.search(r'ANSWER:\s*(.+?)$', llm_response, re.DOTALL | re.IGNORECASE)

        if reasoning_match and answer_match:
            reasoning = reasoning_match.group(1).strip()
            answer = answer_match.group(1).strip()
        else:
            # Fallback: treat entire response as reasoning, extract last sentence as answer
            lines = llm_response.strip().split('\n')
            reasoning = llm_response.strip()
            # Try to find a conclusive sentence
            answer_candidates = [line for line in lines if any(marker in line.lower() for marker in ['therefore', 'thus', 'so', 'answer', 'conclusion'])]
            if answer_candidates:
                answer = answer_candidates[-1].strip()
            else:
                answer = lines[-1].strip() if lines else "See reasoning above"

        return reasoning, answer

    def _generate_with_template(self, question: str, domain: str) -> Demonstration:
        """Genera demostración usando templates (fallback)."""
        reasoning = self._generate_reasoning_template(question, domain)
        answer = self._extract_answer_from_reasoning(reasoning)

        return Demonstration(
            question=question,
            reasoning=reasoning,
            answer=answer,
            quality_score=self._score_demonstration(question, reasoning, answer)
        )

    def _generate_reasoning_template(self, question: str, domain: str) -> str:
        """
        Genera template de razonamiento estructurado.

        En producción: esto vendría del LLM.
        """
        # Template básico para diferentes dominios
        if "test" in question.lower() or "testing" in domain.lower():
            return f"""Let's think step by step.
First, I need to understand what needs to be tested: {self._extract_subject(question)}
Next, I'll identify the test cases: happy path, edge cases, and error cases.
Then, I'll structure the test with setup, execution, and assertions.
Finally, I'll validate the test covers all requirements."""

        elif "code" in question.lower() or "review" in question.lower():
            return f"""Let's analyze this step by step.
First, I'll examine the code structure and design patterns.
Next, I'll check for potential bugs or anti-patterns.
Then, I'll evaluate performance and security implications.
Finally, I'll provide actionable recommendations."""

        else:
            return f"""Let's approach this systematically.
First, I'll break down the problem into components.
Next, I'll analyze each component individually.
Then, I'll identify dependencies and relationships.
Finally, I'll synthesize a comprehensive solution."""

    def _extract_subject(self, question: str) -> str:
        """Extrae el sujeto principal de la pregunta."""
        # Simplificado: retorna las primeras palabras relevantes
        words = question.split()
        return ' '.join(words[:5]) if len(words) > 5 else question

    def _extract_answer_from_reasoning(self, reasoning: str) -> str:
        """Extrae la respuesta final del razonamiento."""
        lines = reasoning.strip().split('\n')
        if lines:
            return lines[-1].replace('Finally,', '').strip()
        return "See reasoning above"

    def _validate_demonstration(self, demo: Demonstration) -> bool:
        """
        Valida calidad de una demostración.

        Aplica filtros de calidad mencionados en Zhang et al. (2022).
        """
        # Filtro 1: Longitud de pregunta (< 60 tokens)
        if len(demo.question.split()) > 60:
            return False

        # Filtro 2: Pasos de razonamiento (< 5 pasos explícitos)
        steps = self._count_reasoning_steps(demo.reasoning)
        if steps > 5:
            return False

        # Filtro 3: Calidad mínima
        if demo.quality_score < 0.5:
            return False

        # Filtro 4: Razonamiento no vacío
        if len(demo.reasoning.split()) < 20:
            return False

        return True

    def _count_reasoning_steps(self, reasoning: str) -> int:
        """Cuenta número de pasos explícitos en el razonamiento."""
        step_indicators = ['first', 'next', 'then', 'finally', 'step', 'now']
        count = sum(1 for indicator in step_indicators if indicator in reasoning.lower())
        return count

    def _score_demonstration(
        self,
        question: str,
        reasoning: str,
        answer: str
    ) -> float:
        """
        Asigna score de calidad a una demostración.

        Returns:
            Float entre 0.0 y 1.0
        """
        score = 0.0

        # Factor 1: Razonamiento tiene estructura clara (0.3)
        if self._has_clear_structure(reasoning):
            score += 0.3

        # Factor 2: Respuesta está presente y no vacía (0.2)
        if answer and len(answer.split()) > 3:
            score += 0.2

        # Factor 3: Razonamiento es proporcionado a la pregunta (0.2)
        length_ratio = len(reasoning.split()) / max(len(question.split()), 1)
        if 2 <= length_ratio <= 10:
            score += 0.2

        # Factor 4: Razonamiento contiene palabras de transición (0.15)
        transitions = ['because', 'therefore', 'thus', 'so', 'since']
        if any(t in reasoning.lower() for t in transitions):
            score += 0.15

        # Factor 5: Razonamiento no se repite (0.15)
        if not self._has_repetition(reasoning):
            score += 0.15

        return min(score, 1.0)

    def _has_clear_structure(self, reasoning: str) -> bool:
        """Verifica si el razonamiento tiene estructura clara."""
        structure_markers = ['first', 'second', 'next', 'then', 'finally', 'step']
        return sum(1 for marker in structure_markers if marker in reasoning.lower()) >= 2

    def _has_repetition(self, reasoning: str) -> bool:
        """Detecta repetición excesiva en el razonamiento."""
        sentences = reasoning.split('.')
        if len(sentences) < 2:
            return False

        # Verificar si hay oraciones muy similares
        for i, sent1 in enumerate(sentences[:-1]):
            for sent2 in sentences[i+1:]:
                # Similitud simple basada en palabras compartidas
                words1 = set(sent1.lower().split())
                words2 = set(sent2.lower().split())

                if len(words1) > 0 and len(words2) > 0:
                    overlap = len(words1 & words2) / min(len(words1), len(words2))
                    if overlap > 0.8:  # 80% de overlap = repetición
                        return True

        return False

    def create_few_shot_prompt(
        self,
        new_question: str,
        max_examples: int = 5
    ) -> str:
        """
        Crea prompt few-shot usando demostraciones generadas.

        Args:
            new_question: Nueva pregunta a resolver
            max_examples: Máximo de ejemplos a incluir

        Returns:
            Prompt completo con ejemplos + nueva pregunta
        """
        if not self.demonstrations:
            raise ValueError("No demonstrations generated. Call generate_demonstrations() first.")

        prompt = "Here are some examples:\n\n"

        # Incluir las mejores demostraciones
        sorted_demos = sorted(
            self.demonstrations,
            key=lambda d: d.quality_score,
            reverse=True
        )

        for i, demo in enumerate(sorted_demos[:max_examples], 1):
            prompt += f"Example {i}:\n"
            prompt += f"Q: {demo.question}\n"
            prompt += f"A: {demo.reasoning}\n"
            prompt += f"Answer: {demo.answer}\n\n"

        prompt += "Now solve this:\n"
        prompt += f"Q: {new_question}\n"
        prompt += "A: Let's think step by step.\n"

        return prompt

    def save_demonstrations(self, output_path: Path):
        """Guarda demostraciones a archivo JSON."""
        data = [
            {
                'question': d.question,
                'reasoning': d.reasoning,
                'answer': d.answer,
                'quality_score': d.quality_score
            }
            for d in self.demonstrations
        ]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"[Auto-CoT] Saved {len(data)} demonstrations to {output_path}")

    def load_demonstrations(self, input_path: Path):
        """Carga demostraciones desde archivo JSON."""
        with open(input_path) as f:
            data = json.load(f)

        self.demonstrations = [
            Demonstration(
                question=d['question'],
                reasoning=d['reasoning'],
                answer=d['answer'],
                quality_score=d.get('quality_score', 0.0)
            )
            for d in data
        ]

        print(f"[Auto-CoT] Loaded {len(self.demonstrations)} demonstrations from {input_path}")


def main():
    """Example usage of Auto-CoT Agent."""
    print("Auto-CoT Agent - Example Usage\n")

    # Example: Code Review domain
    code_review_questions = [
        "How to identify potential security vulnerabilities in this API endpoint?",
        "What performance optimizations can be applied to this database query?",
        "Is this function following SOLID principles?",
        "How to refactor this complex nested loop?",
        "What are the code smells in this class design?",
        "How to improve test coverage for this module?",
        "Is this error handling robust enough?",
        "What naming conventions are violated here?"
    ]

    # Generate demonstrations
    agent = AutoCoTAgent(k_clusters=4, max_demonstrations=6)
    demonstrations = agent.generate_demonstrations(
        code_review_questions,
        domain="code_review"
    )

    # Create few-shot prompt for new question
    new_question = "How to optimize this slow-running SQL query?"
    prompt = agent.create_few_shot_prompt(new_question, max_examples=3)

    print("\n" + "="*70)
    print("GENERATED FEW-SHOT PROMPT:")
    print("="*70)
    print(prompt)

    # Save demonstrations
    output_path = Path("auto_cot_code_review_demos.json")
    agent.save_demonstrations(output_path)


if __name__ == "__main__":
    main()
