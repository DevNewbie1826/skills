---
name: remove-ai-slops
description: "Remove AI-generated code slop from branch changes or an explicit file list while preserving behavior, including junk tests (prose pins, source greps, copied inventories, mock echoes), each proven by its class rule before a cut. Use when asked to remove slop, clean AI code, deslop, clean up generated code, strip slop, prune junk tests, or review generated-code cleanup. Start by locking behavior with regression tests, then use the workflow and category references."
---

# Remove AI Slops

Bounded cleanup of generated-code smells in a changed file set, with observable behavior preserved.

No source edit before a green behavior baseline: if a file's baseline cannot be made green, leave that file untouched and report the blocker.

| Need | Read | When |
| --- | --- | --- |
| Scope and exclusions, behavior lock, per-file cleanup plan, batch execution, serial test-cut proof, quality gates, critical review, repair, report format, failure conduct | [Workflow and quality gates](references/workflow.md) | First, for every cleanup |
| Decide whether code is slop: the deletion ladder, the ten categories with their Keep rules and proof requirements, the per-file worker brief, the oversized-module policy | [Slop categories](references/slop-categories.md) | Before planning or delegating a category pass |
| Judge an existing test: R/F/C/D marks, the retention bar that can keep a test, mutation proofs for a cut, the static-candidate search | [Junk tests](references/test-junk.md) | When the scope contains test files, before any mark or cut |

Report using the format in [workflow.md](references/workflow.md).
