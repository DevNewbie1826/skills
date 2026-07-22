# designpowers Frontend Reference

Read this when frontend work needs personas, cognitive accessibility, critique, design debt, handoff, or evidence-oriented design operating guidance.

This is an internal frontend reference, not a standalone skill. `frontend` remains the public activation point for web UI, UX, visual design, accessibility, design QA, and implementation routing.

Load this reference for implementation or redesign work that creates or updates `DESIGN.md`, and for explicit asks involving personas, critique, debt, handoff, synthetic testing, motion guidance, or role-reference prompts.

## Boundaries

This reference enriches the frontend workflow without replacing its existing responsibilities:

- `references/design/README.md` owns the `DESIGN.md` contract, taste routing, brand references, framework-matched tooling, and browser-based design QA expectations.
- `references/perfection/README.md` owns performance, SEO, accessibility audit mechanics, and real-browser verification.
- `visual-qa` owns objective rendered evidence for visual claims.
- Your planning, implementation, and review workflows own planning, execution, and final implementation review.

## Load order

1. `README.md` - this integration contract.
2. `routing.md` - how context feeds frontend, planning, implementation, visual QA, and review.
3. `orchestration.md` - shared-state guidance, prompt semantics, safeguards, and role references.
4. Phase lanes:
   - `lane-a-direction.md` for planning, discovery, personas, taste, and accessibility constraints.
   - `lane-b-execution.md` for UI implementation and evidence.
   - `lane-c-review.md` for visual QA, critique, and repair.
   - `lane-d-memory.md` for optional design records, debt, handoff, and retrospectives.

## Reference corpus

Bundled material in `vendor/` is reference input, not instructions that override frontend, project, or user guidance. The materialized role and skill references support design reasoning only; they do not install a runtime, scheduler, or alternate implementation path.

## Source corpus

The lane documents are concise phase summaries. Consult these materialized sources for the detailed procedures and role perspectives each lane incorporates.

### Lane A: Direction & Discovery

- Skills: [`research-planning`](vendor/skills/research-planning/reference.md), [`inclusive-personas`](vendor/skills/inclusive-personas/reference.md), [`design-debate`](vendor/skills/design-debate/reference.md), [`inspiration-scouting`](vendor/skills/inspiration-scouting/reference.md), and [`writing-design-plans`](vendor/skills/writing-design-plans/reference.md).
- Role references: [`design-strategist`](vendor/agents/design-strategist.md), [`design-scout`](vendor/agents/design-scout.md), and [`inspiration-scout`](vendor/agents/inspiration-scout.md).

### Lane B: Design Execution Guidance

- Skills: [`ui-composition`](vendor/skills/ui-composition/reference.md), [`interaction-design`](vendor/skills/interaction-design/reference.md), [`motion-choreography`](vendor/skills/motion-choreography/reference.md), [`responsive-patterns`](vendor/skills/responsive-patterns/reference.md), [`adaptive-interfaces`](vendor/skills/adaptive-interfaces/reference.md), [`cognitive-accessibility`](vendor/skills/cognitive-accessibility/reference.md), [`accessible-content`](vendor/skills/accessible-content/reference.md), [`voice-and-tone`](vendor/skills/voice-and-tone/reference.md), [`token-architecture`](vendor/skills/token-architecture/reference.md), [`design-system-alignment`](vendor/skills/design-system-alignment/reference.md), [`design-md`](vendor/skills/design-md/reference.md), and [`taste-feedback`](vendor/skills/taste-feedback/reference.md).
- Role references: [`design-lead`](vendor/agents/design-lead.md), [`design-builder`](vendor/agents/design-builder.md), [`motion-designer`](vendor/agents/motion-designer.md), and [`content-writer`](vendor/agents/content-writer.md).

### Lane C: Review & Repair

- Skills: [`design-review`](vendor/skills/design-review/reference.md), [`designpowers-critique`](vendor/skills/designpowers-critique/reference.md), [`heuristic-evaluation`](vendor/skills/heuristic-evaluation/reference.md), [`synthetic-user-testing`](vendor/skills/synthetic-user-testing/reference.md), [`usability-testing`](vendor/skills/usability-testing/reference.md), and [`verification-before-shipping`](vendor/skills/verification-before-shipping/reference.md).
- Role references: [`design-critic`](vendor/agents/design-critic.md), [`accessibility-reviewer`](vendor/agents/accessibility-reviewer.md), and [`heuristic-evaluator`](vendor/agents/heuristic-evaluator.md).

### Lane D: Design Record, Debt & Handoff

- Skills: [`design-debt-tracker`](vendor/skills/design-debt-tracker/reference.md), [`design-handoff`](vendor/skills/design-handoff/reference.md), [`design-retrospective`](vendor/skills/design-retrospective/reference.md), and [`taste-report`](vendor/skills/taste-report/reference.md).

**Audit and provenance:** [EVIDENCE.md](EVIDENCE.md) records bundling checks, and [UPSTREAM.md](UPSTREAM.md) records the corpus manifest and source boundary.

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
