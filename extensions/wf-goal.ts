import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// /wf <task> → /goal task: <task> + FLOW below. FLOW carries the omp magic
// keywords ultrathink and workflowz as plain prose on their own line, so omp
// adds their hidden notices to the goal's first turn. omp matches only the exact
// lowercase word standing alone, never inside code spans, fences or tags; the
// notice applies to that turn only, workflowz needs the task and eval tools, and
// ultrathink also raises reasoning effort when automatic thinking is on.
// /uwf is removed (its only difference was ultrathink, now part of /wf).
const packRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_MD = join(packRoot, "dag-workflow", "SKILL.md");

const FLOW = `Run this task using the dag-workflow skill.

ultrathink workflowz

First, read the skill router and follow its contract:
${SKILL_MD}

Run its stage order in one pass: collect, define, plan, plan review, decide, goal, build per unit, verify lanes, round, merge, post-merge, cleanup.`;

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
