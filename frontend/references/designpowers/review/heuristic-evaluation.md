---
name: heuristic-evaluation
description: "Use after a build — or on any existing interface — to evaluate usability against Nielsen's ten heuristics and run cognitive walkthroughs of every key task"
---

# Heuristic Evaluation

Read this when a built or existing interface needs a usability check — Nielsen H1–H10 assessed with concrete evidence plus a cognitive walkthrough of every key task — especially when a flow feels confusing and the problem needs a name.

Back-link: [Lane C — Review & Repair](../lane-c-review.md)

Heuristic evaluation is the usability lens. Craft critique asks "does this match the plan?" and accessibility review asks "can everyone access this?"; this leaf asks "will people actually be able to use this without getting lost, confused, or stuck?"

## When to use

- After a build completes — run alongside the craft and accessibility review, not after them
- Before a fix round, so usability findings are reconciled with craft and accessibility findings together
- When a flow feels confusing but the problem is hard to articulate — the heuristics name it
- When evaluating an existing design (see [design-review.md](design-review.md)), not just freshly built work

## Required inputs

- The **build** to evaluate (running app, prototype, or screenshots — test what was built, not the spec)
- The **key tasks** (from the design brief or the inferred review brief)
- The **personas** — each persona's primary task gets a cognitive walkthrough

Without key tasks there is no meaningful task walkthrough — capture them before claiming walkthrough coverage. A shared project state file is optional, not a prerequisite.

## Method

1. **Assess Nielsen H1–H10 with concrete evidence.** Cite the specific heuristic each finding violates. Not every heuristic applies to every project — note which are not applicable.
2. **Walk every key task.** At each step, answer four questions:
   1. Will the user try to achieve the right effect here?
   2. Will the user notice that the correct action is available?
   3. Will the user associate that action with the effect they want?
   4. When the action is performed, will the user see that progress was made?

   A "no" or "uncertain" at any question is a finding.
3. **Examine error and recovery paths**, not just happy paths — error recovery, undo, back navigation, dead ends.
4. **Consider first-time learnability and repeat-user efficiency.** Both matter; each gets its own verdict.
5. **Record what works well**, not only what fails.

### The ten heuristics

| # | Heuristic |
|---|---|
| H1 | Visibility of system status |
| H2 | Match between system and real world |
| H3 | User control and freedom |
| H4 | Consistency and standards |
| H5 | Error prevention |
| H6 | Recognition rather than recall |
| H7 | Flexibility and efficiency of use |
| H8 | Aesthetic and minimalist design |
| H9 | Help users recognize, diagnose, and recover from errors |
| H10 | Help and documentation |

## Coordination with the other review lenses

Usability findings should be reconciled with craft and accessibility findings, not reported in isolation: **usability wins over style** — a beautiful interface that confuses people has failed. Use the reconciliation rules and the single consolidated report in [design-review.md](design-review.md).

## Structural-issue safeguard

A critical **H1 violation** (the user is completely lost) or **H3 violation** (a destructive action has no undo) is structural, not polish. Pause and let the user decide how to resolve it before any automated continuation.

## Feeding the fix round

- Include usability findings in the single prioritised fix list (critical first), labelled with their heuristic source
- Track deferred Minor findings in the design debt register rather than dropping them
- After the fix round, re-evaluate the critical fixes only — not the entire evaluation

## What you get

H1–H10 verdicts with evidence; a walkthrough result for each key task; findings grouped by severity; what works well; and a recommendation (Proceed / Revise / Rethink). This is the checklist's completion test; the full report format lives in [design-review.md](design-review.md).

## Integration

Cross-references: [design-review.md](design-review.md) (entry point and reconciliation), [synthetic-user-testing](synthetic-user-testing.md) and [usability-testing](usability-testing.md) (validation with people), [design-debt-tracker](../memory/design-debt-tracker.md) (deferred findings).
