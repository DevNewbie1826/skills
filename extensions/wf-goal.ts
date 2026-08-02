import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Opt-in triggers (no autocomplete — these are input-hook patterns, omp would
// dispatch a *registered* /wf to a handler that cannot activate Goal Mode):
//   /wf  <task>  → /goal <task> — <tip flow>             (workflowz keyword)
//   /uwf <task>  → /goal <task> — ultrathink. <tip flow> (workflowz + ultrathink)
// `/goal` is never touched, so management subcommands keep working. The task
// leads the objective so omp's goal-status shows the task, not the flow.
// The flow text is the user's original tip verbatim — no added elaboration.

const MARKER = "monolithic DAG workflow"; // idempotency guard
const TIP =
  "workflowz design full agentic one monolithic DAG workflow for these plans and " +
  "tasks; run the full workflowz with multiple council-of-subagents " +
  "(Plan Mode → Plan DAGs → work with subagent councils).";

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf, /uwf)");

  pi.on("input", async (event) => {
    if (!(event && typeof event === "object" && "text" in event)) return;
    const text = event.text;
    if (typeof text !== "string" || text.includes(MARKER)) return;
    if (text.startsWith("/uwf ")) {
      return { text: "/goal " + text.slice("/uwf ".length) + " — ultrathink. " + TIP };
    }
    if (text.startsWith("/wf ")) {
      return { text: "/goal " + text.slice("/wf ".length) + " — " + TIP };
    }
  });
}
