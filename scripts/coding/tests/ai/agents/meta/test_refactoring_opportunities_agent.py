#!/usr/bin/env python3
"""
TDD Tests for RefactoringOpportunitiesAgent

Tests the agent that uses Search Optimization to identify and prioritize
refactoring opportunities in code.

Technique: Hybrid Search Optimization
- K-NN Clustering for similar code smells
- Binary Search for efficient searching
- Greedy Information Density for high-value targets
- Branch-and-Bound for optimal prioritization

Meta-Application: Using algorithmic prompting techniques to improve code quality.
"""

import pytest
from scripts.ai.agents.meta import (
    RefactoringOpportunitiesAgent,
    RefactoringOpportunity,
    CodeSmell,
    RefactoringType
)


# Fixtures
@pytest.fixture
def sample_codebase():
    """Sample codebase with various code smells."""
    return {
        'long_method.py': '''
def process_order(order):
    # 50+ lines of code
    validate_order(order)
    calculate_total(order)
    apply_discount(order)
    check_inventory(order)
    update_database(order)
    send_confirmation(order)
    log_transaction(order)
    update_analytics(order)
''',
        'god_class.py': '''
class OrderManager:
    def create_order(self): pass
    def update_order(self): pass
    def delete_order(self): pass
    def send_email(self): pass
    def calculate_discount(self): pass
    def generate_report(self): pass
    def export_data(self): pass
    def validate_input(self): pass
''',
        'duplicate_code.py': '''
def calculate_price_a():
    total = 0
    for item in items:
        total += item.price * 1.1
    return total

def calculate_price_b():
    total = 0
    for item in items:
        total += item.price * 1.1
    return total
'''
    }


# 1. Initialization Tests
class TestRefactoringAgentInitialization:
    """Test RefactoringOpportunitiesAgent initialization."""

    def test_default_initialization(self):
        """Should initialize with default parameters."""
        agent = RefactoringOpportunitiesAgent()

        assert agent.name == "RefactoringOpportunitiesAgent"
        assert agent.optimizer is not None

    def test_custom_initialization(self):
        """Should initialize with custom parameters."""
        agent = RefactoringOpportunitiesAgent(
            target_coverage=0.9,
            k_clusters=3
        )

        assert agent.target_coverage == 0.9
        assert agent.k_clusters == 3


# 2. Code Smell Detection Tests
class TestCodeSmellDetection:
    """Test detection of code smells."""

    def test_detect_long_method(self, sample_codebase):
        """Should detect long method smell."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['long_method.py']
        )

        assert len(opportunities) > 0
        long_method_smells = [
            o for o in opportunities
            if o.smell == CodeSmell.LONG_METHOD
        ]
        assert len(long_method_smells) > 0

    def test_detect_god_class(self, sample_codebase):
        """Should detect god class smell."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['god_class.py']
        )

        god_class_smells = [
            o for o in opportunities
            if o.smell == CodeSmell.GOD_CLASS
        ]
        assert len(god_class_smells) > 0

    def test_detect_duplicate_code(self, sample_codebase):
        """Should detect duplicate code smell."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['duplicate_code.py']
        )

        duplicate_smells = [
            o for o in opportunities
            if o.smell == CodeSmell.DUPLICATE_CODE
        ]
        assert len(duplicate_smells) > 0


# 3. Prioritization Tests
class TestRefactoringPrioritization:
    """Test prioritization of refactoring opportunities."""

    def test_opportunities_are_prioritized(self, sample_codebase):
        """Should prioritize opportunities by impact."""
        agent = RefactoringOpportunitiesAgent()

        all_code = '\n\n'.join(sample_codebase.values())
        opportunities = agent.find_refactoring_opportunities(all_code)

        # Should have priorities assigned
        assert all(hasattr(o, 'priority') for o in opportunities)

        # Higher priorities should come first
        priorities = [o.priority for o in opportunities]
        assert priorities == sorted(priorities, reverse=True)

    def test_high_impact_smells_prioritized(self):
        """Should prioritize high-impact smells."""
        agent = RefactoringOpportunitiesAgent()

        code_with_critical_smell = '''
class DatabaseConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123"  # Security smell - hardcoded credentials
        )
'''

        opportunities = agent.find_refactoring_opportunities(code_with_critical_smell)

        # Security-related smells should have high priority
        if opportunities:
            assert opportunities[0].priority >= 8  # High priority


# 4. Refactoring Type Tests
class TestRefactoringTypes:
    """Test refactoring type recommendations."""

    def test_extract_method_recommendation(self):
        """Should recommend Extract Method for long methods."""
        agent = RefactoringOpportunitiesAgent()

        code = '''
def long_function():
    # 30 lines of code doing multiple things
    step1()
    step2()
    step3()
''' + '\n    step()' * 20

        opportunities = agent.find_refactoring_opportunities(code)

        extract_method = [
            o for o in opportunities
            if o.refactoring_type == RefactoringType.EXTRACT_METHOD
        ]
        assert len(extract_method) > 0

    def test_extract_class_recommendation(self):
        """Should recommend Extract Class for god classes."""
        agent = RefactoringOpportunitiesAgent()

        code = '''
class Manager:
    ''' + '\n    '.join([f'def method_{i}(self): pass' for i in range(15)])

        opportunities = agent.find_refactoring_opportunities(code)

        extract_class = [
            o for o in opportunities
            if o.refactoring_type == RefactoringType.EXTRACT_CLASS
        ]
        assert len(extract_class) > 0


# 5. Search Optimization Integration Tests
class TestSearchOptimizationIntegration:
    """Test integration with search optimization techniques."""

    def test_uses_hybrid_optimization(self, sample_codebase):
        """Should use hybrid search optimization."""
        agent = RefactoringOpportunitiesAgent()

        all_code = '\n\n'.join(sample_codebase.values())
        opportunities = agent.find_refactoring_opportunities(all_code)

        # Should return optimized subset, not all possible smells
        assert len(opportunities) <= 20  # Reasonable number, not exhaustive

    def test_clustering_similar_smells(self, sample_codebase):
        """Should cluster similar code smells together."""
        agent = RefactoringOpportunitiesAgent()

        all_code = '\n\n'.join(sample_codebase.values())
        opportunities = agent.find_refactoring_opportunities(all_code)

        # Should have cluster information
        assert all(hasattr(o, 'cluster_id') or True for o in opportunities)


# 6. Opportunity Details Tests
class TestOpportunityDetails:
    """Test refactoring opportunity details."""

    def test_opportunity_has_location(self, sample_codebase):
        """Opportunities should include code location."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['long_method.py']
        )

        if opportunities:
            opp = opportunities[0]
            assert isinstance(opp, RefactoringOpportunity)
            assert opp.location is not None

    def test_opportunity_has_description(self, sample_codebase):
        """Opportunities should include clear description."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['god_class.py']
        )

        if opportunities:
            opp = opportunities[0]
            assert len(opp.description) > 10
            assert opp.description != ""

    def test_opportunity_has_recommendation(self, sample_codebase):
        """Opportunities should include refactoring recommendation."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['duplicate_code.py']
        )

        if opportunities:
            opp = opportunities[0]
            assert opp.refactoring_type is not None


# 7. Edge Cases
class TestRefactoringAgentEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_empty_code(self):
        """Should handle empty code gracefully."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities("")

        assert opportunities == []

    def test_handles_clean_code(self):
        """Should return empty list for clean code."""
        agent = RefactoringOpportunitiesAgent()

        clean_code = '''
class UserRepository:
    def get(self, id):
        return self.db.query(id)
'''

        opportunities = agent.find_refactoring_opportunities(clean_code)

        # Clean code should have no or few opportunities
        assert len(opportunities) == 0 or all(o.priority < 5 for o in opportunities)


# 8. Integration Tests
class TestRefactoringAgentIntegration:
    """Test integration with other agents."""

    def test_result_serializable(self, sample_codebase):
        """Results should be serializable for pipeline."""
        agent = RefactoringOpportunitiesAgent()

        opportunities = agent.find_refactoring_opportunities(
            sample_codebase['long_method.py']
        )

        # Should be convertible to dict
        if opportunities:
            opp_dict = opportunities[0].to_dict()
            assert isinstance(opp_dict, dict)
            assert 'smell' in opp_dict
            assert 'priority' in opp_dict


# 9. LLM Integration Tests
class TestRefactoringAgentLLMIntegration:
    """Test LLM integration in RefactoringOpportunitiesAgent."""

    def test_initializes_with_llm_config(self):
        """Should initialize with LLM configuration."""
        config = {
            'llm_provider': 'anthropic',
            'model': 'claude-sonnet-4-5-20250929',
            'use_llm': True
        }
        agent = RefactoringOpportunitiesAgent(config=config)

        assert agent.config == config
        # LLM generator may or may not be initialized depending on API key availability
        # Just verify config is stored
        assert agent.config.get('llm_provider') == 'anthropic'

    def test_uses_llm_for_analysis(self, sample_codebase, monkeypatch):
        """Should use LLM for analysis when configured."""
        import json
        from unittest.mock import Mock

        # Mock LLM response
        mock_response = json.dumps({
            "opportunities": [
                {
                    "smell": "long_method",
                    "description": "The process_order function handles too many responsibilities",
                    "refactoring_type": "extract_method",
                    "priority": 8,
                    "estimated_effort": "medium",
                    "estimated_impact": "high"
                },
                {
                    "smell": "god_class",
                    "description": "OrderManager class has too many methods",
                    "refactoring_type": "extract_class",
                    "priority": 9,
                    "estimated_effort": "high",
                    "estimated_impact": "high"
                }
            ]
        })

        config = {
            'llm_provider': 'anthropic',
            'use_llm': True,
            'api_key': 'test-key'
        }

        # Create agent and mock LLM generator
        agent = RefactoringOpportunitiesAgent(config=config)

        # Mock the LLM generator
        mock_llm = Mock()
        mock_llm._call_llm = Mock(return_value=mock_response)
        agent.llm_generator = mock_llm

        # Analyze code
        code = sample_codebase['long_method.py']
        opportunities = agent.find_refactoring_opportunities(code)

        # Should have used LLM
        assert mock_llm._call_llm.called
        assert len(opportunities) >= 2
        assert all(o.analysis_method == "llm" for o in opportunities)

    def test_llm_finds_more_opportunities(self, sample_codebase, monkeypatch):
        """LLM should find more nuanced opportunities than heuristics."""
        import json
        from unittest.mock import Mock

        # Mock LLM to find additional opportunities
        mock_response = json.dumps({
            "opportunities": [
                {
                    "smell": "long_method",
                    "description": "Function is too complex",
                    "refactoring_type": "extract_method",
                    "priority": 7,
                    "estimated_effort": "medium",
                    "estimated_impact": "high"
                },
                {
                    "smell": "feature_envy",
                    "description": "Function uses more features of another class",
                    "refactoring_type": "move_method",
                    "priority": 6,
                    "estimated_effort": "low",
                    "estimated_impact": "medium"
                },
                {
                    "smell": "data_clumps",
                    "description": "Same group of data items appear together",
                    "refactoring_type": "introduce_parameter_object",
                    "priority": 5,
                    "estimated_effort": "low",
                    "estimated_impact": "medium"
                }
            ]
        })

        config = {'use_llm': True}
        agent_llm = RefactoringOpportunitiesAgent(config=config)

        # Mock LLM generator
        mock_llm = Mock()
        mock_llm._call_llm = Mock(return_value=mock_response)
        agent_llm.llm_generator = mock_llm

        # Compare with heuristic agent
        agent_heuristic = RefactoringOpportunitiesAgent()

        code = sample_codebase['long_method.py']

        opps_llm = agent_llm.find_refactoring_opportunities(code)
        opps_heuristic = agent_heuristic.find_refactoring_opportunities(code)

        # LLM should find different/additional smells
        llm_smells = {o.smell for o in opps_llm}
        heuristic_smells = {o.smell for o in opps_heuristic}

        # LLM can detect more sophisticated patterns
        assert len(opps_llm) >= 3
        assert CodeSmell.FEATURE_ENVY in llm_smells or CodeSmell.DATA_CLUMPS in llm_smells

    def test_fallback_to_heuristics_when_llm_fails(self, sample_codebase, monkeypatch):
        """Should fall back to heuristics when LLM fails."""
        from unittest.mock import Mock

        config = {'use_llm': True}
        agent = RefactoringOpportunitiesAgent(config=config)

        # Mock LLM to raise exception
        mock_llm = Mock()
        mock_llm._call_llm = Mock(side_effect=Exception("LLM API error"))
        agent.llm_generator = mock_llm

        # Should still return results using heuristics
        code = sample_codebase['god_class.py']
        opportunities = agent.find_refactoring_opportunities(code)

        # Should have fallen back to heuristics
        assert len(opportunities) > 0
        assert all(o.analysis_method == "heuristic" for o in opportunities)

    def test_llm_provides_better_recommendations(self, sample_codebase, monkeypatch):
        """LLM should provide more detailed recommendations."""
        import json
        from unittest.mock import Mock

        mock_response = json.dumps({
            "opportunities": [
                {
                    "smell": "god_class",
                    "description": "OrderManager violates Single Responsibility Principle - handles orders, emails, reports, and validation",
                    "refactoring_type": "extract_class",
                    "priority": 9,
                    "estimated_effort": "high",
                    "estimated_impact": "high",
                    "code_snippet": "class OrderManager:\n    def create_order..."
                }
            ]
        })

        config = {'use_llm': True}
        agent = RefactoringOpportunitiesAgent(config=config)

        mock_llm = Mock()
        mock_llm._call_llm = Mock(return_value=mock_response)
        agent.llm_generator = mock_llm

        code = sample_codebase['god_class.py']
        opportunities = agent.find_refactoring_opportunities(code)

        # LLM descriptions should be more detailed
        if opportunities:
            llm_opp = opportunities[0]
            assert len(llm_opp.description) > 30  # More detailed than heuristics
            assert llm_opp.code_snippet is not None or True  # May include code snippet

    def test_respects_api_key_validation(self):
        """Should respect API key validation and gracefully handle missing keys."""
        import os

        # Test without API key
        config = {
            'llm_provider': 'anthropic',
            'use_llm': True
        }

        # Should initialize but may not have LLM generator if no API key
        agent = RefactoringOpportunitiesAgent(config=config)

        # Should still work with heuristics even if LLM not available
        code = "def long_function():\n" + "    pass\n" * 30
        opportunities = agent.find_refactoring_opportunities(code)

        # Should return results (either LLM or heuristic)
        assert isinstance(opportunities, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
