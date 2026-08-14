"""Restricted Python execution for calculations and small scripts.

This is a defense-in-depth helper, not a hardened multi-tenant sandbox. Run it
only for trusted users and isolate the whole application further in production.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path


BLOCKED_NAMES = {
    "__import__", "eval", "exec", "compile", "open", "input", "breakpoint",
    "getattr", "setattr", "delattr", "globals", "locals", "vars",
}
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib", "requests",
    "urllib", "http", "ftplib", "ctypes", "multiprocessing", "signal",
}


def _validate_script(script: str) -> None:
    if not script or not script.strip():
        raise ValueError("script must not be empty")
    if len(script) > 30_000:
        raise ValueError("script is too large; maximum is 30,000 characters")
    try:
        tree = ast.parse(script, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"Python syntax error: {exc}") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [alias.name.split(".")[0] for alias in getattr(node, "names", [])]
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module.split(".")[0])
            if any(module in BLOCKED_MODULES for module in modules):
                raise PermissionError("This script imports a blocked module")
        if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            raise PermissionError(f"Blocked operation: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr in BLOCKED_NAMES:
            raise PermissionError(f"Blocked attribute: {node.attr}")


def execute_python(script: str, timeout_seconds: int = 5) -> str:
    """Validate and execute a short Python script with bounded output/time."""
    _validate_script(script)
    timeout_seconds = max(1, min(timeout_seconds, 15))
    with tempfile.TemporaryDirectory(prefix="united-code-") as temp_dir:
        script_path = Path(temp_dir) / "script.py"
        script_path.write_text(script, encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
            "HOME": temp_dir,
        }
        try:
            result = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                cwd=temp_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return f"Execution timed out after {timeout_seconds} seconds."
        output = (result.stdout + ("\nSTDERR:\n" + result.stderr if result.stderr else "")).strip()
        output = output[:20_000]
        if result.returncode != 0:
            return f"Execution failed with exit code {result.returncode}:\n{output}"
        return output or "Script completed successfully with no output."
