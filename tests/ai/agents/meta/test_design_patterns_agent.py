#!/usr/bin/env python3
"""
TDD Tests for DesignPatternsRecommendationAgent

Tests the agent that uses Auto-CoT to recommend design patterns for code.

Technique: Auto-CoT (Automatic Chain-of-Thought)
- Automatically generates reasoning chains
- Clusters similar problems
- Provides pattern recommendations with rationale

Meta-Application: Using AI reasoning techniques to suggest architectural improvements.
"""

import pytest
from scripts.ai.agents.meta import (
    DesignPatternsRecommendationAgent,
    PatternRecommendation,
    PatternType,
    PatternApplicability
)


# Fixtures
@pytest.fixture
def strategy_pattern_scenario():
    """Code that would benefit from Strategy pattern."""
    return '''
class PaymentProcessor:
    def process_payment(self, amount, payment_type):
        if payment_type == "credit_card":
            # Credit card processing logic
            return self._process_credit_card(amount)
        elif payment_type == "paypal":
            # PayPal processing logic
            return self._process_paypal(amount)
        elif payment_type == "bitcoin":
            # Bitcoin processing logic
            return self._process_bitcoin(amount)
        else:
            raise ValueError("Unknown payment type")
'''


@pytest.fixture
def observer_pattern_scenario():
    """Code that would benefit from Observer pattern."""
    return '''
class DataModel:
    def __init__(self):
        self.data = {}
        self.ui_component = None
        self.logger = None
        self.cache = None

    def update_data(self, key, value):
        self.data[key] = value
        # Manual notification to all dependents
        if self.ui_component:
            self.ui_component.refresh()
        if self.logger:
            self.logger.log(f"Data updated: {key}")
        if self.cache:
            self.cache.invalidate(key)
'''


# 1. Initialization Tests
class TestDesignPatternsAgentInitialization:
    """Test DesignPatternsRecommendationAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = DesignPatternsRecommendationAgent()

        assert agent.name == "DesignPatternsRecommendationAgent"
        assert agent.auto_cot is not None

    def test_custom_initialization(self):
        """Should initialize with custom parameters."""
        agent = DesignPatternsRecommendationAgent(
            max_recommendations=3
        )

        assert agent.max_recommendations == 3


# 2. Pattern Detection Tests
class TestPatternDetection:
    """Test detection of applicable design patterns."""

    def test_detect_strategy_pattern(self, strategy_pattern_scenario):
        """Should detect need for Strategy pattern."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        strategy_recs = [
            r for r in recommendations
            if r.pattern_type == PatternType.STRATEGY
        ]
        assert len(strategy_recs) > 0

    def test_detect_observer_pattern(self, observer_pattern_scenario):
        """Should detect need for Observer pattern."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(observer_pattern_scenario)

        observer_recs = [
            r for r in recommendations
            if r.pattern_type == PatternType.OBSERVER
        ]
        assert len(observer_recs) > 0

    def test_detect_factory_pattern(self):
        """Should detect need for Factory pattern."""
        agent = DesignPatternsRecommendationAgent()

        code = '''
class Application:
    def create_button(self, os_type):
        if os_type == "windows":
            return WindowsButton()
        elif os_type == "mac":
            return MacButton()
        elif os_type == "linux":
            return LinuxButton()
'''

        recommendations = agent.recommend_patterns(code)

        factory_recs = [
            r for r in recommendations
            if r.pattern_type == PatternType.FACTORY
        ]
        assert len(factory_recs) > 0


# 3. Reasoning Tests
class TestPatternReasoning:
    """Test Auto-CoT reasoning for pattern recommendations."""

    def test_recommendations_include_reasoning(self, strategy_pattern_scenario):
        """Recommendations should include chain-of-thought reasoning."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        assert len(recommendations) > 0
        for rec in recommendations:
            assert hasattr(rec, 'reasoning')
            assert len(rec.reasoning) > 20  # Substantial reasoning

    def test_reasoning_explains_problem(self, observer_pattern_scenario):
        """Reasoning should explain the problem being solved."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(observer_pattern_scenario)

        if recommendations:
            rec = recommendations[0]
            # Reasoning should mention key concepts
            reasoning_lower = rec.reasoning.lower()
            assert any(word in reasoning_lower for word in [
                'notify', 'update', 'depend', 'coupling', 'change'
            ])


# 4. Applicability Scoring Tests
class TestApplicabilityScoring:
    """Test pattern applicability scoring."""

    def test_applicability_levels(self, strategy_pattern_scenario):
        """Should assign appropriate applicability levels."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        assert all(hasattr(r, 'applicability') for r in recommendations)
        assert all(isinstance(r.applicability, PatternApplicability) for r in recommendations)

    def test_high_applicability_for_obvious_cases(self, strategy_pattern_scenario):
        """Should give high applicability for obvious pattern needs."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # Strategy pattern should have high applicability for this case
        strategy_recs = [
            r for r in recommendations
            if r.pattern_type == PatternType.STRATEGY
        ]

        if strategy_recs:
            assert strategy_recs[0].applicability in [
                PatternApplicability.HIGH,
                PatternApplicability.VERY_HIGH
            ]


# 5. Recommendation Details Tests
class TestRecommendationDetails:
    """Test recommendation detail quality."""

    def test_recommendation_has_pattern_name(self, strategy_pattern_scenario):
        """Recommendations should include pattern name."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        if recommendations:
            rec = recommendations[0]
            assert rec.pattern_type is not None
            assert isinstance(rec.pattern_type, PatternType)

    def test_recommendation_has_benefits(self, observer_pattern_scenario):
        """Recommendations should list benefits."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(observer_pattern_scenario)

        if recommendations:
            rec = recommendations[0]
            assert hasattr(rec, 'benefits')
            assert isinstance(rec.benefits, list)
            assert len(rec.benefits) > 0

    def test_recommendation_has_implementation_hint(self, strategy_pattern_scenario):
        """Recommendations should include implementation hints."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        if recommendations:
            rec = recommendations[0]
            assert hasattr(rec, 'implementation_hint')
            assert len(rec.implementation_hint) > 10


# 6. Auto-CoT Integration Tests
class TestAutoCoTIntegration:
    """Test Auto-CoT technique integration."""

    def test_uses_auto_cot_demonstrations(self, strategy_pattern_scenario):
        """Should use Auto-CoT for generating demonstrations."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # Should have reasoning chains (Auto-CoT output)
        assert all(rec.reasoning for rec in recommendations)

    def test_clusters_similar_patterns(self):
        """Should cluster similar pattern scenarios."""
        agent = DesignPatternsRecommendationAgent()

        # Multiple similar scenarios with strategy pattern needs
        scenarios = [
            '''
if payment_type == 'credit':
    process_credit()
elif payment_type == 'debit':
    process_debit()
elif payment_type == 'paypal':
    process_paypal()
''',
            '''
if shipping_type == 'express':
    ship_express()
elif shipping_type == 'standard':
    ship_standard()
elif shipping_type == 'overnight':
    ship_overnight()
''',
            '''
if notification_type == 'email':
    send_email()
elif notification_type == 'sms':
    send_sms()
elif notification_type == 'push':
    send_push()
'''
        ]

        all_recs = []
        for scenario in scenarios:
            recs = agent.recommend_patterns(scenario)
            all_recs.extend(recs)

        # Should recommend similar patterns for similar code
        pattern_types = [r.pattern_type for r in all_recs]
        # All should recommend Strategy pattern
        assert len(all_recs) >= len(scenarios)  # At least one rec per scenario
        assert PatternType.STRATEGY in pattern_types  # Strategy should be recommended


# 7. Ranking Tests
class TestPatternRanking:
    """Test pattern recommendation ranking."""

    def test_recommendations_are_ranked(self, strategy_pattern_scenario):
        """Recommendations should be ranked by applicability."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # Should be sorted by applicability (high to low)
        if len(recommendations) > 1:
            applicability_values = [r.applicability.value for r in recommendations]
            assert applicability_values == sorted(applicability_values, reverse=True)

    def test_limits_recommendations(self):
        """Should limit number of recommendations."""
        agent = DesignPatternsRecommendationAgent(max_recommendations=2)

        code = '''
class ComplexClass:
    # Has many anti-patterns
    pass
''' * 10

        recommendations = agent.recommend_patterns(code)

        assert len(recommendations) <= 2


# 8. Edge Cases
class TestDesignPatternsEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_empty_code(self):
        """Should handle empty code gracefully."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns("")

        assert recommendations == []

    def test_handles_clean_code(self):
        """Should return empty or low-applicability for well-designed code."""
        agent = DesignPatternsRecommendationAgent()

        clean_code = '''
class UserRepository:
    def __init__(self, db):
        self.db = db

    def get(self, id):
        return self.db.query(id)
'''

        recommendations = agent.recommend_patterns(clean_code)

        # Clean code should have no or low-priority recommendations
        assert len(recommendations) == 0 or all(
            r.applicability in [PatternApplicability.LOW, PatternApplicability.MEDIUM]
            for r in recommendations
        )


# 9. Integration Tests
class TestDesignPatternsIntegration:
    """Test integration with other components."""

    def test_result_serializable(self, strategy_pattern_scenario):
        """Results should be serializable for pipeline."""
        agent = DesignPatternsRecommendationAgent()

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        if recommendations:
            rec_dict = recommendations[0].to_dict()
            assert isinstance(rec_dict, dict)
            assert 'pattern_type' in rec_dict
            assert 'applicability' in rec_dict


# 10. LLM Integration Tests (TDD - RED Phase)
class TestLLMIntegration:
    """Test LLM integration for design pattern recommendations."""

    def test_initializes_with_llm_config(self):
        """Should initialize with LLM configuration."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        agent = DesignPatternsRecommendationAgent(config=config)

        # WILL FAIL: Agent doesn't accept config yet
        assert hasattr(agent, 'llm_generator')
        assert agent.llm_generator is not None

    def test_uses_llm_for_recommendations(self, strategy_pattern_scenario):
        """Should use LLM for detailed pattern recommendations."""
        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent = DesignPatternsRecommendationAgent(config=config)

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # WILL FAIL: Currently uses only heuristics
        assert len(recommendations) > 0
        first_rec = recommendations[0]
        assert hasattr(first_rec, 'analysis_method')
        assert first_rec.analysis_method == 'llm'

    def test_llm_provides_better_reasoning(self, strategy_pattern_scenario):
        """LLM should provide more detailed reasoning than heuristics."""
        config_llm = {"llm_provider": "anthropic", "use_llm": True}
        config_heuristic = {"use_llm": False}

        agent_llm = DesignPatternsRecommendationAgent(config=config_llm)
        agent_heuristic = DesignPatternsRecommendationAgent(config=config_heuristic)

        recs_llm = agent_llm.recommend_patterns(strategy_pattern_scenario)
        recs_heuristic = agent_heuristic.recommend_patterns(strategy_pattern_scenario)

        # WILL FAIL: LLM reasoning should be more detailed
        if recs_llm and recs_heuristic:
            assert len(recs_llm[0].reasoning) > len(recs_heuristic[0].reasoning)

    def test_llm_finds_more_patterns(self, strategy_pattern_scenario):
        """LLM should identify more applicable patterns."""
        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }
        agent = DesignPatternsRecommendationAgent(config=config, max_recommendations=10)

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # WILL FAIL: LLM should find multiple patterns
        assert len(recommendations) >= 2

    def test_fallback_to_heuristics_when_llm_fails(self, strategy_pattern_scenario):
        """Should fallback to heuristics if LLM fails."""
        config = {
            "llm_provider": "anthropic",
            "model": "invalid-model",
            "use_llm": True
        }
        agent = DesignPatternsRecommendationAgent(config=config)

        recommendations = agent.recommend_patterns(strategy_pattern_scenario)

        # WILL FAIL: No fallback mechanism yet
        assert len(recommendations) > 0
        if recommendations:
            assert recommendations[0].analysis_method == 'heuristic'

    def test_respects_api_key_validation(self):
        """Should validate API key before using LLM."""
        import os
        original_key = os.environ.get('ANTHROPIC_API_KEY')
        if original_key:
            del os.environ['ANTHROPIC_API_KEY']

        config = {
            "llm_provider": "anthropic",
            "use_llm": True
        }

        try:
            agent = DesignPatternsRecommendationAgent(config=config)
            # WILL FAIL: Should handle missing API key
            assert hasattr(agent, 'llm_generator')
            assert agent.config.get('use_llm') == False or agent.llm_generator is None
        finally:
            if original_key:
                os.environ['ANTHROPIC_API_KEY'] = original_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
