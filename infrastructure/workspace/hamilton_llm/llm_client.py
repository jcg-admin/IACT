"""Deterministic mock client emulating an LLM completion API."""

from __future__ import annotations

from typing import Mapping


class MockLLMClient:
    """Return canned responses y exponer tarifa para estimar costos."""

    def __init__(self, price_per_1k_tokens: float, response_catalog: Mapping[str, str]):
        self.price_per_1k_tokens = price_per_1k_tokens
        self._response_catalog = dict(response_catalog)

    def complete(self, prompt: str) -> str:
        """Return the first response cuyo identificador esté contenido en el prompt."""

        lower_prompt = prompt.lower()
        for key, response in self._response_catalog.items():
            if key.lower() in lower_prompt:
                return response
        return self._response_catalog.get(
            "__default__",
            "Document modular functions, validate with pytest and guard against prompt injection.",
        )


__all__ = ["MockLLMClient"]
