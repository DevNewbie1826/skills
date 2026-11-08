# Testing

> Read this when creating, reshaping, reviewing, or deleting a test file, or when deciding whether a change needs a test at all.

This file is the language-independent test contract the per-language recipes assume (`../go/testing.md`, `../rust/proptest-insta.md`, and the test sections of the other language READMEs). The red/green cycle, naming the break, fakes before mocks, and determinism live in the `tdd` skill; this file adds the authoring gate, the isolation and prompt-test rules, and the "test your test" step. [`junk-classes.md`](junk-classes.md) is the companion table: every class there is a test this file tells you not to write.

## Before writing: the authoring gate

Answer all four; a missing answer means do not add the test yet.

1. **What observable behavior, invariant, or independent contract does it protect?** Name it in the test name.
2. **What credible regression makes it fail?** If no plausible edit to the production owner turns it red, it is a [change certificate or cannot-fail](junk-classes.md), not a test.
3. **Why does existing coverage not already catch that failure?** Each contract has one primary owner test at the strongest boundary. Extend a table row or a shared fixture instead of adding a near-duplicate, a copy in another package, or a replay through a wrapper.
4. **Does it need a production seam no production caller needs** (an export, flag, getter, reset hook, wrapper, injection point)? If yes, test at the real boundary instead; a seam that exists for one test is a [seam keeper](junk-classes.md).

The run proves the change; a test proves that the next change cannot silently undo it. Add a test only where the repository keeps tests for this behavior AND a regression would otherwise pass unnoticed by the run and the existing tests. A bug fix starts from a reproduction that fails on the pre-fix code for the intended reason (an existing owner test that already fails may serve as that proof). Prose has no behavioral seam ([prompt tests](#prompt-tests-assert-behavior-never-text)).

A test that fails on the unchanged base is a product bug to fix at its owner; a test your own change turns red is fixed at the code or at the test. Neither is deleted or edited green to unblock a run.

## Shape

| Rung | Count | Purpose | Budget |
|---|---|---|---|
| Unit | many | pure-function correctness for every meaningful input class (happy, edge, boundary, error path) | under 10 ms each; whole unit suite under 30 s |
| Integration | some | the real adapter against the real downstream (database, queue, HTTP) through containers, `httptest`, or the equivalent; never a unit test pretending to be one | under 1 s each; suite under 5 min |
| End-to-end scenario | few | one narrative per user-visible outcome, driven through the real surface (HTTP route, CLI invocation, TUI keystroke); include one error-path scenario | seconds, on CI |

A user-visible outcome never driven through its real surface is unverified; a green unit suite does not stand in for that run. Every test is Given / When / Then with one `When`; names state behavior and condition so a failure reads without the body.

If a test fails when the owner's implementation changes but its behavior did not, it is over-mocked: drop the mock and assert on observable outputs. A boundary list (allowlist, flag filter) is tested with the real list imported from production, not a copy.

### Accurate, deterministic, isolated

- **Accurate**: the test fails for the bug it names and only that bug. Assert the contract, not a dump; no coupling to format, ordering, whitespace, or unrelated fields. Snapshots pin structure (CLI help, a JSON shape), never behavior or prose.
- **Deterministic**: no `sleep`, no wall-clock dependence, no order dependence (`-shuffle=on`, a random-order plugin, a random seed). Inject a clock. For async behavior subscribe to the exact event or state change BEFORE triggering the action, then await it with a bounded timeout that fails with a message; the timeout is a circuit breaker, never the synchronization. A test that passes 9 of 10 runs is broken.
- **Isolated**: every test starts from a known fixture and tears down (temporary directories, scoped environment, transactional rollback). Two tests that pass alone and fail together are a fixture leak; fix the leak, never the order, and never `.only` / `.skip` / a separate process to hide it. Suite-global resources (sandbox roots, listen ports, container names) are namespaced per run (`mktemp`, port `0`, unique names) so two checkouts running the suite concurrently cannot interfere; the signature of that leak is "a different test fails each run".

### Prompt tests: assert behavior, never text

A prompt, skill, rule, or markdown file is prose; its wording changes every sprint. `toContain("<sentence>")`, `not.toContain("old wording")`, a snapshot of prose, a word count, a phrase-occurrence count: each stays green while the behavior it claims to guard breaks, then blocks every legitimate rewording. Assert only what a machine consumes: a builder's routing decision, a structural token the runtime dispatches on (a tool name, a tag, a parsed frontmatter field), the conditional the code enforces (skill loaded -> tool present; `verbose=false` -> directive absent), equality between two shipped copies of one artifact, or the minimal routing-bearing fragment of a parsed `description` that a router dispatches on. A pure-prose change gets review and a read-through, not a test.

When delegating test-writing, hand the child the behavior the test must distinguish ("fails if override precedence breaks"), never a ready-made assertion string or marker to copy: a prescribed mechanism that is wrong gets implemented faithfully and ships behind a green suite.

## After writing: test your test

A test earns its place by failing. Before handoff, run the junk checker on the test files (it flags the classes a regex can see: source grep, prose pin, fixed sleep, `.only`/`.skip`, self-comparison, lower bound), then for each new or reshaped test:

1. **Break the owner** (flip the condition, drop the branch, return a constant, skip the write) and run the test. Confirm the mutated bytes are actually in the file before reading the result; a no-op edit "passes" identically to the original.
2. **Red for the intended reason?** Read the failure message: a loose pattern can match the base's generic error by coincidence, and a fake that simulates the failure by a different mechanism than the guard reads fails with the fix present.
3. **Still green?** Then one of: the test is vacuous (fix the assertion); the mutant is equivalent (a `try/catch`, fallback, or normalization maps it back to the same outcome: retarget the mutation at the observable claim); a second rule already produces the same outcome (make the input exercise only the rule under test); or the mutated code is dead (delete the code, not the test's teeth).
4. **Restore byte for byte.** Never commit a mutation.

From the skill directory, with Bun or another TypeScript runner (`bun` shown):

```bash
bun scripts/typescript/check-test-junk.ts <test files>
bun scripts/typescript/mutation-proof.ts --file <owner> --find <text> --replace <text> \
  --test 'candidate=<test command>' --test 'keeper=<test command>'
```

`mutation-proof.ts` does steps 1, 3 and 4 in one run and prints red/green per test. If no TypeScript runner is available, do the same four steps by hand and say the scripts were not run.

Assertion shapes that survive this step:

| Vacuous shape | Why it passes with the bug present | Discriminating shape |
|---|---|---|
| expected value derived from the output under test | compares a projection of the output to itself | derive the expected value from the test's input |
| override fixture equal to its fallback | precedence is never exercised | every value the code must select or override differs from the fallback |
| `>= n` / `> 0` over independently produced items | removing one item still satisfies the bound | pin the exact set |
| a count after deduplication where duplicates are byte-identical to a mandatory item | dropping all duplicates gives the same count | distinct payloads, assert retention and placement |
| the argv, flags, URL, or request handed to a child | an input transcript, not the child's outcome | drive the real component and assert the state it resolved, with a control case |
| a counter or filter keyed on a value the code path never produces | both sides count zero | count the operation itself |
| a copy of the production component, props, or allowlist | the copy passes while the shipped one is broken | mount or import the real one |
| a timing assertion for an off-thread or performance claim | passes on the base at fixture size | prove performance on a field harness; keep the unit test to behavior |
| a gated or fallback path tested without forcing it | the base's own error path produces the same side effect | force the path (flag, crash limit) and assert the reason the new path records |

## Review

A reviewer applies [`junk-classes.md`](junk-classes.md) to every test in the diff and blocks a prose pin as high severity. Deleting such a test is a fix, not a coverage loss, and needs the proof rule in that file. For a branch-wide cleanup use the `remove-ai-slops` skill.
