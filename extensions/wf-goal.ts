import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Opt-in triggers (no autocomplete — these are input-hook patterns; registering
// them makes omp dispatch to a handler that cannot activate Goal Mode):
//   /wf  <task>  → /goal <task> — <flow>            (workflowz keyword)
//   /uwf <task>  → /goal <task> — ultrathink. <flow> (workflowz + ultrathink)
// `/goal` is never touched, so management subcommands keep working. The task
// leads the objective so omp's goal-status shows the task, not the flow.
// Flow concept (refined from the source tip): Plan Mode → Plan DAGs → Councils.

const MARKER = "three-phase flow"; // idempotency guard
const FLOW =
  "workflowz. Run this as a three-phase flow: " +
  "(1) Plan Mode — break the task into independent slices; plan only, do not execute yet; scope the full task yourself. " +
  "(2) Plan DAGs — compose the slices into one dependency DAG: parallel where independent, a barrier only where a stage needs the full prior result. " +
  "(3) Councils — execute the DAG; at each decision run a council-of-subagents (independent reviewers in parallel) " +
  "and keep only what survives an adversarial refute — default to refuted when unsure.";

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf, /uwf)");

  pi.on("input", async (event) => {
    if (!(event && typeof event === "object" && "text" in event)) return;
    const text = event.text;
    if (typeof text !== "string" || text.includes(MARKER)) return;
    if (text.startsWith("/uwf ")) {
      return { text: "/goal " + text.slice("/uwf ".length) + " — ultrathink. " + FLOW };
    }
    if (text.startsWith("/wf ")) {
      return { text: "/goal " + text.slice("/wf ".length) + " — " + FLOW };
    }
  });
}
