---
name: visual-qa
description: "Use after building or changing a web, page, component, or terminal UI, or when asked whether it looks right. Covers screenshot and pixel comparison, visual regression, reference fidelity, design-system checks, responsive behavior, CJK clipping, TUI alignment, and box-drawing drift."
---

# Visual QA

Use this skill to verify a rendered surface against stated intent and, when present, a concrete visual reference. Script output focuses review; it never replaces review of the rendered result.

## Route by surface and task

| Situation | Read | Use it for |
| --- | --- | --- |
| Any web, page, terminal UI, or mixed surface | [Capture evidence](references/capture-evidence.md) | Surface inventory, safe reference handling, fresh captures, motion, and bundled evidence |
| A browser screenshot is needed and no project capture path is ready | [Headless browser setup](references/headless-browser-setup.md) | Built-in control, CDP, and Playwright capture options |
| A rendered change needs approval | [Independent review passes](references/independent-review.md) | Separate design-system/functional and visual/CJK reviews, verdicts, and retry rules |
| The task must match a screenshot, design export, or existing site closely | [Reference fidelity](references/reference-fidelity.md) | Mandatory pixel and code-level fidelity checks in addition to normal review |

Skip this skill only when there is no rendered web or terminal surface to inspect.

## Run order

1. Inventory every page, route, state, viewport, scroll position, and terminal size in scope.
2. Capture the complete current surface and any reference at matching conditions.
3. Generate image or terminal evidence with the bundled CLI.
4. Complete the two independent review passes and address findings on fresh captures.
5. For a concrete reference, also complete both checks in [Reference fidelity](references/reference-fidelity.md).

## Browser capability ladder

For web capture, use whatever real-browser driving capability your runtime offers (built-in browser control, a CDP-driven Chromium, Playwright, or equivalent).

- Use built-in browser control when it is available and can reach the required state; otherwise connect to a CDP-driven Chromium.
- If CDP access is unavailable, use Playwright when it is installed or can be used by the project.
- If neither is available, use another real-browser driver already supported by the environment.
- If no real-browser driver is available, record that limitation, retain any nonvisual evidence, and do not claim a screenshot-based visual pass.

## Bundled evidence CLI

`$SKILL_DIR` means this skill's directory. Choose an available runtime rather than requiring a particular one:

| Available runtime | Image comparison | Terminal width check |
| --- | --- | --- |
| Node | `node "$SKILL_DIR/scripts/visual-qa.mjs" image-diff <reference.png> <actual.png>` | `node "$SKILL_DIR/scripts/visual-qa.mjs" tui-check <capture.txt> --cols <N>` |
| Bun | `bun "$SKILL_DIR/scripts/visual-qa.mjs" image-diff <reference.png> <actual.png>` | `bun "$SKILL_DIR/scripts/visual-qa.mjs" tui-check <capture.txt> --cols <N>` |
| TypeScript runner such as tsx | `tsx "$SKILL_DIR/scripts/cli.ts" image-diff <reference.png> <actual.png>` | `tsx "$SKILL_DIR/scripts/cli.ts" tui-check <capture.txt> --cols <N>` |

If one runner is unavailable or cannot execute the source entry point, use another listed runner. If none is available, say that the automated evidence could not be produced; do not invent its result.

## Completion rule

A visual claim is complete only when every in-scope surface has fresh evidence and the required independent review passes have no unresolved blocking findings. A single failing page, state, viewport, or terminal layout keeps the surface incomplete.
