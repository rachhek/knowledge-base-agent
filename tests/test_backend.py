from __future__ import annotations

import pytest

import quality_agent_demo.checks as checks


class DummyClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyProvider:
    def __init__(self, *, openai_client):
        self.openai_client = openai_client


class DummyModel:
    def __init__(self, model_name, *, provider):
        self.model_name = model_name
        self.provider = provider


class DummyAgent:
    def __init__(self, model, **kwargs):
        self.model = model
        self.kwargs = kwargs


@pytest.fixture(autouse=True)
def clear_api_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_API_VERSION", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def fake_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(checks, "AsyncAzureOpenAI", DummyClient)
    monkeypatch.setattr(checks, "AsyncOpenAI", DummyClient)
    monkeypatch.setattr(checks, "OpenAIProvider", DummyProvider)
    monkeypatch.setattr(checks, "OpenAIChatModel", DummyModel)
    monkeypatch.setattr(checks, "Agent", DummyAgent)


def test_build_agent_prefers_azure_when_both_providers_are_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "azure-key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

    agent = checks._build_agent("gpt-4.1", "system prompt", dict)

    assert agent.model.provider.openai_client.kwargs == {
        "azure_endpoint": "https://example.openai.azure.com",
        "api_key": "azure-key",
        "api_version": "2025-01-01-preview",
    }


def test_build_agent_uses_openai_when_azure_is_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

    agent = checks._build_agent("gpt-4.1-mini", "system prompt", dict)

    assert agent.model.model_name == "gpt-4.1-mini"
    assert agent.model.provider.openai_client.kwargs == {"api_key": "openai-key"}


def test_build_agent_requires_credentials() -> None:
    with pytest.raises(EnvironmentError, match="No API credentials found"):
        checks._build_agent("gpt-4.1", "system prompt", dict)
