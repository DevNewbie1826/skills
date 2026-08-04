---
description: Goal Mode with the Plan→DAG→Council→Quality flow
---

/goal task: $ARGUMENTS

workflowz. Run this task through the following four-phase flow:

<workflow-flow>
  <phase step="1" name="Plan Mode">
    Break the task into slices; note which can run in parallel and their dependencies. Plan only; do not execute yet. Scope the full task yourself. For each slice, name the skill or agent that should do it AND the quality check that should review it (e.g. `programming` for Python/Rust/TypeScript/Go source work, `debugging` for runtime bugs, `frontend` and `visual-qa` for UI, `scout`/`librarian` for investigation; code QA with `programming` + `remove-ai-slops`, evidence review for investigation, consistency review for docs).
  </phase>
  <phase step="2" name="Plan DAGs">
    Compose the slices into one dependency DAG: parallel where independent, a barrier only where a stage needs the full prior result.
  </phase>
  <phase step="3" name="Councils">
    Execute the DAG. At each decision run a council-of-subagents (independent reviewers in parallel) and keep only what survives an adversarial refute — default to refuted when unsure.
  </phase>
  <phase step="4" name="Quality loop">
    One round = run every slice's Phase-1-assigned quality check once, then one integrated whole-output pass across all slices (cross-slice consistency, duplication, conflicts, overall slop); establish a green regression-test baseline first for code. Resolve every finding a round surfaces before the next round. By default, repeat rounds until a round surfaces zero findings. If the user asked for a specific number of rounds, run exactly that many rounds and then stop, reporting any unresolved findings; never declare done unless the final round surfaced zero findings. Report each round's output.
  </phase>
</workflow-flow>
