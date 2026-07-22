# Lane B: Design Execution Guidance

Read this when implementing UI with designpowers composition, interaction, accessibility, or evidence constraints.

Lane B feeds the implementation workflow and `frontend`. It does not install a separate builder. Its job is to carry composition, interaction, motion, content, responsive, adaptive, token, and cognitive-accessibility guidance into implementation assignments while the implementation workflow retains ownership of decomposition, QA, evidence, and completion.

## Phase owner

| Capability | Materialized source | Owner | Mapping |
|---|---|---|---|
| Visual hierarchy, layout, color, typography, touch targets, and WCAG contrast | `ui-composition` | Implementation workflow + `frontend` | Add visual constraints and acceptance checks to assignments. |
| States, feedback, loading, error, keyboard, touch, and recovery behavior | `interaction-design` | Implementation workflow + `frontend` | Define default, hover, focus, active, disabled, loading, success, and error states where applicable. |
| Purposeful motion and reduced-motion alternatives | `motion-choreography` | Implementation workflow + `frontend` | Explain what changed, what to notice, or how elements relate; provide safe alternatives. |
| Content-driven breakpoints and zoom behavior | `responsive-patterns` | Implementation workflow + `frontend` | Prove narrow, mid, desktop, and 200-percent zoom behavior when the surface is visual. |
| User-preference adaptation | `adaptive-interfaces` | Implementation workflow + `frontend` | Support relevant color scheme, contrast, reduced motion, text sizing, and density preferences. |
| Mental load, wayfinding, focus management, memory demands, and recovery paths | `cognitive-accessibility` | Implementation workflow + `frontend` | Add COGA-style checks for flows, forms, navigation, and dense tools. |
| Plain-language labels, headings, alt text, link text, errors, and instructions | `accessible-content` and `voice-and-tone` | Implementation workflow + `frontend` | Require final copy, useful errors, readable labels, and consistent tone. |
| Tokens and design-system consistency | `token-architecture` and `design-system-alignment` | `frontend` | Use real tokens and existing components before one-off styling. |

The `design-lead`, `motion-designer`, and `content-writer` files are prompt-role references, not alternate executors.

## Prompt injection

Add this block to a UI implementation assignment:

```text
Load `frontend` for UI implementation and apply Lane B Design Execution Guidance.

Carry forward:
- design principles, personas, taste direction, and accepted trade-offs
- hierarchy, spacing, type, color, contrast, and touch-target constraints
- interaction states, feedback, keyboard, touch, loading, empty, and error paths
- purposeful motion and reduced-motion alternatives
- content-driven breakpoints, zoom, and relevant user preferences
- cognitive accessibility, plain-language, reusable-token, and existing-component requirements

Do not invent visual direction that conflicts with the plan. If a user-impacting decision is missing, identify the exact owner decision needed.
```

## Evidence requirements

A Lane B completion claim includes:

- changed files and `frontend` references loaded;
- the real-surface QA invocation and captured artifact path;
- screenshot, browser, HTTP, or terminal artifacts appropriate to the surface;
- accessibility evidence required by the plan, such as keyboard checks or framework-matched diagnostics;
- a short trace from major UI decisions to personas, principles, tokens, or state requirements; and
- cleanup receipts for browser sessions, servers, temporary artifacts, or processes used during QA.

## Guardrails

- UI implementation goes through `frontend`; Lane B only enriches implementation context.
- The implementation workflow owns decomposition, dispatch, evidence, and completion.
- Role references describe a perspective, not an available executor.
- No placeholders, generic copy, unverified contrast claims, decorative-only motion, or one-off hardcoded systems pass this lane.
- Accessibility and cognitive accessibility are implementation constraints, not review-only cleanup.
- Prompt wording cannot create hidden automation.

## Pass / fail behavior

PASS when implementation uses `frontend`, applies Lane B constraints, and returns actual-surface evidence.

FAIL when implementation skips frontend guidance, invents unplanned direction, omits cognitive-accessibility checks for complex flows, ships placeholder content, leaves required states undesigned, or claims success without evidence.
