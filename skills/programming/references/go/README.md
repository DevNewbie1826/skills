
# Go Programmer

> Read this when writing or reviewing Go source, modules, service definitions, or Go-adjacent interface specifications.

Production Go in 2026. **Boring on purpose, strict by tooling, illegal states unrepresentable by convention.**

## Philosophy

Go gives you fewer type-system tools than Python, TypeScript, or Rust:

- No native sum types — only `interface{}` with type-switch.
- No exhaustiveness check from the compiler — only the `exhaustive` linter.
- No `Option<T>` — only `nil` and the eternal trap of "is this nil interface or nil concrete?".
- No `Result<T, E>` — only `(T, error)`, no compiler enforcement of unwrapping.
- No newtype that prevents primitive coercion — `type UserID string` is still implicitly convertible from a literal when used carelessly.

**This is the whole point of the skill.** Where the language is weak, the linter bundle becomes the type checker, and code patterns become the type system. Treat `golangci-lint v2` with the configuration in `golangci-strict.md` as if it were `tsc --strict` or `basedpyright`. Treat `nilaway` and `go test -race` as if they were Miri.

The skill enforces five non-negotiables:

1. **Parse-don't-validate at every boundary.** HTTP/RPC/CLI/config gets parsed into a domain struct constructed only via `New*(...)` smart constructors. Once inside the domain, no further validation. See `data-modeling.md`.
2. **`(T, error)` everywhere.** No panics in library code. No bare `_ = err`. Errors are wrapped with `%w` and asserted with `errors.Is` / `errors.As`. Typed error structs for anything a caller can branch on. See `error-handling.md`.
3. **Sealed interfaces for variants.** Sum types via a sealed unexported method, dispatched through a `type switch`, with the `exhaustive` linter checking completeness. See `type-patterns.md`.
4. **`context.Context` is the first parameter.** Always. No `context.Background()` inside leaf functions. No goroutine without context-driven shutdown. No `time.Now()` in domain code — inject a clock. See `concurrency.md`.
5. **Generated, not hand-written, for external contracts.** `sqlc` for DB, `oapi-codegen` for OpenAPI servers and clients, `protoc-gen-go` + `protoc-gen-connect-go` for RPC. Hand-rolled marshalling is a regression. See `sqlc-pgx.md`, `grpc-connect.md`.

## Reference index

Toolchain policy and the CI gate live in [`golangci-strict.md`](golangci-strict.md); CI wiring lives in [`bootstrap.md`](bootstrap.md).

- **Types & data** → `type-patterns.md`, `data-modeling.md` — branded named types, smart constructors with unexported fields, sealed interfaces as sum types.
- **Errors** → `error-handling.md` — sentinel vs typed struct, `errors.Is/As`, `%w` wrapping, no panic in libraries, the `errorlint` ruleset.
- **Concurrency** → `concurrency.md` — `context.Context` discipline, `errgroup`, `sync.OnceValue`, `goleak`, `-race`, channel selection rules.
- **HTTP backend (framework lane)** → `backend-stack.md` — service skeleton, middleware ordering, SSE/streaming with `http.Flusher`, structured logging, and graceful shutdown.
- **RPC** → `grpc-connect.md` — when to pick Connect vs grpc-go, codegen pipeline, protovalidate, streaming.
- **DB** → `sqlc-pgx.md` — compile-time-safe SQL via sqlc + pgx connection pool + migrations via goose + testcontainers in CI.
- **CLI** → `cobra-stack.md` — cobra layout, slog integration, graceful shutdown on signals, fang-style colored help.
- **TUI** → `bubbletea-v2.md` — v2 model, `SetVirtualCursor(false)` + `tea.View{Cursor}` for CJK IME, why v1 was broken for Korean/Japanese/Chinese input.
- **Testing** → `testing.md` — table-driven tests, `require` vs `assert`, `autogold` snapshots, `rapid` property tests, `testcontainers` for integration, `goleak` for goroutine leaks.
- **Bootstrap** → `bootstrap.md` — `scripts/go/new-project.py` invocation, project layout (`cmd/`, `internal/`, `pkg/`), Taskfile, CI.
- **Strict config** → `golangci-strict.md` — the canonical `.golangci.yml` with the full linter whitelist, toolchain policy, and the CI gate.
- **One-liners** → `one-liners.md` — `go run` scripts with `//go:build ignore`, `gorun`-style invocation.

## Scope rules

The 250 pure LOC ceiling applies to `.go` files as in [`../code-smells.md`](../code-smells.md); `cmd/*/main.go` only wires signals into `cmd.Execute`. In a non-strict codebase, write new code in strict style and don't refactor existing code in the same change.

## Activation

This skill activates whenever you write or modify any `.go` file, `go.mod`, `go.sum`, `.golangci.yml`, `Taskfile.yml`, or any of the codegen specs (`*.proto`, `*.sql` next to `sqlc.yaml`, `openapi.yaml` next to `oapi-codegen.yaml`). Even one-off scripts get the strict treatment — that is what `//go:build ignore` + `go run` is for: production hygiene with throwaway ergonomics.

The references contain the recipes. **Read them before writing code. Re-read them when project constraints change.**
