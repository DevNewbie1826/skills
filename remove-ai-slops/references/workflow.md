Read this when scoping a cleanup, locking behavior with tests, coordinating category passes, running quality gates, or reporting results.

# Workflow and quality gates

## Core rule

A cleanup begins only after observable behavior is protected by a green regression-test baseline. The test is the safety mechanism; a checklist complements it but does not replace it. If the relevant tests cannot be made green, stop and report the blocker rather than editing unverified code.

Read [slop-categories.md](slop-categories.md) before planning changes. It defines the ten categories, KEEP rules, proof requirements, deletion ladder, and oversized-module policy.

## Phase 0: Prepare

Create a checklist covering every phase below. Mark only one phase active at a time so scope and evidence remain clear.

## Phase 1: Determine scope

1. Use an explicit file list when one was supplied.
2. Otherwise, use the version-control system to list changed files from the current branch relative to its merge base with the integration branch. If version control is unavailable, require an explicit file list.
3. Exclude deleted and binary files, generated or vendored paths, dependency lock files, and build artifacts.
4. List the final source-file scope before editing. Do not change files outside it; report nearby findings as deferred work.

## Phase 2: Lock behavior with regression tests

For every in-scope source file:

1. Identify public or otherwise observable behavior: exports, handlers, commands, integration points, and classes used by other code.
2. Find related tests using project conventions and search tools.
3. If coverage is absent or weak, write the narrowest regression test that pins current observable behavior before editing the source. Favor outputs, side effects, errors, and boundary behavior over implementation details.
4. A prose-only file is exempt from wording-pinning tests. Test a machine-consumed value only through its real parser, validator, or runtime seam; otherwise use review.
5. Run the relevant tests, or the full suite when practical. They must be green before cleanup starts.

If the baseline is broken, do not clean up on that ground. Record the failure and stop.

## Phase 3: Create the cleanup plan

Run the deletion ladder from [slop-categories.md](slop-categories.md) on each changed unit before assigning smell categories: delete entirely, reuse existing project code, use platform or installed support, then simplify in place.

For a bug-fix diff, inspect callers of each shared changed function. Prefer the root-cause correction at the shared seam over repeated caller-side guards.

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

When deliberately retaining a bounded simplification, document it in code with a `debt:` comment or the project's equivalent intentional-debt marker. Name the ceiling and the upgrade trigger, then include it in the final debt ledger. A known ceiling without a marker is indistinguishable from a defect.

## Phase 4: Execute category passes with batch discipline

Use the categories in this order: obvious comments, dead code, over-defensive code, duplication, excessive complexity, needless abstraction and boundary violations, performance equivalences, missing tests, oversized modules.

For independent files, delegation — when the runtime supports it — means exactly one worker per file, in batches of no more than five files. Never spawn workers per category, per finding, or per review question; without delegation, work file by file.

1. Divide the scoped file list into batches of at most five.
2. When delegation is available, start all independent file reviews in the current batch together; otherwise complete the batch one file at a time.
3. Give each reviewer the per-file cleanup brief from [slop-categories.md](slop-categories.md), including every category and hard constraint.
4. Collect and review every result before starting the next batch.
5. Do not let one blocked file prevent review of the remaining files in its batch.
6. Retry a file once only if its result is missing, explicitly blocked, or lacks the required deliverable.
7. After a failed retry, record the file and blocker under issues rather than silently abandoning it.

Every per-file pass must preserve behavior, public APIs, type information, error behavior, and scope. It must not add dependencies or speculative abstractions. Skip any uncertain change.

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
  - Baseline status: GREEN | BLOCKED

Cleanup Plan:
  - path/to/file: [ladder decision] -> [category order]

Per-File Results:
  path/to/file
    - [category]: [before] -> [after]; why slop; why safe
    - Skipped (preserved): [issue and reason]

Quality Gates:
  - Regression tests: PASS | FAIL | N/A (reason)
  - Lint: PASS | FAIL | N/A (reason)
  - Type checking: PASS | FAIL | N/A (reason)
  - Unit/integration tests: PASS | FAIL | N/A (reason)
  - Static/security scan: PASS | FAIL | N/A (reason)

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
  - [None] or [risk, blocker, or out-of-scope finding]
  - Intentional-debt markers: [none or file:line -- ceiling -> upgrade trigger]

Final Status: CLEAN | ISSUES FIXED | REQUIRES ATTENTION
```

## Failure-resistant conduct

If a tool fails, retry it with corrected parameters or use an available equivalent; do not silently skip the evidence. Never claim a gate passed without executing it and reading the output. When correctness needs more inspection, continue with source reads, diagnostics, and the project test runner — at most three further inspection rounds on the same question; if still ungrounded after that, stop and report what remains unproven.

Avoid these anti-patterns: skipping the behavior lock, bundling unrelated refactors, disguising an algorithm change as a performance optimization, silently skipping a gate, removing comments that explain why, and touching files outside scope.
