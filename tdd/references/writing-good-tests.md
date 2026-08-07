# Writing Good Tests

> Read this when writing or changing tests, adding mocks, or adding cleanup helpers.

A test exists to catch a specific break. Two principles govern everything here:

```
1. Every test names the break it catches
2. Every test exercises the real thing
```

Ship the tests the behavior needs and only those: trivial code and human prose earn none, and a test written to satisfy process costs maintenance forever.

## Principle 1: Name the break

Before the test body, name the production change that should make this test fail — and judge whether that change is a bug or a decision. A test earns its place by catching a wrong branch, missing side effect, wrong argument, boundary case, or broken contract.

**Derive expectations independently.** Use literals and hand-checked fixtures; table-driven tests with literal `want` values are the preferred shape. An expectation computed by the code under test — or its helpers — passes no matter what that code does:

```ts
// Mirror assertion: the same builder computes both sides — always true
const expected = buildSearchQuery({ tag: 'urgent' });
expect(buildSearchQuery({ tag: 'urgent' })).toBe(expected);

// Hand-derived literal
expect(buildSearchQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

**No change detectors.** A test that only intentional decisions can fail — a constant's value, exact message wording, private structure — fires on redesign and sleeps through bugs. Test the behavior that depends on the decision: not `expect(MAX_RETRIES).toBe(5)` but "a failing call is retried 5 times and the 6th attempt never happens."

**Behavior, not source text.** Asserting that a script, skill, or config contains an exact line proves only that the source is the source. Run scripts against controlled inputs and assert outputs, side effects, or exit codes; test agent-consumed documents through the consuming agent's behavior, never by grepping their text.

**Your code, not the framework.** Test the contract your code makes at its boundaries — the route you register, the query you emit, the payload you produce. Upstream mechanics are their maintainers' tests to write (asserting that your router invokes a registered handler tests the framework, not you). When upstream behavior genuinely surprised you, write one narrow characterization test naming the assumption. The same boundary applies inside your code: constructors, getters, constants, and trivial forwarding earn tests only when they validate, normalize, default, derive, enforce, or cause side effects — otherwise assert the first consumer-visible result that depends on them.

## Principle 2: Exercise the real thing

**Assert contracts, not mock setup.** An assertion that restates the mock's own configuration (you told it to return X, then assert it returned X) proves only that the mock is wired. But an interaction that is itself the contract — the component emitted one command, to the right collaborator, with the right payload — is the behavior under test; keep it. Delete an assertion whose only check is that the mock exists.

**Substitute at the right level.** Learn every side effect of the real method before replacing it; replace the slow or external boundary with the narrowest truthful fake or sandbox, and keep what the test depends on real. Reach for a strict mock only when the dependency cannot be made real or deterministic. When unsure, run the test against the real implementation first and observe what actually needs to happen.

**Make doubles specific.** When arguments, call counts, or ordering are part of the contract, assert them — a fake that accepts anything verifies nothing. Give each branch (success, error, malformed) its own fixture or spy, so the wrong branch cannot satisfy the expectation.

**Mirror the data the scenario depends on.** Populate every field the scenario exercises plus all fields required for the response to be valid — not every documented optional field. A response missing a field downstream code reads fails silently (test passes, integration breaks); a response padded with irrelevant fields masks accidental dependencies and breaks whenever docs change.

**Production classes carry production methods only.** Cleanup that only tests need lives in test utilities, never as a `destroy()` on the production class. Ask: is this method called only from tests? Does this class own this resource's lifecycle? Wrong answers → test utility.

**Prefer real components over complex mocks.** When mock setup outgrows the test logic, mocks miss methods the real components have, or tests break when the mock changes, switch to an integration test with real components.

## Fakes before mocks

Choose the narrowest truthful substitute:

1. A real object when it is cheap to construct.
2. An in-memory fake with its own contract tests.
3. A real service in an isolated sandbox or container.
4. A wire-level fake that preserves the protocol.
5. A mock only when the dependency cannot be made real or deterministic, such as a clock, randomness source, or unavailable external service.

A test that fails when internals change but observable behavior stays the same is over-mocked. Reduce the mock boundary or assert the outcome instead.

## Determinism is part of correctness

- No fixed sleeps, unbounded polling, wall-clock assumptions, or test-order dependence. When no subscribable event or state hook exists (eventual consistency, black-box systems), a bounded poll with a timeout and a diagnostic failure is the correct synchronization.
- For asynchronous behavior, subscribe to the exact event or state transition before triggering the action, then await it with a bounded timeout.
- Inject clocks, randomness, and external seams where their values affect behavior.
- Start each test from a known fixture and clean up all files, environment variables, transactions, goroutines, tasks, and processes it owns.
- Ensure override and fallback fixtures differ; a test cannot prove precedence when both values are identical.

## Test structure

| Layer | Purpose | Expectation |
|---|---|---|
| Unit | Pure behavior, edges, boundaries, error paths | Fast and local; exercise meaningful input classes |
| Integration | A real adapter against a real downstream or faithful sandbox | Verify the wire, schema, query, or process boundary rather than an implementation imitation |
| End-to-end | A user-visible narrative through the real surface | Drive the binary, route, CLI, TUI, or equivalent and assert observable outcomes |

Use all applicable layers. An end-to-end scenario does not replace edge-focused units; units do not prove that the real boundary is wired correctly.

**Given / When / Then:** structure each test around one action — the preconditions and fixtures, the single action under test, and the observable outcome caused by that action. Keep one `When` per test. Assert the contract that changed, not unrelated state, formatting, ordering, whitespace, or implementation details.

## Don't pin prose

A text-fragment assertion or prose snapshot usually blocks legitimate wording changes while failing to prove a machine-consumed decision. Instead test the routing decision, parsed metadata, tool or action schema, feature flag, or other structural behavior. If no machine consumes the text, document that it is reviewed as prose rather than inventing a brittle test.
