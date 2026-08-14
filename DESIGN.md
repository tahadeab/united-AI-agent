# United AI Agent — Design

## Goals

United is designed as a small, dependable agent core rather than a provider-specific chatbot. The architecture separates configuration, model transport, memory, orchestration, and tools so each concern can evolve independently.

## Runtime architecture

1. `Settings` loads runtime options from environment variables.
2. `ModelGateway` converts generic settings and messages into a provider-neutral completion request through LiteLLM.
3. `UnitedAgent` maintains the system prompt and bounded conversation context, then runs the response/tool-call loop.
4. `ToolRegistry` publishes JSON Schemas and executes only explicitly registered handlers.
5. `main.py` provides a minimal interactive CLI; other interfaces can reuse `UnitedAgent` without importing the CLI.

## Provider strategy

The project does not hard-code a separate SDK for every provider. LiteLLM provides a stable compatibility layer for a broad range of cloud and local providers. Provider-specific credentials remain in environment variables, while the agent only depends on the normalized completion response. A provider prefix in the model name is preserved to support advanced configurations.

## Tool safety

Tools are opt-in and schema-driven. Each tool must have a unique name, a JSON Schema, and a callable handler. Tool arguments are parsed as JSON and failures are returned as ordinary tool results so the model can recover. Tools that access the filesystem, network, credentials, or external systems must add authorization, timeouts, input validation, and audit logging before production use.

## Memory strategy

`Memory` retains only the most recent configured number of messages. It returns deep copies so callers cannot mutate internal state accidentally. A future persistent-memory implementation can satisfy the same interface while storing encrypted records in SQLite or another database.

## Reliability and operations

The orchestration loop has a configurable maximum number of tool rounds. Provider failures are normalized into `ProviderError`, while the CLI keeps the session alive. Production deployments should add retries with exponential backoff, request timeouts, rate limits, secret redaction, structured logs, and metrics around provider latency and token usage.

## Extension points

A web API, streaming output, persistent memory, retrieval, or additional tools can be added around the existing core without rewriting provider integration. New provider support is generally a configuration change when the provider is supported by LiteLLM; otherwise a dedicated gateway implementation can be introduced behind the same `complete()` interface.
