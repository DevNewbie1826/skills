import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Goal-gated, same-turn injection of the Plan → DAG → Council workflow.
// The `input` hook rewrites `/goal <task>` into `/goal <flow> <task>` so the
// flow becomes the Goal Mode objective AND the ultrathink/workflowz keywords
// fire for that turn (verified: omp matches keywords in /goal objectives).
// Fires ONLY for /goal — non-goal input is untouched.

const MARKER = "Plan-DAG-Council flow"; // idempotency guard
const FLOW =
  "ultrathink. Run this task through the Plan-DAG-Council flow: " +
  "(1) Plan — decompose into independent slices, planning only, no execution; " +
  "(2) DAG — arrange the slices into one dependency DAG, parallel where independent, " +
  "a barrier only where a stage needs the full prior result set; " +
  "(3) Councils — execute along the DAG, running a council-of-subagents (independent reviewers) " +
  "at each decision and keeping only what survives an adversarial refute. " +
  "Skip this flow for trivial requests. workflowz: ";

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (goal-gated)");

  pi.on("input", async (event) => {
    if (!(event && typeof event === "object" && "text" in event)) return;
    const text = event.text;
    if (typeof text !== "string" || !text.startsWith("/goal ") || text.includes(MARKER)) return;
    return { text: "/goal " + FLOW + text.slice("/goal ".length) };
  });
}
