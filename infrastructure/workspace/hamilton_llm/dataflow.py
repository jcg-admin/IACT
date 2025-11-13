"""Declarative dataflow modeling the Data → Prompt → LLM → $ pipeline.

The module captures the pace differences between aplicaciones ML tradicionales y
aplicaciones LLM, destacando que ambas requieren habilidades fuertes de
ingeniería de software. Cada función sigue el paradigma Hamilton: el nombre es
el output y los argumentos son las dependencias explícitas.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .llm_client import MockLLMClient

PACE_OF_DEVELOPMENT: Dict[str, List[str]] = {
    "traditional_ml": [
        "Idea & Data/Resources",
        "Design",
        "Development/Prototype",
        "Model Development",
        "Getting to Production",
        "Operations",
        "Maintenance & Business Value",
    ],
    "llm_apps": [
        "Idea & Data/Resources",
        "Design",
        "Development/Prototype",
        "Prompt / Model Development",
        "Getting to Production",
        "Operations",
        "Maintenance & Business Value",
    ],
}

DATAFLOW_LABEL = "Data → Prompt → LLM → $"


def pace_of_development() -> Dict[str, List[str]]:
    """Return the canonical ordering of fases para ML tradicional y apps LLM."""

    return PACE_OF_DEVELOPMENT


def prompt_template(
    idea: str,
    domain_data: Dict[str, str],
    pace_of_development: Dict[str, List[str]],
) -> str:
    """Create a template that contrasta los ritmos y exige prácticas SWE."""

    traditional = " → ".join(pace_of_development["traditional_ml"])
    llm = " → ".join(pace_of_development["llm_apps"])
    return (
        "You are designing a Hamilton micro-orchestration experiment.\n"
        f"Traditional ML pace: {traditional}.\n"
        f"LLM app pace: {llm}.\n"
        "Explain how strong SWE practices (testing, modularity, reuse, portability)\n"
        "keep the system resilient while iterating quickly.\n"
        f"Business domain: {domain_data['business_process']} with UI {domain_data['ui']}.\n"
        f"Primary data assets: {domain_data['data']}.\n"
        f"Goal: deliver {idea} using Hamilton declarative functions.\n"
    )


def llm_prompt(prompt_template: str, edge_cases: List[str]) -> str:
    """Combine template with guardrails against edge cases y prompt injection."""

    formatted_edge_cases = ", ".join(edge_cases)
    return (
        f"{prompt_template}"
        "Consider the following edge cases explicitly: "
        f"{formatted_edge_cases}.\n"
        "Detail the pipeline as Data → Prompt → LLM → $, highlighting how guardrails\n"
        "prevent prompt injection and balance evaluation with GPU cost awareness."
    )


def llm_response(llm_prompt: str, llm_client: MockLLMClient) -> str:
    """Obtain respuesta determinística del cliente LLM simulado."""

    return llm_client.complete(llm_prompt)


def prompt_token_estimate(llm_prompt: str, edge_cases: List[str]) -> int:
    """Estimate token count con amortiguador para cobertura de edge cases."""

    narrative_tokens = len(llm_prompt.split())
    scaled_tokens = round(narrative_tokens * 0.75)
    guardrail_tokens = len(edge_cases) * 3
    return max(scaled_tokens + guardrail_tokens, 120)


def business_value(
    llm_response: str,
    pace_of_development: Dict[str, List[str]],
) -> Dict[str, Any]:
    """Empaquetar plan de acción y el contexto de ritmo de desarrollo."""

    return {
        "llm_plan": llm_response,
        "pace": pace_of_development,
        "next_step": "Prototype with guarded prompts",
    }


def cost_estimate(
    prompt_token_estimate: int,
    pricing_policy: Dict[str, float],
) -> float:
    """Calcular costo esperado usando tarifa por 1K tokens y factor de seguridad."""

    price = pricing_policy["price_per_1k_tokens"]
    safety = pricing_policy.get("safety_multiplier", 1.0)
    return round((prompt_token_estimate / 1000) * price * safety, 6)


__all__ = [
    "PACE_OF_DEVELOPMENT",
    "DATAFLOW_LABEL",
    "pace_of_development",
    "prompt_template",
    "llm_prompt",
    "llm_response",
    "prompt_token_estimate",
    "business_value",
    "cost_estimate",
]
