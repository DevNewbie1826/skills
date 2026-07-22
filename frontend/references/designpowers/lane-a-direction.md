# Lane A: Direction & Discovery

Read this when planning a UI, UX, product-surface, visual-direction, accessibility, or user-flow task.

Lane A feeds the project's planning workflow. It does not write a parallel plan or start implementation. Its job is to translate design discovery, research, personas, taste, debate, and optional project state into decision-complete planning context with design-specific acceptance criteria.

## Phase owner

| Capability | Source boundary | Owner | Mapping |
|---|---|---|---|
| Discover the human problem, constraints, audience, success criteria, and early taste signals | Authored discovery guidance | Planning workflow | Add a compact design brief before tasks are drafted; ask only unresolved owner decisions. |
| Identify research gaps and inclusion-aware methods | `research-planning` | Planning workflow | Turn questions into discovery tasks or explicit assumptions with evidence requirements. |
| Define principles, experience map, positioning, and success metrics | Authored strategy guidance | Planning workflow | Add strategy constraints and design principles to acceptance criteria. |
| Represent the full ability spectrum | `inclusive-personas` | Planning workflow | Require personas and stress cases, including permanent, temporary, and situational contexts. |
| Calibrate current-project taste and quality bar | Authored taste guidance | Planning workflow | Add project-specific taste constraints; do not import cross-project memory as a design rule. |
| Surface competing directions and trade-offs | `design-debate` | Planning workflow | Present two or three options with accessibility and usability trade-offs before selecting defaults. |
| Curate references without copying | `inspiration-scouting` | Planning workflow | Add evidence-backed notes describing what to take and what to leave. |
| Maintain shared design state | Optional project design record | Planning workflow | Read or update it only when the project already uses one or the user requests durable state. |

The `design-strategist`, `design-scout`, and `inspiration-scout` files are role-reference material for prompts, not separately installed executors.

## Prompt injection

Use this context in a planning request when the work is UI, UX, product surface, visual direction, design-system, accessibility, or user-flow shaped:

```text
Apply Lane A Direction & Discovery as design-process context.

Before planning, extract or infer:
- problem statement, primary users, constraints, and out-of-scope work
- inclusive-personas ability spectrum and stress contexts
- design principles, success metrics, quality bar, and current-project taste signals
- research gaps that affect design decisions
- competing directions and trade-offs when direction is not settled
- existing project design-record decisions, debt, and open questions when available

Add design-specific acceptance criteria:
- each UI task names the persona or journey it serves
- each relevant task has accessibility and cognitive-accessibility checks
- each visual decision traces to a design principle, taste signal, or design-system token
- deferred questions are explicit owner decisions, not hidden assumptions
```

## Evidence requirements

Lane A passes only when the plan has inspectable design context, not vague intent:

- the plan names the design brief, personas, success criteria, constraints, and owner decisions;
- an optional design record contains the current brief, personas, principles, taste signals, decisions, questions, and debt register;
- verification entries include real-surface QA and affected persona or ability-spectrum checks; and
- each adopted default names why it was safe to use.

## Guardrails

- The planning workflow owns the final plan; Lane A may enrich it but must not create a second plan.
- Cross-project memory is descriptive only and cannot steer the project unless the user states the preference now.
- Product-shaping, accessibility-critical, or hard-to-reverse trade-offs pause for a user decision.
- Do not introduce a scheduler, background automation, or a project-root state convention solely for this reference.

## Pass / fail behavior

PASS when the planning workflow produces a decision-complete, design-aware, persona-aware, evidence-bound plan.

FAIL when the plan skips inclusive personas, treats accessibility as final polish, treats taste as generic style, writes a parallel plan, or leaves design decisions for implementers to invent.
