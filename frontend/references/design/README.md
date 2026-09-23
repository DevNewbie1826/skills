# Frontend Design Router

Read this when routing frontend visual work through design-system gates, Layer A/B reference loading, and design-QA phase routing.

A finished surface is coherent, distinctive, accessible, and production-ready. Correct-but-flat is not done: expressive work needs a dimensional focal object and atmosphere, grounded in the selected references rather than generic defaults.

## Mandatory Design System Gate

Run this before routing or touching UI code.

1. Search the project root, `docs/`, and `src/` for `DESIGN.md`, `design-system.md`, or `design-tokens.md`.
2. If none exists, read [design-system-architecture.md](design-system-architecture.md) and take the applicable branch below.
3. If one exists, read and follow it. Every color, type size, spacing value, and component pattern must use its tokens; add a needed token there first. Do not introduce raw hex values, arbitrary pixel values, or ad-hoc component patterns outside it.

No design system means no UI work.

### Greenfield workflow

1. From [_INDEX.md](_INDEX.md), shortlist 2-3 Layer B references, then read exactly one Layer A style skill and one Layer B reference in full. Use a larger local design library only if the curated set has no fit.
2. Create `DESIGN.md` with `## 0. Research Log`. Record the deliverable or named skip for each lane: embedded-reference shortlist and pick; shipped-product research from [lazyweb.md](lazyweb.md) when available; and 2-3 token-seeded image/model concepts when available. If a lane is unavailable, name the fallback.
3. Before extracting tokens, commit a 1-2 sentence direction: atmosphere, signature material, color story, and the memorable moment. For expressive briefs, compare 2-3 genuinely different directions and choose one rather than averaging them.
4. Extract tokens, layout grammar, component anatomy, states, motion, and content jobs into project-specific primitives. Do not copy logos, trademarked assets, or brand copy.
5. For expressive briefs, preserve and name the source material: elevation recipe, multi-stop perceptual color ramp, display/body/mono choices, and one signature interaction. If `DESIGN.md` could describe generic dark SaaS, strengthen it before coding.

For an existing UI with implicit patterns, extract and codify the system before changing it. With no reusable component layer, stop and ask whether to preserve the look with local styling or first extract `DESIGN.md` and reusable components; do not silently choose.

### Primitive Showcase Gate (MANDATORY)

Do not compose product screens until `DESIGN.md` Section 5 names reusable primitives and states, and each required state passes visual QA in a component showcase or equivalent harness at mobile, tablet, and desktop widths. The detailed creation and validation rules are in [design-system-architecture.md](design-system-architecture.md).

## Optional framework tooling

For a React project, read [react-dev-tooling-skill.md](react-dev-tooling-skill.md) when optional source inspection, render diagnostics, or static analysis fit its dependency policy. Keep runtime tools dev-only and do not add dependencies without a project need or consent. Other stacks use comparable tooling when available.

## Choosing within design/

SKILL.md owns the request-to-reference routes; this note only records the choices those routes leave open.

- Combine all applicable rows: load the design gate, then add task-specific lanes (layout, motion, perfection, etc.) and any style reference. Apply first-match only within the mutually exclusive Layer A style choices below. Do not stack extra references "just in case".
- Named brand absent from the catalog: take the closest mood shortcut in [_INDEX.md](_INDEX.md), then select a compatible Layer A style skill.
- A concrete screenshot or generated mockup is a contract: use [image-to-code-skill.md](image-to-code-skill.md), extract its tokens and responsive intent into `DESIGN.md`, and run `visual-qa` in reference-fidelity mode. For a live URL use [clone-from-url.md](clone-from-url.md) instead.
- Dashboard, settings, inbox, split pane, and app-shell routes select a project-appropriate system separately. Do not use [taste-skill.md](taste-skill.md) for these routes.
- The [StyleGallery motion](../stylegallery/motion/index.md) reference covers motion naming, specification, and review-level edge cases. Production motion defaults live in SKILL.md's shared axioms.

## Stacking rules

- Select at most one Layer A style skill. `taste-skill.md`, `cinematic-taste-skill.md`, `minimalist-skill.md`, `brutalist-skill.md`, and `soft-skill.md` are alternatives, not a stack.
- `output-skill.md` and `mockup-export-skill.md` stack on a style skill. `redesign-skill.md` replaces a style skill during audit work; `image-to-code-skill.md` pairs with one image-concept reference.
- Layer B supplies project-specific visual tokens and is orthogonal to Layer A. Apply its principles to the project's content; do not copy protected assets.
- `layout-skill.md` stacks for app-shell mechanics and scroll ownership; it adds no visual direction.

## Implementation rules

Before implementation, read `DESIGN.md`, inspect `package.json`, and match the project's existing framework and styling conventions. Choose the installed Tailwind generation and framework patterns rather than assuming a stack.

- Do not use emoji icons; use accessible SVG icon sets.
- Use `min-h-[100dvh]`, not `h-screen`, for full-height heroes.
- Isolate client-only state, motion, and portals in the smallest client component where the framework requires it.
- Document reusable patterns used 2+ times in `DESIGN.md` Section 5.
- For expressive work, load declared fonts and use the documented material, color ramp, and signature interaction; do not collapse them into generic defaults.

## Design QA (MANDATORY)

Before declaring visual work done, `visual-qa` is the verification authority. Run it on fresh evidence at 375, 768, and 1280px. Exercise hover, focus, active, loading, empty, error, and motion states as applicable; run reference-fidelity mode for concrete references and complete two independent review passes.

Fix both defects (clipping, wrong font, missing state, jank) and flatness. Motion must communicate interaction, state, hierarchy, or narrative; remove decorative motion with no job. Report done only after the visual QA passes and neither failure class remains.
