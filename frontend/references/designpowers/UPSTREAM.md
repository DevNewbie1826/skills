# Designpowers Reference Manifest

Read this when auditing where the designpowers corpus came from, what was kept, and what was removed or merged, and why.

## Source

The corpus originates from a third-party design-operating collection ("designpowers") adapted for this self-contained frontend skill, distributed under the MIT License — see [LICENSE](LICENSE) (Copyright (c) 2026 MC Dean). It is reference material only: the source collection is not required at runtime, and nothing here introduces hooks, scripts, schedulers, shared host state, or a competing frontend workflow.

## Retained verbatim (moved out of the retired vendor tree)

- `direction/` — inclusive-personas, research-planning, design-debate, voice-and-tone
- `execution/` — accessible-content, cognitive-accessibility, taste-feedback
- `review/` — synthetic-user-testing, usability-testing
- `memory/` — design-debt-tracker, design-handoff

Each moved leaf keeps its upstream content verbatim except the opening routing cue (a specific read-when line), an added back-link to its lane file, and link adjustments.

## Merged (per the review-consolidation audit)

- `review/design-review.md` — former design-review + designpowers-critique: one entry for evaluating existing or built work, three evaluation perspectives (craft and intent, accessibility, usability), a single consolidated report, and one next-step flow. Duplicated parallel-dispatch scaffolding and runtime mechanics were dropped in favor of capability language.
- `review/heuristic-evaluation.md` — former heuristic-evaluation, made self-contained: Nielsen H1–H10 with evidence, the four-question cognitive walkthrough, error-path analysis, the H1/H3 structural-issue pause safeguard, and fix-round handling. Pipeline enforcement language was removed; the method is offered, not mandated.
- `memory/design-retrospective.md` — former design-retrospective + taste-report: project-level reflection plus the longitudinal, personal-layer taste synthesis (three-project threshold, report contents, editorial rules, contamination check). Duplicated prompts and framing were consolidated.

## Removed as duplicated elsewhere

Removed after overlap audits against the StyleGallery mirror and the `design/` references; the guidance is owned by:

- motion-choreography, interaction-design, adaptive-interfaces — `references/stylegallery/` motion, design-engineering, and platform-guides domains
- responsive-patterns, ui-composition — `references/stylegallery/` patterns, recipes, and guides plus `references/design/layout-skill.md`
- token-architecture, design-system-alignment, design-md — `references/design/design-system-architecture.md`
- verification-before-shipping — the project's review workflow plus Lane C's evidence requirements (a completion-summary salvage was kept in `lane-c-review.md`)
- writing-design-plans — the project's planning workflow plus Lane A's design-aware acceptance criteria
- inspiration-scouting — Lane A planning context (a reference-curation salvage was kept in `lane-a-direction.md`)

The ten role-reference files from the retired agents directory were removed with the vendor tree; their perspectives survive as capability language inside the merged leaves and lane guidance, not as installed roles or runtimes.

## Salvage record

- Into `references/design/design-system-architecture.md` and `references/design/layout-skill.md`: the audited unique items from design-md and responsive-patterns were applied by the design-area maintenance pass (recorded in its salvage ledger).
- Into designpowers lane files, each marked "from former <doc>": the breakpoint and content-priority method and the What/Why/Accessibility decision record (Lane B, layout audit); the visual-foundation prerequisite trio (Lane A, layout audit); the colour-vision simulation test (Lane C, layout audit). Per the process audit: the cross-domain lookup table, the "cautionary tale" accessibility flag, and the 5–8-reference board cap with a cross-domain wild card (Lane A, from inspiration-scouting and its scout role); the testable design-principle shape (Lane A, from the design-strategist role); the three-part error structure, Grade 6–8 reading target, and time-sensitive-copy rule (Lane B, from the content-writer role); the duration/easing/not-to-animate motion numbers (Lane B, from the motion-designer role); the URL Discovery Protocol (Lane C, from the heuristic-evaluator role). The process audit found no unique salvage in verification-before-shipping or writing-design-plans; the design-review and design-builder role files contributed nothing unique.
- Not inserted: two audited unique lines from adaptive-interfaces (persist the user's preference choice across sessions; never require users to justify a preference). Their audited destination is `references/stylegallery/platform-guides/preferences-and-accessibility.md`, but the StyleGallery mirror is upstream-owned and is not edited locally; the upstream sync owner decides their insertion.

## Excluded integration surfaces

Bridge, state, router, scheduler, and runtime-integration materials remain intentionally excluded. The bundled corpus must not introduce hooks, scripts, background automation, shared host state, or a competing frontend workflow.
