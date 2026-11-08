Read this when the task asks to closely reproduce a concrete screenshot, design export, page, or visual reference packet.

# Reference fidelity

Run this procedure in addition to the capture and independent review process. It applies to requests such as rebuilding a screen, matching an existing page, or reproducing a supplied visual target. Normal visual review alone is not sufficient for a concrete reference.

## Required evidence

Enumerate every reference page, viewport, state, scroll position, and annotation. Capture each actual counterpart under identical conditions and use the bundled image comparison from [the skill router](../SKILL.md#bundled-evidence-cli):

```sh
node "$SKILL_DIR/scripts/visual-qa.mjs" image-diff <reference.png> <actual.png>
```

Use a different available runner when Node is unavailable. Treat a missing runner as an evidence limitation, not a passing result. The comparison result directs attention to differences but does not establish fidelity by itself.

## Required check 1: pixel and content comparison

Use a read-only reviewer to crop and zoom matching regions of both reference and actual captures. It must inspect them region by region, not at a glance:

- page bounds, header, navigation, hero, cards, grids, charts, media, and overlays;
- geometry, spacing, alignment, type ramp, colors, borders, radii, shadows, and icon sizes;
- rendered copy and DOM text against overview text and annotations; and
- each changed state, viewport, and responsive extrapolation.

The reviewer must consume `dimensionsMatch`, `diffRatio`, `similarityScore`, `alphaChannelIntact`, and every hotspot. Anything beyond unavoidable rasterization or rounding is a finding, with a capture region and concrete fix.

## Required check 2: code-level design-system fidelity

Use a separate read-only reviewer to inspect the source, relevant change set, reference artifacts, and evidence. It must determine whether:

1. Live, reusable components and state variants render the UI rather than a pasted screenshot, raster image, or background image standing in for elements.
2. Tokens or reusable primitives drive colors, spacing, typography, and component anatomy rather than scattered one-off values.
3. The DOM or terminal layout hierarchy matches the target's layer and layout structure.
4. The rendered design, content, and behavior match the reference.

Require this response shape:

```text
RECOMMENDATION: APPROVE | REQUEST_CHANGES
BLOCKERS: <file or capture locations and concrete gaps; empty only for APPROVE>
EVIDENCE REVIEWED: <artifacts inspected>
```

## Completion loop

Both checks must approve the same current revision and complete fresh evidence set. If either requests changes, fix the product gap, re-capture all affected items, and re-run both checks at most twice; a third mismatch stops the task with the fidelity gap reported. Do not declare fidelity complete from a visual-only pass, a code-only pass, an old approval, or a high similarity score.

When delegated reviewers are unavailable, perform the pixel/content and code-level checks as separate fresh-eyes review contexts with their own evidence traces. State that limitation plainly in the final report.
