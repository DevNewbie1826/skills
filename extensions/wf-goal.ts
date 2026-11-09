import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// /wf <task> → /goal ultrathink workflowz, then task: <task> + FLOW below. The
// omp magic keywords ultrathink and workflowz open the goal objective as plain
// prose, so omp adds their hidden notices to the goal's first turn. omp matches
// only the exact lowercase word standing alone, never inside code spans, fences
// or tags, so the line goes before the task text: an unclosed fence or tag in
// the task would mask anything after it. The notice applies to that turn only,
// workflowz needs the task and eval tools, and ultrathink also raises reasoning
// effort when automatic thinking is on.
// /uwf is removed (its only difference was ultrathink, now part of /wf).
const packRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_MD = join(packRoot, "skills", "dag-workflow", "SKILL.md");

const KEYWORDS = "ultrathink workflowz";

const FLOW = `Run this task using the dag-workflow skill.

First, read the skill router and follow its contract:
${SKILL_MD}

Work the request in its order: analyze the context with a DAG and define the ideal state, create the worktree, set the goal's criteria, run all work as DAGs with a confirmation device for every implementation and fix, open one PR, review it until APPROVED, and merge only on MERGE GO.`;

export default function wfGoalExtension(pi: ExtensionAPI) {
  pi.setLabel("Workflowz flow (/wf)");

  pi.on("input", async (event) => {
    const match = /^\/wf\s+([\s\S]*)$/.exec(event.text);
    if (!match) return;
    const task = match[1].trim();
    if (!task) return;
    return { text: "/goal " + KEYWORDS + "\n\ntask: " + task + "\n\n" + FLOW };
  });
}
