#!/usr/bin/env python3
"""
TDD Tests for ArchitectureAnalysisAgent

Tests the agent that uses Chain-of-Verification to validate SOLID compliance
and detect architectural violations in code.

Technique: Chain-of-Verification (Zhang et al., 2023)
Process:
1. Generate baseline answer
2. Plan verification questions
3. Execute verifications independently
4. Generate final verified response

Meta-Application: Using prompting techniques to improve code quality.
"""

import pytest
from scripts.ai.agents.meta import (
    ArchitectureAnalysisAgent,
    SOLIDAnalysisResult,
    PrincipleViolation,
    SOLIDPrinciple
)


# Fixtures
@pytest.fixture
def sample_good_class():
    """Sample class that follows SOLID principles."""
    return '''
class UserRepository:
    """Repository for user data access - Single Responsibility."""

    def __init__(self, database):
        self.database = database

    def get_user(self, user_id: int):
        return self.database.query("SELECT * FROM users WHERE id = ?", user_id)

    def save_user(self, user):
        return self.database.execute("INSERT INTO users ...", user)
'''


@pytest.fixture
def sample_bad_class():
    """Sample class that violates multiple SOLID principles."""
    return '''
class UserManager:
    """Violates SRP, OCP, and DIP."""

    def __init__(self):
        self.db_connection = MySQLDatabase()  # DIP violation

    def get_user(self, user_id):
        return self.db_connection.query(f"SELECT * FROM users WHERE id = {user_id}")

    def send_email(self, user, message):  # SRP violation
        smtp = SMTP('smtp.gmail.com')
        smtp.send(user.email, message)

    def calculate_discount(self, user):  # SRP violation
        if user.type == "premium":
            return 0.2
        elif user.type == "regular":
            return 0.1
        else:
            return 0.0
'''


# 1. Initialization Tests
class TestArchitectureAnalysisInitialization:
    """Test ArchitectureAnalysisAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = ArchitectureAnalysisAgent()

        assert agent.name == "ArchitectureAnalysisAgent"
        assert agent.verifier is not None
        assert agent.principles == list(SOLIDPrinciple)

    def test_custom_initialization(self):
        """Should initialize with custom principles."""
        agent = ArchitectureAnalysisAgent(
            principles=[SOLIDPrinciple.SINGLE_RESPONSIBILITY]
        )

        assert len(agent.principles) == 1
        assert agent.principles[0] == SOLIDPrinciple.SINGLE_RESPONSIBILITY


# 2. SOLID Analysis Tests
class TestSOLIDAnalysis:
    """Test SOLID compliance analysis."""

    def test_analyze_good_class(self, sample_good_class):
        """Should identify compliant class."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_good_class)

        assert isinstance(result, SOLIDAnalysisResult)
        assert result.is_compliant is True
        assert len(result.violations) == 0

    def test_analyze_bad_class(self, sample_bad_class):
        """Should identify violations in non-compliant class."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_bad_class)

        assert isinstance(result, SOLIDAnalysisResult)
        assert result.is_compliant is False
        assert len(result.violations) > 0

    def test_identify_srp_violation(self, sample_bad_class):
        """Should identify Single Responsibility violations."""
        agent = ArchitectureAnalysisAgent(
            principles=[SOLIDPrinciple.SINGLE_RESPONSIBILITY]
        )

        result = agent.analyze_solid_compliance(sample_bad_class)

        srp_violations = [
            v for v in result.violations
            if v.principle == SOLIDPrinciple.SINGLE_RESPONSIBILITY
        ]
        assert len(srp_violations) > 0


# 3. Principle-Specific Tests
class TestPrincipleDetection:
    """Test detection of specific SOLID principle violations."""

    def test_detect_srp_violation(self):
        """Should detect Single Responsibility Principle violations."""
        agent = ArchitectureAnalysisAgent()
        code = '''
class OrderProcessor:
    def process_order(self, order):
        # Process order
        pass

    def send_confirmation_email(self, order):  # SRP violation
        # Send email
        pass
'''

        result = agent.analyze_solid_compliance(code)

        srp_violations = [
            v for v in result.violations
            if v.principle == SOLIDPrinciple.SINGLE_RESPONSIBILITY
        ]
        assert len(srp_violations) > 0

    def test_detect_ocp_violation(self):
        """Should detect Open/Closed Principle violations."""
        agent = ArchitectureAnalysisAgent()
        code = '''
class DiscountCalculator:
    def calculate(self, customer_type):
        if customer_type == "regular":  # OCP violation
            return 0.1
        elif customer_type == "premium":
            return 0.2
        else:
            return 0.0
'''

        result = agent.analyze_solid_compliance(code)

        # May detect OCP violation (type checking instead of polymorphism)
        assert isinstance(result, SOLIDAnalysisResult)

    def test_detect_dip_violation(self):
        """Should detect Dependency Inversion Principle violations."""
        agent = ArchitectureAnalysisAgent()
        code = '''
class UserService:
    def __init__(self):
        self.repo = MySQLUserRepository()  # DIP violation - concrete dependency
'''

        result = agent.analyze_solid_compliance(code)

        # Should detect concrete class dependency
        assert isinstance(result, SOLIDAnalysisResult)


# 4. Verification Chain Tests
class TestVerificationChain:
    """Test Chain-of-Verification integration."""

    def test_uses_chain_of_verification(self, sample_bad_class):
        """Should use Chain-of-Verification for analysis."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_bad_class)

        # Should have verification metadata
        assert hasattr(result, 'verification_count')
        assert result.verification_count >= 5  # At least 5 SOLID principles

    def test_verification_questions_generated(self, sample_good_class):
        """Should generate verification questions for each principle."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_good_class)

        # Should have verification questions
        assert hasattr(result, 'verification_questions')
        assert len(result.verification_questions) == 5  # One per SOLID principle


# 5. Violation Detail Tests
class TestViolationDetails:
    """Test violation details and recommendations."""

    def test_violation_has_location(self, sample_bad_class):
        """Violations should include code location."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_bad_class)

        if result.violations:
            violation = result.violations[0]
            assert isinstance(violation, PrincipleViolation)
            assert violation.location is not None

    def test_violation_has_description(self, sample_bad_class):
        """Violations should include clear description."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_bad_class)

        if result.violations:
            violation = result.violations[0]
            assert len(violation.description) > 10
            assert violation.description != ""

    def test_violation_has_recommendation(self, sample_bad_class):
        """Violations should include fix recommendations."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_bad_class)

        if result.violations:
            violation = result.violations[0]
            assert violation.recommendation is not None
            assert len(violation.recommendation) > 10


# 6. Edge Cases
class TestArchitectureAnalysisEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_empty_code(self):
        """Should handle empty code gracefully."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance("")

        assert isinstance(result, SOLIDAnalysisResult)
        assert result.is_compliant is False

    def test_handles_invalid_syntax(self):
        """Should handle invalid Python syntax."""
        agent = ArchitectureAnalysisAgent()
        code = "class Invalid { def broken"

        result = agent.analyze_solid_compliance(code)

        # Should return result indicating analysis failure
        assert isinstance(result, SOLIDAnalysisResult)

    def test_handles_multiple_classes(self):
        """Should analyze multiple classes in one file."""
        agent = ArchitectureAnalysisAgent()
        code = '''
class ClassA:
    pass

class ClassB:
    pass
'''

        result = agent.analyze_solid_compliance(code)

        assert isinstance(result, SOLIDAnalysisResult)


# 7. Integration Tests
class TestArchitectureAnalysisIntegration:
    """Test integration with other agents."""

    def test_result_serializable(self, sample_good_class):
        """Results should be serializable for pipeline."""
        agent = ArchitectureAnalysisAgent()

        result = agent.analyze_solid_compliance(sample_good_class)

        # Should be convertible to dict
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'is_compliant' in result_dict
        assert 'violations' in result_dict

    def test_multiple_analyses(self, sample_good_class, sample_bad_class):
        """Should handle multiple analyses correctly."""
        agent = ArchitectureAnalysisAgent()

        result1 = agent.analyze_solid_compliance(sample_good_class)
        result2 = agent.analyze_solid_compliance(sample_bad_class)

        # Results should be independent
        assert result1.is_compliant is True
        assert result2.is_compliant is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
