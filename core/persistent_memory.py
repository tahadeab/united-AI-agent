"""SQLite-backed conversation memory and lightweight lexical RAG."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


_TOKEN_RE = re.compile(r"[\w']+", re.UNICODE)


class PersistentMemory:
    def __init__(self, db_path: str = "data/united_memory.db") -> None:
        self.db_path = Path(db_path).expanduser()
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self._connection.commit()

    def add_message(self, role: str, content: str) -> None:
        self._connection.execute(
            "INSERT INTO messages(role, content, created_at) VALUES (?, ?, ?)",
            (role, content, datetime.now(timezone.utc).isoformat()),
        )
        self._connection.commit()

    def recent_messages(self, limit: int = 20) -> list[dict[str, str]]:
        rows = self._connection.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def add_document(self, source: str, content: str) -> int:
        if not source or not content.strip():
            raise ValueError("source and content are required")
        cursor = self._connection.execute(
            "INSERT INTO documents(source, content, created_at) VALUES (?, ?, ?)",
            (source, content, datetime.now(timezone.utc).isoformat()),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, str | float]]:
        query_tokens = set(_TOKEN_RE.findall(query.lower()))
        if not query_tokens:
            return []
        rows = self._connection.execute(
            "SELECT id, source, content FROM documents ORDER BY id DESC"
        ).fetchall()
        scored: list[dict[str, str | float]] = []
        for row in rows:
            tokens = set(_TOKEN_RE.findall(row["content"].lower()))
            overlap = len(query_tokens & tokens)
            if overlap:
                score = overlap / max(1, len(query_tokens))
                scored.append({"source": row["source"], "content": row["content"], "score": score})
        scored.sort(key=lambda item: float(item["score"]), reverse=True)
        return scored[: max(1, min(top_k, 10))]

    def clear(self) -> None:
        self._connection.execute("DELETE FROM messages")
        self._connection.execute("DELETE FROM documents")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
