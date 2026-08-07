---
name: tdd
description: "Use when implementing a feature or fixing a bug, before writing implementation code; when writing or changing tests; when refactoring behavior. Applies to any language. Triggers: TDD, test first, red/green/refactor, write a test, test quality, name the break, add a mock, fix a flaky test."
---

# Test-Driven Delivery

Write the failing test first, watch it fail for the right reason, implement the minimum that passes, then refactor while green. Watching the test fail for the right reason is what proves it can catch the bug — a test that has only ever passed may be asserting the wrong thing, pinning the implementation, or missing the edge case, and you would not know.

## Red — write the failing test

Before the test body, **name the break**: the production change that should make this test fail — a wrong branch, missing side effect, wrong argument, boundary case, or broken contract. Cannot name one? Redesign around an observable behavior.

- One behavior per test, with a clear name.
- Test real code; no mocks unless the dependency cannot be real or deterministic.
- Run it. It must fail because the behavior is absent or incorrect — not because the fixture or import is broken.
- It passes immediately? You may be testing existing behavior rather than the change you intend — sharpen the test to target the new behavior. (A characterization test that pins existing behavior before a behavior-preserving refactor is meant to pass against the current code; that is its purpose.)

## Green — implement the minimum

- Make only the change required for that behavior to pass. No extra features, no refactors, no "improvements."
- Run it: the test passes and the rest of the suite stays green.

## Refactor — improve while green

- Remove duplication, improve names, extract helpers. Keep tests green; add no behavior.
- A test that blocks a safe refactor is a coupling problem: fix the test, then refactor.
- Add the next case as the next red test.

## Mutation check

Before finishing, mentally mutate the production code. For each realistic mutation — a wrong constant or argument, a wrong branch handler, a missing state change or side effect, an empty or default return, or missing validation for zero, empty, nil, unauthorized, or malformed input — at least one test should fail. A mutation nothing catches marks the behavior unprotected or the test tautological.

## When TDD does not apply

Judgment, not ritual. Skip the cycle for throwaway prototypes, generated code, and pure configuration — and say why. Reconsider once the code survives or the behavior starts to matter. A test written after the code is still useful when its expectation is derived independently; one that merely mirrors what the code already does proves only that the code agrees with itself.

## Test quality

When writing or changing any test, read [writing-good-tests.md](references/writing-good-tests.md): name the break, exercise the real thing, fakes before mocks, determinism, and never pin prose.
