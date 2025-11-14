"""Tests for the Hamilton-style LLM dataflow example located in the workspace tree."""

import pytest

from infrastructure.workspace.hamilton_llm import dataflow
from infrastructure.workspace.hamilton_llm import driver as mini_driver
from infrastructure.workspace.hamilton_llm.driver import MissingDependencyError
from infrastructure.workspace.hamilton_llm.llm_client import MockLLMClient


@pytest.fixture()
def hamilton_driver():
    return (
        mini_driver.Builder()
        .with_modules(dataflow)
        .with_config({"pricing_policy": {"price_per_1k_tokens": 0.4, "safety_multiplier": 1.15}})
        .with_adapters(mini_driver.DictResult())
        .build()
    )


def test_pace_of_development_metadata_matches_expected_sequence():
    """Validate that the module exposes the canonical pacing differences described in the slides."""
    assert dataflow.PACE_OF_DEVELOPMENT["traditional_ml"] == [
        "Idea & Data/Resources",
        "Design",
        "Development/Prototype",
        "Model Development",
        "Getting to Production",
        "Operations",
        "Maintenance & Business Value",
    ]
    assert dataflow.PACE_OF_DEVELOPMENT["llm_apps"] == [
        "Idea & Data/Resources",
        "Design",
        "Development/Prototype",
        "Prompt / Model Development",
        "Getting to Production",
        "Operations",
        "Maintenance & Business Value",
    ]


def test_hamilton_builder_executes_llm_business_flow(hamilton_driver):
    """End-to-end execution should transform data into a business value package and cost estimate."""
    mock_client = MockLLMClient(
        price_per_1k_tokens=0.4,
        response_catalog={
            "Data → Prompt → LLM → $": "Use Hamilton declarative functions to keep prompts versioned and guarded against injection.",
        },
    )

    inputs = {
        "idea": "AI copilots for compliance analysts",
        "domain_data": {
            "data": "archived compliance tickets",
            "ui": "browser extension",
            "business_process": "regulatory audit",
        },
        "edge_cases": [
            "Input state space",
            "Guard against prompt injection",
            "Domain expertise",
            "Evaluation",
            "Cost/GPUs",
        ],
        "llm_client": mock_client,
    }

    result = hamilton_driver.execute(["business_value", "cost_estimate"], inputs)

    assert result["business_value"]["llm_plan"].startswith("Use Hamilton declarative functions")
    assert result["business_value"]["next_step"] == "Prototype with guarded prompts"
    assert pytest.approx(result["cost_estimate"], rel=1e-3) == 0.0552

    executed = hamilton_driver.execution_log
    assert executed[-1] == "cost_estimate"
    assert "llm_response" in executed
    assert executed.index("business_value") < executed.index("cost_estimate")


def test_driver_reports_missing_inputs():
    driver = mini_driver.Builder().with_modules(dataflow).build()
    mock_client = MockLLMClient(price_per_1k_tokens=0.5, response_catalog={})

    with pytest.raises(MissingDependencyError) as exc:
        driver.execute(
            ["cost_estimate"],
            {
                "idea": "Guardrails demo",
                "domain_data": {"data": "logs", "ui": "cli", "business_process": "ops"},
                "edge_cases": ["Injection"],
                "llm_client": mock_client,
            },
        )

    assert "pricing_policy" in str(exc.value)


def test_builder_requires_modules_before_building():
    with pytest.raises(ValueError) as exc:
        mini_driver.Builder().build()

    assert "modules" in str(exc.value).lower()


def test_custom_adapter_transforms_execution_result():
    class KeysAdapter:
        def __call__(self, results):
            return tuple(sorted(results))

    driver = (
        mini_driver.Builder()
        .with_modules(dataflow)
        .with_adapters(KeysAdapter())
        .build()
    )

    assert driver.execute(["pace_of_development"], {}) == ("pace_of_development",)
