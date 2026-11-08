---
name: frontend
description: "Use for frontend, web UI, UX, visual design, styling, layout, animation, mockups, performance, accessibility, or SEO work, and for any HTML/CSS/SVG artifact rendered to a PDF, print page, report, figure, diagram, or slide. Routes design references, a ground-brief-build-subtract-verify flow, a draft-guard lint, real-browser audits, UI/UX lookups, design operating guidance, and a visual/copy AI-slop taxonomy with a scanner for de-slop audits and pre-ship scans; includes optional framework-specific lanes such as React tooling. Also triggers on: kill AI slop, de-slop, remove the AI look, looks AI-generated, templated, print stylesheet, paged media."
---

# Frontend

This file is a router, not a rulebook. Load the smallest set of references that covers the request, state which you loaded, then execute under their guidance. The bar is restraint with a visible hierarchy: one primary action, the important thing first, nothing on screen without a job. A quiet, correct screen that holds its hierarchy at 375, 768, and 1280 CSS px in both themes is a finish; atmosphere, motion, and award-grade surface work are built when the brief asks (a named brand, "premium", a marketing page), never by default for an internal tool, dashboard, report, or figure. For implementation work, load design and perfection together.

## Flow

ground -> brief -> build -> subtract -> verify. Name the references the request routes to, with one reason each, before the first edit; rows below stack, and a reference you named but never opened is a gap you still owe.

1. **Ground** a new screen, redesign, or design-system change: [`design/grounding.md`](references/design/grounding.md) (guideline source, ideal state, gap ledger). Skip for a small change.
2. **Brief** every screen you build or change: [`design/brief-and-subtract.md`](references/design/brief-and-subtract.md) (primary action, priorities, left-out-on-purpose, required content, `Layout:` line, before captures).
3. **Build** under [`perfection/build-rules.md`](references/perfection/build-rules.md) and [`perfection/craft-floor.md`](references/perfection/craft-floor.md); keep the draft-guard tells out of the first draft and run the lint (Commands below).
4. **Subtract**: delete what has no job, then confirm the required-content list is intact (same file as the brief).
5. **Verify** with `visual-qa`, then state the WCAG 2.2 AA result per [`perfection/wcag-gate.md`](references/perfection/wcag-gate.md).

## Task -> Read

| Task | Read |
|---|---|
| Any UI implementation, styling, redesign, mockup, or visual decision | [`design/README.md`](references/design/README.md). It owns the design-system gate and routes Layer B brand references and framework-matched tooling. |
| Greenfield work | [`design/README.md#greenfield-workflow`](references/design/README.md#greenfield-workflow) before UI work; it owns research, `DESIGN.md`, and the Primitive Showcase Gate. |
| Existing project that already has `DESIGN.md` or a component system | Read and follow it; update it only for a needed token, primitive, state, motion rule, accessibility constraint, accepted debt, or fidelity requirement |
| Existing UI with neither `DESIGN.md` nor a component system | For a new screen or flow: ask whether to preserve the current look with local styling or first extract a design system ([`design/design-system-architecture.md`](references/design/design-system-architecture.md)); do not silently choose. A small change (fix, new control, restyled component, copy or spacing change) with a styled sibling to copy needs no extraction and no question: see the small-change rule in [`design/README.md`](references/design/README.md) |
| No `DESIGN.md`, or extracting a system from existing UI | [`design/design-system-architecture.md`](references/design/design-system-architecture.md) |
| A concrete visual reference (screenshot, mockup, Figma export) as the contract, or generating/analyzing a visual direction before implementing it | [`design/image-to-code-skill.md`](references/design/image-to-code-skill.md); extract tokens, geometry, states, motion into `DESIGN.md`. For image-only concepts (no code): [`design/image-gen-concepts-web.md`](references/design/image-gen-concepts-web.md) or the mobile/brandkit variants. |
| A live URL as the contract | [`design/clone-from-url.md`](references/design/clone-from-url.md) |
| Landing page, portfolio, or redesign needing visual direction with no narrower named style | [`design/taste-skill.md`](references/design/taste-skill.md) as the fallback. If the request names a style (cinematic, minimalist, brutalist, soft), use that row instead, not both. Not dashboards or multi-step product UI. |
| Expressive cinematic, high-variance, scroll-led marketing surface | [`design/cinematic-taste-skill.md`](references/design/cinematic-taste-skill.md) |
| Minimal, clean, editorial, restrained work | [`design/minimalist-skill.md`](references/design/minimalist-skill.md) |
| Brutalist, raw, Swiss, experimental, anti-design | [`design/brutalist-skill.md`](references/design/brutalist-skill.md) |
| Premium, luxury, calm, elegant, glassy product surfaces | [`design/soft-skill.md`](references/design/soft-skill.md) |
| Improving existing UI | [`design/redesign-skill.md`](references/design/redesign-skill.md); audit first, never greenfield |
| Completing an unfinished implementation | [`design/output-skill.md`](references/design/output-skill.md), stacked on a style skill |
| Exporting a portable `DESIGN.md` specification | [`design/mockup-export-skill.md`](references/design/mockup-export-skill.md), stacked on a style skill; worked example: [`design/mockup-export-example.md`](references/design/mockup-export-example.md) |
| Image-only mockups, screen concepts, identity boards (no code) | [`design/image-gen-concepts-web.md`](references/design/image-gen-concepts-web.md) / [`image-gen-concepts-mobile.md`](references/design/image-gen-concepts-mobile.md) / [`image-gen-brandkit.md`](references/design/image-gen-brandkit.md) |
| Layer B brand reference for a named brand or site | [`design/_INDEX.md`](references/design/_INDEX.md) for the catalog and mood shortcuts; apply extracted principles, never copy logos or assets |
| Shipped-product research | [`design/lazyweb.md`](references/design/lazyweb.md) when available, plus the [`design/_INDEX.md`](references/design/_INDEX.md) shortlist |
| Layout mechanics: dashboards, settings, inboxes, split panes, app shells, scroll ownership | [`design/layout-skill.md`](references/design/layout-skill.md) plus the concrete pattern catalog below |
| Spatial pattern lookup: centering, stacking, sidebars, grids, overlays | [`stylegallery/layout/index.md`](references/stylegallery/layout/index.md) and [`stylegallery/CATALOG.md`](references/stylegallery/CATALOG.md); category indexes via [`stylegallery/patterns/index.md`](references/stylegallery/patterns/index.md) |
| Whole-screen composition: homepage, dashboard, settings flow, article, list-detail, form, command surface | [`stylegallery/recipes/index.md`](references/stylegallery/recipes/index.md) |
| Naming, reviewing, or specifying product motion | [`stylegallery/motion/index.md`](references/stylegallery/motion/index.md) |
| Verifying product-layer craft decisions or interaction evidence | [`stylegallery/design-engineering/index.md`](references/stylegallery/design-engineering/index.md) |
| Comparing design terms across named design systems | [`stylegallery/design-terminology/index.md`](references/stylegallery/design-terminology/index.md) |
| Domain map of all StyleGallery areas | [`stylegallery/index.md`](references/stylegallery/index.md); synced revision and resync procedure: [`stylegallery/UPSTREAM.md`](references/stylegallery/UPSTREAM.md) |
| Frontend code, performance, SEO, accessibility, or quality auditing | [`perfection/README.md`](references/perfection/README.md); build for production, then run the lighthouse audit (Commands below). Any code change also takes [`perfection/build-rules.md`](references/perfection/build-rules.md) and [`perfection/craft-floor.md`](references/perfection/craft-floor.md). |
| A new screen or flow, a redesign, or design-system creation or rework | [`design/grounding.md`](references/design/grounding.md), then the brief in [`design/brief-and-subtract.md`](references/design/brief-and-subtract.md) |
| Any screen you build or change (small changes included) | [`design/brief-and-subtract.md`](references/design/brief-and-subtract.md): brief, draft guard, subtract, scoped fix passes |
| Finishing a UI or design-system deliverable | [`perfection/wcag-gate.md`](references/perfection/wcag-gate.md): the PASS/FAIL table for the hand-off |
| Paged output: a PDF report, print stylesheet, headless print pipeline, a deck printed to paper, "why is this page half empty" | [`design/print-paged-media.md`](references/design/print-paged-media.md) |
| Interaction or motion: micro-interactions, transitions, gestures, hover/press/state feedback | [`design/interaction-skill.md`](references/design/interaction-skill.md); for motion naming and review see also [`stylegallery/motion/index.md`](references/stylegallery/motion/index.md) |
| Ambience, only when the brief asks: animated, shader, particle, or grid backgrounds, typographic reveals, scroll storytelling, spotlight or tilt cards | [`design/ambience-skill.md`](references/design/ambience-skill.md) |
| Tone outside both anchors (AI-agent UI, charts, landing sections, a brutalist or utility-class-only build) or no nearest interaction/ambience pattern | [`design/component-catalogs.md`](references/design/component-catalogs.md): which catalog per tone, exploration procedure, licence gates |
| Concrete style, palette, font pairing, chart, UX guideline, or generated design system lookup | [`ui-ux-db/README.md`](references/ui-ux-db/README.md); a lookup tool, not a visual-direction substitute. Search CLI: Commands below. |
| Creating or updating `DESIGN.md`, or any implementation/redesign needing personas, critique, debt, or handoff | Load the applicable lane(s) below. |
| Personas, discovery, research, voice (planning) | [`designpowers/lane-a-direction.md`](references/designpowers/lane-a-direction.md) |
| Accessible content, cognitive accessibility, taste checkpoints (building) | [`designpowers/lane-b-execution.md`](references/designpowers/lane-b-execution.md) |
| Critique, heuristics, persona and usability testing (reviewing) | [`designpowers/lane-c-review.md`](references/designpowers/lane-c-review.md) |
| Design debt, handoff, retrospective (records) | [`designpowers/lane-d-memory.md`](references/designpowers/lane-d-memory.md); [`designpowers/README.md`](references/designpowers/README.md) is the optional overview |
| De-slop request ("looks AI-generated", "remove the AI look"), or any build approaching done | [`deslop/README.md`](references/deslop/README.md): audit mode (scope, scan, triage, report, fix; never mass-edit before the user sees the report), creation-time checklist, pre-ship scan. Tells: [`deslop/taxonomy.md`](references/deslop/taxonomy.md); grep patterns and false positives: [`deslop/detection.md`](references/deslop/detection.md); before/after patches: [`deslop/fixes.md`](references/deslop/fixes.md). |
| Optional: stack is React, want React-specific dev tooling | [`design/react-dev-tooling-skill.md`](references/design/react-dev-tooling-skill.md); for other stacks use comparable tooling |
| Optional: stack is React, component-level render diagnosis | [`perfection/react-perf-tooling.md`](references/perfection/react-perf-tooling.md) |
| Optional: game HUD, menu, inventory, or other game interface | [`stylegallery/game-ui/index.md`](references/stylegallery/game-ui/index.md) for engine-neutral hierarchy and named-engine guidance |
| Optional: bounded platform-convention comparison before web adaptation | [`stylegallery/platform-guides/index.md`](references/stylegallery/platform-guides/index.md) |
| Driving a browser for design QA | A browser-driving capability |
| Visual QA of final screens | `visual-qa` in reference-fidelity mode at 375, 768, and 1280px with states and motion exercised |
| Code-level AI slop (comments, dead code, over-defensive code) | `remove-ai-slops`; `deslop` here covers visual and copy slop only |
| Pure logic work with no visual surface | `programming` alone |
| No suitable brand/style in the catalog | A larger local design library if available; otherwise the closest Layer A reference plus project research |

## Shared axioms

- **No design system, no UI work.** `DESIGN.md` exists before components; color, type, and spacing trace to tokens. Exception: a small change copies the nearest styled sibling ([`design/README.md`](references/design/README.md), small-change rule).
- **Concrete reference means contract.** Match its pixels, copy, component structure, and responsive intent unless the user approves a deviation.
- **Do not weaken UX to buy a score.** Preserve meaningful motion, content, and interaction while fixing architecture and assets.
- **No emoji icons.** Use accessible SVG icon sets.
- **Use composited animation for new code.** Prefer composited properties (`transform`, `opacity`, `filter`); review-level edge cases follow [`stylegallery/motion/`](references/stylegallery/motion/).
- **Motion serves meaning.** Every animation or hover maps to an interaction, state change, or affordance.
- **Done requires evidence.** Run `visual-qa` at 375, 768, and 1280px with states and motion exercised, then complete two independent review passes on fresh evidence, and state the WCAG 2.2 AA table ([`perfection/wcag-gate.md`](references/perfection/wcag-gate.md)).
- **Keep tells out of the first draft.** The draft-guard list in [`design/brief-and-subtract.md`](references/design/brief-and-subtract.md) (one-side colour bars, accent outlines on rounded cards, decorative badges, invented proof, promotional copy) is applied while writing, not found afterwards.
- **No machine-default tells.** New UI ships free of the 34 AI-slop tells in [`deslop/taxonomy.md`](references/deslop/taxonomy.md). Run the deslop scanner over changed source and triage every hit before the evidence gate; a defended, intentional choice documented in `DESIGN.md` is not slop.

## Commands

Run from the skill directory (`$SKILL_DIR`); full flags live in each owning README.

```bash
bun $SKILL_DIR/scripts/perfection/check-draft-guard.ts <changed files or dirs>   # exit 1 = a first-draft tell; design/brief-and-subtract.md
bun $SKILL_DIR/scripts/perfection/check-accent-stripes.ts <changed files or dirs>   # stripe and accent-outline rules only
python3 $SKILL_DIR/scripts/perfection/lighthouse-audit.py https://localhost:3000   # perfection/README.md; run mobile + desktop presets
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --design-system -p "Project"   # guide/usage.md
node $SKILL_DIR/references/deslop/scripts/scan.mjs <root> [--json] [--only=01,06] [--exclude=legacy]   # deslop/README.md
```
