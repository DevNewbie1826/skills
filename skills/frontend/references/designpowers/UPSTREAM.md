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

- motion-choreography — `references/stylegallery/motion/`; reduced-motion alternatives and motion evidence are routed through `lane-b-execution.md`. The timing/easing material in Lane B is a separate salvage from former motion-designer, not a replacement for the motion owner.
- interaction-design — `references/stylegallery/design-engineering/` and `execution/cognitive-accessibility.md` for states, feedback, input preservation, and recovery.
- adaptive-interfaces — `references/stylegallery/platform-guides/` for preference mechanics; `lane-b-execution.md` also preserves the application-level safeguards that choices such as density persist across sessions and users are never asked to justify them (from former adaptive-interfaces).
- responsive-patterns — `references/stylegallery/` patterns, recipes, and guides; `lane-b-execution.md` owns the content-driven breakpoint and content-priority method (from former responsive-patterns), and `references/design/layout-skill.md` owns responsive text and viewport checks.
- ui-composition — `references/stylegallery/` patterns, recipes, and guides; `lane-a-direction.md` owns the foundation prerequisites (from former ui-composition), `lane-b-execution.md` the What/Why/Accessibility decision record (from former ui-composition), `lane-c-review.md` the colour-vision simulation check (from former ui-composition), and `references/design/design-system-architecture.md` the typography readability checks.
- token-architecture — `references/design/design-system-architecture.md` owns global-to-semantic-to-optional-component token layering, the component-to-semantic dependency boundary, and semantic-layer theme remapping (from former token-architecture).
- design-system-alignment — `references/design/design-system-architecture.md` for design-system extraction, component reuse, validation, and maintenance; `references/stylegallery/design-engineering/consumer-migration-readiness.md` for migration and version evidence.
- design-md — `references/design/design-system-architecture.md` owns the untrusted-input boundary, reporting injected instructions, and pausing for the user's source-trust decision (from former design-md); it also keeps project requirements separate from descriptive personal design habits.
- verification-before-shipping — the project's review workflow and `lane-c-review.md` evidence requirements. No separate completion-summary salvage remains; the lane's phase-owner and evidence requirements cover completion reporting.
- writing-design-plans — the project's planning workflow and `lane-a-direction.md` design-aware acceptance criteria. Its former unique planning items were found covered, with no separate salvage.
- inspiration-scouting — `lane-a-direction.md` owns the annotated 5–8-reference board, cross-domain wild card and lookup table, accessibility caution, and take/leave notes (from former inspiration-scouting and its scout role).

The ten role-reference files from the retired agents directory were removed with the vendor tree; their perspectives survive as capability language inside the merged leaves and lane guidance, not as installed roles or runtimes.

## Salvage record

- In `references/design/design-system-architecture.md`:
  - Untrusted `DESIGN.md` input is treated as data, injected instructions are ignored and reported, and the user is asked to decide whether to trust the source (from former design-md).
  - Project requirements remain distinct from descriptive observations about personal design habits (from former design-md).
  - Global tokens feed semantic tokens, optional component tokens depend on semantic tokens rather than globals, and themes remap at the semantic layer (from former token-architecture).
  - Typography checks cover paragraph spacing, avoiding justified body prose, distinct `I/l/1` and `O/0` glyphs, and matching-class fallbacks (from former ui-composition).
- In `references/design/layout-skill.md`: responsive body-text size and measure, 200-percent zoom, breakpoint-edge, landscape-phone, and real-device checks (from former responsive-patterns).
- In `lane-a-direction.md`: the visual-foundation prerequisites (from former ui-composition); an annotated 5–8-reference board, cross-domain lookup and wild card, take/leave notes, and accessibility caution (from former inspiration-scouting and its scout role); and the four-part testable design-principle shape (from former design-strategist).
- In `direction/research-planning.md`: optional competitive UX/accessibility assessment with evidence-versus-speculation labels and project implications, a findability probe for proposed navigation, and stage-level journey-map fields when a map is made (from former design-scout and design-strategist).
- In `lane-b-execution.md`: content-driven breakpoints and content-priority dispositions (from former responsive-patterns); the What/Why/Accessibility decision record (from former ui-composition); persistent, non-judgmental application preferences (from former adaptive-interfaces); reduced-motion alternatives that may reduce, remove, or substitute motion while preserving equivalent feedback (from former adaptive-interfaces, aligned to the StyleGallery motion owner); motion duration/easing and never-animate guidance (from former motion-designer); and error structure, reading target, and time-sensitive-copy rule (from former content-writer).
- In `execution/accessible-content.md`: empty states explain what belongs there, why it is empty, and what to do next, distinguishing first use from filtered/no-result states (from former content-writer).
- In `lane-c-review.md`: colour-vision simulation checks (from former ui-composition) and the URL Discovery Protocol, including resolving hrefs against the effective document base URL (from former heuristic-evaluator).
- The process audit found no unique salvage from verification-before-shipping or writing-design-plans. It also removed an interim completion-summary block; completion evidence remains owned by `lane-c-review.md`'s phase-owner and evidence requirements. The design-review and design-builder role files contributed no unique material.

## Excluded integration surfaces

Bridge, state, router, scheduler, and runtime-integration materials remain intentionally excluded. The bundled corpus must not introduce hooks, scripts, background automation, shared host state, or a competing frontend workflow.
