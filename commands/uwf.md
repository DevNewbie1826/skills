---
description: Goal Mode with ultrathink + Plan→DAG→Council flow
---

/goal $ARGUMENTS — ultrathink. workflowz. Run this task through the following three-phase flow:

<workflow-flow>
  <phase step="1" name="Plan Mode">
    Break the task into independent slices. Plan only; do not execute yet. Scope the full task yourself.
  </phase>
  <phase step="2" name="Plan DAGs">
    Compose the slices into one dependency DAG: parallel where independent, a barrier only where a stage needs the full prior result.
  </phase>
  <phase step="3" name="Councils">
    Execute the DAG. At each decision run a council-of-subagents (independent reviewers in parallel) and keep only what survives an adversarial refute — default to refuted when unsure.
  </phase>
</workflow-flow>
