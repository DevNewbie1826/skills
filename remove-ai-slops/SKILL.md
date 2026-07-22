---
name: remove-ai-slops
description: "Remove AI-generated code slop from branch changes or an explicit file list while preserving behavior. Use when asked to remove slop, clean AI code, deslop, clean up generated code, strip slop, or review generated-code cleanup. Start by locking behavior with regression tests, then use the category and workflow references."
---

# Remove AI Slops

Use this skill for a bounded cleanup of generated-code smells without changing observable behavior.

## Non-negotiable invariant

Before removing or simplifying source code, establish a green regression-test baseline for its observable behavior. A checklist does not replace a test. If a green baseline cannot be established, stop and report the blocker.

## Inputs and scope

- Default scope: changed source files in the current branch relative to its merge base with the integration branch.
- Optional scope: an explicit file list supplied by the caller.
- Exclude deleted, binary, generated, vendored, and lock files; list the final scope before editing.
- Keep every edit within that scope. Report nearby issues outside it rather than changing them.

## Phase flow

1. Create a phase checklist and work on one phase at a time.
2. Determine and state the bounded file scope.
3. Identify observable behavior, add narrow regression tests where coverage is weak, and run them green before cleanup.
4. Run the deletion ladder: delete, reuse existing code, use platform or dependency support, then simplify only what must remain.
5. Make a per-file plan that names categories, order, risk, and any intentional debt.
6. Evaluate every category in the prescribed safest-to-riskiest order.
7. Process independent files in bounded batches: when delegation is available, one worker per file in batches of at most five — never one worker per category, per finding, or per review question; otherwise work file by file.
8. Run all applicable quality gates, perform critical review, and repair only failures caused by the cleanup.
9. Report scope, behavior lock, plan, category results, gates, risks, and final status.

## Operating constraints

- Preserve public APIs, type information, exception behavior, and intentional boundary validation.
- Apply a performance change only when semantic equivalence is obvious; otherwise skip it.
- Do not add abstractions or dependencies merely to make a cleanup look tidier.
- State every skipped gate as `N/A` with its reason; never claim a pass without running and reading it.
- If a modular split is required, present the responsibility-based split plan before making the split.

## Read on demand

| Need | Read |
| --- | --- |
| Decide whether code is slop; apply KEEP, REFACTOR, and proof rules; handle a large module | [Slop categories](references/slop-categories.md) |
| Scope the work, lock tests first, plan and batch cleanup, run gates, recover failures, or format the report | [Workflow and quality gates](references/workflow.md) |

## Fast routing

- Start with [Workflow and quality gates](references/workflow.md) for every cleanup.
- Read [Slop categories](references/slop-categories.md) before planning or delegating a category pass.
- For a prose-only change, do not create wording-pinning tests; review machine-consumed values through their real parser or validator when one exists.
