# Lane A: Direction & Discovery

Read this when planning a UI, UX, product-surface, visual-direction, accessibility, or user-flow task.

Lane A feeds the project's planning workflow. It does not write a parallel plan or start implementation. Its job is to translate design discovery, research, personas, taste, debate, and optional project state into decision-complete planning context with design-specific acceptance criteria.

## Leaves in this lane

| Leaf | Read when |
|---|---|
| [inclusive-personas.md](direction/inclusive-personas.md) | defining who the design serves across the full ability spectrum — personas, stories, and scenario intersections |
| [research-planning.md](direction/research-planning.md) | user needs are unclear or assumptions need validation — plan what to learn, which methods, from whom |
| [design-debate.md](direction/design-debate.md) | a design direction is contested and options should be argued with trade-offs before the user decides |
| [voice-and-tone.md](direction/voice-and-tone.md) | establishing or applying brand voice — attributes, tone by context, vocabulary, reading level |

## Phase owner

| Capability | Owner | Mapping |
|---|---|---|
| Discover the human problem, constraints, audience, success criteria, and early taste signals | Planning workflow | Add a compact design brief before tasks are drafted; ask only unresolved owner decisions. |
| Identify research gaps and inclusion-aware methods | [research-planning.md](direction/research-planning.md) | Turn questions into discovery tasks or explicit assumptions with evidence requirements. |
| Define principles, experience map, positioning, and success metrics | Planning workflow | Add strategy constraints and design principles to acceptance criteria. |
| Represent the full ability spectrum | [inclusive-personas.md](direction/inclusive-personas.md) | Require personas and stress cases, including permanent, temporary, and situational contexts. |
| Calibrate current-project taste and quality bar | Planning workflow | Add project-specific taste constraints; do not import cross-project memory as a design rule. |
| Surface competing directions and trade-offs | [design-debate.md](direction/design-debate.md) | Present two or three options with accessibility and usability trade-offs before selecting defaults. |
| Assess competitors when competitive research is undertaken | [research-planning.md](direction/research-planning.md) | Compare UX and accessibility; distinguish observed evidence from speculation, and state implications for this project. Competitive research is optional, not a requirement for every task. |
| Validate proposed navigation and information architecture | [research-planning.md](direction/research-planning.md) | Include a findability task probe to check whether users can locate key destinations. |
| Produce journey maps when useful | [research-planning.md](direction/research-planning.md) | For each journey stage, capture goals, actions, thoughts, emotions, pain points, opportunities, and ability considerations. Journey maps are not required for every task. |
| Define and apply brand voice and tone | [voice-and-tone.md](direction/voice-and-tone.md) | Carry voice attributes, tone-by-context, and vocabulary into content acceptance checks. |
| Curate references without copying | Planning workflow (salvage below) | Add evidence-backed notes describing what to take and what to leave. |
| Maintain shared design state | Optional project design record | Read or update it only when the project already uses one or the user requests durable state. |

## Salvaged from removed references

Short items whose full source documents were removed as duplicated elsewhere:

- **From former ui-composition:** before making visual decisions, confirm the foundation trio exists — a design brief or strategy (from earlier phases), personas (especially ability-spectrum considerations), and the existing design system (read it before inventing a new one).
- **From former inspiration-scouting and its scout role reference:** keep the board small and annotated — 5–8 references across the visual, interaction, and emotional layers, including at least one cross-domain wild card. For each, record what to take and what to leave. The best inspiration often comes from outside the project's domain — actively seek cross-domain references:

  | Project Domain | Look At |
  |---------------|---------|
  | Healthcare | Meditation apps (calm), fitness apps (motivation), journaling apps (reflection) |
  | Finance | Productivity tools (clarity), weather apps (data viz), news apps (hierarchy) |
  | Education | Games (engagement), music apps (progression), social apps (community) |
  | E-commerce | Editorial sites (storytelling), gallery apps (browsing), travel apps (discovery) |
  | Enterprise | Consumer apps (polish), design tools (power + clarity), documentation sites (wayfinding) |

  Don't force connections — but don't limit yourself to competitors either. A beautiful reference with 2:1 contrast ratios is not inspiration — it's a cautionary tale. Flag accessibility issues in references rather than imitating them.

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

When design principles are part of that context, distil them into 3–5 principles that are opinionated, actionable, and testable — "Simple" is not a principle; "Show only what matters for the current task" is. Each principle includes: **the principle** (one sentence, opinionated and specific), **what it means in practice** (concrete examples of decisions this principle would drive), **what it rules out** (what this principle says no to), and **how to test it** (how to verify the design lives up to it). *(from the former design-strategist role reference)*

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
