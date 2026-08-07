---
name: programming
description: "MUST USE for work on Python, Rust, TypeScript, or Go source files and project manifests. Triggers: write or edit code; new project; Go HTTP service (gin lane); Bubble Tea TUI; CJK IME; Connect-Go RPC; sqlc or pgx; branded IDs; exhaustive matching; unsafe Rust; Miri; oversized file; refactoring; logging, log levels, structured logging, or observability; arena, allocator, bumpalo, const fn, const generics, compile-time programming, zero-allocation APIs, bitfields, repr, scope guards, errdefer-style cleanup, Zig-like patterns, zero-copy parsing, packed data, or FFI."
---

# Programming

Build the smallest correct change: type-strict, boundary-aware, async-correct, and honest about module size. Read the applicable language lane before changing code.

## Shared philosophy

Use these principles; the full doctrine lives in [Shared programming philosophy](references/philosophy.md).

- Root causes over symptoms
- Types as proof
- Parse once at the boundary
- Exhaustive matches and focused tests

## Language gate

Before writing or editing code, identify the language and read its entry point. Follow the entry point's on-demand links for the affected concern.

| Files or request | Read first | Also read when relevant |
|---|---|---|
| `.py`, `.pyi`, Python | [Python lane](references/python/README.md) | The linked Python topic reference |
| `.rs`, `Cargo.toml`, Rust | [Rust lane](references/rust/README.md) | [Rust soundness lane](references/rust-ub/README.md) for `unsafe`, raw pointers, `MaybeUninit`, FFI, manual `Send`/`Sync`, or lock-free primitives |
| `.ts`, `.tsx`, `.mts`, `.cts`, TypeScript | [TypeScript lane](references/typescript/README.md) | The linked TypeScript topic reference |
| `.go`, `go.mod`, `go.sum`, `.golangci.yml`, or Go-adjacent `.proto` | [Go lane](references/go/README.md) | The linked Go topic reference |

## Cross-cutting routes

| Need | Read |
|---|---|
| Before the first edit: assumptions, task scope, or done criteria | [Shared programming philosophy § Pre-edit discipline](references/philosophy.md) |
| Design, review, LOC limits, or portable verification | [Shared programming philosophy](references/philosophy.md) |
| Test-driven development, test shape, fakes or mocks, or test quality | the `tdd` skill (Test-Driven Delivery) |
| Adding or changing logs, logger setup, or boundary error handling | [Logging](references/logging.md) |
| A file exceeds 200 pure LOC, a function has more than three parameters, verification is redundant, or names are negative-form | [Code smells](references/code-smells.md) |
| Rust memory safety, FFI, or concurrent primitive audit | [Rust soundness lane](references/rust-ub/README.md) and its linked taxonomy |

## Python lane

Read [Python lane](references/python/README.md) first, then select the relevant detail.

| Need | Read |
|---|---|
| Strict project configuration and tooling | [Python strict configuration](references/python/pyproject-strict.md) |
| Type patterns | [Python type patterns](references/python/type-patterns.md) |
| Data models and boundary parsing | [Python data modeling](references/python/data-modeling.md) |
| Typed errors and exhaustive matching | [Python error handling](references/python/error-handling.md) |
| Structured async work | [Python async](references/python/async-anyio.md) |
| Production HTTP client behavior | [Python HTTP client](references/python/httpx2-optimization.md) |
| Fast JSON paths | [Python JSON stack](references/python/orjson-stack.md) |
| Data processing | [Python data processing](references/python/data-processing.md) |
| HTTP service implementation | [Python HTTP service](references/python/fastapi-stack.md) |
| Model-driven workflow implementation | [Python model workflows](references/python/pydantic-ai.md) |
| Terminal UI | [Python TUI](references/python/textual-tui.md) |
| Disposable scripts | [Python one-liners](references/python/one-liners.md) |
| Library selection | [Python library defaults](references/python/libraries.md) |

## Rust lane

Read [Rust lane](references/rust/README.md) first, then select the relevant detail.

| Need | Read |
|---|---|
| Strict project configuration and tooling | [Rust strict configuration](references/rust/cargo-strict.md) |
| Type state and semantic types | [Rust type state](references/rust/type-state.md) |
| `unsafe` implementation discipline | [Rust unsafe discipline](references/rust/unsafe-discipline.md) |
| Full undefined-behavior audit | [Rust soundness lane](references/rust-ub/README.md) |
| Async work | [Rust async](references/rust/async-tokio.md) |
| Concurrency primitives | [Rust concurrency](references/rust/concurrency.md) |
| HTTP service implementation | [Rust HTTP service](references/rust/axum-stack.md) |
| Command-line application | [Rust CLI](references/rust/clap-stack.md) |
| Property and snapshot testing | [Rust testing](references/rust/proptest-insta.md) |
| Disposable scripts | [Rust one-liners](references/rust/one-liners.md) |
| Libraries, allocation, compile-time, or zero-allocation work | [Rust library defaults](references/rust/libraries.md) and [Rust zero-cost safety](references/rust/zero-cost-safety.md) |

## TypeScript lane

Read [TypeScript lane](references/typescript/README.md) first, then select the relevant detail.

| Need | Read |
|---|---|
| Strict project configuration and tooling | [TypeScript strict configuration](references/typescript/tsconfig-strict.md) |
| Branded types and narrowing | [TypeScript type patterns](references/typescript/type-patterns.md) |
| Data models and boundary parsing | [TypeScript data modeling](references/typescript/data-modeling.md) |
| Typed errors, results, cancellation, and timeouts | [TypeScript error handling](references/typescript/error-handling.md) |
| New project or package setup | [TypeScript bootstrap](references/typescript/bootstrap.md) |
| HTTP service implementation | [TypeScript HTTP service](references/typescript/backend-hono.md) |

## Go lane

Read [Go lane](references/go/README.md) first, then select the relevant detail.

| Need | Read |
|---|---|
| Go library and framework selection | [Go library defaults](references/go/libraries.md) |
| Strict lint configuration | [Go strict configuration](references/go/golangci-strict.md) |
| New project, layout, or CI | [Go bootstrap](references/go/bootstrap.md) |
| Named types, constructors, interfaces, or generics | [Go type patterns](references/go/type-patterns.md) |
| Boundary and domain validation | [Go data modeling](references/go/data-modeling.md) |
| Errors and wrapping | [Go error handling](references/go/error-handling.md) |
| Context, goroutines, channels, locks, or race detection | [Go concurrency](references/go/concurrency.md) |
| HTTP service implementation | [Go HTTP service](references/go/backend-stack.md) |
| RPC service implementation | [Go RPC](references/go/grpc-connect.md) |
| Command-line application | [Go CLI](references/go/cobra-stack.md) |
| Database access and migrations | [Go database](references/go/sqlc-pgx.md) |
| Terminal UI and CJK input | [Go TUI](references/go/bubbletea-v2.md) |
| Tests, fakes, and integration coverage | [Go testing](references/go/testing.md) |
| Disposable scripts | [Go one-liners](references/go/one-liners.md) |

## Activation

Use this router for source changes and relevant manifests. For a one-off script, use the same language lane and the smallest suitable verification command; disposable code still crosses boundaries, has failure modes, and benefits from types and tests.
