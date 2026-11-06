Read this when stage 9 (the build run) of the dag-workflow flow starts; SKILL.md, The stage map, lists it.

# dag-workflow: execution

Covers stage 9 of the flow (see `SKILL.md`, The stage map).

## Stage 9: Run the plan

Run the plan's nodes under these rules.

### Decisions, captures, and readiness

Before build, gather the requester-owned decisions into one batch. Record the question, options, recommended default and one-line rationale for each in the plan or evidence dir, and ask the batch once. Do not ask again for authorized stages. If a new owner decision emerges mid-run, park only the lane that needs it, record what it awaits, and continue independent lanes. Before the first edit anywhere in the request, capture one before artifact for every defect row and every row that edits existing UI. Link each capture to its row and record the tree on which it was taken in the evidence dir outside the worktree. The capture is historical evidence: never mark it stale merely because the tree changes. If there is no applicable row, keep the before step in `todo` with a skip reason. ### Worktree and nodes

Decide the unit split in the plan, never during a build. A unit is an independently verifiable part of the request with its own IS rows and a disjoint write scope. Give each unit its own branch and worktree off main, kept through that unit's merge; a correction run for that unit reuses its worktree and PR. A one-unit request stays one PR; otherwise deliver one PR per unit. Each PR body has `## Before` and `## After` sections showing that unit's change. Keep commits within the unit and serialize commits that share a worktree's index. ```
git worktree add -b <branch> <path> main
```

- Every command in every node prompt pins that worktree: `cd <worktree> && ...` or `git -C <worktree> ...`, never a default cwd (pinned rule, `references/planning.md`, Stages 4-5: The plan file and its checks).
- Parallel nodes have a disjoint write scope: no two nodes running together write the same file. Dispatch a node after another only for a real dependency: it reads or writes a file the upstream node writes, or a rule orders them, such as serialized commits.
- Dispatch all independent units and lanes up to host capacity, subject to real dependencies and disjoint write scopes. Units whose scopes overlap wait for a later wave; after an earlier wave merges, rebase the later unit and rejudge its evidence before reuse. Use the host workflow tool when dependency ordering is the point, or existing `agent()`/`parallel()` nodes. - Every lane proves its own assigned work and captures its own evidence; a green result for another lane or unit is not its proof. This extends the existing rule that an editing node owns its change and its proof; it does not add a verification, review or synthesis node inside the build run. - For a refactor, when the repository keeps tests for the area, the first build node writes a characterization test that passes against unchanged code before moving the structure. For a patch, retain the existing injection check. - One node owns a change and its proof, and the proof is the one its work type names: a `design` node ends with the draft-guard checker at exit 0 on its own output; a `research` node ends when every high-risk claim it touches has a status and a gate record; an `audit` node has no build step at all, because its lanes prove the register rather than a change.
- Cut at stable interface seams; merge two nodes rather than share a file.
- Route each node by agent type: `agent(agent='task', ...)` by default, `agent(agent='sonic', ...)` only for strictly mechanical edits (`SKILL.md`, Agents per stage). Never dispatch to an agent the host does not list.
- One node owns a change AND its proof: the node that makes the edit runs the VERIFY that proves it and captures the evidence. Test rules: `SKILL.md`, Rules.
- Node fields: TASK, DELIVERABLE, SCOPE, VERIFY, STOP WHEN. Every node prompt follows `SKILL.md`, Delegation prompts, and carries these fields. SCOPE names this node's disjoint write scope and the worktree pin. VERIFY is the command that proves the change, including the injection check when the node owns a guard row. STOP WHEN is those artifacts written and no background command the node started still running.
- A batch is the nodes whose dependencies are satisfied, dispatched together in one `parallel()` call of `agent()` thunks (`references/orchestration.md`, `<structure>`). Read each output and its artifacts. A node that returned without the artifacts it names is a call error (Recovery).
- No verification, review, or synthesis node inside the run. Verification is stage 10.

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

Commit after each verified unit, in the repository's commit style, staging only its own unit's files. Parallel nodes share one git index, so commits are serialized: give committing to one node, or order the committing nodes so they do not run in the same batch. Record a commit only after `git -C <worktree> cat-file -t <sha>` prints `commit`.

### Evidence ownership, reuse, and freeze

Assign one writer to each run file. The lead writes shared plan, decision and finding records; a lane writes only its own evidence artifact. Keep the evidence dir outside the worktree. Record enough for each lane's evidence to identify its unit, head, tree, covered paths or globs, result, commands or observations, artifacts, and any relevant environment or build identity. After a fix or rebase, judge each lane's evidence against the new tree. A matching tree is valid; otherwise compare changed files with its recorded scope: an intersection makes that evidence stale. A changed recorded surface or build identity also makes the affected evidence stale. Record each reuse decision and its reason; rerun only stale lanes, not every lane. Before captures remain historical and are exempt. The final-review gate is stricter: when code review is required, it needs a valid code-review receipt for this unit at the exact frozen head and matching tree; a same-tree receipt from another head or a reused sibling receipt does not satisfy it. After triage and required fixes, freeze the unit's head and tree before opening its PR and starting the final review. Nothing commits while that freeze is in force; correction memos and other evidence go to the evidence dir, never the branch. Keep the head frozen through the verdict. A fix following a REVISE verdict starts a new correction run and a fresh freeze; it remains in the same PR. If the observed head moved, do not carry a verdict forward: re-establish valid evidence, freeze and review for the actual head. ### Concurrency and ownership

Nodes, reviewers, and you share one worktree. Three rules keep one from corrupting another's work:

1. **One foreground command per injection.** An injection driver injects, runs the test, restores the file from a backup, and checks that the restored file's hash matches the backup, all in one foreground shell command, never split across separate tool calls or left in a background session. A turn that ends early then can't leave code injected.
2. **No injection where a reviewer reads.** Never inject into the worktree while a reviewer may read it. Run injections before the reader starts, or in a private copy of the worktree.
3. **Siblings see each other's edits.** Parallel nodes see each other's mid-edit state. A whole-tree check (a build, `go vet ./...`) that fails in a file outside the node's write scope may have caught a sibling mid-edit: check whether a sibling was writing that file, and rerun after it settles before calling the failure a defect.

### Recovery

`agent()` cannot be resumed after it returns, so a re-run is a fresh `agent()` call. Before re-dispatching a failed node, restore its files to their pre-dispatch state, because a fresh `agent()` works in the shared worktree.

**Call errors** are failures of the host or the call, not the work: `agent()` raised, the output was empty or didn't match the schema, a tool or provider error, a crash, a timeout, or a node that ended without its named artifacts. Re-run that node as a fresh `agent()` call with the same prompt. Leave the plan alone.

**Work failures** are genuine: a criterion the work does not meet. Find the cause (a plan problem, a node-instruction problem, or an environment problem), fix that cause, then re-dispatch the corrected node.

### Tier execution and progress

Use the tier and facts fixed in planning. Never lower the tier; raise it when newly discovered facts require it. S permits plan review to start alongside build, with a blocker amending the run, and at most one mutation per guard row; M runs stages serially by default with the full verification wave; L adds an adversarial lane even without a high-risk row and QA covers state and lifetime transitions. Below L, the adversarial lane is required for a high-risk plan row. These are execution differences, not permission to reduce review depth or skip a required lane. Keep `todo` current as the live checklist. At each transition changing a count, and at least every 30 minutes while a unit runs, use the handoff to report a `PROGRESS:` line with whole-request units done/total, defect gaps fixed/total when tracked, PRs merged and open, the current wave, review round, switch count, and what is waiting. Use `n/a` for a missing register. Suppress repeats with no change; keep ordinary step-transition handoffs without duplicating an unchanged progress line.

### Restart after a death or a compaction

The rules are in `references/verification.md`, Restart after a death or a compaction. This subsection carries
only the mechanics, so the two never state the same rule twice.

- The first command of a restarted run is the rebind: read the plan's evidence dir, `git worktree list`, and
  `git branch --show-current`, then confirm all three match what the plan records.
- Before dispatching, read the plan file, the todo list, and the evidence dir. Never carry a next action out
  of the previous turn's conversation.
- Read the live external state with a command, not from memory: `git ls-remote` for a push, the PR's own state
  for a PR or a merge, the deploy target's own status for a deploy.
- A restarted run re-dispatches with the same node prompt. Do not rewrite the prompt to match what the
  half-finished work did.
- Inject, run the guard test, and restore in one foreground command, so a killed turn cannot leave a mutant in
  the tree.

---
