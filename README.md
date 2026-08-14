# United AI Agent

United is a provider-agnostic, tool-capable conversational AI agent built in Python. It provides a clean command-line experience, bounded conversation memory, safe built-in tools, and one configuration surface for many hosted and local model providers.

## Highlights

United uses a single gateway powered by [LiteLLM](https://github.com/BerriAI/litellm), so the same agent loop can work with OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, Mistral, Groq, DeepSeek, OpenRouter, Together AI, Ollama, hosted vLLM endpoints, and other providers supported by LiteLLM. Custom OpenAI-compatible services can be configured with `AI_API_BASE`.

The agent supports structured tool calling, including a safe arithmetic calculator and UTC time lookup. The tool registry is intentionally small and explicit so that new tools can be added without changing the orchestration loop. Conversation history is bounded and copied defensively to prevent accidental mutation or unbounded memory growth.

## Requirements

Python 3.11 or newer is recommended. A provider API key is required for live conversations; no key is needed to run the unit tests.

## Quick start

```bash
git clone https://github.com/tahadeab/united-AI-agent.git
cd united-AI-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set the provider and credentials. For example:

```dotenv
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
AI_API_KEY=your-api-key
```

Then run the CLI:

```bash
python main.py
```

Available commands are `/help`, `/clear`, and `/exit`.

## Provider configuration

The recommended approach is to set `AI_PROVIDER` and `AI_MODEL`. LiteLLM maps the pair to the correct provider protocol. Provider-specific credentials can be supplied using the environment variable expected by that provider, or through the generic `AI_API_KEY` variable when supported.

| Provider | Example `AI_PROVIDER` | Example `AI_MODEL` |
| --- | --- | --- |
| OpenAI | `openai` | `gpt-4o-mini` |
| Anthropic | `anthropic` | `claude-3-5-sonnet-latest` |
| Google Gemini | `gemini` | `gemini/gemini-2.0-flash` |
| Groq | `groq` | `llama-3.3-70b-versatile` |
| DeepSeek | `deepseek` | `deepseek-chat` |
| OpenRouter | `openrouter` | `openrouter/auto` |
| Ollama | `ollama` | `llama3.2` |
| Custom endpoint | `openai` | `your-model-name` |

For a custom endpoint, set `AI_API_BASE=https://your-service.example/v1`. Model identifiers that already contain a provider prefix are preserved, which allows advanced LiteLLM configurations.

## Project structure

```text
.
├── core/
│   ├── agent.py       # Agent orchestration and tool-calling loop
│   ├── config.py      # Environment-backed runtime settings
│   ├── memory.py      # Bounded conversation memory
│   ├── providers.py   # Provider-agnostic model gateway
│   ├── tools.py       # Explicit, safe tool registry
│   ├── web.py         # Public web search helper
│   └── file_tools.py  # Sandboxed local file reader
├── tests/
│   └── test_agent.py  # Offline unit tests
├── .env.example
├── main.py
└── requirements.txt
```

## Advanced tools

The agent now exposes two additional tools through the same JSON-schema tool-calling loop:

| Tool | Purpose | Safety boundary |
| --- | --- | --- |
| `web_search` | Searches the public web and returns titles, URLs, and short snippets. | Uses a timeout and returns reference data only; page content must be treated as untrusted input. |
| `read_file` | Reads UTF-8 text files for code and document analysis. | Access is restricted to `AGENT_FILE_ROOT`, text extensions, a 2 MB file size limit, and a configurable output limit. |

Set `AGENT_FILE_ROOT` in `.env` when the agent should inspect a specific workspace. Relative paths are resolved inside that directory, and path traversal outside it is rejected. The web search tool does not require an API key and uses DuckDuckGo's public HTML results endpoint.

## Testing

Run the complete offline test suite with:

```bash
pytest -q
```

The tests use a fake gateway and never send requests to a model provider.

## Security notes

Never commit `.env`, API keys, or provider credentials. The built-in calculator uses an allow-listed Python AST evaluator and does not execute arbitrary code. Production deployments should add authentication, rate limiting, structured logging with secret redaction, and a policy review for every tool that can access files, networks, or external systems.

## Extending the agent

Register a new tool through `ToolRegistry.register()` with a JSON Schema and a callable handler. The handler result is returned to the model through the standard tool message format. For production tools, validate all arguments, apply timeouts, restrict network destinations, and log failures without storing sensitive payloads.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

Developed by **taha deab**.
