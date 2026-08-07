import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// /wf <task> → /goal task: <task> + "use the dag-workflow skill" (no keywords —
// both workflowz and ultrathink steering are absorbed into the skill itself:
// execution-patterns.md + SKILL.md Execution mode section).
// /uwf is removed (the only difference was ultrathink, now absorbed).
const packRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_MD = join(packRoot, "dag-workflow", "SKILL.md");

const FLOW = `Run this task using the dag-workflow skill.

First, read the skill router and follow its contract:
${SKILL_MD}`;

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf)");

  pi.on("input", async (event) => {
    const match = /^\/wf\s+([\s\S]*)$/.exec(event.text);
    if (!match) return;
    const task = match[1].trim();
    if (!task) return;
    return { text: "/goal task: " + task + "\n\n" + FLOW };
  });
}
