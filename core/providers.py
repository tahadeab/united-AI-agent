"""Provider-agnostic model gateway.

LiteLLM gives the agent one stable interface for OpenAI, Anthropic, Google,
Azure, AWS Bedrock, Mistral, Groq, DeepSeek, OpenRouter, local servers, and
other supported providers. Custom OpenAI-compatible endpoints can be used via
AI_PROVIDER=openai and AI_API_BASE.
"""

from __future__ import annotations

from typing import Any

from .config import Settings


class ProviderError(RuntimeError):
    """A normalized provider failure with an actionable message."""


class ModelGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            import litellm
        except ImportError as exc:  # pragma: no cover - exercised in bad installs
            raise ProviderError(
                "The 'litellm' package is missing. Install dependencies with "
                "'pip install -r requirements.txt'."
            ) from exc
        self._litellm = litellm
        self._litellm.drop_params = True

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.settings.completion_model(),
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }
        if self.settings.api_key:
            kwargs["api_key"] = self.settings.api_key
        if self.settings.api_base:
            kwargs["api_base"] = self.settings.api_base
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        try:
            return self._litellm.completion(**kwargs)
        except Exception as exc:
            provider = self.settings.provider
            raise ProviderError(
                f"{provider} request failed for {self.settings.model}: {exc}"
            ) from exc
