# FASE 3: DESIGN - Diseño de Tests TDD para Técnicas de Prompting

**Agent**: SDLCDesignAgent
**Fecha**: 2025-11-14
**Decisión**: GO
**Técnicas aplicadas**: Expert Prompting, Pattern Recognition, RAG

---

## High-Level Design (HLD)

### Arquitectura General

```
scripts/coding/ai/
├── agents/base/                    # Código a testear
│   ├── auto_cot_agent.py
│   ├── self_consistency.py
│   └── ...
└── tests/
    ├── conftest.py                # Fixtures compartidos
    ├── techniques/                # Tests de técnicas
    │   ├── __init__.py
    │   ├── test_auto_cot_agent.py
    │   ├── test_self_consistency.py
    │   └── ...
    ├── fixtures/                  # Fixtures específicos
    │   ├── llm_responses.py      # Mock responses
    │   ├── sample_data.py        # Datos de prueba
    │   └── agent_mocks.py        # Agent mocks
    └── integration/              # Tests de integración
        └── test_techniques_integration.py
```

### Componentes Principales

#### 1. Test Infrastructure

**conftest.py** - Configuración global
- Fixtures compartidos
- Configuración de pytest
- Hooks de setup/teardown
- Coverage configuration

#### 2. Mock Layer

**fixtures/llm_responses.py** - Responses predefinidas
- Mock responses para cada técnica
- Multiple scenarios (success, error, edge cases)
- Parametrización de responses

#### 3. Test Suites

**tests/techniques/** - Tests por módulo
- Test unitarios aislados
- Tests parametrizados
- Assertions específicas

#### 4. Integration Tests

**tests/integration/** - Tests end-to-end
- Técnicas interactuando
- Flujos completos
- Performance tests

---

## Low-Level Design (LLD)

### 1. conftest.py - Fixtures Compartidos

```python
# conftest.py
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_llm_generator():
    """Mock LLMGenerator con responses predefinidas."""
    mock = MagicMock()

    # Response genérica
    mock.generate.return_value = {
        "content": "Mock response content",
        "model": "mock-model",
        "usage": {"tokens": 100}
    }

    return mock

@pytest.fixture
def sample_question():
    """Pregunta de ejemplo para tests."""
    return "¿Cuáles son las implicaciones de seguridad de este código?"

@pytest.fixture
def sample_context():
    """Contexto de ejemplo."""
    return """
    def authenticate_user(username, password):
        # Code here
        pass
    """

@pytest.fixture
def auto_cot_responses():
    """Responses para Auto-CoT tests."""
    return [
        {"thought": "Step 1", "action": "analyze", "observation": "result1"},
        {"thought": "Step 2", "action": "reason", "observation": "result2"},
        {"thought": "Step 3", "action": "conclude", "observation": "final"}
    ]

@pytest.fixture
def self_consistency_responses():
    """Multiple responses para Self-Consistency."""
    return [
        {"answer": "Option A", "reasoning": "Because..."},
        {"answer": "Option A", "reasoning": "Different reason..."},
        {"answer": "Option B", "reasoning": "Alternative..."},
        {"answer": "Option A", "reasoning": "Another reason..."},
    ]
```

### 2. test_auto_cot_agent.py - Tests para Auto-CoT

```python
# tests/techniques/test_auto_cot_agent.py
import pytest
from scripts.coding.ai.agents.base.auto_cot_agent import AutoCoTAgent

class TestAutoCoTAgent:
    """Tests para AutoCoTAgent - Automatic Chain-of-Thought."""

    def test_init_default_config(self):
        """Test inicialización con configuración por defecto."""
        agent = AutoCoTAgent()

        assert agent.enable_clustering == True
        assert agent.num_demonstrations >= 1
        assert hasattr(agent, 'execute')

    def test_init_custom_config(self):
        """Test inicialización con configuración custom."""
        config = {
            "enable_clustering": False,
            "num_demonstrations": 3,
            "model": "test-model"
        }
        agent = AutoCoTAgent(config=config)

        assert agent.enable_clustering == False
        assert agent.num_demonstrations == 3

    def test_execute_simple_question(self, mock_llm_generator, sample_question):
        """Test ejecución con pregunta simple."""
        agent = AutoCoTAgent()
        agent.llm_generator = mock_llm_generator

        result = agent.execute({
            "question": sample_question,
            "context": ""
        })

        assert "answer" in result
        assert "reasoning_chain" in result
        assert len(result["reasoning_chain"]) > 0

    def test_question_clustering(self, mock_llm_generator):
        """Test clustering de preguntas similares."""
        agent = AutoCoTAgent(config={"enable_clustering": True})
        agent.llm_generator = mock_llm_generator

        questions = [
            "How to secure authentication?",
            "Best practices for auth security",
            "What are authentication vulnerabilities?"
        ]

        clusters = agent.cluster_questions(questions)

        assert len(clusters) >= 1
        assert all(len(cluster) > 0 for cluster in clusters)

    def test_demonstration_sampling(self, auto_cot_responses):
        """Test sampling de demostraciones representativas."""
        agent = AutoCoTAgent()

        demonstrations = agent.sample_demonstrations(
            auto_cot_responses,
            num_samples=2
        )

        assert len(demonstrations) == 2
        assert all("thought" in demo for demo in demonstrations)

    @pytest.mark.parametrize("num_demos", [1, 3, 5])
    def test_different_num_demonstrations(self, num_demos, mock_llm_generator):
        """Test con diferentes números de demostraciones."""
        agent = AutoCoTAgent(config={"num_demonstrations": num_demos})
        agent.llm_generator = mock_llm_generator

        result = agent.execute({"question": "Test question"})

        assert result is not None

    def test_error_handling_invalid_question(self):
        """Test manejo de errores con pregunta inválida."""
        agent = AutoCoTAgent()

        with pytest.raises(ValueError):
            agent.execute({"question": ""})

    def test_error_handling_missing_input(self):
        """Test manejo de errores con input faltante."""
        agent = AutoCoTAgent()

        with pytest.raises(KeyError):
            agent.execute({})

    def test_zero_shot_cot_generation(self, mock_llm_generator, sample_question):
        """Test generación Zero-Shot CoT."""
        agent = AutoCoTAgent(config={"num_demonstrations": 0})
        agent.llm_generator = mock_llm_generator

        result = agent.execute({"question": sample_question})

        assert result is not None
        assert "reasoning_chain" in result
```

### 3. test_self_consistency.py - Tests para Self-Consistency

```python
# tests/techniques/test_self_consistency.py
import pytest
from scripts.coding.ai.agents.base.self_consistency import SelfConsistencyAgent

class TestSelfConsistencyAgent:
    """Tests para SelfConsistencyAgent - Multiple Reasoning Paths."""

    def test_init_default_config(self):
        """Test inicialización con valores por defecto."""
        agent = SelfConsistencyAgent()

        assert agent.num_samples >= 3
        assert 0 <= agent.temperature <= 1.0

    def test_execute_multiple_samples(self, mock_llm_generator, sample_question):
        """Test generación de múltiples samples."""
        agent = SelfConsistencyAgent(config={"num_samples": 5})
        agent.llm_generator = mock_llm_generator

        result = agent.execute({"question": sample_question})

        assert "final_answer" in result
        assert "samples" in result
        assert len(result["samples"]) == 5

    def test_majority_voting(self, self_consistency_responses):
        """Test votación por mayoría."""
        agent = SelfConsistencyAgent()

        winner = agent.majority_vote(self_consistency_responses)

        assert winner == "Option A"  # 3 votes vs 1 vote

    def test_consistency_scoring(self, self_consistency_responses):
        """Test scoring de consistencia."""
        agent = SelfConsistencyAgent()

        score = agent.calculate_consistency_score(self_consistency_responses)

        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be > 0.5 since Option A is majority

    @pytest.mark.parametrize("num_samples,expected_time", [
        (3, "fast"),
        (10, "medium"),
        (20, "slow")
    ])
    def test_performance_scales_with_samples(self, num_samples, expected_time, mock_llm_generator):
        """Test que performance escala con número de samples."""
        agent = SelfConsistencyAgent(config={"num_samples": num_samples})
        agent.llm_generator = mock_llm_generator

        import time
        start = time.time()
        agent.execute({"question": "Test"})
        duration = time.time() - start

        # Verify it scales linearly (mock should be fast)
        assert duration < num_samples * 0.1  # Mock should be < 0.1s each

    def test_temperature_affects_diversity(self, mock_llm_generator):
        """Test que temperatura afecta diversidad de respuestas."""
        agent_low_temp = SelfConsistencyAgent(config={
            "temperature": 0.1,
            "num_samples": 3
        })
        agent_high_temp = SelfConsistencyAgent(config={
            "temperature": 0.9,
            "num_samples": 3
        })

        # This test validates the configuration is passed
        assert agent_low_temp.temperature < agent_high_temp.temperature
```

### 4. fixtures/llm_responses.py - Mock Responses

```python
# tests/fixtures/llm_responses.py
"""Mock LLM responses para testing."""

AUTO_COT_RESPONSES = {
    "security_analysis": {
        "reasoning_chain": [
            {
                "step": 1,
                "thought": "Analizar método de autenticación",
                "observation": "Usa password en texto plano"
            },
            {
                "step": 2,
                "thought": "Evaluar riesgos",
                "observation": "Alto riesgo de intercepción"
            },
            {
                "step": 3,
                "thought": "Recomendar mitigación",
                "observation": "Usar hashing y salts"
            }
        ],
        "answer": "El código presenta vulnerabilidades de seguridad..."
    },
    "edge_case_empty_input": {
        "reasoning_chain": [],
        "answer": "",
        "error": "No input provided"
    }
}

SELF_CONSISTENCY_RESPONSES = {
    "architecture_decision": [
        {
            "answer": "Microservices",
            "reasoning": "Better scalability and independence",
            "confidence": 0.8
        },
        {
            "answer": "Microservices",
            "reasoning": "Easier to maintain and deploy",
            "confidence": 0.7
        },
        {
            "answer": "Monolith",
            "reasoning": "Simpler for small team",
            "confidence": 0.5
        },
        {
            "answer": "Microservices",
            "reasoning": "Industry best practice",
            "confidence": 0.9
        }
    ]
}

CHAIN_OF_VERIFICATION_RESPONSES = {
    "initial_response": "The function authenticates users by checking password",
    "verification_questions": [
        "Does it use secure password hashing?",
        "Does it prevent SQL injection?",
        "Does it implement rate limiting?"
    ],
    "verification_answers": [
        "No, password is in plaintext",
        "Yes, uses parameterized queries",
        "No, no rate limiting implemented"
    ],
    "refined_response": "The function has security gaps: no password hashing and no rate limiting"
}
```

---

## Patrones de Testing

### Pattern 1: AAA (Arrange-Act-Assert)

```python
def test_feature():
    # Arrange
    agent = AutoCoTAgent()
    input_data = {"question": "test"}

    # Act
    result = agent.execute(input_data)

    # Assert
    assert result is not None
```

### Pattern 2: Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("question1", "answer1"),
    ("question2", "answer2"),
])
def test_multiple_cases(input, expected):
    assert process(input) == expected
```

### Pattern 3: Fixture Composition

```python
@pytest.fixture
def configured_agent(mock_llm_generator):
    agent = AutoCoTAgent()
    agent.llm_generator = mock_llm_generator
    return agent

def test_with_configured_agent(configured_agent):
    result = configured_agent.execute({"question": "test"})
    assert result is not None
```

---

## Assertions Específicas

### Auto-CoT Assertions

```python
def assert_valid_reasoning_chain(chain):
    assert isinstance(chain, list)
    assert len(chain) > 0
    for step in chain:
        assert "thought" in step
        assert "observation" in step
        assert isinstance(step["thought"], str)
```

### Self-Consistency Assertions

```python
def assert_valid_consistency_result(result):
    assert "final_answer" in result
    assert "samples" in result
    assert "consistency_score" in result
    assert 0.0 <= result["consistency_score"] <= 1.0
    assert len(result["samples"]) >= 3
```

---

## Coverage Strategy

### Target Coverage por Módulo

| Módulo | Target | Strategy |
|--------|--------|----------|
| auto_cot_agent | 85% | Parametrized tests + edge cases |
| self_consistency | 85% | Multiple scenarios + voting tests |
| chain_of_verification | 80% | Step-by-step validation |
| tree_of_thoughts | 75% | Tree traversal tests |
| fundamental_techniques | 90% | Simple, high coverage |
| Others | 80% | Standard coverage |

### Exclusions

- `__init__.py` files
- Import-only code
- Debug/logging statements

---

## Próximo Paso

**Fase 4: Testing Strategy**
Implementar los tests siguiendo este diseño y aplicando Auto-CoT y Self-Consistency.

**Decisión**: GO ✅
