import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Opt-in triggers WITH autocomplete (from commands/*.md) and a zero-config
// fallback input hook. Both rewrite /wf and /uwf into /goal with the flow.
//   /wf  <task>  → /goal task: <task>\n\n<flow>            (workflowz keyword)
//   /uwf <task>  → /goal task: <task>\n\nultrathink. <flow> (workflowz + ultrathink)
// "task:" wrapper: omp's goal parser treats a leading set/show/pause/resume/
// drop/budget as a goal-management subcommand; prefixing with the non-reserved
// word "task:" keeps the user's text as the goal objective.
// Keywords stay OUTSIDE the XML so omp's magic-keyword matcher sees them
// (XML/HTML sections are ignored by the matcher per the omp docs).
// No idempotency guard is needed: a rewrite begins with "/goal ", so it no
// longer matches the "/wf " / "/uwf " prefix predicates on re-entry.
// InputEventResult is { handled?, text?, images? } (omp 17.2.7
// src/extensibility/extensions/types.ts), so returning { text } is the
// documented transform contract.

const FLOW = `workflowz. Run this task through the following four-phase flow:

<workflow-flow>
  <phase step="1" name="Plan Mode">
    Break the task into slices; note which can run in parallel and their dependencies. Plan only; do not execute yet. Scope the full task yourself. For each slice, name the skill or agent that should do it AND the quality check that should review it (e.g. \`programming\` for Python/Rust/TypeScript/Go source work, \`debugging\` for runtime bugs, \`frontend\` and \`visual-qa\` for UI, \`scout\`/\`librarian\` for investigation; code QA with \`programming\` + \`remove-ai-slops\`, evidence review for investigation, consistency review for docs).
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
`;

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf, /uwf)");

  pi.on("input", async (event) => {
    const text = event.text;
    const isUwf = text.startsWith("/uwf ");
    const isWf = text.startsWith("/wf ");
    if (!isUwf && !isWf) return;
    const objective = "task: " + text.slice(isUwf ? "/uwf ".length : "/wf ".length);
    if (isUwf) {
      return { text: "/goal " + objective + "\n\nultrathink. " + FLOW };
    }
    return { text: "/goal " + objective + "\n\n" + FLOW };
  });
}
