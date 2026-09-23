# Lane B: Design Execution Guidance

Read this when implementing UI with designpowers content, cognitive-accessibility, taste-feedback, or evidence constraints.

Lane B feeds the implementation workflow and `frontend`. It does not install a separate builder. Its job is to carry content, cognitive-accessibility, and taste guidance into implementation assignments while the implementation workflow retains ownership of decomposition, QA, evidence, and completion.

Visual-system mechanics — layout, composition, interaction states, motion, responsive behavior, preference adaptation, and tokens — are owned by the StyleGallery mirror (`references/stylegallery/`) and the design-system contract (`references/design/design-system-architecture.md`); Lane B carries their constraints into assignments without restating them.

## Leaves in this lane

| Leaf | Read when |
|---|---|
| [accessible-content.md](execution/accessible-content.md) | writing labels, headings, errors, help text, alt text, link text, or tables that must work for everyone |
| [cognitive-accessibility.md](execution/cognitive-accessibility.md) | evaluating mental load, wayfinding, focus management, memory demands, or decision complexity |
| [taste-feedback.md](execution/taste-feedback.md) | a build has subjective aesthetic decisions and the user should course-correct at 2–4 visual checkpoints |

## Phase owner

| Capability | Owner | Mapping |
|---|---|---|
| Mental load, wayfinding, focus management, memory demands, and recovery paths | [cognitive-accessibility.md](execution/cognitive-accessibility.md) | Add COGA-style checks for flows, forms, navigation, and dense tools. |
| Plain-language labels, headings, alt text, link text, errors, and instructions | [accessible-content.md](execution/accessible-content.md) + [voice-and-tone.md](direction/voice-and-tone.md) | Require final copy, useful errors, readable labels, and consistent tone. |
| Mid-build taste checkpoints | [taste-feedback.md](execution/taste-feedback.md) | Show intermediate output with specific taste questions; record responses as taste signals. |
| Visual hierarchy, layout, color, typography, touch targets, and WCAG contrast | `references/stylegallery/` patterns, recipes, and guides | Carry their constraints as acceptance checks; do not restate their guidance here. |
| States, feedback, loading, error, keyboard, touch, and recovery behavior | `references/stylegallery/design-engineering/` | Require default, hover, focus, active, disabled, loading, empty, success, and error states where applicable. |
| Purposeful motion and reduced-motion alternatives | `references/stylegallery/motion/` | Explain what changed, what to notice, or how elements relate; provide safe alternatives. |
| Content-driven breakpoints and user-preference adaptation | `references/stylegallery/platform-guides/` | Prove narrow, mid, desktop, and 200-percent zoom behavior when the surface is visual; support relevant preferences. Application-level choices such as density persist across sessions, and users are never asked to justify a preference (from former adaptive-interfaces). |
| Tokens and design-system consistency | `references/design/design-system-architecture.md` | Use real tokens and existing components before one-off styling. |

### Motion numbers (from the former motion-designer role reference)

- **Duration discipline** — micro-interactions: 100–200ms. Transitions: 200–400ms. Complex choreography: 400–700ms. Nothing over 1 second unless it is a loading indicator
- **Reduced-motion alternatives** — for `prefers-reduced-motion: reduce`, reduce, remove, or substitute non-essential motion as appropriate while preserving equivalent state and feedback. A fade is not automatically safe or a pass; verify the alternative against the task and device evidence, following the StyleGallery motion owner (`references/stylegallery/motion/`). Numeric duration and easing examples below are subordinate to that evidence and owner (from former motion-designer).
- **Test at 6x slow-motion** — if an animation looks wrong at 6x slowdown, the timing is wrong

| Context | Easing | Why |
|---------|--------|-----|
| Element entering | ease-out (decelerate) | Arrives and settles |
| Element leaving | ease-in (accelerate) | Departs with momentum |
| State change | ease-in-out | Smooth weight shift |
| Micro-interaction | spring (stiffness 300–500, damping 20–30) | Responsive, alive |
| Attention redirect | sharp ease-out, 150ms | Snappy, purposeful |

Never animate:

- Colour changes on text (accessibility issue — can cause flickering for photosensitive users)
- Layout properties (`width`, `height`, `top`, `left`) in performance-critical paths — use `transform` instead
- Anything that delays the user from completing their task
- Decorative loops that run continuously — they drain battery, consume attention, and can trigger vestibular disorders

Done checks: all animated properties are GPU-compositable (`transform`, `opacity`, `filter`) where possible; no continuously looping animations without user control; no large-scale zoom, spin, or parallax without a reduced-motion fallback (vestibular safety).

## Salvaged from removed references

Short items whose full source documents were removed as duplicated elsewhere:

- **From former responsive-patterns:** find breakpoints from the content — start at 320px and widen until the layout looks wrong; that width is a breakpoint. Name breakpoints by behaviour, not device. At narrow widths, decide each item's disposition: kept (essential for the task), collapsed (behind a toggle), deferred (lower in scroll order), or hidden (last resort) — and document these decisions.
- **From former ui-composition:** for each visual decision, record three fields — What (the decision made), Why (how it serves the design principles and personas), Accessibility (how it meets inclusive-design requirements).

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

Content rules from the former content-writer role reference:

- Every error message follows this structure: 1. **What happened** — in plain language ("We couldn't save your changes"); 2. **Why** — if it helps the user ("The file is too large"); 3. **What to do** — always actionable ("Try a file under 10 MB"). Never: "Error 403: Forbidden", "An unexpected error occurred", or "Invalid input"
- Reading level assessment (target: Grade 6–8 / age 11–14)
- Time-sensitive content includes enough context to remain meaningful later

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
- No placeholders, generic copy, unverified contrast claims, decorative-only motion, or one-off hardcoded systems pass this lane.
- Accessibility and cognitive accessibility are implementation constraints, not review-only cleanup.
- Prompt wording cannot create hidden automation.

## Pass / fail behavior

PASS when implementation uses `frontend`, applies Lane B constraints, and returns actual-surface evidence.

FAIL when implementation skips frontend guidance, invents unplanned direction, omits cognitive-accessibility checks for complex flows, ships placeholder content, leaves required states undesigned, or claims success without evidence.
