"""
Configuración global de pytest y fixtures compartidos para tests de técnicas de prompting.

Este archivo proporciona fixtures reutilizables para todos los tests, incluyendo:
- Mock LLM generators
- Sample data (preguntas, contextos, respuestas)
- Configuraciones de agentes
- Utilidades de assertions

Generado usando SDLC pipeline con Auto-CoT y Self-Consistency.
Fecha: 2025-11-14
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock, patch


# ============================================================================
# LLM Mocking Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_generator():
    """
    Mock LLMGenerator con responses predefinidas.

    Returns:
        MagicMock: Mock objeto que simula LLMGenerator
    """
    mock = MagicMock()

    # Response genérica por defecto
    mock.generate.return_value = {
        "content": "This is a mock response content from the LLM.",
        "model": "mock-model-v1",
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150
        },
        "finish_reason": "stop"
    }

    return mock


@pytest.fixture
def mock_llm_with_custom_response():
    """
    Factory para crear mock LLM con response customizada.

    Usage:
        mock = mock_llm_with_custom_response("custom response")
    """
    def _create_mock(response_content: str):
        mock = MagicMock()
        mock.generate.return_value = {
            "content": response_content,
            "model": "mock-model",
            "usage": {"total_tokens": 100}
        }
        return mock

    return _create_mock


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_question():
    """Pregunta de ejemplo para tests."""
    return "¿Cuáles son las implicaciones de seguridad de este código?"


@pytest.fixture
def sample_context():
    """Contexto de código de ejemplo."""
    return """
def authenticate_user(username, password):
    # Authenticate user against database
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_query(query)
    return result is not None
"""


@pytest.fixture
def sample_questions_list():
    """Lista de preguntas para clustering tests."""
    return [
        "How to secure authentication in web applications?",
        "Best practices for password hashing and storage",
        "What are common authentication vulnerabilities?",
        "How to implement OAuth2 securely?",
        "SQL injection prevention techniques",
        "How to validate user input properly?"
    ]


# ============================================================================
# Auto-CoT Specific Fixtures
# ============================================================================

@pytest.fixture
def auto_cot_responses():
    """Responses de ejemplo para Auto-CoT tests."""
    return [
        {
            "step": 1,
            "thought": "Necesito analizar el método de autenticación usado",
            "action": "analyze_code",
            "observation": "El código usa una query SQL directa con concatenación de strings"
        },
        {
            "step": 2,
            "thought": "Esto indica una vulnerabilidad de SQL injection",
            "action": "identify_vulnerability",
            "observation": "Confirmed: SQL injection vulnerability presente"
        },
        {
            "step": 3,
            "thought": "Debo evaluar el impacto y recomendar mitigación",
            "action": "assess_risk",
            "observation": "Riesgo CRÍTICO: Acceso no autorizado a base de datos"
        },
        {
            "step": 4,
            "thought": "Generar recomendaciones de corrección",
            "action": "generate_recommendations",
            "observation": "Usar parametrized queries, validar input, implementar ORM"
        }
    ]


@pytest.fixture
def auto_cot_demo_questions():
    """Preguntas para demonstrations en Auto-CoT."""
    return [
        {
            "question": "¿Cómo prevenir XSS?",
            "reasoning": "Analizar inputs → Sanitizar → Escapar output",
            "answer": "Sanitizar inputs y escapar outputs"
        },
        {
            "question": "¿Qué es CSRF?",
            "reasoning": "Definir CSRF → Identificar vectores → Mitigaciones",
            "answer": "Cross-Site Request Forgery: usar tokens"
        }
    ]


# ============================================================================
# Self-Consistency Specific Fixtures
# ============================================================================

@pytest.fixture
def self_consistency_responses():
    """Multiple responses para Self-Consistency tests."""
    return [
        {
            "answer": "Use microservices architecture",
            "reasoning": "Better scalability and maintainability for large teams",
            "confidence": 0.85
        },
        {
            "answer": "Use microservices architecture",
            "reasoning": "Independent deployment and technology choices per service",
            "confidence": 0.78
        },
        {
            "answer": "Use monolithic architecture",
            "reasoning": "Simpler for small teams, easier debugging",
            "confidence": 0.55
        },
        {
            "answer": "Use microservices architecture",
            "reasoning": "Industry best practice for scalable systems",
            "confidence": 0.90
        },
        {
            "answer": "Use microservices architecture",
            "reasoning": "Better fault isolation and resilience",
            "confidence": 0.82
        }
    ]


@pytest.fixture
def self_consistency_edge_cases():
    """Edge cases para Self-Consistency."""
    return {
        "all_same": [
            {"answer": "A", "confidence": 0.9},
            {"answer": "A", "confidence": 0.9},
            {"answer": "A", "confidence": 0.9}
        ],
        "tie": [
            {"answer": "A", "confidence": 0.8},
            {"answer": "B", "confidence": 0.8}
        ],
        "empty": [],
        "single": [
            {"answer": "A", "confidence": 0.9}
        ]
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def default_agent_config():
    """Configuración por defecto para agentes."""
    return {
        "llm_provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "temperature": 0.7,
        "max_tokens": 2000,
        "enable_guardrails": True
    }


@pytest.fixture
def auto_cot_config():
    """Configuración específica para Auto-CoT."""
    return {
        "enable_clustering": True,
        "num_demonstrations": 3,
        "temperature": 0.7,
        "model": "test-model"
    }


@pytest.fixture
def self_consistency_config():
    """Configuración específica para Self-Consistency."""
    return {
        "num_samples": 5,
        "temperature": 0.8,
        "voting_strategy": "majority",
        "min_consistency_score": 0.6
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def assert_valid_response():
    """Helper para validar estructura de response."""
    def _validator(response: Dict[str, Any], required_keys: List[str]):
        assert isinstance(response, dict), "Response debe ser un diccionario"
        for key in required_keys:
            assert key in response, f"Response debe contener '{key}'"
        return True
    return _validator


@pytest.fixture
def create_mock_agent():
    """Factory para crear agentes mock."""
    def _factory(agent_class, config=None):
        mock_agent = Mock(spec=agent_class)
        if config:
            mock_agent.config = config
        mock_agent.execute = Mock(return_value={"result": "mock"})
        return mock_agent
    return _factory


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configuración personalizada de pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_llm: marks tests that require real LLM (skip in CI)"
    )


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Cleanup if needed
    pass
