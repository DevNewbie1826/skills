# Pydantic AI Reference (v1.x)

> Read this when building typed, model-driven workflows with Pydantic AI.

Source: [Pydantic AI documentation](https://ai.pydantic.dev). These patterns cover production use of the package's typed workflow API. In every snippet, `model` is supplied by application configuration at the deployment boundary; keep provider identifiers and credentials out of domain logic.

---

## 1. Workflow constructor

```python
from pydantic_ai import Agent
from pydantic_ai.models import Model


def build_workflow(model: str | Model) -> Agent:
    return Agent(
        model,                         # configured model object or identifier
        output_type=MyOutputModel,     # structured output type; default=str
        instructions="Return concise, factual output.",
        system_prompt="Use the available tools when needed.",
        deps_type=MyDeps,              # dependency type for type checking only
        name="my-workflow",           # optional; inferred from variable name if omitted
        retries=1,                     # default retries for tools and output validation
        output_retries=None,           # override retries for output validation only
        tools=[my_tool],               # Tool objects or plain functions
        defer_model_check=False,       # delay configuration validation only when necessary
        end_strategy="early",         # "early" | "graceful" | "exhaustive"
    )
```

`result_type` was renamed to `output_type`; use `output_type`.

## 2. Model configuration

Resolve the model at the application configuration boundary. A string identifier is adapter-specific; many adapters use a form such as `provider:model-id`. Keep that identifier in configuration, not scattered through source files.

```python
from pydantic_ai import Agent


class Settings:
    model_id: str


def build_workflow(settings: Settings) -> Agent:
    return Agent(settings.model_id)


async def run_with_override(
    workflow: Agent,
    prompt: str,
    model_id: str,
) -> str:
    result = await workflow.run(prompt, model=model_id)
    return result.output
```

Use a test model or a fake adapter for unit tests. Exercise the configured provider adapter in integration tests only when credentials and a stable sandbox are available.

## 3. Tools

### Decorator syntax

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model


def build_greeter(model: str | Model) -> Agent:
    workflow = Agent(model, deps_type=str)

    @workflow.tool                    # receives RunContext as the first argument
    async def greet(ctx: RunContext[str], name: str) -> str:
        return f"Hello {ctx.deps}, {name}!"

    @workflow.tool_plain              # no context needed
    async def roll_dice(sides: int) -> int:
        import random
        return random.randint(1, sides)

    return workflow
```

### `RunContext[Deps]`

The first parameter of a `@workflow.tool` function carries:

- `ctx.deps`: the dependency instance.
- `ctx.model`: the configured model.
- `ctx.usage`: token usage so far.
- `ctx.messages`: conversation history.
- `ctx.retry` and `ctx.max_retries`: retry state.
- `ctx.agent`: the running workflow instance.

Use `@workflow.tool_plain` when the tool does not need this context. Keep tools narrow, typed, and independently testable.

## 4. Structured output

Pass a Pydantic `BaseModel` (or `bool`, `int`, `list[str]`, and similar types) as `output_type`. Read the result through `.output`.

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model


class City(BaseModel):
    name: str
    country: str
    population_millions: float


def describe_city(model: str | Model) -> City:
    workflow = Agent(model, output_type=City)
    result = workflow.run_sync("Describe a city with its country and population.")
    return result.output
```

`result.data` was renamed; the canonical accessor is `result.output`.

## 5. Async, sync, and streaming

| Method | Mode | Returns |
|---|---|---|
| `await workflow.run(prompt, ...)` | async | `AgentRunResult[OutputDataT]` |
| `workflow.run_sync(prompt, ...)` | sync | `AgentRunResult[OutputDataT]` |
| `async with workflow.run_stream(prompt, ...) as response:` | async streaming | `StreamedRunResult` |

```python
async def stream_response(workflow: Agent, prompt: str) -> str:
    async with workflow.run_stream(prompt) as response:
        async for text in response.stream_text():
            print(text, end="")
        return response.output
```

`run_sync()` wraps the async path. Do not call it from an active async context.

## 6. Dependencies

Use a dataclass container, pass its type to `deps_type`, and pass an instance through `deps` at run time.

```python
from dataclasses import dataclass

import httpx
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model


@dataclass(frozen=True, slots=True)
class Deps:
    api_token: str
    http_client: httpx.AsyncClient


def build_fetcher(model: str | Model) -> Agent:
    workflow = Agent(model, deps_type=Deps)

    @workflow.tool
    async def fetch_data(ctx: RunContext[Deps], endpoint: str) -> str:
        response = await ctx.deps.http_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {ctx.deps.api_token}"},
        )
        response.raise_for_status()
        return response.text

    return workflow


async def run_fetcher(model: str | Model, endpoint: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        workflow = build_fetcher(model)
        result = await workflow.run(
            f"Fetch {endpoint}",
            deps=Deps(api_token=token, http_client=client),
        )
        return result.output
```

Keep credentials in the application's secret configuration and pass only the dependency values a tool actually needs.

## 7. Error types and retrying from a tool

```python
from pydantic_ai import (
    Agent,
    ModelRetry,
    UnexpectedModelBehavior,
    capture_run_messages,
)
from pydantic_ai.models import Model


def build_volume_workflow(model: str | Model) -> Agent:
    workflow = Agent(model, retries=3)

    @workflow.tool_plain
    def calc_volume(size: int) -> int:
        if size == 42:
            return size**3
        raise ModelRetry("Retry with the required size.")

    return workflow


def inspect_failure(workflow: Agent) -> None:
    with capture_run_messages() as messages:
        try:
            workflow.run_sync("Calculate the volume for size 6.")
        except UnexpectedModelBehavior as error:
            print("Error:", error)
            print("Cause:", error.__cause__)
            print("Messages:", messages)
```

- `ModelRetry`: raise from a tool, output validator, or capability hook to request another attempt.
- `UnexpectedModelBehavior`: raised when the retry limit is exhausted or the model API returns an unrecoverable error.
- `capture_run_messages()`: records messages exchanged during a run for diagnosis.

## 8. Observability integration

If the optional `logfire` extra is installed, configure it through the project's normal settings and instrument the workflow API there:

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
```

Alternatively, set `instrument=True` when constructing the workflow:

```python
from pydantic_ai import Agent
from pydantic_ai.models import Model


def build_instrumented_workflow(model: str | Model) -> Agent:
    return Agent(model, instrument=True)
```

If that optional integration is unavailable, use the project's existing telemetry convention or leave instrumentation out and state that limitation. Do not introduce a second logging or tracing stack only for this workflow.

## 9. Minimal complete patterns

### Basic workflow with structured output

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model


class City(BaseModel):
    name: str
    country: str


def get_city(model: str | Model) -> City:
    workflow = Agent(model, output_type=City)
    result = workflow.run_sync("Provide a city and its country.")
    return result.output
```

### Workflow with tools and dependencies

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model


@dataclass(frozen=True, slots=True)
class Deps:
    secret: str


def build_secret_workflow(model: str | Model) -> Agent:
    workflow = Agent(model, deps_type=Deps)

    @workflow.tool
    async def get_secret(ctx: RunContext[Deps], code: str) -> str:
        if code == "1234":
            return f"secret-for-{ctx.deps.secret}"
        return "wrong code"

    return workflow
```

### Async streaming

```python
import anyio
from pydantic_ai import Agent
from pydantic_ai.models import Model


async def main(model: str | Model) -> None:
    workflow = Agent(model)
    async with workflow.run_stream("Summarize the supplied text.") as response:
        async for text in response.stream_text():
            print(text, end="")
        print("\n---")
        print("Final:", response.output)


# Supply a configured model from the application's startup boundary.
# anyio.run(main, configured_model)
```

## Version notes

- Version 1 established a stable public API; breaking changes are reserved for the next major version.
- Version 1.88.0 renamed `result_type` to `output_type` and removed the older result-tool fields.
- Read run results through `result.output`, not the older `result.data` field.
