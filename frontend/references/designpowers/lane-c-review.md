# Lane C: Review & Repair

Read this when UI implementation needs evidence-based visual, accessibility, heuristic, and persona review before final sign-off.

Lane C runs after implementation and before final sign-off. It requires objective `visual-qa` evidence first, then applies designpowers judgment to the same artifact, then hands reconciled context to the project's review workflow. Measurements and screenshots anchor the review; designpowers adds human-centered judgment that metrics alone do not encode.

## Phase owner

| Capability | Materialized source | Owner | Mapping |
|---|---|---|---|
| Review an existing surface without rerunning discovery | `design-review` | `visual-qa` + review workflow | Use for critique context while still capturing objective artifacts. |
| Critique against brief, plan, personas, principles, taste, and craft | `designpowers-critique` | `visual-qa` evidence + review workflow | Run after screenshots and objective checks so findings cite the built surface. |
| WCAG, COGA, keyboard, screen reader, motion, content, and adaptive needs | `accessibility-reviewer` role | `visual-qa` evidence + review workflow | Name affected users and exact fixes. |
| Nielsen heuristics and cognitive walkthroughs | `heuristic-evaluation` + `heuristic-evaluator` role | `visual-qa` evidence + review workflow | Walk key tasks and classify H1-H10 findings with severity. |
| Persona and task walkthroughs | `synthetic-user-testing` | `visual-qa` evidence + review workflow | Validate that inclusive personas can complete real tasks in assistive or situational contexts. |
| Human testing plan when needed | `usability-testing` | Review workflow | Produce a participant-test plan or follow-up recommendation when synthetic testing is insufficient. |
| Completion evidence discipline | `verification-before-shipping` | Review workflow | Summarize completion, accessibility, persona, content, and debt status. |

The `design-critic`, `accessibility-reviewer`, and `heuristic-evaluator` files are role-reference material.

## Prompt injection

Use this sequence for UI review and repair:

```text
Run `visual-qa` first against the built surface. Capture objective screenshots, diffs, browser or terminal artifacts, and any required visual QA report.

Then apply Lane C Review & Repair to the same artifact:
- critique against brief, plan, principles, personas, taste, craft, and design-system alignment
- accessibility review for WCAG, COGA, keyboard, screen reader, touch, motion, adaptive preferences, and content
- heuristic evaluation for Nielsen H1-H10 and cognitive walkthroughs
- persona walkthroughs for relevant inclusive personas
- a real-participant testing plan when synthetic evidence is insufficient
- one evidence-backed report reconciling the findings

Resolve conflicts in this order: accessibility, usability, brief, personas, aesthetics. Escalate unresolved trade-offs to the user.

Pass the reconciled report, objective `visual-qa` artifacts, open findings, and accepted debt to the review workflow.
```

## Evidence requirements

Lane C requires:

- `visual-qa` artifacts from the actual surface;
- critique findings citing the plan, brief, personas, or taste direction;
- accessibility findings with severity, affected users, exact fix, and type;
- heuristic-evaluation results for relevant tasks;
- persona walkthrough results with task, steps, outcome, and barriers;
- a repair decision for every Critical or Major issue; and
- deferred Minor or Note findings routed to design debt with final review context.

## Guardrails

- Do not run design judgment before objective `visual-qa` evidence exists.
- A high numeric visual score cannot override an accessibility, usability, or persona-blocking finding.
- Critical findings require repair, escalation, or explicit blocking status.
- Minor findings may be deferred only when recorded as debt with affected users and a suggested fix.
- Lane C supplies review input; the independent review workflow owns final sign-off.
- Static screenshots can support visual critique, but unexercised interaction, keyboard, and screen-reader findings are labeled inferred.

## Pass / fail behavior

PASS when objective `visual-qa` evidence exists, review lanes pass or have explicit accepted debt, and reconciled context reaches independent final review.

FAIL when review lacks real artifacts, skips relevant heuristic or persona testing, treats accessibility as optional, leaves Critical or Major issues unrepaired, or omits design findings from final review.
