# Shared Programming Philosophy

> Read this when a change needs cross-language design, testing, review, logging, or verification guidance.

The best code is code that never needs to exist. When code is necessary, make the smallest change that preserves the real contract: type-strict, boundary-aware, async-correct, and clear about ownership.

## Pre-edit discipline

These apply before the first edit, for any change to code, configuration, documentation, prompts, or skill guidance.

1. **Resolve assumptions at the source.** Read the approved task and any relevant plan, the current behavior and tests, and nearby conventions before the first edit; then confirm types, interfaces, imports, and call sites through reads, AST/LSP, or tests — not after. A guessed API or contract is a bug waiting to happen.
2. **Touch only what the task justifies.** No drive-by refactors, broad renames, or style rewrites alongside an unrelated change. A corrective change the escalation rules below require (a responsibility split, a typed parameter group) is justified, not a drive-by.
3. **Define done before editing.** Name the concrete success criterion and the verification command first. Completion is evidence, not effort.

## The seven axioms

1. **Stop at the first rung that holds.** Ask, in order: does this need to exist; does the codebase already provide it; does the standard library or platform provide it; does an existing dependency provide it; can it be one direct operation; only then write the minimum new code. Trace the flow first. A small patch at the wrong seam is a second bug.
2. **Fix root causes.** A ticket describes a symptom. Inspect callers and adjacent paths before adding a guard. Prefer one correction at the shared seam over repeated compensating checks.
3. **Use types as proof.** Model illegal states out of existence. Distinct units, identifiers, and state transitions deserve distinct types. Let the compiler or type checker reject invalid combinations before runtime.
4. **Parse once at the boundary.** Convert untrusted HTTP, RPC, CLI, configuration, file, queue, and database inputs into typed values at ingress. Interior code consumes typed values and does not repeat validation.
5. **Match closed variants exhaustively.** Use the language's exhaustive-match pattern and an explicit unreachable assertion where the compiler cannot prove completeness. Do not let a default conditional silently accept a new variant.
6. **Trust established contracts.** Do not add null checks, broad catches, casts, or post-action verification for states that a type, framework, or operation already guarantees. Validate only at true system boundaries.
7. **Prove behavior with focused tests.** Start a behavior change with a test that fails for the intended reason, implement the minimum, then refactor with the test green.

## Test-driven delivery

### Red, green, refactor

1. **Red:** write a failing test that names the behavior and run it. Confirm that it fails because the behavior is absent or incorrect, not because the fixture or import is broken.
2. **Green:** make only the change required for that behavior to pass. Add the next case as the next red test.
3. **Refactor:** improve the design only while the test is green. If the test blocks a safe refactor, fix the test's coupling before changing production code.

### Test shape

| Layer | Purpose | Expectation |
|---|---|---|
| Unit | Pure behavior, edges, boundaries, and error paths | Fast and local; exercise meaningful input classes |
| Integration | A real adapter against a real downstream or faithful sandbox | Verify the wire, schema, query, or process boundary rather than an implementation imitation |
| End-to-end | A user-visible narrative through the real surface | Drive the binary, route, CLI, TUI, or equivalent and assert observable outcomes |

Use all applicable layers. An end-to-end scenario does not replace edge-focused units; units do not prove that the real boundary is wired correctly.

### Given / When / Then

Structure each test around one action:

```text
Given: the preconditions and fixtures
When:  the single action under test
Then:  the observable outcome caused by that action
```

Keep one `When` per test. Assert the contract that changed, not unrelated state, formatting, ordering, whitespace, or implementation details.

### Fakes before mocks

Choose the narrowest truthful substitute:

1. A real object when it is cheap to construct.
2. An in-memory fake with its own contract tests.
3. A real service in an isolated sandbox or container.
4. A wire-level fake that preserves the protocol.
5. A mock only when the dependency cannot be made real or deterministic, such as a clock, randomness source, or unavailable external service.

A test that fails when internals change but observable behavior stays the same is over-mocked. Reduce the mock boundary or assert the outcome instead.

### Determinism is part of correctness

- Do not use fixed sleeps, polling loops, wall-clock assumptions, or test-order dependence.
- For asynchronous behavior, subscribe to the exact event or state transition before triggering the action, then await it with a bounded timeout.
- Inject clocks, randomness, and external seams where their values affect behavior.
- Start each test from a known fixture and clean up all files, environment variables, transactions, goroutines, tasks, and processes it owns.
- Ensure override and fallback fixtures differ; a test cannot prove precedence when both values are identical.

### Prompt and generated-text tests

Do not pin prose. A text-fragment assertion or prose snapshot usually blocks legitimate wording changes while failing to prove a machine-consumed decision. Instead test the routing decision, parsed metadata, tool or action schema, feature flag, or other structural behavior. If no machine consumes the text, document that it is reviewed as prose rather than inventing a brittle test.

## Cross-language design rules

Use the language lane for exact syntax and libraries. These principles apply in every lane:

| Concern | Rule |
|---|---|
| Immutability | Default to immutable values; make mutation explicit and local to the owner. |
| Semantic primitives | Use a named or branded type for IDs, units, and other non-interchangeable primitives. |
| Errors | Use typed errors or values that callers can branch on; preserve causal context when wrapping. |
| Resource ownership | Acquire and release resources with the language's scoped ownership mechanism. |
| Async work | Propagate cancellation, bound concurrency, and make ownership of spawned work explicit. |
| Parameters | Prefer a typed domain value when related inputs outgrow a small, coherent signature. |
| Abstractions | Do not create a helper, class, trait, or interface for a single trivial use with no second caller. |

## Code-smell escalation

Read [Code smells](code-smells.md) when any of these triggers fires.

| Trigger | Required response |
|---|---|
| A source file exceeds 200 pure LOC | Treat it as a warning band; name the responsibility and plan a split before the next growth. |
| A source file exceeds 250 pure LOC | Treat it as a defect. Split by responsibility before adding more behavior, except for a specifically justified generated or data-only exception. |
| A function has more than three independent parameters | Group related inputs in a typed domain value or justify the independent inputs concretely. |
| A destructive action is immediately re-queried | Remove the redundant verification; fix an operation that can silently fail instead. |
| A variable, function, or flag is named negatively | Rename it positively and invert the branch where that improves readability. |

Pure LOC excludes blank and comment-only lines. Measure it with a language-appropriate tool or the bundled checker.

## Logging

Read [Logging](logging.md) before adding or changing log lines, logger setup, service entry points, or boundary error handling.

The existing project convention wins, including the convention of having no logging in a layer. Choose a level by naming its consumer, place logs at decisions and boundaries rather than helpers, keep messages stable, and put variable data in structured fields.

## Post-write review

Run this review after every substantive code change.

1. **Responsibility:** can the file's job be named in one short noun phrase without "and"?
2. **Boundary:** did untrusted input become a typed value at the boundary, or did an unstructured value leak inward?
3. **Variants:** is every tagged variant or enum matched exhaustively?
4. **Escape hatches:** did a cast, unchecked assertion, broad catch, suppression, or warning override hide a type or contract problem?
5. **Defensive layers:** did a redundant null check, catch, or verification accumulate around a trusted contract?
6. **Abstractions:** did a one-use helper or broad interface appear without a real second caller?
7. **Tests:** would a focused test fail if this behavior regressed?
8. **Parameters:** did a signature gain too many independent inputs or an untyped options bag?
9. **Names:** are names positive and direct?
10. **Logging:** if logs changed, are they consistent with the local practice and useful to their consumer?

Fix a failed answer before declaring the change complete. For a structural change, use a safe refactoring workflow: map callers, make one behavior-preserving step at a time, and run the narrowest relevant verification after each step.

## Verification commands and fallbacks

Run commands from the skill directory or use equivalent relative paths from the current working directory.

```bash
# Python: standard-library checker; no package manager is required.
python3 scripts/python/check-no-excuse-rules.py <changed-paths>

# Rust
bash scripts/rust/check-no-excuse-rules.sh <changed-paths>

# TypeScript
bun run scripts/typescript/check-no-excuse-rules.ts <changed-paths>
```

The Python checker requires Python 3.9 or newer and only the standard library. If `python3` is not the local command, use the platform's compatible Python launcher. The Rust and TypeScript checkers require their respective runtimes; if one is unavailable, run the project's native compiler and test command where possible, or state that the unavailable check was not run. Never report an unavailable validator as a pass.

Then run the language lane's formatter, type checker or compiler, relevant tests, and the real user-facing entry point when one exists. Scale breadth to the change, but do not substitute assumptions for a command that actually passed.
