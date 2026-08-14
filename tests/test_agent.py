from types import SimpleNamespace

from core.agent import UnitedAgent
from core.config import Settings
from core.memory import Memory
from core.tools import ToolRegistry


class FakeGateway:
    def __init__(self):
        self.calls = 0

    def complete(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            call = SimpleNamespace(
                id="call-1",
                function=SimpleNamespace(name="calculator", arguments='{"expression":"2 + 3"}'),
            )
            message = SimpleNamespace(content=None, tool_calls=[call])
        else:
            message = SimpleNamespace(content="The result is 5.", tool_calls=[])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_memory_is_bounded_and_returns_copies():
    memory = Memory(max_messages=2)
    memory.add_message("user", "one")
    memory.add_message("assistant", "two")
    memory.add_message("user", "three")
    history = memory.get_history()
    assert [item["content"] for item in history] == ["two", "three"]
    history[0]["content"] = "changed"
    assert memory.get_history()[0]["content"] == "two"


def test_calculator_rejects_code():
    tools = ToolRegistry()
    result = tools.execute("calculator", {"expression": "__import__('os').getcwd()"})
    assert "failed" in result.lower()


def test_agent_executes_tool_and_returns_final_answer():
    settings = Settings(max_tool_rounds=2, max_history_messages=10)
    gateway = FakeGateway()
    agent = UnitedAgent(settings=settings, gateway=gateway)
    assert agent.chat("What is 2 + 3?") == "The result is 5."
    assert gateway.calls == 2
    assert agent.memory.get_history()[-1]["content"] == "The result is 5."
