"""Safe local file reading for explicit agent requests."""

from __future__ import annotations

import os
from pathlib import Path


TEXT_EXTENSIONS = {
    ".c", ".cfg", ".conf", ".cpp", ".css", ".csv", ".env", ".go", ".html",
    ".ini", ".java", ".js", ".json", ".jsx", ".md", ".py", ".rb", ".rs",
    ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}


def _allowed_root() -> Path:
    return Path(os.getenv("AGENT_FILE_ROOT", os.getcwd())).expanduser().resolve()


def read_local_file(path: str, max_chars: int = 20_000) -> str:
    """Read a UTF-8 text file only when it stays inside AGENT_FILE_ROOT."""
    if not path or not path.strip():
        raise ValueError("path must not be empty")
    max_chars = max(1_000, min(max_chars, 100_000))
    root = _allowed_root()
    candidate = (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PermissionError("File access is restricted to AGENT_FILE_ROOT") from exc
    if not candidate.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if candidate.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported or potentially binary file type: {candidate.suffix or '<none>'}")
    if candidate.stat().st_size > 2_000_000:
        raise ValueError("File is too large; maximum supported size is 2 MB")
    content = candidate.read_text(encoding="utf-8", errors="strict")
    if len(content) > max_chars:
        return content[:max_chars] + f"\n\n[Output truncated at {max_chars} characters.]"
    return content
