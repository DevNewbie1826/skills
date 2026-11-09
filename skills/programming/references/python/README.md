
# Python Programmer

> Read this when writing or reviewing Python source, packages, scripts, or project configuration.

Modern Python. Type-strict, stack-first, async-correct.

## Philosophy

The type checker is your compiler. Make illegal states unrepresentable. Parse at boundaries. Own resources explicitly. Every function has a contract; the type system enforces it.

## Hard rules

These are deliberate project choices. Violations are always wrong, not "style preferences".

### Tooling

| Category | Use | Never |
|---|---|---|
| Package manager | `uv` | pip, poetry, conda, pipenv |
| Type checker | `basedpyright` (`typeCheckingMode = "all"`) | pyright, mypy |
| Linter + formatter | `ruff` (`select = ["ALL"]`) | flake8, black, isort, autopep8 |
| Async runtime | `anyio` | `import asyncio` |
| Data | `polars` + `duckdb` + `numpy` | pandas |
| Web framework | FastAPI + Pydantic v2 | Flask, Django REST |
| ORM | SQLAlchemy 2.x async | Django ORM, Tortoise |
| HTTP client | [`httpx2`](https://github.com/pydantic/httpx2) | requests, aiohttp, httpx |
| Testing | `pytest` | unittest |
| CLI | `typer` + `rich` | argparse, click, fire |

### The iron list

1. **Frozen by default** — `@dataclass(frozen=True, slots=True)`. Pydantic: `model_config = ConfigDict(frozen=True)`. Mutable only when mutation is the documented purpose.
2. **NewType for distinct IDs** — `UserId = NewType("UserId", int)`. Never pass raw `int` where a branded type exists.
3. **`match` only for variants, `if` only for booleans** — **NEVER** use `if/elif/else` to discriminate on type (`isinstance`), enum value, or literal variant. `match/case` is mandatory for these — non-negotiable. **ALWAYS** end with `case unreachable: assert_never(unreachable)` — bare `case _: pass` and `case _: raise ValueError` are banned (they silently swallow new variants). `if/else` is fine only for boolean expressions, range checks, and predicate calls that aren't variant discrimination. Examples: [error-handling.md](error-handling.md).
4. **Protocol over ABC** — `typing.Protocol` for interfaces. ABC only when you need shared method implementation.
5. **No raw dicts in signatures** — params and returns use `TypedDict`, `dataclass`, or Pydantic model. Internal scratch dicts are fine.
6. **Parse, don't validate** — constructors produce typed objects or raise. Never pass unvalidated data deeper into the call stack.
7. **Typed errors** — error types are dataclasses or exceptions with typed fields. Never `raise ValueError("something")` with a bare string. Use union returns when the caller is within 1-2 call levels and must handle the outcome (repository → service). Use exceptions when the error should propagate up many layers to a boundary handler (service → HTTP handler).
8. **Final for constants** — module-level constants use `Final`. Mutable module globals are a code smell.
9. **Explicit None** — annotate `-> X | None`. Never return `None` from a function whose signature omits it.
10. **Context managers for resources** — files, DB connections, HTTP clients, locks. No manual `.close()`.
11. **No Any, no object** — both are banned as type annotations. `object` erases all structural information (zero callable attributes, zero narrowing). Use `Protocol` (structural typing), `TypeVar` (generic pass-through), explicit union (known variants), or `TypedDict` (dict shapes). Examples: [type-patterns.md](type-patterns.md).
12. **No cast** — `cast()` is banned. Redesign the types.
13. **No type: ignore** — fix the type error. The checker is right; you are wrong.
14. **No broad except** — `except Exception` and `except BaseException` are banned. Catch the **specific** exception you expect. A broad catch swallows bugs you need to see — `KeyError`, `AttributeError`, `TypeError` all vanish silently. If you genuinely need a catch-all at a top-level boundary (CLI entry, HTTP handler), use `# noqa: BROAD_EXCEPT_OK` and log + re-raise. Examples: [error-handling.md](error-handling.md).

### Typing and safety

- `basedpyright` in `typeCheckingMode = "all"`. Every public function has full annotations. Internal helpers: annotate return type; parameter types may be inferred.
- `ruff` with `select = ["ALL"]`. Override specific rules per project in `pyproject.toml`, never globally disable the strict baseline.
- Every new function must have a `docstring` unless its name + signature make it completely obvious (e.g. `def full_name(first: str, last: str) -> str:`).
- Use `X | Y` union syntax (PEP 604), never `Union[X, Y]` or `Optional[X]`.

### Async

- `import asyncio` is **BANNED**. Use `import anyio`.
- For background tasks, use `anyio.create_task_group`. Never fire-and-forget with `asyncio.create_task`.
- For concurrency gates, use `anyio.CapacityLimiter` (not `asyncio.Semaphore`).
- Load `async-anyio.md` when writing async code for the full pattern library.

### Data modeling — which container, when

All model fields carry type annotations. No `Any`, no untyped dicts in public APIs.
Use `polars` + `duckdb` for data. pandas is never the right answer in this stack.

**The one rule**: data crosses a trust boundary → Pydantic. Everything else → dataclass.

Load `data-modeling.md` for the container table, decision flowchart, and comparison matrix.

### When frozen=True does not apply

- **ORM models** — SQLAlchemy `Mapped[]` requires mutation. Use `# noqa: MUTABLE_OK`.
- **Builder / accumulator** — object exists to be mutated (counter, buffer, state machine). Docstring must explain why.
- **Pydantic Settings** — tests override fields. Mutable is acceptable.

If you need `# noqa: MUTABLE_OK`, the class docstring must say why mutation is required.

### Libraries

Canonical defaults (override only if `pyproject.toml` explicitly picks something else):

| Domain | Library | Reason |
|---|---|---|
| CLI | `typer` | Type-annotated CLI from function sigs |
| Pretty output | `rich` | Tables, progress, tracebacks, markdown |
| HTTP client | [`httpx2`](https://github.com/pydantic/httpx2) | Next-gen HTTP client (Pydantic stewardship), HTTP/2, brotli+zstd. Always `httpx2[http2,brotli,zstd]`. See `httpx2-optimization.md` |
| Validation | `pydantic` v2 | Fast native validator, JSON Schema |
| Web API | `fastapi` | Async, Pydantic-native, OpenAPI |
| ORM | `sqlalchemy` 2.x async | `Mapped[]` types, async sessions |
| DB driver (Postgres) | `asyncpg` (via SQLAlchemy) | Fastest PG driver |
| AI agents | `pydantic-ai` | Typed deps, structured output |
| TUI | `textual` | Rich-based, CSS layout, widgets |
| Logging | `rich.logging.RichHandler` | Pretty; swap to `structlog` in prod |

## pyproject.toml — the one true config

Scaffold a new project with all strict defaults pre-configured:

```bash
uv run ../../scripts/python/new-project.py myproject
uv run ../../scripts/python/new-project.py myproject --path ./workspace
uv run ../../scripts/python/new-project.py myproject --lib   # publishable library
```

The script runs `uv init`, then injects basedpyright `typeCheckingMode = "all"` + ruff `select = ["ALL"]` + pytest strict. Cross-platform (macOS, Linux, Windows).

For manual setup: `uv init --app myproject`, then load `pyproject-strict.md`.

## PEP 723 — inline script metadata (mandatory for ALL scripts)

Every `.py` script, even a throwaway one, uses PEP 723 inline metadata; the full mandate lives in `one-liners.md`. Use plain pip / pipx / python3 -m venv if uv is unavailable.

Scaffold with: `uv run ../../scripts/python/new-script.py <name> --deps "httpx2[http2,brotli,zstd]"` (writes to temp dir by default, `--output` for specific path).

Load `one-liners.md` for full patterns, examples, and anti-patterns.

## Reference loading

Load on demand — not all at once. This index is the lane's topic map; the router links here.

| Need | Load |
|---|---|
| Full pyproject.toml config | `pyproject-strict.md` |
| Type patterns (NewType, Final, enums, narrowing) | `type-patterns.md` |
| Data modeling (container choice, frozen, parse-don't-validate) | `data-modeling.md` |
| Error handling (typed errors, union returns, exhaustive match) | `error-handling.md` |
| Async patterns (anyio) | `async-anyio.md` |
| Data processing (polars / duckdb) | `data-processing.md` |
| FastAPI + SQLAlchemy stack | `fastapi-stack.md` |
| Library decision tree | `libraries.md` |
| **httpx2 optimization** (MUST load for any network code) | `httpx2-optimization.md` |
| **orjson** (when JSON is in the hot path; FastAPI/Pydantic v2 integration) | `orjson-stack.md` |
| One-liner scripts (PEP 723) | `one-liners.md` |
| PydanticAI agents | `pydantic-ai.md` |
| Textual TUI | `textual-tui.md` |

## httpx2 — mandatory for ALL network requests

Every outgoing HTTP call uses the `httpx2` factory from `httpx2-optimization.md`; a bare client is a bug. Never `requests`, never `aiohttp`, never the original `httpx`.

## No-excuse audit

From the skill directory, run `python3 scripts/python/check-no-excuse-rules.py <changed-paths>` after every edit session. The checker uses only Python's standard library; use the platform's compatible Python launcher if `python3` is unavailable. Fix every violation before declaring work done.

Opt-out tokens (rules not listed here have none):

| Rule ID | Opt-out |
|---|---|
| `no-asyncio` | `# noqa: ANYIO_OK` |
| `no-pandas` | `# noqa: PANDAS_OK` |
| `mutable-dataclass` | `# noqa: MUTABLE_OK` |
| `missing-slots` | `# noqa: SLOTS_OK` |
| `raw-dict-return` | `# noqa: DICT_OK` |
| `missing-assert-never` | `# noqa: MATCH_OK` |
| `generic-exception` | `# noqa: GENERIC_ERR_OK` |
| `no-object` | `# noqa: OBJECT_OK` |
| `if-elif-on-variant` | `# noqa: IF_VARIANT_OK` |
| `oversized-module` | `# noqa: SIZE_OK` |
| `broad-except` | `# noqa: BROAD_EXCEPT_OK` |

## In tests

Tests relax only the rules in the `tests/**` per-file-ignores of `pyproject-strict.md`. They still follow the iron list and the authoring gate in [`../testing/README.md`](../testing/README.md). If test fixtures need mutable state, use `# noqa: MUTABLE_OK` on the fixture class.

## Existing codebases

When editing an existing file that doesn't follow these rules: **write new code in strict style, don't refactor existing code in the same change.** Mixing feature work with style migration makes reviews harder and bugs likelier.
