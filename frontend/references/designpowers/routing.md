# designpowers Routing Contract

Read this when routing design operating guidance into frontend planning, implementation, visual QA, or review.

`designpowers` adds design-process context inside `frontend`; it does not replace frontend, `visual-qa`, or the project's planning, implementation, and review workflows. It must not create a second planner, builder, verification harness, or orchestration API.

## Phase routing

| User intent or workflow phase | Load or instruct | Required handoff |
|---|---|---|
| Ambiguous or multi-step web UI request; a request needing a plan | Your planning workflow + `lane-a-direction.md` | Provide design discovery prompts, target users, inclusive personas, taste direction, owner decisions, and design-debt policy as planning inputs. |
| Approved-plan execution | Your implementation workflow + `lane-b-execution.md` | Carry current design constraints into implementation assignments and evidence expectations. |
| Building, styling, redesigning, auditing, or performance-checking a web UI | Frontend `design` + `perfection`; add `lane-b-execution.md` when designpowers affects implementation | Preserve the `DESIGN.md` gate, design/perfection routing, framework-matched tooling, real-browser checks, and implementation standards. |
| Screenshots, visual regressions, clone fidelity, layout quality, alpha/CJK checks, or design QA | `visual-qa` + `lane-c-review.md` | Capture objective evidence before design judgment and use the same artifacts for persona, accessibility, and heuristic review. |
| Final approval, QA, review changes, or significant completed implementation | Your review workflow + `lane-c-review.md` and `lane-d-memory.md` | Include the design brief, visual artifacts, unresolved design debt, and accessibility-debt acknowledgements. |

## Planning

When planning is needed, supply design-specific context to the project's planning workflow rather than writing a parallel plan. Include:

- product or page goal;
- primary tasks and user journeys;
- inclusive personas and assistive or cognitive constraints;
- taste direction, anti-references, and design-system constraints;
- content tone and plain-language requirements;
- motion, responsive, and adaptive-interface requirements;
- verification expectations: frontend checks, visual QA artifacts, persona walkthroughs, and independent review; and
- explicit constraints, including prohibited bridge or canvas tooling.

## Implementation

When a plan is approved, the implementation workflow owns execution. Enrich implementation assignments with:

- the exact task and files in scope;
- relevant project design-record decisions, if one exists;
- required frontend `design` and `perfection` references;
- required `visual-qa` evidence for rendered claims; and
- the design-debt rule: unresolved accessibility debt cannot disappear into a summary.

## UI build through frontend design and perfection

The frontend skill owns UI build quality. This reference may point it to user taste and anti-reference notes, target personas and success criteria, content and state expectations, cognitive-accessibility and adaptive-preference requirements, and design-token constraints. It does not replace the `DESIGN.md` gate, taste routing, real-browser QA, or performance discipline.

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

Frames, bridge tooling, canvas adapters, and fabricated direct calls are not available integration paths. Do not add scripts, hooks, schedulers, or competing planning and build harnesses.
