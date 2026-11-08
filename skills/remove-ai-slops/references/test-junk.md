Read this when judging whether an existing test is junk, marking tests R/F/C/D, proving a test cut, or deciding what a changed file still needs tested.

# Junk tests: classes, retention bar, marks, proof

Tests are code in scope like any other file. A test that matches a class below is junk unless the retention bar keeps it. This file is self-contained: it is the single table for both adding missing tests and pruning junk ones.

## Missing tests

Add a test only when both hold: the repository keeps tests for this kind of behavior, and a regression would otherwise pass unnoticed.

- Write the narrowest test that asserts an observable output, side effect, error, or boundary at the real seam, and name the contract it guards.
- Never assert the implementation shape the cleanup is about to change, and never a value derived from the code under test.
- A prose file (prompt, `SKILL.md`, rule, markdown) has no behavioral seam. Cover only a machine-consumed value (a parsed field, a sentinel a runtime greps, a documented JSON sample through its real validator); otherwise leave it to review.

## Marks (one per test declaration; one per row when table rows differ)

| Mark | Meaning | What the ledger line names |
|---|---|---|
| `R` retain | guards a contract | the contract and the regression it catches |
| `F` fix | real contract, weak assertion (a negative that passes when only one of several items is missing; a truthiness check on a value that is always an object; a lower bound over independently removable items) | the repaired assertion |
| `C` consolidate | the assertion moves into a keeper (a table row in a sibling test, a stronger boundary suite); the declaration disappears | the keeper |
| `D` delete | no contract, or another test owns it | the owner test that still fails on the regression, or why no contract exists; plus a proof receipt |

## Junk classes (candidates for `D` or `C`)

| Class | What it looks like | Proof that it is junk |
|---|---|---|
| Cannot fail | no assertion; `expect(x).toBe(x)`; expected value computed by the code under test; `assert result is not None` and nothing else; an override fixture equal to its fallback; an assertion inside a callback that never runs | a mutation of the owner that the test survives |
| Change certificate | pins the diff, not a behavior: a constant, a string, a rename, a call, the shape of the edit | revert the change: it fails for the diff, not for a regression; the run is the proof |
| Mock echo | the mock returns the value the test then asserts; the behavior lives in the mock | mutate the owner: the test stays green |
| Implementation mirror | asserts call order, call count, private helper arguments, private member access, or internal state shape that a behavior-preserving refactor would break | a keeper at the real boundary catches the behavioral mutation |
| Prose pin | asserts wording, headings, section order, snapshots, phrase counts, or length of a skill file, prompt, agent doc, docs, or rule text | no runtime behavior to mutate; cite the repository's prose-test rule |
| Copied inventory | a hard-coded list of exports, files, tools, or keys that mirrors the source and fails only when someone edits both | a generator, freshness check, or real consumer already owns it |
| Source grep | reads a source file and greps for a string or import | an identifier-only refactor turns it red for no reason; a behavior mutation it misses |
| Duplicate contract | the same input and output asserted at two or more layers with no distinct transport or lifecycle risk | the mutation is caught by both: keep the stronger boundary |
| Layer replay | a shared helper re-tested through every wrapper that calls it | one helper owner test plus one wiring test per real wrapper |
| Seam keeper | exists only to keep a test-only export, flag, getter, or reset hook alive | an unused-export checker or a grep shows no production caller; delete test and seam together |
| Fabricated postcondition | the fixture supplies the receipt, ordering, or stored state the owner should produce; asserts a store nothing writes | mutate the writer: the test stays green |
| Capability restatement | asserts a flag or capability is `true` instead of the delivery it promises | a delivery test owns it, or none exists (then `F`, not `D`) |
| Input transcript | asserts the argv, flags, URL, or request handed to a child, not the state the child resolved | mutate the child's handling of that input: the test stays green; the witness drives the real component and asserts resolved state |
| Misnamed | the name promises a behavior its inputs never exercise | read the assertions; mark by what it actually checks |
| Near-duplicate cases | N tests differing only in input literals | `C` into one parameterized table; typecheck after; every old assertion stays a row |

## Retention bar (these stay `R` even when they match a class above)

Keep a test that independently guards a public API, wire or protocol contract, config schema or default, migration, storage format, security boundary, platform behavior, byte equality between shipped artifacts, a generated or cross-language contract, a package or install payload, a release step, or an architecture invariant. Say which one in the ledger. Also keep:

- **Platform suites**: anything that runs shipped code under its real runtime is a platform contract even when another runtime covers the same assertions.
- **Issue regressions**: a test naming an issue number stays until another test is shown to fail on that exact regression.
- **Machine-consumed text**: parsed fields, sentinel tokens, tool names, schema keys, a routing-bearing fragment of a parsed frontmatter description.
- **Baseline-red tests**: a test that fails on the unchanged base is a product bug to report and fix at its owner, never a deletion; exclude it from every proof.

Outside that list, a source-inspection test survives only as the cheapest independent guard of a user-facing key, byte, or path that an identifier-only refactor leaves green. Static or slow is never a reason to delete.

## Proof rule for `D` and `C`

Break the production owner (flip a condition, drop a branch, return a constant, skip a write) and run the candidate and its named keeper on the unmodified test tree:

| Candidate | Keeper | Verdict |
|---|---|---|
| green | red | the candidate cannot catch this: `D` proven |
| red | red | the candidate is redundant for this behavior: `D` or `C` proven |
| red | green | the candidate is the only proof: `R`, or `C` it into the keeper and re-run |
| green | green | the mutation missed the behavior: confirm the edit landed, then pick another mutation |

Run one mutation at a time, never while another worker edits the tree. Record the owner's checksum before the mutation and confirm it is byte-identical after restoring; never commit a mutation. A prose pin needs no mutation: the receipt is the assertion line plus the repository rule. A coverage diff proves lines still execute, not that anything still asserts on them; pair it with at least one mutation per theme.

Proof kind per class: behavior classes (cannot fail, mock echo, source grep, duplicate contract, layer replay, implementation mirror, fabricated postcondition, input transcript) use the mutation above; prose pin uses the assertion line plus the repository rule; change certificate uses the revert that turns it red; seam keeper uses the no-production-caller check; copied inventory uses the generator or consumer that owns it; capability restatement uses the delivery test that owns the promise; near-duplicate cases use the single table that keeps every old assertion as a row.

## Static candidates

Without a bundled detector, list candidates with a repository search over in-scope test files: source reads that grep for a string, snapshot or phrase-count assertions on prose files, fixed sleeps, focused or skipped markers, and self-comparison assertions. Each hit is a candidate to mark, never an automatic cut.
