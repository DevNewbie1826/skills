# designpowers Frontend Reference

Read this when frontend work needs people-centered design process: inclusive personas, design research planning, structured debate, brand voice, accessible content, cognitive accessibility, mid-build taste feedback, critique and usability review, design debt, handoff, or retrospectives.

This is an internal frontend reference, not a standalone skill. `frontend` remains the public activation point for web UI, UX, visual design, accessibility, design QA, and implementation routing. This corpus is reference input only — it never overrides frontend, project, or user guidance, and it installs no runtime, scheduler, or alternate implementation path.

## What this reference owns

People, content, and process concerns around design work:

- who the design serves — inclusive personas across the full ability spectrum;
- design research planning and evidence over assumptions;
- competing directions argued honestly (debate) and brand voice and tone;
- accessibility of content and of cognition (language, structure, mental load);
- mid-build taste checkpoints, plus critique, usability, and accessibility review;
- design debt, handoff to engineering, and retrospectives (including longitudinal taste reflection).

## What this reference does NOT own

Layout, composition patterns, interaction contracts, motion, responsive and platform-adaptive behavior, and design tokens are owned elsewhere — route there first:

- `references/stylegallery/` — [layout patterns and recipes](../stylegallery/patterns/), [motion](../stylegallery/motion/index.md), [design-engineering](../stylegallery/design-engineering/) (component contracts, loading and feedback, state management), [platform guides](../stylegallery/platform-guides/index.md) (including preferences and accessibility), and [design terminology](../stylegallery/design-terminology/)
- `references/design/design-system-architecture.md` — the project design-system contract, tokens, and the DESIGN.md format

## Route table

| Need | Read |
|---|---|
| Plan with discovery, research, personas, debate, voice, taste direction | [lane-a-direction.md](lane-a-direction.md) |
| Implement with accessible content, cognitive accessibility, taste checkpoints | [lane-b-execution.md](lane-b-execution.md) |
| Critique, usability, and accessibility review of built or existing work | [lane-c-review.md](lane-c-review.md) |
| Design debt, handoff, retrospective, taste reflection | [lane-d-memory.md](lane-d-memory.md) |
| Route design context into planning, implementation, visual QA, or review | [routing.md](routing.md) |
| Shared design record, safeguards, reconciliation ladder, closeout | [orchestration.md](orchestration.md) |

Each lane file indexes the leaves in its directory with a one-line read-when cue.

## Boundaries

- `references/design/README.md` owns the DESIGN.md contract, taste routing, brand references, framework-matched tooling, and browser-based design QA expectations.
- `references/perfection/README.md` owns performance, SEO, and accessibility audit mechanics.
- `visual-qa` owns objective rendered evidence for visual claims.
- Your planning, implementation, and review workflows own planning, execution, and final implementation review.

## Guardrails

Do not introduce scripts, hooks, tool APIs, schedulers, bridge tooling, canvas adapters, or fake direct calls from this reference. Keep it as design-process context inside `frontend`.

## Completion rule

Designpowers-enhanced frontend work is complete only when:

- the frontend design ruleset ran or was explicitly ruled out for the scope;
- perfection ran for implementation, audit, performance, SEO, or accessibility work;
- visual claims cite objective visual evidence;
- any project design record used names the brief, personas, taste constraints, accessibility constraints, and accepted debt;
- remaining accessibility or persona debt is explicit, located, and user-accepted; and
- significant implementation work completes through the project's review workflow.

## Provenance

[EVIDENCE.md](EVIDENCE.md) records bundling checks; [UPSTREAM.md](UPSTREAM.md) records the corpus manifest, removals, and merges with reasons; [LICENSE](LICENSE) carries the upstream MIT notice.
