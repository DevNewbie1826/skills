Read this when scoping a cleanup, locking behavior with tests, coordinating category passes, running quality gates, or reporting results.

# Workflow and quality gates

## Core rule

A cleanup begins only after observable behavior is protected by a green regression-test baseline; a checklist complements the test but does not replace it. If a file's baseline cannot be made green, leave that file untouched and report the blocker; only a runner that cannot run at all stops the whole pass (Phase 2 owns the mechanics).

Read [slop-categories.md](slop-categories.md) before planning changes. It defines the ten categories, their Keep rules and proof requirements, the deletion ladder, and the oversized-module policy.

## Phase 1: Determine scope

1. Use an explicit file list when one was supplied.
2. Otherwise, use the version-control system to list changed files from the current branch relative to its merge base with the integration branch. If version control is unavailable, require an explicit file list.
3. Exclude deleted and binary files, generated or vendored paths, dependency lock files, and build artifacts.
4. List the final source-file scope before editing. Do not change files outside it; report nearby findings as deferred findings.

## Phase 2: Lock behavior with regression tests

For every in-scope source file:

1. Identify public or otherwise observable behavior: exports, handlers, commands, integration points, and classes used by other code.
2. Find related tests using project conventions and search tools.
3. If coverage is absent or weak, write the narrowest regression test that pins current observable behavior before editing the source, under the admission conditions in [test-junk.md](test-junk.md). Favor outputs, side effects, errors, and boundary behavior over implementation details.
4. A prose-only file is exempt from prose-pinning tests; [test-junk.md](test-junk.md) owns the rule and the machine-consumed-value exception.
5. Run the relevant tests, or the full suite when practical. A test that is red on the unchanged base is recorded as a product bug on a baseline-red list and is never deleted. If it covers behavior of an in-scope file, that file's baseline is not green: leave the file untouched and report the blocker. A red test unrelated to every in-scope file is only recorded and excluded from proofs. Everything covering in-scope behavior must be green before cleanup starts.
6. Search every in-scope test file, including any written in step 3, for junk candidates as listed under Static candidates in [test-junk.md](test-junk.md). Hits become candidates for the tests ledger, never automatic cuts.

Only a runner that cannot run at all stops the pass: record the failure and stop.

## Phase 3: Create the cleanup plan

Run the deletion ladder from [slop-categories.md](slop-categories.md) on each changed unit before assigning smell categories.

For a bug-fix diff, inspect callers of each shared changed function; [slop-categories.md](slop-categories.md) owns the root-cause-over-caller-guards rule.

Write an explicit plan before edits. Include the ladder decision, relevant categories, safest-to-riskiest order, and risk for each file. For example:

```text
File: src/example-a
  Ladder: 2 units simplify in place; 1 unit delete because platform support replaces it
  Categories: dead code, excessive complexity, performance equivalences
  Order: dead code -> excessive complexity -> performance equivalences
  Risk: medium (touches caching)

File: src/example-b
  Ladder: all simplify in place
  Categories: obvious comments, over-defensive code
  Order: obvious comments -> over-defensive code
  Risk: low
```

When deliberately retaining a bounded simplification, mark it the way the deletion ladder's step 4 prescribes in [slop-categories.md](slop-categories.md), and include it in the report's Debt Ledger.

Plan the tests ledger: one ledger row per `D`, `C`, or `F` mark, plus one `R` row for each test that matches a junk class but stays under the retention bar. Workers produce the rows per the per-file brief in [slop-categories.md](slop-categories.md); Phase 4b proves and cuts.

## Phase 4: Execute category passes with batch discipline

Use the categories in the numbered order defined in [slop-categories.md](slop-categories.md).

For independent files, delegation — when the runtime supports it, one `task` worker per file — means exactly one worker per file, never one worker per category, per finding, or per review question; without delegation, work file by file.

1. Divide the scoped file list into batches of at most five files.
2. When delegation is available, start all independent file reviews in the current batch together; otherwise complete the batch one file at a time.
3. Give each worker the per-file cleanup brief from [slop-categories.md](slop-categories.md), including every category and hard constraint.
4. Collect and review every result before starting the next batch.
5. Do not let one blocked file prevent review of the remaining files in its batch.
6. Retry a file once only if its result is missing, explicitly blocked, or lacks the required deliverable.
7. After a failed retry, record the file and blocker under issues rather than silently abandoning it.

A running worker is alive: treat only a finished worker without its deliverable, an acknowledgment-only reply after one follow-up, or an explicit `BLOCKED:` message as failed.

Every per-file pass must preserve the safety-frame guarantees of [slop-categories.md](slop-categories.md) and stay in scope. It must not add dependencies or speculative abstractions. Skip any uncertain change.

## Phase 4b: Prove the test cuts, serially, then cut

After the last batch finishes and no worker is running, the lead proves each collected ledger row serially, exactly as the proof rule in [test-junk.md](test-junk.md) prescribes. Cut a `D` or `C` row only after its proof is recorded and every behavior the candidate asserts is covered by a surviving keeper, not just the one mutated; a row whose proof does not hold becomes `R` and stays. Workers apply `F` repairs in the files they own and report them as applied; the lead verifies them here.

## Phase 5: Run quality gates and critical review

Run every applicable gate. If a project does not configure a gate, report it as `N/A` with the reason; never silently skip it.

| Gate | Evidence required for pass |
| --- | --- |
| Regression tests | The relevant regression tests are green. |
| Lint | The project linter reports zero new errors; note pre-existing warnings or failures separately. |
| Type checking | Changed-file diagnostics and the project type checker report zero new errors. |
| Unit and integration tests | The applicable project test suite is green; note pre-existing failures not introduced by this work. |
| Static or security scan | The configured scanner has zero new findings, or `N/A` is reported when none is configured. |

Then answer these questions yourself, per changed file, from the diff and gate output. This review is a reasoning step, not a delegation step — do not spawn per-finding or per-question reviewers:

### Safety

- Was any functional logic removed accidentally?
- Is error handling preserved, especially around I/O, network calls, and external services?
- Are type declarations intact and correct?
- Are imports valid?
- Did any public API change?

### Behavior

- Do return values remain unchanged as demonstrated by the regression tests?
- Do side effects remain unchanged?
- Does exception behavior remain unchanged?
- Is edge-case handling preserved?

### Quality

- Are removed items genuinely slop rather than intentional patterns?
- Does the remaining code follow project conventions?
- Are there orphaned references or dead paths?
- Are performance changes obviously equivalent rather than subtle algorithm shifts?
- Were new abstractions avoided?

## Phase 6: Repair failures

If a gate fails or review finds a problem:

1. Identify the specific cleanup change that caused it and explain the failure.
2. Revert only the affected hunk through the available version-control workflow or a targeted edit.
3. If genuine slop remains, make the smallest directly provable fix within scope.
4. Rerun the failed gate and redo review for the affected file.
5. Stop after three failed attempts on the same file and report the file, attempted changes, failures, and hypothesis.

Do not delete or weaken tests to make a gate pass. Do not use unrelated edits or blind retries.

## Reporting format

Use evidence rather than assertions. A complete report contains:

```text
AI SLOP REMOVAL REPORT
======================

Scope: [branch comparison / explicit file list]
Files: [N files]
  - path/to/file

Behavior Lock:
  - Existing coverage: [files already covered]
  - Tests added: [new regression-test paths, or none]
  - Baseline status: GREEN | BLOCKED (baseline-red tests, recorded as bugs and excluded from proofs: none | list)

Cleanup Plan:
  - path/to/file: [ladder decision] -> [category order]

Per-File Results:
  path/to/file
    - [category]: [before] -> [after]; why slop; why safe
    - Skipped (preserved): [issue and reason]

Tests Ledger (one row per `D`, `C`, or `F` mark, plus one per `R` that matches a junk class but stays under the retention bar; proofs run in Phase 4b):
  | Test | Mark | Keeper / reason | Proof |
  |---|---|---|---|
  | path/to/test > name | D | source grep; named keeper owns the contract | mutation of the owner: candidate green, keeper red; owner restored checksum-equal |

Quality Gates:
  - Regression tests: PASS | FAIL | N/A (reason)
  - Lint: PASS | FAIL | N/A (reason)
  - Type checking: PASS | FAIL | N/A (reason)
  - Unit and integration tests: PASS | FAIL | N/A (reason)
  - Static or security scan: PASS | FAIL | N/A (reason)

Critical Review:
  - Safety: PASS | FAIL
  - Behavior: PASS | FAIL
  - Quality: PASS | FAIL

Issues Found & Fixed:
  - [None] or [issue -> fix]

Net Impact:
  - LOC: [removed and added]
  - Dependencies: [removed, added, or none]
  - Files deleted: [paths or none]

Remaining Risks / Deferred:
  - [None] or [risk, blocker, or deferred finding (out of scope)]

Debt Ledger (intentional-debt markers):
  - [none or file:line -- ceiling -> upgrade trigger]

Final Status: CLEAN | ISSUES FIXED | REQUIRES ATTENTION
```

## Failure-resistant conduct

If a tool fails, retry it with corrected parameters or use an available equivalent; do not silently skip the evidence. Never claim a gate passed without executing it and reading the output. When correctness needs more inspection, continue with source reads, diagnostics, and the project test runner — at most three further inspection rounds on the same question; if still ungrounded after that, stop and report what remains unproven.

Avoid these anti-patterns: skipping the behavior lock, bundling unrelated refactors, disguising an algorithm change as a performance optimization, silently skipping a gate, removing comments that explain why, and touching files outside scope.
