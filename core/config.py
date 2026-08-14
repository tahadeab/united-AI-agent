"""Configuration management for United AI Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    api_base: str | None = None
    temperature: float = 0.2
    max_tokens: int = 2048
    max_history_messages: int = 40
    max_tool_rounds: int = 6
    memory_db_path: str = "data/united_memory.db"
    rag_top_k: int = 4

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
        model = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
        api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("AI_API_BASE") or None
        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            api_base=api_base,
            temperature=float(os.getenv("AI_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "2048")),
            max_history_messages=int(os.getenv("AI_MAX_HISTORY_MESSAGES", "40")),
            max_tool_rounds=int(os.getenv("AI_MAX_TOOL_ROUNDS", "6")),
            memory_db_path=os.getenv("MEMORY_DB_PATH", "data/united_memory.db"),
            rag_top_k=int(os.getenv("RAG_TOP_K", "4")),
        )

    def completion_model(self) -> str:
        """Return a LiteLLM model identifier, preserving explicit prefixes."""
        if "/" in self.model:
            return self.model
        return f"{self.provider}/{self.model}"
