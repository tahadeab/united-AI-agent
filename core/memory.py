"""Conversation memory with bounded history."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class Memory:
    def __init__(self, max_messages: int = 40):
        if max_messages < 2:
            raise ValueError("max_messages must be at least 2")
        self.max_messages = max_messages
        self.history: list[dict[str, Any]] = []

    def add_message(self, role: str, content: Any, **metadata: Any) -> None:
        message: dict[str, Any] = {"role": role, "content": content}
        message.update(metadata)
        self.history.append(message)
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages :]

    def add_message_dict(self, message: dict[str, Any]) -> None:
        self.history.append(deepcopy(message))
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages :]

    def get_history(self) -> list[dict[str, Any]]:
        return deepcopy(self.history)

    def clear(self) -> None:
        self.history.clear()
