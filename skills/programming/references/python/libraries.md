# Library Defaults — Decision Tree

> Read this when selecting Python libraries or an implementation lane for a new concern.

For each domain, the canonical 2026 choice, why, and the canonical usage snippet. The skill enforces these unless the project's `pyproject.toml` explicitly says otherwise.

## CLI — typer

`typer` builds a CLI from type-annotated function signatures. argparse needs 5x the code; click ignores type annotations; fire is magic that breaks at scale.

```python
import typer
from rich import print as rprint

app = typer.Typer()

@app.command()
def greet(name: str, count: int = 1, shout: bool = False) -> None:
    """Print a greeting `count` times."""
    message = f"Hello, {name}!" if not shout else f"HELLO, {name.upper()}!"
    for _ in range(count):
        rprint(message)

if __name__ == "__main__":
    app()
```

For a single-function script, `typer.run(main)` skips the `Typer()` boilerplate. Subcommands use `@app.command()`.

## Terminal output — rich

`rich` produces tables, progress bars, syntax highlighting, traceback rendering. Use it for any structured output. Plain `print` is acceptable for non-interactive log lines (and even those are usually better via `rich.console.Console(stderr=True).log(...)`).

```python
from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Users")
table.add_column("ID", style="cyan")
table.add_column("Name", style="magenta")
table.add_row("1", "Alice")
console.print(table)

# Rich tracebacks (call once at process start)
from rich.traceback import install
install(show_locals=True)
```

## HTTP client — [httpx2](https://github.com/pydantic/httpx2)

Next-generation HTTP client under Pydantic stewardship. Sync and async in one library, HTTP/2 native, brotli + zstd content decoding, real type stubs. Replaces `requests` (sync only), `aiohttp` (async only), and the original `httpx`.

**Install**: `httpx2[http2,brotli,zstd]` — always include all three extras, no exceptions.

**A bare `httpx2.AsyncClient()` / `httpx2.Client()` is a bug.** Use the factory functions (`create_client()` / `create_async_client()`) from `httpx2-optimization.md`, which carries the verbatim defaults, event hooks, and rationale. **Load that reference whenever you write ANY network code.**

## JSON — stdlib `json` (default) or `orjson` (hot paths)

Stdlib `json` is fine for cold paths and configs. **Reach for `orjson` when JSON is in the hot path** — cache layers, queue payloads, streaming responses, structured logs, FastAPI endpoints returning raw `dict` / `list`.

```python
import orjson

# orjson.dumps returns bytes, not str
raw: bytes = orjson.dumps(
    payload,
    option=orjson.OPT_NAIVE_UTC | orjson.OPT_UTC_Z | orjson.OPT_SERIALIZE_DATACLASS,
)
```

Use `model_dump_json()` for Pydantic models and orjson for everything else. See `orjson-stack.md` for the decision tree, flags, and FastAPI integration.

## Validation — pydantic v2

Pydantic v2's core is in Rust (~10x faster than v1). It is the de-facto boundary validator. Use it for:

- HTTP request/response models (FastAPI uses pydantic natively)
- Config files (env vars via `pydantic-settings`)
- Anything entering the program from outside

Patterns: [data-modeling.md](data-modeling.md).

`@dataclass` is fine for purely internal records (no validation needed). For anything crossing a process boundary, use Pydantic.

## Async — anyio

Full reference: [async-anyio.md](async-anyio.md). The summary:

```python
import anyio

async def fetch(url: str) -> str:
    await anyio.sleep(0.1)
    return url

async def main() -> None:
    async with anyio.create_task_group() as tg:
        for url in ["a", "b", "c"]:
            tg.start_soon(fetch, url)

anyio.run(main)
```

Never `import asyncio` directly. The third-party libraries you call are free to use asyncio internally.

## Web framework — fastapi

Type-hint-driven HTTP framework. Pydantic models become OpenAPI schemas automatically.

Full stack with database: [fastapi-stack.md](fastapi-stack.md).

## ORM — sqlalchemy 2.x async

SQLAlchemy 2.x finally has a real async API. Use the modern declarative `MappedAsDataclass` style with type annotations.

Full pattern with FastAPI integration: [fastapi-stack.md](fastapi-stack.md).

## Database — postgres + asyncpg

For new applications, default to Postgres. SQLite for tests is fine; SQLite for production is not.

asyncpg is the fastest Python Postgres driver, native to SQLAlchemy 2.x async, native to FastAPI's lifespan model. URL: `postgresql+asyncpg://user:pass@host:5432/db`.

For migrations, use Alembic's async template and set `sqlalchemy.url` in `env.py` (see [fastapi-stack.md](fastapi-stack.md)):

```bash
uv add alembic
uv run alembic init -t async migrations
```

## TUI — textual

Textual builds rich, mouse-aware, mobile-style TUIs on the rich rendering engine. See [textual-tui.md](textual-tui.md).

## AI agents — pydantic-ai

The agent framework from the Pydantic team. Type-strict, structured outputs are first-class, model-agnostic. See [pydantic-ai.md](pydantic-ai.md).

## DataFrames — polars + numpy

Polars is 10-50x faster than pandas, has a real type system, and supports lazy evaluation. Numpy stays in the toolbox for arrays. See [data-processing.md](data-processing.md).

## OLAP / SQL — duckdb

DuckDB is the SQL engine for analytical workloads. Query CSV/Parquet/JSON files directly without loading into memory; perform joins and aggregations 3-4x faster than Polars; zero-copy interchange with Polars via Arrow. See [data-processing.md](data-processing.md).

## Tests — pytest

Use pytest. Conventions:

- File names `test_*.py`, function names `test_*`.
- Fixtures via `@pytest.fixture`. Async fixtures are anyio-aware (`@pytest.fixture` on an async function works under anyio's pytest plugin).
- Parametrise with `@pytest.mark.parametrize`.
- Mark async tests with `@pytest.mark.anyio` (provided by anyio's pytest plugin).

```python
import pytest

@pytest.fixture
def sample_user() -> dict[str, str]:
    return {"name": "Alice", "email": "a@b.com"}

@pytest.mark.parametrize("count,expected", [(1, "Hello"), (2, "Hello, Hello")])
def test_greet(count: int, expected: str) -> None:
    result = ", ".join(["Hello"] * count)
    assert result == expected
```

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = ["-ra", "--strict-config", "--strict-markers"]
```

## Settings / config — pydantic-settings

Loads env vars and `.env` files into a Pydantic model. Replaces ad-hoc `os.environ.get(...)` everywhere.

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MYAPP_")

    database_url: str
    api_key: str = Field(min_length=1)
    debug: bool = False

settings = Settings()  # loads at import time; raises if any required var is missing
```

## Logging — stdlib logging + rich handler

Stdlib `logging` is fine; it gets a face-lift from `rich.logging.RichHandler`.

```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
log = logging.getLogger(__name__)
log.info("ready")
```

For structured logging in production, swap to `structlog` (separate dep). Don't roll your own.
