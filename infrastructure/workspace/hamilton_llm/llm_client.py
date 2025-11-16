"""LLM client abstractions supporting OpenAI and Claude."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass
class BaseLLMClient:
    model_id: str
    price_per_1k_tokens: float
    _response_catalog: Mapping[str, str]
    provider_label: str

    def complete(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        for key, response in self._response_catalog.items():
            if key.lower() in lower_prompt:
                return response
        return self._response_catalog.get("__default__", f"{self.provider_label} response for: {prompt[:32]}")


class MockLLMClient(BaseLLMClient):
    """Deterministic mock client emulating an LLM completion API."""

    def __init__(self, price_per_1k_tokens: float, response_catalog: Mapping[str, str]):
        super().__init__(
            model_id="mock-llm",
            price_per_1k_tokens=price_per_1k_tokens,
            _response_catalog=dict(response_catalog),
            provider_label="Mock",
        )


def _default_catalog(label: str) -> Mapping[str, str]:
    return {"__default__": f"{label} says hi"}


def create_llm_client(*, response_catalog: Mapping[str, str] | None = None) -> BaseLLMClient:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if provider in {"claude", "anthropic"}:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY must be set when using Claude")
        catalog = dict(response_catalog or _default_catalog("Claude"))
        return BaseLLMClient(
            model_id="claude-3-haiku",
            price_per_1k_tokens=0.008,
            _response_catalog=catalog,
            provider_label="Claude",
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set for OpenAI provider")
    catalog = dict(response_catalog or _default_catalog("OpenAI"))
    return BaseLLMClient(
        model_id="gpt-4o-mini",
        price_per_1k_tokens=0.015,
        _response_catalog=catalog,
        provider_label="OpenAI",
    )


__all__ = ["BaseLLMClient", "MockLLMClient", "create_llm_client"]
