"""Tests for the LLM client factory supporting OpenAI and Claude."""

from __future__ import annotations


def test_create_llm_client_defaults_to_openai(monkeypatch) -> None:
    from infrastructure.workspace.hamilton_llm.llm_client import create_llm_client

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    client = create_llm_client(response_catalog={"__default__": "OpenAI says hi"})

    assert client.model_id == "gpt-4o-mini"
    assert "OpenAI" in client.complete("Hello")


def test_create_llm_client_requires_api_key(monkeypatch) -> None:
    from infrastructure.workspace.hamilton_llm.llm_client import create_llm_client

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    try:
        create_llm_client()
    except RuntimeError as exc:  # pragma: no branch - explicit expectation
        assert "OPENAI_API_KEY" in str(exc)
    else:  # pragma: no cover - should not succeed
        raise AssertionError("Expected a RuntimeError when API key missing")
