---
name: design-review
description: "Use when the user wants something that already exists evaluated — a screenshot, URL, prototype, or code — through one reconciled craft, accessibility, and usability critique, without rerunning discovery or build"
---

# Design Review

Read this when the user wants something that ALREADY EXISTS evaluated — a screenshot, a live URL, a prototype, or existing code/markup — critiqued for intent, craft, accessibility, and usability in one reconciled report, without rerunning discovery, strategy, or build.

Back-link: [Lane C — Review & Repair](../lane-c-review.md)

Most design work improves something that already exists. This is the review-only entry: take an existing artefact, evaluate it through three perspectives — craft and intent, accessibility, usability — and reconcile the findings into one prioritised report. It is the counterpart to building: the build lane asks "what are we designing?"; this leaf asks "what are we evaluating?"

## When to use

- "Review / audit / critique this [screen / page / app / flow / component]"
- "What's wrong with this?" / "How can I improve this?" / "Is this accessible?"
- The user shares a screenshot, a URL, or points at existing code or markup
- A usability, accessibility, or craft assessment of work that already exists is wanted

If the user wants to build something new, use the normal planning and build workflow instead. If it is genuinely unclear which they want, ask one question: "Do you want me to review something you already have, or design something new?"

## What this leaf skips and why

It deliberately skips discovery, research, strategy, inspiration, planning, and build — there is nothing to build. It does **not** skip accessibility, usability, or craft evaluation. The point is a rigorous, reconciled critique, fast, then a decision about what to fix.

## Process

### Step 1: Get the artefact

Establish what is being reviewed and take it in directly — always evaluate the **actual artefact**, never a description of it:

| Artefact | How to take it in |
|----------|-------------------|
| **Screenshot / image** | Read the image directly |
| **Live URL** | Load and screenshot it (browser tooling); note interactive states |
| **Existing code / markup** | Read the relevant files; if it runs, screenshot the running build |
| **A design spec + a build** | Read the spec, then review the build against it |

If only a static image is available, say so — keyboard, focus, and screen-reader findings will be **inferred, not verified**. Be explicit about that coverage limit.

When the artefact is a live site, follow the URL Discovery Protocol in [lane-c-review.md](../lane-c-review.md) before fetching sub-pages: never guess URLs from labels or navigation text, and state the coverage limit honestly when no sub-page URLs can be discovered.

### Step 2: Capture a lightweight inferred brief

Review normally evaluates against a brief, personas, and principles. In review mode those may not exist, so build a **minimal inferred brief** — a few quick questions, not a discovery session:

1. **What is this, and what is the main thing a person is trying to do here?** (the key task)
2. **Who is it for?** (audience and ability spectrum — if unknown, assume the full spectrum: permanent, temporary, situational)
3. **What is the quality bar, and what prompted the review?** (prototype vs flagship; "it feels off" vs "failed an audit")

Label it **inferred** (reconstructed for review, not authored up front), and record it with the review notes if a shared project record exists.

### Step 3: Evaluate through three perspectives

Assess the artefact against the inferred brief from all three perspectives — craft and intent, accessibility, usability — then reconcile (Step 4). No particular runtime or dispatch is required; what matters is that all three lenses actually run.

**Gather review inputs.** Assemble whatever exists: the relevant brief, plan, principles, personas, and the actual artefacts. Unavailable project context is not a reason to invent findings — evaluate against what exists and say what is missing.

**Evaluate against intent.** For each design decision:

1. **Does it solve the stated problem?** Refer to the brief
2. **Does it serve all the identified personas** — not just the primary user?
3. **Does it follow the design principles?** Name which principles it upholds or violates
4. **Does it align with the design system**, where one applies?

**Craft and taste evaluation (optional).** When a taste profile exists, evaluate against it: the intended emotional target (would the user describe the experience with the profile's words?), the agreed craft standards (spacing rhythm, colour restraint, consistent shadows/borders/radii, typography serving readability and personality, cohesive composition), the reference benchmark (would this sit next to the taste references; does quality match the agreed bar). Record craft findings per element as **taste expectation / current state / gap**. When no taste profile exists, say so plainly: craft evaluation is based on general quality standards only — do not substitute arbitrary personal preference.

**Accessibility review.** Every review includes an accessibility evaluation:

- **Perceivable:** content available to screen readers; colour is not the sole indicator of meaning; contrast meets WCAG AA; text resizes to 200% without loss of function; alt text present and appropriate
- **Operable:** all interactions keyboard accessible; logical focus order; visible focus indicators; touch targets at least 44x44px; motion respects reduced-motion preferences; no keyboard traps
- **Understandable:** plain, clear language; consistent navigation; error messages explain the problem and the solution; visible, associated form labels; predictable behaviour
- **Robust:** semantic HTML used correctly; ARIA only where necessary and correct; works across supported browsers and assistive technology

On a static artefact, distinguish observed checks from inferred ones.

**Usability.** Nielsen H1–H10 plus per-task cognitive walkthroughs — see [heuristic-evaluation.md](heuristic-evaluation.md).

### Step 4: Reconcile

Classify findings as **aligned**, **complementary**, or **conflicting**, and resolve conflicts by priority:

1. Accessibility over aesthetics
2. Usability over style
3. Brief over opinion
4. Personas break ties
5. If still unresolvable, ask the user

### Step 5: Classify issues

| Severity | Definition | Action |
|----------|-----------|--------|
| **Critical** | Blocks access for some users or violates the design intent | Must fix before proceeding |
| **Major** | Degrades experience significantly but does not block access | Should fix before handoff |
| **Minor** | Improvement opportunity; does not block or significantly degrade | Fix if time allows |
| **Note** | Observation or suggestion for future iteration | Document for next cycle |

### Step 6: Present one consolidated report

```markdown
# Design Review: [what was reviewed]

**Reviewed:** [artefact + how it was accessed]
**Inferred brief:** [key task · audience · quality bar]
**Coverage:** [verified vs inferred — e.g. "static screenshot: visual and content verified; interaction, keyboard, screen reader inferred"]

## Summary
[2-3 sentences: overall assessment]

## Findings (prioritised, reconciled)
### Critical — blocks access or breaks the key task
- [perspective(s)] [finding] → [fix] · affects [persona(s)]
### Major — significantly degrades the experience
- ...
### Minor — improvement opportunities
- ...

## What works well
- [genuine strengths — review is not only problems]

## Recommendation
[Ship as-is / fix criticals first / rethink — and the single most important next move]
```

For every Critical and Major finding, state who is affected, why it matters, and a recommended action — not just what is wrong.

### Step 7: Offer next steps (the user decides)

End by handing the decision to the user:

- **Fix it** — if it is code that can be edited, hand a prioritised fix list to the implementation workflow
- **Track it** — send deferred Minor and Note findings to the design debt register ([design-debt-tracker](../memory/design-debt-tracker.md)) so they are not silently dropped; record the deferred issue, affected people, suggested fix, and reason for deferral. Accessibility debt needs explicit user acknowledgement to accept
- **Go deeper** — if the review reveals the problem is *strategic* (the flow itself is wrong, not the execution), recommend the direction and discovery lane ([lane-a-direction](../lane-a-direction.md))
- **Validate with people** — if findings are contested, suggest [synthetic-user-testing](synthetic-user-testing.md) (persona walkthroughs) or [usability-testing](usability-testing.md) (real participants)

The review proposes; it does not auto-fix or decide for the user.

## Integration

Review feeds fixes (implementation workflow), debt tracking ([design-debt-tracker](../memory/design-debt-tracker.md)), strategic work (lane A), and validation with people ([synthetic-user-testing](synthetic-user-testing.md), [usability-testing](usability-testing.md)). The project's review workflow owns final sign-off for significant work.
