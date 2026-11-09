# Rust Programmer

> Read this when writing or reviewing Rust source, crates, manifests, or performance-sensitive code.

Production Rust in 2026. **Explicit allocation, compile-time proof, zero hidden cost.** Type-state-first, unsafe-banished-by-default, agent-proof.

## Identity — What Kind of Rust You Write

You write Rust that looks like a Zig programmer designed it and a Rust compiler enforces it. Every allocation is visible. Every cost is explicit. Every invariant is encoded in the type system. Every cleanup is deterministic. The borrow checker, lifetime analysis, trait bounds, and `miri` then guarantee what Zig leaves to discipline.

**Five pillars, every file, no exceptions:**

| Pillar | Default Behavior | Reference |
|---|---|---|
| **Explicit allocation** | Arena for hot paths, `&[T]`/`Cow` over `Vec`/`String` in signatures, `try_*` when allocation can fail | [zero-cost-safety.md §1](zero-cost-safety.md) |
| **Compile-time proof** | `const fn` everything const-eligible, `const { assert!(...) }` for compile-time guards, const generics for sized buffers | [zero-cost-safety.md §2](zero-cost-safety.md) |
| **Zero hidden cost** | Slice-based APIs where caller owns memory, no hidden `.clone()`/`.to_string()`, `Cow` to defer allocation | [zero-cost-safety.md §3](zero-cost-safety.md) |
| **Type-encoded invariants** | Newtype wrappers for every semantic unit, type-state for state machines, domain ID newtypes | [type-state.md](type-state.md) |
| **Deterministic cleanup** | `scopeguard::guard` for errdefer, `Drop` for RAII, defuse-on-success for rollback | [zero-cost-safety.md §5](zero-cost-safety.md) |

The two highest-leverage tools Rust gives a coding agent:

1. **Bounded polymorphism** (traits). Real, machine-checked, composable constraints.
2. **Newtype-as-coordinate-space.** `Point<Screen>` and `Point<World>` are distinct types — the agent literally cannot pass one where the other is expected. This is the `euclid` crate pattern; generalize ruthlessly to money, durations, IDs, byte offsets, char offsets, paths rooted at different bases. Full patterns → [type-state.md](type-state.md).

---

## Hard Rules (Every `.rs` File)

1. **No `unwrap()`/`expect()` outside tests.** Propagate with `?` and context. The one exception is a proven invariant: `.expect("<the invariant>")` behind `#[expect(clippy::expect_used, reason = "<why it cannot fail>")]`, the form clippy and the bundled Rust no-excuse checker both honor. Discarding is handling too: `let _ = fallible();` and `.ok();` that drop an error are forbidden (`let_underscore_must_use`); a best-effort call logs the error it cannot return. Error crates → [libraries.md](libraries.md).
2. **No `unsafe` without miri proof.** Every `unsafe` block gets a safe wrapper, a `// SAFETY:` comment, and a miri test → [unsafe-discipline.md](unsafe-discipline.md). Load the soundness lane entry point [`../rust-ub/README.md`](../rust-ub/README.md) and open its linked taxonomy or sanitizer file only when that hazard is present.
3. **Explicit allocation.** Arena in hot paths, borrows (`&[T]`, `&str`, `Cow`) in signatures, caller-provided buffers where it pays → [zero-cost-safety.md §1](zero-cost-safety.md), [§3](zero-cost-safety.md).
4. **Compile-time first.** Tables, size assertions, and buffer sizes are computed at build time; never contort runtime logic to be const → [zero-cost-safety.md §2](zero-cost-safety.md).
5. **Deterministic cleanup.** `scopeguard` for errdefer with defuse-on-success, `Drop` for RAII → [zero-cost-safety.md §5](zero-cost-safety.md).
6. **No hand-written `transmute` for wire formats.** Use `zerocopy` → [zero-cost-safety.md §4](zero-cost-safety.md).
7. **Exhaustive match on enums you control.** No `_ =>`; for external `#[non_exhaustive]` enums the wildcard logs a `tracing::warn!`.
8. **Type-state over runtime checks.** Never `if self.state == State::Validated` → [type-state.md](type-state.md).
9. **Numbers state what overflow and conversion mean.** `checked_*`/`saturating_*`/`wrapping_*` instead of bare `+`, `From`/`TryFrom` instead of `as` (except a lossless widening inside `const`), floats compared with a domain tolerance and sorted with `f64::total_cmp`, `NonZeroU32` for values that can never be zero.

---

## Standard Library Defaults

Full decision tree with rationale and code snippets → [libraries.md](libraries.md).

| Category | Crate | Why |
|---|---|---|
| Async runtime | `tokio` | Ecosystem standard. Patterns → [async-tokio.md](async-tokio.md) |
| HTTP server | `axum` + `tower` | Type-safe extractors, tower middleware. Stack → [axum-stack.md](axum-stack.md) |
| CLI | `clap` derive + `color-eyre` | Typed args, beautiful errors. Stack → [clap-stack.md](clap-stack.md) |
| Serialization | `serde` + `serde_json` | Non-negotiable for any boundary type |
| Error (library) | `thiserror` | Derive `Error` with zero boilerplate |
| Error (binary) | `anyhow` / `color-eyre` | Context-rich ad-hoc errors |
| Database | `sqlx` (compile-time checked) | No runtime SQL surprises |
| Arena alloc | `bumpalo` / `typed-arena` | Explicit allocation scope. Patterns → [zero-cost-safety.md §1](zero-cost-safety.md) |
| Zero-copy parse | `zerocopy` | Safe binary parsing, no transmute. Patterns → [zero-cost-safety.md §4](zero-cost-safety.md) |
| Scope guard | `scopeguard` | errdefer/defer. Patterns → [zero-cost-safety.md §5](zero-cost-safety.md) |
| Stack collections | `smallvec` / `arrayvec` / `tinyvec` | Stack-first, heap-spillover. Patterns → [zero-cost-safety.md §3](zero-cost-safety.md) |
| Bitfield | `bitfield` / `modular-bitfield` | Bit-packed flags. Patterns → [zero-cost-safety.md §4](zero-cost-safety.md) |
| Testing | `proptest` + `insta` | Property + snapshot tests. Patterns → [proptest-insta.md](proptest-insta.md) |
| Concurrency | `tokio::sync` / `parking_lot` | Channel-first, lock-second. Patterns → [concurrency.md](concurrency.md) |

---

## Cargo Strict Configuration

Every new project gets the strict lint config and the CI gate from [cargo-strict.md](cargo-strict.md).

---

## Reference Index

| File | When to Load |
|---|---|
| [zero-cost-safety.md](zero-cost-safety.md) | Arena, allocator, const fn, comptime, zero-alloc, bitfield, repr, scopeguard, errdefer, Zig-like patterns |
| [type-state.md](type-state.md) | Newtype wrappers, validated construction, type-state machines, domain ID newtypes, phantom types |
| [api-design.md](api-design.md) | Public API: naming, conversions, trait design, `#[must_use]`, `#[non_exhaustive]`, visibility, rustdoc sections |
| [macros.md](macros.md) | `macro_rules!` hygiene, proc-macro crates (`syn`/`quote`), spanned compile errors |
| [unsafe-discipline.md](unsafe-discipline.md) | Any `unsafe` block — SAFETY comments, safe wrappers, miri proof |
| [libraries.md](libraries.md) | Library selection, crate decision tree, dependency audit |
| [cargo-strict.md](cargo-strict.md) | Project bootstrap, lint config, CI gate commands |
| [async-tokio.md](async-tokio.md) | Async runtime, spawning, cancellation, `JoinSet`, `select!` |
| [axum-stack.md](axum-stack.md) | HTTP services — axum + sqlx + tower + tracing |
| [clap-stack.md](clap-stack.md) | CLI tools — clap derive + color-eyre + indicatif |
| [concurrency.md](concurrency.md) | Locks, atomics, channels, loom model checker |
| [proptest-insta.md](proptest-insta.md) | Property tests, snapshot tests, round-trip invariants |
| [one-liners.md](one-liners.md) | `rust-script` one-liners, disposable scripts, inline deps |
| [../rust-ub/README.md](../rust-ub/README.md) | UB hunting — the soundness lane router |
| [../rust-ub/ub-taxonomy.md](../rust-ub/ub-taxonomy.md) | 14-category UB taxonomy with detection status |
| [../rust-ub/miri-sanitizers-loom.md](../rust-ub/miri-sanitizers-loom.md) | Miri flags, ASAN/TSAN/MSAN, loom, cargo-fuzz |

---

## The Shape of Every Function

```rust
/// One-line doc explaining WHAT, not HOW.
///
/// # Errors
/// Returns `FooError::Bar` when the input is invalid.
fn frobnicate<'a>(
    arena: &'a Bump,        // explicit allocator when arena is in play
    input: &[u8],           // borrow, not owned
    output: &mut [u8],      // caller-provided buffer
) -> Result<&'a Frob, FrobError> {
    // ...
}
```

**Why this shape:** the caller sees every cost. Allocation scope is the arena's lifetime. Input is borrowed. Output buffer is caller-owned. Error is typed. The compiler enforces all of it.

