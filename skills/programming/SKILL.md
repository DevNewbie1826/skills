---
name: programming
description: "MUST USE for work on Python, Rust, TypeScript, JavaScript, or Go source files and project manifests, and whenever a test or spec file is written, reshaped, reviewed, or deleted. Triggers: write or edit code; add, change, or delete a test; test authoring gate; junk tests; new project; Go HTTP service (gin lane); Bubble Tea TUI; CJK IME; Connect-Go RPC; sqlc or pgx; branded IDs; exhaustive matching; unsafe Rust; Miri; oversized file; refactoring; logging, log levels, structured logging, or observability; arena, allocator, bumpalo, const fn, const generics, compile-time programming, zero-allocation APIs, bitfields, repr, scope guards, errdefer-style cleanup, Zig-like patterns, zero-copy parsing, packed data, or FFI; Rust public API design or macros."
---

# Programming

Build the smallest correct change: type-strict, boundary-aware, async-correct, and clear about ownership. The doctrine lives in [Shared programming philosophy § The seven axioms](references/philosophy.md).

## Language gate

Before writing or editing code, identify the language and read its lane. Each lane README is that language's topic index; follow its links for the affected concern. One-off scripts use the same lane with the smallest suitable verification command.

| Files or request | Read first | Also read when relevant |
|---|---|---|
| `.py`, `.pyi`, Python | [Python lane](references/python/README.md) | Its topic index |
| `.rs`, `Cargo.toml`, Rust | [Rust lane](references/rust/README.md) | [Rust soundness lane](references/rust-ub/README.md) for `unsafe`, raw pointers, `MaybeUninit`, FFI, manual `Send`/`Sync`, lock-free primitives, or a memory-safety audit |
| `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`, TypeScript or JavaScript | [TypeScript lane](references/typescript/README.md) | Its topic index |
| `.go`, `go.mod`, `go.sum`, `.golangci.yml`, or Go-adjacent `.proto` | [Go lane](references/go/README.md) | Its topic index |
| Any test file (`*.test.*`, `*.spec.*`, `*_test.go`, `test_*.py`, `tests/`, `__tests__/`) or a change that adds, reshapes, or deletes a test | The language row above | [Testing § Before writing: the authoring gate](references/testing/README.md) and [Junk classes](references/testing/junk-classes.md) |

## Cross-cutting routes

| Need | Read |
|---|---|
| Before the first edit: assumptions, task scope, or done criteria | [Shared programming philosophy § Pre-edit discipline](references/philosophy.md) |
| Cross-language design rules or the post-write review | [Shared programming philosophy § Cross-language design rules and § Post-write review](references/philosophy.md) |
| Upgrading a dependency, bumping a version, or resolving a lockfile conflict | [Shared programming philosophy § Dependency upgrades](references/philosophy.md) |
| A file past 200 pure LOC (warning) or 250 (defect), a function with more than three parameters, redundant verification, or negative-form names | [Code smells](references/code-smells.md) |
| Test-driven development, test shape, fakes or mocks | the `tdd` skill (Test-Driven Delivery) |
| Proving a test can fail or pruning junk tests | [Junk classes § Proof rule for `D` and `C`](references/testing/junk-classes.md) |
| Bundled checkers, scaffolders, and the test-junk and mutation scripts | [Bundled script dependencies](scripts/DEPS.md) |
| Adding or changing logs, logger setup, service entry points, or boundary error handling | [Logging](references/logging.md) |
