import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Opt-in trigger: `/wf <task>` is rewritten to `/goal <task> — <flow>` so Goal
// Mode runs with the Plan-DAG-Council methodology (ultrathink/workflowz fire).
// `/goal` itself is NEVER touched — management subcommands (drop/show/pause/...)
// and plain goals keep working. The task goes FIRST so omp's goal-status display
// shows the task, not the flow prefix.

const MARKER = "Plan-DAG-Council"; // idempotency guard
const FLOW_SUFFIX =
  " — approach via the Plan-DAG-Council flow: " +
  "ultrathink; (1) Plan — decompose into independent slices, planning only; " +
  "(2) DAG — one dependency DAG, parallel where independent, a barrier only where " +
  "a stage needs the full prior result set; (3) Councils — each decision runs a " +
  "council-of-subagents (independent reviewers), keep only what survives an " +
  "adversarial refute. Skip for trivial requests. workflowz";

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf trigger)");

  pi.on("input", async (event) => {
    if (!(event && typeof event === "object" && "text" in event)) return;
    const text = event.text;
    if (typeof text !== "string" || !text.startsWith("/wf ") || text.includes(MARKER)) return;
    return { text: "/goal " + text.slice("/wf ".length) + FLOW_SUFFIX };
  });
}
