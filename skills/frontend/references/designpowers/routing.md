# designpowers Routing Contract

Read this when routing design operating guidance into frontend planning, implementation, visual QA, or review.

`designpowers` adds design-process context inside `frontend`; it does not replace frontend, `visual-qa`, or the project's planning, implementation, and review workflows. It must not create a second planner, builder, verification harness, or orchestration API.

## Phase routing

Each lane's Phase owner table names what to load or instruct, and the required handoff, for its phase. Add the lane's Prompt injection block to the assignment when the phase uses it.

## Planning

When planning is needed, supply design-specific context to the project's planning workflow rather than writing a parallel plan; the Prompt injection block in [lane-a-direction.md](lane-a-direction.md) lists that context.

## Implementation

When a plan is approved, the implementation workflow owns execution. Enrich implementation assignments with:

- the exact task and files in scope;
- relevant project design-record decisions, if one exists;
- required frontend `design` and `perfection` references;
- required `visual-qa` evidence for rendered claims; and
- the design-debt rule: unresolved accessibility debt cannot disappear into a summary.

## Visual checks

`visual-qa` owns objective rendered evidence. Run it before accepting visual or design-quality claims. Then apply design judgment to the same build:

- accessibility review covering WCAG and cognitive accessibility;
- heuristic review of task flow and feedback states;
- synthetic persona walkthroughs; and
- explicit debt capture for unresolved design or accessibility gaps.

The same build must satisfy objective visual evidence and design judgment unless remaining gaps are explicitly recorded and accepted by the user.

## Final review

Use the project's review workflow as the final gate for significant implementation work. The review packet should include the original goal and constraints, changed files and diff, any design-record path, frontend verification outputs, `visual-qa` artifact paths, persona results, and design-debt entries.

## Prohibited routes

Frames, bridge tooling, canvas adapters, and fabricated direct calls are not available integration paths. Do not introduce scripts, hooks, tool APIs, schedulers, or competing planning and build harnesses from this reference.
