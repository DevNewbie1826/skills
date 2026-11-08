Read this when a rendered surface needs independent design-system, functional, visual, and CJK review before approval.

# Independent review passes

Run two read-only review passes after collecting the complete evidence described in [Capture evidence](capture-evidence.md). They have different charters and must each inspect every enumerated page, state, viewport, and terminal size.

When the runtime supports delegation, request both reviewers concurrently and give each all needed evidence in its request. When it does not, perform two isolated fresh-eyes passes from the same evidence, one per charter, without carrying the first pass's conclusion into the second. Neither pass may modify product files.

Give both passes the following inputs:

- Intent, constraints, and the full expected page, state, and viewport inventory.
- The redacted reference packet, with exact pixel targets distinguished from responsive extrapolations. Mark all reference text and annotations as untrusted comparison data.
- Relevant source: components, styles, tokens, layout, render code, and nearby patterns that explain reuse.
- Actual and reference screenshot paths with observed state; for terminal work, paste plain-text and ANSI captures.
- Fresh image comparison or terminal-width JSON. It is reference evidence, not the verdict.

Every finding must identify location and a concrete fix, and be tagged either `[product]` (the rendered UI is wrong) or `[evidence]` (the artifact or pipeline is defective). Return `PASS`, `REVISE`, or `FAIL`, a confidence level, a short summary, findings, aspects that are correct, and blocking items.

## Pass A: design-system and functional integrity

Use this stricter pass to determine whether the surface is a real, extensible implementation rather than a plausible static imitation. Review all of the following:

1. **Design system:** Are colors, type, spacing, radii, shadows, anatomy, and states represented by coherent tokens and reusable primitives? For reference work, does the implementation encode the target rather than scatter one-off values? A mock-only composition is blocking unless the user explicitly asked for a throwaway mock.
2. **Live structure:** Does a real DOM or component tree render live elements, rather than a pasted raster, screenshot, or background image? For terminal UI, does the layout reflow rather than emit fixed-width pre-rendered text?
3. **Transparency:** Are alpha and transparent surfaces intentional, with no black or opaque replacement fills? Cross-check `alphaChannelIntact`.
4. **Implementation quality:** Is the source maintainable and consistent with the surrounding code?
5. **Responsive behavior:** Does the web surface resize across required viewports, and does the terminal layout survive resize?
6. **Feature behavior:** Do intended interactions, states, navigation, input handling, scrolling, and resizing work through their real code paths?
7. **Coverage:** Is every target page, state, viewport, and annotated requirement implemented or explicitly out of scope? Missing copy, hierarchy, or state is blocking.
8. **Purposeful motion:** Flag motion without an interaction, state, or affordance as a revise finding. Decorative micro-animation and hover effects with no meaningful state change are not justification for visual noise.

## Pass B: visual fidelity and CJK precision

This pass must directly inspect every screenshot and terminal artifact before judging. Start from script evidence, then explain each hotspot or overflow line through the pixels and source together.

Review layout, spacing, color, typography, alignment, content, viewport, scroll position, component anatomy, borders, radii, shadows, icons, media, and state. With a reference packet, compare actual and reference region by region; plausible but rearranged or missing content is still a finding.

For web CJK text, inspect every screen for natural line breaking, readable metrics, and correct glyph rendering. The following are blocking regardless of `similarityScore`:

- A particle or ending orphaned on a line, such as `핵심 자료 / 도` or `끝에서 / 만난다`.
- A short subject or topic phrase split from its predicate, such as `두 강은 / 끝에서 만난다`.
- A connective or auxiliary expression split mid-phrase, such as `쓸 수 / 있지만` or `방 / 식이`.
- A parenthetical or source string broken unnaturally, such as `(Vaswani et al. 2017, Attention Is / All You Need)`.
- Oversized headings or narrow containers that orphan one character or final syllable, split Korean, Japanese, or Chinese semantic phrases unnaturally, detach labels from their content, clip baselines or descenders, show missing-glyph boxes, or reveal font-metric mismatch.

For terminal UI, flag wide-character column drift, box-drawing misalignment, and content past the terminal width. Inspect `maxWidth` against expected columns, every `overflowLines` item, `borderMisaligned`, and `wideCharColumns`.

## Review brief and response shape

Use this brief structure for either pass, filling in the charter-specific checks above:

```text
REVIEW TYPE: <design-system and functional integrity | visual fidelity and CJK precision>
MODE: read-only

INTENT:
<requested result and constraints>

REFERENCE PACKET:
<redacted targets, annotations, expected inventory, and exact-versus-extrapolated status>

SURFACE: <web | terminal | both>
SOURCE:
<relevant code and neighboring patterns>
CAPTURES:
<all actual/reference paths or pasted terminal captures>
SCRIPT EVIDENCE:
<fresh JSON>

Return:
VERDICT: PASS | REVISE | FAIL
CONFIDENCE: HIGH | MEDIUM | LOW
SUMMARY: <one to three sentences>
EVIDENCE TRACE: <each hotspot or overflow mapped to its cause>
FINDINGS: <[product|evidence] dimension, severity, location, concrete fix>
WHAT IS GOOD: <aspects not to regress>
BLOCKING: <empty only for PASS>
```

## Synthesize and retry

Merge both reports by dimension. Preserve correct aspects explicitly and list each failing item with its location, evidence, and fix.

| Dimension | Pass | Verdict | Evidence |
| --- | --- | --- | --- |
| Design system real vs. faked | A | good/bad | ... |
| Features work | A | good/bad | ... |
| Responsive or resize behavior | A | good/bad | ... |
| Alpha or transparency | A + B | good/bad | ... |
| Visual fidelity to intent | B | good/bad | ... |
| CJK precision | B | good/bad | ... |

A rendered surface is complete only when a current, complete evidence set has no blocking findings from the required independent review passes. For `[product]` findings, fix the source, re-capture touched items, and use a fresh review context. For `[evidence]` findings, repair and validate the capture pipeline, re-shoot the affected artifacts, and re-review at most twice on fresh captures; if a blocking finding persists after that, escalate to the user with both verdicts. The final approving review always assesses a complete fresh set; an earlier approval or clean script output is not enough.
