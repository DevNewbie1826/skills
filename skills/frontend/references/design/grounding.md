# Grounding: guideline source, ideal state, gap ledger

Read this when the request is a new screen or flow, a redesign ("this looks bad", "make it better", "rework the design system"), or any design-system creation or rework. A small change skips this run and reads the ledger in `DESIGN.md` section 9 when one exists.

It replaces taste guesses with a written bar: what a good interface does for its users, and every place the work falls short of it. The output is `DESIGN.md` section 9 (the template is in [design-system-architecture.md](design-system-architecture.md)), or the change description when the project has no `DESIGN.md`.

## 1. Guideline source, read in full

Pick the authoritative sources for the platform and the domain: the platform's own human-interface guidelines, the WCAG 2.2 success criteria, and the project's `DESIGN.md`. Read every page. When a source is too large for one context, split it into slices of at most one section each and read them in parallel if your runtime supports delegation, otherwise as sequential passes. Each reader returns the principles from its pages with their URLs. A skimmed or sampled source counts as unread.

## 2. Universal principles

Drop the platform idioms: named materials, system icon sets, platform control chrome, and vendor elevation and motion names. Keep what holds for any interface: hierarchy, feedback, consistency, error prevention and recovery, input effort, density, legibility, and accessibility.

Tie each principle to a persona and a journey step. Name who uses the product and what they are trying to get done, then the step where the principle decides the experience: first visit, daily use, recovery from an error, or a return after time away.

## 3. Ideal state

For each journey step, write what the product does at its best: what the user sees first, the one action, the feedback after it, and the way back from a mistake. Write it so a reviewer can check it on a screenshot. "The run's status and its one next action are the first thing on the screen" is checkable; "clean and intuitive" is not.

## 4. Gap ledger

Capture the surface under work with `visual-qa` (every state at 375, 768, and 1280 CSS px, both themes; for a new screen, capture the first draft after the brief is written, and let the ledger grow as the draft is checked). List every difference from the ideal state. Do not rank the small ones away.

Then add every violation of the build rules and draft guard in [brief-and-subtract.md](brief-and-subtract.md) and [../perfection/build-rules.md](../perfection/build-rules.md) (include the `check-draft-guard.ts` output) and of the WCAG 2.2 AA items in [../perfection/wcag-gate.md](../perfection/wcag-gate.md). Capture a screenshot for each row and keep the ledger in a durable record (a file in the repository or the task's own tracking record) so no finding lives only in context. One row per gap:

| ID | Screen / state | Gap | Principle or rule broken | Evidence | Fix | Status |
|---|---|---|---|---|---|---|
| G1 | Settings / save | Save button widens from 96 to 128 px when its spinner appears | State-stable controls | `before/settings-save-loading.png` | Spinner overlays the hidden label in a fixed-width slot | open |

## 5. Close the ledger

Plan the fixes before the first edit: each row names its fix and, in advance, the `visual-qa` item or probe that will prove it. Then execute without stopping to ask between rows. Independent rows may run in parallel, at most one lane per screen, where your runtime supports delegation; each fix is a scoped pass ([brief-and-subtract.md](brief-and-subtract.md), Scoped fix passes), and a large ledger ships as several changes grouped by screen or rule.

A row closes only with its passing proof and the before/after pair required by [brief-and-subtract.md](brief-and-subtract.md) (Before captures); the pairs go in the pull-request body. Report progress as closed/total rows, naming what closed since the last report.
