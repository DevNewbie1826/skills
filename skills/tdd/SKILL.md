---
name: tdd
description: "Use when implementing a feature or fixing a bug, before writing implementation code; when writing or changing tests; when refactoring behavior. Applies to any language — not just the four the programming skill covers. Triggers: TDD, test first, red/green/refactor, write a test, watch it fail, regression test, characterization test, test quality, name the break, add a mock."
---

# Test-Driven Delivery

Drive a behavior change with a failing test that names the break, implement the minimum that passes, then refactor while green. Language-agnostic — it loads for any language, not just the four the programming skill covers.

| Need | Read |
|---|---|
| The red/green/refactor cycle, name-the-break gate, mutation check, and when TDD does not apply | [The cycle](references/cycle.md) |
| Test quality — name the break, exercise the real thing, fakes before mocks, determinism, never pin prose | [Writing good tests](references/writing-good-tests.md) |

A flaky (intermittently failing) test is a nondeterminism problem, not a TDD task: reach a controlled reproduction with the `debugging` skill first, then add a regression test here.
