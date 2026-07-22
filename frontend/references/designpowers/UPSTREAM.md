# Designpowers Reference Manifest

Read this when auditing the bundled designpowers corpus and its intended boundaries.

The `vendor/` directory contains a curated third-party design-operating corpus adapted for this self-contained frontend skill. It is reference material only; the source collection is not required at runtime.

## Materialized files

- `vendor/LICENSE`
- ten role-reference files in `vendor/agents/`
- selected skill-reference files in `vendor/skills/*/reference.md`

## Included skill references

- `accessible-content`
- `adaptive-interfaces`
- `cognitive-accessibility`
- `design-debate`
- `design-debt-tracker`
- `design-handoff`
- `design-md`
- `design-retrospective`
- `design-review`
- `design-system-alignment`
- `designpowers-critique`
- `heuristic-evaluation`
- `inclusive-personas`
- `inspiration-scouting`
- `interaction-design`
- `motion-choreography`
- `research-planning`
- `responsive-patterns`
- `synthetic-user-testing`
- `taste-feedback`
- `taste-report`
- `token-architecture`
- `ui-composition`
- `usability-testing`
- `verification-before-shipping`
- `voice-and-tone`
- `writing-design-plans`

## Included role references

- `accessibility-reviewer.md`
- `content-writer.md`
- `design-builder.md`
- `design-critic.md`
- `design-lead.md`
- `design-scout.md`
- `design-strategist.md`
- `heuristic-evaluator.md`
- `inspiration-scout.md`
- `motion-designer.md`

## Excluded integration surfaces

Bridge, state, router, scheduler, and runtime-integration materials are intentionally excluded. The bundled corpus must not introduce hooks, scripts, background automation, shared host state, or a competing frontend workflow.

## Source-of-truth boundary

`vendor/` is the shipped reference corpus. It remains subordinate to `frontend`, project rules, and user instructions; it is never executable configuration.
