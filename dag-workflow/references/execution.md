Read this when stage 2 (execution) of the dag-workflow flow starts; SKILL.md, Stages and required reads, lists it.

# dag-workflow: execution

This file covers stage 2: the worktree, the baseline, batches of implementation nodes, and one verification node per batch. The stage ends when every implementation node has a PASS verdict.

## The goal

There is one goal per run. When the run started from `/wf`, `/goal` is already armed with the task text; never start a second goal, and never rewrite it into several. Without `/wf`, run without a goal. Either way the plan file and the `todo` list are the record of progress: the plan holds the IS rows, criteria, and scenarios, and `todo` mirrors its atomic units (`SKILL.md`, Progress reporting).

## Worktree and node design

Create one worktree per task off the integration base and record the base SHA in the plan:

```
git worktree add -b <branch> <path> <base>
git -C <path> rev-parse HEAD
```

Every command in a node prompt pins that worktree with `git -C <worktree> ...` or `cd <worktree> && ...`, never the node's default cwd.

**Baseline first.** Before the first batch, run the plan's baseline command (the repository's tests and checks) in the worktree and keep the output in the evidence dir. A red baseline observed after implementation can't separate pre-existing failures from regressions. If the baseline is already red, stop and report the blocker; don't dispatch implementation against a broken baseline.

**Slicing.** Aim for the shortest critical path (the longest dependency chain), not the fewest edges. A large node with no dependencies still holds up its batch if it's the slowest one there.

- Cut at stable interface seams (type signatures, API contracts, file boundaries), where one node's output feeds another's input without shared mutable state.
- Keep real data and state dependencies. Remove artificial ones by widening a node, or by putting a preemptive interface node first when two nodes would otherwise share a surface.
- Balance node sizes so no single node straggles behind its batch.
- No two parallel nodes share a write scope. When two would edit the same file, merge them rather than share it.
- Keep each production change and its behavioral proof in the same node.

**Routing.** Pick each node's agent from `SKILL.md`, Agents per stage, by the kind of work: `task` by default, `sonic` only for strictly mechanical edits. Never dispatch to an agent the host doesn't list.

**Node prompt fields.** Every node prompt follows `SKILL.md`, Delegation prompts, and carries all five of these:

1. the success criterion the node must meet;
2. the exact VERIFY command or check that proves it;
3. numbered must-do steps;
4. forbidden deviations;
5. the artifact paths it must write, such as reports or verdict files in the evidence dir.

Its stop condition is: those artifacts written and no background command it started still running. Each dependent node's prompt makes it re-check the specific upstream facts it builds on before trusting them.

**Batches.** A batch is the set of nodes whose dependencies are satisfied, dispatched together in ONE eval `parallel()` call of `agent()` thunks (the pattern in `references/orchestration.md`, `<structure>`), with `schema=` where you need a structured return. When the batch returns, read each output against its criterion and check that every artifact it names exists and is non-empty. A node that returned without them is handled as a call error under Recovery. For a node that owns `guard` rows, also check its injection evidence (Regression tests): the test, the injection diff, the failing output, and the passing output after restore, with the diff producing the regression the guard names. A missing piece is unproven work.

## Batch verification node

After each batch returns, run ONE `agent(agent='reviewer', schema=...)` call over the whole batch. Its prompt follows `SKILL.md`, Delegation prompts. It:

- diffs each node's output against the pinned base SHA;
- reruns every node's VERIFY;
- checks each output against its success criterion and against `references/verification.md`, Batch verification checks;
- writes `<evidence dir>/<batch-id>-verdict.md`, whose first line is exactly `VERDICT: PASS` or `VERDICT: FAIL`, followed by the reasons and every finding.

When a batch touches security-sensitive code, one `security-reviewer` reviews that batch alongside it and its findings go into the same verdict.

The eval cell reads the verdict file and dispatches the next batch only when the first line is `VERDICT: PASS`. The gate is transitive: every later node's FIRST must-do step re-reads every upstream verdict file and stops at once with `BLOCKED: <id> not PASS` unless each first line is `VERDICT: PASS`. A blocked node exits with that line as its answer; it never waits or polls for a verdict to change. Whether the blocked work resumes is your decision, made under Recovery.

Report each verdict as it lands (`SKILL.md`, Progress reporting). A verification node never fixes its own batch; a FAIL is a work failure and goes to Recovery.

## Commits

A node commits each verified unit inside the task worktree, in the repository's commit style, with only that unit's files staged. Parallel nodes share one Git index, so serialize commits: give committing to one node, or chain the committing nodes. Record a commit only after `git -C <worktree> cat-file -t <sha>` prints `commit`.

## Concurrency and ownership

Nodes, reviewers, and you share one worktree. Three rules keep one from corrupting another's work:

1. **One foreground command per injection.** An injection driver injects, runs the test, restores the file from a backup, and checks that the restored file's hash matches the backup, all in one foreground shell command, never split across separate tool calls or left in a background session. A turn that ends early then can't leave code injected.
2. **No injection where a reviewer reads.** Never inject into the worktree while a reviewer or verification node may read it. Run injections before the reader starts, or in a private copy of the worktree.
3. **Siblings see each other's edits.** Parallel nodes see each other's mid-edit state. A whole-tree check (a build, `go vet ./...`) that fails in a file outside the node's write scope may have caught a sibling mid-edit: check whether a sibling was writing that file, and rerun after it settles before calling the failure a defect.

`agent()` is synchronous: once it returns, that agent can't be reached again. Any re-run is a fresh `agent()` call with the original prompt plus the feedback.

## Regression tests

This applies where a node changes runtime behavior and the repository can hold tests for it. Three principles, in this order:

1. **Code first.** Write the change before its test.
2. **Once it works, add the tests.** What matters is that the tests exist at the end.
3. **Test only externally visible behavior.** A test breaks when behavior changes, not when the implementation is refactored.

Steps:

1. Read the existing tests for that behavior. Note whether they encode the intended behavior, cover the changed path, and pass. For a behavior the plan says stays intact, record its reference before editing (`references/planning.md`, The plan).
2. For a bug fix, reproduce the bug before fixing it and capture the failure, through an existing test or a real-surface reproduction.
3. Implement the change and confirm it works on its real surface.
4. For each `guard` row assigned to the node, add or extend one test on the behavior the user relies on. If an existing test already catches the guard's regression, name it and add none; the injection check still applies to it. Only `guard` rows get new tests. A green test that requires the opposite of the guard's intended outcome isn't evidence for that guard.
5. Run the injection check on each guard's test.
6. Clean up only while the same tests stay green.

**Injection check.** Recreate the regression the guard names, run its test once, and capture the failure; then restore, run it again, and capture the pass. For a bug fix, revert only the production fix and keep the test. For new code, make the one smallest edit that produces the regression: drop a condition, shift a boundary by one, omit a return value or side effect. Remove the whole feature only when the guard is the feature's existence. The capture must show a non-zero executed test count with the test named; a run that executed nothing proves nothing. A test that stays green under its injection doesn't guard anything.

**Interleaving check.** When a node changes concurrency, ordering, or subscription identity, each affected interleaving is a `guard` row (add it to the risk list when missing), and the same commit adds a test that reproduces it deterministically, holding each step at a barrier or explicit release instead of relying on timing. Cover at least: two concurrent requests; a renewal or resubscription under the same ID; a failure or stale result arriving after a newer state. The test passes the check only when it fails under that interleaving with the fix reverted.

Use the pack's `debugging` skill only for a bug whose cause isn't confirmed, or a test that stays green under its injection for an unclear reason. Use the `tdd` skill only when the user asked for test-first.

Don't pin prose, prompt wording, content hashes, or incidental tunables and call counts. Prose, prompt, and docs changes are `no-test` rows with read-through QA. Never delete, weaken, or skip an existing test, and never loosen its assertion to make it pass. If one is removed anyway, the node report and the final report name it, say why, and give the evidence that replaces it.

## Findings during execution

Apply `SKILL.md`, The purpose boundary and Follow-up record; this file adds no second definition. An in-scope finding becomes a node in the next batch. Everything else goes to the follow-up record and is never fixed here. You decide which side each finding falls on and correct drift by re-scoping the next prompt.

## Recovery

Every failure is one of two kinds, and only the second touches the plan.

**Call errors** are failures of the host or the call, not the work: `agent()` raised, the output was empty or didn't match the schema, named artifacts are missing, or the call timed out. Re-run that same node once with the same prompt as a fresh `agent()` call. That isn't a redesign; leave the plan alone. Never re-run a verification or review node for its judgment, only for a call error.

**Work failures** are genuine: a `VERDICT: FAIL`, or a criterion the work doesn't meet. Then:

1. Record the cause in the plan as one of three classes: a plan problem, a node-instruction problem, or an environment problem.
2. Fix that cause in the plan, the node prompt, or the environment.
3. Restore the failing nodes' files to their pre-dispatch snapshot.
4. Re-dispatch ONLY the failing nodes, plus one new verification node for that re-run batch.

There's no attempt cap. When the same cause class is recorded a third time in a row, tell the user in one line and keep going. A stronger agent doesn't fix a wrong plan.
