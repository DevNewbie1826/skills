import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Opt-in triggers WITH autocomplete (from commands/*.md) and a zero-config
// fallback input hook. Both rewrite /wf and /uwf into /goal with the flow.
//   /wf  <task>  → /goal <task>\n\n<flow>            (workflowz keyword)
//   /uwf <task>  → /goal <task>\n\nultrathink. <flow> (workflowz + ultrathink)
// Keywords stay OUTSIDE the XML so omp's magic-keyword matcher sees them
// (XML/HTML sections are ignored by the matcher per the omp docs).

const MARKER = "three-phase flow"; // idempotency guard
const FLOW = `workflowz. Run this task through the following three-phase flow:

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
</workflow-flow>`;

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf, /uwf)");

  pi.on("input", async (event) => {
    if (!(event && typeof event === "object" && "text" in event)) return;
    const text = event.text;
    if (typeof text !== "string" || text.includes(MARKER)) return;
    if (text.startsWith("/uwf ")) {
      return { text: "/goal " + text.slice("/uwf ".length) + "\n\nultrathink. " + FLOW };
    }
    if (text.startsWith("/wf ")) {
      return { text: "/goal " + text.slice("/wf ".length) + "\n\n" + FLOW };
    }
  });
}
