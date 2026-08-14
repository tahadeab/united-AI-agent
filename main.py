"""Command-line interface for United AI Agent."""

from __future__ import annotations

from core.agent import UnitedAgent
from core.providers import ProviderError


HELP_TEXT = """Commands:
  /help   Show this help message
  /clear  Clear conversation memory
  /exit   Exit the application
"""


def main() -> None:
    agent = UnitedAgent()
    print("United AI Agent")
    print("Ask anything in English, or type /help for commands. Type /exit to quit.")

    while True:
        try:
            user_input = input("You: ").strip()
            command = user_input.lower()
            if command in {"/exit", "exit", "quit"}:
                print("United: Goodbye!")
                return
            if command == "/help":
                print(HELP_TEXT)
                continue
            if command == "/clear":
                agent.clear_memory()
                print("United: Conversation memory cleared.")
                continue
            if not user_input:
                continue

            print(f"United: {agent.chat(user_input)}")
        except KeyboardInterrupt:
            print("\nUnited: Session ended. Goodbye!")
            return
        except EOFError:
            print("\nUnited: Goodbye!")
            return
        except (ProviderError, ValueError) as exc:
            print(f"United: {exc}")
        except Exception as exc:  # Keep the CLI alive while exposing a useful diagnostic.
            print(f"United: Unexpected error: {exc}")


if __name__ == "__main__":
    main()
