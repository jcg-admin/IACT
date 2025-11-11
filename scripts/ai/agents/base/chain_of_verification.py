#!/usr/bin/env python3
"""
Chain-of-Verification (CoVe) Agent

Implementa Chain-of-Verification de Dhuliawala et al. (2023) para reducir
alucinaciones y errores mediante verificación sistemática.

Basado en: "Chain-of-Verification Reduces Hallucination in Large Language Models" (Meta AI, 2023)
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from generators.llm_generator import LLMGenerator


class VerificationStatus(Enum):
    """Estado de verificación."""
    VERIFIED = "verified"
    FAILED = "failed"
    CORRECTED = "corrected"
    UNCERTAIN = "uncertain"


@dataclass
class Verification:
    """Representa una verificación individual."""
    question: str
    answer: str
    status: VerificationStatus
    original_claim: str
    correction: Optional[str] = None


@dataclass
class VerifiedResponse:
    """Respuesta verificada completa."""
    initial_response: str
    verifications: List[Verification]
    final_response: str
    confidence_score: float
    corrections_made: int


class ChainOfVerificationAgent:
    """
    Agente que implementa Chain-of-Verification.

    Proceso de 5 fases:
    1. Generate baseline response
    2. Plan verification questions
    3. Answer verification questions independently
    4. Generate final verified response
    5. Calculate confidence score
    """

    def __init__(
        self,
        verify_threshold: float = 0.7,
        llm_provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
        use_llm: bool = True
    ):
        """
        Args:
            verify_threshold: Umbral mínimo de confianza para aceptar respuesta
            llm_provider: Proveedor de LLM (anthropic o openai)
            model: Modelo a usar
            use_llm: Si True, usa LLM; si False, usa heurísticas
        """
        self.verify_threshold = verify_threshold
        self.use_llm = use_llm

        if use_llm:
            self.llm = LLMGenerator(config={
                "llm_provider": llm_provider,
                "model": model
            })
        else:
            self.llm = None

    def verify_response(
        self,
        question: str,
        initial_response: str,
        context: Optional[Dict] = None
    ) -> VerifiedResponse:
        """
        Verifica una respuesta usando Chain-of-Verification.

        Args:
            question: Pregunta original
            initial_response: Respuesta inicial a verificar
            context: Contexto adicional para verificación

        Returns:
            VerifiedResponse con resultado de verificación
        """
        print(f"[CoVe] Verifying response to: {question[:60]}...")

        # Phase 1: Ya tenemos baseline response (initial_response)

        # Phase 2: Plan verification questions
        verification_questions = self._plan_verification_questions(
            question,
            initial_response,
            context
        )

        print(f"[CoVe] Generated {len(verification_questions)} verification questions")

        # Phase 3: Answer verification questions independently
        verifications = []
        for vq in verification_questions:
            verification = self._answer_verification_question(
                vq,
                initial_response,
                context
            )
            verifications.append(verification)

        # Phase 4: Generate final verified response
        final_response = self._generate_final_response(
            question,
            initial_response,
            verifications
        )

        # Phase 5: Calculate confidence
        confidence = self._calculate_confidence(verifications)
        corrections = sum(1 for v in verifications if v.status == VerificationStatus.CORRECTED)

        print(f"[CoVe] Verification complete: {corrections} corrections, confidence={confidence:.2f}")

        return VerifiedResponse(
            initial_response=initial_response,
            verifications=verifications,
            final_response=final_response,
            confidence_score=confidence,
            corrections_made=corrections
        )

    def _plan_verification_questions(
        self,
        question: str,
        response: str,
        context: Optional[Dict]
    ) -> List[Dict[str, str]]:
        """
        Genera preguntas de verificación para claims en la respuesta.

        Strategy: Identificar claims específicos y generar preguntas verificables.
        """
        verification_questions = []

        # Extraer claims de la respuesta
        claims = self._extract_claims(response)

        for claim in claims:
            # Generar pregunta de verificación para cada claim
            vq = self._create_verification_question(claim, context)
            if vq:
                verification_questions.append({
                    'question': vq,
                    'original_claim': claim
                })

        return verification_questions

    def _extract_claims(self, response: str) -> List[str]:
        """
        Extrae claims verificables de la respuesta.

        En producción: usar análisis semántico o LLM.
        Esta versión simplificada extrae oraciones con patrones específicos.
        """
        claims = []

        # Split por oraciones
        sentences = [s.strip() for s in response.split('.') if s.strip()]

        # Patrones que indican claims verificables
        claim_indicators = [
            'is', 'are', 'must', 'should', 'will', 'requires', 'needs',
            'validates', 'checks', 'ensures', 'prevents', 'allows'
        ]

        for sentence in sentences:
            words = sentence.lower().split()
            if any(indicator in words for indicator in claim_indicators):
                # Esta oración hace un claim verificable
                claims.append(sentence)

        return claims[:5]  # Limitar a 5 claims más importantes

    def _create_verification_question(
        self,
        claim: str,
        context: Optional[Dict]
    ) -> Optional[str]:
        """
        Crea pregunta de verificación para un claim específico.

        Strategies:
        - Fact checking: ¿Es X verdadero/correcto?
        - Consistency: ¿Es X consistente con Y?
        - Completeness: ¿Falta algo en X?
        - Accuracy: ¿Son correctos los detalles de X?
        """
        # Detectar tipo de claim y generar pregunta apropiada
        claim_lower = claim.lower()

        if 'must' in claim_lower or 'should' in claim_lower:
            # Requirement claim
            return f"Is this requirement accurate and complete: {claim}?"

        elif 'validates' in claim_lower or 'checks' in claim_lower:
            # Validation claim
            return f"Does this validation cover all necessary cases: {claim}?"

        elif 'prevents' in claim_lower or 'ensures' in claim_lower:
            # Security/safety claim
            return f"Are there edge cases not covered by: {claim}?"

        elif 'is' in claim_lower or 'are' in claim_lower:
            # Factual claim
            return f"Is this statement factually correct: {claim}?"

        else:
            # Generic verification
            return f"Is this claim accurate and complete: {claim}?"

    def _answer_verification_question(
        self,
        verification_q: Dict[str, str],
        original_response: str,
        context: Optional[Dict]
    ) -> Verification:
        """
        Responde pregunta de verificación independientemente.

        Key: Responder SIN mirar la respuesta original para evitar sesgo.
        """
        question = verification_q['question']
        original_claim = verification_q['original_claim']

        if self.use_llm and self.llm:
            # Usar LLM para verificación
            return self._answer_with_llm(question, original_claim, context)
        else:
            # Fallback a heurísticas
            return self._answer_with_heuristics(question, original_claim, context)

    def _answer_with_llm(
        self,
        question: str,
        original_claim: str,
        context: Optional[Dict]
    ) -> Verification:
        """Verifica usando LLM."""
        # Construir prompt sin mostrar la respuesta original (evitar sesgo)
        context_str = ""
        if context:
            context_str = f"Context: {str(context)}\n\n"

        prompt = f"""You are a fact-checker verifying claims.

{context_str}Verification Question: {question}

Original Claim to verify: {original_claim}

Analyze the claim and answer:
1. Is the claim accurate?
2. Is it complete?
3. Are there any issues or missing aspects?

Respond in JSON format:
{{
  "status": "verified" | "corrected" | "failed",
  "answer": "Detailed analysis",
  "issues": ["issue1", "issue2", ...],
  "correction": "Corrected claim if needed (null if verified)"
}}

Response:"""

        try:
            response = self.llm._call_llm(prompt)

            # Parsear JSON
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))

                status_map = {
                    "verified": VerificationStatus.VERIFIED,
                    "corrected": VerificationStatus.CORRECTED,
                    "failed": VerificationStatus.FAILED,
                    "uncertain": VerificationStatus.UNCERTAIN
                }

                return Verification(
                    question=question,
                    answer=data.get("answer", ""),
                    status=status_map.get(data.get("status", "failed"), VerificationStatus.FAILED),
                    original_claim=original_claim,
                    correction=data.get("correction")
                )

        except Exception as e:
            print(f"[CoVe] LLM verification failed: {e}, falling back to heuristics")

        # Fallback
        return self._answer_with_heuristics(question, original_claim, context)

    def _answer_with_heuristics(
        self,
        question: str,
        original_claim: str,
        context: Optional[Dict]
    ) -> Verification:
        """Verifica usando heurísticas."""
        # Heurística 1: Verificar keywords críticos
        critical_keywords = self._check_critical_keywords(original_claim, context)

        # Heurística 2: Verificar completitud
        completeness = self._check_completeness(original_claim, context)

        # Heurística 3: Verificar consistencia
        consistency = self._check_consistency(original_claim, context)

        # Determinar status basado en verificaciones
        issues = []
        if not critical_keywords['passed']:
            issues.append(critical_keywords['issue'])
        if not completeness['passed']:
            issues.append(completeness['issue'])
        if not consistency['passed']:
            issues.append(consistency['issue'])

        if not issues:
            # Verificación passed
            return Verification(
                question=question,
                answer="Verified: Claim is accurate and complete",
                status=VerificationStatus.VERIFIED,
                original_claim=original_claim
            )
        else:
            # Verificación failed, generar corrección
            correction = self._generate_correction(original_claim, issues)

            return Verification(
                question=question,
                answer=f"Issues found: {'; '.join(issues)}",
                status=VerificationStatus.CORRECTED,
                original_claim=original_claim,
                correction=correction
            )

    def _check_critical_keywords(
        self,
        claim: str,
        context: Optional[Dict]
    ) -> Dict:
        """Verifica presencia de keywords críticos del dominio."""
        # Keywords críticos por dominio
        if context and 'domain' in context:
            domain = context['domain']

            if domain == 'database':
                critical = ['read-only', 'read', 'write', 'transaction']
                if any(kw in claim.lower() for kw in ['write', 'update', 'delete']):
                    if 'ivr' in claim.lower() and 'write' in claim.lower():
                        return {
                            'passed': False,
                            'issue': 'IVR database is READ-ONLY, cannot write'
                        }

            elif domain == 'security':
                critical = ['authentication', 'authorization', 'permission', 'validate']
                if 'permission' in claim.lower():
                    if not any(kw in claim.lower() for kw in ['check', 'validate', 'verify']):
                        return {
                            'passed': False,
                            'issue': 'Permission claim missing validation aspect'
                        }

        return {'passed': True, 'issue': None}

    def _check_completeness(
        self,
        claim: str,
        context: Optional[Dict]
    ) -> Dict:
        """Verifica que el claim sea completo."""
        # Verificar que claims de validación incluyan casos edge
        if 'validates' in claim.lower() or 'checks' in claim.lower():
            edge_keywords = ['edge case', 'null', 'empty', 'invalid', 'error']
            if not any(kw in claim.lower() for kw in edge_keywords):
                return {
                    'passed': False,
                    'issue': 'Validation claim should mention edge cases'
                }

        # Verificar que claims de requirements incluyan constraints
        if 'must' in claim.lower() or 'required' in claim.lower():
            constraint_keywords = ['if', 'when', 'unless', 'except', 'only']
            if not any(kw in claim.lower() for kw in constraint_keywords):
                return {
                    'passed': False,
                    'issue': 'Requirement claim should include conditions/constraints'
                }

        return {'passed': True, 'issue': None}

    def _check_consistency(
        self,
        claim: str,
        context: Optional[Dict]
    ) -> Dict:
        """Verifica consistencia con restricciones del proyecto."""
        if not context or 'project_restrictions' not in context:
            return {'passed': True, 'issue': None}

        restrictions = context['project_restrictions']

        # Verificar contra restricciones conocidas
        for restriction in restrictions:
            if restriction.lower() in claim.lower():
                return {
                    'passed': False,
                    'issue': f'Claim conflicts with project restriction: {restriction}'
                }

        return {'passed': True, 'issue': None}

    def _generate_correction(
        self,
        original_claim: str,
        issues: List[str]
    ) -> str:
        """Genera corrección para claim con issues."""
        # En producción: usar LLM para generar corrección natural
        # Esta versión genera corrección estructurada

        correction = original_claim

        for issue in issues:
            if 'READ-ONLY' in issue:
                correction = correction.replace('write', 'read')
                correction += " (IVR database is READ-ONLY)"

            elif 'edge cases' in issue:
                correction += ", including edge cases (null, empty, invalid input)"

            elif 'conditions' in issue:
                correction += " when applicable conditions are met"

        return correction

    def _generate_final_response(
        self,
        question: str,
        initial_response: str,
        verifications: List[Verification]
    ) -> str:
        """
        Genera respuesta final incorporando correcciones.

        Strategy: Reconstruir respuesta con corrections aplicadas.
        """
        corrections = [v for v in verifications if v.status == VerificationStatus.CORRECTED]

        if self.use_llm and self.llm and corrections:
            # Usar LLM para regenerar respuesta coherente con correcciones
            return self._generate_final_with_llm(question, initial_response, verifications)
        else:
            # Fallback: simple replacement
            return self._generate_final_with_replacement(initial_response, verifications)

    def _generate_final_with_llm(
        self,
        question: str,
        initial_response: str,
        verifications: List[Verification]
    ) -> str:
        """Regenera respuesta final usando LLM."""
        # Formatear verificaciones
        verifications_text = ""
        for i, v in enumerate(verifications, 1):
            verifications_text += f"\n{i}. Claim: {v.original_claim}\n"
            verifications_text += f"   Status: {v.status.value}\n"
            if v.correction:
                verifications_text += f"   Correction: {v.correction}\n"

        prompt = f"""You are refining a response based on verification results.

Original Question: {question}

Initial Response:
{initial_response}

Verification Results:
{verifications_text}

Task: Generate a final, accurate response that:
1. Incorporates all corrections
2. Maintains a coherent narrative
3. Removes or corrects any inaccurate claims
4. Is clear and complete

Generate only the final response, without meta-commentary.

Final Response:"""

        try:
            final_response = self.llm._call_llm(prompt)
            return final_response.strip()
        except Exception as e:
            print(f"[CoVe] LLM final response generation failed: {e}")
            return self._generate_final_with_replacement(initial_response, verifications)

    def _generate_final_with_replacement(
        self,
        initial_response: str,
        verifications: List[Verification]
    ) -> str:
        """Genera respuesta final con simple replacement."""
        final_response = initial_response

        # Aplicar todas las correcciones
        for verification in verifications:
            if verification.status == VerificationStatus.CORRECTED and verification.correction:
                # Reemplazar claim original con versión corregida
                final_response = final_response.replace(
                    verification.original_claim,
                    verification.correction
                )

        # Agregar nota de verificación si hubo correcciones
        corrections = [v for v in verifications if v.status == VerificationStatus.CORRECTED]
        if corrections:
            final_response += f"\n\n[Note: Response verified and corrected ({len(corrections)} improvements applied)]"

        return final_response

    def _calculate_confidence(self, verifications: List[Verification]) -> float:
        """
        Calcula confidence score basado en verificaciones.

        Formula:
        confidence = (verified + 0.5 * corrected) / total
        """
        if not verifications:
            return 0.0

        verified = sum(1 for v in verifications if v.status == VerificationStatus.VERIFIED)
        corrected = sum(1 for v in verifications if v.status == VerificationStatus.CORRECTED)
        failed = sum(1 for v in verifications if v.status == VerificationStatus.FAILED)

        # Verified = 1.0, Corrected = 0.5 (parcialmente correcto), Failed = 0.0
        score = (verified + 0.5 * corrected) / len(verifications)

        return score


def main():
    """Example usage of Chain-of-Verification."""
    print("Chain-of-Verification Agent - Example\n")
    print("="*70)

    # Example: Database validation
    question = "How does the database router handle writes to IVR database?"

    initial_response = """
The database router validates write operations to ensure data integrity.
It checks permissions before allowing writes to any database.
The router handles both IVR and Analytics databases equally.
All write operations are logged for audit purposes.
"""

    context = {
        'domain': 'database',
        'project_restrictions': [
            'NO writes to IVR database',
            'IVR is READ-ONLY',
            'Only Analytics database is writable'
        ]
    }

    # Apply Chain-of-Verification
    agent = ChainOfVerificationAgent()
    verified = agent.verify_response(question, initial_response, context)

    # Display results
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)

    print(f"\nInitial Response:\n{initial_response}")

    print(f"\nVerifications Performed: {len(verified.verifications)}")
    for i, v in enumerate(verified.verifications, 1):
        print(f"\n{i}. {v.question}")
        print(f"   Status: {v.status.value}")
        if v.correction:
            print(f"   Correction: {v.correction}")

    print(f"\nFinal Verified Response:\n{verified.final_response}")

    print(f"\nConfidence Score: {verified.confidence_score:.2%}")
    print(f"Corrections Made: {verified.corrections_made}")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
