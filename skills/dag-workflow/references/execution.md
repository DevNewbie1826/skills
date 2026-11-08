Read this when stage 9 (the build graph) or a stage 12 fix graph of the dag-workflow flow starts; SKILL.md, The stage map, lists it.

# dag-workflow: the build graph

Covers stage 9 of the flow and the fix graphs of stage 12 (see `SKILL.md`, The stage map).

## Stage 9: Build — the build graph

Stage 9 runs the plan as a build graph: the defined work cut into the smallest nodes that can run independently, every node owning its change, its confirming device, and the captured output of that device. A multi-unit request runs one such graph per unit, because each unit owns its worktree, branch, and PR; units launch together whenever their dependencies are settled. Everything the plan can foresee is defined before the first launch, and a node the plan did not foresee is recorded as a revision, never added silently. The lead records each launch and each attempt in the graph state; the discipline itself is owned by `references/graphs.md`, One graph per phase.

A node is a complete assignment: it makes the edit, runs the device that confirms the edit, and writes the device output to the absolute path its DELIVERABLE names. A node that fixes a defect also owns a fix device, a check that fails on the code before the fix and passes after it, and it keeps both captures. A node that returns without the outputs it named is a failed attempt, not a partial success.

The build graph contains no verification, review, or synthesis node. Verification is the next stage's own graph, and a green result for a sibling node or another unit is never this node's proof.

### Decisions, captures, and readiness

Before the build, gather the requester-owned decisions into one batch. Record the question, the options, the recommended default, and a one-line rationale for each in the plan or the evidence dir, and ask the batch once. Do not ask again for authorized stages. If a new owner decision emerges mid-run, park only the node that needs it, record what it awaits, and keep independent nodes running.

Before the first edit anywhere in the request, capture one before artifact for every defect row and every row that edits existing UI. Link each capture to its row and record the tree it was taken on in the evidence dir outside the worktree. A before capture is historical evidence: never mark it stale because the tree moved. When no row applies, leave the before step in `todo` with a skip reason.

Readiness is a fact about a node, not a time on a schedule. A node is ready when every dependency is settled and every handoff file it consumes exists and passes the check its brief names. An edge only orders; it proves neither that the file exists nor that its content is right. The handoff shape is owned by `references/graphs.md`, Handoff files. The launch pattern that follows readiness is owned by `references/graphs.md`, Running a graph on omp.

### Cutting the build graph

The unit split is decided at plan, never during a build. A unit is an independently verifiable part of the request with its own IS rows and a disjoint write scope. A one-unit request stays one PR; otherwise deliver one PR per unit, and write `## Before` and `## After` sections in each PR body showing that unit's change.

Stage 8 created each unit's branch and worktree off main, and owns the command that made them: `references/planning.md`, Stage 8: The goal and the worktree. Keep each worktree through that unit's merge, and let a correction run reuse its worktree and PR.

Cut the defined work into the smallest pieces that can run independently. Start from the plan's units and Todos rows, split each unit into nodes, then ask of every node whether it still splits; split again whenever two halves can each carry a deliverable and their write scopes stay apart. Stop at stable interface seams, and merge two nodes rather than let them share a file.

- Every command in every node prompt pins that worktree: `cd <worktree> && ...` or `git -C <worktree> ...`, never a default cwd. The pinned rule is `references/planning.md`, Stages 4-5: The plan file and its checks.
- Concurrent nodes have a disjoint write scope: no two nodes running at the same time write the same file. Dispatch a node after another only for a real dependency: it reads or writes a file the upstream node writes, or a rule orders them, such as a serialized commit.
- Launch every ready node and every independent unit in the same wave, as wide as omp's limits allow. `async.maxJobs` (100 by default) counts every `agent()` handle. A node whose scope overlaps a running node waits for a later wave; after an earlier wave merges, rebase the later unit and rejudge its evidence before reuse.
- A node owns its change AND its confirming device, and the device is the one its work type names. A `code` node runs its guard tests plus its QA scenario, with the injection check when it owns a guard row. A `design` node ends with the draft-guard checker at exit 0 on its own output, plus the post-edit capture for every surface it touched. A `research` node ends when every high-risk claim it touches has a status and a gate record. An `audit` node has no build step at all, because its lanes prove the register rather than a change. A `mixed` node does the primary type's shape plus the secondary type's verification for the surfaces the secondary type adds. The node captures what its device printed; a green result for another node or unit is not its proof. Test rules: `SKILL.md`, Rules.
- For a refactor, when the repository keeps tests for the area, the first build node writes a characterization test that passes against unchanged code before moving the structure. For a patch, retain the existing injection check.
- Route each node by agent: `task` by default, `sonic` only for strictly mechanical edits, as in `agent(prompt, { agent: "sonic", label })`. The routing table is `SKILL.md`, Agents per stage.
- Node fields: TASK, DELIVERABLE, SCOPE, VERIFY, STOP WHEN. Every node prompt follows the prompt shape in `SKILL.md`, Delegation prompts, and carries all five fields. DELIVERABLE names the changed files and the absolute path of every capture. SCOPE names the node's disjoint write scope and the worktree pin. VERIFY is the command that proves the change, including the injection check when the node owns a guard row and the fix device when the node fixes a defect. STOP WHEN is those artifacts written and no background command the node started still running.
- Keep commits within their unit. One serialized commit node per worktree loads the `git-master` skill and is the only node that runs `git commit` there; editing nodes never commit, so commits that share a worktree's index cannot interleave. A commit counts only after `git -C <worktree> cat-file -t <sha>` prints `commit`.
- Launch per `references/graphs.md`, Running a graph on omp. A wave is a set of `agent()` calls that return handles at once, then one `wait()` over those handles. For a wave of same-shaped mechanical edits, `workpool()` takes one string item per edit and delivers its aggregate once when it drains, while the kernel stays free.
- After a wave settles, read every node's output and every artifact it named. A node that returned without its named outputs is a failed attempt; record it and follow the attempt and revision rules at `references/graphs.md`, Failure, attempts, and revisions before re-dispatching it.
- No verification, review, or synthesis node inside the build graph. Verification is stage 10.

A wave in an eval cell:

```js
// One build wave: launch the nodes whose dependencies are settled, then collect.
(async () => {
  const worktree = "/abs/path/to/unit-worktree";
  const evidenceDir = "/abs/path/to/evidence/unit-a";

  const brief = (task, deliverable, scope, verify) =>
    [
      `TASK: ${task}`,
      `DELIVERABLE: ${deliverable}`,
      `SCOPE: ${scope}; worktree pin: cd ${worktree} && ...`,
      `VERIFY: ${verify}`,
      "STOP WHEN: the deliverable's files exist and no background command this node started is still running.",
    ].join("\n");

  const wave = [
    {
      id: "n1",
      agent: "task",
      text: brief(
        "Split the parser out of the CLI",
        `${worktree}/src/parser.ts plus ${evidenceDir}/n1-device.txt`,
        "src/parser.ts, src/cli.ts",
        `cd ${worktree} && bun test src/parser.test.ts`,
      ),
    },
    {
      id: "n2",
      agent: "task",
      text: brief(
        "Document the parser boundary",
        `${worktree}/docs/parser.md plus ${evidenceDir}/n2-device.txt`,
        "docs/parser.md",
        `cd ${worktree} && bun run check:docs`,
      ),
    },
  ];

  phase("build wave 1");
  const launched = [];
  for (const node of wave) {
    // Awaiting here resolves only the handle, so the whole wave still runs at once.
    const handle = await agent(node.text, { agent: node.agent, label: node.id });
    launched.push(handle);
    log(`${node.id} launched as ${handle.handle}`);
  }

  const results = await wait(launched, { timeout: 3600, raiseErrors: false });
  for (let i = 0; i < results.length; i += 1) {
    const value = results[i];
    if (value instanceof Error) {
      log(`${wave[i].id} failed attempt: ${value.message}`);
      continue;
    }
    let captured = "";
    try {
      captured = await read(`${evidenceDir}/${wave[i].id}-device.txt`);
    } catch {
      log(`${wave[i].id} returned without its device capture; record a failed attempt`);
      continue;
    }
    log(`${wave[i].id} settled with ${captured.length} captured bytes`);
  }
})();
```

A wave of the same-shaped mechanical edits uses a pool instead of one `agent()` per node:

```js
// Same-shaped edits: one string item per edit, one named pool for this wave.
(async () => {
  const worktree = "/abs/path/to/unit-worktree";
  const paths = ["docs/a.md", "docs/b.md", "docs/c.md"];
  const pool = await workpool("sonic", { name: "docs-wording-wave" });
  for (const path of paths) {
    await pool.push(
      [
        `TASK: Apply the approved wording change to ${path}.`,
        `DELIVERABLE: ${path} edited, with the checker output captured at the evidence dir.`,
        `SCOPE: ${path} only; worktree pin: cd ${worktree} && ...`,
        `VERIFY: cd ${worktree} && bun run check:docs ${path}`,
        "STOP WHEN: the edit is written, the checker output is captured, and this item is answered with yield({ key, data }).",
      ].join("\n"),
    );
  }
  log(`docs-wording-wave queued ${paths.length} items; its aggregate arrives once when the pool drains`);
})();
```

### Work-type node shapes

The work type decides what a node's VERIFY means, and the node prompt must say it.

- **`code`**: the node's guard tests plus its QA scenario, with the injection check when the node owns a
  guard row.
- **`design`**: the draft-guard checker at exit 0 on the node's own output, plus the post-edit capture for
  every surface it touched. A capture older than the node's last edit is not proof.
- **`research`**: the claim gate for every claim the node touches, and as its STOP WHEN: every high-risk
  claim has a status and a gate record. A node never restates a gate in prose; it runs the gate.
- **`audit`**: the node writes register rows or report sections only. It never edits the product, and its
  proof is a reproduced hit or a re-judged cell, not an exit code from a linter.
- **`mixed`**: the primary type's node shape, plus the secondary type's verification for the surfaces the
  secondary type adds.

### Injection check inside the node

For each guard row the node owns, prove its test can fail, inside the same node:

1. Recreate the regression the guard names: revert the fix, or make the one smallest edit that produces it.
2. Run the guard's test once and capture the failing output.
3. Restore the file, run the test once more, and capture the passing output.

The evidence set is the injection diff, the failing output, and the passing output after restore. A test that stays green under its injection guards nothing. Run inject, test, and restore as one command, so nothing ends mid-injection.

### Commits

Commit after each verified unit, in the repository's commit style, staging only its own unit's files. Nodes in the same wave share one git index, so commits are serialized: give committing to one node, or order the committing nodes so they do not run in the same wave. Record a commit only after `git -C <worktree> cat-file -t <sha>` prints `commit`.

### Evidence ownership, reuse, and freeze

Assign one writer to each run file. The lead writes shared plan, decision and finding records; a lane writes only its own evidence artifact. Keep the evidence dir outside the worktree. Record enough for each lane's evidence to identify its unit, head, tree, covered paths or globs, result, commands or observations, artifacts, and any relevant environment or build identity.

After a fix or rebase, judge each lane's evidence against the new tree. A matching tree is valid; otherwise compare changed files with its recorded scope: an intersection makes that evidence stale. A changed recorded surface or build identity also makes the affected evidence stale. Record each reuse decision and its reason; rerun only stale lanes, not every lane. Before captures remain historical and are exempt. The final-review gate is stricter: when code review is required, it needs a valid code-review receipt for this unit at the exact frozen head and matching tree; a same-tree receipt from another head or a reused sibling receipt does not satisfy it.

After triage and required fixes, freeze the unit's head and tree before opening its PR and starting the final review. Nothing commits while that freeze is in force; correction memos and other evidence go to the evidence dir, never the branch. Keep the head frozen through the verdict. A fix following a REVISE verdict starts a new correction run and a fresh freeze; it remains in the same PR. If the observed head moved, do not carry a verdict forward: re-establish valid evidence, freeze and review for the actual head.

### Concurrency and ownership

Nodes, reviewers, and you share one worktree. Three rules keep one from corrupting another's work:

1. **One foreground command per injection.** An injection driver injects, runs the test, restores the file from a backup, and checks that the restored file's hash matches the backup, all in one foreground shell command, never split across separate tool calls or left in a background session. A turn that ends early then can't leave code injected.
2. **No injection where a reviewer reads.** Never inject into the worktree while a reviewer may read it. Run injections before the reader starts, or in a private copy of the worktree.
3. **Siblings see each other's edits.** Nodes in the same wave see each other's mid-edit state. A whole-tree check (a build, `go vet ./...`) that fails in a file outside the node's write scope may have caught a sibling mid-edit: check whether a sibling was writing that file, and rerun after it settles before calling the failure a defect.

### Recovery

A settled node's child can be messaged with `handle.send` while it is resident. Once it is no longer resident, a re-run is a fresh `agent()` call with the same prompt. A node has two attempts total (`references/graphs.md`, Failure, attempts, and revisions). Before re-dispatching a failed node, restore its files to their pre-dispatch state, because a fresh `agent()` works in the shared worktree.

**Call errors** are failures of the host or the call, not the work: `agent()` raised, the output was empty or didn't match the schema, a tool or provider error, a crash, a timeout, or a node that ended without its named artifacts. Re-run that node as a fresh `agent()` call with the same prompt. Leave the plan alone.

**Work failures** are genuine: a criterion the work does not meet. Find the cause (a plan problem, a node-instruction problem, or an environment problem), fix that cause, then re-dispatch the corrected node.

### Tier execution and progress

Use the tier and facts fixed in planning. Never lower the tier; raise it when newly discovered facts require it. S permits plan review to start alongside build, with a blocker amending the run, and at most one mutation per guard row; M runs stages serially by default with the full verification wave; L adds an adversarial lane even without a high-risk row and QA covers state and lifetime transitions. Below L, the adversarial lane is required for a high-risk plan row. These are execution differences, not permission to reduce review depth or skip a required lane.

Keep `todo` current as the live checklist. At each transition changing a count, and at least every 30 minutes while a unit runs, use the handoff to report a `PROGRESS:` line with whole-request units done/total, defect gaps fixed/total when tracked, PRs merged and open, the current wave, review round, switch count, and what is waiting. Use `n/a` for a missing register. Suppress repeats with no change; keep ordinary stage-transition handoffs without duplicating an unchanged progress line.

### Restart after a death or a compaction

The rules are in `references/verification.md`, Stages 18-19: Checkpoint, cleanup, and final report. This subsection carries
only the mechanics, so the two never state the same rule twice.

- The first command of a restarted run is the rebind: read the plan's evidence dir, `git worktree list`, and
  `git branch --show-current`, then confirm all three match what the plan records.
- Before dispatching, read the plan file, the todo list, and the evidence dir. Never carry a next action out
  of the previous turn's conversation.
- Read the build graph's snapshot and event log and reconcile live handles before relaunching any node; see
  `references/graphs.md`, Picking a graph back up.
- Read the live external state with a command, not from memory: `git ls-remote` for a push, the PR's own state
  for a PR or a merge, the deploy target's own status for a deploy.
- A restarted run re-dispatches with the same node prompt. Do not rewrite the prompt to match what the
  half-finished work did.
- Inject, run the guard test, and restore in one foreground command, so a killed turn cannot leave a mutant in
  the tree.

---
