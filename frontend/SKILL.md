---
name: frontend
description: "Use for frontend, web UI, UX, visual design, styling, layout, animation, mockups, performance, accessibility, or SEO work. Routes design references, real-browser audits, UI/UX lookups, design operating guidance, and a visual/copy AI-slop taxonomy with a scanner for de-slop audits and pre-ship scans; includes optional framework-specific lanes such as React tooling. Also triggers on: kill AI slop, de-slop, remove the AI look, looks AI-generated, templated."
---

# Frontend

This file is a router, not a rulebook. Load the smallest set of references that covers the request, state which you loaded, then execute under their guidance. The bar is a coherent, distinctive, accessible surface with a production-quality implementation - not merely clean code or a passing build.

## Route before UI work

| Request involves... | Read |
|---|---|
| Any UI implementation, styling, redesign, mockup, or visual decision | `references/design/README.md` first. It routes the design-system gate, taste and brand references, and framework-matched development tooling. |
| Frontend code, performance, SEO, accessibility, or quality auditing | Also `references/perfection/README.md` for real-browser audits and root-cause remediation. |
| A concrete style, palette, font pairing, chart, landing structure, UX guideline, or generated project design system | `references/ui-ux-db/README.md` on demand. It is a lookup tool, not a visual-direction substitute. |
| An implementation or redesign that creates or updates `DESIGN.md`, or needs personas, critique, debt, handoff, or synthetic testing | `references/designpowers/README.md` and `lane-c-review.md`; load other lanes only for their applicable phase. |
| A de-slop request ("looks AI-generated", "remove the AI look", feels templated), or any build/redesign approaching done | `references/deslop/README.md`. A 34-tell visual and copy AI-slop taxonomy with a dependency-free scanner: audit workflow for explicit requests, a creation-time checklist during builds, and a final scan before the visual-evidence gate. |

For implementation work, load design and perfection together. A fast page that looks generic, or a beautiful page with an avoidable performance cost, has not met the bar.

## Design-system and component workflow

Choose a branch before changing UI code:

1. **Concrete visual reference** - treat a supplied screenshot, generated mockup, design-mockup export, Figma export, live site, or annotated packet as the contract. For static material load `design/image-to-code-skill.md`; for a live URL load `design/clone-from-url.md`. Extract tokens, geometry, states, motion, and responsive intent into `DESIGN.md`, then build reusable primitives. Run `visual-qa` in reference-fidelity mode afterward.
2. **Greenfield** - follow the [greenfield workflow](references/design/README.md#greenfield-workflow) before UI work; it owns research, `DESIGN.md`, and the Primitive Showcase Gate.
3. **Existing project with `DESIGN.md` or a component system** - read and follow it; update it only for a needed token, primitive, state, motion rule, accessibility constraint, accepted debt, or fidelity requirement.
4. **Existing UI with neither** - ask whether to preserve the existing look with local styling or first extract a real design system and reusable components. Do not silently choose.

For work that updates `DESIGN.md`, use designpowers to incorporate personas, accessibility, critique, debt, and handoff guidance. Verify final screens with real visual evidence and pass significant work through your review workflow.

## Ruleset 1 - design (`references/design/`)

Most non-trivial tasks load one Layer A style skill plus one Layer B brand reference. `README.md` has the full routing flow; `_INDEX.md` has the complete catalog and mood shortcuts.

### Layer 0 - architecture

| File | Read when |
|---|---|
| `design-system-architecture.md` | No `DESIGN.md` exists, or you are extracting a system from existing UI. |

### Layer A - taste and output skills

| File | Read when |
|---|---|
| `taste-skill.md` | Landing pages, portfolios, or redesigns that need deliberate visual direction without a narrow named style. Not dashboards, data tables, or multi-step product UI. |
| `cinematic-taste-skill.md` | An expressive marketing or landing surface: cinematic, high-variance, magnetic, or scroll-led. |
| `minimalist-skill.md` | Minimal, clean, editorial, or intentionally restrained work. |
| `brutalist-skill.md` | Brutalist, raw, Swiss, experimental, or anti-design work. |
| `soft-skill.md` | Premium, luxury, calm, elegant, glassy, or high-craft product surfaces. |
| `redesign-skill.md` | Improving existing UI; audit first rather than using it for greenfield work. |
| `image-to-code-skill.md` | Generate or analyze a visual direction before implementing it. |
| `output-skill.md` | Complete an unfinished implementation; it stacks on a style skill. |
| `mockup-export-skill.md` | Export a portable `DESIGN.md` design specification; it stacks on a style skill. |
| `image-gen-concepts-web.md` / `image-gen-concepts-mobile.md` / `image-gen-brandkit.md` | Image-only mockups, screen concepts, or identity boards. They do not write code. |
| `layout-skill.md` | Dashboards, settings, inboxes, split panes, app shells, scroll ownership, or content-stress layout problems. `layout-skill.md` owns mechanics; `layout-patterns/` is the concrete catalog. |

### Pattern catalog & recipes

| File | Read when |
|---|---|
| [`layout-patterns/CATALOG.md`](references/design/layout-patterns/CATALOG.md) | You need a concrete spatial pattern lookup for centering, stacking, sidebars/splits, grids, overlays, or scroll/shell problems. |
| [`layout-recipes/index.md`](references/design/layout-recipes/index.md) | You need a whole-screen composition built from patterns, such as a homepage, dashboard, settings flow, article, list-detail view, form flow, or command surface. |

### Product-layer motion & craft

| File | Read when |
|---|---|
| [`motion/index.md`](references/design/motion/index.md) | Naming, reviewing, or specifying product motion. It provides vocabulary and a review procedure; the shared motion axioms remain the law. |
| [`design-engineering/index.md`](references/design/design-engineering/index.md) | Verifying product-layer craft decisions, interaction details, or their evidence. |

### Optional React lane

| File | Read when |
|---|---|
| `react-dev-tooling-skill.md` | The stack is React and you want optional React-specific inspection and render tooling. For other stacks, use comparable development tooling when available. |

Layer B references supply visual tokens for named brands or sites. Apply their extracted principles to the project's own content; do not copy logos or proprietary assets. If the catalog has no fit, use a larger local design library if available, or select the closest Layer A mood direction.

## Ruleset 2 - perfection (`references/perfection/`)

| File | Read when |
|---|---|
| `README.md` | Frontend code is written or audited; it covers real-browser performance, accessibility, SEO, and design-system compliance. |
| `react-perf-tooling.md` | The stack is React and component-level render diagnosis is useful. This is an optional React-specific lane. |

Build for production before measuring. From the skill directory, run the bundled audit with Python; another compatible dependency runner is also acceptable:

```bash
python3 $SKILL_DIR/scripts/perfection/lighthouse-audit.py https://localhost:3000
```

Run mobile and desktop presets, repeat enough times to establish a reliable result, and diagnose from the JSON report.

## Ruleset 3 - ui-ux-db (`references/ui-ux-db/`)

Run its self-contained CLI from the skill directory or through `$SKILL_DIR`:

```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --design-system -p "Project"
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --domain <domain>
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --stack <stack>
```

Domains and stacks are enumerated in its README; choose the stack matching the project rather than assuming one framework.

## Ruleset 4 - designpowers (`references/designpowers/`)

Use this internal reference for design operating guidance. It complements frontend routing and can inform planning, implementation, visual evidence, independent critique, design debt, and handoff; it does not create a separate runtime or workflow.

## Ruleset 5 - deslop (`references/deslop/`)

`README.md` documents the three uses: audit mode for explicit de-slop requests (scope, scan, triage, report, fix; never mass-edit before the user sees the report), a creation-time checklist, and the final pre-ship scan. The 34 tells (indigo-to-violet gradients, gradient-clip headlines, kickers over every heading, invented stat rows, stock font pairings, and 29 more) live in `taxonomy.md`; grep patterns and false positives in `detection.md`; before-and-after patches in `fixes.md`. The core discipline: slop is the absence of a decision - triage every hit as slop vs. intentional before touching code, and prefer fixing shared tokens or `DESIGN.md` over every call site. Distinct from the `remove-ai-slops` skill, which removes code-level slop (comments, dead code, over-defensive code); deslop judges what the user sees and reads.

Scanner (pure Node, no dependencies, never edits files):

```bash
node $SKILL_DIR/references/deslop/scripts/scan.mjs <root>          # human-readable report
node $SKILL_DIR/references/deslop/scripts/scan.mjs <root> --json   # machine-readable, for triage
```

Narrow with `--only=01,06` / `--skip=19` / `--exclude=legacy`; extend with `--rules=extra.mjs` for project- or language-specific tells. Defended hits are pinned in source with `deslop-ignore` / `deslop-ignore-next-line 06` / `deslop-ignore-file` comments.

## Quick routes

| Request | Load |
|---|---|
| Landing page with no direction | `design/README.md` + `design/_INDEX.md` shortlist + one Layer B reference + `design/taste-skill.md` + `perfection/README.md` |
| Named brand or site | `design/README.md` + the matching Layer B reference + an appropriate Layer A style skill + `perfection/README.md` |
| Improve an existing dashboard | `design/README.md` + `design/redesign-skill.md` + `perfection/README.md` |
| Layout breaks with real content | [`design/layout-skill.md`](references/design/layout-skill.md) + [`design/layout-patterns/CATALOG.md`](references/design/layout-patterns/CATALOG.md) |
| Review or standardize motion | [`design/motion/index.md`](references/design/motion/index.md) |
| Reproduce a screenshot or generated mockup | `design/README.md` + `design/image-to-code-skill.md` + `perfection/README.md` + `visual-qa` reference-fidelity mode |
| Audit or speed up a site | `perfection/README.md` (+ `perfection/react-perf-tooling.md` for the optional React lane) |
| Image-only mobile mockup | `design/image-gen-concepts-mobile.md` (+ a Layer B reference if named) |
| Palette, fonts, or UX guidance | `ui-ux-db/README.md` then its search CLI |
| Shipped-product research | `design/lazyweb.md` when available + `design/_INDEX.md` shortlist |
| React setup | `design/README.md` + optional `design/react-dev-tooling-skill.md` |
| Personas, accessibility, critique, debt, or handoff | `design/README.md` + `designpowers/README.md` (+ perfection if implementation follows) |
| Looks AI-generated, de-slop a page, remove the AI look | `deslop/README.md` audit mode (scan, triage, report, fix) + `design/README.md` if tokens or `DESIGN.md` need rework |
| Pre-done check on a new page | `deslop` scanner over the changed source + `perfection/README.md` audit + `visual-qa` |

## Shared axioms

- **No design system, no UI work.** `DESIGN.md` exists before components; color, type, and spacing trace to tokens.
- **Concrete reference means contract.** Match its pixels, copy, component structure, and responsive intent unless the user approves a deviation.
- **Do not weaken UX to buy a score.** Preserve meaningful motion, content, and interaction while fixing architecture and assets.
- **No emoji icons.** Use accessible SVG icon sets.
- **Use composited animation for new code.** When writing new animation, prefer composited properties (`transform`, `opacity`, and `filter`); review-level edge cases follow [`references/design/motion/`](references/design/motion/).
- **Motion serves meaning.** Every animation or hover maps to an interaction, state change, or affordance.
- **Done requires evidence.** Run `visual-qa` at 375, 768, and 1280px with states and motion exercised, then complete two independent review passes on fresh evidence.
- **No machine-default tells.** New UI ships free of the 34 AI-slop tells in `references/deslop/taxonomy.md` - run the deslop scanner over new or changed source and triage every hit before the evidence gate. A defended, intentional choice documented in `DESIGN.md` is not slop.

## When to load something else

| Situation | Load |
|---|---|
| A suitable brand/style is absent from the catalog | A larger local design library if available; otherwise the closest Layer A reference and project research. |
| Driving a browser for design QA | A browser-driving capability. |
| **Optional game UI / engine lane:** The work is a game HUD, menu, inventory, or another game interface. | [`design/game-ui/index.md`](references/design/game-ui/index.md) for engine-neutral hierarchy and named-engine guidance. |
| **Optional platform-comparison lane:** A platform convention needs a bounded, current comparison before web adaptation. | [`design/platform-guides/index.md`](references/design/platform-guides/index.md). |
| Pure logic work with no visual surface | `programming` alone. |
| Code-level AI slop (obvious comments, dead code, over-defensive code, needless abstraction) | `remove-ai-slops` - the `deslop` ruleset here covers visual and copy slop only. |

## Activation

Use for frontend, web UI, UX, visual design, styling, layout, animation, performance, accessibility, SEO, mockups, redesigns, and audits. Do not use it for backend, CLI, or pure-logic work with no visual surface.
