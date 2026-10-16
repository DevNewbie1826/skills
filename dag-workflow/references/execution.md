Read this when step 5 (execution) of the dag-workflow flow starts; SKILL.md, The 13 steps, lists it.

# dag-workflow: execution

Covers step 5 of the flow (see `SKILL.md`, The 13 steps).

## Step 5: Run the plan

Run the plan's nodes under these rules.

### Worktree and nodes

Create one worktree per task off main, kept through merge. A correction run in the same task reuses that worktree.

```
git worktree add -b <branch> <path> main
```

- Every command in every node prompt pins that worktree: `cd <worktree> && ...` or `git -C <worktree> ...`, never a default cwd (pinned rule, `references/planning.md`, Step 2: The plan file).
- Parallel nodes have a disjoint write scope: no two nodes running together write the same file. Dispatch a node after another only for a real dependency: it reads or writes a file the upstream node writes, or a rule orders them, such as serialized commits.
- Cut at stable interface seams; merge two nodes rather than share a file.
- Route each node by agent type: `agent(agent='task', ...)` by default, `agent(agent='sonic', ...)` only for strictly mechanical edits (`SKILL.md`, Agents per step). Never dispatch to an agent the host does not list.
- One node owns a change AND its proof: the node that makes the edit runs the VERIFY that proves it and captures the evidence. Test rules: `SKILL.md`, Rules.
- Node fields: TASK, DELIVERABLE, SCOPE, VERIFY, STOP WHEN. Every node prompt follows `SKILL.md`, Delegation prompts, and carries these fields. SCOPE names this node's disjoint write scope and the worktree pin. VERIFY is the command that proves the change, including the injection check when the node owns a guard row. STOP WHEN is those artifacts written and no background command the node started still running.
- A batch is the nodes whose dependencies are satisfied, dispatched together in one `parallel()` call of `agent()` thunks (`references/orchestration.md`, `<structure>`). Read each output and its artifacts. A node that returned without the artifacts it names is a call error (Recovery).
- No verification, review, or synthesis node inside the run. Verification is step 6.

### Injection check inside the node

For each guard row the node owns, prove its test can fail, inside the same node:

1. Recreate the regression the guard names: revert the fix, or make the one smallest edit that produces it.
2. Run the guard's test once and capture the failing output.
3. Restore the file, run the test once more, and capture the passing output.

The evidence set is the injection diff, the failing output, and the passing output after restore. A test that stays green under its injection guards nothing. Run inject, test, and restore as one command, so nothing ends mid-injection.

### Commits

Commit after each verified unit, in the repository's commit style, staging only its own unit's files. Parallel nodes share one git index, so commits are serialized: give committing to one node, or order the committing nodes so they do not run in the same batch. Record a commit only after `git -C <worktree> cat-file -t <sha>` prints `commit`.

### Concurrency and ownership

Nodes, reviewers, and you share one worktree. Three rules keep one from corrupting another's work:

1. **One foreground command per injection.** An injection driver injects, runs the test, restores the file from a backup, and checks that the restored file's hash matches the backup, all in one foreground shell command, never split across separate tool calls or left in a background session. A turn that ends early then can't leave code injected.
2. **No injection where a reviewer reads.** Never inject into the worktree while a reviewer may read it. Run injections before the reader starts, or in a private copy of the worktree.
3. **Siblings see each other's edits.** Parallel nodes see each other's mid-edit state. A whole-tree check (a build, `go vet ./...`) that fails in a file outside the node's write scope may have caught a sibling mid-edit: check whether a sibling was writing that file, and rerun after it settles before calling the failure a defect.

### Recovery

`agent()` cannot be resumed after it returns, so a re-run is a fresh `agent()` call. Before re-dispatching a failed node, restore its files to their pre-dispatch state, because a fresh `agent()` works in the shared worktree.

**Call errors** are failures of the host or the call, not the work: `agent()` raised, the output was empty or didn't match the schema, a tool or provider error, a crash, a timeout, or a node that ended without its named artifacts. Re-run that node as a fresh `agent()` call with the same prompt. Leave the plan alone.

**Work failures** are genuine: a criterion the work does not meet. Find the cause (a plan problem, a node-instruction problem, or an environment problem), fix that cause, then re-dispatch the corrected node.
