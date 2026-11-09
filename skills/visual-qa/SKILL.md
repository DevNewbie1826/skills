---
name: visual-qa
description: "Use to verify a rendered surface against stated intent, a platform-baseline checklist, or a concrete visual reference - not to build or style the UI (that is the frontend skill). Covers web, terminal, and paginated-document surfaces: screenshot and pixel comparison, visual regression, before/after pairs, reference fidelity, design-system checks, responsive behavior, light/dark pairs, reduced motion, CJK clipping, TUI alignment, and box-drawing drift. Triggers: compare screenshot to mockup or design, does it match, does this look right, visual regression, screenshot diff, pixel diff, before and after, responsive check, mobile layout, breakpoint check, dark mode check, CJK clipping, TUI alignment, PDF page layout."
---

# Visual QA

Verify a rendered surface against its brief, the platform baseline, and, when one exists, a concrete reference: objective script evidence plus two independent read-only review passes, merged into one verdict with a row per item inside a bounded review budget. Script numbers aim the reviewers; they are never the verdict. Run it after you build or change any UI and before calling it done; skip it only when there is no rendered web, terminal, or paginated surface to inspect.

## Route by surface and task

| Situation | Read | Use it for |
| --- | --- | --- |
| Any web, terminal, paginated, or mixed surface | [Capture evidence](references/capture-evidence.md) | Surface inventory, safe reference handling, coverage, fresh and valid captures, the viewport and theme matrix, motion, bundled evidence |
| A browser screenshot is needed and no project capture path is ready | [Headless browser setup](references/headless-browser-setup.md) | Driver ladder (built-in browser control, headless CLI, CDP, Playwright, equivalent), matrix loop, teardown |
| Judging what the captures show, or briefing a reviewer | [Checklist](references/checklist.md) | The platform-baseline items A1-J2, each rated PASS, FAIL, or N/A and proven by a named capture |
| A rendered change needs approval | [Independent review passes](references/independent-review.md) | The two charters, the reviewer brief, defect/taste tags, the round budget, the verdict report |
| An existing UI is being changed | [Before/after mode](references/before-after.md) | Fixed case list, `before` captured ahead of the first edit, composed pairs |
| The task must match a screenshot, design export, or existing site closely | [Reference fidelity](references/reference-fidelity.md) | Mandatory pixel and code-level checks in addition to normal review |

## Run order

1. Classify the surface and write the complete inventory ([Capture evidence](references/capture-evidence.md) defines it); a change to an existing UI starts [Before/after mode](references/before-after.md) before the first edit.
2. Capture the whole inventory fresh, after the last edit, plus any reference at matching conditions, and validate every capture before a reviewer sees it.
3. Compare image and terminal captures with the bundled CLI below, then walk the [checklist](references/checklist.md) yourself and fix what you can.
4. Run both independent review passes with all evidence pasted in, merge them into one verdict report, and fix every `[defect]` on fresh captures; [Independent review passes](references/independent-review.md) owns the budget, the re-review rules, and the NEEDS HUMAN REVIEW outcome.

## Bundled evidence CLI

`$SKILL_DIR` means this skill's directory. Choose an available runtime rather than requiring a particular one:

| Available runtime | Image comparison | Terminal width check |
| --- | --- | --- |
| Node | `node "$SKILL_DIR/scripts/visual-qa.mjs" image-diff <reference.png> <actual.png>` | `node "$SKILL_DIR/scripts/visual-qa.mjs" tui-check <capture.txt> --cols <N>` |
| Bun | `bun "$SKILL_DIR/scripts/visual-qa.mjs" image-diff <reference.png> <actual.png>` | `bun "$SKILL_DIR/scripts/visual-qa.mjs" tui-check <capture.txt> --cols <N>` |
| TypeScript runner such as tsx | `tsx "$SKILL_DIR/scripts/cli.ts" image-diff <reference.png> <actual.png>` | `tsx "$SKILL_DIR/scripts/cli.ts" tui-check <capture.txt> --cols <N>` |

`visual-qa.mjs` is generated from `cli.ts` and its modules and is never hand-edited; a behavior fix lands in the TypeScript source.

## Completion rule

A visual claim is complete only when every in-scope surface has fresh evidence and the required independent review passes have no unresolved blocking findings. When the review budget is spent with a `[defect]` still open, report NEEDS HUMAN REVIEW; never self-certify a silent PASS.
