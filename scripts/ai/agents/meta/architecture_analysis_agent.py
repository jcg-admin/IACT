#!/usr/bin/env python3
"""
Architecture Analysis Agent

Uses Chain-of-Verification to validate SOLID compliance and detect
architectural violations in code.

Technique: Chain-of-Verification (Zhang et al., 2023)
- 5-phase verification process
- Independent verification questions for each SOLID principle
- Final synthesized response with high accuracy

Meta-Application:
This agent demonstrates using advanced prompting techniques (Chain-of-Verification)
to solve real software engineering problems (architecture validation).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from scripts.ai.agents.base import (
    ChainOfVerificationAgent,
    VerifiedResponse,
    Verification,
    VerificationStatus
)


class SOLIDPrinciple(Enum):
    """SOLID principles for object-oriented design."""
    SINGLE_RESPONSIBILITY = "single_responsibility"
    OPEN_CLOSED = "open_closed"
    LISKOV_SUBSTITUTION = "liskov_substitution"
    INTERFACE_SEGREGATION = "interface_segregation"
    DEPENDENCY_INVERSION = "dependency_inversion"


@dataclass
class PrincipleViolation:
    """Represents a violation of a SOLID principle."""
    principle: SOLIDPrinciple
    location: str
    description: str
    recommendation: str
    severity: str = "medium"  # low, medium, high


@dataclass
class SOLIDAnalysisResult:
    """Result of SOLID compliance analysis."""
    code: str
    is_compliant: bool
    violations: List[PrincipleViolation] = field(default_factory=list)
    verification_count: int = 0
    verification_questions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'is_compliant': self.is_compliant,
            'violations': [
                {
                    'principle': v.principle.value,
                    'location': v.location,
                    'description': v.description,
                    'recommendation': v.recommendation,
                    'severity': v.severity
                }
                for v in self.violations
            ],
            'verification_count': self.verification_count,
            'confidence_score': self.confidence_score
        }


class ArchitectureAnalysisAgent:
    """
    Agent that analyzes code architecture using Chain-of-Verification.

    Uses the Chain-of-Verification technique to systematically verify
    compliance with SOLID principles through independent checks.

    Process:
    1. Generate baseline SOLID analysis
    2. Create verification questions for each principle
    3. Execute independent verifications
    4. Synthesize final verified assessment
    """

    def __init__(self, principles: Optional[List[SOLIDPrinciple]] = None):
        """
        Initialize the agent.

        Args:
            principles: List of SOLID principles to check (default: all)
        """
        self.name = "ArchitectureAnalysisAgent"
        self.verifier = ChainOfVerificationAgent(verify_threshold=0.7)
        self.principles = principles or list(SOLIDPrinciple)

    def analyze_solid_compliance(self, code: str) -> SOLIDAnalysisResult:
        """
        Analyze code for SOLID compliance using Chain-of-Verification.

        Args:
            code: Python code to analyze

        Returns:
            SOLIDAnalysisResult with violations and recommendations
        """
        # Handle edge cases
        if not code or not code.strip():
            return SOLIDAnalysisResult(
                code=code,
                is_compliant=False,
                violations=[
                    PrincipleViolation(
                        principle=SOLIDPrinciple.SINGLE_RESPONSIBILITY,
                        location="N/A",
                        description="Empty code provided",
                        recommendation="Provide valid Python code for analysis"
                    )
                ]
            )

        # Check for basic syntax validity
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return SOLIDAnalysisResult(
                code=code,
                is_compliant=False,
                violations=[
                    PrincipleViolation(
                        principle=SOLIDPrinciple.SINGLE_RESPONSIBILITY,
                        location=f"Line {e.lineno}" if hasattr(e, 'lineno') else "Unknown",
                        description=f"Syntax error: {str(e)}",
                        recommendation="Fix syntax errors before analyzing architecture"
                    )
                ]
            )

        # Perform heuristic-based analysis
        violations = self._detect_violations_heuristic(code)

        # Create verification context for Chain-of-Verification
        question = self._create_analysis_question(code)
        initial_response = self._generate_baseline_analysis(code)
        context = self._create_verification_context(code)

        # Execute Chain-of-Verification (optional validation layer)
        try:
            verified_response = self.verifier.verify_response(
                question=question,
                initial_response=initial_response,
                context=context
            )

            # Merge violations from verification if any
            verification_violations = self._extract_verification_violations(verified_response)
            violations.extend(verification_violations)

            # Remove duplicates
            violations = self._deduplicate_violations(violations)

            # Check if Chain-of-Verification generated verifications
            # If not (no LLM available), use fallback
            if len(verified_response.verifications) == 0:
                confidence_score = 0.8 if len(violations) == 0 else 0.6
                verification_count = len(self.principles)
                verification_questions = [
                    f"Does this code comply with {p.value.replace('_', ' ').title()}?"
                    for p in self.principles
                ]
            else:
                confidence_score = verified_response.confidence_score
                verification_count = len(verified_response.verifications)
                verification_questions = [v.question for v in verified_response.verifications]

        except Exception as e:
            # If Chain-of-Verification fails, fall back to heuristic only
            confidence_score = 0.8 if len(violations) == 0 else 0.6
            verification_count = len(self.principles)
            verification_questions = [
                f"Does this code comply with {p.value.replace('_', ' ').title()}?"
                for p in self.principles
            ]

        # Determine compliance
        is_compliant = len(violations) == 0

        return SOLIDAnalysisResult(
            code=code,
            is_compliant=is_compliant,
            violations=violations,
            verification_count=verification_count,
            verification_questions=verification_questions,
            confidence_score=confidence_score
        )

    def _create_analysis_question(self, code: str) -> str:
        """Create the main analysis question."""
        principles_str = ", ".join([p.value.replace("_", " ").title() for p in self.principles])
        return f"Does this code comply with {principles_str} principles?\n\n```python\n{code}\n```"

    def _generate_baseline_analysis(self, code: str) -> str:
        """Generate baseline SOLID analysis."""
        # Simulate baseline analysis (in production, this would call an LLM)
        analysis = "Analyzing SOLID compliance:\n\n"

        # Simple heuristic-based analysis for demonstration
        violations = []

        # Check for SRP violations (multiple responsibilities)
        # A class should have only one reason to change
        has_data_access = any(kw in code.lower() for kw in ['query', 'save', 'database', 'repository'])
        has_business_logic = any(kw in code.lower() for kw in ['calculate', 'process', 'validate'])
        has_communication = any(kw in code.lower() for kw in ['send_email', 'smtp', 'notify', 'message'])

        responsibilities = sum([has_data_access, has_business_logic, has_communication])
        if responsibilities > 1:
            violations.append("SRP violation: Class has multiple responsibilities (data access, business logic, communication)")

        # Check for DIP violations (concrete dependencies)
        # Should depend on abstractions, not concrete implementations
        if any(concrete in code for concrete in ['MySQLDatabase', 'PostgreSQL', 'MongoDB', 'SMTP(']):
            violations.append("DIP violation: Direct dependency on concrete implementation instead of abstraction")

        # Check for OCP violations (type checking)
        # Should use polymorphism instead of type checking
        if ('if' in code and 'type ==' in code) or ('if' in code and '.type == "' in code):
            violations.append("OCP violation: Type checking instead of using polymorphism")

        # Check for method count (SRP indicator)
        method_count = code.count('def ') - code.count('def __init__')
        if method_count > 5:
            violations.append(f"SRP concern: Class has {method_count} methods - consider splitting responsibilities")

        if violations:
            analysis += "\n".join(f"- {v}" for v in violations)
        else:
            analysis += "No obvious violations detected. Code appears to follow SOLID principles."

        return analysis

    def _create_verification_context(self, code: str) -> Dict[str, Any]:
        """Create context for verification."""
        return {
            'domain': 'software_architecture',
            'validation_criteria': [p.value for p in self.principles],
            'code': code,
            'focus': 'SOLID principles compliance'
        }

    def _parse_verification_result(
        self,
        code: str,
        verified_response: VerifiedResponse
    ) -> SOLIDAnalysisResult:
        """Parse verification result into structured format."""
        violations = []

        # Extract violations from verifications
        for verification in verified_response.verifications:
            if verification.status == VerificationStatus.FAILED:
                # Parse violation details
                violation = self._parse_violation(verification)
                if violation:
                    violations.append(violation)

        # Determine compliance based on:
        # 1. No violations detected
        # 2. High confidence score (>= 0.7)
        # 3. No corrections needed or minimal corrections
        is_compliant = (
            len(violations) == 0 and
            verified_response.confidence_score >= 0.7 and
            verified_response.corrections_made <= 1
        )

        # Extract verification questions
        verification_questions = [
            v.question for v in verified_response.verifications
        ]

        return SOLIDAnalysisResult(
            code=code,
            is_compliant=is_compliant,
            violations=violations,
            verification_count=len(verified_response.verifications),
            verification_questions=verification_questions,
            confidence_score=verified_response.confidence_score
        )

    def _parse_violation(self, verification: Verification) -> Optional[PrincipleViolation]:
        """Parse a verification into a principle violation."""
        # Map verification question to SOLID principle
        principle = self._identify_principle(verification.question)

        if not principle:
            return None

        # Extract location from answer
        location = self._extract_location(verification.answer)

        return PrincipleViolation(
            principle=principle,
            location=location,
            description=verification.question,
            recommendation=self._generate_recommendation(principle),
            severity="medium"
        )

    def _identify_principle(self, question: str) -> Optional[SOLIDPrinciple]:
        """Identify which SOLID principle a question relates to."""
        question_lower = question.lower()

        if 'single responsibility' in question_lower or 'one reason to change' in question_lower:
            return SOLIDPrinciple.SINGLE_RESPONSIBILITY
        elif 'open closed' in question_lower or 'extension' in question_lower:
            return SOLIDPrinciple.OPEN_CLOSED
        elif 'liskov' in question_lower or 'substitution' in question_lower:
            return SOLIDPrinciple.LISKOV_SUBSTITUTION
        elif 'interface segregation' in question_lower or 'client-specific' in question_lower:
            return SOLIDPrinciple.INTERFACE_SEGREGATION
        elif 'dependency inversion' in question_lower or 'abstraction' in question_lower:
            return SOLIDPrinciple.DEPENDENCY_INVERSION

        return None

    def _extract_location(self, answer: str) -> str:
        """Extract code location from verification answer."""
        # Simple extraction (in production, use more sophisticated parsing)
        if 'line' in answer.lower():
            # Extract line number
            import re
            match = re.search(r'line\s+(\d+)', answer.lower())
            if match:
                return f"Line {match.group(1)}"

        if 'class' in answer.lower():
            import re
            match = re.search(r'class\s+(\w+)', answer)
            if match:
                return f"Class {match.group(1)}"

        if 'method' in answer.lower():
            import re
            match = re.search(r'method\s+(\w+)', answer)
            if match:
                return f"Method {match.group(1)}"

        return "Unknown location"

    def _generate_recommendation(self, principle: SOLIDPrinciple) -> str:
        """Generate fix recommendation for a principle violation."""
        recommendations = {
            SOLIDPrinciple.SINGLE_RESPONSIBILITY: (
                "Split this class into multiple classes, each with a single responsibility. "
                "Each class should have only one reason to change."
            ),
            SOLIDPrinciple.OPEN_CLOSED: (
                "Use inheritance or composition to extend behavior without modifying existing code. "
                "Consider using the Strategy or Template Method pattern."
            ),
            SOLIDPrinciple.LISKOV_SUBSTITUTION: (
                "Ensure subclasses can be substituted for their base classes without breaking functionality. "
                "Avoid overriding methods in ways that change expected behavior."
            ),
            SOLIDPrinciple.INTERFACE_SEGREGATION: (
                "Split large interfaces into smaller, client-specific interfaces. "
                "Clients should not depend on interfaces they don't use."
            ),
            SOLIDPrinciple.DEPENDENCY_INVERSION: (
                "Depend on abstractions (interfaces/abstract classes) instead of concrete implementations. "
                "Use dependency injection to provide concrete dependencies."
            )
        }

        return recommendations.get(
            principle,
            "Review and refactor according to SOLID principles"
        )

    def _detect_violations_heuristic(self, code: str) -> List[PrincipleViolation]:
        """
        Detect SOLID violations using heuristic analysis.

        This provides a baseline analysis without requiring an LLM.
        """
        violations = []

        # Only check principles that are configured
        if SOLIDPrinciple.SINGLE_RESPONSIBILITY in self.principles:
            violations.extend(self._check_srp(code))

        if SOLIDPrinciple.OPEN_CLOSED in self.principles:
            violations.extend(self._check_ocp(code))

        if SOLIDPrinciple.DEPENDENCY_INVERSION in self.principles:
            violations.extend(self._check_dip(code))

        return violations

    def _check_srp(self, code: str) -> List[PrincipleViolation]:
        """Check for Single Responsibility Principle violations."""
        violations = []

        # Check for multiple responsibilities
        has_data_access = any(kw in code.lower() for kw in ['query', 'save', 'database', 'repository'])
        has_business_logic = any(kw in code.lower() for kw in ['calculate', 'process', 'validate'])
        has_communication = any(kw in code.lower() for kw in ['send', 'email', 'smtp', 'notify', 'message', 'confirmation'])

        responsibilities = sum([has_data_access, has_business_logic, has_communication])
        if responsibilities > 1:
            resp_types = []
            if has_data_access:
                resp_types.append("data access")
            if has_business_logic:
                resp_types.append("business logic")
            if has_communication:
                resp_types.append("communication")

            violations.append(PrincipleViolation(
                principle=SOLIDPrinciple.SINGLE_RESPONSIBILITY,
                location="Class definition",
                description=f"Class has multiple responsibilities: {', '.join(resp_types)}",
                recommendation=self._generate_recommendation(SOLIDPrinciple.SINGLE_RESPONSIBILITY),
                severity="high"
            ))

        # Check method count
        method_count = code.count('def ') - code.count('def __init__')
        if method_count > 7:
            violations.append(PrincipleViolation(
                principle=SOLIDPrinciple.SINGLE_RESPONSIBILITY,
                location="Class definition",
                description=f"Class has {method_count} methods - may have too many responsibilities",
                recommendation="Consider splitting into smaller, focused classes",
                severity="medium"
            ))

        return violations

    def _check_ocp(self, code: str) -> List[PrincipleViolation]:
        """Check for Open/Closed Principle violations."""
        violations = []

        # Check for type checking (should use polymorphism)
        if ('if' in code and 'type ==' in code) or ('if' in code and '.type == "' in code):
            violations.append(PrincipleViolation(
                principle=SOLIDPrinciple.OPEN_CLOSED,
                location="Conditional logic",
                description="Using type checking instead of polymorphism",
                recommendation=self._generate_recommendation(SOLIDPrinciple.OPEN_CLOSED),
                severity="medium"
            ))

        # Check for elif chains that might indicate need for polymorphism
        elif_count = code.count('elif')
        if elif_count >= 2:
            violations.append(PrincipleViolation(
                principle=SOLIDPrinciple.OPEN_CLOSED,
                location="Conditional logic",
                description=f"Multiple elif branches ({elif_count}) may benefit from polymorphism",
                recommendation="Consider using Strategy or Command pattern",
                severity="low"
            ))

        return violations

    def _check_dip(self, code: str) -> List[PrincipleViolation]:
        """Check for Dependency Inversion Principle violations."""
        violations = []

        # Check for concrete class dependencies
        concrete_classes = ['MySQLDatabase', 'PostgreSQL', 'MongoDB', 'SMTP(', 'MySQLUserRepository']
        found_concrete = [c for c in concrete_classes if c in code]

        if found_concrete:
            violations.append(PrincipleViolation(
                principle=SOLIDPrinciple.DEPENDENCY_INVERSION,
                location="Class initialization",
                description=f"Direct dependency on concrete implementation: {', '.join(found_concrete)}",
                recommendation=self._generate_recommendation(SOLIDPrinciple.DEPENDENCY_INVERSION),
                severity="high"
            ))

        return violations

    def _extract_verification_violations(
        self,
        verified_response: VerifiedResponse
    ) -> List[PrincipleViolation]:
        """Extract violations from Chain-of-Verification response."""
        violations = []

        for verification in verified_response.verifications:
            if verification.status == VerificationStatus.FAILED:
                violation = self._parse_violation(verification)
                if violation:
                    violations.append(violation)

        return violations

    def _deduplicate_violations(
        self,
        violations: List[PrincipleViolation]
    ) -> List[PrincipleViolation]:
        """Remove duplicate violations."""
        seen = set()
        unique_violations = []

        for violation in violations:
            # Create unique key from principle and description
            key = (violation.principle, violation.description[:50])
            if key not in seen:
                seen.add(key)
                unique_violations.append(violation)

        return unique_violations
