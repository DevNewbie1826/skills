---
description: "How a DAG runs on omp: nodes as eval agent() handles, prompts and handoff files, stages joined by wait() and a review node, retrying or revising one node, the single goal with todo phases, and picking a run back up after a death or a compaction."
---

# Running a DAG on omp

> Read this when you are about to start, steer, repair or resume a DAG. The DAG's shape comes from `dag-construction.md`; this file is only how it runs. Names come from `omp-names.md`.

## The pieces

- **A node** is one `agent()` call inside the `eval` tool. It returns a handle at once; the node runs in the background. Pick the agent by what the node does: `task` for a change and its proof, `sonic` for a purely mechanical edit, `scout` for read-only collection, `reviewer` or `security-reviewer` for a review node.
- **An edge** is a file. A node writes its result to the handoff path its prompt names; a node that depends on it reads that path. Starting the downstream node only after the upstream handle finished is the edge's ordering; the file is its data. A missing handoff file is a FAIL for the consumer, never an empty input.
- **A stage** is one wave of handles closed by the kernel `wait()` on all of them. Pass `raiseErrors: false` so one failed node keeps its slot and only its own branch degrades.
- **The run file** is one small markdown table the lead keeps beside the handoffs: node id, agent, handoff path, status (`waiting`, `running`, `done`, `failed`, `blocked`), attempt number, and the handle's `agent://` id. Update it when a node starts and when it ends. It is what makes a run resumable.

Keep handoffs, the run file and build files in the worktree's git-ignored folder (SKILL.md, Node prompts).

## Writing a node prompt

A node sees only its prompt. Write it so a stranger can do the work without asking:

1. `TASK:` one imperative sentence naming the deliverable.
2. `DELIVERABLE:` the exact file or files it writes, and the shape of its report.
3. `SCOPE:` what this node reads and what this node writes, as paths. Name the node, never the repository (SKILL.md, Node prompts).
4. `VERIFY:` the command it runs on its own work and the result that means PASS.
5. `STOP WHEN:` the one observable condition that ends it.

Paste every fact the node needs; a phrase like "as above" points at nothing. Give each node one role: a node that writes code does not review it. Two nodes that may run at the same time never write the same file; when they would, chain them or merge them. When a node edits a repository at the same time as others, give it `isolated: true` so it works in its own copy, and decide with `apply` and `merge` how its change comes back.

## Building and starting a DAG

1. Write the tree per `dag-construction.md`: goal, levels, atomic leaves, the direct parent of each leaf, and the real dependencies.
2. Turn the leaves into stages: everything whose inputs exist goes in the first stage; each later stage holds the nodes whose inputs the earlier stages produce. A parent that only collects and checks its children is a check the lead runs after the stage, not a node.
3. Between two stages where every later node needs every earlier one, put one review node instead of a web of edges. It reads the earlier handoffs and writes PASS or FAIL per node, so a finding re-runs only the node it names.
4. End the DAG with its review node: a `reviewer` node that reads every handoff of the last stage, re-runs their VERIFY commands and lists every problem at once.
5. Write the run file, then start the first stage's handles in one `eval` cell and record their ids.

Size the work, not the node count: one node per independent piece, many small nodes rather than a few large ones, and a piece small enough that briefing it costs more than doing it folds into its neighbour. For a wide wave, give each node a bounded report (a short file with a fixed shape) and let a review node read those, so the lead never reads raw output.

## Supervising a running DAG

Let the run wake you: a finished handle delivers its result to the session, and the `wait` tool (outside `eval`) blocks only when nothing else can move. Do not poll.
When a node drifts outside its SCOPE or circles one sub-problem, steer it with `.send()` naming the exact boundary. Give each node a time box when you start it. A node past its time box gets one steer; if its handoff file still has not changed, `.cancel()` it, keep what it wrote, and treat it as failed. Elapsed time alone is not failure while the file keeps growing.
A node that reports completion has made a claim. Read its handoff and check the facts the next node depends on before marking it `done`.

## When a node fails

- **Call failure** (the node never ran, a provider error, a refused start): start the same prompt again as a new `agent()` call. That is a retry; it costs nothing upstream.
- **Work failure** (it ran and its VERIFY failed, or its review said FAIL): fix the prompt with the finding and start the node again with the edited prompt. That is a revision. Every node downstream of it runs again; every node beside it or upstream keeps its handoff.
- A node gets two attempts. After the second failure, mark it `blocked` with the reason; its branch stops, independent branches keep running, and its parent is not done.
- When a node was right but its definition was wrong (the task itself changed), revise only that node and its downstream nodes; finished nodes elsewhere keep their files.

Never restart a whole DAG to repair one node.

## The goal and the phases

omp holds one goal at a time (`goal` tool), so one request has one goal. Its objective names the deliverable and lists, per phase (analysis, build, review and merge), the success criteria and the device that will prove each one. The `goal` tool can create, read, resume, complete or drop a goal but cannot rewrite one, so when `/wf` already armed it with the task text, keep that goal and put each phase's criteria in `todo` as the phase's first items. Mirror the phases and their steps in `todo`, marking each step when it starts and when it finishes.
A phase is done when its criteria pass with captured evidence, not when its last node reports. Mark the goal complete only when every phase's criteria pass. A decision only the user can make is asked with the `ask` tool before the stage that needs it.

## Picking a run back up

After a session death or a compaction, before any other action:

1. Read the goal (`goal` op `get`; resume it if it is paused), the `todo` list and the run file.
2. For each node marked `running`, check its handle id or its handoff file. A handoff that is complete and passes its VERIFY means `done`; anything else means the node starts again.
3. Start only the nodes that are not `done`. Never re-run a node whose handoff already passed, and never repeat a remote action (a push, a PR comment, a merge) that already happened: check the remote state first.

The `checkpoint` tool is a context checkpoint you later `rewind`; it is not where run state lives. The run file, the handoffs, `todo` and the goal are.
