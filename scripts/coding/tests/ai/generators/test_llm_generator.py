#!/usr/bin/env python3
"""
TDD Tests for LLMGenerator

Tests the LLMGenerator implementation which generates test code using LLMs.
Supports Anthropic (Claude), OpenAI (ChatGPT), Ollama (local models), and
Hugging Face pipelines for fine-tuned checkpoints.

Tests cover initialization, validation, LLM calls, error handling, and fallbacks.
"""

import json
import os
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch, Mock, mock_open

import importlib.machinery
import importlib.util
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
CODING_ROOT = SCRIPTS_ROOT / "coding"

# Ensure namespace package resolution for `scripts.ai` imports used across the suite
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CODING_ROOT))

namespace_paths = [str(SCRIPTS_ROOT), str(CODING_ROOT)]
scripts_pkg = ModuleType("scripts")
scripts_pkg.__package__ = "scripts"
scripts_pkg.__path__ = namespace_paths
scripts_pkg.__spec__ = importlib.machinery.ModuleSpec(
    name="scripts",
    loader=None,
    is_package=True
)
sys.modules["scripts"] = scripts_pkg

try:
    from scripts.ai.generators.llm_generator import LLMGenerator
except ModuleNotFoundError:
    module_path = CODING_ROOT / "ai" / "generators" / "llm_generator.py"
    spec = importlib.util.spec_from_file_location(
        "scripts.ai.generators.llm_generator",
        module_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "No se pudo cargar spec para llm_generator"
    spec.loader.exec_module(module)
    sys.modules["scripts.ai.generators.llm_generator"] = module
    LLMGenerator = module.LLMGenerator


# Fixtures
@pytest.fixture
def sample_test_plan():
    """Sample test plan for testing."""
    return {
        "source_file": "scripts/example/module.py",
        "test_file": "tests/example/test_module.py",
        "test_cases": [
            {
                "name": "test_function_success",
                "description": "Test function with valid input"
            },
            {
                "name": "test_function_error",
                "description": "Test function with invalid input"
            }
        ]
    }


@pytest.fixture
def sample_source_code():
    """Sample source code to test."""
    return """
def calculate_sum(a, b):
    \"\"\"Calculate sum of two numbers.\"\"\"
    return a + b
"""


@pytest.fixture
def sample_generated_code():
    """Sample generated test code."""
    return """
import pytest

def test_calculate_sum_success():
    \"\"\"Test calculate_sum with valid input.\"\"\"
    result = calculate_sum(2, 3)
    assert result == 5

def test_calculate_sum_negative():
    \"\"\"Test calculate_sum with negative numbers.\"\"\"
    result = calculate_sum(-2, -3)
    assert result == -5
"""


@pytest.fixture
def sample_input_data(tmp_path, sample_test_plan):
    """Sample input data for agent run."""
    # Create source file
    source_file = tmp_path / "scripts" / "example" / "module.py"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("def calculate_sum(a, b): return a + b")

    return {
        "test_plans": [sample_test_plan],
        "project_path": str(tmp_path)
    }


# 1. Initialization Tests
class TestLLMGeneratorInitialization:
    """Test LLMGenerator initialization with different providers."""

    def test_default_initialization_anthropic(self):
        """Should initialize with Anthropic as default provider."""
        agent = LLMGenerator()

        assert agent.name == "LLMGenerator"
        assert agent.llm_provider == "anthropic"
        assert agent.model == "claude-sonnet-4-5-20250929"
        assert agent._client is None

    def test_initialization_with_anthropic_config(self):
        """Should initialize with Anthropic config."""
        config = {
            "llm_provider": "anthropic",
            "model": "claude-3-opus-20240229"
        }
        agent = LLMGenerator(config=config)

        assert agent.llm_provider == "anthropic"
        assert agent.model == "claude-3-opus-20240229"

    def test_initialization_with_openai_config(self):
        """Should initialize with OpenAI config."""
        config = {
            "llm_provider": "openai",
            "model": "gpt-4-turbo-preview"
        }
        agent = LLMGenerator(config=config)

        assert agent.llm_provider == "openai"
        assert agent.model == "gpt-4-turbo-preview"

    def test_initialization_with_ollama_config(self):
        """Should initialize with Ollama config."""
        config = {
            "llm_provider": "ollama",
            "model": "llama3.1:8b"
        }
        agent = LLMGenerator(config=config)

        assert agent.llm_provider == "ollama"
        assert agent.model == "llama3.1:8b"

    def test_initialization_with_huggingface_config(self):
        """Should initialize with Hugging Face config."""
        config = {
            "llm_provider": "huggingface",
            "model": "TinyLlama-1.1B-dpo"
        }
        agent = LLMGenerator(config=config)

        assert agent.llm_provider == "huggingface"
        assert agent.model == "TinyLlama-1.1B-dpo"

    def test_initialization_with_ollama_custom_url(self):
        """Should initialize with Ollama custom base URL."""
        config = {
            "llm_provider": "ollama",
            "model": "deepseek-coder-v2",
            "ollama_base_url": "http://192.168.1.100:11434"
        }
        agent = LLMGenerator(config=config)

        assert agent.llm_provider == "ollama"
        assert agent.get_config("ollama_base_url") == "http://192.168.1.100:11434"

    def test_initialization_with_empty_config(self):
        """Should initialize with empty config (use defaults)."""
        agent = LLMGenerator(config={})

        assert agent.llm_provider == "anthropic"
        assert agent.model == "claude-sonnet-4-5-20250929"


# 2. Input Validation Tests
class TestInputValidation:
    """Test input validation for different providers."""

    def test_validate_valid_input_anthropic(self, sample_input_data):
        """Should accept valid input for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            config = {"llm_provider": "anthropic"}
            agent = LLMGenerator(config=config)

            errors = agent.validate_input(sample_input_data)

            assert errors == []

    def test_validate_valid_input_openai(self, sample_input_data):
        """Should accept valid input for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            config = {"llm_provider": "openai"}
            agent = LLMGenerator(config=config)

            errors = agent.validate_input(sample_input_data)

            assert errors == []

    def test_validate_valid_input_ollama(self, sample_input_data):
        """Should accept valid input for Ollama (no API key needed)."""
        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_valid_input_huggingface(self, sample_input_data):
        """Should accept valid input for Hugging Face pipelines."""
        config = {"llm_provider": "huggingface", "model": "TinyLlama-1.1B-dpo"}
        agent = LLMGenerator(config=config)

        errors = agent.validate_input(sample_input_data)

        assert errors == []

    def test_validate_missing_test_plans(self):
        """Should reject input without test_plans."""
        agent = LLMGenerator()
        input_data = {"project_path": "/path/to/project"}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("test_plans" in err.lower() for err in errors)

    def test_validate_missing_project_path(self, sample_test_plan):
        """Should reject input without project_path."""
        agent = LLMGenerator()
        input_data = {"test_plans": [sample_test_plan]}

        errors = agent.validate_input(input_data)

        assert len(errors) > 0
        assert any("project_path" in err.lower() for err in errors)

    def test_validate_missing_anthropic_api_key(self, sample_input_data):
        """Should reject Anthropic without API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = {"llm_provider": "anthropic"}
            agent = LLMGenerator(config=config)

            errors = agent.validate_input(sample_input_data)

            assert len(errors) > 0
            assert any("anthropic_api_key" in err.lower() for err in errors)

    def test_validate_missing_openai_api_key(self, sample_input_data):
        """Should reject OpenAI without API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = {"llm_provider": "openai"}
            agent = LLMGenerator(config=config)

            errors = agent.validate_input(sample_input_data)

            assert len(errors) > 0
            assert any("openai_api_key" in err.lower() for err in errors)

    def test_validate_missing_model_huggingface(self, sample_input_data):
        """Should reject Hugging Face provider without model path."""
        config = {"llm_provider": "huggingface"}
        agent = LLMGenerator(config=config)

        errors = agent.validate_input(sample_input_data)

        assert len(errors) > 0
        assert any("hugging face" in err.lower() for err in errors)

    def test_validate_ollama_no_api_key_required(self, sample_input_data):
        """Should accept Ollama without API key (local model)."""
        with patch.dict(os.environ, {}, clear=True):
            config = {"llm_provider": "ollama"}
            agent = LLMGenerator(config=config)

            errors = agent.validate_input(sample_input_data)

            assert errors == []


# 3. Ollama Call Tests
class TestOllamaCall:
    """Test _call_ollama() method with mocking."""

    @patch('requests.post')
    def test_call_ollama_success(self, mock_post):
        """Should successfully call Ollama and return generated code."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "```python\ndef test_example():\n    assert True\n```"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama", "model": "llama3.1:8b"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert "def test_example():" in result
        assert "assert True" in result
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_call_ollama_with_custom_url(self, mock_post):
        """Should call Ollama with custom base URL."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "test code"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {
            "llm_provider": "ollama",
            "model": "llama3.1:8b",
            "ollama_base_url": "http://custom-host:11434"
        }
        agent = LLMGenerator(config=config)

        agent._call_ollama("Generate test")

        call_args = mock_post.call_args
        assert "http://custom-host:11434/api/generate" in call_args[0][0]

    @patch('requests.post')
    def test_call_ollama_with_default_url(self, mock_post):
        """Should call Ollama with default localhost URL."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "test code"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama", "model": "llama3.1:8b"}
        agent = LLMGenerator(config=config)

        agent._call_ollama("Generate test")

        call_args = mock_post.call_args
        assert "http://localhost:11434/api/generate" in call_args[0][0]

    @patch('requests.post')
    def test_call_ollama_with_default_model(self, mock_post):
        """Should use default model when not specified."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "test code"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)
        agent.model = None

        agent._call_ollama("Generate test")

        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        assert request_data["model"] == "llama3.1:8b"

    @patch('requests.post')
    def test_call_ollama_request_parameters(self, mock_post):
        """Should send correct request parameters to Ollama."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "test code"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama", "model": "llama3.1:8b"}
        agent = LLMGenerator(config=config)

        agent._call_ollama("Test prompt")

        call_args = mock_post.call_args
        request_data = call_args[1]["json"]

        assert request_data["model"] == "llama3.1:8b"
        assert request_data["prompt"] == "Test prompt"
        assert request_data["stream"] is False
        assert request_data["options"]["temperature"] == 0.3
        assert request_data["options"]["num_predict"] == 4096

    @patch('requests.post')
    def test_call_ollama_timeout_parameter(self, mock_post):
        """Should use 120 second timeout for Ollama calls."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "test code"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        agent._call_ollama("Generate test")

        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 120

    @patch('requests.post')
    def test_call_ollama_extracts_python_code(self, mock_post):
        """Should extract Python code from markdown blocks."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Here is the test:\n```python\ndef test_func():\n    pass\n```\nDone!"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == "def test_func():\n    pass"

    @patch('requests.post')
    def test_call_ollama_extracts_generic_code_blocks(self, mock_post):
        """Should extract code from generic markdown blocks."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "```\ndef test_func():\n    pass\n```"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == "def test_func():\n    pass"

    @patch('requests.post')
    def test_call_ollama_returns_plain_text(self, mock_post):
        """Should return plain text when no code blocks present."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "def test_func():\n    pass"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == "def test_func():\n    pass"


# 4. Ollama Error Handling Tests
class TestOllamaErrorHandling:
    """Test error handling for Ollama calls."""

    @patch('requests.post')
    def test_call_ollama_connection_error(self, mock_post):
        """Should handle connection errors gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""

    @patch('requests.post')
    def test_call_ollama_timeout_error(self, mock_post):
        """Should handle timeout errors gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""

    @patch('requests.post')
    def test_call_ollama_http_error(self, mock_post):
        """Should handle HTTP errors gracefully."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Error")
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""

    @patch('requests.post')
    def test_call_ollama_invalid_json_response(self, mock_post):
        """Should handle invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""

    @patch('requests.post')
    def test_call_ollama_missing_response_field(self, mock_post):
        """Should handle missing 'response' field in JSON."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Model not found"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""


# 5. Hugging Face Pipeline Tests
class TestHuggingFacePipeline:
    """Tests for Hugging Face provider integration."""

    def _build_fake_transformers(self, response_builder):
        """Create a fake transformers module returning controlled responses."""
        fake_module = ModuleType("transformers")
        fake_generator = MagicMock(side_effect=lambda prompt, **kwargs: [
            {"generated_text": response_builder(prompt, kwargs)}
        ])
        fake_pipeline = MagicMock(return_value=fake_generator)
        fake_module.pipeline = fake_pipeline
        return fake_module, fake_pipeline, fake_generator

    def test_call_huggingface_extracts_code_block(self):
        """Should extract python code blocks from Hugging Face responses."""
        config = {"llm_provider": "huggingface", "model": "TinyLlama"}
        agent = LLMGenerator(config=config)

        fake_module, fake_pipeline, fake_generator = self._build_fake_transformers(
            lambda prompt, _: f"{prompt}\n```python\nprint('hola')\n```"
        )

        with patch.dict(sys.modules, {"transformers": fake_module}):
            result = agent._call_huggingface("Prompt base")

        assert result == "print('hola')"
        fake_pipeline.assert_called_once()
        fake_generator.assert_called_once()

    def test_call_huggingface_returns_plain_text(self):
        """Should return trimmed plain text when no code block is present."""
        config = {"llm_provider": "huggingface", "model": "TinyLlama"}
        agent = LLMGenerator(config=config)

        fake_module, fake_pipeline, fake_generator = self._build_fake_transformers(
            lambda prompt, _: f"{prompt}\nGenerated tests"
        )

        with patch.dict(sys.modules, {"transformers": fake_module}):
            result = agent._call_huggingface("Prompt base")

        assert result == "Generated tests"
        fake_pipeline.assert_called_once()
        fake_generator.assert_called_once()

    def test_call_huggingface_pipeline_error(self):
        """Should return empty string when pipeline raises an error."""
        config = {"llm_provider": "huggingface", "model": "TinyLlama"}
        agent = LLMGenerator(config=config)

        fake_module = ModuleType("transformers")
        fake_pipeline = MagicMock(side_effect=RuntimeError("load error"))
        fake_module.pipeline = fake_pipeline

        with patch.dict(sys.modules, {"transformers": fake_module}):
            result = agent._call_huggingface("Prompt base")

        assert result == ""
        fake_pipeline.assert_called_once()

    def test_call_huggingface_reuses_cached_pipeline(self):
        """Should cache the pipeline between calls for performance."""
        config = {"llm_provider": "huggingface", "model": "TinyLlama"}
        agent = LLMGenerator(config=config)

        fake_module, fake_pipeline, fake_generator = self._build_fake_transformers(
            lambda prompt, _: f"{prompt} -> result"
        )

        with patch.dict(sys.modules, {"transformers": fake_module}):
            agent._call_huggingface("Prompt 1")
            agent._call_huggingface("Prompt 2")

        fake_pipeline.assert_called_once()
        assert fake_generator.call_count == 2


# 6. LLM Routing Tests
class TestLLMRouting:
    """Test _call_llm() routing to correct provider."""

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_anthropic')
    def test_call_llm_routes_to_anthropic(self, mock_anthropic):
        """Should route to Anthropic when provider is anthropic."""
        mock_anthropic.return_value = "generated code"

        config = {"llm_provider": "anthropic"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        mock_anthropic.assert_called_once_with("Test prompt")
        assert result == "generated code"

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_openai')
    def test_call_llm_routes_to_openai(self, mock_openai):
        """Should route to OpenAI when provider is openai."""
        mock_openai.return_value = "generated code"

        config = {"llm_provider": "openai"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        mock_openai.assert_called_once_with("Test prompt")
        assert result == "generated code"

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_call_llm_routes_to_ollama(self, mock_ollama):
        """Should route to Ollama when provider is ollama."""
        mock_ollama.return_value = "generated code"

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        mock_ollama.assert_called_once_with("Test prompt")
        assert result == "generated code"

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_huggingface')
    def test_call_llm_routes_to_huggingface(self, mock_hf):
        """Should route to Hugging Face when provider is huggingface."""
        mock_hf.return_value = "generated code"

        config = {"llm_provider": "huggingface", "model": "TinyLlama"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        mock_hf.assert_called_once_with("Test prompt")
        assert result == "generated code"

    def test_call_llm_unsupported_provider(self):
        """Should return empty string for unsupported provider."""
        config = {"llm_provider": "unsupported"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        assert result == ""

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_call_llm_handles_ollama_exception(self, mock_ollama):
        """Should handle exceptions from Ollama gracefully."""
        mock_ollama.side_effect = Exception("Ollama error")

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_llm("Test prompt")

        assert result == ""


# 6. Full Pipeline Tests with Ollama
class TestFullPipelineWithOllama:
    """Test full pipeline with Ollama provider."""

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_run_with_ollama_success(self, mock_ollama, sample_input_data, sample_generated_code):
        """Should run full pipeline with Ollama successfully."""
        mock_ollama.return_value = sample_generated_code

        config = {"llm_provider": "ollama", "model": "llama3.1:8b"}
        agent = LLMGenerator(config=config)

        result = agent.run(sample_input_data)

        assert result["total_generated"] == 1
        assert result["llm_provider"] == "ollama"
        assert result["model"] == "llama3.1:8b"
        assert len(result["generated_tests"]) == 1

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_run_with_ollama_multiple_test_plans(self, mock_ollama, tmp_path, sample_generated_code):
        """Should handle multiple test plans with Ollama."""
        mock_ollama.return_value = sample_generated_code

        # Create multiple source files
        for i in range(3):
            source_file = tmp_path / "scripts" / f"module{i}.py"
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_text(f"def func{i}(): pass")

        input_data = {
            "test_plans": [
                {
                    "source_file": f"scripts/module{i}.py",
                    "test_file": f"tests/test_module{i}.py",
                    "test_cases": [{"name": "test", "description": "test"}]
                }
                for i in range(3)
            ],
            "project_path": str(tmp_path)
        }

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent.run(input_data)

        assert result["total_generated"] == 3
        assert mock_ollama.call_count == 3

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_run_with_ollama_partial_failure(self, mock_ollama, tmp_path, sample_generated_code):
        """Should continue on partial failures with Ollama."""
        # First call succeeds, second fails, third succeeds
        mock_ollama.side_effect = [sample_generated_code, "", sample_generated_code]

        # Create multiple source files
        for i in range(3):
            source_file = tmp_path / "scripts" / f"module{i}.py"
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_text(f"def func{i}(): pass")

        input_data = {
            "test_plans": [
                {
                    "source_file": f"scripts/module{i}.py",
                    "test_file": f"tests/test_module{i}.py",
                    "test_cases": [{"name": "test", "description": "test"}]
                }
                for i in range(3)
            ],
            "project_path": str(tmp_path)
        }

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent.run(input_data)

        assert result["total_generated"] == 2  # Only 2 succeeded


# 7. Response Parsing Tests
class TestResponseParsing:
    """Test response parsing from different providers."""

    @patch('requests.post')
    def test_ollama_response_with_explanations(self, mock_post):
        """Should extract only code from response with explanations."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": """Here are the tests you requested:

```python
def test_example():
    assert True
```

These tests cover all the requirements."""
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert "def test_example():" in result
        assert "Here are the tests" not in result
        assert "These tests cover" not in result


# 8. Provider Comparison Tests
class TestProviderComparison:
    """Test consistency across all three providers."""

    def test_all_providers_support_same_interface(self):
        """All providers should support the same interface."""
        configs = [
            {"llm_provider": "anthropic"},
            {"llm_provider": "openai"},
            {"llm_provider": "ollama"}
        ]

        for config in configs:
            agent = LLMGenerator(config=config)
            assert hasattr(agent, '_call_llm')
            assert hasattr(agent, 'llm_provider')
            assert hasattr(agent, 'model')

    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_anthropic')
    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_openai')
    @patch('scripts.ai.generators.llm_generator.LLMGenerator._call_ollama')
    def test_all_providers_extract_code_blocks(self, mock_ollama, mock_openai, mock_anthropic):
        """All providers should extract code blocks consistently."""
        # All should return the same processed code
        expected_code = "def test_func(): pass"

        mock_anthropic.return_value = expected_code
        mock_openai.return_value = expected_code
        mock_ollama.return_value = expected_code

        for provider in ["anthropic", "openai", "ollama"]:
            config = {"llm_provider": provider}
            agent = LLMGenerator(config=config)
            result = agent._call_llm("Generate test")
            assert result == expected_code


# 9. Guardrails Tests with Ollama
class TestGuardrailsWithOllama:
    """Test guardrails work with Ollama-generated code."""

    def test_guardrails_accept_valid_ollama_code(self):
        """Should accept valid code from Ollama."""
        agent = LLMGenerator()

        output_data = {
            "generated_tests": [
                {
                    "test_file": "test_module.py",
                    "generated_code": "def test_example():\n    assert True"
                }
            ]
        }

        errors = agent.apply_guardrails(output_data)

        assert len(errors) == 0

    def test_guardrails_reject_dangerous_ollama_code(self):
        """Should reject dangerous patterns in Ollama code."""
        agent = LLMGenerator()

        output_data = {
            "generated_tests": [
                {
                    "test_file": "test_module.py",
                    "generated_code": "def test_example():\n    eval('malicious code')"
                }
            ]
        }

        errors = agent.apply_guardrails(output_data)

        assert len(errors) > 0
        assert any("eval()" in err for err in errors)


# 10. Edge Cases and Integration Tests
class TestEdgeCasesOllama:
    """Test edge cases specific to Ollama."""

    @patch('requests.post')
    def test_ollama_empty_response(self, mock_post):
        """Should handle empty response from Ollama."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": ""}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert result == ""

    @patch('requests.post')
    def test_ollama_very_long_response(self, mock_post):
        """Should handle very long responses from Ollama."""
        long_code = "def test_func():\n    pass\n" * 1000
        mock_response = Mock()
        mock_response.json.return_value = {"response": f"```python\n{long_code}\n```"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        config = {"llm_provider": "ollama"}
        agent = LLMGenerator(config=config)

        result = agent._call_ollama("Generate test")

        assert "def test_func():" in result
        assert len(result) > 0

    def test_ollama_model_variations(self):
        """Should support different Ollama models."""
        models = [
            "llama3.1:8b",
            "llama3.1:70b",
            "deepseek-coder-v2",
            "qwen2.5-coder:32b",
            "codellama:13b"
        ]

        for model in models:
            config = {"llm_provider": "ollama", "model": model}
            agent = LLMGenerator(config=config)
            assert agent.model == model


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
