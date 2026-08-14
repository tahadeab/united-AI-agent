"""Built-in tools exposed to the model."""

from __future__ import annotations

import ast
import operator
from datetime import datetime, timezone
from typing import Any, Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}
        self.register(
            name="calculator",
            description="Evaluate a basic arithmetic expression safely.",
            parameters={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
                "additionalProperties": False,
            },
            handler=self._calculator,
        )
        self.register(
            name="current_time",
            description="Return the current UTC time in ISO 8601 format.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda: datetime.now(timezone.utc).isoformat(),
        )

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        if not name or name in self._handlers:
            raise ValueError(f"Invalid or duplicate tool name: {name}")
        self._handlers[name] = handler
        self._schemas[name] = {
            "type": "function",
            "function": {"name": name, "description": description, "parameters": parameters},
        }

    def schemas(self) -> list[dict[str, Any]]:
        return list(self._schemas.values())

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        if name not in self._handlers:
            return f"Tool '{name}' is not registered."
        try:
            return str(self._handlers[name](**arguments))
        except Exception as exc:
            return f"Tool '{name}' failed: {exc}"

    @staticmethod
    def _calculator(expression: str) -> float | int:
        tree = ast.parse(expression, mode="eval")
        allowed = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def evaluate(node: ast.AST) -> float | int:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
                return allowed[type(node.op)](evaluate(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                return allowed[type(node.op)](evaluate(node.left), evaluate(node.right))
            raise ValueError("Only numeric arithmetic is allowed")

        result = evaluate(tree)
        if abs(result) > 10**12:
            raise ValueError("Result is outside the safe limit")
        return result
