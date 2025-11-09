#!/usr/bin/env python3
"""
Tests for TDD Constitution module.

Validates:
- ConstitutionRule and ConstitutionViolation dataclasses
- All 8 TDD constitution rules
- Compliance validation logic
- Evidence gathering
- Score calculation

Reference: scripts/ai/agents/tdd_constitution.py
"""

from __future__ import annotations

import pytest
from datetime import datetime
from typing import Dict, List

import sys
from pathlib import Path

# Add scripts to path for imports
scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

from ai.agents.tdd_constitution import (
    ConstitutionRule,
    ConstitutionViolation,
    Severity,
    TDDConstitution,
)


class TestSeverityEnum:
    """Tests for Severity enumeration."""

    def test_severity_values_are_correct(self):
        """Verify severity levels have correct string values."""
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"

    def test_severity_has_three_levels(self):
        """Verify there are exactly 3 severity levels."""
        assert len(Severity) == 3


class TestConstitutionRule:
    """Tests for ConstitutionRule dataclass."""

    def test_create_rule_without_threshold(self):
        """Create rule without threshold succeeds."""
        rule = ConstitutionRule(
            code="TEST_RULE",
            description="Test rule description",
            severity=Severity.CRITICAL,
            auto_fix=False,
        )

        assert rule.code == "TEST_RULE"
        assert rule.description == "Test rule description"
        assert rule.severity == Severity.CRITICAL
        assert rule.auto_fix is False
        assert rule.threshold is None

    def test_create_rule_with_threshold(self):
        """Create rule with threshold succeeds."""
        rule = ConstitutionRule(
            code="COVERAGE_RULE",
            description="Coverage must be >= 90%",
            severity=Severity.HIGH,
            auto_fix=False,
            threshold=90.0,
        )

        assert rule.code == "COVERAGE_RULE"
        assert rule.threshold == 90.0

    def test_rule_to_dict_conversion(self):
        """Convert rule to dictionary includes all fields."""
        rule = ConstitutionRule(
            code="TEST_RULE",
            description="Test description",
            severity=Severity.MEDIUM,
            auto_fix=True,
            threshold=80.0,
        )

        result = rule.to_dict()

        assert result["code"] == "TEST_RULE"
        assert result["description"] == "Test description"
        assert result["severity"] == "MEDIUM"
        assert result["auto_fix"] is True
        assert result["threshold"] == 80.0


class TestConstitutionViolation:
    """Tests for ConstitutionViolation dataclass."""

    def test_create_violation_without_evidence(self):
        """Create violation without evidence succeeds."""
        violation = ConstitutionViolation(
            rule_code="RED_BEFORE_GREEN",
            severity=Severity.CRITICAL,
            message="Tests were not written before implementation",
        )

        assert violation.rule_code == "RED_BEFORE_GREEN"
        assert violation.severity == Severity.CRITICAL
        assert violation.message == "Tests were not written before implementation"
        assert violation.evidence is None

    def test_create_violation_with_evidence(self):
        """Create violation with evidence succeeds."""
        evidence = {
            "test_file": "test_feature.py",
            "impl_file": "feature.py",
            "test_timestamp": "2025-01-15T10:00:00",
            "impl_timestamp": "2025-01-15T09:00:00",
        }

        violation = ConstitutionViolation(
            rule_code="RED_BEFORE_GREEN",
            severity=Severity.CRITICAL,
            message="Implementation created before tests",
            evidence=evidence,
        )

        assert violation.evidence == evidence
        assert violation.evidence["test_file"] == "test_feature.py"

    def test_violation_to_dict_conversion(self):
        """Convert violation to dictionary includes all fields."""
        violation = ConstitutionViolation(
            rule_code="MINIMUM_COVERAGE",
            severity=Severity.HIGH,
            message="Coverage below 90%",
            evidence={"coverage": 75.5},
        )

        result = violation.to_dict()

        assert result["rule_code"] == "MINIMUM_COVERAGE"
        assert result["severity"] == "HIGH"
        assert result["message"] == "Coverage below 90%"
        assert result["evidence"]["coverage"] == 75.5

    def test_violation_to_dict_with_no_evidence(self):
        """Convert violation with no evidence returns empty dict."""
        violation = ConstitutionViolation(
            rule_code="TEST_RULE",
            severity=Severity.MEDIUM,
            message="Test message",
        )

        result = violation.to_dict()

        assert result["evidence"] == {}


class TestTDDConstitutionRules:
    """Tests for TDD Constitution rules definitions."""

    def test_constitution_has_eight_rules(self):
        """Verify constitution defines exactly 8 rules."""
        assert len(TDDConstitution.RULES) == 8

    def test_all_critical_rules_exist(self):
        """Verify all 4 CRITICAL rules are defined."""
        critical_rules = [
            "RED_BEFORE_GREEN",
            "TESTS_MUST_FAIL_FIRST",
            "ALL_TESTS_MUST_PASS",
            "TESTS_STAY_GREEN_AFTER_REFACTOR",
        ]

        for rule_code in critical_rules:
            assert rule_code in TDDConstitution.RULES
            rule = TDDConstitution.RULES[rule_code]
            assert rule.severity == Severity.CRITICAL
            assert rule.auto_fix is False

    def test_all_high_severity_rules_exist(self):
        """Verify all 2 HIGH severity rules are defined."""
        high_rules = ["MINIMUM_COVERAGE", "NO_SECURITY_ISSUES"]

        for rule_code in high_rules:
            assert rule_code in TDDConstitution.RULES
            rule = TDDConstitution.RULES[rule_code]
            assert rule.severity == Severity.HIGH

    def test_all_medium_severity_rules_exist(self):
        """Verify all 2 MEDIUM severity rules are defined."""
        medium_rules = ["CODE_QUALITY_PASSING", "DOCUMENTATION_REQUIRED"]

        for rule_code in medium_rules:
            assert rule_code in TDDConstitution.RULES
            rule = TDDConstitution.RULES[rule_code]
            assert rule.severity == Severity.MEDIUM

    def test_minimum_coverage_rule_has_threshold(self):
        """Verify MINIMUM_COVERAGE rule has 90% threshold."""
        rule = TDDConstitution.RULES["MINIMUM_COVERAGE"]
        assert rule.threshold == 90.0

    def test_code_quality_rule_has_auto_fix(self):
        """Verify CODE_QUALITY_PASSING has auto_fix enabled."""
        rule = TDDConstitution.RULES["CODE_QUALITY_PASSING"]
        assert rule.auto_fix is True


class TestTDDComplianceValidation:
    """Tests for validate_tdd_compliance method."""

    def create_valid_execution_log(self) -> Dict:
        """Create a valid execution log for testing."""
        return {
            "feature_name": "test_feature",
            "start_timestamp": "2025-01-15T10:00:00",
            "phases": {
                "red_phase": {
                    "start_timestamp": "2025-01-15T10:00:00",
                    "end_timestamp": "2025-01-15T10:05:00",
                    "status": "completed",
                    "details": {
                        "test_file_created": "tests/test_feature.py",
                    },
                },
                "green_phase": {
                    "start_timestamp": "2025-01-15T10:06:00",
                    "end_timestamp": "2025-01-15T10:15:00",
                    "status": "completed",
                    "details": {
                        "implementation_file": "api/feature.py",
                    },
                },
                "refactor_phase": {
                    "start_timestamp": "2025-01-15T10:16:00",
                    "end_timestamp": "2025-01-15T10:20:00",
                    "status": "completed",
                },
            },
            "test_executions": [
                {
                    "phase": "red",
                    "timestamp": "2025-01-15T10:04:00",
                    "total_tests": 5,
                    "passed": 0,
                    "failed": 5,
                    "result": "failed",
                },
                {
                    "phase": "green",
                    "timestamp": "2025-01-15T10:14:00",
                    "total_tests": 5,
                    "passed": 5,
                    "failed": 0,
                    "result": "passed",
                },
                {
                    "phase": "refactor",
                    "timestamp": "2025-01-15T10:19:00",
                    "total_tests": 5,
                    "passed": 5,
                    "failed": 0,
                    "result": "passed",
                },
            ],
            "artifacts": [
                {"type": "test", "path": "tests/test_feature.py", "phase": "red"},
                {"type": "implementation", "path": "api/feature.py", "phase": "green"},
            ],
            "metrics": {
                "coverage_percentage": 95.5,
                "security_issues": [],
                "linting_passed": True,
                "type_checking_passed": True,
                "missing_docstrings": 0,
            },
        }

    def test_validate_compliant_execution_succeeds(self):
        """Validate fully compliant execution returns success."""
        execution_log = self.create_valid_execution_log()

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is True
        assert len(result["violations"]) == 0
        assert result["score"] == 100.0
        assert "evidence" in result
        assert len(result["evidence"]) == 8

    def test_validate_returns_all_evidence_keys(self):
        """Validate returns evidence for all 8 rules."""
        execution_log = self.create_valid_execution_log()

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        expected_keys = [
            "RED_BEFORE_GREEN",
            "TESTS_MUST_FAIL_FIRST",
            "ALL_TESTS_MUST_PASS",
            "TESTS_STAY_GREEN_AFTER_REFACTOR",
            "MINIMUM_COVERAGE",
            "NO_SECURITY_ISSUES",
            "CODE_QUALITY_PASSING",
            "DOCUMENTATION_REQUIRED",
        ]

        for key in expected_keys:
            assert key in result["evidence"]
            assert "passed" in result["evidence"][key]

    def test_validate_missing_red_phase_fails(self):
        """Validate missing RED phase fails RED_BEFORE_GREEN."""
        execution_log = self.create_valid_execution_log()
        del execution_log["phases"]["red_phase"]

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is False
        violations = [v for v in result["violations"] if v.rule_code == "RED_BEFORE_GREEN"]
        assert len(violations) > 0

    def test_validate_tests_not_failing_first_fails(self):
        """Validate tests passing in RED phase fails TESTS_MUST_FAIL_FIRST."""
        execution_log = self.create_valid_execution_log()
        # Make RED phase tests pass (should fail)
        execution_log["test_executions"][0]["passed"] = 5
        execution_log["test_executions"][0]["failed"] = 0
        execution_log["test_executions"][0]["result"] = "passed"

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is False
        violations = [v for v in result["violations"] if v.rule_code == "TESTS_MUST_FAIL_FIRST"]
        assert len(violations) > 0

    def test_validate_green_phase_tests_failing_fails(self):
        """Validate tests failing in GREEN phase fails ALL_TESTS_MUST_PASS."""
        execution_log = self.create_valid_execution_log()
        # Make GREEN phase tests fail (should pass)
        execution_log["test_executions"][1]["passed"] = 3
        execution_log["test_executions"][1]["failed"] = 2
        execution_log["test_executions"][1]["result"] = "failed"

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is False
        violations = [v for v in result["violations"] if v.rule_code == "ALL_TESTS_MUST_PASS"]
        assert len(violations) > 0

    def test_validate_refactor_phase_tests_failing_fails(self):
        """Validate tests failing after REFACTOR fails TESTS_STAY_GREEN_AFTER_REFACTOR."""
        execution_log = self.create_valid_execution_log()
        # Make REFACTOR phase tests fail (should stay green)
        execution_log["test_executions"][2]["passed"] = 4
        execution_log["test_executions"][2]["failed"] = 1
        execution_log["test_executions"][2]["result"] = "failed"

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is False
        violations = [
            v for v in result["violations"] if v.rule_code == "TESTS_STAY_GREEN_AFTER_REFACTOR"
        ]
        assert len(violations) > 0

    def test_validate_low_coverage_creates_high_severity_violation(self):
        """Validate coverage below 90% creates HIGH severity violation."""
        execution_log = self.create_valid_execution_log()
        execution_log["metrics"]["coverage_percentage"] = 85.0

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        # Should still be compliant (not CRITICAL), but have violations
        violations = [v for v in result["violations"] if v.rule_code == "MINIMUM_COVERAGE"]
        assert len(violations) > 0
        assert violations[0].severity == Severity.HIGH

    def test_validate_security_issues_creates_high_severity_violation(self):
        """Validate security issues create HIGH severity violation."""
        execution_log = self.create_valid_execution_log()
        execution_log["metrics"]["security_issues"] = [
            {"severity": "HIGH", "issue": "SQL injection risk"},
        ]

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        violations = [v for v in result["violations"] if v.rule_code == "NO_SECURITY_ISSUES"]
        assert len(violations) > 0
        assert violations[0].severity == Severity.HIGH

    def test_validate_linting_failure_creates_medium_severity_violation(self):
        """Validate linting failure creates MEDIUM severity violation."""
        execution_log = self.create_valid_execution_log()
        execution_log["metrics"]["linting_passed"] = False

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        violations = [v for v in result["violations"] if v.rule_code == "CODE_QUALITY_PASSING"]
        assert len(violations) > 0
        assert violations[0].severity == Severity.MEDIUM

    def test_validate_missing_docstrings_creates_medium_severity_violation(self):
        """Validate missing docstrings creates MEDIUM severity violation."""
        execution_log = self.create_valid_execution_log()
        execution_log["metrics"]["missing_docstrings"] = 5

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        violations = [v for v in result["violations"] if v.rule_code == "DOCUMENTATION_REQUIRED"]
        assert len(violations) > 0
        assert violations[0].severity == Severity.MEDIUM

    def test_validate_score_calculation_with_violations(self):
        """Validate score calculation decreases with violations."""
        execution_log = self.create_valid_execution_log()

        # Add some non-critical violations
        execution_log["metrics"]["coverage_percentage"] = 85.0
        execution_log["metrics"]["linting_passed"] = False

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        # Score should be less than 100 but still compliant (no CRITICAL violations)
        assert result["compliant"] is True
        assert result["score"] < 100.0
        assert result["score"] > 0.0

    def test_validate_empty_execution_log_fails(self):
        """Validate empty execution log fails multiple rules."""
        execution_log = {
            "feature_name": "test",
            "phases": {},
            "test_executions": [],
            "artifacts": [],
            "metrics": {},
        }

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert result["compliant"] is False
        assert len(result["violations"]) > 0

    def test_validate_result_structure(self):
        """Validate result has correct structure."""
        execution_log = self.create_valid_execution_log()

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        # Check required keys
        assert "compliant" in result
        assert "violations" in result
        assert "score" in result
        assert "evidence" in result

        # Check types
        assert isinstance(result["compliant"], bool)
        assert isinstance(result["violations"], list)
        assert isinstance(result["score"], (int, float))
        assert isinstance(result["evidence"], dict)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_validate_with_missing_metrics(self):
        """Validate handles missing metrics gracefully."""
        execution_log = {
            "feature_name": "test",
            "phases": {
                "red_phase": {"start_timestamp": "2025-01-15T10:00:00"},
                "green_phase": {"start_timestamp": "2025-01-15T10:05:00"},
            },
            "test_executions": [],
            "artifacts": [],
            # metrics is missing entirely
        }

        # Should not crash, should handle gracefully
        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert "compliant" in result
        assert "violations" in result

    def test_validate_with_partial_test_executions(self):
        """Validate handles partial test execution data."""
        execution_log = {
            "feature_name": "test",
            "phases": {
                "red_phase": {"status": "completed"},
                "green_phase": {"status": "completed"},
            },
            "test_executions": [
                {"phase": "red", "result": "failed"},
                # Missing green phase test execution
            ],
            "artifacts": [],
            "metrics": {},
        }

        result = TDDConstitution.validate_tdd_compliance(execution_log)

        assert "compliant" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
